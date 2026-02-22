#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
#   "scikit-learn>=1.5.0",
# ]
# ///
"""Step 8: Longitudinal Analysis (paired, non-IRT-linked alternatives).

This script builds longitudinal analyses using paired comparisons instead of
IRT-linked growth, because Step 6 found no usable wave-pair anchor links.

Primary design choices:
- Use public-best GRM question categories (0/1/2) from Step 6 for comparable
  wave/term student-performance summaries.
- Use paired student comparisons (within-term and cross-term) to respect the
  progressive-filter cohort structure.
- Export both raw paired-cohort counts and a stricter "substantive
  participation" cohort used for primary summaries:
    * at least 3 question rows in each compared wave/term

Outputs are written under ``analysis/longitudinal_analysis/``.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import duckdb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "longitudinal_analysis"

SUBSTANTIVE_MIN_QUESTION_ROWS = 3
STANDARD_WAVES = ("wave1", "wave2")

STATE_ORDER = {
    "NO_PUBLIC_RUNS": -1,
    "S0_no_code": 0,
    "S1_syntax_fundamental": 1,
    "S1b_syntax_structure": 2,
    "S2_parseable_zero": 3,
    "S3_public_partial": 4,
    "S4_public_all": 5,
    "S5_all_tests": 6,
}
STATE_LABELS = {
    "NO_PUBLIC_RUNS": "No public test runs",
    "S0_no_code": "State 0: no code beyond skeleton",
    "S1_syntax_fundamental": "State 1: non-parseable, no recoverable structure",
    "S1b_syntax_structure": "State 1b: non-parseable, structure evident",
    "S2_parseable_zero": "State 2: parseable, passes 0 public tests",
    "S3_public_partial": "State 3: passes some public tests",
    "S4_public_all": "State 4: passes all public tests",
    "S5_all_tests": "State 5: passes all tests",
}

TERM_ORDER = {"25t1": 1, "25t2": 2, "25t3": 3}
NEXT_TERM = {"25t1": "25t2", "25t2": "25t3"}

KEY_CONSTRUCTS = [
    "function_def",
    "for_loop",
    "if_stmt",
    "while_loop",
    "list_comp",
    "dict_comp",
    "try_stmt",
    "print_call",
]


@dataclass(frozen=True)
class Inputs:
    grm_rows: Path = ANALYSIS_DIR / "psychometric_irt" / "question_level_grm_rows.csv"
    namespace_metadata: Path = ANALYSIS_DIR / "psychometric_irt" / "namespace_metadata.csv"
    question_flags: Path = ANALYSIS_DIR / "psychometric_irt" / "question_parameter_flags.csv"
    pair_anchor_drift: Path = ANALYSIS_DIR / "psychometric_irt" / "namespace_pair_anchor_parameter_drift.csv"

    attempt_archetypes: Path = ANALYSIS_DIR / "process_analysis" / "attempt_archetypes.csv"
    public_state_rows: Path = ANALYSIS_DIR / "process_analysis" / "public_test_run_state_rows.parquet"
    attempt_construct_first: Path = ANALYSIS_DIR / "process_analysis" / "attempt_construct_first_appearance.csv"

    selected_snapshot_rows: Path = ANALYSIS_DIR / "error_taxonomy" / "selected_snapshot_taxonomy_rows.csv"
    best_public_rows: Path = ANALYSIS_DIR / "error_taxonomy" / "best_public_test_run_classification_rows.csv"

    dependency_graph_summary: Path = ANALYSIS_DIR / "classical_item_quality" / "question_dependency_graph_summary.csv"


INPUTS = Inputs()


def cpu_threads() -> int:
    try:
        n = os.cpu_count() or 4
    except Exception:
        n = 4
    return max(1, n - 1)


def make_conn() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute(f"PRAGMA threads={cpu_threads()}")
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def qdf(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


def sql_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def ensure_inputs() -> None:
    missing = [p for p in INPUTS.__dict__.values() if not p.exists()]
    if missing:
        lines = "\n".join(f"- {p}" for p in missing)
        raise FileNotFoundError(f"Missing Step 8 inputs:\n{lines}")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_manifest() -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "output_manifest.csv":
            rows.append({"path": path.relative_to(OUT_DIR).as_posix(), "bytes": path.stat().st_size})
    pd.DataFrame(rows).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def normalize_title(s: str | None) -> str:
    if not s:
        return ""
    txt = str(s).strip().lower()
    txt = txt.replace("&", " and ")
    txt = re.sub(r"\bq\d+\s*:\s*", "", txt)
    txt = re.sub(r"[^a-z0-9]+", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def dominant_label_summary(
    df: pd.DataFrame,
    group_cols: list[str],
    label_col: str,
    count_name: str,
    dominant_col_name: str,
) -> pd.DataFrame:
    """Return dominant label per group with tie diagnostics."""
    if df.empty:
        cols = group_cols + [
            dominant_col_name,
            count_name,
            "group_total",
            "dominant_share",
            "dominant_label_tie_count",
            "dominant_label_tied",
        ]
        return pd.DataFrame(columns=cols)

    counts = df.groupby(group_cols + [label_col], dropna=False).size().reset_index(name=count_name)
    counts["label_sort"] = counts[label_col].astype(str).fillna("")
    counts = counts.sort_values(group_cols + [count_name, "label_sort"], ascending=[True] * len(group_cols) + [False, True])

    group_total = counts.groupby(group_cols, dropna=False)[count_name].sum().reset_index(name="group_total")
    max_count = counts.groupby(group_cols, dropna=False)[count_name].max().reset_index(name="max_count")
    counts = counts.merge(group_total, on=group_cols, how="left").merge(max_count, on=group_cols, how="left")
    counts["is_max"] = counts[count_name] == counts["max_count"]

    tie = (
        counts.groupby(group_cols, dropna=False)["is_max"]
        .sum()
        .reset_index(name="dominant_label_tie_count")
    )
    top = counts.sort_values(group_cols + ["is_max", count_name, "label_sort"], ascending=[True] * len(group_cols) + [False, False, True])
    top = top.groupby(group_cols, dropna=False, as_index=False).head(1).copy()
    top = top.rename(columns={label_col: dominant_col_name})
    top = top.merge(tie, on=group_cols, how="left")
    top["dominant_label_tied"] = top["dominant_label_tie_count"].fillna(0).astype(int) > 1
    top["dominant_share"] = np.where(top["group_total"] > 0, top[count_name] / top["group_total"], np.nan)
    top = top[group_cols + [
        dominant_col_name,
        count_name,
        "group_total",
        "dominant_share",
        "dominant_label_tie_count",
        "dominant_label_tied",
    ]]
    return top


def compute_weighted_change_summary(
    pairs: pd.DataFrame,
    group_col: str,
    label_col: str,
    weight_col: str | None = None,
    out_label: str | None = None,
) -> pd.DataFrame:
    if pairs.empty:
        return pd.DataFrame(columns=[group_col, label_col, "students", "weighted_students", "pct_students", "pct_weighted_students"])

    df = pairs.copy()
    if weight_col is None or weight_col not in df.columns:
        df["_weight"] = 1.0
    else:
        df["_weight"] = pd.to_numeric(df[weight_col], errors="coerce").fillna(0.0)
    g = df.groupby([group_col, label_col], dropna=False).agg(
        students=("student_id", "nunique"),
        weighted_students=("_weight", "sum"),
    ).reset_index()
    denom_students = g.groupby(group_col)["students"].sum().reset_index(name="_den_students")
    denom_weighted = g.groupby(group_col)["weighted_students"].sum().reset_index(name="_den_weighted")
    g = g.merge(denom_students, on=group_col, how="left").merge(denom_weighted, on=group_col, how="left")
    g["pct_students"] = np.where(g["_den_students"] > 0, 100.0 * g["students"] / g["_den_students"], np.nan)
    g["pct_weighted_students"] = np.where(
        g["_den_weighted"] > 0, 100.0 * g["weighted_students"] / g["_den_weighted"], np.nan
    )
    g.drop(columns=["_den_students", "_den_weighted"], inplace=True)
    if out_label and out_label != label_col:
        g = g.rename(columns={label_col: out_label})
    return g


def state_rank_value(state: str | None) -> int:
    if state is None or (isinstance(state, float) and pd.isna(state)):
        return STATE_ORDER["NO_PUBLIC_RUNS"]
    return STATE_ORDER.get(str(state), STATE_ORDER["NO_PUBLIC_RUNS"])


def label_sign(delta: float | int | None, eps: float = 1e-12) -> str:
    if delta is None or (isinstance(delta, float) and pd.isna(delta)):
        return "unknown"
    if delta > eps:
        return "improve"
    if delta < -eps:
        return "decline"
    return "same"


def materialize_base_views(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW grm_rows AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            term,
            wave,
            question_title,
            CAST(grm_category AS DOUBLE) AS grm_category,
            CAST(category_public_best AS DOUBLE) AS category_public_best
        FROM read_csv_auto('{sql_path(INPUTS.grm_rows)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW attempt_core AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            track,
            term,
            wave,
            question_title,
            primary_archetype,
            process_outcome_success_flag,
            no_activity_flag,
            public_test_run_count,
            any_public_pass,
            any_public_all_pass
        FROM read_csv_auto('{sql_path(INPUTS.attempt_archetypes)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW selected_snapshot_core AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            term,
            wave,
            track,
            question_title,
            outcome_category,
            skeleton_modification_status,
            selected_tree_sitter_parseable,
            ts_has_function_def,
            ts_has_for_loop,
            ts_has_if_stmt,
            ts_has_while_loop,
            ts_has_list_comp,
            ts_has_dict_comp,
            ts_has_try_stmt,
            ts_has_print_call,
            ts_complexity_score
        FROM read_csv_auto('{sql_path(INPUTS.selected_snapshot_rows)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW best_public_core AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            term,
            wave,
            best_public_summary,
            best_public_runtime_error_type,
            best_public_wrong_output_subtype,
            best_public_primary_failure_mode,
            best_public_num_test_passed,
            best_public_test_case_count
        FROM read_csv_auto('{sql_path(INPUTS.best_public_rows)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW state_rows_core AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            track,
            term,
            wave,
            public_run_index,
            process_state
        FROM read_parquet('{sql_path(INPUTS.public_state_rows)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW construct_first_core AS
        SELECT
            namespace,
            CAST(problem_id AS BIGINT) AS problem_id,
            student_id,
            construct,
            term,
            wave,
            track
        FROM read_csv_auto('{sql_path(INPUTS.attempt_construct_first)}')
        WHERE wave IN ('wave1', 'wave2');
        """
    )

    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW namespace_meta_core AS
        SELECT
            namespace,
            term,
            wave,
            start_time,
            end_time,
            exam_date,
            slot_order_in_day,
            namespace_standard_pattern
        FROM read_csv_auto('{sql_path(INPUTS.namespace_metadata)}');
        """
    )


def build_term_wave_gap_summary(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    ns = qdf(
        conn,
        """
        WITH w AS (
            SELECT
                term,
                wave,
                MIN(CAST(start_time AS TIMESTAMPTZ)) AS min_start_ts,
                MAX(CAST(start_time AS TIMESTAMPTZ)) AS max_start_ts,
                COUNT(*) AS namespaces
            FROM namespace_meta_core
            WHERE wave IN ('wave1','wave2')
            GROUP BY 1,2
        ),
        paired AS (
            SELECT
                w1.term,
                w1.namespaces AS wave1_namespaces,
                w2.namespaces AS wave2_namespaces,
                w1.min_start_ts AS wave1_min_start_ts,
                w1.max_start_ts AS wave1_max_start_ts,
                w2.min_start_ts AS wave2_min_start_ts,
                w2.max_start_ts AS wave2_max_start_ts,
                EXTRACT(EPOCH FROM (w2.min_start_ts - w1.min_start_ts)) / 86400.0 AS min_start_gap_days
            FROM w w1
            JOIN w w2
              ON w1.term = w2.term
             AND w1.wave = 'wave1'
             AND w2.wave = 'wave2'
        )
        SELECT * FROM paired
        ORDER BY term
        """,
    )
    if not ns.empty:
        ns["min_start_gap_days"] = pd.to_numeric(ns["min_start_gap_days"], errors="coerce").round(2)
    return ns


def build_student_wave_performance(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = qdf(
        conn,
        """
        SELECT
            term,
            wave,
            student_id,
            COUNT(*) AS question_rows,
            SUM(grm_category) AS grm_sum_category,
            AVG(grm_category) AS grm_mean_category,
            SUM(CASE WHEN grm_category >= 1 THEN 1 ELSE 0 END) AS questions_any_test_pass,
            SUM(CASE WHEN grm_category = 2 THEN 1 ELSE 0 END) AS questions_all_public_tests_pass,
            AVG(CASE WHEN grm_category >= 1 THEN 1 ELSE 0 END) AS frac_questions_any_test_pass,
            AVG(CASE WHEN grm_category = 2 THEN 1 ELSE 0 END) AS frac_questions_all_public_tests_pass
        FROM grm_rows
        GROUP BY 1,2,3
        """
    )
    if df.empty:
        return df
    df["substantive_wave_participation"] = df["question_rows"] >= SUBSTANTIVE_MIN_QUESTION_ROWS
    df["term_order"] = df["term"].map(TERM_ORDER).fillna(99).astype(int)
    df = df.sort_values(["term_order", "wave", "student_id"]).drop(columns=["term_order"]).reset_index(drop=True)

    # Rank within term+wave score distribution (higher = better).
    rank_cols = ["grm_mean_category", "grm_sum_category", "questions_any_test_pass"]
    for c in rank_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    ranked_parts: list[pd.DataFrame] = []
    for (term, wave), g in df.groupby(["term", "wave"], sort=False):
        gg = g.copy()
        gg = gg.sort_values(["grm_mean_category", "grm_sum_category", "questions_any_test_pass", "student_id"], ascending=[True, True, True, True])
        n = len(gg)
        if n == 1:
            gg["wave_rank_pct"] = 1.0
            gg["wave_rank_index_1based"] = 1
        else:
            # deterministic tie-break ranking over ordered rows; pct maps worst->0, best->1
            gg["wave_rank_index_1based"] = np.arange(1, n + 1)
            gg["wave_rank_pct"] = (gg["wave_rank_index_1based"] - 1) / (n - 1)
        ranked_parts.append(gg)
    out = pd.concat(ranked_parts, ignore_index=True) if ranked_parts else df.head(0)
    return out


def build_within_term_wave_pairs(student_wave_perf: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if student_wave_perf.empty:
        empty = pd.DataFrame()
        return empty, empty, empty

    w1 = student_wave_perf[student_wave_perf["wave"] == "wave1"].copy()
    w2 = student_wave_perf[student_wave_perf["wave"] == "wave2"].copy()
    pairs = w1.merge(w2, on=["term", "student_id"], how="inner", suffixes=("_w1", "_w2"))
    if pairs.empty:
        return pairs, pd.DataFrame(), pd.DataFrame()

    pairs["paired_question_rows_min"] = pairs[["question_rows_w1", "question_rows_w2"]].min(axis=1)
    pairs["paired_question_rows_mean"] = pairs[["question_rows_w1", "question_rows_w2"]].mean(axis=1)
    pairs["substantive_pair"] = (
        (pairs["question_rows_w1"] >= SUBSTANTIVE_MIN_QUESTION_ROWS)
        & (pairs["question_rows_w2"] >= SUBSTANTIVE_MIN_QUESTION_ROWS)
    )
    pairs["rank_pct_delta_w2_minus_w1"] = pairs["wave_rank_pct_w2"] - pairs["wave_rank_pct_w1"]
    pairs["grm_mean_category_delta_w2_minus_w1"] = pairs["grm_mean_category_w2"] - pairs["grm_mean_category_w1"]
    pairs["grm_sum_category_delta_w2_minus_w1"] = pairs["grm_sum_category_w2"] - pairs["grm_sum_category_w1"]
    pairs["questions_any_test_pass_delta_w2_minus_w1"] = pairs["questions_any_test_pass_w2"] - pairs["questions_any_test_pass_w1"]
    pairs["rank_change_label"] = pairs["rank_pct_delta_w2_minus_w1"].apply(label_sign)
    pairs["category_change_label"] = pairs["grm_mean_category_delta_w2_minus_w1"].apply(label_sign)
    pairs["question_any_pass_count_change_label"] = pairs["questions_any_test_pass_delta_w2_minus_w1"].apply(label_sign)
    pairs["term_order"] = pairs["term"].map(TERM_ORDER).fillna(99).astype(int)
    pairs = pairs.sort_values(["term_order", "student_id"]).drop(columns=["term_order"]).reset_index(drop=True)

    coverage = (
        pairs.groupby("term", dropna=False)
        .agg(
            paired_students_raw=("student_id", "nunique"),
            paired_students_substantive=("substantive_pair", lambda s: int(pd.Series(s).fillna(False).sum())),
            avg_question_rows_wave1=("question_rows_w1", "mean"),
            avg_question_rows_wave2=("question_rows_w2", "mean"),
            median_question_rows_wave1=("question_rows_w1", "median"),
            median_question_rows_wave2=("question_rows_w2", "median"),
        )
        .reset_index()
        .sort_values("term")
    )
    for c in ["avg_question_rows_wave1", "avg_question_rows_wave2", "median_question_rows_wave1", "median_question_rows_wave2"]:
        coverage[c] = pd.to_numeric(coverage[c], errors="coerce").round(2)

    return pairs, coverage, pairs[pairs["substantive_pair"]].copy()


def build_student_wave_archetype(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = qdf(
        conn,
        """
        SELECT
            term,
            wave,
            student_id,
            primary_archetype,
            COUNT(*) AS question_rows,
            SUM(CASE WHEN process_outcome_success_flag THEN 1 ELSE 0 END) AS success_question_rows
        FROM attempt_core
        GROUP BY 1,2,3,4
        """
    )
    if df.empty:
        return df
    dom = dominant_label_summary(df.loc[df["question_rows"] > 0], ["term", "wave", "student_id"], "primary_archetype", "question_rows", "dominant_primary_archetype")
    totals = (
        df.groupby(["term", "wave", "student_id"], dropna=False)
        .agg(
            archetype_question_rows=("question_rows", "sum"),
            archetype_success_question_rows=("success_question_rows", "sum"),
            archetype_labels_seen=("primary_archetype", "nunique"),
        )
        .reset_index()
    )
    out = totals.merge(dom, on=["term", "wave", "student_id"], how="left")
    dom_success = (
        df.merge(
            out[["term", "wave", "student_id", "dominant_primary_archetype"]],
            left_on=["term", "wave", "student_id", "primary_archetype"],
            right_on=["term", "wave", "student_id", "dominant_primary_archetype"],
            how="inner",
        )
        .groupby(["term", "wave", "student_id"])["success_question_rows"]
        .sum()
        .reset_index(name="dominant_primary_archetype_success_rows")
    )
    out = out.merge(dom_success, on=["term", "wave", "student_id"], how="left")
    out["dominant_primary_archetype_success_rows"] = out["dominant_primary_archetype_success_rows"].fillna(0).astype(int)
    return out


def build_student_term_archetype(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = qdf(
        conn,
        """
        SELECT
            term,
            student_id,
            primary_archetype,
            COUNT(*) AS question_rows,
            SUM(CASE WHEN process_outcome_success_flag THEN 1 ELSE 0 END) AS success_question_rows
        FROM attempt_core
        GROUP BY 1,2,3
        """
    )
    if df.empty:
        return df
    dom = dominant_label_summary(df.loc[df["question_rows"] > 0], ["term", "student_id"], "primary_archetype", "question_rows", "dominant_primary_archetype")
    totals = (
        df.groupby(["term", "student_id"], dropna=False)
        .agg(
            archetype_question_rows=("question_rows", "sum"),
            archetype_success_question_rows=("success_question_rows", "sum"),
            archetype_labels_seen=("primary_archetype", "nunique"),
        )
        .reset_index()
    )
    out = totals.merge(dom, on=["term", "student_id"], how="left")
    dom_success = (
        df.merge(
            out[["term", "student_id", "dominant_primary_archetype"]],
            left_on=["term", "student_id", "primary_archetype"],
            right_on=["term", "student_id", "dominant_primary_archetype"],
            how="inner",
        )
        .groupby(["term", "student_id"])["success_question_rows"]
        .sum()
        .reset_index(name="dominant_primary_archetype_success_rows")
    )
    out = out.merge(dom_success, on=["term", "student_id"], how="left")
    out["dominant_primary_archetype_success_rows"] = out["dominant_primary_archetype_success_rows"].fillna(0).astype(int)
    return out


def build_state_counts(conn: duckdb.DuckDBPyConnection, by_term_only: bool = False) -> pd.DataFrame:
    if by_term_only:
        sql = """
            SELECT
                term,
                student_id,
                process_state,
                COUNT(*) AS public_run_rows
            FROM state_rows_core
            GROUP BY 1,2,3
        """
        group_cols = ["term", "student_id"]
    else:
        sql = """
            SELECT
                term,
                wave,
                student_id,
                process_state,
                COUNT(*) AS public_run_rows
            FROM state_rows_core
            GROUP BY 1,2,3,4
        """
        group_cols = ["term", "wave", "student_id"]
    df = qdf(conn, sql)
    if df.empty:
        return df
    df["state_order"] = df["process_state"].map(STATE_ORDER).fillna(-99).astype(int)
    df["state_label"] = df["process_state"].map(STATE_LABELS).fillna(df["process_state"])
    dom = dominant_label_summary(df, group_cols, "process_state", "public_run_rows", "dominant_process_state")
    totals = df.groupby(group_cols, dropna=False)["public_run_rows"].sum().reset_index(name="public_run_rows_total")
    out = totals.merge(dom, on=group_cols, how="left")
    out["dominant_process_state_order"] = out["dominant_process_state"].map(STATE_ORDER).fillna(-99).astype(int)
    out["dominant_process_state_label"] = out["dominant_process_state"].map(STATE_LABELS).fillna(out["dominant_process_state"])
    return out


def attach_no_public_run_state(
    student_scope: pd.DataFrame,
    state_summary: pd.DataFrame,
    group_cols: list[str],
) -> pd.DataFrame:
    if student_scope.empty:
        return state_summary
    out = student_scope.merge(state_summary, on=group_cols, how="left")
    missing = out["dominant_process_state"].isna()
    if missing.any():
        out.loc[missing, "dominant_process_state"] = "NO_PUBLIC_RUNS"
        out.loc[missing, "dominant_process_state_order"] = STATE_ORDER["NO_PUBLIC_RUNS"]
        out.loc[missing, "dominant_process_state_label"] = STATE_LABELS["NO_PUBLIC_RUNS"]
        out.loc[missing, "public_run_rows"] = 0
        out.loc[missing, "group_total"] = 0
        out.loc[missing, "public_run_rows_total"] = 0
        out.loc[missing, "dominant_share"] = np.nan
        out.loc[missing, "dominant_label_tie_count"] = 0
        out.loc[missing, "dominant_label_tied"] = False
    return out


def derive_final_primary_taxonomy(row: pd.Series) -> str:
    oc = row.get("outcome_category")
    if oc == "Full pass":
        return "Full pass"
    if oc == "Partial pass":
        return "Partial pass"
    if oc == "Submitted, zero":
        return "Submitted, zero"
    if oc == "No activity":
        return "No activity"

    status = row.get("skeleton_modification_status")
    if isinstance(status, str) and status in {
        "Unmodified skeleton",
        "Empty / trivial",
        "Modified, partially broken",
        "Modified, fundamentally broken",
        "Unsupported language (non-Python)",
    }:
        return status

    bsum = row.get("best_public_summary")
    if bsum == "Runtime Error":
        return "Runtime error"
    if bsum == "Time Limit Exceeded":
        return "Timeout"
    if bsum == "Wrong Answer":
        return "Wrong output"
    if bsum == "All Cases Passed":
        return "Public full pass, no submit"
    return "Active, unresolved"


def map_error_bucket(row: pd.Series) -> str:
    fp = row.get("final_primary_taxonomy")
    wrong_sub = row.get("best_public_wrong_output_subtype")

    if fp in {"Full pass", "Partial pass"}:
        return fp
    if fp == "Public full pass, no submit":
        return "Public full pass, no submit"
    if fp == "Submitted, zero":
        return "Submitted, zero"
    if fp in {"Unmodified skeleton", "Empty / trivial", "No activity"}:
        return "No activity / skeleton"
    if fp in {"Modified, partially broken", "Modified, fundamentally broken", "Unsupported language (non-Python)"}:
        return "Syntax gated"
    if fp == "Runtime error":
        return "Runtime error"
    if fp == "Timeout":
        return "Timeout"
    if fp == "Wrong output":
        if wrong_sub == "Wrong output - logic/completely wrong":
            return "Wrong output - logic"
        if wrong_sub in {
            "Wrong output - partial correctness",
            "Wrong output - off-by-one/boundary",
            "Wrong output - formatting",
        }:
            return "Wrong output - edge/partial"
        return "Wrong output - unspecified"
    return "Active / unresolved"


ERROR_PROGRESS_ORDER = {
    "No activity / skeleton": 0,
    "Syntax gated": 1,
    "Runtime error": 2,
    "Timeout": 2,
    "Wrong output - logic": 3,
    "Wrong output - unspecified": 3,
    "Wrong output - edge/partial": 4,
    "Submitted, zero": 4,
    "Public full pass, no submit": 5,
    "Partial pass": 6,
    "Full pass": 7,
    "Active / unresolved": 1,
}


def build_error_rows(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = qdf(
        conn,
        """
        SELECT
            s.namespace,
            s.problem_id,
            s.student_id,
            s.term,
            s.wave,
            s.track,
            s.question_title,
            s.outcome_category,
            s.skeleton_modification_status,
            b.best_public_summary,
            b.best_public_runtime_error_type,
            b.best_public_wrong_output_subtype,
            b.best_public_primary_failure_mode,
            b.best_public_num_test_passed,
            b.best_public_test_case_count
        FROM selected_snapshot_core s
        LEFT JOIN best_public_core b
          ON b.namespace = s.namespace
         AND b.problem_id = s.problem_id
         AND b.student_id = s.student_id
        """
    )
    if df.empty:
        return df
    df["final_primary_taxonomy"] = df.apply(derive_final_primary_taxonomy, axis=1)
    df["error_profile_bucket"] = df.apply(map_error_bucket, axis=1)
    df["error_progress_order"] = df["error_profile_bucket"].map(ERROR_PROGRESS_ORDER).fillna(-1).astype(int)
    return df


def build_student_error_summary(error_rows: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if error_rows.empty:
        return pd.DataFrame()
    total_rows = (
        error_rows.groupby(group_cols, dropna=False)
        .agg(
            question_rows=("problem_id", "count"),
            runtime_error_rows=("best_public_summary", lambda s: int((pd.Series(s) == "Runtime Error").sum())),
            wrong_answer_rows=("best_public_summary", lambda s: int((pd.Series(s) == "Wrong Answer").sum())),
            wrong_logic_rows=("best_public_wrong_output_subtype", lambda s: int((pd.Series(s) == "Wrong output - logic/completely wrong").sum())),
            syntax_gated_rows=("error_profile_bucket", lambda s: int((pd.Series(s) == "Syntax gated").sum())),
            no_activity_or_skeleton_rows=("error_profile_bucket", lambda s: int((pd.Series(s) == "No activity / skeleton").sum())),
            full_pass_rows=("final_primary_taxonomy", lambda s: int((pd.Series(s) == "Full pass").sum())),
            partial_pass_rows=("final_primary_taxonomy", lambda s: int((pd.Series(s) == "Partial pass").sum())),
        )
        .reset_index()
    )

    dom_final = dominant_label_summary(
        error_rows[group_cols + ["final_primary_taxonomy"]].copy(),
        group_cols,
        "final_primary_taxonomy",
        "dominant_final_rows",
        "dominant_final_primary_taxonomy",
    )
    dom_bucket = dominant_label_summary(
        error_rows[group_cols + ["error_profile_bucket"]].copy(),
        group_cols,
        "error_profile_bucket",
        "dominant_error_bucket_rows",
        "dominant_error_profile_bucket",
    )
    dom_runtime = dominant_label_summary(
        error_rows.loc[error_rows["best_public_summary"] == "Runtime Error", group_cols + ["best_public_runtime_error_type"]].rename(
            columns={"best_public_runtime_error_type": "runtime_type"}
        ),
        group_cols,
        "runtime_type",
        "dominant_runtime_rows",
        "dominant_runtime_error_type",
    )
    dom_wrong = dominant_label_summary(
        error_rows.loc[error_rows["best_public_summary"] == "Wrong Answer", group_cols + ["best_public_wrong_output_subtype"]].rename(
            columns={"best_public_wrong_output_subtype": "wrong_subtype"}
        ),
        group_cols,
        "wrong_subtype",
        "dominant_wrong_answer_rows",
        "dominant_wrong_output_subtype",
    )

    dom_final_keep = dom_final[group_cols + ["dominant_final_primary_taxonomy", "dominant_final_rows", "dominant_share"]].rename(
        columns={"dominant_share": "dominant_final_primary_taxonomy_share"}
    )
    dom_bucket_keep = dom_bucket[group_cols + ["dominant_error_profile_bucket", "dominant_error_bucket_rows", "dominant_share"]].rename(
        columns={"dominant_share": "dominant_error_profile_bucket_share"}
    )
    dom_runtime_keep = dom_runtime[group_cols + ["dominant_runtime_error_type", "dominant_runtime_rows"]]
    dom_wrong_keep = dom_wrong[group_cols + ["dominant_wrong_output_subtype", "dominant_wrong_answer_rows"]]

    out = total_rows.merge(dom_final_keep, on=group_cols, how="left").merge(dom_bucket_keep, on=group_cols, how="left")
    out = out.merge(dom_runtime_keep, on=group_cols, how="left").merge(dom_wrong_keep, on=group_cols, how="left")

    for c in ["runtime_error_rows", "wrong_answer_rows", "wrong_logic_rows", "syntax_gated_rows", "no_activity_or_skeleton_rows", "full_pass_rows", "partial_pass_rows"]:
        out[c] = out[c].fillna(0).astype(int)
    return out


def build_student_term_construct_profile(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    attempts = qdf(
        conn,
        """
        SELECT
            term,
            student_id,
            COUNT(*) AS attempt_question_rows
        FROM attempt_core
        GROUP BY 1,2
        """
    )
    if attempts.empty:
        return attempts

    cf = qdf(
        conn,
        """
        SELECT
            term,
            student_id,
            construct,
            COUNT(*) AS attempts_with_construct
        FROM construct_first_core
        GROUP BY 1,2,3
        """
    )
    if cf.empty:
        out = attempts.copy()
        for c in KEY_CONSTRUCTS:
            out[f"attempts_with_{c}"] = 0
            out[f"ever_{c}"] = False
            out[f"rate_{c}"] = 0.0
        return out

    pivot = (
        cf.pivot_table(index=["term", "student_id"], columns="construct", values="attempts_with_construct", aggfunc="sum", fill_value=0)
        .reset_index()
    )
    pivot.columns = [str(c) for c in pivot.columns]
    out = attempts.merge(pivot, on=["term", "student_id"], how="left")
    for c in KEY_CONSTRUCTS:
        if c not in out.columns:
            out[c] = 0
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)
        out[f"attempts_with_{c}"] = out[c]
        out[f"ever_{c}"] = out[c] > 0
        out[f"rate_{c}"] = np.where(out["attempt_question_rows"] > 0, out[c] / out["attempt_question_rows"], np.nan)
        out.drop(columns=[c], inplace=True)
    return out


def build_student_term_performance(student_wave_perf: pd.DataFrame) -> pd.DataFrame:
    if student_wave_perf.empty:
        return student_wave_perf
    df = (
        student_wave_perf.groupby(["term", "student_id"], dropna=False)
        .agg(
            wave_count=("wave", "nunique"),
            term_question_rows=("question_rows", "sum"),
            term_grm_sum_category=("grm_sum_category", "sum"),
            term_grm_mean_category=("grm_sum_category", lambda s: np.nan),  # placeholder
            term_questions_any_test_pass=("questions_any_test_pass", "sum"),
            term_questions_all_public_tests_pass=("questions_all_public_tests_pass", "sum"),
            wave1_present=("wave", lambda s: bool((pd.Series(s) == "wave1").any())),
            wave2_present=("wave", lambda s: bool((pd.Series(s) == "wave2").any())),
        )
        .reset_index()
    )
    # Recompute means correctly using question-row weighted aggregation.
    tmp = (
        student_wave_perf.groupby(["term", "student_id"], dropna=False)
        .agg(
            term_question_rows=("question_rows", "sum"),
            term_grm_sum_category=("grm_sum_category", "sum"),
        )
        .reset_index()
    )
    df = df.drop(columns=["term_question_rows", "term_grm_sum_category", "term_grm_mean_category"]).merge(
        tmp, on=["term", "student_id"], how="left"
    )
    df["term_grm_mean_category"] = np.where(
        df["term_question_rows"] > 0,
        df["term_grm_sum_category"] / df["term_question_rows"],
        np.nan,
    )
    df["substantive_term_participation"] = df["term_question_rows"] >= SUBSTANTIVE_MIN_QUESTION_ROWS
    return df


def build_within_term_outputs(
    pairs_all: pd.DataFrame,
    pairs_sub: pd.DataFrame,
    student_wave_archetype: pd.DataFrame,
    student_wave_state: pd.DataFrame,
    student_wave_error: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if pairs_all.empty:
        return out

    out["within_term_wave_pairs.csv"] = pairs_all
    out["within_term_wave_pairs_substantive.csv"] = pairs_sub

    rank_summary = (
        pairs_sub.groupby("term", dropna=False)
        .agg(
            paired_students=("student_id", "nunique"),
            mean_rank_delta=("rank_pct_delta_w2_minus_w1", "mean"),
            median_rank_delta=("rank_pct_delta_w2_minus_w1", "median"),
            p25_rank_delta=("rank_pct_delta_w2_minus_w1", lambda s: np.nanquantile(pd.to_numeric(s, errors="coerce"), 0.25)),
            p75_rank_delta=("rank_pct_delta_w2_minus_w1", lambda s: np.nanquantile(pd.to_numeric(s, errors="coerce"), 0.75)),
            mean_category_delta=("grm_mean_category_delta_w2_minus_w1", "mean"),
            median_category_delta=("grm_mean_category_delta_w2_minus_w1", "median"),
        )
        .reset_index()
    )
    for c in ["mean_rank_delta", "median_rank_delta", "p25_rank_delta", "p75_rank_delta", "mean_category_delta", "median_category_delta"]:
        rank_summary[c] = pd.to_numeric(rank_summary[c], errors="coerce").round(4)
    out["within_term_rank_change_summary.csv"] = rank_summary

    rank_change_dist = compute_weighted_change_summary(
        pairs_sub, "term", "rank_change_label", weight_col="paired_question_rows_mean", out_label="rank_change_label"
    ).sort_values(["term", "rank_change_label"])
    rank_change_dist["analysis_weight"] = "paired_question_rows_mean"
    out["within_term_rank_change_distribution.csv"] = rank_change_dist

    cat_change_unweighted = compute_weighted_change_summary(
        pairs_sub, "term", "category_change_label", weight_col=None, out_label="category_change_label"
    )
    cat_change_unweighted["weighting"] = "unweighted_students"
    cat_change_weighted = compute_weighted_change_summary(
        pairs_sub, "term", "category_change_label", weight_col="paired_question_rows_mean", out_label="category_change_label"
    )
    cat_change_weighted["weighting"] = "question_count_weighted_students"
    cat_change = pd.concat([cat_change_unweighted, cat_change_weighted], ignore_index=True)
    out["within_term_category_change_summary.csv"] = cat_change.sort_values(["term", "weighting", "category_change_label"])

    # Archetype shifts
    if not student_wave_archetype.empty:
        arch = student_wave_archetype.copy()
        w1 = arch[arch["wave"] == "wave1"][["term", "student_id", "dominant_primary_archetype"]].rename(
            columns={"dominant_primary_archetype": "wave1_primary_archetype"}
        )
        w2 = arch[arch["wave"] == "wave2"][["term", "student_id", "dominant_primary_archetype"]].rename(
            columns={"dominant_primary_archetype": "wave2_primary_archetype"}
        )
        arch_pairs = pairs_sub[["term", "student_id"]].drop_duplicates().merge(w1, on=["term", "student_id"], how="left").merge(
            w2, on=["term", "student_id"], how="left"
        )
        arch_pairs["wave1_primary_archetype"] = arch_pairs["wave1_primary_archetype"].fillna("Unknown")
        arch_pairs["wave2_primary_archetype"] = arch_pairs["wave2_primary_archetype"].fillna("Unknown")
        arch_pairs["same_archetype"] = arch_pairs["wave1_primary_archetype"] == arch_pairs["wave2_primary_archetype"]
        out["within_term_archetype_pairs.csv"] = arch_pairs

        arch_matrix = (
            arch_pairs.groupby(["term", "wave1_primary_archetype", "wave2_primary_archetype"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = arch_matrix.groupby(["term", "wave1_primary_archetype"])["students"].sum().reset_index(name="source_students")
        arch_matrix = arch_matrix.merge(row_den, on=["term", "wave1_primary_archetype"], how="left")
        arch_matrix["pct_of_source"] = np.where(
            arch_matrix["source_students"] > 0, 100.0 * arch_matrix["students"] / arch_matrix["source_students"], np.nan
        )
        out["within_term_archetype_shift_matrix.csv"] = arch_matrix.sort_values(
            ["term", "wave1_primary_archetype", "students"], ascending=[True, True, False]
        )

        targeted = arch_matrix[
            arch_matrix["wave1_primary_archetype"].isin(["Thrasher", "Skeleton-only", "Regression"])
        ].copy()
        out["within_term_archetype_targeted_shifts.csv"] = targeted.sort_values(
            ["term", "wave1_primary_archetype", "students"], ascending=[True, True, False]
        )

    # Dominant-state shifts
    if not student_wave_state.empty:
        st = student_wave_state.copy()
        w1 = st[st["wave"] == "wave1"][
            ["term", "student_id", "dominant_process_state", "dominant_process_state_label", "dominant_process_state_order", "public_run_rows_total"]
        ].rename(
            columns={
                "dominant_process_state": "wave1_dominant_state",
                "dominant_process_state_label": "wave1_dominant_state_label",
                "dominant_process_state_order": "wave1_dominant_state_order",
                "public_run_rows_total": "wave1_public_run_rows_total",
            }
        )
        w2 = st[st["wave"] == "wave2"][
            ["term", "student_id", "dominant_process_state", "dominant_process_state_label", "dominant_process_state_order", "public_run_rows_total"]
        ].rename(
            columns={
                "dominant_process_state": "wave2_dominant_state",
                "dominant_process_state_label": "wave2_dominant_state_label",
                "dominant_process_state_order": "wave2_dominant_state_order",
                "public_run_rows_total": "wave2_public_run_rows_total",
            }
        )
        spairs = pairs_sub[["term", "student_id"]].drop_duplicates().merge(w1, on=["term", "student_id"], how="left").merge(
            w2, on=["term", "student_id"], how="left"
        )
        for c, default in [
            ("wave1_dominant_state", "NO_PUBLIC_RUNS"),
            ("wave2_dominant_state", "NO_PUBLIC_RUNS"),
            ("wave1_dominant_state_label", STATE_LABELS["NO_PUBLIC_RUNS"]),
            ("wave2_dominant_state_label", STATE_LABELS["NO_PUBLIC_RUNS"]),
        ]:
            spairs[c] = spairs[c].fillna(default)
        for c in ["wave1_dominant_state_order", "wave2_dominant_state_order"]:
            spairs[c] = pd.to_numeric(spairs[c], errors="coerce").fillna(STATE_ORDER["NO_PUBLIC_RUNS"]).astype(int)
        for c in ["wave1_public_run_rows_total", "wave2_public_run_rows_total"]:
            spairs[c] = pd.to_numeric(spairs[c], errors="coerce").fillna(0).astype(int)
        spairs["dominant_state_order_delta_w2_minus_w1"] = spairs["wave2_dominant_state_order"] - spairs["wave1_dominant_state_order"]
        spairs["dominant_state_change_label"] = spairs["dominant_state_order_delta_w2_minus_w1"].apply(label_sign)
        spairs.loc[
            (spairs["wave1_dominant_state"] == "NO_PUBLIC_RUNS") | (spairs["wave2_dominant_state"] == "NO_PUBLIC_RUNS"),
            "dominant_state_change_label",
        ] = "missing_public_runs_one_side"
        out["within_term_dominant_state_pairs.csv"] = spairs

        state_matrix = (
            spairs.groupby(["term", "wave1_dominant_state", "wave2_dominant_state"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = state_matrix.groupby(["term", "wave1_dominant_state"])["students"].sum().reset_index(name="source_students")
        state_matrix = state_matrix.merge(row_den, on=["term", "wave1_dominant_state"], how="left")
        state_matrix["pct_of_source"] = np.where(
            state_matrix["source_students"] > 0, 100.0 * state_matrix["students"] / state_matrix["source_students"], np.nan
        )
        out["within_term_dominant_state_shift_matrix.csv"] = state_matrix.sort_values(
            ["term", "wave1_dominant_state", "students"], ascending=[True, True, False]
        )

        state_change_summary = compute_weighted_change_summary(
            spairs, "term", "dominant_state_change_label", weight_col="wave1_public_run_rows_total", out_label="dominant_state_change_label"
        )
        state_change_summary["analysis_weight"] = "wave1_public_run_rows_total"
        out["within_term_dominant_state_shift_summary.csv"] = state_change_summary.sort_values(
            ["term", "dominant_state_change_label"]
        )

        s2_targets = spairs[spairs["wave1_dominant_state"] == "S2_parseable_zero"].copy()
        if not s2_targets.empty:
            s2_targets["escaped_from_s2_to_S3plus"] = s2_targets["wave2_dominant_state"].isin(
                ["S3_public_partial", "S4_public_all", "S5_all_tests"]
            )
            s2_targets["escaped_from_s2_to_S3orS4"] = s2_targets["wave2_dominant_state"].isin(
                ["S3_public_partial", "S4_public_all"]
            )
            s2_summary = (
                s2_targets.groupby("term", dropna=False)
                .agg(
                    source_students=("student_id", "nunique"),
                    escaped_to_S3plus_students=("escaped_from_s2_to_S3plus", lambda s: int(pd.Series(s).sum())),
                    escaped_to_S3orS4_students=("escaped_from_s2_to_S3orS4", lambda s: int(pd.Series(s).sum())),
                )
                .reset_index()
            )
            s2_summary["pct_escaped_to_S3plus"] = np.where(
                s2_summary["source_students"] > 0,
                100.0 * s2_summary["escaped_to_S3plus_students"] / s2_summary["source_students"],
                np.nan,
            )
            s2_summary["pct_escaped_to_S3orS4"] = np.where(
                s2_summary["source_students"] > 0,
                100.0 * s2_summary["escaped_to_S3orS4_students"] / s2_summary["source_students"],
                np.nan,
            )
            out["within_term_s2_dominant_escape_summary.csv"] = s2_summary

    # Within-term error profile shifts (wave1->wave2)
    if not student_wave_error.empty:
        e = student_wave_error.copy()
        w1 = e[["term", "wave", "student_id", "dominant_error_profile_bucket", "dominant_final_primary_taxonomy", "dominant_runtime_error_type"]]
        w1 = w1[w1["wave"] == "wave1"].drop(columns=["wave"]).rename(
            columns={
                "dominant_error_profile_bucket": "wave1_dominant_error_profile_bucket",
                "dominant_final_primary_taxonomy": "wave1_dominant_final_primary_taxonomy",
                "dominant_runtime_error_type": "wave1_dominant_runtime_error_type",
            }
        )
        w2 = e[["term", "wave", "student_id", "dominant_error_profile_bucket", "dominant_final_primary_taxonomy", "dominant_runtime_error_type"]]
        w2 = w2[w2["wave"] == "wave2"].drop(columns=["wave"]).rename(
            columns={
                "dominant_error_profile_bucket": "wave2_dominant_error_profile_bucket",
                "dominant_final_primary_taxonomy": "wave2_dominant_final_primary_taxonomy",
                "dominant_runtime_error_type": "wave2_dominant_runtime_error_type",
            }
        )
        epairs = pairs_sub[["term", "student_id"]].drop_duplicates().merge(w1, on=["term", "student_id"], how="left").merge(
            w2, on=["term", "student_id"], how="left"
        )
        for c in ["wave1_dominant_error_profile_bucket", "wave2_dominant_error_profile_bucket"]:
            epairs[c] = epairs[c].fillna("Unknown")
        out["within_term_error_profile_pairs.csv"] = epairs
        ematrix = (
            epairs.groupby(["term", "wave1_dominant_error_profile_bucket", "wave2_dominant_error_profile_bucket"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = ematrix.groupby(["term", "wave1_dominant_error_profile_bucket"])["students"].sum().reset_index(name="source_students")
        ematrix = ematrix.merge(row_den, on=["term", "wave1_dominant_error_profile_bucket"], how="left")
        ematrix["pct_of_source"] = np.where(ematrix["source_students"] > 0, 100.0 * ematrix["students"] / ematrix["source_students"], np.nan)
        out["within_term_error_profile_shift_matrix.csv"] = ematrix.sort_values(
            ["term", "wave1_dominant_error_profile_bucket", "students"], ascending=[True, True, False]
        )

    return out


def build_cross_term_pairs(
    student_term_perf: pd.DataFrame,
    student_term_archetype: pd.DataFrame,
    student_term_state: pd.DataFrame,
    student_term_error: pd.DataFrame,
    student_term_construct: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    outputs: dict[str, pd.DataFrame] = {}
    if student_term_perf.empty:
        return pd.DataFrame(), outputs

    t = student_term_perf.copy()
    t["substantive_term_participation"] = t["substantive_term_participation"].fillna(False).astype(bool)

    pair_rows: list[pd.DataFrame] = []
    for term_from, term_to in [("25t1", "25t2"), ("25t2", "25t3")]:
        left = t[t["term"] == term_from].copy()
        right = t[t["term"] == term_to].copy()
        p = left.merge(right, on="student_id", how="inner", suffixes=("_from", "_to"))
        if p.empty:
            continue
        p["term_pair"] = f"{term_from}->{term_to}"
        p["substantive_pair"] = p["substantive_term_participation_from"] & p["substantive_term_participation_to"]
        p["term_grm_mean_category_delta_to_minus_from"] = p["term_grm_mean_category_to"] - p["term_grm_mean_category_from"]
        p["term_grm_sum_category_delta_to_minus_from"] = p["term_grm_sum_category_to"] - p["term_grm_sum_category_from"]
        p["term_questions_any_test_pass_delta_to_minus_from"] = (
            p["term_questions_any_test_pass_to"] - p["term_questions_any_test_pass_from"]
        )
        p["term_category_change_label"] = p["term_grm_mean_category_delta_to_minus_from"].apply(label_sign)
        pair_rows.append(p)
    term_pairs = pd.concat(pair_rows, ignore_index=True) if pair_rows else pd.DataFrame()
    outputs["cross_term_term_pairs.csv"] = term_pairs

    # Coverage summary
    if not term_pairs.empty:
        cov = (
            term_pairs.groupby("term_pair", dropna=False)
            .agg(
                repeat_students_raw=("student_id", "nunique"),
                repeat_students_substantive=("substantive_pair", lambda s: int(pd.Series(s).sum())),
                avg_question_rows_from=("term_question_rows_from", "mean"),
                avg_question_rows_to=("term_question_rows_to", "mean"),
            )
            .reset_index()
        )
        for c in ["avg_question_rows_from", "avg_question_rows_to"]:
            cov[c] = pd.to_numeric(cov[c], errors="coerce").round(2)
        outputs["cross_term_repeat_coverage.csv"] = cov

    # Join term-level archetype / state / error / construct summaries
    if not term_pairs.empty and not student_term_archetype.empty:
        arch = student_term_archetype[["term", "student_id", "dominant_primary_archetype"]].copy()
        arch_from = arch.rename(columns={"term": "term_from", "dominant_primary_archetype": "dominant_primary_archetype_from"})
        arch_to = arch.rename(columns={"term": "term_to", "dominant_primary_archetype": "dominant_primary_archetype_to"})
        term_pairs = term_pairs.merge(arch_from, on=["term_from", "student_id"], how="left").merge(
            arch_to, on=["term_to", "student_id"], how="left"
        )
        term_pairs["dominant_primary_archetype_from"] = term_pairs["dominant_primary_archetype_from"].fillna("Unknown")
        term_pairs["dominant_primary_archetype_to"] = term_pairs["dominant_primary_archetype_to"].fillna("Unknown")

        amatrix = (
            term_pairs[term_pairs["substantive_pair"]]
            .groupby(["term_pair", "dominant_primary_archetype_from", "dominant_primary_archetype_to"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = amatrix.groupby(["term_pair", "dominant_primary_archetype_from"])["students"].sum().reset_index(name="source_students")
        amatrix = amatrix.merge(row_den, on=["term_pair", "dominant_primary_archetype_from"], how="left")
        amatrix["pct_of_source"] = np.where(amatrix["source_students"] > 0, 100.0 * amatrix["students"] / amatrix["source_students"], np.nan)
        outputs["cross_term_archetype_shift_matrix.csv"] = amatrix.sort_values(
            ["term_pair", "dominant_primary_archetype_from", "students"], ascending=[True, True, False]
        )

    if not term_pairs.empty and not student_term_state.empty:
        st = student_term_state[["term", "student_id", "dominant_process_state", "dominant_process_state_order", "dominant_process_state_label"]].copy()
        st_from = st.rename(
            columns={
                "term": "term_from",
                "dominant_process_state": "dominant_process_state_from",
                "dominant_process_state_order": "dominant_process_state_order_from",
                "dominant_process_state_label": "dominant_process_state_label_from",
            }
        )
        st_to = st.rename(
            columns={
                "term": "term_to",
                "dominant_process_state": "dominant_process_state_to",
                "dominant_process_state_order": "dominant_process_state_order_to",
                "dominant_process_state_label": "dominant_process_state_label_to",
            }
        )
        term_pairs = term_pairs.merge(st_from, on=["term_from", "student_id"], how="left").merge(
            st_to, on=["term_to", "student_id"], how="left"
        )
        for c in ["dominant_process_state_from", "dominant_process_state_to"]:
            term_pairs[c] = term_pairs[c].fillna("NO_PUBLIC_RUNS")
        for c in ["dominant_process_state_order_from", "dominant_process_state_order_to"]:
            term_pairs[c] = pd.to_numeric(term_pairs[c], errors="coerce").fillna(STATE_ORDER["NO_PUBLIC_RUNS"]).astype(int)
        term_pairs["dominant_state_order_delta_to_minus_from"] = (
            term_pairs["dominant_process_state_order_to"] - term_pairs["dominant_process_state_order_from"]
        )
        term_pairs["dominant_state_change_label"] = term_pairs["dominant_state_order_delta_to_minus_from"].apply(label_sign)

        smatrix = (
            term_pairs[term_pairs["substantive_pair"]]
            .groupby(["term_pair", "dominant_process_state_from", "dominant_process_state_to"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = smatrix.groupby(["term_pair", "dominant_process_state_from"])["students"].sum().reset_index(name="source_students")
        smatrix = smatrix.merge(row_den, on=["term_pair", "dominant_process_state_from"], how="left")
        smatrix["pct_of_source"] = np.where(smatrix["source_students"] > 0, 100.0 * smatrix["students"] / smatrix["source_students"], np.nan)
        outputs["cross_term_dominant_state_shift_matrix.csv"] = smatrix.sort_values(
            ["term_pair", "dominant_process_state_from", "students"], ascending=[True, True, False]
        )

        s2 = term_pairs[
            term_pairs["substantive_pair"] & (term_pairs["dominant_process_state_from"] == "S2_parseable_zero")
        ].copy()
        if not s2.empty:
            s2["escaped_to_S3plus"] = s2["dominant_process_state_to"].isin(["S3_public_partial", "S4_public_all", "S5_all_tests"])
            s2["escaped_to_S3orS4"] = s2["dominant_process_state_to"].isin(["S3_public_partial", "S4_public_all"])
            s2_summary = (
                s2.groupby("term_pair", dropna=False)
                .agg(
                    source_students=("student_id", "nunique"),
                    escaped_to_S3plus_students=("escaped_to_S3plus", lambda s: int(pd.Series(s).sum())),
                    escaped_to_S3orS4_students=("escaped_to_S3orS4", lambda s: int(pd.Series(s).sum())),
                )
                .reset_index()
            )
            s2_summary["pct_escaped_to_S3plus"] = np.where(
                s2_summary["source_students"] > 0, 100.0 * s2_summary["escaped_to_S3plus_students"] / s2_summary["source_students"], np.nan
            )
            s2_summary["pct_escaped_to_S3orS4"] = np.where(
                s2_summary["source_students"] > 0, 100.0 * s2_summary["escaped_to_S3orS4_students"] / s2_summary["source_students"], np.nan
            )
            outputs["cross_term_s2_escape_summary.csv"] = s2_summary

    if not term_pairs.empty and not student_term_error.empty:
        err = student_term_error[
            [
                "term",
                "student_id",
                "dominant_error_profile_bucket",
                "dominant_final_primary_taxonomy",
                "dominant_runtime_error_type",
                "runtime_error_rows",
                "wrong_logic_rows",
                "syntax_gated_rows",
                "question_rows",
            ]
        ].copy()
        err_from = err.rename(
            columns={
                "term": "term_from",
                "dominant_error_profile_bucket": "dominant_error_profile_bucket_from",
                "dominant_final_primary_taxonomy": "dominant_final_primary_taxonomy_from",
                "dominant_runtime_error_type": "dominant_runtime_error_type_from",
                "runtime_error_rows": "runtime_error_rows_from",
                "wrong_logic_rows": "wrong_logic_rows_from",
                "syntax_gated_rows": "syntax_gated_rows_from",
                "question_rows": "error_question_rows_from",
            }
        )
        err_to = err.rename(
            columns={
                "term": "term_to",
                "dominant_error_profile_bucket": "dominant_error_profile_bucket_to",
                "dominant_final_primary_taxonomy": "dominant_final_primary_taxonomy_to",
                "dominant_runtime_error_type": "dominant_runtime_error_type_to",
                "runtime_error_rows": "runtime_error_rows_to",
                "wrong_logic_rows": "wrong_logic_rows_to",
                "syntax_gated_rows": "syntax_gated_rows_to",
                "question_rows": "error_question_rows_to",
            }
        )
        term_pairs = term_pairs.merge(err_from, on=["term_from", "student_id"], how="left").merge(
            err_to, on=["term_to", "student_id"], how="left"
        )
        for c in ["dominant_error_profile_bucket_from", "dominant_error_profile_bucket_to"]:
            term_pairs[c] = term_pairs[c].fillna("Unknown")
        term_pairs["error_progress_order_from"] = term_pairs["dominant_error_profile_bucket_from"].map(ERROR_PROGRESS_ORDER).fillna(-1).astype(int)
        term_pairs["error_progress_order_to"] = term_pairs["dominant_error_profile_bucket_to"].map(ERROR_PROGRESS_ORDER).fillna(-1).astype(int)
        term_pairs["error_progress_delta_to_minus_from"] = term_pairs["error_progress_order_to"] - term_pairs["error_progress_order_from"]
        term_pairs["error_progress_label"] = term_pairs["error_progress_delta_to_minus_from"].apply(label_sign)
        outputs["cross_term_error_pairs.csv"] = term_pairs[
            [
                "student_id", "term_pair", "substantive_pair",
                "dominant_error_profile_bucket_from", "dominant_error_profile_bucket_to",
                "dominant_final_primary_taxonomy_from", "dominant_final_primary_taxonomy_to",
                "dominant_runtime_error_type_from", "dominant_runtime_error_type_to",
                "error_progress_delta_to_minus_from", "error_progress_label",
                "syntax_gated_rows_from", "syntax_gated_rows_to",
                "wrong_logic_rows_from", "wrong_logic_rows_to",
                "runtime_error_rows_from", "runtime_error_rows_to",
            ]
        ].copy()

        ematrix = (
            term_pairs[term_pairs["substantive_pair"]]
            .groupby(["term_pair", "dominant_error_profile_bucket_from", "dominant_error_profile_bucket_to"], dropna=False)
            .size()
            .reset_index(name="students")
        )
        row_den = ematrix.groupby(["term_pair", "dominant_error_profile_bucket_from"])["students"].sum().reset_index(name="source_students")
        ematrix = ematrix.merge(row_den, on=["term_pair", "dominant_error_profile_bucket_from"], how="left")
        ematrix["pct_of_source"] = np.where(ematrix["source_students"] > 0, 100.0 * ematrix["students"] / ematrix["source_students"], np.nan)
        outputs["cross_term_error_shift_matrix.csv"] = ematrix.sort_values(
            ["term_pair", "dominant_error_profile_bucket_from", "students"], ascending=[True, True, False]
        )

        # Syntax -> logic/edge/etc progression summary
        syn = term_pairs[term_pairs["substantive_pair"] & (term_pairs["dominant_error_profile_bucket_from"] == "Syntax gated")].copy()
        if not syn.empty:
            syn["moved_to_runtime_or_wrong_output"] = syn["dominant_error_profile_bucket_to"].isin(
                ["Runtime error", "Wrong output - logic", "Wrong output - edge/partial", "Wrong output - unspecified"]
            )
            syn["moved_to_wrong_output_logic"] = syn["dominant_error_profile_bucket_to"].eq("Wrong output - logic")
            syn["moved_to_pass_like"] = syn["dominant_error_profile_bucket_to"].isin(
                ["Partial pass", "Full pass", "Public full pass, no submit"]
            )
            syn_summary = (
                syn.groupby("term_pair", dropna=False)
                .agg(
                    source_students=("student_id", "nunique"),
                    moved_to_runtime_or_wrong_output_students=("moved_to_runtime_or_wrong_output", lambda s: int(pd.Series(s).sum())),
                    moved_to_wrong_output_logic_students=("moved_to_wrong_output_logic", lambda s: int(pd.Series(s).sum())),
                    moved_to_pass_like_students=("moved_to_pass_like", lambda s: int(pd.Series(s).sum())),
                )
                .reset_index()
            )
            for col in [
                "moved_to_runtime_or_wrong_output_students",
                "moved_to_wrong_output_logic_students",
                "moved_to_pass_like_students",
            ]:
                syn_summary[f"pct_{col.replace('_students', '')}"] = np.where(
                    syn_summary["source_students"] > 0, 100.0 * syn_summary[col] / syn_summary["source_students"], np.nan
                )
            outputs["cross_term_syntax_progression_summary.csv"] = syn_summary

        # Runtime subtype persistence
        rt = term_pairs[
            term_pairs["substantive_pair"]
            & (term_pairs["dominant_error_profile_bucket_from"] == "Runtime error")
            & (term_pairs["dominant_error_profile_bucket_to"] == "Runtime error")
            & term_pairs["dominant_runtime_error_type_from"].notna()
            & term_pairs["dominant_runtime_error_type_to"].notna()
        ].copy()
        if not rt.empty:
            rt["same_runtime_type"] = rt["dominant_runtime_error_type_from"] == rt["dominant_runtime_error_type_to"]
            rt_summary = (
                rt.groupby(["term_pair", "dominant_runtime_error_type_from"], dropna=False)
                .agg(
                    students=("student_id", "nunique"),
                    same_runtime_type_students=("same_runtime_type", lambda s: int(pd.Series(s).sum())),
                )
                .reset_index()
            )
            rt_summary["pct_same_runtime_type"] = np.where(
                rt_summary["students"] > 0, 100.0 * rt_summary["same_runtime_type_students"] / rt_summary["students"], np.nan
            )
            outputs["cross_term_runtime_type_persistence.csv"] = rt_summary.sort_values(
                ["term_pair", "students"], ascending=[True, False]
            )

    if not term_pairs.empty and not student_term_construct.empty:
        c = student_term_construct.copy()
        c_from = c.rename(columns={"term": "term_from"})
        c_to = c.rename(columns={"term": "term_to"})
        term_pairs = term_pairs.merge(c_from, on=["term_from", "student_id"], how="left", suffixes=("", "_cf_from"))
        term_pairs = term_pairs.merge(c_to, on=["term_to", "student_id"], how="left", suffixes=("", "_cf_to"))

        summaries: list[dict[str, Any]] = []
        sub = term_pairs[term_pairs["substantive_pair"]].copy()
        for construct in KEY_CONSTRUCTS:
            ever_from = f"ever_{construct}"
            ever_to = f"ever_{construct}"
            rate_from = f"rate_{construct}"
            rate_to = f"rate_{construct}"
            # After merge, duplicate names are suffixed by pandas; map explicitly.
            if f"{ever_from}_x" in sub.columns and f"{ever_to}_y" in sub.columns:
                ef = sub[f"{ever_from}_x"].fillna(False).astype(bool)
                et = sub[f"{ever_to}_y"].fillna(False).astype(bool)
                rf = pd.to_numeric(sub[f"{rate_from}_x"], errors="coerce")
                rt = pd.to_numeric(sub[f"{rate_to}_y"], errors="coerce")
            elif f"{ever_from}_from" in sub.columns and f"{ever_to}_to" in sub.columns:
                ef = sub[f"{ever_from}_from"].fillna(False).astype(bool)
                et = sub[f"{ever_to}_to"].fillna(False).astype(bool)
                rf = pd.to_numeric(sub[f"{rate_from}_from"], errors="coerce")
                rt = pd.to_numeric(sub[f"{rate_to}_to"], errors="coerce")
            else:
                # pandas suffixes from the merge above are '' and '_cf_to'; first merge kept unsuffixed names.
                ef = sub.get(ever_from, pd.Series(False, index=sub.index)).fillna(False).astype(bool)
                et = sub.get(f"{ever_to}_cf_to", pd.Series(False, index=sub.index)).fillna(False).astype(bool)
                rf = pd.to_numeric(sub.get(rate_from, pd.Series(np.nan, index=sub.index)), errors="coerce")
                rt = pd.to_numeric(sub.get(f"{rate_to}_cf_to", pd.Series(np.nan, index=sub.index)), errors="coerce")

            tmp = sub[["term_pair", "student_id"]].copy()
            tmp["ever_from"] = ef
            tmp["ever_to"] = et
            tmp["rate_delta"] = rt - rf
            for term_pair, g in tmp.groupby("term_pair", dropna=False):
                n = g["student_id"].nunique()
                summaries.append(
                    {
                        "term_pair": term_pair,
                        "construct": construct,
                        "students": int(n),
                        "ever_from_students": int(g["ever_from"].sum()),
                        "ever_to_students": int(g["ever_to"].sum()),
                        "newly_appears_students": int((~g["ever_from"] & g["ever_to"]).sum()),
                        "lost_construct_students": int((g["ever_from"] & ~g["ever_to"]).sum()),
                        "increased_consistency_students": int((g["rate_delta"] > 1e-12).sum()),
                        "decreased_consistency_students": int((g["rate_delta"] < -1e-12).sum()),
                        "median_rate_delta": float(np.nanmedian(g["rate_delta"])) if len(g) else np.nan,
                        "mean_rate_delta": float(np.nanmean(g["rate_delta"])) if len(g) else np.nan,
                    }
                )
        outputs["cross_term_construct_progression_summary.csv"] = pd.DataFrame(summaries).sort_values(
            ["term_pair", "construct"]
        )

    outputs["cross_term_term_pairs_enriched.csv"] = term_pairs
    return term_pairs, outputs


def build_all_three_outputs(
    student_term_perf: pd.DataFrame,
    student_term_archetype: pd.DataFrame,
    student_term_state: pd.DataFrame,
    student_term_error: pd.DataFrame,
    student_term_construct: pd.DataFrame,
    within_term_pairs_sub: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if student_term_perf.empty:
        return out

    perf = student_term_perf.copy()
    perf["substantive_term_participation"] = perf["substantive_term_participation"].fillna(False).astype(bool)

    p = perf.pivot_table(
        index="student_id",
        columns="term",
        values="substantive_term_participation",
        aggfunc="max",
        fill_value=False,
    ).reset_index()
    for t in ["25t1", "25t2", "25t3"]:
        if t not in p.columns:
            p[t] = False
    all_three_sub = p[(p["25t1"]) & (p["25t2"]) & (p["25t3"])][["student_id"]].copy()
    all_three_raw = (
        perf.groupby("student_id", dropna=False)["term"]
        .nunique()
        .reset_index(name="terms_seen")
        .query("terms_seen >= 3")[["student_id"]]
        .copy()
    )

    out["all_three_term_students_substantive.csv"] = all_three_sub
    out["all_three_term_students_raw.csv"] = all_three_raw

    if all_three_sub.empty:
        return out

    # Long table of per-term summaries for the cohort.
    term_rows = perf[perf["student_id"].isin(all_three_sub["student_id"])].copy()
    if not student_term_archetype.empty:
        term_rows = term_rows.merge(
            student_term_archetype[["term", "student_id", "dominant_primary_archetype", "dominant_share"]].rename(
                columns={"dominant_share": "archetype_dominant_share"}
            ),
            on=["term", "student_id"],
            how="left",
        )
    if not student_term_state.empty:
        term_rows = term_rows.merge(
            student_term_state[
                ["term", "student_id", "dominant_process_state", "dominant_process_state_label", "dominant_process_state_order", "public_run_rows_total"]
            ],
            on=["term", "student_id"],
            how="left",
        )
    if not student_term_error.empty:
        term_rows = term_rows.merge(
            student_term_error[
                [
                    "term",
                    "student_id",
                    "dominant_error_profile_bucket",
                    "dominant_final_primary_taxonomy",
                    "dominant_runtime_error_type",
                    "runtime_error_rows",
                    "wrong_logic_rows",
                    "syntax_gated_rows",
                    "full_pass_rows",
                    "partial_pass_rows",
                ]
            ],
            on=["term", "student_id"],
            how="left",
        )
    if not student_term_construct.empty:
        keep = ["term", "student_id"]
        for c in ["function_def", "for_loop", "if_stmt"]:
            keep += [f"ever_{c}", f"rate_{c}"]
        term_rows = term_rows.merge(student_term_construct[keep], on=["term", "student_id"], how="left")

    out["all_three_term_student_term_rows.csv"] = term_rows.sort_values(["student_id", "term"])

    # Trajectory strings
    def seq_table(df: pd.DataFrame, col: str, out_name: str, label_name: str) -> pd.DataFrame:
        parts = []
        for sid, g in df.sort_values(["student_id", "term"]).groupby("student_id", dropna=False):
            vals = {r["term"]: ("" if pd.isna(r[col]) else str(r[col])) for _, r in g.iterrows()}
            seq = " -> ".join(vals.get(t, "MISSING") or "MISSING" for t in ["25t1", "25t2", "25t3"])
            parts.append({"student_id": sid, "trajectory": seq})
        traj = pd.DataFrame(parts)
        summary = traj.groupby("trajectory", dropna=False).size().reset_index(name="students").sort_values("students", ascending=False)
        summary = summary.rename(columns={"trajectory": label_name})
        out[out_name] = summary
        return traj

    err_traj = seq_table(term_rows, "dominant_error_profile_bucket", "all_three_term_error_trajectory_summary.csv", "error_trajectory")
    arch_traj = seq_table(term_rows, "dominant_primary_archetype", "all_three_term_archetype_trajectory_summary.csv", "archetype_trajectory")
    state_traj = seq_table(term_rows, "dominant_process_state", "all_three_term_state_trajectory_summary.csv", "state_trajectory")

    traj = all_three_sub.copy()
    traj = traj.merge(err_traj.rename(columns={"trajectory": "error_trajectory"}), on="student_id", how="left")
    traj = traj.merge(arch_traj.rename(columns={"trajectory": "archetype_trajectory"}), on="student_id", how="left")
    traj = traj.merge(state_traj.rename(columns={"trajectory": "state_trajectory"}), on="student_id", how="left")
    out["all_three_term_trajectories.csv"] = traj

    # Term-level t3 success proxy for the full substantive all-three cohort.
    t3_term = term_rows[term_rows["term"] == "25t3"].copy()
    if not t3_term.empty:
        t3_term["t3_term_high_success_proxy"] = (
            t3_term["dominant_error_profile_bucket"].isin(["Full pass", "Partial pass", "Public full pass, no submit"])
            | (pd.to_numeric(t3_term["term_grm_mean_category"], errors="coerce") >= 1.4)
            | t3_term.get("dominant_process_state", pd.Series(index=t3_term.index, dtype="object")).isin(["S4_public_all", "S5_all_tests"])
        )
        out["all_three_term_t3_term_level_proxy_rows.csv"] = t3_term.sort_values(
            ["t3_term_high_success_proxy", "term_grm_mean_category", "student_id"],
            ascending=[False, False, True],
        )
        t3_term_summary = (
            t3_term.groupby("t3_term_high_success_proxy", dropna=False)
            .agg(
                students=("student_id", "nunique"),
                mean_term_grm_mean_category=("term_grm_mean_category", "mean"),
                median_term_grm_mean_category=("term_grm_mean_category", "median"),
                mean_term_questions_any_test_pass=("term_questions_any_test_pass", "mean"),
                pct_with_pass_like_dominant_error=(
                    "dominant_error_profile_bucket",
                    lambda s: float(pd.Series(s).isin(["Full pass", "Partial pass", "Public full pass, no submit"]).mean()),
                ),
                pct_with_S4_or_S5_dominant_state=(
                    "dominant_process_state",
                    lambda s: float(pd.Series(s).isin(["S4_public_all", "S5_all_tests"]).mean()),
                ),
            )
            .reset_index()
            .sort_values("t3_term_high_success_proxy", ascending=False)
        )
        out["all_three_term_t3_term_level_success_proxy_summary.csv"] = t3_term_summary

    # t3 success is not directly observable as "exit" (no t4); use high-success proxy based on t3 wave2 performance + dominant state.
    t3w2 = within_term_pairs_sub[within_term_pairs_sub["term"] == "25t3"].copy()
    t3w2 = t3w2[t3w2["student_id"].isin(all_three_sub["student_id"])]
    if not t3w2.empty:
        t3w2["t3_high_success_proxy"] = (
            (pd.to_numeric(t3w2["grm_mean_category_w2"], errors="coerce") >= 1.5)
            | (pd.to_numeric(t3w2["wave_rank_pct_w2"], errors="coerce") >= 0.75)
        )
        # If state info is available, strengthen proxy with S4/S5 dominant in wave2.
        if not student_term_state.empty:
            # We only have term-level state here. Build wave-level from within-term state outputs outside this function isn't available directly.
            pass
        proxy_summary = (
            t3w2.groupby("t3_high_success_proxy", dropna=False)
            .agg(
                students=("student_id", "nunique"),
                mean_wave2_rank_pct=("wave_rank_pct_w2", "mean"),
                mean_wave2_grm_mean_category=("grm_mean_category_w2", "mean"),
                mean_rank_delta=("rank_pct_delta_w2_minus_w1", "mean"),
                mean_category_delta=("grm_mean_category_delta_w2_minus_w1", "mean"),
            )
            .reset_index()
            .sort_values("t3_high_success_proxy", ascending=False)
        )
        out["all_three_term_t3_success_proxy_summary.csv"] = proxy_summary

        # Compare t1->t2 and t2->t3 internal changes for proxy-vs-non-proxy students
        features = t3w2[[
            "student_id",
            "t3_high_success_proxy",
            "wave_rank_pct_w1",
            "wave_rank_pct_w2",
            "grm_mean_category_w1",
            "grm_mean_category_w2",
            "rank_pct_delta_w2_minus_w1",
            "grm_mean_category_delta_w2_minus_w1",
            "questions_any_test_pass_w1",
            "questions_any_test_pass_w2",
        ]].copy()
        # attach term1/term2 summaries for trajectory context
        term_subset = term_rows[term_rows["term"].isin(["25t1", "25t2", "25t3"])].copy()
        wide_parts = []
        for term in ["25t1", "25t2", "25t3"]:
            gt = term_subset[term_subset["term"] == term].copy()
            keep_cols = ["student_id", "dominant_error_profile_bucket", "dominant_primary_archetype", "dominant_process_state"]
            gt = gt[keep_cols].rename(columns={
                "dominant_error_profile_bucket": f"{term}_dominant_error_profile_bucket",
                "dominant_primary_archetype": f"{term}_dominant_primary_archetype",
                "dominant_process_state": f"{term}_dominant_process_state",
            })
            wide_parts.append(gt)
        comp = features
        for part in wide_parts:
            comp = comp.merge(part, on="student_id", how="left")
        out["all_three_term_t3_success_proxy_feature_comparison.csv"] = comp.sort_values(
            ["t3_high_success_proxy", "grm_mean_category_w2", "wave_rank_pct_w2"],
            ascending=[False, False, False],
        )

    return out


def build_pass_through_model(
    within_term_pairs_sub: pd.DataFrame,
    student_wave_archetype: pd.DataFrame,
    student_wave_error: pd.DataFrame,
    student_wave_state: pd.DataFrame,
    student_term_perf: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], Pipeline | None, list[str], list[str]]:
    outputs: dict[str, pd.DataFrame] = {}
    if within_term_pairs_sub.empty:
        return outputs, None, [], []

    model_df = within_term_pairs_sub[within_term_pairs_sub["term"].isin(["25t1", "25t2"])].copy()
    if model_df.empty:
        return outputs, None, [], []

    # Start-of-term features = wave1 summaries.
    if not student_wave_archetype.empty:
        a = student_wave_archetype[student_wave_archetype["wave"] == "wave1"][
            ["term", "student_id", "dominant_primary_archetype"]
        ].rename(columns={"dominant_primary_archetype": "wave1_primary_archetype"})
        model_df = model_df.merge(a, on=["term", "student_id"], how="left")
    if not student_wave_error.empty:
        e = student_wave_error[student_wave_error["wave"] == "wave1"][
            ["term", "student_id", "dominant_error_profile_bucket", "dominant_final_primary_taxonomy", "dominant_runtime_error_type"]
        ].rename(
            columns={
                "dominant_error_profile_bucket": "wave1_dominant_error_profile_bucket",
                "dominant_final_primary_taxonomy": "wave1_dominant_final_primary_taxonomy",
                "dominant_runtime_error_type": "wave1_dominant_runtime_error_type",
            }
        )
        model_df = model_df.merge(e, on=["term", "student_id"], how="left")
    if not student_wave_state.empty:
        s = student_wave_state[student_wave_state["wave"] == "wave1"][
            ["term", "student_id", "dominant_process_state", "dominant_process_state_order"]
        ].rename(
            columns={
                "dominant_process_state": "wave1_dominant_state",
                "dominant_process_state_order": "wave1_dominant_state_order",
            }
        )
        model_df = model_df.merge(s, on=["term", "student_id"], how="left")

    # Observed exit = not present in next term (substantive term participation)
    term_presence = student_term_perf[["term", "student_id", "substantive_term_participation"]].copy()
    term_presence["substantive_term_participation"] = term_presence["substantive_term_participation"].fillna(False).astype(bool)
    next_rows = []
    for _, r in model_df[["term", "student_id"]].drop_duplicates().iterrows():
        next_term = NEXT_TERM.get(r["term"])
        next_rows.append({"term": r["term"], "student_id": r["student_id"], "next_term": next_term})
    next_df = pd.DataFrame(next_rows).drop_duplicates()
    if not next_df.empty:
        next_presence = term_presence.rename(columns={"term": "next_term", "substantive_term_participation": "appears_next_term_substantive"})
        model_df = model_df.merge(next_df, on=["term", "student_id"], how="left").merge(
            next_presence, on=["next_term", "student_id"], how="left"
        )
    else:
        model_df["next_term"] = pd.NA
        model_df["appears_next_term_substantive"] = pd.NA
    model_df["appears_next_term_substantive"] = model_df["appears_next_term_substantive"].fillna(False).astype(bool)
    model_df["exit_after_term_observed"] = ~model_df["appears_next_term_substantive"]

    # Feature engineering
    model_df["wave1_primary_archetype"] = model_df["wave1_primary_archetype"].fillna("Unknown")
    model_df["wave1_dominant_error_profile_bucket"] = model_df["wave1_dominant_error_profile_bucket"].fillna("Unknown")
    model_df["wave1_dominant_state"] = model_df["wave1_dominant_state"].fillna("NO_PUBLIC_RUNS")
    model_df["wave1_dominant_state_order"] = pd.to_numeric(model_df["wave1_dominant_state_order"], errors="coerce").fillna(-1)
    model_df["wave1_question_pass_rate"] = np.where(
        pd.to_numeric(model_df["question_rows_w1"], errors="coerce") > 0,
        pd.to_numeric(model_df["questions_any_test_pass_w1"], errors="coerce") / pd.to_numeric(model_df["question_rows_w1"], errors="coerce"),
        np.nan,
    )
    model_df["wave2_question_pass_rate"] = np.where(
        pd.to_numeric(model_df["question_rows_w2"], errors="coerce") > 0,
        pd.to_numeric(model_df["questions_any_test_pass_w2"], errors="coerce") / pd.to_numeric(model_df["question_rows_w2"], errors="coerce"),
        np.nan,
    )

    outputs["pass_through_model_dataset.csv"] = model_df

    feature_cols_num = [
        "wave_rank_pct_w1",
        "wave_rank_pct_w2",
        "rank_pct_delta_w2_minus_w1",
        "grm_mean_category_w1",
        "grm_mean_category_w2",
        "grm_mean_category_delta_w2_minus_w1",
        "question_rows_w1",
        "question_rows_w2",
        "questions_any_test_pass_w1",
        "questions_any_test_pass_w2",
        "questions_any_test_pass_delta_w2_minus_w1",
        "wave1_question_pass_rate",
        "wave2_question_pass_rate",
        "wave1_dominant_state_order",
    ]
    feature_cols_cat = [
        "term",
        "wave1_primary_archetype",
        "wave1_dominant_error_profile_bucket",
        "wave1_dominant_state",
        "rank_change_label",
        "category_change_label",
    ]
    use_cols = feature_cols_num + feature_cols_cat
    fit_df = model_df.dropna(subset=["exit_after_term_observed"]).copy()
    if fit_df["exit_after_term_observed"].nunique() < 2 or len(fit_df) < 50:
        perf = pd.DataFrame([{
            "n_rows": int(len(fit_df)),
            "positive_rate_exit_after_term_observed": float(fit_df["exit_after_term_observed"].mean()) if len(fit_df) else np.nan,
            "cv_auc": np.nan,
            "cv_brier": np.nan,
            "note": "Insufficient class variation for logistic model",
        }])
        outputs["pass_through_model_performance.csv"] = perf
        return outputs, None, feature_cols_num, feature_cols_cat

    X = fit_df[use_cols].copy()
    y = fit_df["exit_after_term_observed"].astype(int).to_numpy()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, feature_cols_num),
            ("cat", categorical_transformer, feature_cols_cat),
        ]
    )
    clf = LogisticRegression(max_iter=2000, solver="lbfgs")
    pipe = Pipeline(steps=[("prep", preprocessor), ("clf", clf)])

    # Cross-validated predictions for performance
    min_class = int(pd.Series(y).value_counts().min())
    n_splits = max(3, min(5, min_class))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    prob_cv = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
    auc = roc_auc_score(y, prob_cv)
    brier = brier_score_loss(y, prob_cv)
    perf = pd.DataFrame(
        [{
            "n_rows": int(len(fit_df)),
            "n_positive_exit_after_term_observed": int(y.sum()),
            "positive_rate_exit_after_term_observed": float(y.mean()),
            "cv_splits": int(n_splits),
            "cv_auc": float(auc),
            "cv_brier": float(brier),
            "outcome_definition": "exit_after_term_observed = not present in next term (substantive participation)",
            "caveat": "Exit proxy may mix passing and attrition",
        }]
    )
    outputs["pass_through_model_performance.csv"] = perf

    # Fit on full data for coefficients and segment tables
    pipe.fit(X, y)
    prob_full = pipe.predict_proba(X)[:, 1]
    fit_df = fit_df.copy()
    fit_df["pred_exit_probability"] = prob_full
    outputs["pass_through_model_scored_rows.csv"] = fit_df

    # Coefficients
    prep: ColumnTransformer = pipe.named_steps["prep"]
    coef = pipe.named_steps["clf"].coef_[0]
    feature_names = prep.get_feature_names_out()
    coef_df = pd.DataFrame({"feature": feature_names, "coefficient": coef})
    coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
    coef_df["odds_ratio"] = np.exp(np.clip(coef_df["coefficient"], -20, 20))
    outputs["pass_through_logistic_coefficients.csv"] = coef_df.sort_values("abs_coefficient", ascending=False)

    # Risk segments
    scored = fit_df.copy()
    scored["risk_decile"] = pd.qcut(scored["pred_exit_probability"], q=min(10, scored["pred_exit_probability"].nunique()), duplicates="drop")
    seg = (
        scored.groupby("risk_decile", dropna=False)
        .agg(
            students=("student_id", "nunique"),
            rows=("student_id", "count"),
            mean_pred_exit_probability=("pred_exit_probability", "mean"),
            observed_exit_rate=("exit_after_term_observed", "mean"),
            mean_rank_delta=("rank_pct_delta_w2_minus_w1", "mean"),
            mean_category_delta=("grm_mean_category_delta_w2_minus_w1", "mean"),
        )
        .reset_index()
        .sort_values("mean_pred_exit_probability")
    )
    for c in ["mean_pred_exit_probability", "observed_exit_rate", "mean_rank_delta", "mean_category_delta"]:
        seg[c] = pd.to_numeric(seg[c], errors="coerce").round(4)
    outputs["pass_through_risk_segments.csv"] = seg

    # Grouped simple rates for interpretability
    grouped = (
        fit_df.groupby(
            ["term", "wave1_primary_archetype", "wave1_dominant_error_profile_bucket", "rank_change_label", "category_change_label"],
            dropna=False,
        )
        .agg(
            students=("student_id", "nunique"),
            rows=("student_id", "count"),
            observed_exit_rate=("exit_after_term_observed", "mean"),
            mean_pred_exit_probability=("pred_exit_probability", "mean"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["rows"] >= 10].copy()
    for c in ["observed_exit_rate", "mean_pred_exit_probability"]:
        grouped[c] = pd.to_numeric(grouped[c], errors="coerce").round(4)
    outputs["pass_through_grouped_rates.csv"] = grouped.sort_values(["rows", "observed_exit_rate"], ascending=[False, False])

    return outputs, pipe, feature_cols_num, feature_cols_cat


def build_future_anchor_candidates(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    q = qdf(
        conn,
        f"""
        SELECT
            q.namespace,
            CAST(q.problem_id AS BIGINT) AS problem_id,
            q.question_title,
            q.a_discrimination,
            q.b1_any_partial_threshold AS b1,
            q.b2_full_threshold AS b2,
            q.threshold_gap_b2_minus_b1 AS threshold_gap,
            q.count_cat0,
            q.count_cat1,
            q.count_cat2,
            q.flag_cliff_like,
            q.flag_partial_credit_low_information,
            q.flag_very_high_discrimination,
            q.distribution_shape_step1,
            d.num_items,
            d.num_students,
            d.redundant_pairs_gt_0_90,
            CASE
                WHEN d.num_items >= 2 THEN CAST(d.dependency_edges_support5 AS DOUBLE) / (d.num_items * (d.num_items - 1))
                ELSE NULL
            END AS dependency_edge_density_raw,
            CASE
                WHEN d.num_items >= 2 THEN CAST(d.redundant_pairs_gt_0_90 AS DOUBLE) / (d.num_items * (d.num_items - 1) / 2)
                ELSE NULL
            END AS redundant_pair_rate
        FROM read_csv_auto('{sql_path(INPUTS.question_flags)}') q
        LEFT JOIN read_csv_auto('{sql_path(INPUTS.dependency_graph_summary)}') d
          ON d.namespace = q.namespace
         AND CAST(d.problem_id AS BIGINT) = CAST(q.problem_id AS BIGINT)
        """
    )
    if q.empty:
        return out

    q["question_title_norm"] = q["question_title"].map(normalize_title)
    q["mid_threshold"] = (pd.to_numeric(q["b1"], errors="coerce") + pd.to_numeric(q["b2"], errors="coerce")) / 2.0
    q["abs_mid_threshold"] = pd.to_numeric(q["mid_threshold"], errors="coerce").abs()
    q["threshold_gap"] = pd.to_numeric(q["threshold_gap"], errors="coerce")
    q["a_discrimination"] = pd.to_numeric(q["a_discrimination"], errors="coerce")
    q["redundant_pair_rate"] = pd.to_numeric(q["redundant_pair_rate"], errors="coerce")
    q["dependency_edge_density_raw"] = pd.to_numeric(q["dependency_edge_density_raw"], errors="coerce")

    q["anchor_moderate_difficulty_flag"] = q["abs_mid_threshold"].le(1.0)
    q["anchor_good_discrimination_flag"] = q["a_discrimination"].between(1.0, 3.8, inclusive="both")
    q["anchor_spread_flag"] = q["threshold_gap"].ge(0.5)
    q["anchor_not_cliff_flag"] = ~q["flag_cliff_like"].fillna(False)
    q["anchor_not_floor_ceiling_flag"] = ~q["distribution_shape_step1"].fillna("").isin(["Floor", "Ceiling"])
    q["anchor_not_equivalent_tests_flag"] = ~q["dependency_edge_density_raw"].round(6).eq(1.0)
    q["anchor_enough_middle_responses_flag"] = pd.to_numeric(q["count_cat1"], errors="coerce").fillna(0).ge(30)

    q["anchor_candidate_score"] = (
        q["anchor_good_discrimination_flag"].astype(int) * 3
        + q["anchor_moderate_difficulty_flag"].astype(int) * 2
        + q["anchor_spread_flag"].astype(int) * 3
        + q["anchor_not_cliff_flag"].astype(int) * 3
        + q["anchor_not_floor_ceiling_flag"].astype(int) * 2
        + q["anchor_not_equivalent_tests_flag"].astype(int) * 2
        + q["anchor_enough_middle_responses_flag"].astype(int) * 1
    )
    q["anchor_candidate_reason"] = (
        q.apply(
            lambda r: "; ".join(
                x
                for x, ok in [
                    ("good discrimination", bool(r["anchor_good_discrimination_flag"])),
                    ("moderate difficulty", bool(r["anchor_moderate_difficulty_flag"])),
                    ("wide threshold gap", bool(r["anchor_spread_flag"])),
                    ("not cliff-like", bool(r["anchor_not_cliff_flag"])),
                    ("not floor/ceiling", bool(r["anchor_not_floor_ceiling_flag"])),
                    ("non-equivalent test set", bool(r["anchor_not_equivalent_tests_flag"])),
                    ("enough partial responses", bool(r["anchor_enough_middle_responses_flag"])),
                ]
                if ok
            ),
            axis=1,
        )
    )
    q["anchor_candidate_pool_flag"] = (
        q["anchor_candidate_score"] >= 12
    ) & q["a_discrimination"].notna()

    # Add variant stability info from anchor drift table (same normalized title basis).
    drift = qdf(
        conn,
        f"""
        SELECT
            question_title_norm,
            COUNT(*) AS variant_anchor_rows,
            MAX(ABS(delta_a_linked)) AS max_abs_delta_a_linked,
            MAX(ABS(delta_b1_linked)) AS max_abs_delta_b1_linked,
            MAX(ABS(delta_b2_linked)) AS max_abs_delta_b2_linked
        FROM read_csv_auto('{sql_path(INPUTS.pair_anchor_drift)}')
        WHERE pair_type = 'variant_pair_same_slot'
          AND question_title_norm IS NOT NULL
          AND question_title_norm <> ''
        GROUP BY 1
        """
    )
    if not drift.empty:
        q = q.merge(drift, on="question_title_norm", how="left")

    question_pool = q.sort_values(
        ["anchor_candidate_pool_flag", "anchor_candidate_score", "a_discrimination", "threshold_gap"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    out["future_wave_anchor_candidate_questions.csv"] = question_pool

    title_agg = (
        question_pool.groupby("question_title_norm", dropna=False)
        .agg(
            title_forms=("question_title", "nunique"),
            namespaces=("namespace", "nunique"),
            median_a_discrimination=("a_discrimination", "median"),
            median_threshold_gap=("threshold_gap", "median"),
            median_abs_mid_threshold=("abs_mid_threshold", "median"),
            any_cliff=("flag_cliff_like", lambda s: bool(pd.Series(s).fillna(False).any())),
            max_anchor_candidate_score=("anchor_candidate_score", "max"),
            candidate_forms=("anchor_candidate_pool_flag", lambda s: int(pd.Series(s).fillna(False).sum())),
            median_redundant_pair_rate=("redundant_pair_rate", "median"),
            max_abs_delta_b1_linked=("max_abs_delta_b1_linked", "max"),
        )
        .reset_index()
    )
    title_agg["recommended_anchor_title_flag"] = (
        (title_agg["candidate_forms"] >= 1)
        & (~title_agg["any_cliff"].fillna(False))
        & (pd.to_numeric(title_agg["median_abs_mid_threshold"], errors="coerce").fillna(np.inf) <= 1.0)
        & (pd.to_numeric(title_agg["median_threshold_gap"], errors="coerce").fillna(-np.inf) >= 0.5)
    )
    title_agg = title_agg.sort_values(
        ["recommended_anchor_title_flag", "candidate_forms", "max_anchor_candidate_score", "median_a_discrimination"],
        ascending=[False, False, False, False],
    )
    out["future_wave_anchor_candidate_titles.csv"] = title_agg

    return out


def build_step8_key_metrics(
    term_wave_gap: pd.DataFrame,
    within_term_cov: pd.DataFrame,
    cross_term_cov: pd.DataFrame | None,
    all_three_raw: pd.DataFrame | None,
    all_three_sub: pd.DataFrame | None,
    within_term_rank_summary: pd.DataFrame | None,
    within_term_cat_summary: pd.DataFrame | None,
    within_term_archetype_targeted: pd.DataFrame | None,
    within_term_s2_escape: pd.DataFrame | None,
    cross_term_s2_escape: pd.DataFrame | None,
    cross_term_syntax_prog: pd.DataFrame | None,
    cross_term_runtime_persistence: pd.DataFrame | None,
    pass_perf: pd.DataFrame | None,
    anchor_titles: pd.DataFrame | None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for _, r in term_wave_gap.iterrows():
        rows.append({
            "metric_group": "Coverage",
            "metric_name": f"{r['term']}_wave1_to_wave2_min_start_gap_days",
            "value": float(r["min_start_gap_days"]),
            "unit": "days",
            "note": "Gap between earliest wave1 and earliest wave2 namespace starts",
        })

    for _, r in within_term_cov.iterrows():
        rows.append({
            "metric_group": "Within-term pairing",
            "metric_name": f"{r['term']}_paired_students_raw",
            "value": int(r["paired_students_raw"]),
            "unit": "students",
            "note": "Students with both wave1 and wave2 rows",
        })
        rows.append({
            "metric_group": "Within-term pairing",
            "metric_name": f"{r['term']}_paired_students_substantive",
            "value": int(r["paired_students_substantive"]),
            "unit": "students",
            "note": f"Both waves have >= {SUBSTANTIVE_MIN_QUESTION_ROWS} question rows",
        })

    if cross_term_cov is not None and not cross_term_cov.empty:
        for _, r in cross_term_cov.iterrows():
            rows.append({
                "metric_group": "Cross-term pairing",
                "metric_name": f"{r['term_pair']}_repeat_students_raw",
                "value": int(r["repeat_students_raw"]),
                "unit": "students",
                "note": "Repeat students across term pair",
            })
            rows.append({
                "metric_group": "Cross-term pairing",
                "metric_name": f"{r['term_pair']}_repeat_students_substantive",
                "value": int(r["repeat_students_substantive"]),
                "unit": "students",
                "note": f"Both terms have >= {SUBSTANTIVE_MIN_QUESTION_ROWS} question rows",
            })

    if all_three_raw is not None and all_three_sub is not None:
        rows.append({
            "metric_group": "All-three cohort",
            "metric_name": "all_three_students_raw",
            "value": int(len(all_three_raw)),
            "unit": "students",
            "note": "Any participation in all three terms (wave1/wave2 rows present)",
        })
        rows.append({
            "metric_group": "All-three cohort",
            "metric_name": "all_three_students_substantive",
            "value": int(len(all_three_sub)),
            "unit": "students",
            "note": f"Substantive participation (>= {SUBSTANTIVE_MIN_QUESTION_ROWS} question rows per term)",
        })

    if within_term_rank_summary is not None and not within_term_rank_summary.empty:
        for _, r in within_term_rank_summary.iterrows():
            rows.append({
                "metric_group": "Within-term growth",
                "metric_name": f"{r['term']}_median_rank_delta",
                "value": float(r["median_rank_delta"]),
                "unit": "rank_pct",
                "note": "Wave2 - Wave1 rank percentile change (substantive paired cohort)",
            })
    if within_term_cat_summary is not None and not within_term_cat_summary.empty:
        target = within_term_cat_summary[
            within_term_cat_summary["weighting"].eq("question_count_weighted_students")
            & within_term_cat_summary["category_change_label"].isin(["improve", "decline", "same"])
        ]
        for _, r in target.iterrows():
            rows.append({
                "metric_group": "Within-term growth",
                "metric_name": f"{r['term']}_category_change_{r['category_change_label']}_pct_weighted",
                "value": float(r["pct_weighted_students"]),
                "unit": "pct",
                "note": "Weighted by paired question rows mean",
            })

    if within_term_archetype_targeted is not None and not within_term_archetype_targeted.empty:
        targets = within_term_archetype_targeted[
            (within_term_archetype_targeted["wave1_primary_archetype"] == "Thrasher")
            & (within_term_archetype_targeted["wave2_primary_archetype"].isin(["Steady builder", "Incremental debugger"]))
        ]
        for _, r in targets.iterrows():
            rows.append({
                "metric_group": "Within-term archetype shift",
                "metric_name": f"{r['term']}_thrasher_to_{str(r['wave2_primary_archetype']).replace(' ', '_').lower()}_pct",
                "value": float(r["pct_of_source"]),
                "unit": "pct",
                "note": "Row-normalized among Wave1 thrashers",
            })

    if within_term_s2_escape is not None and not within_term_s2_escape.empty:
        for _, r in within_term_s2_escape.iterrows():
            rows.append({
                "metric_group": "Within-term state shift",
                "metric_name": f"{r['term']}_dominant_S2_escape_to_S3orS4_pct",
                "value": float(r["pct_escaped_to_S3orS4"]),
                "unit": "pct",
                "note": "Wave1 dominant S2 -> Wave2 dominant S3/S4 among substantive paired students",
            })

    if cross_term_s2_escape is not None and not cross_term_s2_escape.empty:
        for _, r in cross_term_s2_escape.iterrows():
            rows.append({
                "metric_group": "Cross-term state shift",
                "metric_name": f"{r['term_pair']}_dominant_S2_escape_to_S3orS4_pct",
                "value": float(r["pct_escaped_to_S3orS4"]),
                "unit": "pct",
                "note": "Term N dominant S2 -> Term N+1 dominant S3/S4 among substantive repeaters",
            })

    if cross_term_syntax_prog is not None and not cross_term_syntax_prog.empty:
        for _, r in cross_term_syntax_prog.iterrows():
            rows.append({
                "metric_group": "Cross-term error progression",
                "metric_name": f"{r['term_pair']}_syntax_to_runtime_or_wrong_output_pct",
                "value": float(r["pct_moved_to_runtime_or_wrong_output"]),
                "unit": "pct",
                "note": "Among repeaters with syntax-gated dominant error profile in source term",
            })

    if cross_term_runtime_persistence is not None and not cross_term_runtime_persistence.empty:
        overall = (
            cross_term_runtime_persistence.groupby("term_pair", dropna=False)
            .apply(lambda g: np.average(g["pct_same_runtime_type"], weights=g["students"]) if g["students"].sum() > 0 else np.nan)
            .reset_index(name="weighted_pct_same_runtime_type")
        )
        for _, r in overall.iterrows():
            rows.append({
                "metric_group": "Cross-term error progression",
                "metric_name": f"{r['term_pair']}_runtime_subtype_persistence_weighted_pct",
                "value": float(r["weighted_pct_same_runtime_type"]),
                "unit": "pct",
                "note": "Weighted across dominant runtime subtype source groups",
            })

    if pass_perf is not None and not pass_perf.empty:
        pr = pass_perf.iloc[0]
        rows.extend(
            [
                {
                    "metric_group": "Pass-through model",
                    "metric_name": "pass_through_model_n_rows",
                    "value": int(pr["n_rows"]),
                    "unit": "rows",
                    "note": "t1/t2 substantive paired-wave students; outcome is observed exit proxy",
                },
                {
                    "metric_group": "Pass-through model",
                    "metric_name": "pass_through_model_cv_auc",
                    "value": float(pr["cv_auc"]) if pd.notna(pr["cv_auc"]) else np.nan,
                    "unit": "auc",
                    "note": "Cross-validated ROC AUC (exit proxy)",
                },
                {
                    "metric_group": "Pass-through model",
                    "metric_name": "pass_through_model_cv_brier",
                    "value": float(pr["cv_brier"]) if pd.notna(pr["cv_brier"]) else np.nan,
                    "unit": "brier",
                    "note": "Cross-validated Brier score (exit proxy)",
                },
            ]
        )

    if anchor_titles is not None and not anchor_titles.empty:
        rows.append({
            "metric_group": "Future anchors",
            "metric_name": "recommended_anchor_title_candidates",
            "value": int(anchor_titles["recommended_anchor_title_flag"].fillna(False).sum()),
            "unit": "titles",
            "note": "Title-level pool for future deliberate wave anchors",
        })

    return pd.DataFrame(rows)


def main() -> None:
    ensure_inputs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = make_conn()
    materialize_base_views(conn)

    print("[1/11] Building schedule gap summary and student-wave performance tables...")
    term_wave_gap = build_term_wave_gap_summary(conn)
    student_wave_perf = build_student_wave_performance(conn)
    within_pairs_all, within_cov, within_pairs_sub = build_within_term_wave_pairs(student_wave_perf)
    write_csv(term_wave_gap, OUT_DIR / "term_wave_gap_summary.csv")
    write_csv(student_wave_perf, OUT_DIR / "student_wave_performance_summary.csv")
    write_csv(within_cov, OUT_DIR / "within_term_wave_pair_coverage.csv")

    print("[2/11] Building student-wave and student-term archetype summaries...")
    student_wave_archetype = build_student_wave_archetype(conn)
    student_term_archetype = build_student_term_archetype(conn)
    write_csv(student_wave_archetype, OUT_DIR / "student_wave_primary_archetype.csv")
    write_csv(student_term_archetype, OUT_DIR / "student_term_primary_archetype.csv")

    print("[3/11] Building dominant-state summaries (wave and term)...")
    sw_scope = student_wave_perf[["term", "wave", "student_id"]].drop_duplicates().copy()
    st_scope = build_student_term_performance(student_wave_perf)[["term", "student_id"]].drop_duplicates().copy()
    student_wave_state = attach_no_public_run_state(sw_scope, build_state_counts(conn, by_term_only=False), ["term", "wave", "student_id"])
    student_term_state = attach_no_public_run_state(st_scope, build_state_counts(conn, by_term_only=True), ["term", "student_id"])
    write_csv(student_wave_state, OUT_DIR / "student_wave_dominant_state.csv")
    write_csv(student_term_state, OUT_DIR / "student_term_dominant_state.csv")

    print("[4/11] Building error-profile summaries (wave and term) from Step 3 row-level outputs...")
    error_rows = build_error_rows(conn)
    student_wave_error = build_student_error_summary(error_rows, ["term", "wave", "student_id"])
    student_term_error = build_student_error_summary(error_rows, ["term", "student_id"])
    write_csv(error_rows, OUT_DIR / "student_question_error_rows_step8.csv")
    write_csv(student_wave_error, OUT_DIR / "student_wave_primary_error_profile.csv")
    write_csv(student_term_error, OUT_DIR / "student_term_primary_error_profile.csv")

    print("[5/11] Building construct progression baseline (term-level tree-sitter usage)...")
    student_term_construct = build_student_term_construct_profile(conn)
    write_csv(student_term_construct, OUT_DIR / "student_term_construct_profile.csv")

    print("[6/11] Building within-term longitudinal outputs (8a)...")
    within_outputs = build_within_term_outputs(
        within_pairs_all,
        within_pairs_sub,
        student_wave_archetype,
        student_wave_state,
        student_wave_error,
    )
    for name, df in within_outputs.items():
        write_csv(df, OUT_DIR / name)

    print("[7/11] Building cross-term repeat-student outputs (8b)...")
    student_term_perf = build_student_term_performance(student_wave_perf)
    write_csv(student_term_perf, OUT_DIR / "student_term_performance_summary.csv")
    term_pairs, cross_outputs = build_cross_term_pairs(
        student_term_perf,
        student_term_archetype,
        student_term_state,
        student_term_error,
        student_term_construct,
    )
    for name, df in cross_outputs.items():
        write_csv(df, OUT_DIR / name)

    print("[8/11] Building dedicated all-three-term cohort outputs (8c)...")
    all_three_outputs = build_all_three_outputs(
        student_term_perf,
        student_term_archetype,
        student_term_state,
        student_term_error,
        student_term_construct,
        within_pairs_sub,
    )
    for name, df in all_three_outputs.items():
        write_csv(df, OUT_DIR / name)

    print("[9/11] Building pass-through exit-proxy model (8d)...")
    model_outputs, model_pipe, num_feats, cat_feats = build_pass_through_model(
        within_pairs_sub,
        student_wave_archetype,
        student_wave_error,
        student_wave_state,
        student_term_perf,
    )
    for name, df in model_outputs.items():
        write_csv(df, OUT_DIR / name)

    print("[10/11] Building future anchor candidate recommendations (8e)...")
    anchor_outputs = build_future_anchor_candidates(conn)
    for name, df in anchor_outputs.items():
        write_csv(df, OUT_DIR / name)

    print("[11/11] Writing Step 8 key metrics and manifest...")
    key_metrics = build_step8_key_metrics(
        term_wave_gap=term_wave_gap,
        within_term_cov=within_cov,
        cross_term_cov=cross_outputs.get("cross_term_repeat_coverage.csv"),
        all_three_raw=all_three_outputs.get("all_three_term_students_raw.csv"),
        all_three_sub=all_three_outputs.get("all_three_term_students_substantive.csv"),
        within_term_rank_summary=within_outputs.get("within_term_rank_change_summary.csv"),
        within_term_cat_summary=within_outputs.get("within_term_category_change_summary.csv"),
        within_term_archetype_targeted=within_outputs.get("within_term_archetype_targeted_shifts.csv"),
        within_term_s2_escape=within_outputs.get("within_term_s2_dominant_escape_summary.csv"),
        cross_term_s2_escape=cross_outputs.get("cross_term_s2_escape_summary.csv"),
        cross_term_syntax_prog=cross_outputs.get("cross_term_syntax_progression_summary.csv"),
        cross_term_runtime_persistence=cross_outputs.get("cross_term_runtime_type_persistence.csv"),
        pass_perf=model_outputs.get("pass_through_model_performance.csv"),
        anchor_titles=anchor_outputs.get("future_wave_anchor_candidate_titles.csv"),
    )
    write_csv(key_metrics, OUT_DIR / "step8_key_metrics.csv")
    write_manifest()

    conn.close()
    print(f"Wrote Step 8 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
