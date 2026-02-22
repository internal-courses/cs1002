#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "pandas>=2.2.0",
# ]
# ///
"""Step 7: Evaluation Redesign synthesis outputs.

This script does not recompute Steps 2/3/5/6. It reads their exported outputs
and produces a compact decision-support bundle under ``analysis/evaluation_redesign/``:

- instrumentation / submission-capture audits
- S2 bottleneck summaries
- archetype intervention tables (including "Other" diagnostics)
- question redesign target lists (test-case redundancy + cliff/thrasher/wrong-logic)
- low-ability measurement target lists
- layered-scoring readiness summaries
- variant-equivalence review tables
- runtime-feedback / debugging-signal summaries

The README section "Step 7: Evaluation Redesign" should be written manually and
cite these outputs.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "evaluation_redesign"

TRACK_A_SUBMITTERS = "Track A: submitters"
TRACK_A_NON_SUBMIT = "Track A: non-submitters (submission-positive NS)"
TRACK_B = "Track B: zero-submission namespaces"
TRACK_ORDER = {
    TRACK_A_NON_SUBMIT: 1,
    TRACK_A_SUBMITTERS: 2,
    TRACK_B: 3,
}

NAMESPACE_PARSE_RE = re.compile(
    r"^ns_(?P<term>[^_]+)_(?P<slot>py(?P<wave_num>\d)(?P<slot_idx>\d+))(?:_(?P<variant>\d+))?$"
)


@dataclass(frozen=True)
class Inputs:
    attempt_archetypes: Path = ANALYSIS_DIR / "process_analysis" / "attempt_archetypes.csv"
    archetype_flags_summary: Path = ANALYSIS_DIR / "process_analysis" / "archetype_outcomes_flags_summary.csv"
    archetype_primary_summary: Path = ANALYSIS_DIR / "process_analysis" / "archetype_outcomes_primary_summary.csv"
    public_state_dist: Path = ANALYSIS_DIR / "process_analysis" / "public_state_distribution_by_track.csv"
    death_spiral_absorb: Path = ANALYSIS_DIR / "process_analysis" / "death_spiral_absorbing_candidates.csv"
    death_spiral_state_summary: Path = ANALYSIS_DIR / "process_analysis" / "death_spiral_transition_difficulty.csv"
    death_spiral_transitions: Path = ANALYSIS_DIR / "process_analysis" / "death_spiral_transition_matrix_combined.csv"
    error_recovery_by_type: Path = ANALYSIS_DIR / "process_analysis" / "error_recovery_by_type.csv"

    track_summary: Path = ANALYSIS_DIR / "error_taxonomy" / "track_summary.csv"
    best_public_rows: Path = ANALYSIS_DIR / "error_taxonomy" / "best_public_test_run_classification_rows.csv"
    runtime_error_summary: Path = ANALYSIS_DIR / "error_taxonomy" / "runtime_error_type_summary.csv"
    regression_summary: Path = ANALYSIS_DIR / "error_taxonomy" / "regression_summary.csv"

    gating_waterfall_pct: Path = ANALYSIS_DIR / "syntax_bottleneck_quantified" / "gating_waterfall_pct.csv"

    question_redundancy_pairs: Path = ANALYSIS_DIR / "classical_item_quality" / "question_item_redundancy_pairs.csv"
    dependency_graph_summary: Path = ANALYSIS_DIR / "classical_item_quality" / "question_dependency_graph_summary.csv"
    reliability_alpha: Path = ANALYSIS_DIR / "classical_item_quality" / "namespace_reliability_cronbach_alpha.csv"
    reliability_summary: Path = ANALYSIS_DIR / "classical_item_quality" / "namespace_reliability_summary.csv"

    irt_overall: Path = ANALYSIS_DIR / "psychometric_irt" / "irt_summary_overall.csv"
    tif_flags: Path = ANALYSIS_DIR / "psychometric_irt" / "tif_low_ability_flags.csv"
    question_flags: Path = ANALYSIS_DIR / "psychometric_irt" / "question_parameter_flags.csv"
    namespace_pair_theta: Path = ANALYSIS_DIR / "psychometric_irt" / "namespace_pair_theta_linked_comparisons.csv"
    theta_linked_wave_pairs: Path = ANALYSIS_DIR / "psychometric_irt" / "theta_linked_wave_pair_comparisons.csv"
    namespace_pair_linking_summary: Path = ANALYSIS_DIR / "psychometric_irt" / "namespace_pair_linking_summary.csv"
    namespace_pair_anchor_drift: Path = ANALYSIS_DIR / "psychometric_irt" / "namespace_pair_anchor_parameter_drift.csv"


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
        missing_list = "\n".join(f"- {p}" for p in missing)
        raise FileNotFoundError(f"Step 7 inputs missing:\n{missing_list}")


def parse_namespace_bits(namespace: str) -> dict[str, Any]:
    m = NAMESPACE_PARSE_RE.match(namespace or "")
    if not m:
        return {
            "parsed_term": None,
            "slot_code": None,
            "parsed_wave": "other",
            "variant": None,
        }
    wave_num = m.group("wave_num")
    return {
        "parsed_term": m.group("term"),
        "slot_code": m.group("slot"),
        "parsed_wave": f"wave{wave_num}" if wave_num else "other",
        "variant": m.group("variant"),
    }


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_manifest() -> None:
    files: list[dict[str, Any]] = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "output_manifest.csv":
            files.append({"path": path.relative_to(OUT_DIR).as_posix(), "bytes": path.stat().st_size})
    pd.DataFrame(files).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def build_submission_capture_audits(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    attempts = sql_path(INPUTS.attempt_archetypes)
    track_summary = sql_path(INPUTS.track_summary)

    track_rows = qdf(
        conn,
        f"""
        WITH process_track AS (
            SELECT
                track,
                COUNT(*) AS process_rows,
                SUM(CASE WHEN any_public_pass THEN 1 ELSE 0 END) AS any_public_pass_rows,
                SUM(CASE WHEN any_public_all_pass THEN 1 ELSE 0 END) AS any_public_all_pass_rows
            FROM read_csv_auto('{attempts}')
            GROUP BY 1
        )
        SELECT
            t.track,
            t.rows,
            t.rows_with_selected_hash,
            t.rows_with_selected_event,
            t.pct_with_selected_hash,
            t.full_pass_rows,
            t.partial_pass_rows,
            t.submitted_zero_rows,
            t.active_never_submitted_rows,
            t.no_activity_rows,
            p.process_rows,
            p.any_public_pass_rows,
            ROUND(100.0 * p.any_public_pass_rows / NULLIF(p.process_rows, 0), 2) AS pct_any_public_pass,
            p.any_public_all_pass_rows,
            ROUND(100.0 * p.any_public_all_pass_rows / NULLIF(p.process_rows, 0), 2) AS pct_any_public_all_pass
        FROM read_csv_auto('{track_summary}') AS t
        LEFT JOIN process_track AS p USING(track)
        """,
    )
    track_rows["track_order"] = track_rows["track"].map(TRACK_ORDER).fillna(99).astype(int)
    track_rows = track_rows.sort_values(["track_order", "track"]).drop(columns=["track_order"])

    namespace_audit = qdf(
        conn,
        f"""
        SELECT
            namespace,
            MIN(term) AS term,
            MIN(wave) AS wave,
            MAX(CASE WHEN submission_positive_namespace THEN 1 ELSE 0 END) = 1 AS submission_positive_namespace,
            COUNT(*) AS rows_total,
            COUNT(DISTINCT problem_id) AS questions,
            COUNT(DISTINCT student_id) AS students,
            SUM(CASE WHEN track = '{TRACK_A_SUBMITTERS}' THEN 1 ELSE 0 END) AS rows_track_a_submitters,
            SUM(CASE WHEN track = '{TRACK_A_NON_SUBMIT}' THEN 1 ELSE 0 END) AS rows_track_a_non_submitters,
            SUM(CASE WHEN track = '{TRACK_B}' THEN 1 ELSE 0 END) AS rows_track_b,
            SUM(CASE WHEN any_public_pass THEN 1 ELSE 0 END) AS any_public_pass_rows,
            ROUND(100.0 * SUM(CASE WHEN any_public_pass THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_any_public_pass,
            SUM(CASE WHEN any_public_all_pass THEN 1 ELSE 0 END) AS any_public_all_pass_rows,
            ROUND(100.0 * SUM(CASE WHEN any_public_all_pass THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_any_public_all_pass
        FROM read_csv_auto('{attempts}')
        GROUP BY 1
        ORDER BY namespace
        """,
    )
    ns_bits = namespace_audit["namespace"].map(parse_namespace_bits).apply(pd.Series)
    namespace_audit = pd.concat([namespace_audit, ns_bits], axis=1)
    namespace_audit["namespace_track"] = namespace_audit["submission_positive_namespace"].map(
        {True: "submission-positive namespace", False: "zero-submission namespace"}
    )

    term_wave_ns = (
        namespace_audit.assign(
            term_filled=namespace_audit["term"].fillna(namespace_audit["parsed_term"]).fillna("unknown"),
            wave_filled=namespace_audit["wave"].fillna(namespace_audit["parsed_wave"]).fillna("unknown"),
        )
        .groupby(["term_filled", "wave_filled"], dropna=False)
        .agg(
            namespaces_total=("namespace", "nunique"),
            zero_submission_namespaces=("submission_positive_namespace", lambda s: int((~s.astype(bool)).sum())),
            submission_positive_namespaces=("submission_positive_namespace", lambda s: int(s.astype(bool).sum())),
            rows_total=("rows_total", "sum"),
        )
        .reset_index()
        .rename(columns={"term_filled": "term", "wave_filled": "wave"})
    )
    term_wave_ns["zero_submission_namespace_pct"] = (
        100.0 * term_wave_ns["zero_submission_namespaces"] / term_wave_ns["namespaces_total"]
    ).round(2)
    term_wave_ns = term_wave_ns.sort_values(["term", "wave"]).reset_index(drop=True)

    overall = pd.DataFrame(
        [
            {
                "namespaces_total": int(namespace_audit["namespace"].nunique()),
                "submission_positive_namespaces": int(namespace_audit["submission_positive_namespace"].sum()),
                "zero_submission_namespaces": int((~namespace_audit["submission_positive_namespace"]).sum()),
                "track_a_submitter_rows": int(track_rows.loc[track_rows["track"] == TRACK_A_SUBMITTERS, "rows"].iloc[0]),
                "track_a_non_submitter_rows": int(track_rows.loc[track_rows["track"] == TRACK_A_NON_SUBMIT, "rows"].iloc[0]),
                "track_b_rows": int(track_rows.loc[track_rows["track"] == TRACK_B, "rows"].iloc[0]),
                "track_b_pct_any_public_all_pass": float(
                    track_rows.loc[track_rows["track"] == TRACK_B, "pct_any_public_all_pass"].iloc[0]
                ),
            }
        ]
    )

    zero_submission_namespaces = (
        namespace_audit.loc[~namespace_audit["submission_positive_namespace"]]
        .sort_values(["term", "wave", "namespace"])
        .reset_index(drop=True)
    )

    return {
        "submission_capture_track_row_summary.csv": track_rows,
        "submission_capture_namespace_audit.csv": namespace_audit,
        "submission_capture_zero_submission_namespaces.csv": zero_submission_namespaces,
        "submission_capture_term_wave_namespace_summary.csv": term_wave_ns,
        "submission_capture_overall_summary.csv": overall,
    }


def build_s2_bottleneck(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    public_state = sql_path(INPUTS.public_state_dist)
    absorb = sql_path(INPUTS.death_spiral_state_summary)
    transitions = sql_path(INPUTS.death_spiral_transitions)

    state_combined = qdf(
        conn,
        f"""
        WITH combined AS (
            SELECT
                process_state,
                MIN(process_state_label) AS process_state_label,
                SUM(public_run_rows) AS public_run_rows
            FROM read_csv_auto('{public_state}')
            GROUP BY 1
        )
        SELECT
            process_state,
            process_state_label,
            public_run_rows,
            ROUND(100.0 * public_run_rows / SUM(public_run_rows) OVER (), 2) AS pct_all_public_runs
        FROM combined
        ORDER BY public_run_rows DESC
        """,
    )

    s2_absorb = qdf(
        conn,
        f"""
        SELECT *
        FROM read_csv_auto('{absorb}')
        WHERE from_state = 'S2_parseable_zero'
        """,
    )
    s2_prevalence = state_combined.loc[state_combined["process_state"] == "S2_parseable_zero"].copy()
    if not s2_prevalence.empty and not s2_absorb.empty:
        s2_summary = s2_absorb.merge(
            s2_prevalence.rename(columns={"process_state": "from_state", "process_state_label": "from_state_label"}),
            on=["from_state", "from_state_label"],
            how="left",
        )
    else:
        s2_summary = s2_absorb

    s2_transitions = qdf(
        conn,
        f"""
        SELECT
            from_state,
            to_state,
            transitions,
            from_total,
            pct_from_state
        FROM read_csv_auto('{transitions}')
        WHERE from_state = 'S2_parseable_zero'
        ORDER BY transitions DESC, to_state
        """,
    )
    if not s2_transitions.empty:
        s2_transitions["is_self_loop"] = s2_transitions["to_state"] == "S2_parseable_zero"
        s2_transitions["is_higher_state"] = s2_transitions["to_state"].isin(["S3_public_partial", "S4_public_all", "S5_all_tests"])
        s2_transitions["transition_rank"] = range(1, len(s2_transitions) + 1)
    s2_escape = s2_transitions.loc[~s2_transitions["is_self_loop"]].reset_index(drop=True)

    return {
        "public_state_distribution_combined.csv": state_combined,
        "s2_bottleneck_summary.csv": s2_summary,
        "s2_transition_destinations.csv": s2_transitions,
        "s2_escape_routes.csv": s2_escape,
    }


def build_archetype_tables(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    flags = sql_path(INPUTS.archetype_flags_summary)
    primary = sql_path(INPUTS.archetype_primary_summary)
    attempts = sql_path(INPUTS.attempt_archetypes)

    archetype_summary = qdf(
        conn,
        f"""
        SELECT
            archetype,
            attempts,
            pct_all_attempts,
            median_process_outcome_metric,
            median_active_time_seconds,
            median_public_test_runs,
            success_rate_state4_or_state5,
            track_a_submitter_pct,
            track_a_non_submit_pct,
            track_b_pct,
            'flag' AS classification_basis
        FROM read_csv_auto('{flags}')
        UNION ALL
        SELECT
            primary_archetype AS archetype,
            attempts,
            pct_all_attempts,
            median_process_outcome_metric,
            median_active_time_seconds,
            median_public_test_runs,
            success_rate_state4_or_state5,
            NULL AS track_a_submitter_pct,
            NULL AS track_a_non_submit_pct,
            NULL AS track_b_pct,
            'primary' AS classification_basis
        FROM read_csv_auto('{primary}')
        WHERE primary_archetype = 'Other'
        """,
    )
    archetype_summary["is_other_unclassified"] = archetype_summary["archetype"].eq("Other")
    archetype_summary["archetype_order"] = archetype_summary["archetype"].map(
        {
            "Steady builder": 1,
            "Incremental debugger": 2,
            "Regression": 3,
            "One-shot": 4,
            "Skeleton-only": 5,
            "Stuck and abandoned": 6,
            "Thrasher": 7,
            "Late starter": 8,
            "Other": 9,
        }
    ).fillna(99)
    archetype_summary = archetype_summary.sort_values(["archetype_order", "classification_basis"]).drop(columns=["archetype_order"])

    debug_compare = archetype_summary.loc[
        (archetype_summary["classification_basis"] == "flag")
        & archetype_summary["archetype"].isin(["Incremental debugger", "Thrasher"])
    ].copy()
    if not debug_compare.empty:
        inc_row = debug_compare.loc[debug_compare["archetype"] == "Incremental debugger"].iloc[0]
        debug_compare["time_ratio_vs_incremental"] = (
            debug_compare["median_active_time_seconds"] / float(inc_row["median_active_time_seconds"])
        ).round(2)
        debug_compare["run_ratio_vs_incremental"] = (
            debug_compare["median_public_test_runs"] / float(inc_row["median_public_test_runs"])
        ).round(2)
        debug_compare["success_rate_gap_vs_incremental_pp"] = (
            debug_compare["success_rate_state4_or_state5"] - float(inc_row["success_rate_state4_or_state5"])
        ).round(2)

    other_by_question = qdf(
        conn,
        f"""
        WITH q AS (
            SELECT
                namespace,
                problem_id,
                question_title,
                COUNT(*) AS attempts,
                SUM(CASE WHEN primary_archetype = 'Other' THEN 1 ELSE 0 END) AS other_attempts,
                AVG(CASE WHEN process_outcome_success_flag THEN 1 ELSE 0 END) AS overall_success_rate,
                AVG(CASE WHEN primary_archetype = 'Other' AND process_outcome_success_flag THEN 1
                         WHEN primary_archetype = 'Other' THEN 0
                         ELSE NULL END) AS other_success_rate
            FROM read_csv_auto('{attempts}')
            GROUP BY 1,2,3
        )
        SELECT
            *,
            ROUND(100.0 * other_attempts / NULLIF(attempts, 0), 2) AS other_rate_pct,
            ROUND(100.0 * overall_success_rate, 2) AS overall_success_rate_pct,
            ROUND(100.0 * other_success_rate, 2) AS other_success_rate_pct
        FROM q
        WHERE other_attempts > 0
        ORDER BY other_rate_pct DESC, attempts DESC, namespace, problem_id
        """,
    )

    other_signatures = qdf(
        conn,
        f"""
        WITH base AS (
            SELECT *
            FROM read_csv_auto('{attempts}')
            WHERE primary_archetype = 'Other'
        ),
        b AS (
            SELECT
                CASE
                    WHEN public_test_run_count <= 1 THEN '0-1 runs'
                    WHEN public_test_run_count <= 5 THEN '2-5 runs'
                    WHEN public_test_run_count <= 15 THEN '6-15 runs'
                    ELSE '16+ runs'
                END AS public_runs_bucket,
                CASE
                    WHEN parseable_fraction = 0 THEN 'never parseable'
                    WHEN parseable_fraction < 1 THEN 'sometimes parseable'
                    ELSE 'always parseable'
                END AS parseable_bucket,
                CASE
                    WHEN active_time_seconds < 60 THEN '<1 min'
                    WHEN active_time_seconds < 600 THEN '1-10 min'
                    WHEN active_time_seconds < 1800 THEN '10-30 min'
                    ELSE '30+ min'
                END AS active_time_bucket,
                any_public_pass,
                no_improvement_latter_half_flag,
                peak_to_final_public_regression,
                process_outcome_success_flag
            FROM base
        )
        SELECT
            public_runs_bucket,
            parseable_bucket,
            active_time_bucket,
            any_public_pass,
            no_improvement_latter_half_flag,
            peak_to_final_public_regression,
            COUNT(*) AS attempts,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM b), 2) AS pct_of_other_attempts,
            ROUND(100.0 * AVG(CASE WHEN process_outcome_success_flag THEN 1 ELSE 0 END), 2) AS success_rate_pct
        FROM b
        GROUP BY 1,2,3,4,5,6
        ORDER BY attempts DESC, public_runs_bucket, parseable_bucket
        LIMIT 50
        """,
    )

    return {
        "archetype_redesign_summary.csv": archetype_summary,
        "archetype_incremental_vs_thrasher_comparison.csv": debug_compare,
        "archetype_other_by_question.csv": other_by_question,
        "archetype_other_signature_clusters.csv": other_signatures,
    }


def build_question_redesign_tables(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    attempts = sql_path(INPUTS.attempt_archetypes)
    best_public = sql_path(INPUTS.best_public_rows)
    qflags = sql_path(INPUTS.question_flags)
    dep = sql_path(INPUTS.dependency_graph_summary)

    thrasher_rates = qdf(
        conn,
        f"""
        SELECT
            namespace,
            problem_id,
            MIN(question_title) AS question_title,
            COUNT(*) AS attempts,
            ROUND(100.0 * AVG(CASE WHEN thrasher_flag THEN 1 ELSE 0 END), 2) AS thrasher_rate_pct
        FROM read_csv_auto('{attempts}')
        GROUP BY 1,2
        """,
    )

    wrong_logic_rates = qdf(
        conn,
        f"""
        SELECT
            namespace,
            problem_id,
            MIN(question_title) AS question_title,
            COUNT(*) AS attempts_best_public_rows,
            ROUND(
                100.0 * AVG(CASE WHEN best_public_wrong_output_subtype = 'Wrong output - logic/completely wrong' THEN 1 ELSE 0 END),
                2
            ) AS wrong_logic_rate_pct,
            ROUND(
                100.0 * AVG(CASE WHEN best_public_primary_failure_mode = 'Wrong output - logic/completely wrong' THEN 1 ELSE 0 END),
                2
            ) AS primary_failure_logic_rate_pct
        FROM read_csv_auto('{best_public}')
        GROUP BY 1,2
        """,
    )

    question_metrics = qdf(
        conn,
        f"""
        SELECT
            d.namespace,
            d.problem_id,
            d.question_title,
            d.num_items,
            d.num_students,
            d.redundant_pairs_gt_0_90,
            CASE WHEN d.num_items >= 2 THEN d.num_items * (d.num_items - 1) / 2 ELSE NULL END AS possible_item_pairs,
            CASE
                WHEN d.num_items >= 2 AND (d.num_items * (d.num_items - 1) / 2) > 0
                    THEN ROUND(100.0 * d.redundant_pairs_gt_0_90 / (d.num_items * (d.num_items - 1) / 2), 2)
                ELSE NULL
            END AS redundant_pair_rate_pct,
            d.dependency_edges_support5,
            CASE
                WHEN d.num_items >= 2 AND (d.num_items * (d.num_items - 1)) > 0
                    THEN CAST(d.dependency_edges_support5 AS DOUBLE) / (d.num_items * (d.num_items - 1))
                ELSE NULL
            END AS dependency_edge_density_raw,
            d.dependency_reduced_edge_density,
            d.minimal_new_information_components
        FROM read_csv_auto('{dep}') AS d
        """,
    )

    irt_questions = qdf(
        conn,
        f"""
        SELECT
            namespace,
            problem_id,
            question_title,
            a_discrimination,
            b1_any_partial_threshold,
            b2_full_threshold,
            threshold_gap_b2_minus_b1,
            count_cat0,
            count_cat1,
            count_cat2,
            flag_partial_credit_low_information,
            flag_partial_credit_missing_or_collapsed,
            flag_cliff_like,
            flag_very_high_discrimination,
            distribution_shape_step1
        FROM read_csv_auto('{qflags}')
        """,
    )

    question_features = thrasher_rates.merge(
        wrong_logic_rates.drop(columns=["question_title"], errors="ignore"),
        on=["namespace", "problem_id"],
        how="left",
    )
    question_features = question_features.merge(
        irt_questions.drop(columns=["question_title"], errors="ignore"),
        on=["namespace", "problem_id"],
        how="left",
    )
    question_features = question_features.merge(
        question_metrics.drop(columns=["question_title"], errors="ignore"),
        on=["namespace", "problem_id"],
        how="left",
    )

    question_features["question_title"] = question_features["question_title"].fillna(
        question_features.get("question_title_y", pd.Series(index=question_features.index, dtype="object"))
    )
    question_features = question_features.loc[:, ~question_features.columns.duplicated()].copy()

    question_features["dependency_edge_density_raw"] = pd.to_numeric(
        question_features["dependency_edge_density_raw"], errors="coerce"
    )
    question_features["flag_dependency_edge_density_raw_eq_1"] = question_features["dependency_edge_density_raw"].round(6).eq(1.0)
    question_features["flag_high_thrasher_rate_ge_5pct"] = (
        pd.to_numeric(question_features["thrasher_rate_pct"], errors="coerce") >= 5.0
    )
    question_features["flag_high_wrong_logic_rate_ge_30pct"] = (
        pd.to_numeric(question_features["wrong_logic_rate_pct"], errors="coerce") >= 30.0
    ) & (pd.to_numeric(question_features["attempts_best_public_rows"], errors="coerce") >= 200)

    # Layered-scoring readiness proxy before computing the dedicated summary.
    gap = pd.to_numeric(question_features["threshold_gap_b2_minus_b1"], errors="coerce")
    question_features["threshold_gap_band"] = pd.Series(pd.NA, index=question_features.index, dtype="object")
    question_features.loc[question_features["flag_partial_credit_missing_or_collapsed"].fillna(False), "threshold_gap_band"] = (
        "missing/collapsed"
    )
    question_features.loc[
        question_features["threshold_gap_band"].isna() & gap.lt(0.35),
        "threshold_gap_band",
    ] = "narrow (<0.35)"
    question_features.loc[
        question_features["threshold_gap_band"].isna() & gap.ge(0.35) & gap.le(0.5),
        "threshold_gap_band",
    ] = "medium (0.35-0.5)"
    question_features.loc[
        question_features["threshold_gap_band"].isna() & gap.gt(0.5),
        "threshold_gap_band",
    ] = "wide (>0.5)"
    question_features["threshold_gap_band"] = question_features["threshold_gap_band"].fillna("no_irt_fit")

    red_rate = pd.to_numeric(question_features["redundant_pair_rate_pct"], errors="coerce")
    question_features["redundancy_band"] = "no_step2_dependency_metrics"
    question_features.loc[question_features["flag_dependency_edge_density_raw_eq_1"], "redundancy_band"] = "all-equivalent (density=1.0)"
    question_features.loc[
        question_features["redundancy_band"].eq("no_step2_dependency_metrics") & red_rate.ge(50),
        "redundancy_band",
    ] = "high redundancy (>=50%)"
    question_features.loc[
        question_features["redundancy_band"].eq("no_step2_dependency_metrics") & red_rate.ge(20) & red_rate.lt(50),
        "redundancy_band",
    ] = "moderate redundancy (20-50%)"
    question_features.loc[
        question_features["redundancy_band"].eq("no_step2_dependency_metrics") & red_rate.lt(20),
        "redundancy_band",
    ] = "lower redundancy (<20%)"

    question_features["dependency_metrics_available"] = question_features["num_items"].notna()

    priority_score = (
        question_features["flag_cliff_like"].fillna(False).astype(int) * 4
        + question_features["flag_dependency_edge_density_raw_eq_1"].astype(int) * 4
        + question_features["flag_high_thrasher_rate_ge_5pct"].astype(int) * 3
        + question_features["flag_high_wrong_logic_rate_ge_30pct"].astype(int) * 2
        + question_features["flag_partial_credit_low_information"].fillna(False).astype(int) * 2
        + question_features["flag_very_high_discrimination"].fillna(False).astype(int) * 1
    )
    question_features["redesign_priority_score"] = priority_score

    def reasons(row: pd.Series) -> str:
        out: list[str] = []
        if bool(row.get("flag_cliff_like", False)):
            out.append("cliff-like IRT")
        if bool(row.get("flag_dependency_edge_density_raw_eq_1", False)):
            out.append("dependency density=1.0")
        if bool(row.get("flag_high_thrasher_rate_ge_5pct", False)):
            out.append("high thrasher rate")
        if bool(row.get("flag_high_wrong_logic_rate_ge_30pct", False)):
            out.append("high wrong-output logic rate")
        if bool(row.get("flag_partial_credit_low_information", False)):
            out.append("narrow threshold gap")
        return "; ".join(out)

    question_features["redesign_priority_reasons"] = question_features.apply(reasons, axis=1)
    question_features = question_features.sort_values(
        ["redesign_priority_score", "thrasher_rate_pct", "wrong_logic_rate_pct", "attempts"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    high_priority_targets = question_features.loc[
        question_features[
            [
                "flag_cliff_like",
                "flag_dependency_edge_density_raw_eq_1",
                "flag_high_thrasher_rate_ge_5pct",
            ]
        ]
        .fillna(False)
        .any(axis=1)
    ].copy()

    named_titles = {
        "Pattern printing - Centered Triangle Of Zeroes",
        "Reversed Squares of List Elements",
        "Pangram Check",
    }
    clarity_targets = question_features.copy()
    clarity_targets["flag_named_step7_example"] = clarity_targets["question_title"].isin(named_titles)
    clarity_targets["clarity_review_score"] = (
        pd.to_numeric(clarity_targets["wrong_logic_rate_pct"], errors="coerce").fillna(0) * 0.65
        + pd.to_numeric(clarity_targets["thrasher_rate_pct"], errors="coerce").fillna(0) * 3.0
    ).round(2)
    clarity_targets = clarity_targets.loc[
        (pd.to_numeric(clarity_targets["attempts"], errors="coerce").fillna(0) >= 200)
        & (
            clarity_targets["flag_named_step7_example"]
            | clarity_targets["flag_high_thrasher_rate_ge_5pct"]
            | clarity_targets["flag_high_wrong_logic_rate_ge_30pct"]
        )
    ].sort_values(["flag_named_step7_example", "clarity_review_score", "attempts"], ascending=[False, False, False])

    layered = question_features.copy()
    layered["layered_scoring_readiness"] = "low"
    layered.loc[
        layered["threshold_gap_band"].eq("wide (>0.5)")
        & layered["redundancy_band"].isin(["lower redundancy (<20%)", "moderate redundancy (20-50%)"]),
        "layered_scoring_readiness",
    ] = "higher"
    layered.loc[
        layered["threshold_gap_band"].eq("medium (0.35-0.5)")
        & layered["dependency_metrics_available"].fillna(False),
        "layered_scoring_readiness",
    ] = "medium"
    layered.loc[
        layered["threshold_gap_band"].eq("no_irt_fit"),
        "layered_scoring_readiness",
    ] = "unknown_no_irt_fit"
    layered.loc[
        layered["dependency_metrics_available"].fillna(False).eq(False),
        "layered_scoring_readiness",
    ] = "unknown_missing_step2_dependency_metrics"
    layered.loc[
        layered["flag_dependency_edge_density_raw_eq_1"],
        "layered_scoring_readiness",
    ] = "low"
    layered.loc[
        layered["threshold_gap_band"].eq("narrow (<0.35)") | layered["threshold_gap_band"].eq("missing/collapsed"),
        "layered_scoring_readiness",
    ] = "low"

    readiness_summary = (
        layered.groupby(["layered_scoring_readiness", "threshold_gap_band", "redundancy_band"], dropna=False)
        .agg(questions=("problem_id", "count"))
        .reset_index()
        .sort_values(["questions", "layered_scoring_readiness"], ascending=[False, True])
    )

    feature_coverage = pd.DataFrame(
        [
            {
                "questions_total": int(question_features.shape[0]),
                "questions_with_step2_dependency_metrics": int(question_features["dependency_metrics_available"].fillna(False).sum()),
                "questions_with_irt_flags": int(question_features["a_discrimination"].notna().sum()),
                "questions_with_wrong_logic_rates": int(question_features["wrong_logic_rate_pct"].notna().sum()),
                "questions_with_thrasher_rates": int(question_features["thrasher_rate_pct"].notna().sum()),
            }
        ]
    )

    return {
        "question_redesign_features.csv": question_features,
        "question_redesign_targets_high_priority.csv": high_priority_targets,
        "problem_statement_clarity_review_targets.csv": clarity_targets,
        "layered_scoring_readiness_by_question.csv": layered,
        "layered_scoring_readiness_summary.csv": readiness_summary,
        "question_redesign_feature_coverage_summary.csv": feature_coverage,
    }


def build_low_ability_tables(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    tif = sql_path(INPUTS.tif_flags)
    irt_overall = sql_path(INPUTS.irt_overall)

    tif_flags = qdf(conn, f"SELECT * FROM read_csv_auto('{tif}')")
    tif_flags = tif_flags.sort_values(["info_low_to_mid_ratio", "term", "wave", "namespace"]).reset_index(drop=True)

    by_term_wave = (
        tif_flags.groupby(["term", "wave"], dropna=False)
        .agg(
            namespaces=("namespace", "count"),
            low_ability_blind_namespaces=("flag_low_ability_blind_ratio_lt_0_5", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            median_info_low_to_mid_ratio=("info_low_to_mid_ratio", "median"),
            median_info_peak_theta=("info_peak_theta", "median"),
        )
        .reset_index()
    )
    by_term_wave["low_ability_blind_pct"] = (
        100.0 * by_term_wave["low_ability_blind_namespaces"] / by_term_wave["namespaces"]
    ).round(2)
    by_term_wave["median_info_low_to_mid_ratio"] = by_term_wave["median_info_low_to_mid_ratio"].round(4)
    by_term_wave["median_info_peak_theta"] = by_term_wave["median_info_peak_theta"].round(2)

    overall = qdf(conn, f"SELECT * FROM read_csv_auto('{irt_overall}')")
    overall["low_ability_blind_namespaces"] = int(tif_flags["flag_low_ability_blind_ratio_lt_0_5"].fillna(False).sum())
    overall["low_ability_blind_namespaces"] = overall["low_ability_blind_namespaces"].astype(int)
    overall["low_ability_blind_namespaces_pct"] = (
        100.0 * overall["low_ability_blind_namespaces"] / overall["namespaces_total"]
    ).round(2)
    overall["median_info_low_to_mid_ratio"] = pd.to_numeric(overall["median_info_low_to_mid_ratio"], errors="coerce").round(4)

    warmup_targets = tif_flags.loc[tif_flags["flag_low_ability_blind_ratio_lt_0_5"].fillna(False)].copy()
    warmup_targets = warmup_targets.sort_values(["info_low_to_mid_ratio", "term", "wave", "namespace"])

    return {
        "low_ability_measurement_namespace_summary.csv": tif_flags,
        "low_ability_measurement_term_wave_summary.csv": by_term_wave,
        "low_ability_measurement_overall_summary.csv": overall,
        "warmup_question_target_namespaces.csv": warmup_targets,
    }


def build_variant_and_linking_tables(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    pair_theta = sql_path(INPUTS.namespace_pair_theta)
    pair_drift = sql_path(INPUTS.namespace_pair_anchor_drift)
    pair_link_summary = sql_path(INPUTS.namespace_pair_linking_summary)
    wave_pairs = sql_path(INPUTS.theta_linked_wave_pairs)

    variants = qdf(
        conn,
        f"""
        SELECT
            namespace_a,
            namespace_b,
            pair_type,
            link_feasible,
            n_shared_anchor_items,
            students_a,
            students_b,
            students_overlap_same_id,
            theta_mean_a,
            theta_mean_b,
            theta_mean_b_linked_to_a_scale,
            theta_median_a,
            theta_median_b_linked_to_a_scale,
            theta_overlap_mean_delta_bminus_a,
            theta_overlap_median_delta_bminus_a,
            theta_overlap_corr,
            link_A_b_to_a,
            link_B_b_to_a,
            link_threshold_rmse,
            (theta_mean_b_linked_to_a_scale - theta_mean_a) AS linked_mean_delta_bminus_a
        FROM read_csv_auto('{pair_theta}')
        WHERE pair_type = 'variant_pair_same_slot'
        ORDER BY ABS(theta_mean_b_linked_to_a_scale - theta_mean_a) DESC NULLS LAST, namespace_a, namespace_b
        """,
    )

    variant_drift = qdf(
        conn,
        f"""
        SELECT
            *
        FROM read_csv_auto('{pair_drift}')
        WHERE pair_type = 'variant_pair_same_slot'
        ORDER BY ABS(delta_b1_linked) DESC NULLS LAST, namespace_a, namespace_b
        """,
    )

    if not variant_drift.empty:
        drift_aug = variant_drift.copy()
        for c in ["delta_a_linked", "delta_b1_linked", "delta_b2_linked"]:
            drift_aug[f"abs_{c}"] = pd.to_numeric(drift_aug[c], errors="coerce").abs()
        drift_summary = (
            drift_aug.groupby(["namespace_a", "namespace_b"], dropna=False)
            .agg(
                max_abs_delta_a_linked=("abs_delta_a_linked", "max"),
                max_abs_delta_b1_linked=("abs_delta_b1_linked", "max"),
                max_abs_delta_b2_linked=("abs_delta_b2_linked", "max"),
                anchor_items_large_threshold_drift_gt_0_75=(
                    "abs_delta_b1_linked",
                    lambda s: int((pd.to_numeric(pd.Series(s), errors="coerce") > 0.75).sum()),
                ),
            )
            .reset_index()
        )
        worst_b1_idx = drift_aug.groupby(["namespace_a", "namespace_b"])["abs_delta_b1_linked"].idxmax()
        worst_b1 = drift_aug.loc[worst_b1_idx, ["namespace_a", "namespace_b", "question_title_a", "problem_id_a", "delta_b1_linked"]]
        worst_b1 = worst_b1.rename(
            columns={
                "question_title_a": "worst_b1_drift_question_title",
                "problem_id_a": "worst_b1_drift_problem_id",
                "delta_b1_linked": "worst_b1_drift_delta_b1_linked",
            }
        )
        variant_review = variants.merge(drift_summary, on=["namespace_a", "namespace_b"], how="left").merge(
            worst_b1, on=["namespace_a", "namespace_b"], how="left"
        )
    else:
        variant_review = variants.copy()

    linking_gap_metrics = qdf(
        conn,
        f"""
        WITH pair_summary AS (
            SELECT * FROM read_csv_auto('{pair_link_summary}')
        ),
        wave_standard AS (
            SELECT *
            FROM pair_summary
            WHERE term_a = term_b
              AND wave_a IN ('wave1', 'wave2')
              AND wave_b IN ('wave1', 'wave2')
              AND wave_a <> wave_b
        ),
        wave_compare_rows AS (
            SELECT COUNT(*) AS n_rows
            FROM read_csv_auto('{wave_pairs}')
        )
        SELECT * FROM (
            VALUES
                ('theta_linked_wave_pair_comparisons_rows', (SELECT n_rows FROM wave_compare_rows), 'rows'),
                ('same_term_wave1_wave2_pairs_in_link_summary', (SELECT COUNT(*) FROM wave_standard), 'pairs'),
                ('same_term_wave1_wave2_pairs_with_any_shared_anchors', (SELECT COALESCE(SUM(CASE WHEN n_shared_anchor_items > 0 THEN 1 ELSE 0 END), 0) FROM wave_standard), 'pairs'),
                ('same_term_wave1_wave2_max_shared_anchor_items', (SELECT COALESCE(MAX(n_shared_anchor_items), 0) FROM wave_standard), 'anchors'),
                ('variant_pair_count', (SELECT COUNT(*) FROM pair_summary WHERE pair_type = 'variant_pair_same_slot'), 'pairs')
        ) AS t(metric_name, value, unit)
        """,
    )

    return {
        "variant_equivalence_review_targets.csv": variant_review,
        "variant_anchor_drift_details.csv": variant_drift,
        "linking_gap_summary.csv": linking_gap_metrics,
    }


def build_runtime_and_recovery_tables(conn: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    runtime = sql_path(INPUTS.runtime_error_summary)
    recovery = sql_path(INPUTS.error_recovery_by_type)
    regression = sql_path(INPUTS.regression_summary)

    runtime_by_track = qdf(
        conn,
        f"""
        WITH t AS (
            SELECT
                track,
                best_public_runtime_error_type,
                rows
            FROM read_csv_auto('{runtime}')
        )
        SELECT
            track,
            SUM(rows) AS runtime_rows,
            SUM(CASE WHEN best_public_runtime_error_type = 'Runtime Error (unspecified)' THEN rows ELSE 0 END) AS unspecified_rows,
            ROUND(
                100.0 * SUM(CASE WHEN best_public_runtime_error_type = 'Runtime Error (unspecified)' THEN rows ELSE 0 END)
                / NULLIF(SUM(rows), 0),
                2
            ) AS unspecified_runtime_pct
        FROM t
        GROUP BY 1
        ORDER BY 1
        """,
    )
    runtime_overall = qdf(
        conn,
        f"""
        SELECT
            SUM(rows) AS runtime_rows,
            SUM(CASE WHEN best_public_runtime_error_type = 'Runtime Error (unspecified)' THEN rows ELSE 0 END) AS unspecified_rows,
            ROUND(
                100.0 * SUM(CASE WHEN best_public_runtime_error_type = 'Runtime Error (unspecified)' THEN rows ELSE 0 END)
                / NULLIF(SUM(rows), 0),
                2
            ) AS unspecified_runtime_pct
        FROM read_csv_auto('{runtime}')
        """,
    )

    recovery_signals = qdf(
        conn,
        f"""
        SELECT
            error_type,
            error_family,
            episodes,
            resolved_episodes,
            pct_resolved_within_attempt,
            median_resolution_time_seconds,
            attempts_with_error_type,
            attempts_error_persists_to_final_public_run,
            pct_attempts_error_persists_to_final_public_run,
            pct_resolved_within_1_public_runs,
            pct_resolved_within_2_public_runs
        FROM read_csv_auto('{recovery}')
        WHERE error_type IN ('SyntaxError (structure evident)', 'SyntaxError (no structure)', 'Wrong Answer')
        ORDER BY error_family, error_type
        """,
    )

    regression_overall = qdf(
        conn,
        f"""
        SELECT
            SUM(ended_nonparseable_python_rows) AS ended_nonparseable_python_rows,
            SUM(ended_nonparseable_with_earlier_parseable) AS ended_nonparseable_with_earlier_parseable,
            ROUND(
                100.0 * SUM(ended_nonparseable_with_earlier_parseable) / NULLIF(SUM(ended_nonparseable_python_rows), 0),
                2
            ) AS pct_ended_nonparseable_with_earlier_parseable
        FROM read_csv_auto('{regression}')
        """,
    )

    return {
        "runtime_feedback_quality_by_track.csv": runtime_by_track,
        "runtime_feedback_quality_overall.csv": runtime_overall,
        "debugging_recovery_signal_summary.csv": recovery_signals,
        "parseability_regression_recovery_summary.csv": regression_overall,
    }


def build_key_metrics(conn: duckdb.DuckDBPyConnection, generated: dict[str, pd.DataFrame]) -> pd.DataFrame:
    gating = qdf(conn, f"SELECT * FROM read_csv_auto('{sql_path(INPUTS.gating_waterfall_pct)}')")
    gating_cols = {c.lower(): c for c in gating.columns}
    combined_col = gating_cols.get("combined")
    gate_col = gating_cols.get("gate")
    if gate_col is None or combined_col is None:
        raise ValueError("Unexpected columns in gating_waterfall_pct.csv")
    gating_map = {
        row[gate_col]: float(row[combined_col]) for _, row in gating.iterrows()
    }
    syntax_combined = gating_map.get("Syntax gated — mechanical", 0.0) + gating_map.get("Syntax gated — fundamental", 0.0)
    logic_pct = gating_map.get("Genuine logic failure", 0.0)

    sub_overall = generated["submission_capture_overall_summary.csv"].iloc[0]
    s2_table = generated["s2_bottleneck_summary.csv"]
    if s2_table.empty:
        raise ValueError("s2_bottleneck_summary.csv is empty")
    s2_summary = s2_table.iloc[0]
    archetype_redesign = generated["archetype_redesign_summary.csv"]
    other_row = archetype_redesign.loc[
        (archetype_redesign["archetype"] == "Other") & (archetype_redesign["classification_basis"] == "primary")
    ].iloc[0]
    incr_row = archetype_redesign.loc[
        (archetype_redesign["archetype"] == "Incremental debugger") & (archetype_redesign["classification_basis"] == "flag")
    ].iloc[0]
    thr_row = archetype_redesign.loc[
        (archetype_redesign["archetype"] == "Thrasher") & (archetype_redesign["classification_basis"] == "flag")
    ].iloc[0]

    redundancy_stats = qdf(
        conn,
        f"""
        SELECT
            COUNT(*) AS pair_rows,
            SUM(CASE WHEN abs_phi_correlation > 0.90 THEN 1 ELSE 0 END) AS near_redundant_pairs,
            ROUND(100.0 * SUM(CASE WHEN abs_phi_correlation > 0.90 THEN 1 ELSE 0 END) / COUNT(*), 2) AS near_redundant_pair_pct
        FROM read_csv_auto('{sql_path(INPUTS.question_redundancy_pairs)}')
        """,
    ).iloc[0]
    reliability = qdf(conn, f"SELECT * FROM read_csv_auto('{sql_path(INPUTS.reliability_summary)}')").iloc[0]
    qflags = qdf(
        conn,
        f"""
        SELECT
            COUNT(*) AS questions_fitted,
            SUM(CASE WHEN flag_partial_credit_low_information THEN 1 ELSE 0 END) AS narrow_threshold_questions,
            ROUND(100.0 * SUM(CASE WHEN flag_partial_credit_low_information THEN 1 ELSE 0 END) / COUNT(*), 2) AS narrow_threshold_pct,
            SUM(CASE WHEN flag_cliff_like THEN 1 ELSE 0 END) AS cliff_like_questions
        FROM read_csv_auto('{sql_path(INPUTS.question_flags)}')
        """,
    ).iloc[0]
    low_ability = qdf(
        conn,
        f"""
        SELECT
            COUNT(*) AS namespaces_total,
            SUM(CASE WHEN flag_low_ability_blind_ratio_lt_0_5 THEN 1 ELSE 0 END) AS low_ability_blind_namespaces,
            ROUND(MEDIAN(info_low_to_mid_ratio), 4) AS median_low_to_mid_ratio
        FROM read_csv_auto('{sql_path(INPUTS.tif_flags)}')
        """,
    ).iloc[0]
    variant_review = generated["variant_equivalence_review_targets.csv"]
    max_variant_delta = pd.to_numeric(variant_review["linked_mean_delta_bminus_a"], errors="coerce").abs().max()
    runtime_quality = generated["runtime_feedback_quality_overall.csv"].iloc[0]
    parse_reg = generated["parseability_regression_recovery_summary.csv"].iloc[0]
    recovery = generated["debugging_recovery_signal_summary.csv"]
    syntax_struct = recovery.loc[recovery["error_type"] == "SyntaxError (structure evident)"].iloc[0]
    syntax_no_struct = recovery.loc[recovery["error_type"] == "SyntaxError (no structure)"].iloc[0]
    wrong_answer = recovery.loc[recovery["error_type"] == "Wrong Answer"].iloc[0]
    link_gap = generated["linking_gap_summary.csv"].set_index("metric_name")["value"]

    rows: list[dict[str, Any]] = [
        {
            "metric_group": "Gating",
            "metric_name": "genuine_logic_failure_pct_combined",
            "value": round(logic_pct, 2),
            "unit": "pct",
            "source_files": "syntax_bottleneck_quantified/gating_waterfall_pct.csv",
            "note": "Combined column",
        },
        {
            "metric_group": "Gating",
            "metric_name": "combined_syntax_gated_pct",
            "value": round(syntax_combined, 2),
            "unit": "pct",
            "source_files": "syntax_bottleneck_quantified/gating_waterfall_pct.csv",
            "note": "Mechanical + fundamental",
        },
        {
            "metric_group": "Gating",
            "metric_name": "logic_to_combined_syntax_ratio",
            "value": round(logic_pct / syntax_combined, 2) if syntax_combined else None,
            "unit": "ratio",
            "source_files": "syntax_bottleneck_quantified/gating_waterfall_pct.csv",
            "note": "Genuine logic failure / (syntax mechanical + syntax fundamental)",
        },
        {
            "metric_group": "Instrumentation",
            "metric_name": "zero_submission_namespaces",
            "value": int(sub_overall["zero_submission_namespaces"]),
            "unit": "count",
            "source_files": "process_analysis/attempt_archetypes.csv",
            "note": "Unique namespaces with submission_positive_namespace = false",
        },
        {
            "metric_group": "Instrumentation",
            "metric_name": "namespaces_total",
            "value": int(sub_overall["namespaces_total"]),
            "unit": "count",
            "source_files": "process_analysis/attempt_archetypes.csv",
            "note": "Unique namespaces",
        },
        {
            "metric_group": "Instrumentation",
            "metric_name": "track_b_rows",
            "value": int(sub_overall["track_b_rows"]),
            "unit": "rows",
            "source_files": "error_taxonomy/track_summary.csv",
            "note": "Student-question rows in zero-submission namespaces",
        },
        {
            "metric_group": "Instrumentation",
            "metric_name": "track_b_any_public_all_pass_pct",
            "value": float(sub_overall["track_b_pct_any_public_all_pass"]),
            "unit": "pct",
            "source_files": "process_analysis/attempt_archetypes.csv",
            "note": "Track B rows with any_public_all_pass",
        },
        {
            "metric_group": "Process",
            "metric_name": "s2_self_loop_pct",
            "value": round(float(s2_summary["pct_self_loop"]), 2),
            "unit": "pct",
            "source_files": "process_analysis/death_spiral_absorbing_candidates.csv",
            "note": "State S2 parseable-zero self-loop",
        },
        {
            "metric_group": "Process",
            "metric_name": "s2_pct_of_public_runs",
            "value": round(float(s2_summary.get("pct_all_public_runs", float("nan"))), 2),
            "unit": "pct",
            "source_files": "process_analysis/public_state_distribution_by_track.csv",
            "note": "Combined across tracks",
        },
        {
            "metric_group": "Archetypes",
            "metric_name": "other_unclassified_pct",
            "value": round(float(other_row["pct_all_attempts"]), 2),
            "unit": "pct",
            "source_files": "process_analysis/archetype_outcomes_primary_summary.csv",
            "note": "Primary-archetype Other row",
        },
        {
            "metric_group": "Archetypes",
            "metric_name": "thrasher_vs_incremental_median_active_time_ratio",
            "value": round(float(thr_row["median_active_time_seconds"]) / float(incr_row["median_active_time_seconds"]), 2),
            "unit": "ratio",
            "source_files": "process_analysis/archetype_outcomes_flags_summary.csv",
            "note": "Flag summaries",
        },
        {
            "metric_group": "Test Design",
            "metric_name": "near_redundant_item_pair_pct_phi_gt_0_90",
            "value": float(redundancy_stats["near_redundant_pair_pct"]),
            "unit": "pct",
            "source_files": "classical_item_quality/question_item_redundancy_pairs.csv",
            "note": "Within-question item pairs",
        },
        {
            "metric_group": "Test Design",
            "metric_name": "cronbach_alpha_all_public_private_median_submitter_namespaces",
            "value": float(reliability["alpha_all_median"]),
            "unit": "alpha",
            "source_files": "classical_item_quality/namespace_reliability_summary.csv",
            "note": "12 submission-positive namespaces",
        },
        {
            "metric_group": "IRT",
            "metric_name": "partial_credit_narrow_threshold_questions_pct",
            "value": float(qflags["narrow_threshold_pct"]),
            "unit": "pct",
            "source_files": "psychometric_irt/question_parameter_flags.csv",
            "note": "threshold_gap_b2_minus_b1 < 0.35",
        },
        {
            "metric_group": "IRT",
            "metric_name": "cliff_like_questions",
            "value": int(qflags["cliff_like_questions"]),
            "unit": "count",
            "source_files": "psychometric_irt/question_parameter_flags.csv",
            "note": "flag_cliff_like = true",
        },
        {
            "metric_group": "IRT",
            "metric_name": "low_ability_blind_namespaces",
            "value": int(low_ability["low_ability_blind_namespaces"]),
            "unit": "count",
            "source_files": "psychometric_irt/tif_low_ability_flags.csv",
            "note": "flag_low_ability_blind_ratio_lt_0_5 = true",
        },
        {
            "metric_group": "IRT",
            "metric_name": "median_low_to_mid_information_ratio",
            "value": float(low_ability["median_low_to_mid_ratio"]),
            "unit": "ratio",
            "source_files": "psychometric_irt/tif_low_ability_flags.csv",
            "note": "Median info_low_to_mid_ratio",
        },
        {
            "metric_group": "Linking",
            "metric_name": "theta_linked_wave_pair_comparisons_rows",
            "value": int(link_gap["theta_linked_wave_pair_comparisons_rows"]),
            "unit": "rows",
            "source_files": "psychometric_irt/theta_linked_wave_pair_comparisons.csv",
            "note": "Usable wave-pair linked comparisons exported",
        },
        {
            "metric_group": "Linking",
            "metric_name": "max_abs_variant_linked_mean_theta_delta",
            "value": round(float(max_variant_delta), 3) if pd.notna(max_variant_delta) else None,
            "unit": "theta",
            "source_files": "psychometric_irt/namespace_pair_theta_linked_comparisons.csv",
            "note": "Variant pairs only",
        },
        {
            "metric_group": "Runtime Feedback",
            "metric_name": "runtime_error_unspecified_pct",
            "value": float(runtime_quality["unspecified_runtime_pct"]),
            "unit": "pct",
            "source_files": "error_taxonomy/runtime_error_type_summary.csv",
            "note": "All runtime-error rows",
        },
        {
            "metric_group": "Recovery",
            "metric_name": "ended_nonparseable_with_earlier_parseable_pct",
            "value": float(parse_reg["pct_ended_nonparseable_with_earlier_parseable"]),
            "unit": "pct",
            "source_files": "error_taxonomy/regression_summary.csv",
            "note": "Weighted across tracks",
        },
        {
            "metric_group": "Recovery",
            "metric_name": "syntax_structure_evident_resolved_within_1_run_pct",
            "value": float(syntax_struct["pct_resolved_within_1_public_runs"]),
            "unit": "pct",
            "source_files": "process_analysis/error_recovery_by_type.csv",
            "note": "SyntaxError (structure evident)",
        },
        {
            "metric_group": "Recovery",
            "metric_name": "syntax_no_structure_resolved_within_1_run_pct",
            "value": float(syntax_no_struct["pct_resolved_within_1_public_runs"]),
            "unit": "pct",
            "source_files": "process_analysis/error_recovery_by_type.csv",
            "note": "SyntaxError (no structure)",
        },
        {
            "metric_group": "Recovery",
            "metric_name": "wrong_answer_persists_to_final_public_run_pct",
            "value": float(wrong_answer["pct_attempts_error_persists_to_final_public_run"]),
            "unit": "pct",
            "source_files": "process_analysis/error_recovery_by_type.csv",
            "note": "Wrong Answer error_family row",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    ensure_inputs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/9] Opening DuckDB and building submission-capture audits...")
    conn = make_conn()
    outputs: dict[str, pd.DataFrame] = {}
    outputs.update(build_submission_capture_audits(conn))
    for name in [
        "submission_capture_track_row_summary.csv",
        "submission_capture_namespace_audit.csv",
        "submission_capture_zero_submission_namespaces.csv",
        "submission_capture_term_wave_namespace_summary.csv",
        "submission_capture_overall_summary.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[2/9] Building S2 bottleneck summaries...")
    outputs.update(build_s2_bottleneck(conn))
    for name in [
        "public_state_distribution_combined.csv",
        "s2_bottleneck_summary.csv",
        "s2_transition_destinations.csv",
        "s2_escape_routes.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[3/9] Building archetype intervention tables...")
    outputs.update(build_archetype_tables(conn))
    for name in [
        "archetype_redesign_summary.csv",
        "archetype_incremental_vs_thrasher_comparison.csv",
        "archetype_other_by_question.csv",
        "archetype_other_signature_clusters.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[4/9] Building question redesign target lists...")
    outputs.update(build_question_redesign_tables(conn))
    for name in [
        "question_redesign_features.csv",
        "question_redesign_targets_high_priority.csv",
        "problem_statement_clarity_review_targets.csv",
        "layered_scoring_readiness_by_question.csv",
        "layered_scoring_readiness_summary.csv",
        "question_redesign_feature_coverage_summary.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[5/9] Building low-ability measurement summaries...")
    outputs.update(build_low_ability_tables(conn))
    for name in [
        "low_ability_measurement_namespace_summary.csv",
        "low_ability_measurement_term_wave_summary.csv",
        "low_ability_measurement_overall_summary.csv",
        "warmup_question_target_namespaces.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[6/9] Building variant-equivalence and linking-gap tables...")
    outputs.update(build_variant_and_linking_tables(conn))
    for name in [
        "variant_equivalence_review_targets.csv",
        "variant_anchor_drift_details.csv",
        "linking_gap_summary.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[7/9] Building runtime-feedback and recovery summaries...")
    outputs.update(build_runtime_and_recovery_tables(conn))
    for name in [
        "runtime_feedback_quality_by_track.csv",
        "runtime_feedback_quality_overall.csv",
        "debugging_recovery_signal_summary.csv",
        "parseability_regression_recovery_summary.csv",
    ]:
        write_csv(outputs[name], OUT_DIR / name)

    print("[8/9] Writing Step 7 key metrics table...")
    key_metrics = build_key_metrics(conn, outputs)
    write_csv(key_metrics, OUT_DIR / "step7_key_metrics.csv")

    print("[9/9] Writing output manifest...")
    write_manifest()
    conn.close()
    print(f"Wrote Step 7 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
