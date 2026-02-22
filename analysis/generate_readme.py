#!/usr/bin/env python3
import csv
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "analysis" / "README.md"


def q(query: str):
    res = subprocess.run(
        ["duckdb", "-csv", "-c", query],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    rows = list(csv.DictReader(res.stdout.splitlines()))
    return rows


def one(query: str):
    rows = q(query)
    if not rows:
        return {}
    return rows[0]


def timed_duckdb(query: str) -> float:
    start = time.perf_counter()
    subprocess.run(
        ["duckdb", "-c", query],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    return time.perf_counter() - start


def main() -> None:
    raw_overview = one(
        """
        SELECT
          COUNT(*) AS raw_events,
          COUNT(DISTINCT StudentID) AS raw_students,
          COUNT(DISTINCT Namespace) AS raw_namespaces,
          COUNT(DISTINCT Namespace || '|' || ProblemID || '|' || StudentID) AS raw_student_question_combos
        FROM read_json('submissions/*.json', format='newline_delimited', columns={StudentID:'VARCHAR', Namespace:'VARCHAR', ProblemID:'VARCHAR'});
        """
    )

    raw_event_mix = q(
        """
        SELECT
          regexp_extract(FileName, '/(saved_code|test_run|submission)/', 1) AS event_type,
          COUNT(*) AS rows
        FROM read_json('submissions/*.json', format='newline_delimited', columns={FileName:'VARCHAR'})
        GROUP BY event_type
        ORDER BY rows DESC;
        """
    )

    final_overview = one(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(DISTINCT StudentID) AS students,
          COUNT(DISTINCT Namespace) AS namespaces,
          COUNT(*) FILTER (WHERE submission_events = 0) AS no_submission_rows,
          ROUND(100.0 * COUNT(*) FILTER (WHERE submission_events = 0) / COUNT(*), 2) AS no_submission_pct,
          COUNT(*) FILTER (
            WHERE TRY_CAST("CompilationResult.score" AS DOUBLE) IS NOT NULL
              AND (
                TRY_CAST("CompilationResult.score" AS DOUBLE) < 0
                OR TRY_CAST("CompilationResult.score" AS DOUBLE) > 100
              )
          ) AS out_of_range_scores
        FROM read_csv_auto('analysis/final_scores.csv', header=true);
        """
    )

    schedule_overview = q(
        """
        SELECT term, wave, COUNT(*) AS namespaces, SUM(num_students) AS namespace_students
        FROM read_csv_auto('analysis/schedule.csv', header=true)
        GROUP BY term, wave
        ORDER BY term, wave;
        """
    )

    timeline_overview = one(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(*) FILTER (WHERE is_parseable) AS parseable_rows,
          ROUND(100.0 * COUNT(*) FILTER (WHERE is_parseable) / COUNT(*), 2) AS parseable_pct
        FROM read_parquet('analysis/submission_timeline.parquet');
        """
    )

    timeline_event_mix = q(
        """
        SELECT event_type, COUNT(*) AS rows
        FROM read_parquet('analysis/submission_timeline.parquet')
        GROUP BY event_type
        ORDER BY rows DESC;
        """
    )

    question_overview = one(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(*) FILTER (WHERE has_skeleton_code) AS with_skeleton,
          ROUND(100.0 * COUNT(*) FILTER (WHERE has_skeleton_code) / COUNT(*), 2) AS with_skeleton_pct,
          ROUND(AVG(num_public_tests), 2) AS avg_public_tests,
          ROUND(AVG(num_private_tests), 2) AS avg_private_tests
        FROM read_csv_auto('analysis/question_metadata.csv', header=true);
        """
    )

    anomalies_overview = one(
        """
        SELECT
          COUNT(*) AS flagged_accounts,
          COUNT(*) FILTER (WHERE flag_dual_variant) AS dual_variant_accounts,
          COUNT(*) FILTER (WHERE anomaly_score >= 3) AS high_confidence_accounts
        FROM read_csv_auto('analysis/anomalous_accounts.csv', header=true);
        """
    )

    anomalies_top = q(
        """
        SELECT anomaly_reasons, COUNT(*) AS accounts
        FROM read_csv_auto('analysis/anomalous_accounts.csv', header=true)
        GROUP BY anomaly_reasons
        ORDER BY accounts DESC
        LIMIT 6;
        """
    )

    derivability_checks = one(
        """
        WITH
        fs AS (
          SELECT COUNT(*) AS final_rows,
                 COUNT(DISTINCT Namespace || '|' || ProblemID || '|' || StudentID) AS final_distinct_combos,
                 COUNT(DISTINCT StudentID || '|' || regexp_extract(Namespace, '^ns_([0-9]{2}t[0-9]+)_', 1)) AS final_student_terms,
                 COUNT(DISTINCT StudentID) AS final_students
          FROM read_csv_auto('analysis/final_scores.csv', header=true)
        ),
        sq AS (SELECT COUNT(*) AS student_question_pairs_rows FROM read_csv_auto('analysis/student-question-pairs.csv', header=true)),
        ft AS (SELECT COUNT(*) AS final_scores_termwise_rows FROM read_csv_auto('analysis/final_scores_termwise.csv', header=true)),
        fp AS (SELECT COUNT(*) AS final_scores_pivot_rows FROM read_csv_auto('analysis/final_scores_pivot.csv', header=true))
        SELECT
          fs.final_rows,
          fs.final_distinct_combos,
          sq.student_question_pairs_rows,
          fs.final_student_terms,
          ft.final_scores_termwise_rows,
          fs.final_students,
          fp.final_scores_pivot_rows
        FROM fs, sq, ft, fp;
        """
    )

    metadata_coverage = one(
        """
        WITH fs_ns AS (
          SELECT DISTINCT Namespace FROM read_csv_auto('analysis/final_scores.csv', header=true)
        ),
        qm_ns AS (
          SELECT DISTINCT namespace AS Namespace FROM read_csv_auto('analysis/question_metadata.csv', header=true)
        )
        SELECT
          COUNT(*) FILTER (WHERE qm.Namespace IS NULL) AS namespaces_missing_metadata
        FROM fs_ns fs
        LEFT JOIN qm_ns qm USING (Namespace);
        """
    )

    schedule_sort_check = one(
        """
        WITH t AS (
          SELECT *,
                 lag(start_time) OVER (ORDER BY start_time, term, wave, namespace) AS prev_start
          FROM read_csv_auto('analysis/schedule.csv', header=true)
        )
        SELECT
          COUNT(*) FILTER (WHERE prev_start IS NOT NULL AND start_time < prev_start) AS out_of_order_rows
        FROM t;
        """
    )

    benchmark_queries = {
        "raw_count": """
            SELECT COUNT(*)
            FROM read_json(
              'submissions/*.json',
              format='newline_delimited',
              columns={FileName:'VARCHAR'}
            )
            WHERE FileName IS NOT NULL;
        """,
        "parquet_count": """
            SELECT COUNT(*)
            FROM read_parquet('analysis/submission_timeline.parquet');
        """,
        "raw_filtered_score": """
            SELECT COUNT(*), AVG(CAST(json_extract_string(CompilationResult, '$.score') AS DOUBLE))
            FROM read_json(
              'submissions/*.json',
              format='newline_delimited',
              columns={Namespace:'VARCHAR', CompilationResult:'VARCHAR'}
            )
            WHERE Namespace LIKE 'ns_25t3_%';
        """,
        "parquet_filtered_score": """
            SELECT COUNT(*), AVG(score)
            FROM read_parquet('analysis/submission_timeline.parquet')
            WHERE namespace LIKE 'ns_25t3_%';
        """,
    }
    benchmarks = {name: timed_duckdb(query) for name, query in benchmark_queries.items()}

    timeline_size_mb = (
        (ROOT / "analysis" / "submission_timeline.parquet").stat().st_size / (1024 * 1024)
        if (ROOT / "analysis" / "submission_timeline.parquet").exists()
        else 0.0
    )
    code_size_mb = (
        (ROOT / "analysis" / "code_snapshots.parquet").stat().st_size / (1024 * 1024)
        if (ROOT / "analysis" / "code_snapshots.parquet").exists()
        else 0.0
    )
    raw_submissions_size_mb = (
        sum(p.stat().st_size for p in (ROOT / "submissions").glob("*.json")) / (1024 * 1024)
        if (ROOT / "submissions").exists()
        else 0.0
    )

    readme = []
    readme.append("# Analysis README")
    readme.append("")
    readme.append("This document describes the OPPE analysis outputs as a single-shot, reproducible data pipeline.")
    readme.append("")
    readme.append("## 1) Data Model (Simple)")
    readme.append("")
    readme.append("Two raw inputs drive the whole analysis:")
    readme.append("")
    readme.append("- `submissions/*.json` (event log, JSONL)")
    readme.append("- `problems/*/*.json` (question metadata)")
    readme.append("")
    readme.append("Core unit:")
    readme.append("")
    readme.append("- Event level: one row per student action (`test_run`, `submission`, optionally `saved_code`).")
    readme.append("- Student-question level: one row per `(Namespace, ProblemID, StudentID)`.")
    readme.append("")
    readme.append("Current raw snapshot:")
    readme.append("")
    readme.append(f"- Raw events: **{raw_overview['raw_events']}**")
    readme.append(f"- Raw students: **{raw_overview['raw_students']}**")
    readme.append(f"- Raw namespaces: **{raw_overview['raw_namespaces']}**")
    readme.append(f"- Raw student-question combos: **{raw_overview['raw_student_question_combos']}**")
    readme.append("")

    readme.append("## 2) Standardized Outputs")
    readme.append("")
    readme.append("### Canonical datasets")
    readme.append("")
    readme.append("- `analysis/final_scores.csv`")
    readme.append("  - Grain: `(Namespace, ProblemID, StudentID)`")
    readme.append("  - Includes latest submission score (nullable), event counts, and first/last event timestamps in UTC and IST.")
    readme.append("- `analysis/submission_timeline.parquet`")
    readme.append("  - Grain: event-level timeline")
    readme.append("  - Standard fields: `namespace, problem_id, student_id, timestamp_utc, timestamp_ist, event_type, evaluation_type, seconds_since_start, code_sha256, code_length, is_parseable, status, reason, summary, score, num_test_evaluated, num_test_passed, test_case_count`.")
    readme.append("- `analysis/code_snapshots.parquet`")
    readme.append("  - Grain: unique code snapshot by `code_sha256`.")
    readme.append("  - Holds full code text once per unique hash; timeline table references it by hash.")
    readme.append("- `analysis/question_metadata.csv`")
    readme.append("  - Grain: question metadata per namespace/problem")
    readme.append("  - Fields: question title/text, skeleton flag, test counts.")
    readme.append("- `analysis/schedule.csv`")
    readme.append("  - Grain: namespace-level schedule")
    readme.append("  - Times are ISO 8601 IST (`+05:30`), computed as 95% activity windows (2.5% to 97.5%), rounded to 15 minutes.")
    readme.append("- `analysis/anomalous_accounts.csv`")
    readme.append("  - Flagged accounts with rule-based anomaly score and explicit reason flags.")
    readme.append("")
    readme.append("### Pipeline scripts (all in `analysis/`)")
    readme.append("")
    readme.append("- `analysis/final_scores.sql`")
    readme.append("- `analysis/final_scores_termwise.sql`")
    readme.append("- `analysis/final_scores_pivot.sql`")
    readme.append("- `analysis/student-question-pairs.sql`")
    readme.append("- `analysis/scores.sql`")
    readme.append("- `analysis/generate_schedule.py`")
    readme.append("- `analysis/question_metadata.py`")
    readme.append("- `analysis/submission_timeline.py`")
    readme.append("- `analysis/generate_anomalous_accounts.py`")
    readme.append("- `analysis/generate_readme.py`")
    readme.append("")
    readme.append("### Rebuild all outputs")
    readme.append("")
    readme.append("```bash")
    readme.append("set -euo pipefail")
    readme.append("")
    readme.append("duckdb -bail -c \".read analysis/student-question-pairs.sql\"")
    readme.append("duckdb -bail -c \".read analysis/scores.sql\"")
    readme.append("duckdb -bail -c \".read analysis/final_scores.sql\"")
    readme.append("duckdb -bail -c \".read analysis/final_scores_termwise.sql\"")
    readme.append("duckdb -bail -c \".read analysis/final_scores_pivot.sql\"")
    readme.append("")
    readme.append("uv run python analysis/question_metadata.py")
    readme.append("# ~2-15 minutes depending on CPU/disk; builds submission_timeline.parquet + code_snapshots.parquet")
    readme.append("uv run python analysis/submission_timeline.py")
    readme.append("uv run python analysis/generate_schedule.py")
    readme.append("uv run python analysis/generate_anomalous_accounts.py")
    readme.append("uv run python analysis/generate_readme.py")
    readme.append("```")
    readme.append("")

    readme.append("### Storage strategy")
    readme.append("")
    readme.append("- Raw `submissions/*.json` is the immutable source layer.")
    readme.append("- `submission_timeline.parquet` is the analytical event layer (columnar, compressed, query-friendly).")
    readme.append("- `code_snapshots.parquet` prevents code text duplication across repeated events.")
    readme.append(f"- Raw submissions size: **{raw_submissions_size_mb:.1f} MB**")
    readme.append(f"- Timeline parquet size: **{timeline_size_mb:.1f} MB**")
    readme.append(f"- Code snapshots parquet size: **{code_size_mb:.1f} MB**")
    readme.append("")
    readme.append("Why this is optimal:")
    readme.append("")
    readme.append("- DuckDB can scan raw JSON directly, but repeated analyses repeatedly pay JSON parsing cost.")
    readme.append("- Parquet provides faster repeated reads, typed columns, predicate pushdown, and better compression.")
    readme.append("- Separating deduplicated code snapshots from event rows minimizes storage while preserving full fidelity.")
    readme.append("")
    readme.append("Quick local benchmark (single-run timings; machine/cache dependent):")
    readme.append("")
    readme.append(
        "- Row count scan: raw JSON {:.3f}s vs parquet {:.3f}s ({:.1f}x faster)".format(
            benchmarks["raw_count"],
            benchmarks["parquet_count"],
            (benchmarks["raw_count"] / benchmarks["parquet_count"]) if benchmarks["parquet_count"] else 0.0,
        )
    )
    readme.append(
        "- Filtered score aggregate: raw JSON {:.3f}s vs parquet {:.3f}s ({:.1f}x faster)".format(
            benchmarks["raw_filtered_score"],
            benchmarks["parquet_filtered_score"],
            (benchmarks["raw_filtered_score"] / benchmarks["parquet_filtered_score"])
            if benchmarks["parquet_filtered_score"]
            else 0.0,
        )
    )
    readme.append("")

    readme.append("### Convenience / derived datasets")
    readme.append("")
    readme.append("These are useful for reporting but derivable from canonical tables:")
    readme.append("")
    readme.append("- `analysis/student-question-pairs.csv` = key projection of student-question rows")
    readme.append("- `analysis/scores.csv` = event-level score extract")
    readme.append("- `analysis/final_scores_termwise.csv` = aggregate from `final_scores.csv`")
    readme.append("- `analysis/final_scores_pivot.csv` = pivot from `final_scores.csv`")
    readme.append("- `analysis/guide.md` = narrative layer built from these outputs")
    readme.append("")

    readme.append("## 3) Redundancy / Derivability Checks")
    readme.append("")
    readme.append("- `final_scores` rows: **{}**".format(derivability_checks["final_rows"]))
    readme.append("- Distinct combos in `final_scores`: **{}**".format(derivability_checks["final_distinct_combos"]))
    readme.append("- Rows in `student-question-pairs`: **{}**".format(derivability_checks["student_question_pairs_rows"]))
    readme.append("- Distinct student-term keys from `final_scores`: **{}**".format(derivability_checks["final_student_terms"]))
    readme.append("- Rows in `final_scores_termwise`: **{}**".format(derivability_checks["final_scores_termwise_rows"]))
    readme.append("- Distinct students in `final_scores`: **{}**".format(derivability_checks["final_students"]))
    readme.append("- Rows in `final_scores_pivot`: **{}**".format(derivability_checks["final_scores_pivot_rows"]))
    readme.append("")
    readme.append("Interpretation: `student-question-pairs`, `final_scores_termwise`, and `final_scores_pivot` are convenience transforms over the canonical student-question table.")
    readme.append("")

    readme.append("## 4) Standardized Metric Definitions")
    readme.append("")
    readme.append("- `submission_events`: count of `.../submission/...` events for a student-question combo.")
    readme.append("- `latest_submission_score`: score from the latest submission event only; null if no submission event.")
    readme.append("- `first_event_utc` / `last_event_utc`: boundary timestamps of observed activity in UTC.")
    readme.append("- `first_event_ist` / `last_event_ist`: UTC+05:30 projection of event boundaries.")
    readme.append("- `seconds_since_start` (timeline): event time minus first observed combo event.")
    readme.append("- `is_parseable`: Python syntax parseability check for decoded snapshot code.")
    readme.append("- `schedule start_time/end_time`: per-namespace 95% activity window in IST, rounded to 15-minute boundaries.")
    readme.append("")

    readme.append("## 5) Quality Checks an Expert Would Run")
    readme.append("")
    readme.append("### A) Score validity and missingness")
    readme.append("")
    readme.append(f"- `final_scores` rows: **{final_overview['rows']}**")
    readme.append(f"- Rows with no submission event: **{final_overview['no_submission_rows']}** ({final_overview['no_submission_pct']}%)")
    readme.append(f"- Out-of-range submission scores (<0 or >100): **{final_overview['out_of_range_scores']}**")
    readme.append("")
    readme.append("### B) Metadata completeness")
    readme.append("")
    readme.append(f"- Namespaces in final_scores missing question metadata: **{metadata_coverage['namespaces_missing_metadata']}**")
    readme.append("")
    readme.append("### C) Ordering and sortability")
    readme.append("")
    readme.append(f"- Out-of-order rows in `schedule.csv` by `start_time`: **{schedule_sort_check['out_of_order_rows']}**")
    readme.append("- Times in `schedule.csv` are stored as ISO 8601 IST to guarantee lexical and chronological ordering are aligned.")
    readme.append("")
    readme.append("### D) Event realism checks")
    readme.append("")
    readme.append(f"- Timeline rows: **{timeline_overview['rows']}**")
    readme.append(f"- Parseable snapshots: **{timeline_overview['parseable_rows']}** ({timeline_overview['parseable_pct']}%)")
    readme.append("")

    readme.append("## 6) Key Insights")
    readme.append("")
    readme.append("1. Most activity is iterative testing, not final submission.")
    readme.append("   - Event mix (raw):")
    for r in raw_event_mix:
        readme.append(f"   - `{r['event_type']}`: {r['rows']} rows")
    readme.append("")
    readme.append("2. Event-aware student-question coverage is essential.")
    readme.append("   - A large share of student-question rows has activity without a submission event; treating missing submission as missing participation is incorrect.")
    readme.append("")
    readme.append("3. Scheduling is wave-based and measurable from behavior.")
    readme.append("   - Namespace coverage by term/wave:")
    for r in schedule_overview:
        readme.append(f"   - {r['term']} / {r['wave']}: {r['namespaces']} namespaces, {r['namespace_students']} namespace-student assignments")
    readme.append("")
    readme.append("4. A small but important abnormal-account set exists and should be tagged, not silently dropped.")
    readme.append(f"   - Flagged accounts: **{anomalies_overview['flagged_accounts']}**")
    readme.append(f"   - Dual-variant accounts: **{anomalies_overview['dual_variant_accounts']}**")
    readme.append(f"   - High-confidence (anomaly_score >= 3): **{anomalies_overview['high_confidence_accounts']}**")
    readme.append("   - Top anomaly reason groups:")
    for r in anomalies_top:
        readme.append(f"   - {r['anomaly_reasons']}: {r['accounts']} accounts")
    readme.append("")
    readme.append("5. Question bank is structured and test-rich.")
    readme.append(f"   - Questions: **{question_overview['rows']}**")
    readme.append(f"   - With skeleton code: **{question_overview['with_skeleton']}** ({question_overview['with_skeleton_pct']}%)")
    readme.append(f"   - Avg public tests: **{question_overview['avg_public_tests']}**")
    readme.append(f"   - Avg private tests: **{question_overview['avg_private_tests']}**")
    readme.append("")

    readme.append("## 7) Recommended Analysis Base")
    readme.append("")
    readme.append("For most analytics work, use this stack:")
    readme.append("")
    readme.append("1. Base fact table: `analysis/final_scores.csv`")
    readme.append("2. Behavior detail: `analysis/submission_timeline.parquet`")
    readme.append("   - Join to `analysis/code_snapshots.parquet` only when raw code text is required.")
    readme.append("3. Question context: `analysis/question_metadata.csv`")
    readme.append("4. Time windows / wave segmentation: `analysis/schedule.csv`")
    readme.append("5. Account-quality filter/tag layer: `analysis/anomalous_accounts.csv`")
    readme.append("")
    readme.append("Use other CSVs as reporting conveniences, not as independent sources of truth.")
    readme.append("")

    README.write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"wrote {README}")


if __name__ == "__main__":
    main()
