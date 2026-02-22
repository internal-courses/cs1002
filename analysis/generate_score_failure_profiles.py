#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "pandas>=2.2.0",
#   "matplotlib>=3.8.0",
# ]
# ///
"""Generate baseline score/failure/non-submission analyses and plots.

Outputs are written under ``analysis/score_failure_profiles/`` and are intended
to support the README section:
"Score Distributions, Failure Profiles, and the Non-Submission Problem".
"""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import duckdb
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "score_failure_profiles"
PLOTS_DIR = OUT_DIR / "plots"


def make_conn() -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection configured for local batch analysis."""
    conn = duckdb.connect()
    threads = max(1, (os_cpu_count() or 4) - 1)
    conn.execute(f"PRAGMA threads={threads}")
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def os_cpu_count() -> int | None:
    try:
        import os

        return os.cpu_count()
    except Exception:
        return None


def copy_query(conn: duckdb.DuckDBPyConnection, sql: str, out_csv: Path) -> None:
    """Run a SELECT query and export to CSV with header."""
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    escaped = out_csv.as_posix().replace("'", "''")
    conn.execute(f"COPY ({sql}) TO '{escaped}' (HEADER, DELIMITER ',')")


def qdf(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """Return a pandas DataFrame for a query."""
    return conn.execute(sql).df()


def one_row(conn: duckdb.DuckDBPyConnection, sql: str) -> dict[str, object]:
    df = qdf(conn, sql)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def setup_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create temporary views used by downstream analyses."""
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW fs_v AS
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          TRY_CAST("CompilationResult.score" AS DOUBLE) AS latest_submission_score,
          CAST(saved_code_events AS BIGINT) AS saved_code_events,
          CAST(test_run_events AS BIGINT) AS test_run_events,
          CAST(submission_events AS BIGINT) AS submission_events,
          CAST(total_events AS BIGINT) AS total_events,
          CAST(first_event_utc AS TIMESTAMP) AS first_event_utc,
          CAST(last_event_utc AS TIMESTAMP) AS last_event_utc,
          CAST(first_event_ist AS TIMESTAMP) AS first_event_ist,
          CAST(last_event_ist AS TIMESTAMP) AS last_event_ist,
          date_diff('second', CAST(first_event_utc AS TIMESTAMP), CAST(last_event_utc AS TIMESTAMP)) AS active_time_seconds
        FROM read_csv_auto('analysis/final_scores.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW timeline_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          student_id,
          timestamp_utc,
          timestamp_ist,
          event_type,
          evaluation_type,
          seconds_since_start,
          code_sha256,
          code_length,
          is_parseable,
          status,
          reason,
          summary,
          score,
          num_test_evaluated,
          num_test_passed,
          test_case_count
        FROM read_parquet('analysis/submission_timeline.parquet');
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_meta_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          question_title,
          question_text,
          has_skeleton_code,
          CAST(num_public_tests AS INTEGER) AS num_public_tests,
          CAST(num_private_tests AS INTEGER) AS num_private_tests
        FROM read_csv_auto('analysis/question_metadata.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW schedule_v AS
        SELECT
          term,
          wave,
          namespace,
          start_time,
          end_time,
          CAST(start_time AS DATE) AS exam_date,
          num_students
        FROM read_csv_auto('analysis/schedule.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW schedule_slots_v AS
        SELECT
          *,
          ROW_NUMBER() OVER (
            PARTITION BY term, wave, exam_date
            ORDER BY start_time, namespace
          ) AS slot_order_in_day
        FROM schedule_v;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW problem_max_score_v AS
        SELECT
          namespace,
          problem_id,
          COALESCE(MAX(latest_submission_score), 100.0) AS problem_max_score
        FROM fs_v
        GROUP BY namespace, problem_id;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW outcome_rows_v AS
        SELECT
          fs.*,
          pm.problem_max_score,
          CASE
            WHEN fs.submission_events > 0
                 AND abs(fs.latest_submission_score - pm.problem_max_score) < 1e-9
              THEN 'Full pass'
            WHEN fs.submission_events > 0
                 AND fs.latest_submission_score > 0
                 AND fs.latest_submission_score < pm.problem_max_score
              THEN 'Partial pass'
            WHEN fs.submission_events > 0
                 AND fs.latest_submission_score = 0
              THEN 'Submitted, zero'
            WHEN fs.submission_events = 0
                 AND fs.total_events > 0
              THEN 'Active, never submitted'
            ELSE 'No activity'
          END AS outcome_category
        FROM fs_v fs
        JOIN problem_max_score_v pm USING (namespace, problem_id);
        """
    )


def build_outcome_tables(conn: duckdb.DuckDBPyConnection) -> None:
    print("[1/8] Writing outcome category row-level and summary tables...")
    copy_query(
        conn,
        """
        SELECT
          o.namespace,
          o.problem_id,
          o.student_id,
          s.term,
          s.wave,
          s.start_time,
          s.end_time,
          s.slot_order_in_day,
          q.question_title,
          o.problem_max_score,
          o.latest_submission_score,
          o.saved_code_events,
          o.test_run_events,
          o.submission_events,
          o.total_events,
          o.active_time_seconds,
          o.first_event_utc,
          o.last_event_utc,
          o.first_event_ist,
          o.last_event_ist,
          o.outcome_category
        FROM outcome_rows_v o
        LEFT JOIN schedule_slots_v s USING (namespace)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY o.namespace, o.problem_id, o.student_id
        """,
        OUT_DIR / "outcome_categories.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          outcome_category,
          COUNT(*) AS rows,
          ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_rows
        FROM outcome_rows_v
        GROUP BY outcome_category
        ORDER BY CASE outcome_category
          WHEN 'Full pass' THEN 1
          WHEN 'Partial pass' THEN 2
          WHEN 'Submitted, zero' THEN 3
          WHEN 'Active, never submitted' THEN 4
          WHEN 'No activity' THEN 5
          ELSE 99
        END
        """,
        OUT_DIR / "outcome_category_summary.csv",
    )


def build_non_submission_profiles(conn: duckdb.DuckDBPyConnection) -> None:
    print("[2/8] Building non-submission profiles from timeline data...")
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW non_submit_rows_v AS
        SELECT * FROM outcome_rows_v
        WHERE outcome_category = 'Active, never submitted';
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW non_submit_timeline_agg_v AS
        SELECT
          t.namespace,
          t.problem_id,
          t.student_id,
          COUNT(*) FILTER (WHERE t.event_type = 'test_run') AS timeline_test_run_events,
          COUNT(*) FILTER (WHERE t.event_type = 'test_run' AND t.evaluation_type = 'public') AS public_test_run_events,
          COUNT(*) FILTER (WHERE t.event_type = 'test_run' AND t.evaluation_type = 'private') AS private_test_run_events,
          COUNT(*) FILTER (
            WHERE t.event_type = 'test_run'
              AND t.evaluation_type = 'public'
              AND COALESCE(t.num_test_passed, 0) > 0
          ) AS public_runs_with_any_pass,
          COUNT(*) FILTER (
            WHERE t.event_type = 'test_run'
              AND t.evaluation_type = 'public'
              AND COALESCE(t.num_test_passed, 0) = COALESCE(t.test_case_count, -1)
              AND COALESCE(t.test_case_count, 0) > 0
          ) AS public_runs_all_cases_passed,
          COUNT(*) FILTER (
            WHERE t.event_type = 'test_run'
              AND COALESCE(t.num_test_passed, 0) > 0
          ) AS all_test_runs_with_any_pass,
          COALESCE(MAX(CASE
            WHEN t.event_type = 'test_run' AND t.evaluation_type = 'public'
              THEN t.num_test_passed
          END), 0) AS max_public_test_passed,
          COALESCE(MAX(CASE
            WHEN t.event_type = 'test_run'
              THEN t.num_test_passed
          END), 0) AS max_any_test_passed,
          COALESCE(MAX(CASE
            WHEN t.event_type = 'test_run'
             AND t.evaluation_type = 'public'
             AND COALESCE(t.test_case_count, 0) > 0
              THEN 1.0 * t.num_test_passed / t.test_case_count
          END), 0.0) AS max_public_pass_fraction,
          COALESCE(MAX(t.seconds_since_start), 0) AS max_seconds_since_start
        FROM timeline_v t
        JOIN non_submit_rows_v n
          USING (namespace, problem_id, student_id)
        GROUP BY t.namespace, t.problem_id, t.student_id;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW non_submit_last_event_v AS
        SELECT *
        FROM (
          SELECT
            t.namespace,
            t.problem_id,
            t.student_id,
            t.timestamp_utc AS last_event_timestamp_utc,
            t.timestamp_ist AS last_event_timestamp_ist,
            t.event_type AS last_event_type,
            t.evaluation_type AS last_event_evaluation_type,
            t.seconds_since_start AS last_event_seconds_since_start,
            t.code_sha256 AS last_code_sha256,
            t.code_length AS last_code_length,
            t.is_parseable AS last_is_parseable,
            t.summary AS last_event_summary,
            t.reason AS last_event_reason,
            t.score AS last_event_score,
            t.num_test_passed AS last_event_num_test_passed,
            t.test_case_count AS last_event_test_case_count,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY t.timestamp_utc DESC,
                       COALESCE(t.event_type, '') DESC,
                       COALESCE(t.evaluation_type, '') DESC,
                       COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
          JOIN non_submit_rows_v n
            USING (namespace, problem_id, student_id)
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW non_submit_last_public_test_run_v AS
        SELECT *
        FROM (
          SELECT
            t.namespace,
            t.problem_id,
            t.student_id,
            t.timestamp_utc AS last_public_test_run_ts_utc,
            t.timestamp_ist AS last_public_test_run_ts_ist,
            t.summary AS last_public_summary,
            t.reason AS last_public_reason,
            t.score AS last_public_score,
            t.num_test_evaluated AS last_public_num_test_evaluated,
            t.num_test_passed AS last_public_num_test_passed,
            t.test_case_count AS last_public_test_case_count,
            t.is_parseable AS last_public_is_parseable,
            t.code_length AS last_public_code_length,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
          JOIN non_submit_rows_v n
            USING (namespace, problem_id, student_id)
          WHERE t.event_type = 'test_run' AND t.evaluation_type = 'public'
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW non_submit_profiles_v AS
        SELECT
          n.namespace,
          n.problem_id,
          n.student_id,
          s.term,
          s.wave,
          s.exam_date,
          s.start_time,
          s.end_time,
          s.slot_order_in_day,
          q.question_title,
          q.num_public_tests,
          q.num_private_tests,
          n.saved_code_events,
          n.test_run_events,
          n.submission_events,
          n.total_events,
          n.active_time_seconds,
          n.first_event_utc,
          n.last_event_utc,
          n.first_event_ist,
          n.last_event_ist,
          a.timeline_test_run_events,
          a.public_test_run_events,
          a.private_test_run_events,
          a.public_runs_with_any_pass,
          a.public_runs_all_cases_passed,
          a.all_test_runs_with_any_pass,
          a.max_public_test_passed,
          a.max_any_test_passed,
          a.max_public_pass_fraction,
          a.max_seconds_since_start,
          le.last_event_timestamp_utc,
          le.last_event_timestamp_ist,
          le.last_event_type,
          le.last_event_evaluation_type,
          le.last_event_seconds_since_start,
          le.last_code_sha256,
          le.last_code_length,
          le.last_is_parseable,
          le.last_event_summary,
          le.last_event_reason,
          le.last_event_score,
          le.last_event_num_test_passed,
          le.last_event_test_case_count,
          lp.last_public_test_run_ts_utc,
          lp.last_public_test_run_ts_ist,
          lp.last_public_summary,
          lp.last_public_reason,
          lp.last_public_score,
          lp.last_public_num_test_evaluated,
          lp.last_public_num_test_passed,
          lp.last_public_test_case_count,
          lp.last_public_is_parseable,
          lp.last_public_code_length,
          (a.public_runs_with_any_pass > 0) AS had_any_public_pass,
          (a.public_runs_all_cases_passed > 0) AS had_all_public_cases_passed_in_test_run,
          (a.timeline_test_run_events > 0 AND a.all_test_runs_with_any_pass = 0) AS all_test_runs_failed,
          (n.test_run_events <= 3) AS very_few_test_runs_le3,
          (n.test_run_events > 10 AND a.public_runs_with_any_pass = 0) AS substantial_activity_all_failing_gt10,
          CASE
            WHEN a.public_runs_with_any_pass > 0
              THEN 'Had passing public test runs but never submitted'
            WHEN n.test_run_events <= 3
              THEN 'Very few test runs (<=3), no public pass'
            WHEN n.test_run_events > 10
              THEN 'Substantial activity (>10), no public pass'
            ELSE 'Moderate activity (4-10), no public pass'
          END AS non_submission_subtype,
          CASE
            WHEN le.last_is_parseable AND a.public_runs_with_any_pass > 0
              THEN 'Parseable last snapshot with public-pass evidence (partial-solution proxy)'
            WHEN le.last_is_parseable
              THEN 'Parseable last snapshot, no public-pass evidence'
            ELSE 'Unparseable/empty last snapshot'
          END AS last_snapshot_proxy
        FROM non_submit_rows_v n
        LEFT JOIN non_submit_timeline_agg_v a
          USING (namespace, problem_id, student_id)
        LEFT JOIN non_submit_last_event_v le
          USING (namespace, problem_id, student_id)
        LEFT JOIN non_submit_last_public_test_run_v lp
          USING (namespace, problem_id, student_id)
        LEFT JOIN schedule_slots_v s
          USING (namespace)
        LEFT JOIN question_meta_v q
          USING (namespace, problem_id);
        """
    )

    copy_query(
        conn,
        """
        SELECT *
        FROM non_submit_profiles_v
        ORDER BY namespace, problem_id, student_id
        """,
        OUT_DIR / "non_submission_profiles.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          metric,
          rows,
          ROUND(100.0 * rows / total_rows, 2) AS pct_non_submitters
        FROM (
          SELECT 'Non-submitters total' AS metric, COUNT(*) AS rows, COUNT(*) AS total_rows FROM non_submit_profiles_v
          UNION ALL
          SELECT 'Had any public test pass', COUNT(*) FILTER (WHERE had_any_public_pass), COUNT(*) FROM non_submit_profiles_v
          UNION ALL
          SELECT 'Had all public tests pass in at least one test_run', COUNT(*) FILTER (WHERE had_all_public_cases_passed_in_test_run), COUNT(*) FROM non_submit_profiles_v
          UNION ALL
          SELECT 'All test runs failed (no passed tests on any test_run)', COUNT(*) FILTER (WHERE all_test_runs_failed), COUNT(*) FROM non_submit_profiles_v
          UNION ALL
          SELECT 'Very few test runs (<=3)', COUNT(*) FILTER (WHERE very_few_test_runs_le3), COUNT(*) FROM non_submit_profiles_v
          UNION ALL
          SELECT 'Substantial activity (>10) and no public pass', COUNT(*) FILTER (WHERE substantial_activity_all_failing_gt10), COUNT(*) FROM non_submit_profiles_v
        ) t
        ORDER BY CASE metric
          WHEN 'Non-submitters total' THEN 1
          WHEN 'Had any public test pass' THEN 2
          WHEN 'Had all public tests pass in at least one test_run' THEN 3
          WHEN 'All test runs failed (no passed tests on any test_run)' THEN 4
          WHEN 'Very few test runs (<=3)' THEN 5
          WHEN 'Substantial activity (>10) and no public pass' THEN 6
          ELSE 99
        END
        """,
        OUT_DIR / "non_submission_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          non_submission_subtype,
          COUNT(*) AS rows,
          ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_non_submitters
        FROM non_submit_profiles_v
        GROUP BY non_submission_subtype
        ORDER BY rows DESC
        """,
        OUT_DIR / "non_submission_subtype_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          CASE
            WHEN test_run_events <= 1 THEN '1'
            WHEN test_run_events = 2 THEN '2'
            WHEN test_run_events = 3 THEN '3'
            WHEN test_run_events BETWEEN 4 AND 5 THEN '4-5'
            WHEN test_run_events BETWEEN 6 AND 10 THEN '6-10'
            WHEN test_run_events BETWEEN 11 AND 20 THEN '11-20'
            WHEN test_run_events BETWEEN 21 AND 50 THEN '21-50'
            ELSE '51+'
          END AS test_run_count_bin,
          COUNT(*) AS rows
        FROM non_submit_profiles_v
        GROUP BY test_run_count_bin
        ORDER BY CASE test_run_count_bin
          WHEN '1' THEN 1
          WHEN '2' THEN 2
          WHEN '3' THEN 3
          WHEN '4-5' THEN 4
          WHEN '6-10' THEN 5
          WHEN '11-20' THEN 6
          WHEN '21-50' THEN 7
          WHEN '51+' THEN 8
          ELSE 99
        END
        """,
        OUT_DIR / "non_submission_test_run_count_histogram.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          CASE
            WHEN COALESCE(active_time_seconds, 0) = 0 THEN '0 min'
            WHEN active_time_seconds <= 300 THEN '1-5 min'
            WHEN active_time_seconds <= 900 THEN '5-15 min'
            WHEN active_time_seconds <= 1800 THEN '15-30 min'
            WHEN active_time_seconds <= 3600 THEN '30-60 min'
            WHEN active_time_seconds <= 7200 THEN '60-120 min'
            ELSE '120+ min'
          END AS active_time_bin,
          COUNT(*) AS rows
        FROM non_submit_profiles_v
        GROUP BY active_time_bin
        ORDER BY CASE active_time_bin
          WHEN '0 min' THEN 1
          WHEN '1-5 min' THEN 2
          WHEN '5-15 min' THEN 3
          WHEN '15-30 min' THEN 4
          WHEN '30-60 min' THEN 5
          WHEN '60-120 min' THEN 6
          WHEN '120+ min' THEN 7
          ELSE 99
        END
        """,
        OUT_DIR / "non_submission_active_time_histogram.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          last_snapshot_proxy,
          COUNT(*) AS rows,
          ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_non_submitters
        FROM non_submit_profiles_v
        GROUP BY last_snapshot_proxy
        ORDER BY rows DESC
        """,
        OUT_DIR / "non_submission_last_snapshot_proxy_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          COALESCE(last_public_summary, '[no public test_run found]') AS last_public_summary,
          COUNT(*) AS rows,
          ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_non_submitters
        FROM non_submit_profiles_v
        GROUP BY 1
        ORDER BY rows DESC
        LIMIT 20
        """,
        OUT_DIR / "non_submission_last_public_summary_top20.csv",
    )


def build_question_metrics(conn: duckdb.DuckDBPyConnection) -> None:
    print("[3/8] Computing per-question score distributions and shape flags...")
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_score_metrics_base_v AS
        SELECT
          o.namespace,
          o.problem_id,
          s.term,
          s.wave,
          s.exam_date,
          s.start_time,
          s.end_time,
          s.slot_order_in_day,
          q.question_title,
          q.num_public_tests,
          q.num_private_tests,
          pm.problem_max_score,
          COUNT(*) AS assigned_students,
          COUNT(*) FILTER (WHERE o.submission_events > 0) AS submitters,
          COUNT(*) FILTER (WHERE o.submission_events = 0) AS non_submitters,
          COUNT(*) FILTER (WHERE o.submission_events > 0 AND o.latest_submission_score = 0) AS submitter_zero_count,
          COUNT(*) FILTER (
            WHERE o.submission_events > 0
              AND abs(o.latest_submission_score - pm.problem_max_score) < 1e-9
          ) AS submitter_full_count,
          COUNT(*) FILTER (
            WHERE o.submission_events > 0
              AND o.latest_submission_score > 0
              AND o.latest_submission_score < pm.problem_max_score
          ) AS submitter_partial_count,
          ROUND(100.0 * COUNT(*) FILTER (WHERE o.submission_events > 0) / COUNT(*), 2) AS submission_rate_pct,
          ROUND(100.0 * COUNT(*) FILTER (WHERE o.submission_events = 0) / COUNT(*), 2) AS non_submission_rate_pct,
          ROUND(AVG(CASE WHEN o.submission_events > 0 THEN o.latest_submission_score END), 2) AS submitter_mean_score,
          ROUND(median(CASE WHEN o.submission_events > 0 THEN o.latest_submission_score END), 2) AS submitter_median_score,
          ROUND(100.0 * COUNT(*) FILTER (WHERE o.submission_events > 0 AND o.latest_submission_score = 0)
                / NULLIF(COUNT(*) FILTER (WHERE o.submission_events > 0), 0), 2) AS submitter_zero_pct,
          ROUND(100.0 * COUNT(*) FILTER (
                WHERE o.submission_events > 0
                  AND abs(o.latest_submission_score - pm.problem_max_score) < 1e-9
              ) / NULLIF(COUNT(*) FILTER (WHERE o.submission_events > 0), 0), 2) AS submitter_full_pct,
          ROUND(100.0 * COUNT(*) FILTER (
                WHERE o.submission_events > 0
                  AND o.latest_submission_score > 0
                  AND o.latest_submission_score < pm.problem_max_score
              ) / NULLIF(COUNT(*) FILTER (WHERE o.submission_events > 0), 0), 2) AS submitter_partial_pct,
          ROUND(AVG(COALESCE(o.latest_submission_score, 0.0)), 2) AS all_assigned_mean_score,
          ROUND(median(COALESCE(o.latest_submission_score, 0.0)), 2) AS all_assigned_median_score
        FROM outcome_rows_v o
        JOIN problem_max_score_v pm USING (namespace, problem_id)
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        LEFT JOIN schedule_slots_v s USING (namespace)
        GROUP BY
          o.namespace, o.problem_id, s.term, s.wave, s.exam_date, s.start_time, s.end_time, s.slot_order_in_day,
          q.question_title, q.num_public_tests, q.num_private_tests, pm.problem_max_score;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_score_metrics_v AS
        SELECT
          *,
          (submitters >= 20 AND submitter_zero_pct >= 30 AND submitter_full_pct >= 30 AND submitter_partial_pct <= 20) AS flag_bimodal,
          (submitters >= 20 AND submitter_full_pct > 80) AS flag_ceiling,
          (submitters >= 20 AND submitter_zero_pct > 70) AS flag_floor,
          (submitters >= 20
           AND submitter_zero_pct <= 50
           AND submitter_full_pct <= 80
           AND submitter_partial_pct BETWEEN 30 AND 70) AS flag_healthy_spread
        FROM question_score_metrics_base_v;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_score_metrics_labeled_v AS
        SELECT
          *,
          CASE
            WHEN submitters < 20 THEN 'Insufficient submitters'
            WHEN flag_bimodal THEN 'Bimodal'
            WHEN flag_floor THEN 'Floor'
            WHEN flag_ceiling THEN 'Ceiling'
            WHEN flag_healthy_spread THEN 'Healthy spread'
            ELSE 'Mixed'
          END AS distribution_shape
        FROM question_score_metrics_v;
        """
    )

    copy_query(
        conn,
        """
        SELECT *
        FROM question_score_metrics_labeled_v
        ORDER BY term, wave, start_time, namespace, problem_id
        """,
        OUT_DIR / "question_score_metrics.csv",
    )

    copy_query(
        conn,
        """
        WITH base AS (
          SELECT
            o.namespace,
            o.problem_id,
            CASE
              WHEN o.latest_submission_score >= 100 THEN 100
              ELSE CAST(floor(o.latest_submission_score / 10.0) * 10 AS INTEGER)
            END AS score_bin_start,
            COUNT(*) AS rows
          FROM outcome_rows_v o
          WHERE o.submission_events > 0
          GROUP BY o.namespace, o.problem_id, score_bin_start
        )
        SELECT
          b.namespace,
          b.problem_id,
          q.question_title,
          b.score_bin_start,
          CASE
            WHEN b.score_bin_start = 100 THEN '100'
            ELSE lpad(CAST(b.score_bin_start AS VARCHAR), 2, '0') || '-' ||
                 lpad(CAST(b.score_bin_start + 9 AS VARCHAR), 2, '0')
          END AS score_bin_label,
          b.rows
        FROM base b
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY b.namespace, b.problem_id, b.score_bin_start
        """,
        OUT_DIR / "question_score_hist_submitters.csv",
    )

    copy_query(
        conn,
        """
        WITH base AS (
          SELECT
            o.namespace,
            o.problem_id,
            CASE
              WHEN COALESCE(o.latest_submission_score, 0.0) >= 100 THEN 100
              ELSE CAST(floor(COALESCE(o.latest_submission_score, 0.0) / 10.0) * 10 AS INTEGER)
            END AS score_bin_start,
            COUNT(*) AS rows
          FROM outcome_rows_v o
          GROUP BY o.namespace, o.problem_id, score_bin_start
        )
        SELECT
          b.namespace,
          b.problem_id,
          q.question_title,
          b.score_bin_start,
          CASE
            WHEN b.score_bin_start = 100 THEN '100'
            ELSE lpad(CAST(b.score_bin_start AS VARCHAR), 2, '0') || '-' ||
                 lpad(CAST(b.score_bin_start + 9 AS VARCHAR), 2, '0')
          END AS score_bin_label,
          b.rows
        FROM base b
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        ORDER BY b.namespace, b.problem_id, b.score_bin_start
        """,
        OUT_DIR / "question_score_hist_all_assigned.csv",
    )


def build_test_case_pass_rates(conn: duckdb.DuckDBPyConnection) -> None:
    print("[4/8] Computing per-test-case pass rates (public from test_run, private from submission)...")
    copy_query(
        conn,
        """
        WITH raw AS (
          SELECT
            Namespace AS namespace,
            CAST(ProblemID AS INTEGER) AS problem_id,
            regexp_extract(FileName, '/(saved_code|test_run|submission)/', 1) AS event_type,
            EvaluationType AS evaluation_type,
            CompilationResult
          FROM read_json(
            'submissions/*.json',
            format='newline_delimited',
            columns={
              Namespace:'VARCHAR',
              ProblemID:'VARCHAR',
              FileName:'VARCHAR',
              EvaluationType:'VARCHAR',
              CompilationResult:'VARCHAR'
            }
          )
          WHERE FileName IS NOT NULL
            AND FileName <> ''
            AND CompilationResult IS NOT NULL
            AND json_valid(CompilationResult)
        ),
        filtered AS (
          SELECT *
          FROM raw
          WHERE (event_type = 'test_run' AND evaluation_type = 'public')
             OR event_type = 'submission'
        ),
        cases AS (
          SELECT
            f.namespace,
            f.problem_id,
            CASE
              WHEN f.event_type = 'submission' THEN 'private'
              ELSE 'public'
            END AS test_scope,
            CAST(je.key AS INTEGER) + 1 AS test_case_index,
            CAST(json_extract(je.value, '$.passed') AS BOOLEAN) AS passed
          FROM filtered f,
               json_each(json_extract(f.CompilationResult, '$.test_case_results')) AS je
        )
        SELECT
          c.namespace,
          c.problem_id,
          q.question_title,
          c.test_scope,
          c.test_case_index,
          COUNT(*) AS attempts,
          SUM(CASE WHEN c.passed THEN 1 ELSE 0 END) AS passes,
          ROUND(100.0 * SUM(CASE WHEN c.passed THEN 1 ELSE 0 END) / COUNT(*), 2) AS pass_rate_pct
        FROM cases c
        LEFT JOIN question_meta_v q USING (namespace, problem_id)
        GROUP BY c.namespace, c.problem_id, q.question_title, c.test_scope, c.test_case_index
        ORDER BY c.namespace, c.problem_id, c.test_scope, c.test_case_index
        """,
        OUT_DIR / "question_test_case_pass_rates.csv",
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_test_case_pass_rates_v AS
        SELECT *
        FROM read_csv_auto('analysis/score_failure_profiles/question_test_case_pass_rates.csv', header=true);
        """
    )

    copy_query(
        conn,
        """
        SELECT
          namespace,
          problem_id,
          question_title,
          test_scope,
          COUNT(*) AS num_cases,
          ROUND(AVG(pass_rate_pct), 2) AS avg_case_pass_rate_pct,
          ROUND(median(pass_rate_pct), 2) AS median_case_pass_rate_pct,
          ROUND(MIN(pass_rate_pct), 2) AS min_case_pass_rate_pct,
          ROUND(MAX(pass_rate_pct), 2) AS max_case_pass_rate_pct
        FROM question_test_case_pass_rates_v
        GROUP BY namespace, problem_id, question_title, test_scope
        ORDER BY namespace, problem_id, test_scope
        """,
        OUT_DIR / "question_test_case_pass_rate_summary.csv",
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW question_case_pass_pivot_v AS
        WITH s AS (
          SELECT *
          FROM read_csv_auto('analysis/score_failure_profiles/question_test_case_pass_rate_summary.csv', header=true)
        )
        SELECT
          namespace,
          problem_id,
          MAX(avg_case_pass_rate_pct) FILTER (WHERE test_scope = 'public') AS public_avg_case_pass_rate_pct,
          MAX(min_case_pass_rate_pct) FILTER (WHERE test_scope = 'public') AS public_min_case_pass_rate_pct,
          MAX(max_case_pass_rate_pct) FILTER (WHERE test_scope = 'public') AS public_max_case_pass_rate_pct,
          MAX(avg_case_pass_rate_pct) FILTER (WHERE test_scope = 'private') AS private_avg_case_pass_rate_pct,
          MAX(min_case_pass_rate_pct) FILTER (WHERE test_scope = 'private') AS private_min_case_pass_rate_pct,
          MAX(max_case_pass_rate_pct) FILTER (WHERE test_scope = 'private') AS private_max_case_pass_rate_pct
        FROM s
        GROUP BY namespace, problem_id;
        """
    )

    copy_query(
        conn,
        """
        SELECT
          q.*,
          c.public_avg_case_pass_rate_pct,
          c.public_min_case_pass_rate_pct,
          c.public_max_case_pass_rate_pct,
          c.private_avg_case_pass_rate_pct,
          c.private_min_case_pass_rate_pct,
          c.private_max_case_pass_rate_pct
        FROM question_score_metrics_labeled_v q
        LEFT JOIN question_case_pass_pivot_v c USING (namespace, problem_id)
        ORDER BY q.term, q.wave, q.start_time, q.namespace, q.problem_id
        """,
        OUT_DIR / "question_score_metrics_with_case_pass_rates.csv",
    )


def build_wave_slot_and_reuse_tables(conn: duckdb.DuckDBPyConnection) -> None:
    print("[5/8] Building wave, slot, and reused-question comparison tables...")
    copy_query(
        conn,
        """
        SELECT
          term,
          wave,
          SUM(assigned_students) AS assigned_students,
          SUM(submitters) AS submitters,
          ROUND(100.0 * SUM(submitters) / NULLIF(SUM(assigned_students), 0), 2) AS submission_rate_pct,
          ROUND(SUM(submitter_mean_score * submitters) / NULLIF(SUM(submitters), 0), 2) AS weighted_submitter_mean_score,
          ROUND(SUM(all_assigned_mean_score * assigned_students) / NULLIF(SUM(assigned_students), 0), 2) AS weighted_effective_mean_score
        FROM question_score_metrics_labeled_v
        GROUP BY term, wave
        ORDER BY term, wave
        """,
        OUT_DIR / "term_wave_score_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          term,
          wave,
          exam_date,
          slot_order_in_day,
          COUNT(*) AS questions,
          SUM(assigned_students) AS assigned_students,
          SUM(submitters) AS submitters,
          ROUND(100.0 * SUM(submitters) / NULLIF(SUM(assigned_students), 0), 2) AS submission_rate_pct,
          ROUND(SUM(submitter_mean_score * submitters) / NULLIF(SUM(submitters), 0), 2) AS weighted_submitter_mean_score,
          ROUND(SUM(all_assigned_mean_score * assigned_students) / NULLIF(SUM(assigned_students), 0), 2) AS weighted_effective_mean_score,
          ROUND(AVG(non_submission_rate_pct), 2) AS avg_question_non_submission_rate_pct
        FROM question_score_metrics_labeled_v
        GROUP BY term, wave, exam_date, slot_order_in_day
        ORDER BY term, wave, exam_date, slot_order_in_day
        """,
        OUT_DIR / "slot_order_score_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          namespace,
          term,
          wave,
          exam_date,
          slot_order_in_day,
          start_time,
          end_time,
          COUNT(*) AS questions,
          SUM(assigned_students) AS assigned_students,
          SUM(submitters) AS submitters,
          ROUND(100.0 * SUM(submitters) / NULLIF(SUM(assigned_students), 0), 2) AS submission_rate_pct,
          ROUND(SUM(submitter_mean_score * submitters) / NULLIF(SUM(submitters), 0), 2) AS weighted_submitter_mean_score,
          ROUND(SUM(all_assigned_mean_score * assigned_students) / NULLIF(SUM(assigned_students), 0), 2) AS weighted_effective_mean_score,
          ROUND(AVG(non_submission_rate_pct), 2) AS avg_question_non_submission_rate_pct
        FROM question_score_metrics_labeled_v
        GROUP BY namespace, term, wave, exam_date, slot_order_in_day, start_time, end_time
        ORDER BY start_time, namespace
        """,
        OUT_DIR / "exam_namespace_score_summary.csv",
    )

    qdf_metrics = qdf(
        conn,
        """
        SELECT *
        FROM read_csv_auto('analysis/score_failure_profiles/question_score_metrics_with_case_pass_rates.csv', header=true)
        """,
    )
    qdf_meta = qdf(conn, "SELECT namespace, problem_id, question_title, question_text FROM question_meta_v")

    merged = qdf_metrics.merge(qdf_meta, on=["namespace", "problem_id"], how="left", suffixes=("", "_meta"))
    if "question_title_meta" in merged.columns:
        merged["question_title"] = merged["question_title"].fillna(merged["question_title_meta"])

    def normalize_text(value: str | None) -> str:
        if not isinstance(value, str):
            value = ""
        text = value.lower()
        text = " ".join(text.split())
        return text

    merged["reuse_title_key"] = merged["question_title"].fillna("").map(normalize_text)
    merged["reuse_text_key"] = merged["question_text"].fillna("").map(normalize_text)
    merged["reuse_key"] = merged["reuse_title_key"] + "||" + merged["reuse_text_key"]
    merged["term"] = merged["term"].astype(str)

    reused = merged.groupby("reuse_key", dropna=False).filter(lambda g: g["term"].nunique() >= 2 and len(g) >= 2).copy()
    if reused.empty:
        reused_out = pd.DataFrame(
            columns=[
                "reuse_group_size",
                "distinct_terms",
                "question_title",
                "namespace",
                "problem_id",
                "term",
                "wave",
                "submission_rate_pct",
                "submitter_mean_score",
                "all_assigned_mean_score",
                "distribution_shape",
            ]
        )
        reused_summary = pd.DataFrame(
            columns=[
                "reuse_group_size",
                "distinct_terms",
                "question_title",
                "min_submission_rate_pct",
                "max_submission_rate_pct",
                "submission_rate_range_pct",
                "min_all_assigned_mean_score",
                "max_all_assigned_mean_score",
                "all_assigned_mean_range",
            ]
        )
    else:
        group_stats = (
            reused.groupby("reuse_key")
            .agg(
                reuse_group_size=("namespace", "size"),
                distinct_terms=("term", "nunique"),
                question_title=("question_title", "first"),
                min_submission_rate_pct=("submission_rate_pct", "min"),
                max_submission_rate_pct=("submission_rate_pct", "max"),
                min_all_assigned_mean_score=("all_assigned_mean_score", "min"),
                max_all_assigned_mean_score=("all_assigned_mean_score", "max"),
            )
            .reset_index()
        )
        group_stats["submission_rate_range_pct"] = (
            group_stats["max_submission_rate_pct"] - group_stats["min_submission_rate_pct"]
        ).round(2)
        group_stats["all_assigned_mean_range"] = (
            group_stats["max_all_assigned_mean_score"] - group_stats["min_all_assigned_mean_score"]
        ).round(2)

        reused_out = reused.merge(group_stats[["reuse_key", "reuse_group_size", "distinct_terms"]], on="reuse_key", how="left")
        reused_out = reused_out[
            [
                "reuse_group_size",
                "distinct_terms",
                "question_title",
                "namespace",
                "problem_id",
                "term",
                "wave",
                "start_time",
                "submission_rate_pct",
                "submitter_mean_score",
                "all_assigned_mean_score",
                "submitter_zero_pct",
                "submitter_full_pct",
                "distribution_shape",
                "public_avg_case_pass_rate_pct",
                "private_avg_case_pass_rate_pct",
            ]
        ].sort_values(["question_title", "term", "wave", "start_time", "namespace", "problem_id"])
        reused_summary = group_stats[
            [
                "reuse_group_size",
                "distinct_terms",
                "question_title",
                "min_submission_rate_pct",
                "max_submission_rate_pct",
                "submission_rate_range_pct",
                "min_all_assigned_mean_score",
                "max_all_assigned_mean_score",
                "all_assigned_mean_range",
            ]
        ].sort_values(["distinct_terms", "reuse_group_size", "submission_rate_range_pct"], ascending=[False, False, False])

    reused_out.to_csv(OUT_DIR / "reused_question_comparison.csv", index=False)
    reused_summary.to_csv(OUT_DIR / "reused_question_summary.csv", index=False)


def build_question_and_non_submit_rate_breakdowns(conn: duckdb.DuckDBPyConnection) -> None:
    print("[6/8] Writing additional non-submission rate breakdowns...")
    copy_query(
        conn,
        """
        SELECT
          namespace,
          problem_id,
          question_title,
          term,
          wave,
          exam_date,
          slot_order_in_day,
          assigned_students,
          non_submitters,
          non_submission_rate_pct,
          submitters,
          submission_rate_pct,
          distribution_shape
        FROM question_score_metrics_labeled_v
        ORDER BY non_submission_rate_pct DESC, assigned_students DESC, namespace, problem_id
        """,
        OUT_DIR / "non_submission_rate_by_question.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          term,
          wave,
          COUNT(*) AS questions,
          SUM(assigned_students) AS assigned_students,
          SUM(non_submitters) AS non_submitters,
          ROUND(100.0 * SUM(non_submitters) / NULLIF(SUM(assigned_students), 0), 2) AS non_submission_rate_pct
        FROM question_score_metrics_labeled_v
        GROUP BY term, wave
        ORDER BY term, wave
        """,
        OUT_DIR / "non_submission_rate_by_term_wave.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          term,
          wave,
          exam_date,
          slot_order_in_day,
          COUNT(*) AS questions,
          SUM(assigned_students) AS assigned_students,
          SUM(non_submitters) AS non_submitters,
          ROUND(100.0 * SUM(non_submitters) / NULLIF(SUM(assigned_students), 0), 2) AS non_submission_rate_pct
        FROM question_score_metrics_labeled_v
        GROUP BY term, wave, exam_date, slot_order_in_day
        ORDER BY term, wave, exam_date, slot_order_in_day
        """,
        OUT_DIR / "non_submission_rate_by_slot.csv",
    )


def plot_outputs() -> None:
    print("[7/8] Rendering plots...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    outcome = pd.read_csv(OUT_DIR / "outcome_category_summary.csv")
    question_metrics = pd.read_csv(OUT_DIR / "question_score_metrics_with_case_pass_rates.csv")
    non_submit_profiles = pd.read_csv(OUT_DIR / "non_submission_profiles.csv")
    test_case_rates = pd.read_csv(OUT_DIR / "question_test_case_pass_rates.csv")
    slot_summary = pd.read_csv(OUT_DIR / "slot_order_score_summary.csv")

    # 1) Overall score distributions.
    all_rows = pd.read_csv(OUT_DIR / "outcome_categories.csv", usecols=["latest_submission_score", "submission_events"])
    submitter_scores = all_rows.loc[all_rows["submission_events"] > 0, "latest_submission_score"].dropna().astype(float)
    effective_scores = all_rows["latest_submission_score"].fillna(0).astype(float)

    bins = list(range(0, 105, 5))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(effective_scores, bins=bins, alpha=0.60, label="All assigned (non-submitters as 0)", color="#4C78A8")
    ax.hist(submitter_scores, bins=bins, alpha=0.70, label="Submitters only", color="#F58518")
    ax.set_title("Overall Score Distributions")
    ax.set_xlabel("Score")
    ax.set_ylabel("Student-question rows")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "overall_score_distributions.png", dpi=160)
    plt.close(fig)

    # 2) Outcome category bar chart.
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(outcome["outcome_category"], outcome["rows"], color=["#54A24B", "#ECA82C", "#E45756", "#4C78A8", "#9D9DA1"])
    ax.set_title("Outcome Categories (151,778 Student-Question Rows)")
    ax.set_ylabel("Rows")
    ax.tick_params(axis="x", rotation=20)
    for i, row in outcome.reset_index(drop=True).iterrows():
        ax.text(i, row["rows"], f"{int(row['rows']):,}\n({row['pct_rows']:.1f}%)", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "outcome_categories.png", dpi=160)
    plt.close(fig)

    # 3) Non-submission distributions (test runs and active time).
    ns = non_submit_profiles.copy()
    ns["test_run_events"] = pd.to_numeric(ns["test_run_events"], errors="coerce").fillna(0)
    ns["active_time_minutes"] = pd.to_numeric(ns["active_time_seconds"], errors="coerce").fillna(0) / 60.0

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    tr_bins = [
        0,
        1,
        2,
        3,
        5,
        10,
        20,
        50,
        100,
        max(100, int(math.ceil(ns["test_run_events"].max() / 10) * 10) + 1),
    ]
    axes[0].hist(ns["test_run_events"], bins=sorted(set(tr_bins)), color="#4C78A8", alpha=0.9)
    axes[0].set_title("Non-submitters: Test Run Count")
    axes[0].set_xlabel("test_run events")
    axes[0].set_ylabel("Rows")
    axes[0].set_xscale("symlog", linthresh=3)
    axes[0].grid(axis="y", alpha=0.2)

    axes[1].hist(ns["active_time_minutes"], bins=[0, 1, 5, 15, 30, 60, 120, 180, 240, 300], color="#E45756", alpha=0.9)
    axes[1].set_title("Non-submitters: Active Time Span")
    axes[1].set_xlabel("Observed span (minutes)")
    axes[1].set_ylabel("Rows")
    axes[1].grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "non_submission_distributions.png", dpi=160)
    plt.close(fig)

    # 4) Question distribution shape map.
    qm = question_metrics.copy()
    qm = qm[pd.to_numeric(qm["submitters"], errors="coerce").fillna(0) >= 20].copy()
    qm["submitter_zero_pct"] = pd.to_numeric(qm["submitter_zero_pct"], errors="coerce")
    qm["submitter_full_pct"] = pd.to_numeric(qm["submitter_full_pct"], errors="coerce")
    qm["submitters"] = pd.to_numeric(qm["submitters"], errors="coerce")
    palette = {
        "Bimodal": "#B279A2",
        "Floor": "#E45756",
        "Ceiling": "#54A24B",
        "Healthy spread": "#4C78A8",
        "Mixed": "#9D9DA1",
    }
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for label, sub in qm.groupby("distribution_shape"):
        ax.scatter(
            sub["submitter_zero_pct"],
            sub["submitter_full_pct"],
            s=sub["submitters"].clip(lower=5) * 1.5,
            alpha=0.75,
            label=label,
            color=palette.get(label, "#9D9DA1"),
            edgecolor="white",
            linewidth=0.4,
        )
    ax.axvline(70, color="#E45756", linestyle="--", alpha=0.35)
    ax.axhline(80, color="#54A24B", linestyle="--", alpha=0.35)
    ax.set_xlabel("% of submitters scoring zero")
    ax.set_ylabel("% of submitters scoring full marks")
    ax.set_title("Per-question Submitter Score Profiles")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "question_score_profile_map.png", dpi=160)
    plt.close(fig)

    # 5) Distribution-shape counts.
    shape_counts = (
        question_metrics["distribution_shape"]
        .value_counts()
        .rename_axis("distribution_shape")
        .reset_index(name="questions")
    )
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(shape_counts["distribution_shape"], shape_counts["questions"], color="#4C78A8")
    ax.set_title("Question Distribution Shape Flags")
    ax.set_ylabel("Questions")
    ax.tick_params(axis="x", rotation=20)
    for i, row in shape_counts.reset_index(drop=True).iterrows():
        ax.text(i, row["questions"], int(row["questions"]), ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "question_distribution_shape_counts.png", dpi=160)
    plt.close(fig)

    # 6) Per-case pass rate distributions.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, scope, color in zip(axes, ["public", "private"], ["#4C78A8", "#F58518"]):
        sub = test_case_rates[test_case_rates["test_scope"] == scope].copy()
        sub["pass_rate_pct"] = pd.to_numeric(sub["pass_rate_pct"], errors="coerce")
        ax.hist(sub["pass_rate_pct"].dropna(), bins=list(range(0, 105, 5)), color=color, alpha=0.9)
        ax.set_title(f"{scope.title()} Test Cases")
        ax.set_xlabel("Pass rate (%)")
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Question-test cases")
    fig.suptitle("Per-test-case Pass Rate Distributions")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "test_case_pass_rate_distributions.png", dpi=160)
    plt.close(fig)

    # 7) Slot-order submission/effective score trends on multi-slot days.
    ss = slot_summary.copy()
    ss["submission_rate_pct"] = pd.to_numeric(ss["submission_rate_pct"], errors="coerce")
    ss["weighted_effective_mean_score"] = pd.to_numeric(ss["weighted_effective_mean_score"], errors="coerce")
    multi = ss.groupby(["term", "wave", "exam_date"])["slot_order_in_day"].transform("max") >= 2
    ss = ss[multi].copy()
    if not ss.empty:
        ss["series"] = ss["term"].astype(str) + " " + ss["wave"].astype(str) + " " + ss["exam_date"].astype(str)
        fig, axes = plt.subplots(2, 1, figsize=(9.5, 7.5), sharex=True)
        for series, sub in ss.groupby("series"):
            sub = sub.sort_values("slot_order_in_day")
            axes[0].plot(sub["slot_order_in_day"], sub["submission_rate_pct"], marker="o", label=series)
            axes[1].plot(sub["slot_order_in_day"], sub["weighted_effective_mean_score"], marker="o", label=series)
        axes[0].set_ylabel("Submission rate (%)")
        axes[0].set_title("Within-day Slot Trends (Days with 2+ Slots)")
        axes[0].grid(alpha=0.2)
        axes[1].set_ylabel("Effective mean score")
        axes[1].set_xlabel("Slot order within wave/day")
        axes[1].grid(alpha=0.2)
        axes[0].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "slot_order_trends_multi_slot_days.png", dpi=160)
        plt.close(fig)


def build_findings_markdown(conn: duckdb.DuckDBPyConnection) -> None:
    print("[8/8] Writing findings summary markdown...")
    outcome = pd.read_csv(OUT_DIR / "outcome_category_summary.csv")
    non_submit_summary = pd.read_csv(OUT_DIR / "non_submission_summary.csv")
    non_submit_profiles = pd.read_csv(OUT_DIR / "non_submission_profiles.csv")
    question_metrics = pd.read_csv(OUT_DIR / "question_score_metrics_with_case_pass_rates.csv")
    term_wave = pd.read_csv(OUT_DIR / "term_wave_score_summary.csv")
    slot_summary = pd.read_csv(OUT_DIR / "slot_order_score_summary.csv")
    reused_summary_path = OUT_DIR / "reused_question_summary.csv"
    reused_summary = pd.read_csv(reused_summary_path) if reused_summary_path.exists() else pd.DataFrame()

    outcome_map = {r["outcome_category"]: r for _, r in outcome.iterrows()}
    ns_total = int(float(outcome_map["Active, never submitted"]["rows"]))
    ns_pct = float(outcome_map["Active, never submitted"]["pct_rows"])
    full_pct = float(outcome_map["Full pass"]["pct_rows"])
    partial_pct = float(outcome_map["Partial pass"]["pct_rows"])
    zero_pct = float(outcome_map["Submitted, zero"]["pct_rows"])

    ns_profile = non_submit_profiles.copy()
    ns_profile["test_run_events"] = pd.to_numeric(ns_profile["test_run_events"], errors="coerce").fillna(0)
    ns_profile["active_time_seconds"] = pd.to_numeric(ns_profile["active_time_seconds"], errors="coerce").fillna(0)
    ns_profile["had_any_public_pass"] = ns_profile["had_any_public_pass"].astype(str).str.lower().eq("true")
    ns_profile["had_all_public_cases_passed_in_test_run"] = (
        ns_profile["had_all_public_cases_passed_in_test_run"].astype(str).str.lower().eq("true")
    )
    ns_profile["last_is_parseable"] = ns_profile["last_is_parseable"].astype(str).str.lower().eq("true")
    ns_profile["substantial_activity_all_failing_gt10"] = (
        ns_profile["substantial_activity_all_failing_gt10"].astype(str).str.lower().eq("true")
    )

    test_run_quantiles = ns_profile["test_run_events"].quantile([0.5, 0.9, 0.99]).to_dict()
    active_min_quantiles = (ns_profile["active_time_seconds"] / 60.0).quantile([0.5, 0.9, 0.99]).to_dict()
    parseable_pct = 100.0 * ns_profile["last_is_parseable"].mean()
    public_pass_pct = 100.0 * ns_profile["had_any_public_pass"].mean()
    public_all_pass_pct = 100.0 * ns_profile["had_all_public_cases_passed_in_test_run"].mean()
    thrash_pct = 100.0 * ns_profile["substantial_activity_all_failing_gt10"].mean()

    q = question_metrics.copy()
    q["submitters"] = pd.to_numeric(q["submitters"], errors="coerce").fillna(0)
    q["submission_rate_pct"] = pd.to_numeric(q["submission_rate_pct"], errors="coerce")
    q["non_submission_rate_pct"] = pd.to_numeric(q["non_submission_rate_pct"], errors="coerce")
    q["all_assigned_mean_score"] = pd.to_numeric(q["all_assigned_mean_score"], errors="coerce")
    q["submitter_mean_score"] = pd.to_numeric(q["submitter_mean_score"], errors="coerce")
    q["public_avg_case_pass_rate_pct"] = pd.to_numeric(q["public_avg_case_pass_rate_pct"], errors="coerce")
    q["private_avg_case_pass_rate_pct"] = pd.to_numeric(q["private_avg_case_pass_rate_pct"], errors="coerce")

    shape_counts = q["distribution_shape"].value_counts().to_dict()
    top_non_submit_questions = q.sort_values(["non_submission_rate_pct", "assigned_students"], ascending=[False, False]).head(5)
    top_floor = q[q["distribution_shape"] == "Floor"].sort_values(["submitters", "submitter_zero_pct"], ascending=[False, False]).head(5)
    top_ceiling = q[q["distribution_shape"] == "Ceiling"].sort_values(["submitters", "submitter_full_pct"], ascending=[False, False]).head(5)
    top_bimodal = q[q["distribution_shape"] == "Bimodal"].sort_values(["submitters"], ascending=[False]).head(5)

    tw = term_wave.copy()
    tw["submission_rate_pct"] = pd.to_numeric(tw["submission_rate_pct"], errors="coerce")
    tw["weighted_effective_mean_score"] = pd.to_numeric(tw["weighted_effective_mean_score"], errors="coerce")
    wave_pairs: list[str] = []
    for term, sub in tw.groupby("term"):
        w1 = sub[sub["wave"] == "wave1"]
        w2 = sub[sub["wave"] == "wave2"]
        if not w1.empty and not w2.empty:
            wave_pairs.append(
                (
                    f"- {term}: Wave 1 submission rate {w1.iloc[0]['submission_rate_pct']:.2f}% vs "
                    f"Wave 2 {w2.iloc[0]['submission_rate_pct']:.2f}% "
                    f"(delta {w2.iloc[0]['submission_rate_pct'] - w1.iloc[0]['submission_rate_pct']:+.2f} pp); "
                    f"effective mean {w1.iloc[0]['weighted_effective_mean_score']:.2f} vs "
                    f"{w2.iloc[0]['weighted_effective_mean_score']:.2f}"
                )
            )

    slot = slot_summary.copy()
    slot["submission_rate_pct"] = pd.to_numeric(slot["submission_rate_pct"], errors="coerce")
    slot["weighted_effective_mean_score"] = pd.to_numeric(slot["weighted_effective_mean_score"], errors="coerce")
    slot["exam_date"] = slot["exam_date"].astype(str)
    slot_counts = slot.groupby(["term", "wave", "exam_date"])["slot_order_in_day"].max().reset_index()
    multi_slot_days = slot_counts[slot_counts["slot_order_in_day"] >= 2]
    slot_lines: list[str] = []
    for _, row in multi_slot_days.sort_values(["term", "wave", "exam_date"]).iterrows():
        sub = slot[
            (slot["term"] == row["term"])
            & (slot["wave"] == row["wave"])
            & (slot["exam_date"] == row["exam_date"])
        ].sort_values("slot_order_in_day")
        if len(sub) < 2:
            continue
        first = sub.iloc[0]
        last = sub.iloc[-1]
        slot_lines.append(
            (
                f"- {row['term']} {row['wave']} {row['exam_date']}: "
                f"slot {int(first['slot_order_in_day'])} -> {int(last['slot_order_in_day'])} "
                f"submission rate {first['submission_rate_pct']:.2f}% -> {last['submission_rate_pct']:.2f}% "
                f"(delta {last['submission_rate_pct'] - first['submission_rate_pct']:+.2f} pp), "
                f"effective mean {first['weighted_effective_mean_score']:.2f} -> {last['weighted_effective_mean_score']:.2f}"
            )
        )

    reused_lines: list[str] = []
    if not reused_summary.empty:
        top_reused = reused_summary.sort_values(
            ["distinct_terms", "submission_rate_range_pct", "all_assigned_mean_range"],
            ascending=[False, False, False],
        ).head(5)
        for _, row in top_reused.iterrows():
            reused_lines.append(
                (
                    f"- {row['question_title']}: {int(row['distinct_terms'])} terms, "
                    f"submission-rate range {row['submission_rate_range_pct']:.2f} pp, "
                    f"effective-mean range {row['all_assigned_mean_range']:.2f}"
                )
            )

    def fmt_top(df: pd.DataFrame, label: str, score_col: str) -> list[str]:
        if df.empty:
            return [f"- No {label.lower()} questions matched the threshold."]
        out: list[str] = []
        for _, r in df.head(5).iterrows():
            out.append(
                f"- {r['namespace']} Q{int(r['problem_id'])} ({r['question_title']}): "
                f"submitters={int(r['submitters'])}, submission_rate={r['submission_rate_pct']:.2f}%, "
                f"{score_col}={r[score_col]:.2f}"
            )
        return out

    findings = textwrap.dedent(
        f"""
        ## Generated Findings (from `analysis/score_failure_profiles/`)

        ### Headline outcomes

        - `Active, never submitted` is **{ns_total:,} / 151,778 ({ns_pct:.2f}%)** rows.
        - Submission outcomes (all student-question rows): **Full pass {full_pct:.2f}%**, **Partial pass {partial_pct:.2f}%**, **Submitted zero {zero_pct:.2f}%**.
        - `No activity` rows after Step 0 filtering: **0**.

        ### Non-submission problem (active but never submitted)

        - Had at least one public `test_run` with >=1 passing test case: **{public_pass_pct:.2f}%** of non-submitters.
        - Had at least one public `test_run` with all public tests passing: **{public_all_pass_pct:.2f}%** of non-submitters.
        - Substantial activity (>10 test runs) with no public pass ("thrashing/stuck" proxy): **{thrash_pct:.2f}%** of non-submitters.
        - Last snapshot parseable rate (timeline `is_parseable` on final observed event): **{parseable_pct:.2f}%**.
        - Non-submitter test-run count quantiles: median **{test_run_quantiles.get(0.5, float('nan')):.0f}**, p90 **{test_run_quantiles.get(0.9, float('nan')):.0f}**, p99 **{test_run_quantiles.get(0.99, float('nan')):.0f}**.
        - Non-submitter active-time span quantiles (minutes, first-to-last observed event): median **{active_min_quantiles.get(0.5, float('nan')):.1f}**, p90 **{active_min_quantiles.get(0.9, float('nan')):.1f}**, p99 **{active_min_quantiles.get(0.99, float('nan')):.1f}**.

        ### Question distribution shapes (submitter score distributions)

        - Shape counts: {", ".join(f"{k}={int(v)}" for k, v in shape_counts.items())}
        - Thresholds used:
          - `Ceiling`: >80% of submitters full marks
          - `Floor`: >70% of submitters zero
          - `Bimodal`: >=30% zero, >=30% full, <=20% partial (submitters >=20)
          - `Healthy spread`: partial between 30% and 70%, with no dominant zero/full mass (submitters >=20)

        Top high non-submission questions:
        {chr(10).join(fmt_top(top_non_submit_questions, "high non-submission", "non_submission_rate_pct"))}

        Top floor questions:
        {chr(10).join(fmt_top(top_floor, "floor", "submitter_zero_pct"))}

        Top ceiling questions:
        {chr(10).join(fmt_top(top_ceiling, "ceiling", "submitter_full_pct"))}

        Top bimodal questions:
        {chr(10).join(fmt_top(top_bimodal, "bimodal", "submitter_mean_score"))}

        ### Wave / slot comparisons

        {chr(10).join(wave_pairs) if wave_pairs else "- No term has both Wave 1 and Wave 2 in the current schedule snapshot."}

        Within-day slot trends (for days with multiple slots in a wave):
        {chr(10).join(slot_lines) if slot_lines else "- No multi-slot wave days found."}

        ### Reused question comparisons across terms

        {chr(10).join(reused_lines) if reused_lines else "- No repeated question-title+text groups found across multiple terms."}
        """
    ).strip() + "\n"

    (OUT_DIR / "findings.md").write_text(findings, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing outputs to {OUT_DIR}")
    conn = make_conn()
    try:
        setup_views(conn)
        build_outcome_tables(conn)
        build_non_submission_profiles(conn)
        build_question_metrics(conn)
        build_test_case_pass_rates(conn)
        build_wave_slot_and_reuse_tables(conn)
        build_question_and_non_submit_rate_breakdowns(conn)
        plot_outputs()
        build_findings_markdown(conn)
    finally:
        conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
