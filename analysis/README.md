# Analysis README

This document describes the OPPE analysis outputs as a single-shot, reproducible data pipeline.

## 1) Data Model (Simple)

Two raw inputs drive the whole analysis:

- `submissions/*.json` (event log, JSONL)
- `problems/*/*.json` (question metadata)

Core unit:

- Event level: one row per student action (`test_run`, `submission`, optionally `saved_code`).
- Student-question level: one row per `(Namespace, ProblemID, StudentID)`.

Current raw snapshot:

- Raw events: **2057658**
- Raw students: **13623**
- Raw namespaces: **35**
- Raw student-question combos: **151778**

## 2) Standardized Outputs

### Canonical datasets

- `analysis/final_scores.csv`
  - Grain: `(Namespace, ProblemID, StudentID)`
  - Includes latest submission score (nullable), event counts, and first/last event timestamps in UTC and IST.
- `analysis/submission_timeline.parquet`
  - Grain: event-level timeline
  - Standard fields: `namespace, problem_id, student_id, timestamp_utc, timestamp_ist, event_type, evaluation_type, seconds_since_start, code_sha256, code_length, is_parseable, status, reason, summary, score, num_test_evaluated, num_test_passed, test_case_count`.
- `analysis/code_snapshots.parquet`
  - Grain: unique code snapshot by `code_sha256`.
  - Holds full code text once per unique hash; timeline table references it by hash.
- `analysis/question_metadata.csv`
  - Grain: question metadata per namespace/problem
  - Fields: question title/text, skeleton flag, test counts.
- `analysis/schedule.csv`
  - Grain: namespace-level schedule
  - Times are ISO 8601 IST (`+05:30`), computed as 95% activity windows (2.5% to 97.5%), rounded to 15 minutes.
- `analysis/anomalous_accounts.csv`
  - Flagged accounts with rule-based anomaly score and explicit reason flags.

### Pipeline scripts (all in `analysis/`)

- `analysis/final_scores.sql`
- `analysis/final_scores_termwise.sql`
- `analysis/final_scores_pivot.sql`
- `analysis/student-question-pairs.sql`
- `analysis/scores.sql`
- `analysis/generate_schedule.py`
- `analysis/question_metadata.py`
- `analysis/submission_timeline.py`
- `analysis/generate_anomalous_accounts.py`
- `analysis/generate_readme.py`

### Rebuild all outputs

```bash
set -euo pipefail

duckdb -bail -c ".read analysis/student-question-pairs.sql"
duckdb -bail -c ".read analysis/scores.sql"
duckdb -bail -c ".read analysis/final_scores.sql"
duckdb -bail -c ".read analysis/final_scores_termwise.sql"
duckdb -bail -c ".read analysis/final_scores_pivot.sql"

uv run python analysis/question_metadata.py
# ~2-15 minutes depending on CPU/disk; builds submission_timeline.parquet + code_snapshots.parquet
uv run python analysis/submission_timeline.py
uv run python analysis/generate_schedule.py
uv run python analysis/generate_anomalous_accounts.py
uv run python analysis/generate_readme.py
```

### Storage strategy

- Raw `submissions/*.json` is the immutable source layer.
- `submission_timeline.parquet` is the analytical event layer (columnar, compressed, query-friendly).
- `code_snapshots.parquet` prevents code text duplication across repeated events.
- Raw submissions size: **6087.3 MB**
- Timeline parquet size: **74.3 MB**
- Code snapshots parquet size: **184.1 MB**

Why this is optimal:

- DuckDB can scan raw JSON directly, but repeated analyses repeatedly pay JSON parsing cost.
- Parquet provides faster repeated reads, typed columns, predicate pushdown, and better compression.
- Separating deduplicated code snapshots from event rows minimizes storage while preserving full fidelity.

Quick local benchmark (single-run timings; machine/cache dependent):

- Row count scan: raw JSON 1.014s vs parquet 0.015s (69.5x faster)
- Filtered score aggregate: raw JSON 0.844s vs parquet 0.018s (47.6x faster)

### Convenience / derived datasets

These are useful for reporting but derivable from canonical tables:

- `analysis/student-question-pairs.csv` = key projection of student-question rows
- `analysis/scores.csv` = event-level score extract
- `analysis/final_scores_termwise.csv` = aggregate from `final_scores.csv`
- `analysis/final_scores_pivot.csv` = pivot from `final_scores.csv`
- `analysis/guide.md` = narrative layer built from these outputs

## 3) Redundancy / Derivability Checks

- `final_scores` rows: **151778**
- Distinct combos in `final_scores`: **151778**
- Rows in `student-question-pairs`: **151778**
- Distinct student-term keys from `final_scores`: **17521**
- Rows in `final_scores_termwise`: **17521**
- Distinct students in `final_scores`: **13623**
- Rows in `final_scores_pivot`: **13623**

Interpretation: `student-question-pairs`, `final_scores_termwise`, and `final_scores_pivot` are convenience transforms over the canonical student-question table.

## 4) Standardized Metric Definitions

- `submission_events`: count of `.../submission/...` events for a student-question combo.
- `latest_submission_score`: score from the latest submission event only; null if no submission event.
- `first_event_utc` / `last_event_utc`: boundary timestamps of observed activity in UTC.
- `first_event_ist` / `last_event_ist`: UTC+05:30 projection of event boundaries.
- `seconds_since_start` (timeline): event time minus first observed combo event.
- `is_parseable`: Python syntax parseability check for decoded snapshot code.
- `schedule start_time/end_time`: per-namespace 95% activity window in IST, rounded to 15-minute boundaries.

## 5) Quality Checks an Expert Would Run

### A) Score validity and missingness

- `final_scores` rows: **151778**
- Rows with no submission event: **108860** (71.72%)
- Out-of-range submission scores (<0 or >100): **0**

### B) Metadata completeness

- Namespaces in final_scores missing question metadata: **0**

### C) Ordering and sortability

- Out-of-order rows in `schedule.csv` by `start_time`: **0**
- Times in `schedule.csv` are stored as ISO 8601 IST to guarantee lexical and chronological ordering are aligned.

### D) Event realism checks

- Timeline rows: **2057658**
- Parseable snapshots: **1651029** (80.24%)

## 6) Key Insights

1. Most activity is iterative testing, not final submission.
   - Event mix (raw):
   - `test_run`: 2002516 rows
   - `submission`: 55142 rows

2. Event-aware student-question coverage is essential.
   - A large share of student-question rows has activity without a submission event; treating missing submission as missing participation is incorrect.

3. Scheduling is wave-based and measurable from behavior.
   - Namespace coverage by term/wave:
   - 25t1 / other: 1 namespaces, 115 namespace-student assignments
   - 25t1 / wave1: 8 namespaces, 5840 namespace-student assignments
   - 25t1 / wave2: 6 namespaces, 5564 namespace-student assignments
   - 25t2 / wave1: 5 namespaces, 4587 namespace-student assignments
   - 25t2 / wave2: 5 namespaces, 4000 namespace-student assignments
   - 25t3 / wave1: 6 namespaces, 4328 namespace-student assignments
   - 25t3 / wave2: 4 namespaces, 3760 namespace-student assignments

4. A small but important abnormal-account set exists and should be tagged, not silently dropped.
   - Flagged accounts: **266**
   - Dual-variant accounts: **2**
   - High-confidence (anomaly_score >= 3): **2**
   - Top anomaly reason groups:
   - final_rows_outlier: 126 accounts
   - event_volume_outlier: 90 accounts
   - event_volume_outlier,final_rows_outlier: 47 accounts
   - namespace_count_outlier,event_volume_outlier,final_rows_outlier: 1 accounts
   - dual_variant_assignment: 1 accounts
   - namespace_count_outlier,event_volume_outlier,final_rows_outlier,dual_variant_assignment,high_namespace_per_term: 1 accounts

5. Question bank is structured and test-rich.
   - Questions: **251**
   - With skeleton code: **243** (96.81%)
   - Avg public tests: **3.6**
   - Avg private tests: **3.5**

## 7) Recommended Analysis Base

For most analytics work, use this stack:

1. Base fact table: `analysis/final_scores.csv`
2. Behavior detail: `analysis/submission_timeline.parquet`
   - Join to `analysis/code_snapshots.parquet` only when raw code text is required.
3. Question context: `analysis/question_metadata.csv`
4. Time windows / wave segmentation: `analysis/schedule.csv`
5. Account-quality filter/tag layer: `analysis/anomalous_accounts.csv`

Use other CSVs as reporting conveniences, not as independent sources of truth.
