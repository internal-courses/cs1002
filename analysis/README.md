# Analysis README

This AI-edited manually maintained document describes the OPPE analysis outputs and how to reproduce the key datasets and analyses.

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
- `analysis/generate_score_failure_profiles.py`

### Rebuild datasets and analysis outputs

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
uv run analysis/generate_score_failure_profiles.py
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

# Score Distributions, Failure Profiles, and the Non-Submission Problem

This is a Step 1 baseline write-up (supported by generated tables/plots in `analysis/score_failure_profiles/`), with explicit treatment of the large `active, never submitted` population.

## New Script and Outputs

- Script: `analysis/generate_score_failure_profiles.py`
- Output folder: `analysis/score_failure_profiles/`
- Plots: `analysis/score_failure_profiles/plots/*.png`

Key generated outputs:

- `outcome_categories.csv` (row-level classification for all 151,778 student-question rows)
- `outcome_category_summary.csv`
- `non_submission_profiles.csv` (row-level non-submitter profile joined to timeline/schedule/metadata)
- `non_submission_summary.csv`, `non_submission_subtype_summary.csv`
- `question_score_metrics.csv`, `question_score_metrics_with_case_pass_rates.csv`
- `question_score_hist_submitters.csv`, `question_score_hist_all_assigned.csv`
- `question_test_case_pass_rates.csv`, `question_test_case_pass_rate_summary.csv`
- `term_wave_score_summary.csv`, `slot_order_score_summary.csv`, `exam_namespace_score_summary.csv`
- `reused_question_comparison.csv`, `reused_question_summary.csv`
- `findings.md` (generated helper summary used while drafting this manual README section)

## Rebuild This Analysis

```bash
# ~2-8 minutes on local machine; per-test-case pass-rate step scans raw submissions JSON once
uv run analysis/generate_score_failure_profiles.py
```

## Definitions and Caveats

- Progressive-filter design (important for interpretation): students who pass in Term 1 do not write Term 2, and students who pass in Term 2 do not write Term 3. Later terms therefore contain a progressively weaker selected population by construction.
- Outcome categories (1a):
  - `Full pass`: latest submission score equals per-question max observed score (100 in current data)
  - `Partial pass`: latest submission score is between 0 and max
  - `Submitted, zero`: latest submission score is 0
  - `Active, never submitted`: `submission_events = 0` and `total_events > 0`
  - `No activity`: `total_events = 0`
- `Active time` is the observed span between first and last event for a student-question row (`last_event - first_event`), not keyboard-active time.
- Public per-test-case pass rates are computed from `test_run` events (`evaluation_type='public'`).
- Private per-test-case pass rates are computed from `submission` events (all `submission` events are `evaluation_type='private'` in this dataset).
- Question shape flags (submitter distribution only) use:
  - `Ceiling`: >80% of submitters full marks
  - `Floor`: >70% of submitters zero
  - `Bimodal`: >=30% zero, >=30% full, <=20% partial (submitters >=20)
  - `Healthy spread`: partial 30-70% with no dominant zero/full mass (submitters >=20)

## Findings

### 1a) Outcome Category Baseline (all 151,778 student-question rows)

- `Full pass`: **23,380** (15.40%)
- `Partial pass`: **4,871** (3.21%)
- `Submitted, zero`: **14,667** (9.66%)
- `Active, never submitted`: **108,860** (71.72%)
- `No activity`: **0**

Interpretation: the baseline is dominated by non-submission behavior, not just scoring.

### 1b / 1e) Non-Submission Is Not One Population

Across all `Active, never submitted` rows (`n=108,860`):

- Had at least one public `test_run` with >=1 passing test case: **61,468** (56.47%)
- Had at least one public `test_run` with all public tests passing: **47,731** (43.85%)
- All test runs failed (no passed tests on any `test_run`): **47,314** (43.46%)
- Very few test runs (<=3): **23,432** (21.52%)
- Substantial activity (>10 test runs) and no public pass ("thrashing/stuck" proxy): **15,316** (14.07%)

Important split (this materially changes interpretation):

- There are **23 / 35 namespaces** with zero submission capture (all rows active but no submissions).
- Those zero-submission namespaces contribute **97,748 / 108,860 non-submitters (89.79%)**.
- In zero-submission namespaces, non-submitters often look "successful but unsubmitted":
  - public-pass evidence: **62.24%**
  - all-public-tests-passed in at least one run: **48.76%**
- In namespaces that do have submissions, non-submitters look much more like genuinely stuck students:
  - public-pass evidence: **5.69%**
  - all-public-tests-passed in at least one run: **0.63%**
  - thrashing proxy (>10 runs, no public pass): **27.71%**

This suggests the global 71.72% non-submission rate is a mixture of:

- likely submission-capture / workflow / gating issues in some namespaces, and
- genuine difficulty / time-pressure failures in namespaces where submissions are observed.

### Non-Submitter Behavior Distributions

- This section is a pooled cross-term baseline. Because of the progressive-filter design, later-term non-submitters are a selected population (e.g., Term 3 students have already failed earlier terms), so term-specific behavioral signatures may differ.
- Test-run count (non-submitters):
  - `1`: 4,554
  - `2`: 7,095
  - `3`: 11,783
  - `4-5`: 16,828
  - `6-10`: 25,942
  - `11-20`: 23,562
  - `21-50`: 16,427
  - `51+`: 2,669
- Quantiles of test-run count: median **8**, p90 **28**, p99 **67**
- Quantiles of observed active-time span (minutes): median **15.6**, p90 **89.4**, p99 **118.4**

Last observed non-submitter snapshot:

- Last event type is `test_run` for **100%** of non-submitters
- Last snapshot parseable rate: **85.07%**
- Last-snapshot proxy categories:
  - Parseable + public-pass evidence (partial-solution proxy): **55.75%**
  - Parseable, no public-pass evidence: **29.32%**
  - Unparseable/empty: **14.93%**
- Last public test-run outcomes (top):
  - `All Cases Passed`: **43.54%**
  - `Runtime Error`: **31.57%**
  - `Wrong Answer`: **24.53%**

Cheap term-split check (non-submitters in namespaces with any submissions):

- `25t2`: thrashing/stuck proxy (`>10` test runs, no public pass) = **27.94%**; had any public-pass evidence = **5.38%**
- `25t3`: thrashing/stuck proxy (`>10` test runs, no public pass) = **27.12%**; had any public-pass evidence = **6.49%**

Interpretation: in submission-positive namespaces, the non-submitter subtype mix is very similar in `25t2` and `25t3` on these coarse measures. Term effects may still exist, but they are not obvious from this quick split.

### 1c) Per-Question Score Distributions and Failure Profiles

Across all 251 questions (including zero-submission namespaces):

- `Insufficient submitters`: 167
- `Mixed`: 32
- `Bimodal`: 28
- `Ceiling`: 10
- `Floor`: 9
- `Healthy spread`: 5

Because many namespaces have zero submission capture, the more meaningful shape count is among questions in namespaces with at least one submission (`n=84`):

- `Mixed`: 32
- `Bimodal`: 28
- `Ceiling`: 10
- `Floor`: 9
- `Healthy spread`: 5

Examples (requested flag classes):

- `Ceiling`:
  - `ns_25t2_py22_1` Q14 (`Check If Multiple of 5 Not 3`): 97.12% submission rate, 88.03% of submitters full marks
  - `ns_25t3_py13_1` Q9 (`Double if Even Else Square`): 96.67% submission rate, 89.52% full marks among submitters
- `Floor`:
  - `ns_25t2_py14_1` Q10 (`Reverse Vowel Order in a String`): 78.90% of submitters scored zero
  - `ns_25t3_py13_1` Q13 (`Step Triangle Pattern`): 83.97% of submitters scored zero
- `Bimodal`:
  - `ns_25t2_py13_2` Q5 (`Double First and Last Elements in a List`)
  - `ns_25t2_py21_2` Q18 (`Pangram Check`)
- `Healthy spread`:
  - `ns_25t2_py14_1` Q6 (`Expand Sum of Products`)
  - `ns_25t2_py22_1` Q19 (`Sales Data Analysis`)
  - `ns_25t2_py13_2` Q12 (`YouTube Video Engagement Analysis`)

High non-submission questions (excluding zero-submission namespaces, so this is not just capture failure):

- `ns_25t2_py11_1` Q13 (`Draw Arrow Trail from Movement Deltas`): **45.74%** non-submission
- `ns_25t2_py11_1` Q12 (`Text Frequency Analysis`): **44.54%** non-submission
- `ns_25t2_py21_1` Q18 (`Rotate Matrix Clockwise 90 degree`): **41.40%** non-submission

Per-test-case pass rates (distribution summary):

- Public test cases (from `test_run` attempts): mean pass rate **20.94%**, median **17.56%** across question-test cases
- Private test cases (from `submission` attempts): mean pass rate **51.72%**, median **53.03%**

Interpretation: public-case pass rates are attempt-level and include repeated failing trial runs, so they are expected to be much lower than private-case pass rates computed on submission attempts.

### 1d) Aggregate by Wave / Term / Time Slot (with Coverage Caveat)

Term-wave summary (descriptive only; do not treat `25t1`/`25t2`/`25t3` as comparable cohorts because of the progressive-filter design):

- `25t1`: Wave 1 and Wave 2 both show **0% submission rate** (all observed rows are active-without-submission)
- `25t2`: Wave 1 submission rate **75.63%**, Wave 2 **58.82%**
- `25t3`: Wave 1 submission rate **41.45%**, Wave 2 **11.38%**

But these aggregates are heavily confounded by namespace-level zero submission capture:

- Zero-submission namespaces by term/wave:
  - `25t1`: **15 / 15 namespaces** (100%)
  - `25t2 wave2`: **2 / 5 namespaces** (40%) are zero-submission (`py23_1`, `py23_2`)
  - `25t3 wave1`: **3 / 6 namespaces** (50%)
  - `25t3 wave2`: **3 / 4 namespaces** (75%)

Coverage-aware slot reading (only namespaces with any submissions):

- `25t2 wave2` on `2025-08-24`:
  - slot 1 `ns_25t2_py21_1`: submission rate **82.73%**, effective mean **54.42**
  - slot 2 `ns_25t2_py21_2`: **83.83%**, **56.81**
  - slot 3 `ns_25t2_py22_1`: **88.11%**, **65.62**
  - slots 4-5 (`py23_1`, `py23_2`) have zero submission capture, so apparent "fatigue collapse" there is not interpretable as performance

Conclusion: time-slot comparisons must be stratified by namespace submission-capture availability before using them to infer fatigue.

Comparability note:

- Cross-term comparisons (`25t1` vs `25t2` vs `25t3`) are confounded by population selection: later terms contain students who did not clear earlier terms.
- Within-term Wave 1 vs Wave 2 comparisons remain the more defensible comparison (same term cohort, roughly ~35 days apart), subject to submission-capture availability.

### Reused Questions Across Terms (and Why Capture Status Matters)

- `Check is even or divisible by 5` appears in:
  - `ns_25t1_py11_1` Q2 and `ns_25t1_py_15_exe` Q5 (both 0% submissions; zero-submission namespaces)
  - `ns_25t2_py12_1` Q5 (94.07% submission rate, 84.41 effective mean, `Ceiling`)

Implications:

- Reused-question comparisons must be split by whether the namespace has any submission capture.
- Cross-term reused-question comparisons are additionally confounded by the progressive-filter design: later terms (`t2`, `t3`) contain a weaker selected population by construction.
- Therefore, pass-rate changes for the same reused question across terms should be interpreted primarily as population-mix differences, not as evidence of question difficulty changes, learning gains, or teaching effects.

### Additional Insights Useful for Future Analysis

- Add a standard namespace-level flag in downstream analyses: `namespace_has_any_submissions` (or equivalent). This single split prevents major misreads in non-submission, difficulty, and fatigue analyses.
- Treat these as separate baselines, not one metric: overall non-submission rate (operational / workflow signal) vs coverage-adjusted non-submission rate (difficulty / behavior signal).
- `100%` of non-submitters end on a `test_run` event. This makes submit-button UX/instructions and submission-event logging prime suspects for instrumentation checks.
- Only **84 / 251** namespace-question rows in the current snapshot have any submissions (and therefore meaningful submitter score distributions).
- Future comparative question-quality analysis should either restrict to submission-positive namespaces/questions or explicitly model missing submission capture as a separate data state.
- Public vs private per-test-case pass rates are both useful, but not directly comparable without normalization: public rates are attempt-level across repeated iterative `test_run`s; private rates are submission-attempt-level.
- For fatigue/time-slot analysis, use within-day comparisons only among contiguous slots with submission capture, and prefer within-term comparisons over cross-term comparisons. Example: `25t2 wave2` slots 1-3 are interpretable, but slots 4-5 are not in the current snapshot because submissions are absent for those namespaces.

## Plots Produced

- `analysis/score_failure_profiles/plots/outcome_categories.png`
- `analysis/score_failure_profiles/plots/overall_score_distributions.png`
- `analysis/score_failure_profiles/plots/non_submission_distributions.png`
- `analysis/score_failure_profiles/plots/question_score_profile_map.png`
- `analysis/score_failure_profiles/plots/question_distribution_shape_counts.png`
- `analysis/score_failure_profiles/plots/test_case_pass_rate_distributions.png`
- `analysis/score_failure_profiles/plots/slot_order_trends_multi_slot_days.png`
