#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
#   "scipy>=1.12.0",
# ]
# ///
"""Classical item-quality analysis for OPPE test cases.

Outputs are written to ``analysis/classical_item_quality/``.

This script defines one analysis snapshot per submitter-question row:
- private test cases: final submission event (scored submission from ``final_scores.csv``)
- public test cases: latest public ``test_run`` at or before that final submission
"""

from __future__ import annotations

import math
import warnings
from pathlib import Path
from typing import Iterable

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import pointbiserialr


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "classical_item_quality"
GRAPHS_DIR = OUT_DIR / "dependency_graphs"
REDUCED_GRAPHS_DIR = OUT_DIR / "dependency_graphs_reduced"


def cpu_threads() -> int:
    """Return a pragmatic thread count for DuckDB."""
    try:
        import os

        n = os.cpu_count() or 4
    except Exception:
        n = 4
    return max(1, n - 1)


def make_conn() -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection tuned for batch analysis."""
    conn = duckdb.connect()
    conn.execute(f"PRAGMA threads={cpu_threads()}")
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def copy_query(conn: duckdb.DuckDBPyConnection, sql: str, out_csv: Path) -> None:
    """Export a SELECT query to CSV."""
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    escaped = out_csv.as_posix().replace("'", "''")
    conn.execute(f"COPY ({sql}) TO '{escaped}' (HEADER, DELIMITER ',')")


def qdf(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """Run query and return a DataFrame."""
    return conn.execute(sql).df()


def setup_base_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Create temp views/tables for final submitter item snapshots."""
    print("[1/7] Building selected public/private event snapshots...")
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_meta_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          question_title,
          CAST(num_public_tests AS INTEGER) AS num_public_tests,
          CAST(num_private_tests AS INTEGER) AS num_private_tests
        FROM read_csv_auto('analysis/question_metadata.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW final_scores_v AS
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          FileName AS final_submission_file,
          TRY_CAST("CompilationResult.score" AS DOUBLE) AS latest_submission_score,
          CAST(submission_events AS BIGINT) AS submission_events
        FROM read_csv_auto('analysis/final_scores.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW namespace_total_scores_v AS
        SELECT
          namespace,
          student_id,
          SUM(COALESCE(latest_submission_score, 0.0)) AS namespace_total_score
        FROM final_scores_v
        GROUP BY namespace, student_id;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW submitter_rows_v AS
        SELECT
          fs.namespace,
          fs.problem_id,
          fs.student_id,
          fs.final_submission_file,
          fs.latest_submission_score AS question_private_score,
          COALESCE(
            try_strptime(regexp_extract(fs.final_submission_file, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(regexp_extract(fs.final_submission_file, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
          ) AS final_submission_ts
        FROM final_scores_v fs
        WHERE fs.submission_events > 0;
        """
    )

    # Read only the columns needed for event selection and test-case extraction.
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW raw_eval_events_v AS
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          FileName AS file_name,
          regexp_extract(FileName, '/(saved_code|test_run|submission)/', 1) AS event_type,
          EvaluationType AS evaluation_type,
          COALESCE(
            try_strptime(regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
          ) AS event_ts,
          CompilationResult
        FROM read_json(
          'submissions/*.json',
          format='newline_delimited',
          columns={
            Namespace:'VARCHAR',
            ProblemID:'VARCHAR',
            StudentID:'VARCHAR',
            FileName:'VARCHAR',
            EvaluationType:'VARCHAR',
            CompilationResult:'VARCHAR'
          }
        )
        WHERE FileName IS NOT NULL
          AND FileName <> ''
          AND CompilationResult IS NOT NULL
          AND json_valid(CompilationResult)
          AND regexp_extract(FileName, '/(saved_code|test_run|submission)/', 1) IN ('test_run', 'submission');
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW timeline_eval_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          student_id,
          timestamp_utc,
          event_type,
          evaluation_type,
          code_sha256,
          code_length,
          score,
          num_test_passed,
          test_case_count,
          summary
        FROM read_parquet('analysis/submission_timeline.parquet')
        WHERE event_type IN ('test_run', 'submission');
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW final_submission_timeline_v AS
        SELECT *
        FROM (
          SELECT
            s.namespace,
            s.problem_id,
            s.student_id,
            s.final_submission_file,
            s.final_submission_ts,
            s.question_private_score,
            t.timestamp_utc AS final_submission_timeline_ts,
            t.code_sha256 AS final_submission_code_sha256,
            t.code_length AS final_submission_code_length,
            t.num_test_passed AS private_num_test_passed,
            t.test_case_count AS private_test_case_count,
            t.summary AS private_summary,
            ROW_NUMBER() OVER (
              PARTITION BY s.namespace, s.problem_id, s.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM submitter_rows_v s
          JOIN timeline_eval_v t
            ON t.namespace = s.namespace
           AND t.problem_id = s.problem_id
           AND t.student_id = s.student_id
          WHERE t.event_type = 'submission'
            AND t.evaluation_type = 'private'
            AND t.timestamp_utc = s.final_submission_ts
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW last_public_before_submission_v AS
        SELECT *
        FROM (
          SELECT
            s.namespace,
            s.problem_id,
            s.student_id,
            r.file_name AS public_file_name,
            r.event_ts AS public_event_ts,
            ROW_NUMBER() OVER (
              PARTITION BY s.namespace, s.problem_id, s.student_id
              ORDER BY r.event_ts DESC, r.file_name DESC
            ) AS rn
          FROM submitter_rows_v s
          JOIN raw_eval_events_v r
            ON r.namespace = s.namespace
           AND r.problem_id = s.problem_id
           AND r.student_id = s.student_id
          WHERE r.event_type = 'test_run'
            AND r.evaluation_type = 'public'
            AND r.event_ts <= s.final_submission_ts
        ) t
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW last_public_same_code_before_submission_v AS
        SELECT *
        FROM (
          SELECT
            f.namespace,
            f.problem_id,
            f.student_id,
            f.final_submission_file,
            f.final_submission_ts,
            f.final_submission_code_sha256,
            t.timestamp_utc AS public_same_code_ts,
            t.code_sha256 AS public_same_code_sha256,
            t.code_length AS public_same_code_code_length,
            t.num_test_passed AS public_num_test_passed,
            t.test_case_count AS public_test_case_count,
            t.summary AS public_summary,
            ROW_NUMBER() OVER (
              PARTITION BY f.namespace, f.problem_id, f.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM final_submission_timeline_v f
          JOIN timeline_eval_v t
            ON t.namespace = f.namespace
           AND t.problem_id = f.problem_id
           AND t.student_id = f.student_id
          WHERE t.event_type = 'test_run'
            AND t.evaluation_type = 'public'
            AND t.code_sha256 IS NOT NULL
            AND f.final_submission_code_sha256 IS NOT NULL
            AND t.code_sha256 = f.final_submission_code_sha256
            AND t.timestamp_utc <= f.final_submission_ts
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW selected_eval_events_v AS
        SELECT
          s.namespace,
          s.problem_id,
          s.student_id,
          'private' AS test_scope,
          s.final_submission_file AS selected_file_name,
          s.final_submission_ts AS selected_event_ts,
          s.question_private_score
        FROM submitter_rows_v s
        UNION ALL
        SELECT
          s.namespace,
          s.problem_id,
          s.student_id,
          'public' AS test_scope,
          p.public_file_name AS selected_file_name,
          p.public_event_ts AS selected_event_ts,
          s.question_private_score
        FROM submitter_rows_v s
        JOIN last_public_before_submission_v p
          USING (namespace, problem_id, student_id);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW item_responses_v AS
        SELECT DISTINCT
          se.namespace,
          se.problem_id,
          se.student_id,
          se.test_scope,
          se.selected_file_name,
          se.selected_event_ts,
          se.question_private_score,
          CAST(je.key AS INTEGER) + 1 AS test_case_index,
          CASE
            WHEN CAST(json_extract(je.value, '$.passed') AS BOOLEAN) THEN 1
            ELSE 0
          END AS passed,
          COALESCE(CAST(json_extract(je.value, '$.reason') AS VARCHAR), '') AS case_reason
        FROM selected_eval_events_v se
        JOIN raw_eval_events_v r
          ON r.namespace = se.namespace
         AND r.problem_id = se.problem_id
         AND r.student_id = se.student_id
         AND r.file_name = se.selected_file_name,
          json_each(json_extract(r.CompilationResult, '$.test_case_results')) AS je;
        """
    )

    coverage = qdf(
        conn,
        """
        SELECT
          COUNT(*) FILTER (WHERE submission_events > 0) AS submitter_rows,
          COUNT(*) FILTER (WHERE p.public_file_name IS NOT NULL) AS with_public_pre_submission,
          COUNT(*) FILTER (WHERE lpsc.public_same_code_ts IS NOT NULL) AS with_public_same_code_pre_submission
        FROM final_scores_v fs
        LEFT JOIN last_public_before_submission_v p
          ON p.namespace = fs.namespace AND p.problem_id = fs.problem_id AND p.student_id = fs.student_id
        LEFT JOIN last_public_same_code_before_submission_v lpsc
          ON lpsc.namespace = fs.namespace AND lpsc.problem_id = fs.problem_id AND lpsc.student_id = fs.student_id
        WHERE fs.submission_events > 0
        """,
    )
    if not coverage.empty:
        row = coverage.iloc[0]
        print(
            (
                "  submitter question rows={}, with public pre-submission={}, "
                "with public same-code pre-submission={}"
            ).format(
                int(row["submitter_rows"]),
                int(row["with_public_pre_submission"]),
                int(row["with_public_same_code_pre_submission"]),
            )
        )


def export_base_outputs(conn: duckdb.DuckDBPyConnection) -> None:
    """Export base item-response and snapshot tables."""
    print("[2/7] Exporting base item-response tables...")
    copy_query(
        conn,
        """
        SELECT
          s.namespace,
          s.problem_id,
          q.question_title,
          s.student_id,
          s.final_submission_file,
          s.final_submission_ts,
          p.public_file_name,
          p.public_event_ts,
          CASE WHEN p.public_file_name IS NOT NULL THEN TRUE ELSE FALSE END AS has_public_pre_submission
        FROM submitter_rows_v s
        LEFT JOIN last_public_before_submission_v p
          USING (namespace, problem_id, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY s.namespace, s.problem_id, s.student_id
        """,
        OUT_DIR / "submitter_question_snapshots.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          f.namespace,
          f.problem_id,
          q.question_title,
          f.student_id,
          f.final_submission_file,
          f.final_submission_ts,
          f.final_submission_code_sha256,
          lpsc.public_same_code_ts,
          lpsc.public_same_code_sha256,
          CASE WHEN lpsc.public_same_code_ts IS NOT NULL THEN TRUE ELSE FALSE END AS has_public_same_code_pre_submission,
          f.private_num_test_passed,
          f.private_test_case_count,
          CASE
            WHEN f.private_test_case_count > 0 AND f.private_num_test_passed = f.private_test_case_count THEN TRUE
            ELSE FALSE
          END AS private_all_pass,
          lpsc.public_num_test_passed,
          lpsc.public_test_case_count,
          CASE
            WHEN lpsc.public_test_case_count > 0 AND lpsc.public_num_test_passed = lpsc.public_test_case_count THEN TRUE
            ELSE FALSE
          END AS public_same_code_all_pass
        FROM final_submission_timeline_v f
        LEFT JOIN last_public_same_code_before_submission_v lpsc
          USING (namespace, problem_id, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY f.namespace, f.problem_id, f.student_id
        """,
        OUT_DIR / "submitter_question_same_code_snapshots.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          ir.namespace,
          ir.problem_id,
          q.question_title,
          ir.student_id,
          ir.test_scope,
          ir.test_case_index,
          ir.passed,
          ir.selected_file_name,
          ir.selected_event_ts,
          ir.question_private_score,
          nts.namespace_total_score,
          nts.namespace_total_score - COALESCE(ir.question_private_score, 0.0) AS namespace_total_score_excl_question
        FROM item_responses_v ir
        JOIN namespace_total_scores_v nts USING (namespace, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY ir.namespace, ir.problem_id, ir.student_id, ir.test_scope, ir.test_case_index
        """,
        OUT_DIR / "item_response_rows.csv",
    )

    copy_query(
        conn,
        """
        WITH scope_rollup AS (
          SELECT
            namespace,
            problem_id,
            student_id,
            test_scope,
            COUNT(*) AS num_cases,
            SUM(passed) AS num_passed,
            MIN(passed) AS all_pass
          FROM item_responses_v
          GROUP BY namespace, problem_id, student_id, test_scope
        )
        SELECT
          s.namespace,
          s.problem_id,
          q.question_title,
          s.student_id,
          MAX(num_cases) FILTER (WHERE test_scope = 'public') AS public_num_cases,
          MAX(num_passed) FILTER (WHERE test_scope = 'public') AS public_num_passed,
          MAX(all_pass) FILTER (WHERE test_scope = 'public') AS public_all_pass,
          MAX(num_cases) FILTER (WHERE test_scope = 'private') AS private_num_cases,
          MAX(num_passed) FILTER (WHERE test_scope = 'private') AS private_num_passed,
          MAX(all_pass) FILTER (WHERE test_scope = 'private') AS private_all_pass
        FROM (
          SELECT DISTINCT namespace, problem_id, student_id FROM item_responses_v
        ) s
        LEFT JOIN scope_rollup r USING (namespace, problem_id, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        GROUP BY s.namespace, s.problem_id, q.question_title, s.student_id
        ORDER BY s.namespace, s.problem_id, s.student_id
        """,
        OUT_DIR / "submitter_question_public_private_summary.csv",
    )


def _point_biserial_safe(binary: np.ndarray, score: np.ndarray) -> tuple[float, float]:
    """Safe point-biserial correlation wrapper with NaN fallbacks."""
    if binary.size < 3:
        return math.nan, math.nan
    if np.unique(binary).size < 2:
        return math.nan, math.nan
    if np.nanstd(score) == 0:
        return math.nan, math.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = pointbiserialr(binary, score)
    return float(res.statistic), float(res.pvalue)


def compute_item_difficulty_discrimination(conn: duckdb.DuckDBPyConnection) -> None:
    """Compute per-test-case difficulty and point-biserial discrimination."""
    print("[3/7] Computing item difficulty and discrimination...")
    df = qdf(
        conn,
        """
        SELECT
          ir.namespace,
          ir.problem_id,
          q.question_title,
          ir.test_scope,
          ir.test_case_index,
          ir.student_id,
          CAST(ir.passed AS INTEGER) AS passed,
          nts.namespace_total_score,
          nts.namespace_total_score - COALESCE(ir.question_private_score, 0.0) AS namespace_total_score_excl_question
        FROM item_responses_v ir
        JOIN namespace_total_scores_v nts USING (namespace, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY ir.namespace, ir.problem_id, ir.test_scope, ir.test_case_index, ir.student_id
        """
    )

    records: list[dict[str, object]] = []
    group_cols = ["namespace", "problem_id", "question_title", "test_scope", "test_case_index"]
    for key, g in df.groupby(group_cols, dropna=False, sort=False):
        namespace, problem_id, question_title, test_scope, test_case_index = key
        passed = g["passed"].to_numpy(dtype=float)
        total = g["namespace_total_score"].to_numpy(dtype=float)
        total_excl = g["namespace_total_score_excl_question"].to_numpy(dtype=float)
        r_pb, pvalue = _point_biserial_safe(passed, total)
        r_pb_excl, pvalue_excl = _point_biserial_safe(passed, total_excl)
        n = int(len(g))
        n_pass = int(g["passed"].sum())
        p_idx = (n_pass / n) if n else math.nan
        records.append(
            {
                "namespace": namespace,
                "problem_id": int(problem_id),
                "question_title": question_title,
                "test_scope": test_scope,
                "test_case_index": int(test_case_index),
                "item_id": f"{test_scope}_{int(test_case_index)}",
                "n_observed": n,
                "n_pass": n_pass,
                "difficulty_p": round(p_idx, 6) if p_idx == p_idx else math.nan,
                "difficulty_pct": round(100.0 * p_idx, 2) if p_idx == p_idx else math.nan,
                "point_biserial_r": r_pb,
                "point_biserial_pvalue": pvalue,
                "point_biserial_r_excl_question": r_pb_excl,
                "point_biserial_pvalue_excl_question": pvalue_excl,
                "flag_good_discrimination_r_gt_0_30": bool(r_pb == r_pb and r_pb > 0.30),
                "flag_low_discrimination_r_lt_0_15": bool(r_pb == r_pb and r_pb < 0.15),
            }
        )

    out = pd.DataFrame(records).sort_values(
        ["namespace", "problem_id", "test_scope", "test_case_index"]
    )
    out.to_csv(OUT_DIR / "item_difficulty_discrimination.csv", index=False)

    if out.empty:
        summary = pd.DataFrame(
            columns=[
                "test_scope",
                "items",
                "avg_difficulty_pct",
                "median_difficulty_pct",
                "avg_point_biserial_r",
                "median_point_biserial_r",
                "good_discrimination_items_r_gt_0_30",
                "low_discrimination_items_r_lt_0_15",
                "nan_discrimination_items",
            ]
        )
    else:
        summary = (
            out.groupby("test_scope", dropna=False)
            .agg(
                items=("item_id", "size"),
                avg_difficulty_pct=("difficulty_pct", "mean"),
                median_difficulty_pct=("difficulty_pct", "median"),
                avg_point_biserial_r=("point_biserial_r", "mean"),
                median_point_biserial_r=("point_biserial_r", "median"),
                good_discrimination_items_r_gt_0_30=("flag_good_discrimination_r_gt_0_30", "sum"),
                low_discrimination_items_r_lt_0_15=("flag_low_discrimination_r_lt_0_15", "sum"),
                nan_discrimination_items=("point_biserial_r", lambda s: int(pd.isna(s).sum())),
            )
            .reset_index()
        )
        for col in [
            "avg_difficulty_pct",
            "median_difficulty_pct",
            "avg_point_biserial_r",
            "median_point_biserial_r",
        ]:
            summary[col] = summary[col].round(4)
    summary.to_csv(OUT_DIR / "item_difficulty_discrimination_summary.csv", index=False)

    low_disc = out[
        out["point_biserial_r"].notna() & (out["point_biserial_r"] < 0.15)
    ].sort_values(["point_biserial_r", "n_observed"], ascending=[True, False])
    low_disc.to_csv(OUT_DIR / "item_low_discrimination_candidates.csv", index=False)

    print(f"  items analyzed={len(out)}")


def _phi_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson/phi correlation for binary vectors with NaN on degenerate inputs."""
    if x.size < 2 or y.size < 2:
        return math.nan
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        return math.nan
    return float(np.corrcoef(x, y)[0, 1])


def _ordered_pairs(cols: Iterable[str]) -> list[tuple[str, str]]:
    c = list(cols)
    return [(a, b) for a in c for b in c if a != b]


def _upper_pairs(cols: Iterable[str]) -> list[tuple[str, str]]:
    c = list(cols)
    return [(c[i], c[j]) for i in range(len(c)) for j in range(i + 1, len(c))]


def _parse_item_col(col: str) -> tuple[str, int]:
    scope, idx = col.split("_", 1)
    return scope, int(idx)


def _build_adj(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    """Build adjacency map with all nodes present."""
    node_list = list(nodes)
    adj = {n: set() for n in node_list}
    for u, v in edges:
        if u in adj and v in adj and u != v:
            adj[u].add(v)
    return adj


def _has_path(adj: dict[str, set[str]], src: str, dst: str) -> bool:
    """Return whether a path exists from src to dst in adjacency map."""
    if src == dst:
        return True
    stack = [src]
    seen = {src}
    while stack:
        u = stack.pop()
        for v in adj.get(u, ()):
            if v == dst:
                return True
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return False


def _toposort(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str]:
    """Topologically sort a DAG (returns partial arbitrary order if cycles exist)."""
    node_list = list(nodes)
    adj = _build_adj(node_list, edges)
    indeg = {n: 0 for n in node_list}
    for u in node_list:
        for v in adj[u]:
            indeg[v] += 1
    queue = [n for n in node_list if indeg[n] == 0]
    out: list[str] = []
    while queue:
        u = queue.pop(0)
        out.append(u)
        for v in sorted(adj[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    if len(out) < len(node_list):
        # Cycle fallback: append remaining nodes deterministically.
        remaining = [n for n in node_list if n not in set(out)]
        out.extend(sorted(remaining))
    return out


def _tarjan_scc(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[list[str]]:
    """Tarjan strongly connected components for a directed graph."""
    node_list = list(nodes)
    adj = _build_adj(node_list, edges)
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    idx: dict[str, int] = {}
    low: dict[str, int] = {}
    comps: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        idx[v] = index
        low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in sorted(adj[v]):
            if w not in idx:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], idx[w])

        if low[v] == idx[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            comps.append(sorted(comp))

    for v in sorted(node_list):
        if v not in idx:
            strongconnect(v)
    return comps


def _transitive_reduction_dag(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> set[tuple[str, str]]:
    """Return transitive reduction for a DAG (simple edge-removal algorithm)."""
    node_list = list(nodes)
    edge_set = set((u, v) for u, v in edges if u != v)
    adj = _build_adj(node_list, edge_set)
    reduced = set(edge_set)
    for u, v in sorted(edge_set):
        if v in adj[u]:
            adj[u].remove(v)
        if _has_path(adj, u, v):
            reduced.discard((u, v))
        adj[u].add(v)
    return reduced


def compute_redundancy_and_dependencies(conn: duckdb.DuckDBPyConnection) -> None:
    """Compute within-question redundancy correlations and dependency edges."""
    print("[4/7] Computing within-question redundancy and dependency structure...")
    item_df = qdf(
        conn,
        """
        SELECT
          namespace,
          problem_id,
          student_id,
          test_scope || '_' || CAST(test_case_index AS VARCHAR) AS item_col,
          CAST(passed AS INTEGER) AS passed
        FROM item_responses_v
        ORDER BY namespace, problem_id, student_id, item_col
        """
    )
    qmeta = qdf(conn, "SELECT namespace, problem_id, question_title FROM question_meta_v")
    qmeta_map = {
        (str(r.namespace), int(r.problem_id)): (r.question_title if isinstance(r.question_title, str) else "")
        for r in qmeta.itertuples(index=False)
    }

    redundancy_rows: list[dict[str, object]] = []
    dependency_rows: list[dict[str, object]] = []
    graph_summary_rows: list[dict[str, object]] = []
    scc_rows: list[dict[str, object]] = []
    reduced_edge_rows: list[dict[str, object]] = []
    minimal_info_rows: list[dict[str, object]] = []
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    REDUCED_GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    for (namespace, problem_id), g in item_df.groupby(["namespace", "problem_id"], sort=False):
        qkey = (str(namespace), int(problem_id))
        question_title = qmeta_map.get(qkey, "")
        mat = (
            g.pivot_table(index="student_id", columns="item_col", values="passed", aggfunc="max")
            .sort_index(axis=1)
            .fillna(0)
            .astype(int)
        )
        cols = list(mat.columns)
        if len(cols) < 2:
            graph_summary_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "question_title": question_title,
                    "num_items": len(cols),
                    "num_students": int(mat.shape[0]),
                    "redundant_pairs_gt_0_90": 0,
                    "dependency_edges_support5": 0,
                    "dependency_scc_components": len(cols),
                    "dependency_scc_nontrivial_components": 0,
                    "largest_dependency_scc_size": 1 if cols else 0,
                    "dependency_edges_transitive_reduced": 0,
                    "dependency_reduced_edge_density": 0.0 if cols else math.nan,
                    "minimal_new_information_components": len(cols),
                }
            )
            if cols:
                c = cols[0]
                scope, idx = _parse_item_col(c)
                scc_rows.append(
                    {
                        "namespace": namespace,
                        "problem_id": int(problem_id),
                        "question_title": question_title,
                        "component_id": "C1",
                        "component_size": 1,
                        "is_nontrivial_scc": False,
                        "representative_item": c,
                        "representative_scope": scope,
                        "representative_index": idx,
                        "members": c,
                        "members_count_public": 1 if scope == "public" else 0,
                        "members_count_private": 1 if scope == "private" else 0,
                        "incoming_components_full": 0,
                        "outgoing_components_full": 0,
                        "incoming_components_reduced": 0,
                        "outgoing_components_reduced": 0,
                        "is_source_component_reduced": True,
                        "is_sink_component_reduced": True,
                    }
                )
                minimal_info_rows.append(
                    {
                        "namespace": namespace,
                        "problem_id": int(problem_id),
                        "question_title": question_title,
                        "component_id": "C1",
                        "component_size": 1,
                        "representative_item": c,
                        "representative_scope": scope,
                        "representative_index": idx,
                        "members": c,
                        "reduced_in_degree": 0,
                        "reduced_out_degree": 0,
                        "is_sink_component_reduced": True,
                    }
                )
            continue

        arr_by_col = {c: mat[c].to_numpy(dtype=float) for c in cols}
        redundant_count = 0

        for a, b in _upper_pairs(cols):
            x = arr_by_col[a]
            y = arr_by_col[b]
            corr = _phi_corr(x, y)
            a_scope, a_idx = _parse_item_col(a)
            b_scope, b_idx = _parse_item_col(b)
            is_redundant = bool(corr == corr and corr > 0.90)
            redundant_count += int(is_redundant)
            redundancy_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "question_title": question_title,
                    "item_a": a,
                    "item_a_scope": a_scope,
                    "item_a_index": a_idx,
                    "item_b": b,
                    "item_b_scope": b_scope,
                    "item_b_index": b_idx,
                    "n_pair": int(len(x)),
                    "phi_correlation": corr,
                    "abs_phi_correlation": abs(corr) if corr == corr else math.nan,
                    "flag_near_redundant_gt_0_90": is_redundant,
                }
            )

        dependency_edges_support5: list[tuple[str, str, float, float, int, int]] = []
        for a, b in _ordered_pairs(cols):
            x = arr_by_col[a].astype(int)
            y = arr_by_col[b].astype(int)
            a_pass = x == 1
            a_fail = x == 0
            n_total = int(len(x))
            n_a_pass = int(a_pass.sum())
            n_a_fail = int(a_fail.sum())
            p_b_given_a_pass = float(y[a_pass].mean()) if n_a_pass > 0 else math.nan
            p_b_given_a_fail = float(y[a_fail].mean()) if n_a_fail > 0 else math.nan
            delta = (
                p_b_given_a_pass - p_b_given_a_fail
                if (p_b_given_a_pass == p_b_given_a_pass and p_b_given_a_fail == p_b_given_a_fail)
                else math.nan
            )
            flag_prereq = bool(p_b_given_a_fail == p_b_given_a_fail and p_b_given_a_fail < 0.05)
            flag_prereq_support5 = bool(flag_prereq and n_a_fail >= 5 and n_a_pass >= 5)
            if flag_prereq_support5:
                dependency_edges_support5.append((a, b, p_b_given_a_pass, p_b_given_a_fail, n_a_pass, n_a_fail))

            a_scope, a_idx = _parse_item_col(a)
            b_scope, b_idx = _parse_item_col(b)
            dependency_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "question_title": question_title,
                    "item_a": a,
                    "item_a_scope": a_scope,
                    "item_a_index": a_idx,
                    "item_b": b,
                    "item_b_scope": b_scope,
                    "item_b_index": b_idx,
                    "n_pair": n_total,
                    "n_a_pass": n_a_pass,
                    "n_a_fail": n_a_fail,
                    "p_pass_b_given_pass_a": p_b_given_a_pass,
                    "p_pass_b_given_fail_a": p_b_given_a_fail,
                    "dependency_gap": delta,
                    "flag_prerequisite_fail_threshold_lt_0_05": flag_prereq,
                    "flag_prerequisite_fail_threshold_lt_0_05_support5": flag_prereq_support5,
                }
            )

        graph_summary_rows.append(
            {
                "namespace": namespace,
                "problem_id": int(problem_id),
                "question_title": question_title,
                "num_items": len(cols),
                "num_students": int(mat.shape[0]),
                "redundant_pairs_gt_0_90": int(redundant_count),
                "dependency_edges_support5": int(len(dependency_edges_support5)),
                "dependency_scc_components": 0,  # filled after SCC computation
                "dependency_scc_nontrivial_components": 0,
                "largest_dependency_scc_size": 0,
                "dependency_edges_transitive_reduced": 0,
                "dependency_reduced_edge_density": math.nan,
                "minimal_new_information_components": 0,
            }
        )

        dot_lines = ["digraph G {", '  rankdir=LR;']
        for c in cols:
            scope, idx = _parse_item_col(c)
            dot_lines.append(f'  "{c}" [label="{scope[0].upper()}{idx}"];')
        for a, b, ppass, pfail, n_pass, n_fail in sorted(
            dependency_edges_support5,
            key=lambda t: (t[0], t[1]),
        ):
            label = f"P(B|A)= {ppass:.2f}\\nP(B|!A)= {pfail:.2f}\\nApass={n_pass}, Afail={n_fail}"
            dot_lines.append(f'  "{a}" -> "{b}" [label="{label}"];')
        dot_lines.append("}")
        graph_file = GRAPHS_DIR / f"{namespace}__q{int(problem_id)}.dot"
        graph_file.write_text("\n".join(dot_lines) + "\n", encoding="utf-8")

        # SCC condensation + transitive reduction (DAG-level).
        dep_edge_pairs = [(a, b) for a, b, *_ in dependency_edges_support5]
        edge_meta = {(a, b): (ppass, pfail, n_pass, n_fail) for a, b, ppass, pfail, n_pass, n_fail in dependency_edges_support5}
        sccs = _tarjan_scc(cols, dep_edge_pairs)
        # Stable component ids in topological order on condensation graph when possible.
        node_to_tmp_comp: dict[str, int] = {}
        for i, comp in enumerate(sccs):
            for item in comp:
                node_to_tmp_comp[item] = i
        comp_nodes_tmp = [f"T{i+1}" for i in range(len(sccs))]
        tmp_name_to_items = {f"T{i+1}": sccs[i] for i in range(len(sccs))}
        comp_edges_tmp: set[tuple[str, str]] = set()
        for a, b in dep_edge_pairs:
            ca = f"T{node_to_tmp_comp[a] + 1}"
            cb = f"T{node_to_tmp_comp[b] + 1}"
            if ca != cb:
                comp_edges_tmp.add((ca, cb))
        topo_tmp = _toposort(comp_nodes_tmp, comp_edges_tmp)
        comp_id_map = {tmp: f"C{idx+1}" for idx, tmp in enumerate(topo_tmp)}
        node_to_comp = {item: comp_id_map[f"T{node_to_tmp_comp[item] + 1}"] for item in cols}
        comp_members: dict[str, list[str]] = {}
        for item, cid in node_to_comp.items():
            comp_members.setdefault(cid, []).append(item)
        for cid in comp_members:
            comp_members[cid] = sorted(comp_members[cid])

        comp_nodes = sorted(comp_members.keys(), key=lambda c: int(c[1:]))
        comp_edges: set[tuple[str, str]] = set()
        edge_examples_by_comp: dict[tuple[str, str], tuple[str, str]] = {}
        for a, b in dep_edge_pairs:
            ca = node_to_comp[a]
            cb = node_to_comp[b]
            if ca == cb:
                continue
            comp_edges.add((ca, cb))
            edge_examples_by_comp.setdefault((ca, cb), (a, b))

        comp_edges_reduced = _transitive_reduction_dag(comp_nodes, comp_edges) if comp_edges else set()

        full_in = {c: 0 for c in comp_nodes}
        full_out = {c: 0 for c in comp_nodes}
        for u, v in comp_edges:
            full_out[u] += 1
            full_in[v] += 1
        red_in = {c: 0 for c in comp_nodes}
        red_out = {c: 0 for c in comp_nodes}
        for u, v in comp_edges_reduced:
            red_out[u] += 1
            red_in[v] += 1

        nontrivial_scc_count = 0
        largest_scc = 0
        sink_components = 0
        for cid in comp_nodes:
            members = comp_members[cid]
            largest_scc = max(largest_scc, len(members))
            is_nontrivial = len(members) > 1
            nontrivial_scc_count += int(is_nontrivial)
            rep = members[-1]  # choose hardest-ish lexical representative (private/public index sorted)
            rep_scope, rep_idx = _parse_item_col(rep)
            members_public = sum(1 for m in members if m.startswith("public_"))
            members_private = sum(1 for m in members if m.startswith("private_"))
            is_sink = red_out[cid] == 0
            sink_components += int(is_sink)
            scc_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "question_title": question_title,
                    "component_id": cid,
                    "component_size": len(members),
                    "is_nontrivial_scc": is_nontrivial,
                    "representative_item": rep,
                    "representative_scope": rep_scope,
                    "representative_index": rep_idx,
                    "members": "|".join(members),
                    "members_count_public": members_public,
                    "members_count_private": members_private,
                    "incoming_components_full": full_in[cid],
                    "outgoing_components_full": full_out[cid],
                    "incoming_components_reduced": red_in[cid],
                    "outgoing_components_reduced": red_out[cid],
                    "is_source_component_reduced": red_in[cid] == 0,
                    "is_sink_component_reduced": is_sink,
                }
            )
            if is_sink:
                minimal_info_rows.append(
                    {
                        "namespace": namespace,
                        "problem_id": int(problem_id),
                        "question_title": question_title,
                        "component_id": cid,
                        "component_size": len(members),
                        "representative_item": rep,
                        "representative_scope": rep_scope,
                        "representative_index": rep_idx,
                        "members": "|".join(members),
                        "reduced_in_degree": red_in[cid],
                        "reduced_out_degree": red_out[cid],
                        "is_sink_component_reduced": True,
                    }
                )

        for u, v in sorted(comp_edges_reduced, key=lambda t: (int(t[0][1:]), int(t[1][1:]))):
            ex_a, ex_b = edge_examples_by_comp.get((u, v), ("", ""))
            ppass = pfail = gap = math.nan
            if (ex_a, ex_b) in edge_meta:
                ppass, pfail, _, _ = edge_meta[(ex_a, ex_b)]
                gap = ppass - pfail
            reduced_edge_rows.append(
                {
                    "namespace": namespace,
                    "problem_id": int(problem_id),
                    "question_title": question_title,
                    "source_component_id": u,
                    "target_component_id": v,
                    "source_representative_item": next(r["representative_item"] for r in scc_rows[::-1] if r["namespace"] == namespace and r["problem_id"] == int(problem_id) and r["component_id"] == u),
                    "target_representative_item": next(r["representative_item"] for r in scc_rows[::-1] if r["namespace"] == namespace and r["problem_id"] == int(problem_id) and r["component_id"] == v),
                    "source_component_size": len(comp_members[u]),
                    "target_component_size": len(comp_members[v]),
                    "example_item_a": ex_a,
                    "example_item_b": ex_b,
                    "example_p_pass_b_given_pass_a": ppass,
                    "example_p_pass_b_given_fail_a": pfail,
                    "example_dependency_gap": gap,
                }
            )

        # Fill back summary fields for this question (last appended row).
        max_pairs = len(comp_nodes) * (len(comp_nodes) - 1)
        graph_summary_rows[-1]["dependency_scc_components"] = len(comp_nodes)
        graph_summary_rows[-1]["dependency_scc_nontrivial_components"] = nontrivial_scc_count
        graph_summary_rows[-1]["largest_dependency_scc_size"] = largest_scc
        graph_summary_rows[-1]["dependency_edges_transitive_reduced"] = len(comp_edges_reduced)
        graph_summary_rows[-1]["dependency_reduced_edge_density"] = (
            (len(comp_edges_reduced) / max_pairs) if max_pairs > 0 else 0.0
        )
        graph_summary_rows[-1]["minimal_new_information_components"] = sink_components

        # Reduced graph DOT (component-level).
        reduced_dot = ["digraph G {", "  rankdir=LR;"]
        for cid in comp_nodes:
            members = comp_members[cid]
            rep = [r for r in scc_rows if r["namespace"] == namespace and r["problem_id"] == int(problem_id) and r["component_id"] == cid][-1]["representative_item"]
            label = f"{cid}: {rep}"
            if len(members) > 1:
                label += f"\\nSCC size={len(members)}"
            reduced_dot.append(f'  "{cid}" [label="{label}"];')
        for u, v in sorted(comp_edges_reduced, key=lambda t: (int(t[0][1:]), int(t[1][1:]))):
            reduced_dot.append(f'  "{u}" -> "{v}";')
        reduced_dot.append("}")
        (REDUCED_GRAPHS_DIR / f"{namespace}__q{int(problem_id)}.dot").write_text(
            "\n".join(reduced_dot) + "\n",
            encoding="utf-8",
        )

    redundancy_df = pd.DataFrame(redundancy_rows)
    dependency_df = pd.DataFrame(dependency_rows)
    graph_summary_df = pd.DataFrame(graph_summary_rows)

    if redundancy_df.empty:
        redundancy_df = pd.DataFrame(
            columns=[
                "namespace",
                "problem_id",
                "question_title",
                "item_a",
                "item_a_scope",
                "item_a_index",
                "item_b",
                "item_b_scope",
                "item_b_index",
                "n_pair",
                "phi_correlation",
                "abs_phi_correlation",
                "flag_near_redundant_gt_0_90",
            ]
        )
    else:
        redundancy_df = redundancy_df.sort_values(
            ["namespace", "problem_id", "item_a", "item_b"]
        )
    redundancy_df.to_csv(OUT_DIR / "question_item_redundancy_pairs.csv", index=False)

    if dependency_df.empty:
        dependency_df = pd.DataFrame(
            columns=[
                "namespace",
                "problem_id",
                "question_title",
                "item_a",
                "item_b",
                "n_pair",
                "n_a_pass",
                "n_a_fail",
                "p_pass_b_given_pass_a",
                "p_pass_b_given_fail_a",
                "dependency_gap",
                "flag_prerequisite_fail_threshold_lt_0_05",
                "flag_prerequisite_fail_threshold_lt_0_05_support5",
            ]
        )
    else:
        dependency_df = dependency_df.sort_values(
            ["namespace", "problem_id", "item_a", "item_b"]
        )
    dependency_df.to_csv(OUT_DIR / "question_dependency_pairs.csv", index=False)

    dependency_edges = dependency_df[
        dependency_df["flag_prerequisite_fail_threshold_lt_0_05_support5"] == True
    ].copy()
    dependency_edges = dependency_edges.sort_values(
        ["namespace", "problem_id", "item_a", "item_b"]
    )
    dependency_edges.to_csv(OUT_DIR / "question_dependency_edges.csv", index=False)

    graph_summary_df = graph_summary_df.sort_values(["namespace", "problem_id"])
    graph_summary_df.to_csv(OUT_DIR / "question_dependency_graph_summary.csv", index=False)

    scc_df = pd.DataFrame(scc_rows)
    if scc_df.empty:
        scc_df = pd.DataFrame(
            columns=[
                "namespace",
                "problem_id",
                "question_title",
                "component_id",
                "component_size",
                "is_nontrivial_scc",
                "representative_item",
                "representative_scope",
                "representative_index",
                "members",
                "members_count_public",
                "members_count_private",
                "incoming_components_full",
                "outgoing_components_full",
                "incoming_components_reduced",
                "outgoing_components_reduced",
                "is_source_component_reduced",
                "is_sink_component_reduced",
            ]
        )
    else:
        scc_df = scc_df.sort_values(["namespace", "problem_id", "component_id"])
    scc_df.to_csv(OUT_DIR / "question_dependency_sccs.csv", index=False)

    reduced_edges_df = pd.DataFrame(reduced_edge_rows)
    if reduced_edges_df.empty:
        reduced_edges_df = pd.DataFrame(
            columns=[
                "namespace",
                "problem_id",
                "question_title",
                "source_component_id",
                "target_component_id",
                "source_representative_item",
                "target_representative_item",
                "source_component_size",
                "target_component_size",
                "example_item_a",
                "example_item_b",
                "example_p_pass_b_given_pass_a",
                "example_p_pass_b_given_fail_a",
                "example_dependency_gap",
            ]
        )
    else:
        reduced_edges_df = reduced_edges_df.sort_values(
            ["namespace", "problem_id", "source_component_id", "target_component_id"]
        )
    reduced_edges_df.to_csv(OUT_DIR / "question_dependency_edges_transitive_reduced.csv", index=False)

    minimal_info_df = pd.DataFrame(minimal_info_rows)
    if minimal_info_df.empty:
        minimal_info_df = pd.DataFrame(
            columns=[
                "namespace",
                "problem_id",
                "question_title",
                "component_id",
                "component_size",
                "representative_item",
                "representative_scope",
                "representative_index",
                "members",
                "reduced_in_degree",
                "reduced_out_degree",
                "is_sink_component_reduced",
            ]
        )
    else:
        minimal_info_df = minimal_info_df.sort_values(["namespace", "problem_id", "component_id"])
    minimal_info_df.to_csv(OUT_DIR / "question_dependency_minimal_new_information.csv", index=False)

    redundancy_summary = (
        redundancy_df.groupby("namespace", dropna=False)
        .agg(
            questions=("problem_id", "nunique"),
            pairwise_item_pairs=("item_a", "size"),
            redundant_pairs_gt_0_90=("flag_near_redundant_gt_0_90", "sum"),
        )
        .reset_index()
        if not redundancy_df.empty
        else pd.DataFrame(columns=["namespace", "questions", "pairwise_item_pairs", "redundant_pairs_gt_0_90"])
    )
    if not redundancy_summary.empty:
        redundancy_summary["redundant_pair_rate_pct"] = (
            100.0 * redundancy_summary["redundant_pairs_gt_0_90"] / redundancy_summary["pairwise_item_pairs"]
        ).round(2)
    redundancy_summary.to_csv(OUT_DIR / "question_item_redundancy_summary_by_namespace.csv", index=False)

    print(
        (
            "  redundancy pairs={}, dependency edges (support5)={}, "
            "reduced edges={}, minimal-new-info components={}"
        ).format(
            len(redundancy_df),
            len(dependency_edges),
            len(reduced_edges_df),
            len(minimal_info_df),
        )
    )


def _cronbach_alpha(frame: pd.DataFrame) -> float:
    """Cronbach's alpha using sample variances (ddof=1)."""
    if frame.shape[0] < 2 or frame.shape[1] < 2:
        return math.nan
    item_vars = frame.var(axis=0, ddof=1)
    total = frame.sum(axis=1)
    total_var = float(total.var(ddof=1))
    if total_var <= 0 or np.isnan(total_var):
        return math.nan
    k = frame.shape[1]
    return float((k / (k - 1)) * (1.0 - (float(item_vars.sum()) / total_var)))


def compute_namespace_reliability(conn: duckdb.DuckDBPyConnection) -> None:
    """Compute Cronbach's alpha per namespace across binary test-case items."""
    print("[5/7] Computing exam-level reliability (Cronbach's alpha)...")
    item_df = qdf(
        conn,
        """
        SELECT
          namespace,
          student_id,
          test_scope || '_' || CAST(problem_id AS VARCHAR) || '_' || CAST(test_case_index AS VARCHAR) AS item_col,
          test_scope,
          CAST(passed AS INTEGER) AS passed
        FROM item_responses_v
        ORDER BY namespace, student_id, item_col
        """
    )
    submitter_q = qdf(
        conn,
        """
        SELECT DISTINCT namespace, student_id
        FROM submitter_rows_v
        ORDER BY namespace, student_id
        """
    )
    ns_students = {
        ns: sorted(sub["student_id"].astype(str).tolist())
        for ns, sub in submitter_q.groupby("namespace", sort=False)
    }
    rows: list[dict[str, object]] = []
    for namespace, sub in item_df.groupby("namespace", sort=False):
        students = ns_students.get(str(namespace), [])
        if not students:
            continue
        mat = (
            sub.pivot_table(index="student_id", columns="item_col", values="passed", aggfunc="max")
            .reindex(students)
            .fillna(0)
            .astype(int)
        )
        all_cols = list(mat.columns)
        public_cols = [c for c in all_cols if str(c).startswith("public_")]
        private_cols = [c for c in all_cols if str(c).startswith("private_")]
        alpha_all = _cronbach_alpha(mat[all_cols]) if all_cols else math.nan
        alpha_public = _cronbach_alpha(mat[public_cols]) if len(public_cols) >= 2 else math.nan
        alpha_private = _cronbach_alpha(mat[private_cols]) if len(private_cols) >= 2 else math.nan
        rows.append(
            {
                "namespace": namespace,
                "n_students_with_any_submission": int(mat.shape[0]),
                "k_items_all_public_private": int(len(all_cols)),
                "k_items_public": int(len(public_cols)),
                "k_items_private": int(len(private_cols)),
                "cronbach_alpha_all_public_private_fill0": alpha_all,
                "cronbach_alpha_public_fill0": alpha_public,
                "cronbach_alpha_private_fill0": alpha_private,
                "mean_total_item_score_all": float(mat.sum(axis=1).mean()) if all_cols else math.nan,
                "sd_total_item_score_all": float(mat.sum(axis=1).std(ddof=1)) if mat.shape[0] > 1 and all_cols else math.nan,
            }
        )

    out = pd.DataFrame(rows).sort_values("namespace")

    # Add zero-submission namespaces (no reliability estimate).
    all_namespaces = qdf(conn, "SELECT DISTINCT namespace FROM final_scores_v ORDER BY namespace")
    present = set(out["namespace"].astype(str)) if not out.empty else set()
    missing_rows = []
    for ns in all_namespaces["namespace"].astype(str).tolist():
        if ns in present:
            continue
        missing_rows.append(
            {
                "namespace": ns,
                "n_students_with_any_submission": 0,
                "k_items_all_public_private": 0,
                "k_items_public": 0,
                "k_items_private": 0,
                "cronbach_alpha_all_public_private_fill0": math.nan,
                "cronbach_alpha_public_fill0": math.nan,
                "cronbach_alpha_private_fill0": math.nan,
                "mean_total_item_score_all": math.nan,
                "sd_total_item_score_all": math.nan,
            }
        )
    if missing_rows:
        out = pd.concat([out, pd.DataFrame(missing_rows)], ignore_index=True).sort_values("namespace")

    out.to_csv(OUT_DIR / "namespace_reliability_cronbach_alpha.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "namespaces_total": int(len(out)),
                "namespaces_with_alpha_all": int(out["cronbach_alpha_all_public_private_fill0"].notna().sum()),
                "alpha_all_median": round(
                    float(out["cronbach_alpha_all_public_private_fill0"].dropna().median()), 4
                )
                if out["cronbach_alpha_all_public_private_fill0"].notna().any()
                else math.nan,
                "alpha_all_min": round(
                    float(out["cronbach_alpha_all_public_private_fill0"].dropna().min()), 4
                )
                if out["cronbach_alpha_all_public_private_fill0"].notna().any()
                else math.nan,
                "alpha_all_max": round(
                    float(out["cronbach_alpha_all_public_private_fill0"].dropna().max()), 4
                )
                if out["cronbach_alpha_all_public_private_fill0"].notna().any()
                else math.nan,
            }
        ]
    )
    summary.to_csv(OUT_DIR / "namespace_reliability_summary.csv", index=False)


def compute_public_private_gap(conn: duckdb.DuckDBPyConnection) -> None:
    """Compute public-vs-private all-pass mismatch metrics (overfit proxy)."""
    print("[6/7] Computing public vs private gap (overfit proxy) analysis...")
    def gap_aggregates(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        work = df.copy()
        work["has_both_scopes"] = work["public_all_pass"].notna() & work["private_all_pass"].notna()
        for col in ["public_all_pass", "private_all_pass"]:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        with_both = work[work["has_both_scopes"]].copy()
        if with_both.empty:
            return pd.DataFrame(), pd.DataFrame()

        with_both["public_all_private_not_all"] = (
            (with_both["public_all_pass"] == 1) & (with_both["private_all_pass"] != 1)
        )
        with_both["private_all_public_not_all"] = (
            (with_both["private_all_pass"] == 1) & (with_both["public_all_pass"] != 1)
        )
        with_both["both_all_pass"] = (
            (with_both["public_all_pass"] == 1) & (with_both["private_all_pass"] == 1)
        )
        with_both["neither_all_pass"] = (
            (with_both["public_all_pass"] != 1) & (with_both["private_all_pass"] != 1)
        )

        by_q = (
            with_both.groupby(["namespace", "problem_id", "question_title"], dropna=False)
            .agg(
                submitters_with_both_scopes=("student_id", "size"),
                n_public_all_private_not_all=("public_all_private_not_all", "sum"),
                n_private_all_public_not_all=("private_all_public_not_all", "sum"),
                n_both_all_pass=("both_all_pass", "sum"),
                n_neither_all_pass=("neither_all_pass", "sum"),
            )
            .reset_index()
        )
        by_q["frac_public_all_private_not_all"] = (
            by_q["n_public_all_private_not_all"] / by_q["submitters_with_both_scopes"]
        ).round(6)
        by_q["frac_private_all_public_not_all"] = (
            by_q["n_private_all_public_not_all"] / by_q["submitters_with_both_scopes"]
        ).round(6)
        by_q["frac_public_all_private_not_all_pct"] = (100.0 * by_q["frac_public_all_private_not_all"]).round(2)
        by_q["frac_private_all_public_not_all_pct"] = (100.0 * by_q["frac_private_all_public_not_all"]).round(2)
        by_q = by_q.sort_values(
            ["frac_public_all_private_not_all", "submitters_with_both_scopes"],
            ascending=[False, False],
        )

        overall = pd.DataFrame(
            [
                {
                    "submitter_question_rows_with_both_scopes": int(len(with_both)),
                    "overall_public_all_private_not_all": int(with_both["public_all_private_not_all"].sum()),
                    "overall_private_all_public_not_all": int(with_both["private_all_public_not_all"].sum()),
                    "overall_frac_public_all_private_not_all": round(float(with_both["public_all_private_not_all"].mean()), 6),
                    "overall_frac_private_all_public_not_all": round(float(with_both["private_all_public_not_all"].mean()), 6),
                    "overall_frac_public_all_private_not_all_pct": round(100.0 * float(with_both["public_all_private_not_all"].mean()), 2),
                    "overall_frac_private_all_public_not_all_pct": round(100.0 * float(with_both["private_all_public_not_all"].mean()), 2),
                }
            ]
        )
        return by_q, overall

    # Baseline proxy: last public test_run before final submission vs final private submission.
    df_baseline = pd.read_csv(OUT_DIR / "submitter_question_public_private_summary.csv")
    by_q, overall = gap_aggregates(df_baseline)
    by_q.to_csv(OUT_DIR / "public_private_gap_by_question.csv", index=False)
    overall.to_csv(OUT_DIR / "public_private_gap_summary.csv", index=False)

    # Cleaner proxy: same-code public test_run (same code_sha256 as final submitted code) vs final private submission.
    same_code_df = qdf(
        conn,
        """
        SELECT
          f.namespace,
          f.problem_id,
          q.question_title,
          f.student_id,
          f.final_submission_code_sha256 AS code_sha256,
          CASE
            WHEN f.private_test_case_count > 0 AND f.private_num_test_passed = f.private_test_case_count THEN 1
            ELSE 0
          END AS private_all_pass,
          CASE
            WHEN lpsc.public_same_code_ts IS NULL THEN NULL
            WHEN lpsc.public_test_case_count > 0 AND lpsc.public_num_test_passed = lpsc.public_test_case_count THEN 1
            ELSE 0
          END AS public_all_pass,
          f.private_num_test_passed,
          f.private_test_case_count,
          lpsc.public_num_test_passed,
          lpsc.public_test_case_count,
          f.final_submission_ts,
          lpsc.public_same_code_ts,
          CASE WHEN lpsc.public_same_code_ts IS NOT NULL THEN TRUE ELSE FALSE END AS has_public_same_code_pair
        FROM final_submission_timeline_v f
        LEFT JOIN last_public_same_code_before_submission_v lpsc
          USING (namespace, problem_id, student_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY f.namespace, f.problem_id, f.student_id
        """
    )
    same_code_df.to_csv(OUT_DIR / "submitter_question_same_code_public_private_summary.csv", index=False)

    same_code_by_q, same_code_overall = gap_aggregates(same_code_df)
    same_code_by_q.to_csv(OUT_DIR / "public_private_gap_same_code_by_question.csv", index=False)
    same_code_overall.to_csv(OUT_DIR / "public_private_gap_same_code_summary.csv", index=False)

    coverage = pd.DataFrame(
        [
            {
                "submitter_question_rows_final_private": int(len(same_code_df)),
                "rows_with_same_code_public_pair": int(same_code_df["has_public_same_code_pair"].astype(bool).sum()) if not same_code_df.empty else 0,
            }
        ]
    )
    if not coverage.empty and coverage.loc[0, "submitter_question_rows_final_private"] > 0:
        coverage["same_code_pair_coverage_pct"] = round(
            100.0 * coverage["rows_with_same_code_public_pair"] / coverage["submitter_question_rows_final_private"],
            2,
        )
    else:
        coverage["same_code_pair_coverage_pct"] = np.nan
    coverage.to_csv(OUT_DIR / "public_private_gap_same_code_coverage.csv", index=False)


def compute_summary_rollups() -> None:
    """Derive small helper summaries from generated CSVs."""
    print("[7/7] Writing helper summaries...")
    items = pd.read_csv(OUT_DIR / "item_difficulty_discrimination.csv")
    redundancy = pd.read_csv(OUT_DIR / "question_item_redundancy_pairs.csv")
    deps = pd.read_csv(OUT_DIR / "question_dependency_edges.csv")
    deps_reduced = pd.read_csv(OUT_DIR / "question_dependency_edges_transitive_reduced.csv")
    dep_scc = pd.read_csv(OUT_DIR / "question_dependency_sccs.csv")
    dep_min = pd.read_csv(OUT_DIR / "question_dependency_minimal_new_information.csv")
    rel = pd.read_csv(OUT_DIR / "namespace_reliability_cronbach_alpha.csv")
    gap = pd.read_csv(OUT_DIR / "public_private_gap_by_question.csv")
    gap_same = pd.read_csv(OUT_DIR / "public_private_gap_same_code_by_question.csv")
    gap_same_cov = pd.read_csv(OUT_DIR / "public_private_gap_same_code_coverage.csv")

    helper_rows = []
    if not items.empty:
        helper_rows.append(
            {
                "metric": "items_total",
                "value": int(len(items)),
            }
        )
        helper_rows.append(
            {
                "metric": "items_good_discrimination_r_gt_0_30",
                "value": int((pd.to_numeric(items["point_biserial_r"], errors="coerce") > 0.30).sum()),
            }
        )
        helper_rows.append(
            {
                "metric": "items_low_discrimination_r_lt_0_15",
                "value": int((pd.to_numeric(items["point_biserial_r"], errors="coerce") < 0.15).sum()),
            }
        )
    if not redundancy.empty:
        helper_rows.append(
            {
                "metric": "redundant_pairs_gt_0_90",
                "value": int(redundancy["flag_near_redundant_gt_0_90"].fillna(False).astype(bool).sum()),
            }
        )
    if not deps.empty:
        helper_rows.append(
            {
                "metric": "dependency_edges_support5",
                "value": int(len(deps)),
            }
        )
    if not deps_reduced.empty:
        helper_rows.append(
            {
                "metric": "dependency_edges_transitive_reduced",
                "value": int(len(deps_reduced)),
            }
        )
    if not dep_scc.empty:
        helper_rows.append(
            {
                "metric": "dependency_scc_components",
                "value": int(len(dep_scc)),
            }
        )
        helper_rows.append(
            {
                "metric": "dependency_nontrivial_scc_components",
                "value": int(dep_scc["is_nontrivial_scc"].fillna(False).astype(bool).sum()),
            }
        )
    if not dep_min.empty:
        helper_rows.append(
            {
                "metric": "minimal_new_information_components",
                "value": int(len(dep_min)),
            }
        )
    if not rel.empty:
        alpha = pd.to_numeric(rel["cronbach_alpha_all_public_private_fill0"], errors="coerce").dropna()
        helper_rows.append({"metric": "namespaces_with_alpha", "value": int(alpha.size)})
        if not alpha.empty:
            helper_rows.append({"metric": "alpha_all_median", "value": round(float(alpha.median()), 4)})
            helper_rows.append({"metric": "alpha_all_min", "value": round(float(alpha.min()), 4)})
            helper_rows.append({"metric": "alpha_all_max", "value": round(float(alpha.max()), 4)})
    if not gap.empty:
        helper_rows.append(
            {
                "metric": "questions_public_all_private_not_all_ge_20pct",
                "value": int(
                    (pd.to_numeric(gap["frac_public_all_private_not_all"], errors="coerce") >= 0.20).sum()
                ),
            }
        )
    if not gap_same.empty:
        helper_rows.append(
            {
                "metric": "questions_same_code_public_all_private_not_all_ge_20pct",
                "value": int(
                    (pd.to_numeric(gap_same["frac_public_all_private_not_all"], errors="coerce") >= 0.20).sum()
                ),
            }
        )
    if not gap_same_cov.empty:
        helper_rows.append(
            {
                "metric": "same_code_pair_coverage_pct",
                "value": float(pd.to_numeric(gap_same_cov["same_code_pair_coverage_pct"], errors="coerce").iloc[0]),
            }
        )
    pd.DataFrame(helper_rows).to_csv(OUT_DIR / "classical_item_quality_helper_metrics.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing outputs to {OUT_DIR}")
    conn = make_conn()
    try:
        setup_base_tables(conn)
        export_base_outputs(conn)
        compute_item_difficulty_discrimination(conn)
        compute_redundancy_and_dependencies(conn)
        compute_namespace_reliability(conn)
        compute_public_private_gap(conn)
        compute_summary_rollups()
    finally:
        conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
