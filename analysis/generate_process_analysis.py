#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
#   "pyarrow>=16.0.0",
#   "tree-sitter>=0.22.0",
#   "tree-sitter-python>=0.23.0",
# ]
# ///
"""Step 5: Process Analysis — What the Snapshots Reveal.

This script builds full-population process features (151,778 student-question rows)
from ``analysis/submission_timeline.parquet`` and tree-sitter structural tracking.

Outputs are written under ``analysis/process_analysis/`` and support the manual
README section "# Process Analysis — What the Snapshots Reveal".

Design notes:
- Uses the Step 3 selected-row table for track / term / wave / outcome metadata.
- Uses question-aware scaffold stripping before tree-sitter analysis (same fix as Step 3).
- Parses unique ``(namespace, problem_id, code_sha256)`` snapshots once, then joins
  features back to the 2.06M-event timeline.
- Recovery analysis and death-spiral transitions are computed on public ``test_run``
  sequences (the only universally available comparable run stream).
"""

from __future__ import annotations

import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.generate_error_taxonomy import (  # noqa: E402
    SkeletonInfo,
    extract_student_editable_code,
    load_question_skeletons,
    normalize_code_text,
)

ANALYSIS_DIR = ROOT / "analysis"
STEP3_DIR = ANALYSIS_DIR / "error_taxonomy"
OUT_DIR = ANALYSIS_DIR / "process_analysis"
PY_LANGUAGE = Language(tspython.language())

TRACK_A_SUBMITTERS = "Track A: submitters"
TRACK_A_NON_SUBMIT = "Track A: non-submitters (submission-positive NS)"
TRACK_B = "Track B: zero-submission namespaces"

ATTEMPT_KEY_COLS = ["namespace", "problem_id", "student_id"]
STATE_ORDER = {
    "S0_no_code": 0,
    "S1_syntax_fundamental": 1,
    "S1b_syntax_structure": 2,
    "S2_parseable_zero": 3,
    "S3_public_partial": 4,
    "S4_public_all": 5,
    "S5_all_tests": 6,
}

STATE_LABELS = {
    "S0_no_code": "State 0: no code beyond skeleton",
    "S1_syntax_fundamental": "State 1: non-parseable, no recoverable structure",
    "S1b_syntax_structure": "State 1b: non-parseable, structure evident",
    "S2_parseable_zero": "State 2: parseable, passes 0 public tests",
    "S3_public_partial": "State 3: passes some (not all) public tests",
    "S4_public_all": "State 4: passes all public tests",
    "S5_all_tests": "State 5: passes all tests (Track A full pass)",
}

CONSTRUCT_TRACK_COLS = [
    "function_def",
    "for_loop",
    "while_loop",
    "if_stmt",
    "list_comp",
    "dict_comp",
    "try_stmt",
    "class_def",
    "return_stmt",
    "print_call",
    "import_stmt",
    "import_from_stmt",
]
CONSTRUCT_NODE_MAP_FAST: dict[str, str] = {
    "function_def": "function_definition",
    "for_loop": "for_statement",
    "while_loop": "while_statement",
    "if_stmt": "if_statement",
    "list_comp": "list_comprehension",
    "dict_comp": "dictionary_comprehension",
    "try_stmt": "try_statement",
    "class_def": "class_definition",
    "return_stmt": "return_statement",
    "import_stmt": "import_statement",
    "import_from_stmt": "import_from_statement",
}
NODE_TYPE_TO_CONSTRUCT_FAST = {v: k for k, v in CONSTRUCT_NODE_MAP_FAST.items()}

RUNTIME_EXC_PATTERN = re.compile(
    r"\b(NameError|TypeError|IndexError|KeyError|ValueError|ZeroDivisionError|RecursionError|AttributeError|MemoryError|AssertionError|RuntimeError|OverflowError|ImportError|ModuleNotFoundError|UnboundLocalError|StopIteration|FileNotFoundError|PermissionError|OSError|EOFError)\b"
)


class FastTsAnalyzer:
    """Lower-overhead tree-sitter analyzer for Step 5 full-population timeline work."""

    def __init__(self) -> None:
        self.parser = Parser(PY_LANGUAGE)

    def analyze(self, code: str | None) -> dict[str, Any]:
        if not code:
            code = ""
        source = code.encode("utf-8", errors="replace")
        tree = self.parser.parse(source)
        root = tree.root_node

        counts: dict[str, int] = {k: 0 for k in CONSTRUCT_TRACK_COLS}
        error_count = 0
        missing_count = 0
        node_count = 0
        max_depth = 0

        stack = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            node_count += 1
            if depth > max_depth:
                max_depth = depth
            ntype = node.type

            c = NODE_TYPE_TO_CONSTRUCT_FAST.get(ntype)
            if c is not None:
                counts[c] += 1

            if ntype == "call":
                fn = node.child_by_field_name("function")
                if fn is not None:
                    fn_text = source[fn.start_byte : fn.end_byte].decode("utf-8", errors="ignore").strip()
                    if fn_text == "print":
                        counts["print_call"] += 1

            if ntype == "ERROR":
                error_count += 1
            if node.is_missing:
                missing_count += 1

            for child in reversed(node.children):
                stack.append((child, depth + 1))

        complexity_score = (
            counts["function_def"] * 3
            + counts["class_def"] * 4
            + counts["for_loop"] * 2
            + counts["while_loop"] * 2
            + counts["if_stmt"]
            + counts["list_comp"] * 2
            + counts["dict_comp"] * 2
            + counts["try_stmt"] * 2
            + counts["return_stmt"]
            + counts["print_call"]
            + counts["import_stmt"]
            + counts["import_from_stmt"]
        )

        out: dict[str, Any] = {
            "ts_error_count": int(error_count),
            "ts_missing_token_count": int(missing_count),
            "ts_node_count": int(node_count),
            "ts_max_depth": int(max_depth),
            "ts_complexity_score": int(complexity_score),
        }
        for ckey in CONSTRUCT_TRACK_COLS:
            out[f"ts_count_{ckey}"] = int(counts[ckey])
            out[f"ts_has_{ckey}"] = bool(counts[ckey] > 0)
        return out


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


def one_row(conn: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    df = qdf(conn, sql)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def _fetch_df_chunks(
    cursor: duckdb.DuckDBPyConnection,
    *,
    vectors_per_chunk: int = 50,
) -> Iterable[pd.DataFrame]:
    if hasattr(cursor, "fetch_df_chunk"):
        while True:
            chunk = cursor.fetch_df_chunk(vectors_per_chunk=vectors_per_chunk)
            if chunk is None or chunk.empty:
                break
            yield chunk
        return

    cols = [d[0] for d in cursor.description]
    while True:
        rows = cursor.fetchmany(50_000)
        if not rows:
            break
        yield pd.DataFrame(rows, columns=cols)


def boolify_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    low = s.astype(str).str.strip().str.lower()
    return low.isin({"true", "1", "t", "yes", "y"})


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def load_attempt_base() -> pd.DataFrame:
    print("[1/11] Loading Step 3/4 metadata tables...")
    sel = pd.read_csv(STEP3_DIR / "selected_snapshot_taxonomy_rows.csv", low_memory=False)
    reg = pd.read_csv(STEP3_DIR / "regression_rows.csv", low_memory=False)

    keep_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "track",
        "term",
        "wave",
        "question_title",
        "outcome_category",
        "submission_positive_namespace",
        "is_python_question",
        "active_time_seconds",
        "latest_submission_score",
        "problem_max_score",
        "skeleton_modification_status",
        "selected_tree_sitter_parseable",
        "ts_error_count",
        "ts_missing_token_count",
    ]
    sel = sel[[c for c in keep_cols if c in sel.columns]].copy()

    for col in ["problem_id", "active_time_seconds", "latest_submission_score", "problem_max_score"]:
        if col in sel.columns:
            sel[col] = to_num(sel[col])
    for col in ["submission_positive_namespace", "is_python_question", "selected_tree_sitter_parseable"]:
        if col in sel.columns:
            sel[col] = boolify_series(sel[col])
    for col in ["ts_error_count", "ts_missing_token_count"]:
        if col in sel.columns:
            sel[col] = to_num(sel[col])

    reg_keep = [
        "namespace",
        "problem_id",
        "student_id",
        "parseability_regression_flag",
        "peak_to_last_public_regression_flag",
        "structural_regression_vs_best_public_flag",
        "structural_regression_vs_last_parseable_flag",
    ]
    reg = reg[[c for c in reg_keep if c in reg.columns]].copy()
    if "problem_id" in reg.columns:
        reg["problem_id"] = to_num(reg["problem_id"])
    for col in [
        "parseability_regression_flag",
        "peak_to_last_public_regression_flag",
        "structural_regression_vs_best_public_flag",
        "structural_regression_vs_last_parseable_flag",
    ]:
        if col in reg.columns:
            reg[col] = boolify_series(reg[col])

    base = sel.merge(reg, on=ATTEMPT_KEY_COLS, how="left")
    for col in [
        "parseability_regression_flag",
        "peak_to_last_public_regression_flag",
        "structural_regression_vs_best_public_flag",
        "structural_regression_vs_last_parseable_flag",
    ]:
        if col in base.columns:
            base[col] = base[col].fillna(False)

    # Track-compatible final outcome metric: private score for submitters, best public pass count for others.
    base["latest_submission_score"] = to_num(base.get("latest_submission_score", pd.Series(dtype=float)))
    base["problem_id"] = to_num(base["problem_id"]).astype("Int64")
    base.sort_values(ATTEMPT_KEY_COLS, inplace=True)
    base.to_csv(OUT_DIR / "attempt_base_metadata.csv", index=False)
    return base


def syntax_structure_evident_from_metrics(
    *,
    is_parseable: bool | None,
    ts_error_count: float | int | None,
    ts_missing_token_count: float | int | None,
    ts_node_count: float | int | None,
    new_constructs_added: float | int | None,
    meaningful_lines_beyond_skeleton: float | int | None,
) -> bool:
    if bool(is_parseable):
        return False
    err = int(ts_error_count or 0)
    miss = int(ts_missing_token_count or 0)
    if (err + miss) <= 0:
        return False
    nodes = max(1, int(ts_node_count or 0))
    error_density = (err + miss) / nodes
    newc = int(new_constructs_added or 0)
    extra_lines = int(meaningful_lines_beyond_skeleton or 0)
    return (err <= 3) and (miss <= 5) and (error_density < 0.08) and (newc > 0 or extra_lines >= 3)


def parse_qhash_structural_features(
    conn: duckdb.DuckDBPyConnection,
    attempt_base: pd.DataFrame,
    skeleton_map: dict[tuple[str, int], SkeletonInfo],
) -> Path:
    print("[2/11] Parsing tree-sitter structural features for all unique (question, code_hash) snapshots...")
    qhash_path = OUT_DIR / "qhash_structural_features.parquet"
    summary_path = OUT_DIR / "qhash_structural_features_summary.csv"

    py_q = attempt_base[attempt_base["is_python_question"] == True][["namespace", "problem_id"]].drop_duplicates()  # noqa: E712
    py_q = py_q.copy()
    py_q["problem_id"] = to_num(py_q["problem_id"]).astype("Int64")
    conn.register("step5_py_q_df", py_q)
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW step5_py_questions_v AS
        SELECT DISTINCT namespace, CAST(problem_id AS INTEGER) AS problem_id
        FROM step5_py_q_df
        """
    )
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW step5_qhash_v AS
        SELECT DISTINCT t.namespace, CAST(t.problem_id AS INTEGER) AS problem_id, t.code_sha256
        FROM read_parquet('analysis/submission_timeline.parquet') t
        JOIN step5_py_questions_v q USING (namespace, problem_id)
        WHERE t.code_sha256 IS NOT NULL AND t.code_sha256 <> ''
        """
    )
    expected = int(one_row(conn, "SELECT COUNT(*) AS n FROM step5_qhash_v").get("n", 0) or 0)
    print(f"  expected unique question-hash rows: {expected:,}")

    if qhash_path.exists():
        try:
            cached_n = int(
                one_row(conn, f"SELECT COUNT(*) AS n FROM read_parquet('{qhash_path.as_posix()}')").get("n", 0) or 0
            )
            if cached_n == expected and expected > 0:
                print(f"  reusing cached qhash structural features ({cached_n:,} rows)")
                if not summary_path.exists():
                    qdf(
                        conn,
                        f"""
                        SELECT
                          COUNT(*) AS qhash_rows,
                          COUNT(*) FILTER (WHERE ts_tree_parseable) AS ts_tree_parseable_rows,
                          COUNT(*) FILTER (WHERE syntax_structure_evident) AS syntax_structure_evident_rows,
                          COUNT(*) FILTER (WHERE ts_has_any_error) AS ts_has_any_error_rows,
                          COUNT(*) FILTER (WHERE strip_status = 'prefix_suffix_not_found') AS strip_prefix_suffix_not_found_rows
                        FROM read_parquet('{qhash_path.as_posix()}')
                        """,
                    ).to_csv(summary_path, index=False)
                return qhash_path
        except Exception:
            pass

    analyzer = FastTsAnalyzer()
    tmp_path = qhash_path.with_suffix(".tmp.parquet")
    if tmp_path.exists():
        tmp_path.unlink()

    cursor = conn.execute(
        """
        SELECT q.namespace, q.problem_id, q.code_sha256, c.code_snapshot
        FROM step5_qhash_v q
        JOIN read_parquet('analysis/code_snapshots.parquet') c USING (code_sha256)
        ORDER BY q.namespace, q.problem_id, q.code_sha256
        """
    )

    writer: pq.ParquetWriter | None = None
    rows_buffer: list[dict[str, Any]] = []
    processed = 0
    strip_counter: Counter[str] = Counter()

    def flush() -> None:
        nonlocal writer, rows_buffer
        if not rows_buffer:
            return
        df = pd.DataFrame(rows_buffer)
        table = pa.Table.from_pandas(df, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(tmp_path, table.schema, compression="zstd")
        writer.write_table(table)
        rows_buffer = []

    for chunk in _fetch_df_chunks(cursor, vectors_per_chunk=30):
        for rec in chunk.itertuples(index=False):
            namespace = str(rec.namespace)
            problem_id = int(rec.problem_id)
            code_sha256 = str(rec.code_sha256)
            sk = skeleton_map.get((namespace, problem_id))
            if sk is None:
                continue
            full_code = rec.code_snapshot if isinstance(rec.code_snapshot, str) else ("" if pd.isna(rec.code_snapshot) else str(rec.code_snapshot))
            student_code, strip_status = extract_student_editable_code(full_code, sk)
            strip_counter[strip_status] += 1
            norm_student = normalize_code_text(student_code)
            ts = analyzer.analyze(student_code)
            student_code_len = len(student_code)
            skeleton_norm_len = len(sk.skeleton_norm)
            new_constructs = 0
            for c in CONSTRUCT_TRACK_COLS:
                stud = int(ts.get(f"ts_count_{c}", 0) or 0)
                skel = int(sk.skeleton_feature_hash.get(f"ts_count_{c}", 0) or 0)
                new_constructs += max(0, stud - skel)

            syn_mech = syntax_structure_evident_from_metrics(
                is_parseable=False,  # tree-sitter-only criterion; caller applies AST flag from timeline
                ts_error_count=ts.get("ts_error_count"),
                ts_missing_token_count=ts.get("ts_missing_token_count"),
                ts_node_count=ts.get("ts_node_count"),
                new_constructs_added=new_constructs,
                meaningful_lines_beyond_skeleton=0,
            )
            row = {
                "namespace": namespace,
                "problem_id": problem_id,
                "code_sha256": code_sha256,
                "strip_status": strip_status,
                "student_code_length": int(student_code_len),
                "skeleton_norm_length": int(skeleton_norm_len),
                "normalized_equals_skeleton": bool(norm_student == sk.skeleton_norm),
                "new_constructs_added": int(new_constructs),
                "ts_has_any_error": bool((int(ts.get("ts_error_count", 0) or 0) + int(ts.get("ts_missing_token_count", 0) or 0)) > 0),
                "ts_tree_parseable": bool((int(ts.get("ts_error_count", 0) or 0) == 0) and (int(ts.get("ts_missing_token_count", 0) or 0) == 0)),
                "syntax_structure_evident": bool(syn_mech),
            }
            for c in CONSTRUCT_TRACK_COLS:
                row[f"ts_has_{c}"] = bool(ts.get(f"ts_has_{c}", False))
            for c in [
                "ts_error_count",
                "ts_missing_token_count",
                "ts_node_count",
                "ts_max_depth",
                "ts_complexity_score",
            ]:
                val = ts.get(c)
                row[c] = (int(val) if val is not None and not (isinstance(val, float) and math.isnan(val)) else None)
            rows_buffer.append(row)
            processed += 1
        if len(rows_buffer) >= 20_000:
            flush()
        if processed and processed % 5_000 == 0:
            print(f"  parsed {processed:,}/{expected:,} qhash snapshots...")

    flush()
    if writer is not None:
        writer.close()
    tmp_path.replace(qhash_path)

    summary = pd.DataFrame(
        [
            {
                "qhash_rows": processed,
                "expected_qhash_rows": expected,
                "pct_expected_covered": round(100.0 * processed / expected, 2) if expected else np.nan,
                "strip_status": k,
                "rows": v,
                "pct_rows": round(100.0 * v / processed, 2) if processed else np.nan,
            }
            for k, v in sorted(strip_counter.items())
        ]
    )
    summary.to_csv(summary_path, index=False)
    qdf(
        conn,
        f"""
        SELECT
          COUNT(*) AS qhash_rows,
          COUNT(*) FILTER (WHERE ts_tree_parseable) AS ts_tree_parseable_rows,
          ROUND(100.0 * COUNT(*) FILTER (WHERE ts_tree_parseable) / COUNT(*), 2) AS pct_ts_tree_parseable,
          COUNT(*) FILTER (WHERE ts_has_any_error) AS ts_has_any_error_rows,
          COUNT(*) FILTER (WHERE syntax_structure_evident) AS syntax_structure_evident_rows
        FROM read_parquet('{qhash_path.as_posix()}')
        """,
    ).to_csv(OUT_DIR / "qhash_tree_sitter_parse_summary.csv", index=False)
    return qhash_path


def write_enriched_event_timeline_parquet(
    conn: duckdb.DuckDBPyConnection,
    attempt_base: pd.DataFrame,
    qhash_path: Path,
) -> Path:
    print("[3/11] Materializing enriched event timeline parquet...")
    out_path = OUT_DIR / "timeline_event_features.parquet"
    conn.register("step5_attempt_base_df", attempt_base)
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW step5_attempt_base_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          student_id,
          track,
          term,
          wave,
          question_title,
          outcome_category,
          CAST(submission_positive_namespace AS BOOLEAN) AS submission_positive_namespace,
          CAST(is_python_question AS BOOLEAN) AS is_python_question,
          CAST(active_time_seconds AS DOUBLE) AS active_time_seconds,
          CAST(latest_submission_score AS DOUBLE) AS latest_submission_score,
          CAST(problem_max_score AS DOUBLE) AS problem_max_score,
          skeleton_modification_status,
          CAST(parseability_regression_flag AS BOOLEAN) AS parseability_regression_flag,
          CAST(peak_to_last_public_regression_flag AS BOOLEAN) AS peak_to_last_public_regression_flag,
          CAST(structural_regression_vs_best_public_flag AS BOOLEAN) AS structural_regression_vs_best_public_flag,
          CAST(structural_regression_vs_last_parseable_flag AS BOOLEAN) AS structural_regression_vs_last_parseable_flag
        FROM step5_attempt_base_df
        """
    )

    if out_path.exists():
        out_path.unlink()

    escaped = out_path.as_posix().replace("'", "''")
    qhash_escaped = qhash_path.as_posix().replace("'", "''")
    conn.execute(
        f"""
        COPY (
          SELECT
            t.namespace,
            CAST(t.problem_id AS INTEGER) AS problem_id,
            t.student_id,
            a.track,
            a.term,
            a.wave,
            a.question_title,
            a.outcome_category,
            a.submission_positive_namespace,
            a.is_python_question,
            a.active_time_seconds,
            a.latest_submission_score,
            a.problem_max_score,
            a.skeleton_modification_status,
            a.parseability_regression_flag,
            a.peak_to_last_public_regression_flag,
            a.structural_regression_vs_best_public_flag,
            a.structural_regression_vs_last_parseable_flag,
            CAST(t.timestamp_utc AS TIMESTAMP) AS timestamp_utc,
            CAST(t.seconds_since_start AS DOUBLE) AS seconds_since_start,
            t.event_type,
            t.evaluation_type,
            t.code_length,
            COALESCE(t.is_parseable, FALSE) AS is_parseable,
            t.summary,
            t.reason,
            t.num_test_passed,
            t.test_case_count,
            CASE t.event_type WHEN 'submission' THEN 3 WHEN 'test_run' THEN 2 ELSE 1 END AS event_type_order,
            qh.strip_status,
            qh.student_code_length,
            qh.skeleton_norm_length,
            qh.normalized_equals_skeleton,
            qh.new_constructs_added,
            qh.ts_has_any_error,
            qh.ts_tree_parseable,
            qh.syntax_structure_evident,
            qh.ts_error_count,
            qh.ts_missing_token_count,
            qh.ts_node_count,
            qh.ts_max_depth,
            qh.ts_complexity_score,
            qh.ts_has_function_def,
            qh.ts_has_for_loop,
            qh.ts_has_while_loop,
            qh.ts_has_if_stmt,
            qh.ts_has_list_comp,
            qh.ts_has_dict_comp,
            qh.ts_has_try_stmt,
            qh.ts_has_class_def,
            qh.ts_has_return_stmt,
            qh.ts_has_print_call,
            qh.ts_has_import_stmt,
            qh.ts_has_import_from_stmt
          FROM read_parquet('analysis/submission_timeline.parquet') t
          JOIN step5_attempt_base_v a
            ON a.namespace = t.namespace
           AND a.problem_id = CAST(t.problem_id AS INTEGER)
           AND a.student_id = t.student_id
          LEFT JOIN read_parquet('{qhash_escaped}') qh
            ON qh.namespace = t.namespace
           AND qh.problem_id = CAST(t.problem_id AS INTEGER)
           AND qh.code_sha256 = t.code_sha256
          ORDER BY
            t.namespace,
            CAST(t.problem_id AS INTEGER),
            t.student_id,
            CAST(t.timestamp_utc AS TIMESTAMP),
            CASE t.event_type WHEN 'submission' THEN 3 WHEN 'test_run' THEN 2 ELSE 1 END,
            COALESCE(t.evaluation_type, ''),
            COALESCE(t.code_sha256, '')
        ) TO '{escaped}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    qdf(
        conn,
        f"""
        SELECT
          COUNT(*) AS event_rows,
          COUNT(*) FILTER (WHERE event_type = 'test_run') AS test_run_rows,
          COUNT(*) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS public_test_run_rows,
          COUNT(DISTINCT (namespace, problem_id, student_id)) AS attempts_covered
        FROM read_parquet('{out_path.as_posix()}')
        """,
    ).to_csv(OUT_DIR / "timeline_event_features_coverage.csv", index=False)
    return out_path


def _runtime_subtype_from_reason(reason: Any, summary: Any) -> str | None:
    summary_s = "" if pd.isna(summary) else str(summary)
    if summary_s == "Time Limit Exceeded":
        return "Timeout"
    if summary_s != "Runtime Error":
        return None
    if pd.isna(reason) or reason is None or str(reason).strip() == "":
        return "Runtime Error"
    m = RUNTIME_EXC_PATTERN.search(str(reason))
    if m:
        return m.group(1)
    return "Runtime Error"


def classify_event_level_states(event_df: pd.DataFrame) -> pd.DataFrame:
    print("[4/11] Computing event-level deltas, state labels, and public-run error categories...")
    df = event_df
    df["problem_id"] = to_num(df["problem_id"]).astype("Int64")
    df["seconds_since_start"] = to_num(df["seconds_since_start"])
    df["code_length"] = to_num(df["code_length"])
    df["num_test_passed"] = to_num(df["num_test_passed"])
    df["test_case_count"] = to_num(df["test_case_count"])
    for c in [
        "active_time_seconds",
        "latest_submission_score",
        "problem_max_score",
        "student_code_length",
        "skeleton_norm_length",
        "new_constructs_added",
        "ts_error_count",
        "ts_missing_token_count",
        "ts_node_count",
        "ts_complexity_score",
    ]:
        if c in df.columns:
            df[c] = to_num(df[c])

    for c in [
        "submission_positive_namespace",
        "is_python_question",
        "is_parseable",
        "normalized_equals_skeleton",
        "ts_has_any_error",
        "ts_tree_parseable",
        "syntax_structure_evident",
        "parseability_regression_flag",
        "peak_to_last_public_regression_flag",
        "structural_regression_vs_best_public_flag",
        "structural_regression_vs_last_parseable_flag",
    ]:
        if c in df.columns:
            df[c] = boolify_series(df[c])

    for c in [f"ts_has_{x}" for x in CONSTRUCT_TRACK_COLS]:
        if c in df.columns:
            df[c] = boolify_series(df[c])

    df.sort_values(
        ["namespace", "problem_id", "student_id", "seconds_since_start", "event_type_order", "evaluation_type"],
        inplace=True,
        kind="mergesort",
    )

    g = df.groupby(ATTEMPT_KEY_COLS, sort=False, dropna=False)
    df["attempt_event_index"] = g.cumcount() + 1

    prev_secs = g["seconds_since_start"].shift(1)
    df["delta_seconds"] = df["seconds_since_start"] - prev_secs
    df["delta_seconds"] = df["delta_seconds"].where(df["delta_seconds"].notna() & (df["delta_seconds"] >= 0))

    prev_code_len = g["code_length"].shift(1)
    code_drop = (prev_code_len - df["code_length"]) / prev_code_len
    code_rise = (df["code_length"] - prev_code_len) / prev_code_len
    df["code_length_drop_pct"] = code_drop.where(prev_code_len > 0)
    df["code_length_rise_pct"] = code_rise.where(prev_code_len > 0)
    df["large_deletion_event"] = df["code_length_drop_pct"].fillna(-np.inf) > 0.30
    df["large_increase_event"] = df["code_length_rise_pct"].fillna(-np.inf) > 0.30

    prev_complexity = g["ts_complexity_score"].shift(1)
    complexity_drop = (prev_complexity - df["ts_complexity_score"]) / prev_complexity
    df["structural_complexity_drop_pct"] = complexity_drop.where(prev_complexity > 0)
    df["structural_regression_event"] = df["structural_complexity_drop_pct"].fillna(-np.inf) > 0.30
    df["structural_complexity_delta"] = df["ts_complexity_score"] - prev_complexity

    err_total = df["ts_error_count"].fillna(0) + df["ts_missing_token_count"].fillna(0)
    prev_err_total = err_total.groupby(
        [df["namespace"], df["problem_id"], df["student_id"]],
        sort=False,
        dropna=False,
    ).shift(1)
    df["ts_error_total"] = err_total
    df["ts_error_total_delta"] = err_total - prev_err_total
    df["ts_error_increase_event"] = df["ts_error_total_delta"].fillna(0) > 0
    df["ts_error_decrease_event"] = df["ts_error_total_delta"].fillna(0) < 0

    if "meaningful_lines_beyond_skeleton" not in df.columns:
        df["meaningful_lines_beyond_skeleton"] = np.nan
    if "student_meaningful_lines" not in df.columns:
        # Approximation placeholder; Step 5 uses this only for state-0 heuristics.
        df["student_meaningful_lines"] = np.nan
    meaningful_extra = df["meaningful_lines_beyond_skeleton"].fillna(0)
    new_constructs = df["new_constructs_added"].fillna(0)
    student_meaningful = df["student_meaningful_lines"].fillna(np.nan)
    normalized_equals_skeleton = df["normalized_equals_skeleton"].fillna(False)
    student_code_len = df["student_code_length"].fillna(0)
    skeleton_norm_len = df["skeleton_norm_length"].fillna(0)
    near_skeleton_len = (student_code_len - skeleton_norm_len).abs().fillna(np.inf) <= 8
    df["no_code_beyond_skeleton_flag"] = (
        normalized_equals_skeleton
        | (
            (new_constructs <= 0)
            & (
                near_skeleton_len
                | (student_code_len <= 4)
            )
        )
    )
    df["meaningful_edit_beyond_skeleton_flag"] = (~normalized_equals_skeleton) | (new_constructs > 0) | (meaningful_extra >= 3)

    public_mask = (df["event_type"] == "test_run") & (df["evaluation_type"] == "public")
    pub = df.loc[public_mask].copy()
    pub["public_run_index"] = pub.groupby(ATTEMPT_KEY_COLS, sort=False, dropna=False).cumcount() + 1

    # Public error categories (timeline-level; runtime subtypes are mostly unavailable because `reason` is blank).
    pub["public_error_type"] = "Other"
    summary_s = pub["summary"].fillna("").astype(str)
    is_parse_pub = pub["is_parseable"].fillna(False)
    pub.loc[~is_parse_pub & pub["syntax_structure_evident"].fillna(False), "public_error_type"] = "SyntaxError (structure evident)"
    pub.loc[~is_parse_pub & ~pub["syntax_structure_evident"].fillna(False), "public_error_type"] = "SyntaxError (no structure)"
    pub.loc[is_parse_pub & summary_s.eq("All Cases Passed"), "public_error_type"] = "All Cases Passed"
    pub.loc[is_parse_pub & summary_s.eq("Wrong Answer"), "public_error_type"] = "Wrong Answer"
    pub.loc[is_parse_pub & summary_s.eq("Time Limit Exceeded"), "public_error_type"] = "Timeout"
    pub.loc[is_parse_pub & summary_s.eq("Not able to run"), "public_error_type"] = "Not able to run"
    runtime_mask = is_parse_pub & summary_s.eq("Runtime Error")
    if runtime_mask.any():
        pub.loc[runtime_mask, "public_error_type"] = pub.loc[runtime_mask, ["reason", "summary"]].apply(
            lambda r: _runtime_subtype_from_reason(r.get("reason"), r.get("summary")),
            axis=1,
        )

    pub["public_error_family"] = pub["public_error_type"].map(
        {
            "All Cases Passed": "Success",
            "Wrong Answer": "Wrong Answer",
            "Timeout": "Timeout",
            "Not able to run": "Not able to run",
            "SyntaxError (structure evident)": "SyntaxError",
            "SyntaxError (no structure)": "SyntaxError",
        }
    )
    runtime_like = pub["public_error_type"].astype(str).str.contains("Error", na=False)
    pub["public_error_family"] = pub["public_error_family"].where(
        pub["public_error_family"].notna(),
        np.where(runtime_like, "Runtime Error", "Other"),
    )

    # Public process state classification.
    passes = pub["num_test_passed"].fillna(0)
    totals = pub["test_case_count"].fillna(0)
    is_parse = pub["is_parseable"].fillna(False)
    state = np.full(len(pub), "S2_parseable_zero", dtype=object)
    state[(totals > 0) & (passes >= totals)] = "S4_public_all"
    state[(passes > 0) & ~((totals > 0) & (passes >= totals))] = "S3_public_partial"
    state[(~is_parse) & pub["syntax_structure_evident"].fillna(False)] = "S1b_syntax_structure"
    state[(~is_parse) & ~pub["syntax_structure_evident"].fillna(False)] = "S1_syntax_fundamental"
    state[pub["no_code_beyond_skeleton_flag"].fillna(False)] = "S0_no_code"
    pub["process_state"] = state
    pub["process_state_order"] = pub["process_state"].map(STATE_ORDER).astype("Int64")
    pub["elapsed_fraction"] = np.where(
        pub["active_time_seconds"].fillna(0) > 0,
        (pub["seconds_since_start"].fillna(0) / pub["active_time_seconds"].replace(0, np.nan)).clip(0, 1),
        np.nan,
    )

    # Attach public_run_index back to main df.
    df = df.merge(
        pub[
            ATTEMPT_KEY_COLS
            + [
                "attempt_event_index",
                "public_run_index",
                "public_error_type",
                "public_error_family",
                "process_state",
                "process_state_order",
                "elapsed_fraction",
            ]
        ],
        on=ATTEMPT_KEY_COLS + ["attempt_event_index"],
        how="left",
    )

    # Write event-level outputs used as trajectory sources.
    pub_cols = [
        *ATTEMPT_KEY_COLS,
        "track",
        "term",
        "wave",
        "question_title",
        "outcome_category",
        "active_time_seconds",
        "seconds_since_start",
        "elapsed_fraction",
        "attempt_event_index",
        "public_run_index",
        "is_parseable",
        "summary",
        "num_test_passed",
        "test_case_count",
        "public_error_type",
        "public_error_family",
        "process_state",
        "process_state_order",
        "code_length",
        "ts_complexity_score",
        "ts_error_count",
        "ts_missing_token_count",
        "ts_error_total",
        "new_constructs_added",
        "meaningful_lines_beyond_skeleton",
        "no_code_beyond_skeleton_flag",
        "syntax_structure_evident",
        "large_deletion_event",
        "structural_regression_event",
    ]
    pub[pub_cols].to_parquet(OUT_DIR / "public_test_run_state_rows.parquet", index=False)
    df.to_parquet(OUT_DIR / "timeline_event_features_enriched.parquet", index=False)
    return df


def _sign_changes(deltas: np.ndarray) -> int:
    if deltas.size == 0:
        return 0
    signs = np.sign(deltas)
    signs = signs[signs != 0]
    if signs.size <= 1:
        return 0
    return int(np.sum(signs[1:] != signs[:-1]))


def _monotonic_non_decreasing(vals: np.ndarray) -> bool | None:
    if vals.size <= 1:
        return None
    return bool(np.all(np.diff(vals) >= 0))


def build_attempt_process_features(
    event_df: pd.DataFrame,
    attempt_base: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[5/11] Aggregating per-attempt timeline and structural evolution features...")
    keys = ATTEMPT_KEY_COLS
    event_df = event_df.sort_values(keys + ["seconds_since_start", "event_type_order", "evaluation_type"], kind="mergesort")

    rows: list[dict[str, Any]] = []
    construct_rows: list[dict[str, Any]] = []
    grouped = event_df.groupby(keys, sort=False, dropna=False)
    total_groups = len(grouped)

    for idx, (key, g) in enumerate(grouped, start=1):
        namespace, problem_id, student_id = key
        g = g.reset_index(drop=True)
        secs = g["seconds_since_start"].to_numpy(dtype=float, copy=False)
        secs_valid = secs[~np.isnan(secs)]
        active_time_obs = float(secs_valid.max() - secs_valid.min()) if secs_valid.size > 0 else np.nan

        parse_flags = g["is_parseable"].fillna(False).to_numpy(dtype=bool, copy=False)
        parseable_fraction = float(parse_flags.mean()) if parse_flags.size > 0 else np.nan

        first_parseable_s = np.nan
        if parse_flags.any():
            first_parseable_s = float(g.loc[parse_flags, "seconds_since_start"].iloc[0])

        meaningful_edit_flags = g["meaningful_edit_beyond_skeleton_flag"].fillna(False).to_numpy(dtype=bool, copy=False)
        meaningful_edit_events = int(meaningful_edit_flags.sum())
        first_meaningful_edit_s = np.nan
        if meaningful_edit_flags.any():
            first_meaningful_edit_s = float(g.loc[meaningful_edit_flags, "seconds_since_start"].iloc[0])

        deltas = g["delta_seconds"].to_numpy(dtype=float, copy=False)
        deltas_nonnull = deltas[~np.isnan(deltas)]
        idle_120 = deltas_nonnull[deltas_nonnull > 120]
        idle_300 = deltas_nonnull[deltas_nonnull > 300]
        idle_120_count = int(idle_120.size)
        idle_120_total_s = float(idle_120.sum()) if idle_120.size else 0.0
        idle_300_count = int(idle_300.size)
        idle_300_total_s = float(idle_300.sum()) if idle_300.size else 0.0
        last_idle_gap_s = float(deltas_nonnull[-1]) if deltas_nonnull.size else np.nan

        code_drop_count = int(g["large_deletion_event"].fillna(False).sum())
        code_rise_count = int(g["large_increase_event"].fillna(False).sum())
        structural_reg_events = int(g["structural_regression_event"].fillna(False).sum())
        ts_err_inc = int(g["ts_error_increase_event"].fillna(False).sum())
        ts_err_dec = int(g["ts_error_decrease_event"].fillna(False).sum())

        complexity = g["ts_complexity_score"].fillna(0).to_numpy(dtype=float, copy=False)
        complexity_deltas = np.diff(complexity) if complexity.size > 1 else np.array([], dtype=float)
        complexity_nondec = _monotonic_non_decreasing(complexity)
        complexity_sign_changes = _sign_changes(complexity_deltas)
        complexity_drop_events = int(np.sum(complexity_deltas < 0)) if complexity_deltas.size else 0
        complexity_rise_events = int(np.sum(complexity_deltas > 0)) if complexity_deltas.size else 0

        err_tot = g["ts_error_total"].fillna(0).to_numpy(dtype=float, copy=False)
        err_deltas = np.diff(err_tot) if err_tot.size > 1 else np.array([], dtype=float)
        err_sign_changes = _sign_changes(err_deltas)
        err_nonzero_frac = float(np.mean(err_tot > 0)) if err_tot.size > 0 else np.nan

        total_test_runs = int((g["event_type"] == "test_run").sum())
        public = g[(g["event_type"] == "test_run") & (g["evaluation_type"] == "public")].copy()
        private_test_runs = int(((g["event_type"] == "test_run") & (g["evaluation_type"] == "private")).sum())
        public_test_runs = len(public)

        pub_pass = public["num_test_passed"].fillna(0).to_numpy(dtype=float, copy=False)
        pub_total = public["test_case_count"].fillna(0).to_numpy(dtype=float, copy=False)
        pub_secs = public["seconds_since_start"].fillna(np.nan).to_numpy(dtype=float, copy=False)
        pub_complexity = public["ts_complexity_score"].fillna(0).to_numpy(dtype=float, copy=False)
        pub_err_tot = public["ts_error_total"].fillna(0).to_numpy(dtype=float, copy=False)

        peak_public_pass = int(np.max(pub_pass)) if pub_pass.size else 0
        final_public_pass = int(pub_pass[-1]) if pub_pass.size else 0
        peak_to_final_public_regression = int(max(0, peak_public_pass - final_public_pass)) if pub_pass.size else 0
        peak_public_case_count = int(np.max(pub_total)) if pub_total.size else 0
        any_public_all_pass = bool(np.any((pub_total > 0) & (pub_pass >= pub_total))) if pub_pass.size else False
        any_public_pass = bool(np.any(pub_pass > 0)) if pub_pass.size else False
        first_public_pass_s = np.nan
        if pub_pass.size and np.any(pub_pass > 0):
            first_public_pass_s = float(pub_secs[np.argmax(pub_pass > 0)])

        pub_deltas = np.diff(pub_pass) if pub_pass.size > 1 else np.array([], dtype=float)
        pub_pass_monotonic = _monotonic_non_decreasing(pub_pass)
        pub_pass_inc_events = int(np.sum(pub_deltas > 0)) if pub_deltas.size else 0
        pub_pass_dec_events = int(np.sum(pub_deltas < 0)) if pub_deltas.size else 0
        pub_pass_oscillation_events = _sign_changes(pub_deltas)

        pub_complexity_deltas = np.diff(pub_complexity) if pub_complexity.size > 1 else np.array([], dtype=float)
        pub_err_deltas = np.diff(pub_err_tot) if pub_err_tot.size > 1 else np.array([], dtype=float)
        median_abs_pub_complexity_delta = float(np.median(np.abs(pub_complexity_deltas))) if pub_complexity_deltas.size else np.nan
        mean_abs_pub_complexity_delta = float(np.mean(np.abs(pub_complexity_deltas))) if pub_complexity_deltas.size else np.nan
        pub_err_inc_events = int(np.sum(pub_err_deltas > 0)) if pub_err_deltas.size else 0
        pub_err_dec_events = int(np.sum(pub_err_deltas < 0)) if pub_err_deltas.size else 0

        test_all = g[g["event_type"] == "test_run"]
        all_pass = test_all["num_test_passed"].fillna(0).to_numpy(dtype=float, copy=False)
        peak_test_pass_any = int(np.max(all_pass)) if all_pass.size else 0
        final_test_pass_any = int(all_pass[-1]) if all_pass.size else 0
        peak_to_final_regression_any = int(max(0, peak_test_pass_any - final_test_pass_any)) if all_pass.size else 0
        run_monotonic_any = _monotonic_non_decreasing(all_pass)

        no_improve_latter_half = False
        total_active_proxy = float(g["active_time_seconds"].dropna().iloc[0]) if g["active_time_seconds"].notna().any() else np.nan
        if pub_pass.size and not np.isnan(total_active_proxy) and total_active_proxy > 0:
            half = total_active_proxy * 0.5
            first_half = pub_pass[pub_secs <= half]
            second_half = pub_pass[pub_secs > half]
            if second_half.size == 0:
                no_improve_latter_half = True
            else:
                first_half_peak = float(np.max(first_half)) if first_half.size else 0.0
                second_half_peak = float(np.max(second_half))
                no_improve_latter_half = second_half_peak <= first_half_peak

        # Compact trajectory descriptors.
        code_len_vals = g["code_length"].fillna(0).to_numpy(dtype=float, copy=False)
        if code_len_vals.size > 1:
            code_len_deltas = np.diff(code_len_vals)
            median_abs_code_delta = float(np.median(np.abs(code_len_deltas)))
            code_delta_sign_changes = _sign_changes(code_len_deltas)
        else:
            median_abs_code_delta = np.nan
            code_delta_sign_changes = 0

        # Construct first appearance timeline (all snapshots, tree-sitter tolerant).
        for construct in CONSTRUCT_TRACK_COLS:
            col = f"ts_has_{construct}"
            if col not in g.columns:
                continue
            mask = g[col].fillna(False).to_numpy(dtype=bool, copy=False)
            if not mask.any():
                continue
            first_idx = int(np.argmax(mask))  # 0-based
            first_row = g.iloc[first_idx]
            construct_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "student_id": student_id,
                    "construct": construct,
                    "first_attempt_event_index": int(first_row["attempt_event_index"]),
                    "first_seconds_since_start": (None if pd.isna(first_row["seconds_since_start"]) else float(first_row["seconds_since_start"])),
                    "first_event_type": first_row["event_type"],
                    "first_evaluation_type": first_row["evaluation_type"],
                    "track": first_row.get("track"),
                    "term": first_row.get("term"),
                    "wave": first_row.get("wave"),
                    "question_title": first_row.get("question_title"),
                }
            )

        row = {
            "namespace": namespace,
            "problem_id": int(problem_id),
            "student_id": student_id,
            "event_count": int(len(g)),
            "code_snapshot_count": int(g["code_length"].notna().sum()),
            "total_active_time_seconds_observed": active_time_obs,
            "total_active_time_seconds": total_active_proxy,
            "test_run_count": total_test_runs,
            "public_test_run_count": public_test_runs,
            "private_test_run_count": private_test_runs,
            "time_to_first_parseable_code_s": first_parseable_s,
            "time_to_first_public_test_pass_s": first_public_pass_s,
            "time_to_first_code_change_beyond_skeleton_s": first_meaningful_edit_s,
            "parseable_fraction": parseable_fraction,
            "meaningful_edit_event_count": meaningful_edit_events,
            "large_deletion_event_count": code_drop_count,
            "large_increase_event_count": code_rise_count,
            "idle_gap_gt120_count": idle_120_count,
            "idle_gap_gt120_total_s": idle_120_total_s,
            "idle_gap_gt300_count": idle_300_count,
            "idle_gap_gt300_total_s": idle_300_total_s,
            "last_idle_gap_s": last_idle_gap_s,
            "run_to_run_improvement_monotonic_any": run_monotonic_any,
            "run_to_run_improvement_monotonic_public": pub_pass_monotonic,
            "peak_test_pass_count_any": peak_test_pass_any,
            "final_test_pass_count_any": final_test_pass_any,
            "peak_to_final_regression_any": peak_to_final_regression_any,
            "peak_public_test_pass_count": peak_public_pass,
            "final_public_test_pass_count": final_public_pass,
            "peak_public_test_case_count": peak_public_case_count,
            "peak_to_final_public_regression": peak_to_final_public_regression,
            "any_public_pass": any_public_pass,
            "any_public_all_pass": any_public_all_pass,
            "public_pass_increase_events": pub_pass_inc_events,
            "public_pass_decrease_events": pub_pass_dec_events,
            "public_pass_oscillation_events": pub_pass_oscillation_events,
            "median_abs_public_complexity_delta": median_abs_pub_complexity_delta,
            "mean_abs_public_complexity_delta": mean_abs_pub_complexity_delta,
            "public_error_increase_events": pub_err_inc_events,
            "public_error_decrease_events": pub_err_dec_events,
            "median_abs_code_length_delta": median_abs_code_delta,
            "code_length_delta_sign_changes": code_delta_sign_changes,
            "structural_complexity_first": (float(complexity[0]) if complexity.size else np.nan),
            "structural_complexity_final": (float(complexity[-1]) if complexity.size else np.nan),
            "structural_complexity_max": (float(np.max(complexity)) if complexity.size else np.nan),
            "structural_complexity_rise_events": complexity_rise_events,
            "structural_complexity_drop_events": complexity_drop_events,
            "structural_complexity_sign_changes": complexity_sign_changes,
            "structural_complexity_monotonic_non_decreasing": complexity_nondec,
            "structural_regression_event_count": structural_reg_events,
            "error_nodes_first": (float(err_tot[0]) if err_tot.size else np.nan),
            "error_nodes_final": (float(err_tot[-1]) if err_tot.size else np.nan),
            "error_nodes_max": (float(np.max(err_tot)) if err_tot.size else np.nan),
            "error_nodes_nonzero_fraction": err_nonzero_frac,
            "error_nodes_sign_changes": err_sign_changes,
            "ts_error_increase_event_count": ts_err_inc,
            "ts_error_decrease_event_count": ts_err_dec,
            "no_improvement_latter_half_flag": bool(no_improve_latter_half),
        }
        rows.append(row)

        if idx % 10_000 == 0 or idx == total_groups:
            print(f"  processed {idx:,}/{total_groups:,} attempts...")

    attempt_feat = pd.DataFrame(rows)
    construct_first = pd.DataFrame(construct_rows)

    # Merge onto full attempt base to preserve rows with no timeline events.
    out = attempt_base.merge(attempt_feat, on=ATTEMPT_KEY_COLS, how="left")
    for c in [
        "event_count",
        "code_snapshot_count",
        "test_run_count",
        "public_test_run_count",
        "private_test_run_count",
        "large_deletion_event_count",
        "large_increase_event_count",
        "idle_gap_gt120_count",
        "idle_gap_gt300_count",
        "peak_test_pass_count_any",
        "final_test_pass_count_any",
        "peak_to_final_regression_any",
        "peak_public_test_pass_count",
        "final_public_test_pass_count",
        "peak_public_test_case_count",
        "peak_to_final_public_regression",
        "public_pass_increase_events",
        "public_pass_decrease_events",
        "public_pass_oscillation_events",
        "structural_complexity_rise_events",
        "structural_complexity_drop_events",
        "structural_complexity_sign_changes",
        "structural_regression_event_count",
        "error_nodes_sign_changes",
        "ts_error_increase_event_count",
        "ts_error_decrease_event_count",
        "meaningful_edit_event_count",
    ]:
        if c in out.columns:
            out[c] = out[c].fillna(0).astype(int)
    for c in [
        "any_public_pass",
        "any_public_all_pass",
        "no_improvement_latter_half_flag",
        "run_to_run_improvement_monotonic_any",
        "run_to_run_improvement_monotonic_public",
        "structural_complexity_monotonic_non_decreasing",
    ]:
        if c in out.columns:
            out[c] = out[c].astype("boolean")

    # Unified outcome metric for 5d.
    out["process_outcome_metric_name"] = np.where(
        out["track"] == TRACK_A_SUBMITTERS, "final_private_score", "best_public_tests_passed"
    )
    out["process_outcome_metric_value"] = np.where(
        out["track"] == TRACK_A_SUBMITTERS,
        out["latest_submission_score"],
        out["peak_public_test_pass_count"].astype(float),
    )
    out["process_outcome_success_flag"] = out["any_public_all_pass"].fillna(False)
    out.loc[out["outcome_category"].eq("Full pass"), "process_outcome_success_flag"] = True
    out["process_outcome_success_flag"] = out["process_outcome_success_flag"].astype(bool)

    out.to_csv(OUT_DIR / "attempt_process_features.csv", index=False)
    if not construct_first.empty:
        construct_first.sort_values(["namespace", "problem_id", "student_id", "construct"], inplace=True)
    construct_first.to_csv(OUT_DIR / "attempt_construct_first_appearance.csv", index=False)

    return out, construct_first


def classify_archetypes(attempts: pd.DataFrame) -> pd.DataFrame:
    print("[6/11] Classifying behavioural archetypes...")
    df = attempts.copy()

    active_time = to_num(df["total_active_time_seconds"].fillna(df["active_time_seconds"]))
    first_edit = to_num(df.get("time_to_first_code_change_beyond_skeleton_s", pd.Series(index=df.index, dtype=float)))
    first_edit_ratio = np.where(active_time > 0, first_edit / active_time, np.nan)
    df["late_starter_flag"] = (first_edit_ratio > 0.30) & active_time.notna() & (active_time >= 60)

    skel_status = df.get("skeleton_modification_status", pd.Series(index=df.index, dtype=object)).fillna("")
    df["skeleton_only_flag"] = skel_status.isin(["Unmodified skeleton", "Empty / trivial"])

    df["one_shot_flag"] = (
        (df["test_run_count"].fillna(0).astype(int) <= 3)
        & (df["large_increase_event_count"].fillna(0).astype(int) <= 2)
        & (df["meaningful_edit_event_count"].fillna(0).astype(int) <= 2)
    )

    parseable_frac = to_num(df["parseable_fraction"])
    pub_runs = df["public_test_run_count"].fillna(0).astype(int)
    pub_inc = df["public_pass_increase_events"].fillna(0).astype(int)
    pub_dec = df["public_pass_decrease_events"].fillna(0).astype(int)
    pub_osc = df["public_pass_oscillation_events"].fillna(0).astype(int)
    struct_reg = df["structural_regression_event_count"].fillna(0).astype(int)
    err_inc_pub = df["public_error_increase_events"].fillna(0).astype(int)
    err_dec_pub = df["public_error_decrease_events"].fillna(0).astype(int)
    med_pub_complex_delta = to_num(df["median_abs_public_complexity_delta"])
    peak_to_final_pub_reg = df["peak_to_final_public_regression"].fillna(0).astype(int)

    df["thrasher_flag"] = (
        (pub_runs > 15)
        & ((pub_osc >= 2) | (pub_dec >= 2))
        & (struct_reg >= 2)
    )

    df["incremental_debugger_flag"] = (
        (pub_runs >= 8)
        & (pub_inc >= 2)
        & (pub_dec <= 1)
        & (parseable_frac >= 0.80)
        & ((med_pub_complex_delta <= 2) | med_pub_complex_delta.isna())
        & (err_dec_pub >= err_inc_pub)
        & (peak_to_final_pub_reg <= 0)
        & (~df["thrasher_flag"])
    )

    run_mon_pub = df["run_to_run_improvement_monotonic_public"].fillna(False).astype(bool)
    df["steady_builder_flag"] = (
        (pub_runs >= 4)
        & (pub_inc >= 1)
        & (pub_dec == 0)
        & (parseable_frac >= 0.80)
        & (struct_reg <= 1)
        & (run_mon_pub | (pub_osc <= 1))
        & (~df["incremental_debugger_flag"])
        & (~df["thrasher_flag"])
    )

    last_idle = to_num(df["last_idle_gap_s"])
    no_improve_late = df["no_improvement_latter_half_flag"].fillna(False).astype(bool)
    df["stuck_and_abandoned_flag"] = (last_idle > 300) & no_improve_late

    reg_flags = (
        df.get("parseability_regression_flag", pd.Series(False, index=df.index)).fillna(False).astype(bool)
        | df.get("peak_to_last_public_regression_flag", pd.Series(False, index=df.index)).fillna(False).astype(bool)
        | df.get("structural_regression_vs_last_parseable_flag", pd.Series(False, index=df.index)).fillna(False).astype(bool)
        | (peak_to_final_pub_reg > 0)
    )
    df["regression_flag"] = reg_flags

    # Reuse the same trajectory signatures written later in 5b so the 5c archetype
    # split can resolve the dominant "Other" bucket with interpretable rule labels.
    complexity_pattern = pd.Series(
        np.select(
            [
                df["structural_complexity_monotonic_non_decreasing"].fillna(False).astype(bool)
                & (df["structural_complexity_rise_events"] > 0)
                & (df["structural_complexity_drop_events"] == 0),
                (df["structural_complexity_drop_events"] > 0) & (df["structural_complexity_rise_events"] > 0),
                (df["structural_complexity_drop_events"] > 0) & (df["structural_complexity_rise_events"] == 0),
                (df["structural_complexity_rise_events"] == 0) & (df["structural_complexity_drop_events"] == 0),
            ],
            [
                "Monotonic build-up",
                "Oscillating / restructuring",
                "Declining / deleting work",
                "Flat / minimal structural change",
            ],
            default="Mixed",
        ),
        index=df.index,
    )
    error_pattern = pd.Series(
        np.select(
            [
                (df["ts_error_decrease_event_count"] > df["ts_error_increase_event_count"])
                & (to_num(df["error_nodes_final"]) < to_num(df["error_nodes_first"])),
                (df["ts_error_increase_event_count"] > df["ts_error_decrease_event_count"])
                & (to_num(df["error_nodes_final"]) > to_num(df["error_nodes_first"])),
                (df["error_nodes_nonzero_fraction"].fillna(0) > 0.75) & (df["ts_error_decrease_event_count"] == 0),
                (df["ts_error_increase_event_count"] > 0) & (df["ts_error_decrease_event_count"] > 0),
            ],
            [
                "Decreasing errors",
                "Increasing errors",
                "Persistent errors",
                "Fluctuating errors",
            ],
            default="No/low errors",
        ),
        index=df.index,
    )

    df["minimal_change_solver_flag"] = (complexity_pattern == "Flat / minimal structural change") & (
        error_pattern == "No/low errors"
    )
    df["volatile_reworker_flag"] = (complexity_pattern == "Oscillating / restructuring") & error_pattern.isin(
        ["Fluctuating errors", "Decreasing errors", "No/low errors"]
    )
    df["builder_with_setbacks_flag"] = (complexity_pattern == "Monotonic build-up") & error_pattern.isin(
        ["No/low errors", "Decreasing errors", "Fluctuating errors"]
    )
    df["flat_stuck_flag"] = (complexity_pattern == "Flat / minimal structural change") & error_pattern.isin(
        ["Persistent errors", "Increasing errors"]
    )

    # Convenience/no-activity bucket (rare after Step 0 filtering, but keep explicit).
    df["no_activity_flag"] = df["event_count"].fillna(0).astype(int).eq(0)

    primary = np.full(len(df), "Other", dtype=object)
    order = [
        ("No activity", df["no_activity_flag"]),
        ("Skeleton-only", df["skeleton_only_flag"]),
        ("One-shot", df["one_shot_flag"]),
        ("Late starter", df["late_starter_flag"] & ~df["skeleton_only_flag"]),
        ("Thrasher", df["thrasher_flag"]),
        ("Stuck and abandoned", df["stuck_and_abandoned_flag"]),
        ("Incremental debugger", df["incremental_debugger_flag"]),
        ("Steady builder", df["steady_builder_flag"]),
        ("Regression", df["regression_flag"]),
        ("Minimal-change solver", df["minimal_change_solver_flag"]),
        ("Volatile reworker", df["volatile_reworker_flag"]),
        ("Builder with setbacks", df["builder_with_setbacks_flag"]),
        ("Flat stuck", df["flat_stuck_flag"]),
    ]
    assigned = np.zeros(len(df), dtype=bool)
    for label, mask in order:
        m = np.asarray(mask.fillna(False), dtype=bool) & (~assigned)
        primary[m] = label
        assigned |= m
    df["primary_archetype"] = primary

    flag_cols = [
        "no_activity_flag",
        "skeleton_only_flag",
        "one_shot_flag",
        "late_starter_flag",
        "thrasher_flag",
        "stuck_and_abandoned_flag",
        "incremental_debugger_flag",
        "steady_builder_flag",
        "regression_flag",
        "minimal_change_solver_flag",
        "volatile_reworker_flag",
        "builder_with_setbacks_flag",
        "flat_stuck_flag",
    ]
    for c in flag_cols:
        df[c] = df[c].fillna(False).astype(bool)

    df.to_csv(OUT_DIR / "attempt_archetypes.csv", index=False)
    return df


def build_archetype_outputs(df: pd.DataFrame) -> None:
    print("[7/11] Building archetype summaries...")
    total = len(df)
    active_time = to_num(df["total_active_time_seconds"].fillna(df["active_time_seconds"]))

    flag_rows: list[dict[str, Any]] = []
    archetype_flags = [
        ("Steady builder", "steady_builder_flag"),
        ("Builder with setbacks", "builder_with_setbacks_flag"),
        ("Minimal-change solver", "minimal_change_solver_flag"),
        ("Late starter", "late_starter_flag"),
        ("Thrasher", "thrasher_flag"),
        ("Volatile reworker", "volatile_reworker_flag"),
        ("One-shot", "one_shot_flag"),
        ("Stuck and abandoned", "stuck_and_abandoned_flag"),
        ("Flat stuck", "flat_stuck_flag"),
        ("Skeleton-only", "skeleton_only_flag"),
        ("Regression", "regression_flag"),
        ("Incremental debugger", "incremental_debugger_flag"),
    ]
    for label, col in archetype_flags:
        mask = df[col].fillna(False).astype(bool)
        g = df.loc[mask]
        flag_rows.append(
            {
                "archetype": label,
                "attempts": int(mask.sum()),
                "pct_all_attempts": round(100.0 * mask.sum() / total, 2) if total else np.nan,
                "median_process_outcome_metric": (float(np.nanmedian(to_num(g["process_outcome_metric_value"]))) if len(g) else np.nan),
                "median_active_time_seconds": (float(np.nanmedian(to_num(g["total_active_time_seconds"].fillna(g["active_time_seconds"])))) if len(g) else np.nan),
                "median_public_test_runs": (float(np.nanmedian(to_num(g["public_test_run_count"]))) if len(g) else np.nan),
                "success_rate_state4_or_state5": (round(100.0 * g["process_outcome_success_flag"].mean(), 2) if len(g) else np.nan),
                "track_a_submitter_pct": (round(100.0 * (g["track"] == TRACK_A_SUBMITTERS).mean(), 2) if len(g) else np.nan),
                "track_a_non_submit_pct": (round(100.0 * (g["track"] == TRACK_A_NON_SUBMIT).mean(), 2) if len(g) else np.nan),
                "track_b_pct": (round(100.0 * (g["track"] == TRACK_B).mean(), 2) if len(g) else np.nan),
            }
        )
    pd.DataFrame(flag_rows).sort_values("archetype").to_csv(OUT_DIR / "archetype_outcomes_flags_summary.csv", index=False)

    primary_summary = (
        df.groupby("primary_archetype", dropna=False)
        .agg(
            attempts=("student_id", "count"),
            pct_all_attempts=("student_id", lambda s: round(100.0 * len(s) / total, 2) if total else np.nan),
            median_process_outcome_metric=("process_outcome_metric_value", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            median_active_time_seconds=("total_active_time_seconds", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            median_public_test_runs=("public_test_run_count", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            success_rate_state4_or_state5=("process_outcome_success_flag", lambda s: round(100.0 * pd.Series(s).fillna(False).astype(bool).mean(), 2)),
        )
        .reset_index()
        .sort_values(["attempts", "primary_archetype"], ascending=[False, True])
    )
    primary_summary.to_csv(OUT_DIR / "archetype_outcomes_primary_summary.csv", index=False)

    # Question and term distributions (primary archetype).
    q = (
        df.groupby(["namespace", "problem_id", "question_title", "primary_archetype"], dropna=False)
        .agg(attempts=("student_id", "count"))
        .reset_index()
    )
    q["question_total_attempts"] = q.groupby(["namespace", "problem_id"])["attempts"].transform("sum")
    q["pct_question_attempts"] = np.where(q["question_total_attempts"] > 0, (100.0 * q["attempts"] / q["question_total_attempts"]).round(2), np.nan)
    q.sort_values(["namespace", "problem_id", "attempts"], ascending=[True, True, False], inplace=True)
    q.to_csv(OUT_DIR / "archetype_primary_by_question.csv", index=False)

    t = (
        df.groupby(["term", "track", "primary_archetype"], dropna=False)
        .agg(attempts=("student_id", "count"))
        .reset_index()
    )
    t["term_track_attempts"] = t.groupby(["term", "track"])["attempts"].transform("sum")
    t["pct_term_track_attempts"] = np.where(t["term_track_attempts"] > 0, (100.0 * t["attempts"] / t["term_track_attempts"]).round(2), np.nan)
    t.sort_values(["term", "track", "attempts"], ascending=[True, True, False], inplace=True)
    t.to_csv(OUT_DIR / "archetype_primary_by_term.csv", index=False)

    # Flag-by-term (useful for Step 5 caveat on progressive filtering).
    rows: list[dict[str, Any]] = []
    for label, col in archetype_flags:
        tmp = (
            df.groupby(["term", "track"], dropna=False)[col]
            .agg(["count", "sum"])
            .reset_index()
            .rename(columns={"count": "attempts", "sum": "flagged_attempts"})
        )
        tmp["archetype"] = label
        tmp["pct_flagged"] = np.where(tmp["attempts"] > 0, (100.0 * tmp["flagged_attempts"] / tmp["attempts"]).round(2), np.nan)
        rows.extend(tmp.to_dict("records"))
    pd.DataFrame(rows).sort_values(["term", "track", "archetype"]).to_csv(OUT_DIR / "archetype_flags_by_term.csv", index=False)


def build_recovery_analysis(public_runs: pd.DataFrame, attempts: pd.DataFrame) -> None:
    print("[8/11] Computing error recovery probabilities and times...")
    keep_cols = [
        *ATTEMPT_KEY_COLS,
        "track",
        "term",
        "wave",
        "public_run_index",
        "seconds_since_start",
        "public_error_type",
        "public_error_family",
    ]
    pr = public_runs[[c for c in keep_cols if c in public_runs.columns]].copy()
    pr.sort_values(ATTEMPT_KEY_COLS + ["public_run_index"], inplace=True)

    # Only consider rows with a classified public error type.
    pr = pr[pr["public_error_type"].notna()].copy()

    # Join track/term metadata if not already present (defensive).
    need_cols = ["track", "term", "wave", "outcome_category"]
    if any(c not in pr.columns for c in need_cols):
        pr = pr.merge(attempts[ATTEMPT_KEY_COLS + [c for c in need_cols if c in attempts.columns]], on=ATTEMPT_KEY_COLS, how="left")

    family_map = {
        "SyntaxError (structure evident)": "SyntaxError",
        "SyntaxError (no structure)": "SyntaxError",
        "Wrong Answer": "Wrong Answer",
        "Timeout": "Timeout",
        "Not able to run": "Not able to run",
        "All Cases Passed": "Success",
    }

    episode_rows: list[dict[str, Any]] = []
    attempt_persist_rows: list[dict[str, Any]] = []
    grouped = pr.groupby(ATTEMPT_KEY_COLS, sort=False, dropna=False)
    total = len(grouped)
    for idx, (_, g) in enumerate(grouped, start=1):
        g = g.sort_values("public_run_index")
        types = g["public_error_type"].astype(str).tolist()
        fams = [family_map.get(t, ("Runtime Error" if "Error" in t and not t.startswith("SyntaxError") else "Other")) for t in types]
        runs = to_num(g["public_run_index"]).fillna(0).astype(int).tolist()
        secs = to_num(g["seconds_since_start"]).fillna(np.nan).tolist()

        # Attempt-level persistence by error type: ever had type and family on final run.
        final_family = fams[-1] if fams else None
        seen_types = set(t for t in types if t != "All Cases Passed")
        for t in sorted(seen_types):
            tfam = family_map.get(t, ("Runtime Error" if "Error" in t and not t.startswith("SyntaxError") else "Other"))
            attempt_persist_rows.append(
                {
                    "namespace": g["namespace"].iloc[0],
                    "problem_id": int(g["problem_id"].iloc[0]),
                    "student_id": g["student_id"].iloc[0],
                    "track": g.get("track", pd.Series([None])).iloc[0],
                    "term": g.get("term", pd.Series([None])).iloc[0],
                    "error_type": t,
                    "error_family": tfam,
                    "ever_had_error_type": True,
                    "persists_to_final_public_run": bool(final_family == tfam),
                }
            )

        i = 0
        while i < len(types):
            t = types[i]
            fam = fams[i]
            if t == "All Cases Passed":
                i += 1
                continue
            start_i = i
            # contiguous same error type episode
            while (i + 1) < len(types) and types[i + 1] == t:
                i += 1
            end_i = i
            # resolution = first subsequent public run that exits the error family
            j = i + 1
            while j < len(types) and fams[j] == fam:
                j += 1
            resolved = j < len(types)
            run_delta = (runs[j] - runs[start_i]) if resolved else None
            time_delta = None
            if resolved and (secs[start_i] is not None) and (secs[j] is not None):
                a = secs[start_i]
                b = secs[j]
                if not (math.isnan(a) or math.isnan(b)):
                    time_delta = float(b - a)
            episode_rows.append(
                {
                    "namespace": g["namespace"].iloc[0],
                    "problem_id": int(g["problem_id"].iloc[0]),
                    "student_id": g["student_id"].iloc[0],
                    "track": g.get("track", pd.Series([None])).iloc[0],
                    "term": g.get("term", pd.Series([None])).iloc[0],
                    "wave": g.get("wave", pd.Series([None])).iloc[0],
                    "error_type": t,
                    "error_family": fam,
                    "episode_start_public_run_index": int(runs[start_i]),
                    "episode_end_public_run_index_same_type": int(runs[end_i]),
                    "episode_start_seconds_since_start": (None if secs[start_i] is None or math.isnan(secs[start_i]) else float(secs[start_i])),
                    "resolved_within_attempt": bool(resolved),
                    "resolution_public_run_index": (int(runs[j]) if resolved else None),
                    "resolution_run_delta": (int(run_delta) if run_delta is not None else None),
                    "resolution_time_seconds": time_delta,
                    "resolution_target_type": (types[j] if resolved else None),
                    "resolution_target_family": (fams[j] if resolved else None),
                }
            )
            i += 1

        if idx % 25_000 == 0 or idx == total:
            print(f"  processed recovery episodes for {idx:,}/{total:,} attempts with public runs...")

    episodes = pd.DataFrame(episode_rows)
    episodes.to_csv(OUT_DIR / "error_recovery_episodes_public.csv", index=False)

    pers = pd.DataFrame(attempt_persist_rows)
    pers.to_csv(OUT_DIR / "error_recovery_attempt_persistence_public.csv", index=False)

    if episodes.empty:
        pd.DataFrame(columns=["error_type"]).to_csv(OUT_DIR / "error_recovery_by_type.csv", index=False)
        return

    summary_rows: list[dict[str, Any]] = []
    for (err_type, fam), g in episodes.groupby(["error_type", "error_family"], dropna=False):
        n = len(g)
        resolved = g["resolved_within_attempt"].fillna(False).astype(bool)
        resolved_g = g[resolved]
        persist_mask = (pers["error_type"] == err_type) if not pers.empty else pd.Series([], dtype=bool)
        attempts_with_type = int(persist_mask.sum()) if not pers.empty else np.nan
        persists_count = int(pers.loc[persist_mask, "persists_to_final_public_run"].sum()) if not pers.empty else np.nan
        row = {
            "error_type": err_type,
            "error_family": fam,
            "episodes": n,
            "resolved_episodes": int(resolved.sum()),
            "pct_resolved_within_attempt": round(100.0 * resolved.mean(), 2) if n else np.nan,
            "median_resolution_time_seconds": (float(np.nanmedian(to_num(resolved_g["resolution_time_seconds"]))) if len(resolved_g) else np.nan),
            "attempts_with_error_type": attempts_with_type,
            "attempts_error_persists_to_final_public_run": persists_count,
            "pct_attempts_error_persists_to_final_public_run": (
                round(100.0 * persists_count / attempts_with_type, 2)
                if isinstance(attempts_with_type, (int, np.integer)) and attempts_with_type > 0
                else np.nan
            ),
        }
        for n_runs in [1, 2, 5, 10]:
            col = f"pct_resolved_within_{n_runs}_public_runs"
            ok = resolved & (to_num(g["resolution_run_delta"]).fillna(np.inf) <= n_runs)
            row[col] = round(100.0 * ok.mean(), 2) if n else np.nan
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows).sort_values(["error_family", "episodes", "error_type"], ascending=[True, False, True])
    summary.to_csv(OUT_DIR / "error_recovery_by_type.csv", index=False)

    # Explicit syntax structural-intent split table (same underlying episodes, easier to cite).
    syntax_split = summary[summary["error_type"].isin(["SyntaxError (structure evident)", "SyntaxError (no structure)"])].copy()
    syntax_split.to_csv(OUT_DIR / "error_recovery_syntax_intent_split.csv", index=False)


def build_death_spiral_analysis(public_runs: pd.DataFrame, attempts: pd.DataFrame) -> None:
    print("[9/11] Building death-spiral / state-transition analysis...")
    keep_cols = [
        *ATTEMPT_KEY_COLS,
        "track",
        "term",
        "wave",
        "public_run_index",
        "process_state",
        "elapsed_fraction",
    ]
    pr = public_runs[[c for c in keep_cols if c in public_runs.columns]].copy()
    pr.sort_values(ATTEMPT_KEY_COLS + ["public_run_index"], inplace=True)

    # Attempt-level success target: reached State 4 public all-pass OR (Track A submitter full pass => State 5).
    att = attempts[ATTEMPT_KEY_COLS + ["track", "term", "wave", "outcome_category", "process_outcome_success_flag"]].copy()
    att["state5_full_pass_flag"] = att["outcome_category"].eq("Full pass")
    att["eventual_success_state4_or_5"] = att["process_outcome_success_flag"].fillna(False).astype(bool)
    pr = pr.merge(att, on=ATTEMPT_KEY_COLS, how="left", suffixes=("", "_att"))

    # State occurrence outcomes (used for absorption and time-conditional views).
    occ = pr[pr["process_state"].notna()].copy()
    occ["state_label"] = occ["process_state"].map(STATE_LABELS).fillna(occ["process_state"])
    occ["elapsed_pct"] = (100.0 * to_num(occ["elapsed_fraction"])).clip(0, 100)
    occ["elapsed_pct_bin"] = pd.cut(
        occ["elapsed_pct"],
        bins=[-0.001, 25, 50, 75, 100.001],
        labels=["0-25%", "25-50%", "50-75%", "75-100%"],
    )
    occ.to_parquet(OUT_DIR / "death_spiral_state_occurrences_public.parquet", index=False)

    state_success = (
        occ.groupby(["process_state", "state_label", "track"], dropna=False)
        .agg(
            state_occurrences=("student_id", "count"),
            attempts=("student_id", pd.Series.nunique),
            eventual_success_occurrences=("eventual_success_state4_or_5", "sum"),
            pct_eventual_success_from_state=("eventual_success_state4_or_5", lambda s: round(100.0 * pd.Series(s).fillna(False).astype(bool).mean(), 2)),
        )
        .reset_index()
        .sort_values(["process_state", "track"])
    )
    state_success.to_csv(OUT_DIR / "death_spiral_state_eventual_success_by_state.csv", index=False)

    time_cond = (
        occ[occ["process_state"].isin(["S1_syntax_fundamental", "S1b_syntax_structure", "S2_parseable_zero", "S3_public_partial"])]
        .groupby(["process_state", "state_label", "elapsed_pct_bin", "track"], dropna=False)
        .agg(
            state_occurrences=("student_id", "count"),
            eventual_success_occurrences=("eventual_success_state4_or_5", "sum"),
            pct_eventual_success=("eventual_success_state4_or_5", lambda s: round(100.0 * pd.Series(s).fillna(False).astype(bool).mean(), 2)),
        )
        .reset_index()
        .sort_values(["process_state", "elapsed_pct_bin", "track"])
    )
    time_cond.to_csv(OUT_DIR / "death_spiral_time_conditional_absorption.csv", index=False)

    # Transition matrices are built with DuckDB SQL to avoid a pandas/native-code
    # path that intermittently segfaults on this large public-run table.
    build_death_spiral_transition_outputs_sql()

    # Critical transition difficulty summary (small tables only).
    trans_comb = pd.read_csv(OUT_DIR / "death_spiral_transition_matrix_combined.csv", low_memory=False)
    succ_map = state_success.groupby("process_state", dropna=False)["pct_eventual_success_from_state"].mean().to_dict()
    if trans_comb.empty:
        pd.DataFrame(columns=["from_state"]).to_csv(OUT_DIR / "death_spiral_transition_difficulty.csv", index=False)
        pd.DataFrame(columns=["from_state"]).to_csv(OUT_DIR / "death_spiral_absorbing_candidates.csv", index=False)
        return
    trans_comb["from_order"] = trans_comb["from_state"].map(STATE_ORDER)
    trans_comb["to_order"] = trans_comb["to_state"].map(STATE_ORDER)
    diff_rows: list[dict[str, Any]] = []
    for from_state, g in trans_comb.groupby("from_state", dropna=False):
        from_order = STATE_ORDER.get(str(from_state), np.nan)
        next_up = to_num(g.loc[g["to_order"] > from_order, "transitions"]).fillna(0).sum()
        self_loop = to_num(g.loc[g["to_state"] == from_state, "transitions"]).fillna(0).sum()
        total = to_num(g["transitions"]).fillna(0).sum()
        diff_rows.append(
            {
                "from_state": from_state,
                "from_state_label": STATE_LABELS.get(str(from_state), str(from_state)),
                "transitions": int(total),
                "pct_self_loop": (round(100.0 * self_loop / total, 2) if total else np.nan),
                "pct_next_transition_to_higher_state": (round(100.0 * next_up / total, 2) if total else np.nan),
                "pct_eventual_success_from_state_occurrence": succ_map.get(from_state),
            }
        )
    diff_df = pd.DataFrame(diff_rows).sort_values("from_state")
    diff_df.to_csv(OUT_DIR / "death_spiral_transition_difficulty.csv", index=False)
    diff_df[diff_df["pct_eventual_success_from_state_occurrence"].fillna(np.inf) < 5].to_csv(
        OUT_DIR / "death_spiral_absorbing_candidates.csv",
        index=False,
    )


def build_death_spiral_transition_outputs_sql() -> None:
    conn = make_conn()
    try:
        public_path = (OUT_DIR / "public_test_run_state_rows.parquet").as_posix().replace("'", "''")
        attempts_path = (OUT_DIR / "attempt_archetypes.csv").as_posix().replace("'", "''")
        out_matrix = (OUT_DIR / "death_spiral_transition_matrix.csv").as_posix().replace("'", "''")
        out_comb = (OUT_DIR / "death_spiral_transition_matrix_combined.csv").as_posix().replace("'", "''")

        conn.execute(
            f"""
            CREATE OR REPLACE TEMP VIEW step5_public_v AS
            SELECT
              namespace,
              CAST(problem_id AS INTEGER) AS problem_id,
              student_id,
              track,
              term,
              CAST(public_run_index AS INTEGER) AS public_run_index,
              process_state
            FROM read_parquet('{public_path}')
            WHERE process_state IS NOT NULL
            """
        )
        conn.execute(
            f"""
            CREATE OR REPLACE TEMP VIEW step5_attempts_v AS
            SELECT
              namespace,
              CAST(problem_id AS INTEGER) AS problem_id,
              student_id,
              track,
              term,
              outcome_category
            FROM read_csv_auto('{attempts_path}', header=true)
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TEMP VIEW step5_seq_transitions_v AS
            SELECT
              p.track,
              p.term,
              p.process_state AS from_state,
              LEAD(p.process_state) OVER (
                PARTITION BY p.namespace, p.problem_id, p.student_id
                ORDER BY p.public_run_index
              ) AS to_state
            FROM step5_public_v p
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TEMP VIEW step5_last_public_v AS
            SELECT * EXCLUDE(rn)
            FROM (
              SELECT
                p.*,
                ROW_NUMBER() OVER (
                  PARTITION BY p.namespace, p.problem_id, p.student_id
                  ORDER BY p.public_run_index DESC
                ) AS rn
              FROM step5_public_v p
            ) x
            WHERE rn = 1
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TEMP VIEW step5_synth_s5_transitions_v AS
            SELECT
              lp.track,
              lp.term,
              lp.process_state AS from_state,
              'S5_all_tests' AS to_state
            FROM step5_last_public_v lp
            JOIN step5_attempts_v a
              ON a.namespace = lp.namespace
             AND a.problem_id = lp.problem_id
             AND a.student_id = lp.student_id
            WHERE lp.track = 'Track A: submitters'
              AND a.outcome_category = 'Full pass'
              AND lp.process_state IS NOT NULL
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TEMP VIEW step5_all_transitions_v AS
            SELECT track, term, from_state, to_state
            FROM step5_seq_transitions_v
            WHERE to_state IS NOT NULL
            UNION ALL
            SELECT track, term, from_state, to_state
            FROM step5_synth_s5_transitions_v
            """
        )

        conn.execute(
            f"""
            COPY (
              WITH agg AS (
                SELECT from_state, to_state, track, term, COUNT(*) AS transitions
                FROM step5_all_transitions_v
                GROUP BY 1,2,3,4
              )
              SELECT
                from_state,
                to_state,
                track,
                term,
                transitions,
                SUM(transitions) OVER (PARTITION BY from_state, track, term) AS from_total_track_term,
                ROUND(100.0 * transitions / NULLIF(SUM(transitions) OVER (PARTITION BY from_state, track, term), 0), 2) AS pct_from_state_track_term
              FROM agg
              ORDER BY from_state, track, term, transitions DESC, to_state
            ) TO '{out_matrix}' (HEADER, DELIMITER ',')
            """
        )

        conn.execute(
            f"""
            COPY (
              WITH agg AS (
                SELECT from_state, to_state, COUNT(*) AS transitions
                FROM step5_all_transitions_v
                GROUP BY 1,2
              )
              SELECT
                from_state,
                to_state,
                transitions,
                SUM(transitions) OVER (PARTITION BY from_state) AS from_total,
                ROUND(100.0 * transitions / NULLIF(SUM(transitions) OVER (PARTITION BY from_state), 0), 2) AS pct_from_state
              FROM agg
              ORDER BY from_state, transitions DESC, to_state
            ) TO '{out_comb}' (HEADER, DELIMITER ',')
            """
        )
    finally:
        conn.close()


def build_process_summary_tables(attempts: pd.DataFrame, public_runs: pd.DataFrame) -> None:
    print("[10/11] Writing process/trajectory summary tables...")
    df = attempts.copy()
    active_s = to_num(df["total_active_time_seconds"].fillna(df["active_time_seconds"]))
    tr_count = to_num(df["test_run_count"]).fillna(0)
    pub_runs_ct = to_num(df["public_test_run_count"]).fillna(0)

    # 5a feature summaries (global + by track).
    global_summary = pd.DataFrame(
        [
            {
                "attempts": len(df),
                "median_active_time_seconds": float(np.nanmedian(active_s)),
                "p90_active_time_seconds": float(np.nanpercentile(active_s.dropna(), 90)) if active_s.notna().any() else np.nan,
                "median_test_run_count": float(np.nanmedian(tr_count)),
                "p90_test_run_count": float(np.nanpercentile(tr_count.dropna(), 90)) if tr_count.notna().any() else np.nan,
                "median_public_test_run_count": float(np.nanmedian(pub_runs_ct)),
                "pct_with_any_public_pass": round(100.0 * df["any_public_pass"].fillna(False).astype(bool).mean(), 2),
                "pct_with_any_public_all_pass": round(100.0 * df["any_public_all_pass"].fillna(False).astype(bool).mean(), 2),
                "pct_parseability_regression_flag": round(100.0 * df["parseability_regression_flag"].fillna(False).astype(bool).mean(), 2),
                "pct_peak_to_last_public_regression_flag": round(100.0 * df["peak_to_last_public_regression_flag"].fillna(False).astype(bool).mean(), 2),
            }
        ]
    )
    global_summary.to_csv(OUT_DIR / "process_feature_summary_global.csv", index=False)

    by_track = (
        df.groupby("track", dropna=False)
        .agg(
            attempts=("student_id", "count"),
            median_active_time_seconds=("total_active_time_seconds", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            median_test_run_count=("test_run_count", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            p90_test_run_count=("test_run_count", lambda s: float(np.nanpercentile(to_num(s).dropna(), 90)) if pd.Series(s).notna().any() else np.nan),
            median_time_to_first_parseable_s=("time_to_first_parseable_code_s", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
            median_time_to_first_public_pass_s=("time_to_first_public_test_pass_s", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
            median_parseable_fraction=("parseable_fraction", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
            pct_large_deletion_any=("large_deletion_event_count", lambda s: round(100.0 * (to_num(pd.Series(s)).fillna(0) > 0).mean(), 2)),
            pct_idle_gap_gt120_any=("idle_gap_gt120_count", lambda s: round(100.0 * (to_num(pd.Series(s)).fillna(0) > 0).mean(), 2)),
            pct_public_monotonic=("run_to_run_improvement_monotonic_public", lambda s: round(100.0 * pd.Series(s).fillna(False).astype(bool).mean(), 2)),
            pct_peak_to_final_public_regression=("peak_to_final_public_regression", lambda s: round(100.0 * (to_num(pd.Series(s)).fillna(0) > 0).mean(), 2)),
        )
        .reset_index()
        .sort_values("track")
    )
    by_track.to_csv(OUT_DIR / "process_feature_summary_by_track.csv", index=False)

    # Structural evolution patterns (5b) summary.
    tmp = df.copy()
    tmp["complexity_trajectory_pattern"] = np.select(
        [
            tmp["structural_complexity_monotonic_non_decreasing"].fillna(False).astype(bool) & (tmp["structural_complexity_rise_events"] > 0) & (tmp["structural_complexity_drop_events"] == 0),
            (tmp["structural_complexity_drop_events"] > 0) & (tmp["structural_complexity_rise_events"] > 0),
            (tmp["structural_complexity_drop_events"] > 0) & (tmp["structural_complexity_rise_events"] == 0),
            (tmp["structural_complexity_rise_events"] == 0) & (tmp["structural_complexity_drop_events"] == 0),
        ],
        [
            "Monotonic build-up",
            "Oscillating / restructuring",
            "Declining / deleting work",
            "Flat / minimal structural change",
        ],
        default="Mixed",
    )
    tmp["error_trajectory_pattern"] = np.select(
        [
            (tmp["ts_error_decrease_event_count"] > tmp["ts_error_increase_event_count"]) & (to_num(tmp["error_nodes_final"]) < to_num(tmp["error_nodes_first"])),
            (tmp["ts_error_increase_event_count"] > tmp["ts_error_decrease_event_count"]) & (to_num(tmp["error_nodes_final"]) > to_num(tmp["error_nodes_first"])),
            (tmp["error_nodes_nonzero_fraction"].fillna(0) > 0.75) & (tmp["ts_error_decrease_event_count"] == 0),
            (tmp["ts_error_increase_event_count"] > 0) & (tmp["ts_error_decrease_event_count"] > 0),
        ],
        [
            "Decreasing errors",
            "Increasing errors",
            "Persistent errors",
            "Fluctuating errors",
        ],
        default="No/low errors",
    )
    tmp.to_csv(OUT_DIR / "attempt_process_features_with_patterns.csv", index=False)

    patt = (
        tmp.groupby(["track", "complexity_trajectory_pattern", "error_trajectory_pattern"], dropna=False)
        .agg(attempts=("student_id", "count"))
        .reset_index()
    )
    patt["track_total"] = patt.groupby("track")["attempts"].transform("sum")
    patt["pct_track"] = np.where(patt["track_total"] > 0, (100.0 * patt["attempts"] / patt["track_total"]).round(2), np.nan)
    patt.sort_values(["track", "attempts"], ascending=[True, False], inplace=True)
    patt.to_csv(OUT_DIR / "structural_evolution_patterns_by_track.csv", index=False)

    # A compact public state distribution table.
    state_dist = (
        public_runs.groupby(["track", "process_state"], dropna=False)
        .agg(public_run_rows=("student_id", "count"))
        .reset_index()
    )
    state_dist["track_total_public_runs"] = state_dist.groupby("track")["public_run_rows"].transform("sum")
    state_dist["pct_track_public_runs"] = np.where(
        state_dist["track_total_public_runs"] > 0,
        (100.0 * state_dist["public_run_rows"] / state_dist["track_total_public_runs"]).round(2),
        np.nan,
    )
    state_dist["process_state_label"] = state_dist["process_state"].map(STATE_LABELS)
    state_dist.sort_values(["track", "process_state"], inplace=True)
    state_dist.to_csv(OUT_DIR / "public_state_distribution_by_track.csv", index=False)

    # Construct first-appearance summaries (5b construct timeline).
    cpath = OUT_DIR / "attempt_construct_first_appearance.csv"
    if cpath.exists():
        cdf = pd.read_csv(cpath, low_memory=False)
        if not cdf.empty:
            total_attempts = len(df)
            c_global = (
                cdf.groupby("construct", dropna=False)
                .agg(
                    attempts_with_construct=("student_id", "count"),
                    median_first_event_idx=("first_attempt_event_index", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
                    median_first_seconds=("first_seconds_since_start", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                )
                .reset_index()
            )
            c_global["pct_attempts"] = np.where(
                total_attempts > 0,
                (100.0 * c_global["attempts_with_construct"] / total_attempts).round(2),
                np.nan,
            )
            c_global.sort_values(["attempts_with_construct", "construct"], ascending=[False, True], inplace=True)
            c_global.to_csv(OUT_DIR / "construct_first_appearance_summary_global.csv", index=False)

            c_track = (
                cdf.groupby(["track", "construct"], dropna=False)
                .agg(
                    attempts_with_construct=("student_id", "count"),
                    median_first_event_idx=("first_attempt_event_index", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
                    median_first_seconds=("first_seconds_since_start", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                )
                .reset_index()
            )
            track_totals = df.groupby("track", dropna=False)["student_id"].count().reset_index(name="track_attempts")
            c_track = c_track.merge(track_totals, on="track", how="left")
            c_track["pct_track_attempts"] = np.where(
                c_track["track_attempts"] > 0,
                (100.0 * c_track["attempts_with_construct"] / c_track["track_attempts"]).round(2),
                np.nan,
            )
            c_track.sort_values(["track", "attempts_with_construct", "construct"], ascending=[True, False, True], inplace=True)
            c_track.to_csv(OUT_DIR / "construct_first_appearance_summary_by_track.csv", index=False)


def write_output_manifest() -> None:
    files: list[dict[str, Any]] = []
    for p in sorted(OUT_DIR.rglob("*")):
        if p.is_file():
            try:
                size = p.stat().st_size
            except Exception:
                size = None
            files.append({"path": str(p.relative_to(OUT_DIR)), "bytes": size})
    pd.DataFrame(files).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = make_conn()
    try:
        skel_df, skeleton_map = load_question_skeletons()
        skel_df.to_csv(OUT_DIR / "question_skeletons_step5_copy.csv", index=False)

        attempt_base = load_attempt_base()

        # Resume path: if the heavy earlier stages already succeeded and only later
        # summaries are missing (e.g., a native-library crash after recovery/death-spiral
        # partial outputs), reuse the saved row-level tables.
        resume_attempts_path = OUT_DIR / "attempt_archetypes.csv"
        resume_public_path = OUT_DIR / "public_test_run_state_rows.parquet"
        resume_recovery_done = (OUT_DIR / "error_recovery_by_type.csv").exists()
        death_done = (OUT_DIR / "death_spiral_transition_matrix.csv").exists()
        process_done = (OUT_DIR / "process_feature_summary_global.csv").exists()
        construct_summary_done = (OUT_DIR / "construct_first_appearance_summary_global.csv").exists()
        if resume_attempts_path.exists() and resume_public_path.exists() and resume_recovery_done and (
            not (death_done and process_done and construct_summary_done)
        ):
            print("[resume] Reusing existing attempt/public-run outputs to finish pending Step 5 summaries...")
            attempts = pd.read_csv(resume_attempts_path, low_memory=False)
            public_runs = pd.read_parquet(resume_public_path)
            build_death_spiral_analysis(public_runs, attempts)
            build_process_summary_tables(attempts, public_runs)
            print("[11/11] Writing output manifest...")
            write_output_manifest()
            print("Done. Outputs written to analysis/process_analysis/")
            return

        qhash_path = parse_qhash_structural_features(conn, attempt_base, skeleton_map)
        event_parquet = write_enriched_event_timeline_parquet(conn, attempt_base, qhash_path)

        print("[4/11] Loading enriched event parquet into pandas for trajectory aggregation...")
        event_df = pd.read_parquet(event_parquet)
        event_df = classify_event_level_states(event_df)

        # Public-run convenience table.
        public_keep_cols = [
            *ATTEMPT_KEY_COLS,
            "track",
            "term",
            "wave",
            "question_title",
            "outcome_category",
            "active_time_seconds",
            "seconds_since_start",
            "elapsed_fraction",
            "attempt_event_index",
            "public_run_index",
            "is_parseable",
            "summary",
            "num_test_passed",
            "test_case_count",
            "public_error_type",
            "public_error_family",
            "process_state",
            "process_state_order",
            "code_length",
            "ts_complexity_score",
            "ts_error_count",
            "ts_missing_token_count",
            "ts_error_total",
            "new_constructs_added",
            "meaningful_lines_beyond_skeleton",
            "no_code_beyond_skeleton_flag",
            "syntax_structure_evident",
            "large_deletion_event",
            "structural_regression_event",
        ]
        public_mask = (event_df["event_type"] == "test_run") & (event_df["evaluation_type"] == "public")
        public_runs = event_df.loc[public_mask, [c for c in public_keep_cols if c in event_df.columns]].copy()

        attempts, construct_first = build_attempt_process_features(event_df, attempt_base)
        del construct_first
        del event_df
        attempts = classify_archetypes(attempts)
        build_archetype_outputs(attempts)
        build_recovery_analysis(public_runs, attempts)
        build_death_spiral_analysis(public_runs, attempts)
        build_process_summary_tables(attempts, public_runs)

        # Additional cheap summaries useful for docs.
        qdf(
            conn,
            f"""
            SELECT
              COUNT(*) AS attempts,
              COUNT(*) FILTER (WHERE primary_archetype = 'Thrasher') AS thrashers,
              COUNT(*) FILTER (WHERE primary_archetype = 'Incremental debugger') AS incremental_debuggers,
              ROUND(100.0 * COUNT(*) FILTER (WHERE primary_archetype = 'Thrasher') / COUNT(*), 2) AS pct_thrashers_primary,
              ROUND(100.0 * COUNT(*) FILTER (WHERE primary_archetype = 'Incremental debugger') / COUNT(*), 2) AS pct_incremental_debuggers_primary
            FROM read_csv_auto('{(OUT_DIR / "attempt_archetypes.csv").as_posix()}', header=true)
            """
        ).to_csv(OUT_DIR / "archetype_primary_global_quick_stats.csv", index=False)

        print("[11/11] Writing output manifest...")
        write_output_manifest()
        print("Done. Outputs written to analysis/process_analysis/")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
