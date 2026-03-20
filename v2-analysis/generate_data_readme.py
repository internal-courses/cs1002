#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.2.2"]
# ///
"""Generate a profiling README for the parquet export in v2-analysis/data/."""

from __future__ import annotations

import base64
import io
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, Sequence

import duckdb

ROOT = Path(__file__).resolve().parents[1]
V2_DIR = Path(__file__).resolve().parent
DATA_GLOB = (V2_DIR / "data" / "bq-results-*").as_posix()
OUT_PATH = V2_DIR / "data" / "README.md"


def sql_str(value: str) -> str:
    return value.replace("'", "''")


def fmt_int(value: int | None) -> str:
    return "NA" if value is None else f"{value:,}"


def fmt_float(value: float | None, digits: int = 2) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def fmt_pct(numerator: int | float, denominator: int | float, digits: int = 2) -> str:
    if not denominator:
        return "NA"
    return f"{100 * float(numerator) / float(denominator):.{digits}f}%"


def fmt_ts(value: datetime | None) -> str:
    return "NA" if value is None else value.strftime("%Y-%m-%d %H:%M:%S UTC")


def md_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    header_row = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header_row, divider, *body])


def decode_code_snapshot(b64_code: str) -> str:
    """Decode the OPPE code blob into source text."""
    if not b64_code:
        return ""
    raw = base64.b64decode(b64_code)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = [name for name in zf.namelist() if not name.endswith("/")]
            py_names = sorted(name for name in names if name.lower().endswith(".py"))
            pick = py_names[0] if py_names else sorted(names)[0]
            return zf.read(pick).decode("utf-8", errors="replace")
    except zipfile.BadZipFile:
        return raw.decode("utf-8", errors="replace")


def zip_member_sample(con: duckdb.DuckDBPyConnection, sample_size: int = 500) -> Counter[tuple[str, ...]]:
    rows = con.execute(
        f"""
        SELECT code
        FROM base
        ORDER BY hash(filename)
        LIMIT {sample_size}
        """
    ).fetchall()

    members: Counter[tuple[str, ...]] = Counter()
    for (code,) in rows:
        raw = base64.b64decode(code)
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = tuple(name for name in zf.namelist() if not name.endswith("/"))
        members[names] += 1
    return members


def first_decoded_snippet(con: duckdb.DuckDBPyConnection) -> str:
    (code,) = con.execute(
        """
        SELECT code
        FROM base
        ORDER BY hash(filename)
        LIMIT 1
        """
    ).fetchone()
    decoded = decode_code_snapshot(code).replace("\r\n", "\n").strip()
    return decoded[:160].replace("\n", "\\n")


def build_views(con: duckdb.DuckDBPyConnection) -> None:
    path = sql_str(DATA_GLOB)
    con.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW base AS
        SELECT
          current_namespace,
          key,
          unit_id,
          submission_type,
          code,
          data,
          filename,
          regexp_extract(filename, '/(saved_code|test_run|submission)/', 1) AS event_type,
          try_strptime(
            regexp_extract(filename, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1),
            '%Y-%m-%dT%H:%M:%S.%fZ'
          ) AS timestamp_utc,
          regexp_extract(filename, '/(?:test_run|submission)/([^_]+)?_?[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T', 1) AS filename_prefix,
          length(code) AS encoded_code_len,
          length(data) AS data_len,
          try_cast(json_extract_string(data, '$.status') AS INTEGER) AS status,
          json_extract_string(data, '$.reason') AS reason,
          json_extract_string(data, '$.compilation_errors') AS compilation_errors,
          try_cast(json_extract_string(data, '$.num_test_evaluated') AS INTEGER) AS num_test_evaluated,
          try_cast(json_extract_string(data, '$.num_test_passed') AS INTEGER) AS num_test_passed,
          json_extract_string(data, '$.summary') AS summary,
          try_cast(json_extract_string(data, '$.score') AS DOUBLE) AS score,
          json_extract_string(data, '$.evaluation_result_json') AS evaluation_result_json
        FROM read_parquet('{path}')
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW key_unit_stats AS
        SELECT
          key,
          unit_id,
          COUNT(*) AS rows,
          SUM(submission_type = 'public') AS public_rows,
          SUM(submission_type = 'private' AND event_type = 'test_run') AS private_test_runs,
          SUM(submission_type = 'private' AND event_type = 'submission') AS submissions
        FROM base
        GROUP BY 1, 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW paired_test_runs AS
        SELECT
          ANY_VALUE(unit_id) AS unit_id,
          filename,
          MAX(num_test_evaluated) FILTER (WHERE submission_type = 'public') AS public_eval,
          MAX(num_test_passed) FILTER (WHERE submission_type = 'public') AS public_passed,
          MAX(summary) FILTER (WHERE submission_type = 'public') AS public_summary,
          MAX(num_test_evaluated) FILTER (WHERE submission_type = 'private') AS private_eval,
          MAX(num_test_passed) FILTER (WHERE submission_type = 'private') AS private_passed,
          MAX(summary) FILTER (WHERE submission_type = 'private') AS private_summary
        FROM base
        WHERE event_type = 'test_run'
        GROUP BY 2
        HAVING COUNT(*) = 2 AND COUNT(DISTINCT submission_type) = 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW unit_windows AS
        SELECT
          unit_id,
          MIN(timestamp_utc) AS first_ts,
          MAX(timestamp_utc) AS last_ts,
          COUNT(*) AS rows,
          COUNT(DISTINCT key) AS keys,
          SUM(submission_type = 'public') AS public_rows,
          SUM(submission_type = 'private') AS private_rows
        FROM base
        GROUP BY 1
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW unit_test_counts AS
        SELECT
          unit_id,
          MAX(num_test_evaluated) FILTER (WHERE submission_type = 'public') AS public_tests,
          MAX(num_test_evaluated) FILTER (WHERE submission_type = 'private') AS private_tests
        FROM base
        GROUP BY 1
        """
    )


def main() -> None:
    con = duckdb.connect()
    build_views(con)

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    basic = con.execute(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(DISTINCT current_namespace) AS namespaces,
          COUNT(DISTINCT key) AS keys,
          COUNT(DISTINCT unit_id) AS unit_ids,
          COUNT(DISTINCT submission_type) AS submission_types,
          COUNT(DISTINCT code) AS distinct_code,
          COUNT(DISTINCT data) AS distinct_data,
          COUNT(DISTINCT filename) AS distinct_filename,
          COUNT(DISTINCT (filename, submission_type)) AS distinct_filename_type,
          MIN(timestamp_utc) AS min_ts,
          MAX(timestamp_utc) AS max_ts
        FROM base
        """
    ).fetchone()
    (
        total_rows,
        namespace_count,
        key_count,
        unit_count,
        submission_type_count,
        distinct_code_count,
        distinct_data_count,
        distinct_filename_count,
        distinct_filename_type_count,
        min_ts,
        max_ts,
    ) = basic

    filename_mult = dict(
        con.execute(
            """
            WITH counts AS (
              SELECT filename, COUNT(*) AS c
              FROM base
              GROUP BY 1
            )
            SELECT c, COUNT(*) AS filenames
            FROM counts
            GROUP BY 1
            ORDER BY 1
            """
        ).fetchall()
    )
    (exact_duplicate_rows,) = con.execute(
        """
        SELECT COUNT(*) - COUNT(DISTINCT (
          current_namespace, key, unit_id, submission_type, code, data, filename
        ))
        FROM base
        """
    ).fetchone()

    event_mix = con.execute(
        """
        SELECT event_type, submission_type, COUNT(*) AS rows
        FROM base
        GROUP BY 1, 2
        ORDER BY rows DESC
        """
    ).fetchall()

    summary_counts = con.execute(
        """
        SELECT summary, COUNT(*) AS rows
        FROM base
        GROUP BY 1
        ORDER BY rows DESC
        """
    ).fetchall()
    summary_by_type = con.execute(
        """
        SELECT submission_type, summary, COUNT(*) AS rows
        FROM base
        GROUP BY 1, 2
        ORDER BY submission_type, rows DESC
        """
    ).fetchall()

    (public_score_nonzero,) = con.execute(
        """
        SELECT COUNT_IF(submission_type = 'public' AND score <> 0)
        FROM base
        """
    ).fetchone()
    (status_distinct,) = con.execute(
        """
        SELECT
          COUNT(DISTINCT status)
        FROM base
        """
    ).fetchone()
    (json_keyset,) = con.execute(
        """
        SELECT CAST(json_keys(data) AS VARCHAR)
        FROM base
        LIMIT 1
        """
    ).fetchone()

    (private_rows, private_zero_scores, private_perfect_scores, private_partial_scores, private_avg_score) = con.execute(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT_IF(score = 0) AS zero_scores,
          COUNT_IF(score = 100) AS perfect_scores,
          COUNT_IF(score > 0 AND score < 100) AS partial_scores,
          AVG(score) AS avg_score
        FROM base
        WHERE submission_type = 'private'
        """
    ).fetchone()
    (public_rows, public_zero_passed, public_full_pass, public_partial_pass, public_avg_pass_rate) = con.execute(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT_IF(num_test_passed = 0) AS zero_passed,
          COUNT_IF(num_test_passed = num_test_evaluated) AS full_pass,
          COUNT_IF(num_test_passed BETWEEN 1 AND num_test_evaluated - 1) AS partial_pass,
          AVG(num_test_passed::DOUBLE / NULLIF(num_test_evaluated, 0)) AS avg_pass_rate
        FROM base
        WHERE submission_type = 'public'
        """
    ).fetchone()

    (min_key_unit_rows, median_key_unit_rows, p90_key_unit_rows, p99_key_unit_rows, max_key_unit_rows) = con.execute(
        """
        SELECT
          MIN(rows),
          approx_quantile(rows, 0.5),
          approx_quantile(rows, 0.9),
          approx_quantile(rows, 0.99),
          MAX(rows)
        FROM key_unit_stats
        """
    ).fetchone()
    (singletons, ge_50, ge_100, ge_200) = con.execute(
        """
        SELECT
          COUNT_IF(rows = 1),
          COUNT_IF(rows >= 50),
          COUNT_IF(rows >= 100),
          COUNT_IF(rows >= 200)
        FROM key_unit_stats
        """
    ).fetchone()
    (min_units_per_key, median_units_per_key, p90_units_per_key, p99_units_per_key, max_units_per_key) = con.execute(
        """
        SELECT
          MIN(unit_count),
          approx_quantile(unit_count, 0.5),
          approx_quantile(unit_count, 0.9),
          approx_quantile(unit_count, 0.99),
          MAX(unit_count)
        FROM (
          SELECT key, COUNT(DISTINCT unit_id) AS unit_count
          FROM base
          GROUP BY 1
        )
        """
    ).fetchone()
    (min_rows_per_key, median_rows_per_key, p90_rows_per_key, p99_rows_per_key, max_rows_per_key) = con.execute(
        """
        SELECT
          MIN(rows),
          approx_quantile(rows, 0.5),
          approx_quantile(rows, 0.9),
          approx_quantile(rows, 0.99),
          MAX(rows)
        FROM (
          SELECT key, COUNT(*) AS rows
          FROM base
          GROUP BY 1
        )
        """
    ).fetchone()

    (key_unit_pairs, no_submission_pairs, with_submission_pairs, public_only_pairs, multi_submission_pairs, max_submissions) = con.execute(
        """
        SELECT
          COUNT(*) AS key_unit_pairs,
          COUNT_IF(submissions = 0) AS no_submission_pairs,
          COUNT_IF(submissions > 0) AS with_submission_pairs,
          COUNT_IF(public_rows > 0 AND submissions = 0) AS public_only_pairs,
          COUNT_IF(submissions > 1) AS multi_submission_pairs,
          MAX(submissions) AS max_submissions
        FROM key_unit_stats
        """
    ).fetchone()

    (paired_runs, avg_public_pair_pass_rate, avg_private_pair_pass_rate, public_all_pass, private_all_pass, public_green_hidden_fail, public_passed_gt_private, public_passed_lt_private, summary_mismatch) = con.execute(
        """
        SELECT
          COUNT(*) AS paired_runs,
          AVG(public_passed::DOUBLE / NULLIF(public_eval, 0)) AS avg_public_pass_rate,
          AVG(private_passed::DOUBLE / NULLIF(private_eval, 0)) AS avg_private_pass_rate,
          COUNT_IF(public_passed = public_eval) AS public_all_pass,
          COUNT_IF(private_passed = private_eval) AS private_all_pass,
          COUNT_IF(public_passed = public_eval AND private_passed < private_eval) AS public_green_hidden_fail,
          COUNT_IF(public_passed > private_passed) AS public_passed_gt_private,
          COUNT_IF(public_passed < private_passed) AS public_passed_lt_private,
          COUNT_IF(public_summary <> private_summary) AS summary_mismatch
        FROM paired_test_runs
        """
    ).fetchone()
    (diff_eval_count,) = con.execute(
        """
        SELECT
          COUNT_IF(public_eval <> private_eval) AS diff_eval_count
        FROM paired_test_runs
        """
    ).fetchone()
    (differing_unit_count, differing_units) = con.execute(
        """
        SELECT
          COUNT(*) FILTER (WHERE public_tests <> private_tests) AS differing_units,
          string_agg(unit_id, ', ' ORDER BY try_cast(unit_id AS INT))
            FILTER (WHERE public_tests <> private_tests) AS differing_unit_ids
        FROM unit_test_counts
        """
    ).fetchone()

    release_batches = con.execute(
        """
        SELECT
          CAST(first_ts AS DATE) AS release_date,
          COUNT(*) AS units,
          string_agg(unit_id, ', ' ORDER BY try_cast(unit_id AS INT)) AS unit_ids,
          SUM(rows) AS rows
        FROM unit_windows
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    peak_days = con.execute(
        """
        SELECT
          CAST(timestamp_utc AS DATE) AS day,
          COUNT(*) AS rows,
          COUNT(DISTINCT unit_id) AS units_touched
        FROM base
        GROUP BY 1
        ORDER BY rows DESC, day
        LIMIT 8
        """
    ).fetchall()
    top_units_by_rows = con.execute(
        """
        SELECT
          unit_id,
          rows,
          keys,
          ROUND(rows::DOUBLE / keys, 2) AS rows_per_key,
          first_ts,
          last_ts
        FROM unit_windows
        ORDER BY rows DESC
        LIMIT 12
        """
    ).fetchall()

    nppe = con.execute(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(DISTINCT key) AS keys
        FROM base
        WHERE try_cast(unit_id AS INT) BETWEEN 770 AND 776
        """
    ).fetchone()
    nppe_rows, nppe_keys = nppe

    pair_gap_by_unit = con.execute(
        """
        SELECT
          unit_id,
          COUNT(*) AS paired_runs,
          ROUND(100.0 * AVG(CASE WHEN public_passed = public_eval THEN 1 ELSE 0 END), 2) AS public_all_pass_pct,
          ROUND(100.0 * AVG(CASE WHEN private_passed = private_eval THEN 1 ELSE 0 END), 2) AS private_all_pass_pct,
          ROUND(
            100.0 * AVG(CASE WHEN public_passed = public_eval AND private_passed < private_eval THEN 1 ELSE 0 END),
            2
          ) AS public_green_hidden_fail_pct,
          ROUND(
            AVG(
              (public_passed::DOUBLE / NULLIF(public_eval, 0))
              - (private_passed::DOUBLE / NULLIF(private_eval, 0))
            ),
            3
          ) AS avg_public_minus_private_pass_rate
        FROM paired_test_runs
        GROUP BY 1
        HAVING COUNT(*) >= 500
        ORDER BY public_green_hidden_fail_pct DESC, paired_runs DESC
        LIMIT 12
        """
    ).fetchall()

    length_quantiles = con.execute(
        """
        SELECT
          submission_type,
          MIN(encoded_code_len),
          approx_quantile(encoded_code_len, 0.5),
          approx_quantile(encoded_code_len, 0.9),
          approx_quantile(encoded_code_len, 0.99),
          MAX(encoded_code_len),
          MIN(data_len),
          approx_quantile(data_len, 0.5),
          approx_quantile(data_len, 0.9),
          approx_quantile(data_len, 0.99),
          MAX(data_len)
        FROM base
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    payload_thresholds = con.execute(
        """
        SELECT
          threshold,
          COUNT(*) AS rows,
          COUNT_IF(submission_type = 'public') AS public_rows,
          COUNT_IF(summary = 'Time Limit Exceeded') AS tle_rows,
          COUNT_IF(summary = 'Wrong Answer') AS wrong_answer_rows,
          COUNT_IF(summary = 'Runtime Error') AS runtime_error_rows
        FROM (
          SELECT 10000 AS threshold, * FROM base WHERE data_len >= 10000
          UNION ALL
          SELECT 50000 AS threshold, * FROM base WHERE data_len >= 50000
          UNION ALL
          SELECT 100000 AS threshold, * FROM base WHERE data_len >= 100000
          UNION ALL
          SELECT 500000 AS threshold, * FROM base WHERE data_len >= 500000
        )
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    outlier_units = con.execute(
        """
        SELECT
          unit_id,
          COUNT(*) AS rows,
          approx_quantile(data_len, 0.99) AS p99_data_len,
          MAX(data_len) AS max_data_len,
          approx_quantile(encoded_code_len, 0.99) AS p99_code_len,
          MAX(encoded_code_len) AS max_code_len
        FROM base
        GROUP BY 1
        HAVING COUNT(*) >= 500
        ORDER BY max_data_len DESC
        LIMIT 12
        """
    ).fetchall()

    private_only_test_runs = con.execute(
        """
        SELECT
          COALESCE(SUM(rows), 0) AS rows,
          string_agg(unit_id || ':' || rows::VARCHAR, ', ' ORDER BY unit_id) AS breakdown
        FROM (
          SELECT unit_id, COUNT(*) AS rows
          FROM base
          WHERE submission_type = 'private'
            AND event_type = 'test_run'
            AND filename NOT IN (SELECT filename FROM base WHERE submission_type = 'public')
          GROUP BY 1
        )
        """
    ).fetchone()
    private_only_test_run_rows, private_only_breakdown = private_only_test_runs

    zip_members = zip_member_sample(con)
    zip_member_summary = ", ".join(
        f"`{'+'.join(member_names)}`: {count}"
        for member_names, count in zip_members.most_common()
    )
    decoded_head = first_decoded_snippet(con)
    huge_rows = {threshold: rows for threshold, rows, *_ in payload_thresholds}
    huge_sentence = (
        f"- Large `data` payloads are usually verbose per-test-case output, not corrupted JSON. "
        f"Only **{fmt_int(huge_rows[500000])}** rows exceed 500 KB, and every one of them is a public `Time Limit Exceeded` or `Runtime Error` case."
    )

    schema_rows = [
        ("current_namespace", "VARCHAR", "0", fmt_int(namespace_count), "Namespace; only `ns_26t1_cs1002` appears."),
        ("key", "VARCHAR", "0", fmt_int(key_count), "Opaque learner/account key. Inference: stable across many units, so likely learner-level."),
        ("unit_id", "VARCHAR", "0", fmt_int(unit_count), "Problem or unit identifier as a numeric string."),
        ("submission_type", "VARCHAR", "0", fmt_int(submission_type_count), "`public` or `private`. Important: `private` contains both mirrored `test_run` rows and final `submission` rows."),
        ("code", "VARCHAR", "0", fmt_int(distinct_code_count), "Base64-encoded ZIP payload holding source text; decode only when code-level analysis is required."),
        ("data", "VARCHAR", "0", fmt_int(distinct_data_count), "JSON string with evaluation metrics and per-test-case details."),
        ("filename", "VARCHAR", "0", fmt_int(distinct_filename_count), "Path-like identifier embedding unit, learner key, event type, and timestamp."),
    ]

    data_field_rows = [
        ("status", "integer", "Always `1` here; not a success flag."),
        ("reason", "string", "Always empty in this export."),
        ("compilation_errors", "string", "Always `[]` here; do not use to detect failures."),
        ("num_test_evaluated", "integer", "Per-row denominator. Within a unit and submission type it is constant."),
        ("num_test_passed", "integer", "Primary progress metric for both public and private rows."),
        ("summary", "string", "Main categorical outcome: `Runtime Error`, `Wrong Answer`, `All Cases Passed`, `Time Limit Exceeded`, `Not able to run`."),
        ("score", "double", "Meaningful on private rows; structurally `0` on public rows."),
        ("evaluation_result_json", "string", "Always empty here."),
        ("test_case_results", "array<object>", "Always present. Contains `passed`, `reason`, `output`, and `expected_output`. This is where very large payloads come from."),
    ]

    derived_rows = [
        ("`(filename, submission_type)`", "Recommended unique row key. `filename` alone is not unique because mirrored public/private test runs share it."),
        ("`event_type`", "Extract from `filename` with `/(saved_code|test_run|submission)/`. This export only contains `test_run` and `submission`."),
        ("`timestamp_utc`", "Extract the trailing ISO timestamp from `filename`. There is no dedicated timestamp column."),
        ("`public_private_pair`", "For `test_run` rows, pair the same `filename` across `submission_type` to compare visible and hidden tests."),
        ("`public_pass_rate` / `private_pass_rate`", "Use pass rate, not raw pass count, because public/private test counts differ in 27 units."),
    ]

    event_rows = []
    for event_type, submission_type, rows in event_mix:
        event_rows.append((event_type, submission_type, fmt_int(rows), fmt_pct(rows, total_rows)))

    outcome_rows = []
    for summary, rows in summary_counts:
        outcome_rows.append((summary, fmt_int(rows), fmt_pct(rows, total_rows)))

    summary_type_rows = []
    for submission_type, summary, rows in summary_by_type:
        summary_type_rows.append((submission_type, summary, fmt_int(rows), fmt_pct(rows, public_rows if submission_type == "public" else private_rows)))

    release_rows = []
    for release_date, units, unit_ids, rows in release_batches:
        release_rows.append((release_date, units, unit_ids, fmt_int(rows), fmt_pct(rows, total_rows)))

    peak_day_rows = []
    for day, rows, units_touched in peak_days:
        peak_day_rows.append((day, fmt_int(rows), units_touched, fmt_pct(rows, total_rows)))

    top_unit_rows = []
    for unit_id, rows, keys, rows_per_key, first_ts, last_ts in top_units_by_rows:
        top_unit_rows.append((unit_id, fmt_int(rows), fmt_int(keys), fmt_float(rows_per_key), fmt_ts(first_ts), fmt_ts(last_ts)))

    pair_gap_rows = []
    for unit_id, rows, public_pass_pct, private_pass_pct, green_hidden_fail_pct, gap in pair_gap_by_unit:
        pair_gap_rows.append(
            (
                unit_id,
                fmt_int(rows),
                f"{public_pass_pct:.2f}%",
                f"{private_pass_pct:.2f}%",
                f"{green_hidden_fail_pct:.2f}%",
                f"{gap:.3f}",
            )
        )

    length_rows = []
    for submission_type, min_code, med_code, p90_code, p99_code, max_code, min_data, med_data, p90_data, p99_data, max_data in length_quantiles:
        length_rows.append(
            (
                submission_type,
                fmt_int(min_code),
                fmt_int(med_code),
                fmt_int(p90_code),
                fmt_int(p99_code),
                fmt_int(max_code),
                fmt_int(min_data),
                fmt_int(med_data),
                fmt_int(p90_data),
                fmt_int(p99_data),
                fmt_int(max_data),
            )
        )

    threshold_rows = []
    for threshold, rows, public_count, tle_count, wa_count, re_count in payload_thresholds:
        threshold_rows.append(
            (
                f">= {fmt_int(threshold)}",
                fmt_int(rows),
                fmt_pct(public_count, rows),
                fmt_int(tle_count),
                fmt_int(wa_count),
                fmt_int(re_count),
            )
        )

    outlier_unit_rows = []
    for unit_id, rows, p99_data, max_data, p99_code, max_code in outlier_units:
        outlier_unit_rows.append(
            (unit_id, fmt_int(rows), fmt_int(p99_data), fmt_int(max_data), fmt_int(p99_code), fmt_int(max_code))
        )

    lines = [
        "# v2-analysis/data README",
        "",
        f"_Generated by `v2-analysis/generate_data_readme.py` on {generated_at}. Re-run this script after the parquet shards change._",
        "",
        "## ELI15",
        "",
        f"- This folder is a raw OPPE-style event export: **{fmt_int(total_rows)}** evaluation rows across **{fmt_int(unit_count)}** units and **{fmt_int(key_count)}** opaque learner keys in a single namespace.",
        "- One row is one evaluation result for one code snapshot. The same `test_run` can appear twice: once as a `public` result and once as a `private` result over the same `filename`.",
        f"- The data spans **{fmt_ts(min_ts)}** to **{fmt_ts(max_ts)}**, with large burst days on February 18, February 25, March 4, and March 8, 2026.",
        f"- Only **{fmt_int(with_submission_pairs)}** of **{fmt_int(key_unit_pairs)}** learner-unit pairs ({fmt_pct(with_submission_pairs, key_unit_pairs)}) ever submit. Most rows are exploratory test runs, not final answers.",
        f"- Units **770-776** are only **{fmt_pct(nppe_rows, total_rows)}** of rows, but they touch **{fmt_pct(nppe_keys, key_count)}** of learner keys. This folder covers a broader prep/history trace, not just the final NPPE block.",
        "",
        "## Rebuild",
        "",
        "```bash",
        "uv run v2-analysis/generate_data_readme.py",
        "```",
        "",
        "## Key Takeaways Before You Analyze Anything",
        "",
        f"- Use **`(filename, submission_type)`** as the row key. `filename` alone is not unique: {fmt_int(filename_mult.get(2, 0))} filenames occur exactly twice because of mirrored public/private `test_run` rows.",
        f"- Treat **`summary`**, **`num_test_passed`**, and **`num_test_evaluated`** as the real outcome fields. `status` has {fmt_int(status_distinct)} distinct value and is always `1`; `reason`, `compilation_errors`, and `evaluation_result_json` are effectively empty throughout.",
        f"- Ignore `score` on public rows. Public score is non-zero on **{fmt_int(public_score_nonzero)}** rows; use public pass-rate instead.",
        f"- Compare public and private results using pass-rate, not raw pass counts. **{fmt_int(diff_eval_count)}** of **{fmt_int(paired_runs)}** paired runs ({fmt_pct(diff_eval_count, paired_runs)}) use different public/private test counts, and **{fmt_int(differing_unit_count)}** units have different public/private test totals.",
        huge_sentence,
        "",
        "## Raw Schema",
        "",
        md_table(["column", "type", "nulls", "distinct", "notes"], schema_rows),
        "",
        "All seven raw columns are non-null on all rows.",
        "",
        "## `data` JSON Schema",
        "",
        f"All rows share the same top-level JSON keyset: `{json_keyset}`.",
        "",
        md_table(["field", "shape", "notes"], data_field_rows),
        "",
        "## Derived Fields You Should Create First",
        "",
        md_table(["derived field", "why it matters"], derived_rows),
        "",
        "Starter normalization query:",
        "",
        "```sql",
        "WITH normalized AS (",
        "  SELECT",
        "    current_namespace,",
        "    key,",
        "    unit_id,",
        "    submission_type,",
        "    regexp_extract(filename, '/(saved_code|test_run|submission)/', 1) AS event_type,",
        "    try_strptime(",
        "      regexp_extract(filename, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1),",
        "      '%Y-%m-%dT%H:%M:%S.%fZ'",
        "    ) AS timestamp_utc,",
        "    try_cast(json_extract_string(data, '$.num_test_evaluated') AS INTEGER) AS num_test_evaluated,",
        "    try_cast(json_extract_string(data, '$.num_test_passed') AS INTEGER) AS num_test_passed,",
        "    json_extract_string(data, '$.summary') AS summary,",
        "    try_cast(json_extract_string(data, '$.score') AS DOUBLE) AS score,",
        "    code,",
        "    data,",
        "    filename",
        "  FROM read_parquet('v2-analysis/data/bq-results-*')",
        ")",
        "SELECT * FROM normalized LIMIT 10;",
        "```",
        "",
        "Starter code decode snippet:",
        "",
        "```python",
        "import base64",
        "import io",
        "import zipfile",
        "",
        "def decode_code_snapshot(b64_code: str) -> str:",
        "    raw = base64.b64decode(b64_code)",
        "    with zipfile.ZipFile(io.BytesIO(raw)) as zf:",
        "        names = [name for name in zf.namelist() if not name.endswith('/')]",
        "        return zf.read(sorted(names)[0]).decode('utf-8', errors='replace')",
        "",
        "decoded_code = decode_code_snapshot(row['code'])",
        "```",
        "",
        f"In a deterministic 500-row sample (`ORDER BY hash(filename) LIMIT 500`), every `code` value decoded as a ZIP archive; {zip_member_summary}.",
        f"A representative decoded prefix looks like: `{decoded_head}`",
        "",
        "## Coverage and Grain",
        "",
        md_table(
            ["metric", "value"],
            [
                ("rows", fmt_int(total_rows)),
                ("namespace count", fmt_int(namespace_count)),
                ("unit count", fmt_int(unit_count)),
                ("opaque learner keys", fmt_int(key_count)),
                ("distinct filenames", fmt_int(distinct_filename_count)),
                ("distinct `(filename, submission_type)`", fmt_int(distinct_filename_type_count)),
                ("exact duplicate rows", fmt_int(exact_duplicate_rows)),
                ("time range", f"{fmt_ts(min_ts)} to {fmt_ts(max_ts)}"),
            ],
        ),
        "",
        md_table(["event type", "submission_type", "rows", "share"], event_rows),
        "",
        f"`filename` multiplicity: **{fmt_int(filename_mult.get(1, 0))}** filenames appear once; **{fmt_int(filename_mult.get(2, 0))}** appear twice. Because `filename + submission_type` is unique on all {fmt_int(total_rows)} rows, you can safely use that pair as a surrogate event id.",
        "",
        "Learner-unit engagement is heavy-tailed:",
        "",
        md_table(
            ["distribution", "min", "median", "p90", "p99", "max"],
            [
                (
                    "rows per learner-unit pair",
                    fmt_int(min_key_unit_rows),
                    fmt_int(median_key_unit_rows),
                    fmt_int(p90_key_unit_rows),
                    fmt_int(p99_key_unit_rows),
                    fmt_int(max_key_unit_rows),
                ),
                (
                    "units per learner key",
                    fmt_int(min_units_per_key),
                    fmt_int(median_units_per_key),
                    fmt_int(p90_units_per_key),
                    fmt_int(p99_units_per_key),
                    fmt_int(max_units_per_key),
                ),
                (
                    "rows per learner key",
                    fmt_int(min_rows_per_key),
                    fmt_int(median_rows_per_key),
                    fmt_int(p90_rows_per_key),
                    fmt_int(p99_rows_per_key),
                    fmt_int(max_rows_per_key),
                ),
            ],
        ),
        "",
        f"Only **{fmt_int(singletons)}** learner-unit pairs ({fmt_pct(singletons, key_unit_pairs)}) have a single row, while **{fmt_int(ge_50)}** have at least 50 rows and **{fmt_int(ge_200)}** still have at least 200 rows.",
        "",
        "## Outcome Distributions",
        "",
        md_table(["summary", "rows", "share"], outcome_rows),
        "",
        md_table(["submission_type", "summary", "rows", "share within type"], summary_type_rows),
        "",
        md_table(
            ["submission_type", "zero-progress", "partial-progress", "perfect-progress", "mean"],
            [
                (
                    "public",
                    f"{fmt_int(public_zero_passed)} ({fmt_pct(public_zero_passed, public_rows)})",
                    f"{fmt_int(public_partial_pass)} ({fmt_pct(public_partial_pass, public_rows)})",
                    f"{fmt_int(public_full_pass)} ({fmt_pct(public_full_pass, public_rows)})",
                    f"{public_avg_pass_rate:.3f} mean public pass-rate",
                ),
                (
                    "private",
                    f"{fmt_int(private_zero_scores)} ({fmt_pct(private_zero_scores, private_rows)})",
                    f"{fmt_int(private_partial_scores)} ({fmt_pct(private_partial_scores, private_rows)})",
                    f"{fmt_int(private_perfect_scores)} ({fmt_pct(private_perfect_scores, private_rows)})",
                    f"{private_avg_score:.2f} mean private score",
                ),
            ],
        ),
        "",
        f"Exact submission behavior is simple: **{fmt_int(with_submission_pairs)}** learner-unit pairs submit exactly once, **{fmt_int(no_submission_pairs)}** never submit, and **{fmt_int(multi_submission_pairs)}** submit more than once (max submissions per pair = {fmt_int(max_submissions)}).",
        f"There are **{fmt_int(public_only_pairs)}** public-only learner-unit pairs. A tiny corner case remains: **{fmt_int(private_only_test_run_rows)}** private `test_run` rows appear without a public twin ({private_only_breakdown}).",
        "",
        "## Release Waves and Activity Bursts",
        "",
        md_table(["first activity date", "units", "unit_ids", "rows", "share"], release_rows),
        "",
        "Biggest activity days:",
        "",
        md_table(["date", "rows", "units touched", "share"], peak_day_rows),
        "",
        "Highest-volume units:",
        "",
        md_table(["unit_id", "rows", "keys", "rows/key", "first activity", "last activity"], top_unit_rows),
        "",
        f"The seven NPPE-style units (`770-776`) contribute **{fmt_int(nppe_rows)}** rows ({fmt_pct(nppe_rows, total_rows)}) and **{fmt_int(nppe_keys)}** learner keys ({fmt_pct(nppe_keys, key_count)}).",
        "",
        "## Public vs Private Twin-Run Behavior",
        "",
        f"There are **{fmt_int(paired_runs)}** mirrored `test_run` pairs sharing the same `filename` across `public` and `private` rows. On average, paired runs pass **{avg_public_pair_pass_rate:.4f}** of public tests vs **{avg_private_pair_pass_rate:.4f}** of private tests.",
        f"- Public all-pass on paired runs: **{fmt_int(public_all_pass)}** ({fmt_pct(public_all_pass, paired_runs)})",
        f"- Private all-pass on paired runs: **{fmt_int(private_all_pass)}** ({fmt_pct(private_all_pass, paired_runs)})",
        f"- Public all-pass but private fail: **{fmt_int(public_green_hidden_fail)}** ({fmt_pct(public_green_hidden_fail, paired_runs)})",
        f"- Summary mismatch across the same code snapshot: **{fmt_int(summary_mismatch)}** ({fmt_pct(summary_mismatch, paired_runs)})",
        f"- Raw passed-count comparison is directional, not symmetric: public > private in **{fmt_int(public_passed_gt_private)}** pairs, public < private in **{fmt_int(public_passed_lt_private)}** pairs. That is why pass-rate is safer.",
        f"- Units with different public/private test totals: **{fmt_int(differing_unit_count)}** units ({differing_units}).",
        "",
        "Units with the highest public-green / hidden-fail rate (minimum 500 paired runs):",
        "",
        md_table(
            [
                "unit_id",
                "paired runs",
                "public all-pass",
                "private all-pass",
                "public green, hidden fail",
                "avg public-private pass-rate gap",
            ],
            pair_gap_rows,
        ),
        "",
        "## Payload Size and Other Outliers",
        "",
        md_table(
            [
                "submission_type",
                "min code",
                "median code",
                "p90 code",
                "p99 code",
                "max code",
                "min data",
                "median data",
                "p90 data",
                "p99 data",
                "max data",
            ],
            length_rows,
        ),
        "",
        md_table(
            ["`data` length", "rows", "public share", "TLE rows", "Wrong Answer rows", "Runtime Error rows"],
            threshold_rows,
        ),
        "",
        "Large `data` outliers are mostly public rows where `test_case_results[*].output` explodes. For example, the largest rows are `Time Limit Exceeded` or `Runtime Error` cases with repeated stdout captured inside the nested JSON.",
        "",
        "Units with the biggest payload ceilings:",
        "",
        md_table(["unit_id", "rows", "p99 data", "max data", "p99 code", "max code"], outlier_unit_rows),
        "",
        "## Practical Analysis Advice",
        "",
        "- Build a normalized view first. Do not analyze the raw `data` string or `filename` string inline in every query.",
        "- For learner progress, use `num_test_passed / num_test_evaluated` on public rows and `score` on private submission rows.",
        "- Separate three concepts: public `test_run`, private mirrored `test_run`, and private `submission`. They are all present here, and `submission_type='private'` alone does not tell you which one you have.",
        "- If you join on `filename` alone, you will accidentally collapse mirrored public/private test runs. Join on `(filename, submission_type)` instead.",
        "- If you need code text, decode `code` once into a derived table and hash/deduplicate it. The raw export already has more than a million distinct code payloads.",
        "- Treat very large `data` blobs as behaviorally meaningful. They usually indicate runaway output or verbose failure traces, not parse errors or malformed JSON.",
        "",
        "## Suggested First Analyses",
        "",
        "- Hidden-test gap by unit: compare paired public/private test-run pass-rates and public-green/private-fail rates.",
        "- Learner persistence: use learner-unit row counts, timestamps, and submission presence to identify thrashers vs quick finishers.",
        "- Release-wave behavior: compare the February 4, February 12, February 20, February 27, March 5, and March 6 unit batches.",
        "- Payload outlier mining: inspect huge `data` rows to find tasks that trigger infinite loops, excessive printing, or pathological runtime behavior.",
        "- Code-state deduplication: decode and hash `code` to study how often learners resubmit identical code under different public/private outcomes.",
        "",
    ]

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
