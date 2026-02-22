
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

# Step 1. Score Distributions, Failure Profiles, and the Non-Submission Problem

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

# Step 2. Classical Item Quality Analysis

This section is a manual write-up of Step 2 ("is the exam measuring well?"), backed by generated outputs in `analysis/classical_item_quality/`.

## New Script and Outputs

- Script: `analysis/generate_classical_item_quality.py`
- Output folder: `analysis/classical_item_quality/`
- Graphs: `analysis/classical_item_quality/dependency_graphs/*.dot` (directed dependency graphs per question)
- Reduced graphs: `analysis/classical_item_quality/dependency_graphs_reduced/*.dot` (SCC-condensed + transitive-reduced dependency graphs)

Key generated outputs:

- `item_response_rows.csv` (selected item responses for submitter-question rows)
- `item_difficulty_discrimination.csv`
- `item_difficulty_discrimination_summary.csv`
- `item_low_discrimination_candidates.csv`
- `question_item_redundancy_pairs.csv`
- `question_item_redundancy_summary_by_namespace.csv`
- `question_dependency_pairs.csv`
- `question_dependency_edges.csv`
- `question_dependency_edges_transitive_reduced.csv`
- `question_dependency_sccs.csv`
- `question_dependency_minimal_new_information.csv`
- `question_dependency_graph_summary.csv`
- `namespace_reliability_cronbach_alpha.csv`
- `namespace_reliability_summary.csv`
- `public_private_gap_by_question.csv`
- `public_private_gap_summary.csv`
- `public_private_gap_same_code_by_question.csv`
- `public_private_gap_same_code_summary.csv`
- `public_private_gap_same_code_coverage.csv`
- `submitter_question_snapshots.csv`
- `submitter_question_public_private_summary.csv`
- `submitter_question_same_code_snapshots.csv`
- `submitter_question_same_code_public_private_summary.csv`

## Rebuild This Analysis

```bash
# ~1-5 minutes on local machine; scans raw submissions JSON to extract selected test-case results
uv run analysis/generate_classical_item_quality.py
```

## Method and Scope (Important)

- Unit of analysis for item responses (submitter-only):
  - private test cases: the **final scored submission** per student-question (from `analysis/final_scores.csv`)
  - public test cases: the **latest public `test_run` at or before that final submission**
- This creates a submitter-only selection effect:
  - non-submitters have no scored private test-case outcomes and are excluded from item-level discrimination/redundancy analyses
  - discrimination values therefore reflect the stronger selected submitter population and may underestimate (or otherwise distort) full-population discrimination
- Discrimination (2a):
  - computed with `scipy.stats.pointbiserialr`
  - reported against namespace total score across all questions in the same namespace (with non-submitted questions contributing zero to the namespace total)
  - exported both as raw item-total (`point_biserial_r`) and a less part-whole-inflated variant excluding the focal question score (`point_biserial_r_excl_question`)
- Redundancy (2b):
  - within each question, pairwise phi/Pearson correlations are computed on binary item pass/fail values across submitters to that question
  - pairs with phi `> 0.90` are flagged as near-redundant
- Dependency structure (2c):
  - for each ordered pair `(A, B)` in a question: `P(pass B | pass A)` and `P(pass B | fail A)`
  - edge flag uses the requested criterion `P(pass B | fail A) < 0.05`
  - graph export uses an additional support filter (`n_A_fail >= 5` and `n_A_pass >= 5`) to reduce one-off edges
  - follow-up extension: strongly connected components (SCCs) + transitive reduction on the SCC-condensed DAG are exported to isolate a smaller set of "minimal new information" test-case groups (sink SCCs in the reduced graph)
- Reliability (2d):
  - Cronbach's alpha is computed per namespace on a student × item binary matrix
  - rows: students with at least one submission in that namespace
  - columns: all observed public+private test-case items in that namespace
  - missing responses from unsubmitted questions are filled with `0` (`*_fill0` in output columns)
- Public/private gap (2e):
  - baseline proxy compares "all public passed" vs "all private passed" using the selected public snapshot above and the final private submission
  - follow-up extension adds a **same-code pairing proxy** using `code_sha256`: final submitted code is paired with the latest public `test_run` on the same code hash before submission
  - caveat (baseline proxy only): the selected public snapshot is **not guaranteed to be the exact same code snapshot** as the final submission

## Findings

### Coverage and Interpretability

- Item-level analysis covers **607 test-case items** across the **84** namespace-question rows that have any submissions.
- These 84 questions are in **12 submission-positive namespaces**; the remaining **23 / 35 namespaces** have no submissions, so item quality metrics and Cronbach alpha are undefined there.
- All **42,918** submitter-question rows had a public `test_run` before the final submission, so Step 2 public/private pairing coverage is **100%** for submitters.
- Same-code public/private pairing coverage is also effectively complete:
  - **42,916 / 42,918** final submissions have a pre-submission public `test_run` with the same `code_sha256` (reported as **100.0%** after rounding in `public_private_gap_same_code_coverage.csv`)

Important public-item caveat (data/versioning):

- Public test-case indices are **not stable** within a question in this snapshot:
  - `84 / 84` public question-scope groups show item coverage drift (`MIN(n_observed) != MAX(n_observed)` across public test-case indices)
  - `0 / 84` private question-scope groups show this drift
- Interpretation: public test sets (or at least public test-case counts/index positions) changed over time within namespace-question rows.
- Consequence: public item-by-index statistics (difficulty/discrimination/redundancy/dependency) are still useful as diagnostics, but they are not as cleanly comparable as private test cases.

### 2a) Per-Test-Case Difficulty and Discrimination

Summary (`analysis/classical_item_quality/item_difficulty_discrimination_summary.csv`):

- Private items: **292**
  - average difficulty (pass %) = **51.73%**
  - median difficulty = **53.03%**
  - average point-biserial `r` = **0.6797** (raw item-total)
  - median point-biserial `r` = **0.6897**
- Public items: **315**
  - average difficulty (pass %) = **55.53%**
  - median difficulty = **58.12%**
  - average point-biserial `r` = **0.6240** (raw item-total)
  - median point-biserial `r` = **0.6351**

`r > 0.30` threshold (using exported corrected variant `point_biserial_r_excl_question` as a stricter screen):

- **591 / 607** items are `> 0.30`
- **13 / 607** items fall in `0.15-0.30` (marginal)
- **0 / 607** items are `< 0.15`
- **3** public items have `NaN` discrimination (all were one-off public indices with `n_observed = 1`)

Interpretation:

- Under this submitter-only, final-snapshot design, discrimination is uniformly high.
- This likely reflects a combination of:
  - strong prerequisite structure (items move together)
  - part-whole overlap (even with the corrected variant, the namespace score still correlates strongly with overall competence)
  - selection into submitting
- Practical implication: the `< 0.15` replacement rule does **not** identify candidates in this snapshot; redundancy/dependency signals are more informative.

### 2b) Inter-Test-Case Redundancy (Within Question)

- Pairwise within-question item pairs analyzed: **2,043**
- Near-redundant pairs (phi `> 0.90`): **704** (**34.46%**)
- Questions with at least one near-redundant pair: **84 / 84**
- Questions with `>=10` near-redundant pairs: **26**

By scope pairing (near-redundant pairs):

- private-public: **382**
- private-private: **176**
- public-public: **146**

Interpretation:

- Redundancy is not just within private tests; many public/private pairs are effectively measuring the same success state on the selected snapshots.
- This is the strongest "candidate for replacement/pruning" signal in Step 2.

### 2c) Test-Case Dependency Structure

- Directed dependency edges (support-filtered graph export): **2,213** across **84** questions
- Median dependency edge density per question (edges / possible ordered pairs): **0.536**
- Average edge density: **0.543**
- Questions with edge density `> 0.75`: **9**

Representative result (matches the anticipated pattern of strong chaining / near-equivalence):

- `ns_25t2_py21_2` Q22 (`Rotate Matrix Clockwise 90 degree`)
  - **8** items
  - **56 / 56** possible ordered edges flagged (edge density = **1.0**)
  - many pairwise phi correlations are `> 0.95`, including private-private and public-private pairs

Interpretation:

- The dependency graphs are often dense, not sparse.
- This means many test cases behave like prerequisites or near-duplicates rather than independent checks.

Follow-up extension (SCC condensation + transitive reduction):

- Full support-filtered dependency edges: **2,213**
- SCC-condensed transitive-reduced edges: **296** (**13.38%** of full edges)
- Total SCC components across analyzed questions: **362** (from **607** item nodes)
- Non-trivial SCCs (size > 1): **102**
- "Minimal new information" components (sink SCCs in reduced graphs): **99** across **84** questions
- Per-question medians:
  - SCC components: **4**
  - minimal new-information components: **1**

Interpretation:

- Transitive reduction confirms that many dense dependency graphs collapse to a very small backbone.
- In many questions, a single terminal SCC captures most of the incremental evaluative signal, while earlier tests mostly behave like prerequisites or equivalent checks.
- The reduced graphs in `analysis/classical_item_quality/dependency_graphs_reduced/` are the best artifact for deciding which test cases are genuinely adding new information.

### 2d) Exam-Level Reliability (Cronbach's Alpha)

Computed per namespace (`analysis/classical_item_quality/namespace_reliability_cronbach_alpha.csv`):

- Namespaces with defined alpha (submission-positive): **12**
- Namespaces with no alpha (zero submissions): **23**

For `cronbach_alpha_all_public_private_fill0`:

- median = **0.9716**
- min = **0.9578**
- max = **0.9806**

Interpretation:

- Reliability is extremely high on this binary item set.
- In this context, that does **not** necessarily mean the exams are optimally designed; it is also consistent with high redundancy and strong hierarchical gating.
- The combination of **very high alpha + heavy >0.90 redundancy** suggests many items are reinforcing the same latent trait/state.

### 2e) Public vs Private Test Case Analysis (Overfitting Proxy)

Baseline proxy (`analysis/classical_item_quality/public_private_gap_summary.csv`), among **42,918** submitter-question rows with both public and private snapshots:

- pass all public, fail >=1 private: **10 rows** (**0.02%**)
- pass all private, fail >=1 public: **169 rows** (**0.39%**)

Per-question pattern:

- Questions with any `public-all / private-not-all`: **10 / 84**
- Questions with any `private-all / public-not-all`: **30 / 84**
- Questions with `public-all / private-not-all >= 20%`: **0**

Same-code proxy (`analysis/classical_item_quality/public_private_gap_same_code_summary.csv`), among **42,916** rows with a same-`code_sha256` public/private pair:

- pass all public, fail >=1 private: **2,341 rows** (**5.45%**)
- pass all private, fail >=1 public: **169 rows** (**0.39%**)

Same-code per-question pattern:

- Questions with any `public-all / private-not-all`: **81 / 84**
- Questions with any `private-all / public-not-all`: **30 / 84**
- Questions with `public-all / private-not-all >= 20%`: **1 / 84**
  - `ns_25t2_py11_1` Q6 (`Card to Value Tuple`): **21.01%** (`58 / 276`)

Interpretation:

- The same-code pairing materially changes the conclusion: there **is** a meaningful public-pass/private-fail gap once we compare public and private results on the same submitted code.
- This is consistent with students passing visible public tests while still failing hidden/private checks on the exact same code snapshot (i.e., a plausible overfitting/generalization gap signal).
- The baseline last-public-before-submission proxy understated this because it mixed different code snapshots.

## Action-Oriented Takeaways for Evaluation Design

- Highest-priority candidates for review are **redundant** and **dependency-dense** test-case sets, not low-discrimination items (none were `< 0.15` in this snapshot).
- Public test cases need versioning stability (or version-aware item IDs) if you want clean item-level analytics across time within a namespace-question.
- Use the **same-code `code_sha256` public/private gap** (not the last-public-before-submission proxy) as the primary overfitting screen in future iterations.
- Use the **transitive-reduced SCC graphs** to identify the minimal set of test cases that contribute new information; large SCCs and high redundancy pairs are the first candidates for pruning/replacement.

# Step 3. Error Taxonomy

Manual note:

- This section is written manually from generated outputs in `analysis/error_taxonomy/`.
- The script does not write README text.

## Outputs

Primary outputs (see also `analysis/error_taxonomy/output_manifest.csv`):

- `selected_snapshot_taxonomy_rows.csv` (one row per student-question, with track selection, skeleton comparison, tree-sitter metrics, syntax taxonomy)
- `best_public_test_run_classification_rows.csv` (best public `test_run` outcome + runtime/wrong-output classifications from raw `CompilationResult.test_case_results`)
- `regression_rows.csv` (parseability and structural regression flags)
- `global_error_profile_multilabel.csv`
- `final_primary_taxonomy_summary.csv`
- `final_primary_taxonomy_by_term.csv`
- `final_primary_taxonomy_by_question.csv`
- `skeleton_modification_status_summary.csv`
- `syntax_error_taxonomy_summary.csv`
- `runtime_error_type_summary.csv`
- `wrong_output_subtype_summary.csv`
- `structural_inventory_by_track.csv`
- `structural_inventory_by_term.csv`
- `structural_inventory_by_question.csv`
- `non_submission_behaviour_by_term.csv`
- `scaffold_strip_status_summary.csv`

## Rebuild This Analysis

```bash
# ~2-10 minutes depending on cache/warm disk
uv run analysis/generate_error_taxonomy.py
```

## Method and Scope (Important)

- Population: full `151,778` student-question rows from `analysis/final_scores.csv`
- Track definitions (as requested):
- Track A submitters: latest submission code (submission event -> `code_sha256`)
- Track A non-submitters in submission-positive namespaces: last `test_run` snapshot
- Track B zero-submission namespaces: best public `test_run` snapshot (max public tests passed, tie-broken by recency)
- Coverage:
- `151,778 / 151,778` rows have a selected event and selected code hash (`100%`)
- `151,778 / 151,778` rows also have a best public `test_run` classification row (`100%`)
- Tree-sitter parser:
- `tree-sitter-python` is used on the selected snapshot code for Python questions, including non-`ast.parse()` code
- Non-Python rows are retained and explicitly marked `Unsupported language (non-Python)` (there are `18` such rows; C questions inside `ns_25t1_py_15_exe`)
- Critical data caveat (and fix implemented in the script):
- `code_snapshots.parquet` stores the **assembled evaluator file**, not just the student-edited region
- This includes per-question scaffolding (for example hidden prefix/suffix test harness code)
- The script strips `prefixed_code` / `suffixed_invisible_code` (and leading `uneditable_code` if present) from question JSON before structural analysis and skeleton comparison
- Strip diagnostics are exported in `scaffold_strip_status_summary.csv`
- Skeleton comparison:
- Skeleton comes from question JSON `allowed_languages[].code_template` (not from `question_metadata.csv`, which does not include skeleton text)
- `new_constructs_added` and `skeleton_constructs_removed_or_missing` are tree-sitter construct-count deltas relative to that skeleton
- `added_regions_structurally_coherent` is an approximation: `new_constructs_added > 0` and no tree-sitter `ERROR` / missing-token nodes in the extracted student code
- Syntax taxonomy (3d):
- Based on `ast.parse()` exception class/message plus tree-sitter error-context signals
- Categories are `Indentation error`, `Missing delimiters`, `Invalid syntax`
- Runtime errors (3e):
- Classified from the **first failing case** in the best public `test_run` by regexing traceback output in `test_case_results[].output`
- Many rows remain `Runtime Error (unspecified)` because the platform summary is generic and some traces do not expose a typed exception string
- Wrong-output taxonomy (3f):
- Implemented here as a **heuristic baseline**, not a validated LLM classifier
- `wrong_output_llm_review_sample.csv` exports up to 40 wrong-answer examples per question for future LLM/manual validation
- Regression (3g):
- Parseability regression uses full timeline `is_parseable` sequence and the final attempt snapshot
- Structural regression uses tree-sitter complexity comparisons on milestone snapshots (attempt final, best public, last parseable before final)
- Caveat: the current regression complexity metrics are hash-level and computed on the assembled snapshot text (scaffolding included); this is still useful for within-question deltas because scaffolding is mostly constant within a question, but it is less clean than the stripped selected-snapshot structural metrics
- Cross-term caveat:
- `t2` and `t3` are progressively filtered (weaker-by-construction) populations
- Cross-term differences are descriptive, not causal
- Within-term comparisons (for the same term cohort) remain the more defensible lens

## Findings

### Coverage and Track Composition

- Track A submitters: `42,918`
- Track A non-submitters (submission-positive namespaces): `11,112`
- Track B zero-submission namespaces: `97,748`
- No rows are left without a selected code snapshot in Step 3 (`0` missing)

### Scaffolding in Code Snapshots (Important for Interpretation)

- The raw snapshots include evaluator scaffolding; without stripping, structural inventory and skeleton-comparison results are misleading.
- After stripping:
- `prefix_suffix_not_found` is low in the Python tracks:
- Track A submitters: `0.85%`
- Track A non-submitters (submission-positive NS): `1.09%`
- Many rows are `partial_prefix_suffix` rather than `exact_prefix_suffix`, which is expected because snapshots often differ in trailing whitespace/newlines around injected sections.
- `no_scaffolding_config` rows are expected for questions whose JSON has no prefix/suffix scaffolding.

### 3c) Skeleton Modification Status (Selected Snapshot)

Overall (`151,778` rows):

- `Modified, structurally valid`: `128,005` (`84.34%`)
- `Modified, partially broken`: `10,847` (`7.15%`)
- `Unmodified skeleton`: `5,687` (`3.75%`)
- `Empty / trivial`: `3,628` (`2.39%`)
- `Modified, fundamentally broken`: `3,593` (`2.37%`)
- `Unsupported language (non-Python)`: `18` (`0.01%`)

By track (selected examples):

- Track A submitters: `Modified, structurally valid` `37,716 / 42,918` (`87.88%`)
- Track A submitters: `Modified, partially broken` `4.49%`
- Track A submitters: `Modified, fundamentally broken` `1.97%`
- Track A submitters: `Unmodified skeleton` `3.28%`
- Track A non-submitters (submission-positive NS): `Modified, structurally valid` `7,694 / 11,112` (`69.24%`)
- Track A non-submitters (submission-positive NS): `Modified, partially broken` `16.68%`
- Track A non-submitters (submission-positive NS): `Modified, fundamentally broken` `4.71%`
- Track A non-submitters (submission-positive NS): `Unmodified skeleton` `5.46%`
- Track B zero-submission namespaces: `Modified, structurally valid` `82,595 / 97,748` (`84.50%`)
- Track B zero-submission namespaces: `Modified, partially broken` `7.23%`
- Track B zero-submission namespaces: `Modified, fundamentally broken` `2.27%`
- Track B zero-submission namespaces: `Unmodified skeleton` `3.76%`

Interpretation:

- The "modified, partially broken" population is substantial, especially in Track A non-submitters in submission-positive namespaces (`16.68%`).
- This supports the intervention hypothesis from the prompt: many failures are not "no attempt"; they are structured attempts with local syntax/assembly problems.

### Structural Distance from Skeleton (3b / 3c)

Among Python rows:

- Students usually add structure beyond the skeleton:
- Track A submitters: `92.54%` have `new_constructs_added > 0`
- Track A non-submitters (submission-positive NS): `86.54%`
- Track B zero-submission namespaces: `91.36%`
- Added structure is often coherent:
- Track A submitters: `94.41%` of rows with additions have `added_regions_structurally_coherent = true`
- Track A non-submitters (submission-positive NS): `78.76%`
- Track B zero-submission namespaces: `91.40%`

Interpretation:

- The main gap for Track A non-submitters in submission-positive namespaces is not "no editing"; it is a higher rate of structurally broken additions.

### 3b / 3h) Structural Inventory (Curriculum Signal, With Caveats)

The structural inventory is much more plausible after stripping scaffolding. Selected-snapshot presence rates by track:

- `for_loop`: ~`41%` across all three tracks (`40.57%`, `43.39%`, `40.96%`)
- `list_comp`: low (`3.24%` to `3.89%`)
- `dict_comp`: very low (`0.22%` to `0.39%`)
- `while_loop`: low (`2.09%` to `4.04%`)

Important interpretation caveat:

- `function_def`, `return_stmt`, and some `if` usage are inflated by function-type templates (skeleton-provided code), so they are not pure "student-chosen construct" measures.
- Use `new_constructs_added` and question-level breakdowns for a cleaner curriculum signal.

### 3d) Syntax Error Taxonomy (Selected Snapshot, Python Rows with `ast.parse()` failure)

The syntax mix is strikingly stable across tracks.

- Track A non-submitters (submission-positive NS), among non-parseable Python snapshots (`3,221`): `Invalid syntax` `61.88%`, `Indentation error` `23.13%`, `Missing delimiters` `15.00%`
- Track A submitters, among non-parseable Python snapshots (`3,775`): `Invalid syntax` `59.21%`, `Indentation error` `25.48%`, `Missing delimiters` `15.31%`
- Track B zero-submission namespaces, among non-parseable Python snapshots (`12,379`): `Invalid syntax` `61.60%`, `Indentation error` `23.44%`, `Missing delimiters` `14.96%`

Tree-sitter context signal (all tracks combined, error-context tags):

- Error contexts are concentrated in function bodies (`42.9%` of tagged contexts), then conditionals (`12.6%`), loops (`10.7%`), and top-level (`11.09%`).

Tree-sitter adds coverage beyond `ast.parse()`:

- Some rows are `ast`-nonparseable but tree-sitter still yields a structurally coherent tree (no `ERROR`/missing-token nodes):
- Track A submitters: `674`
- Track A non-submitters (submission-positive NS): `558`
- Track B zero-submission namespaces: `2,074`

### 3e) Runtime Errors from Best Public `test_run`

Best public `test_run` outcomes by track:

- Track A submitters: `All Cases Passed` `25,745` (`59.99%`), `Wrong Answer` `9,894` (`23.05%`), `Runtime Error` `7,236` (`16.86%`)
- Track A non-submitters (submission-positive NS): `Runtime Error` `6,898` (`62.08%`), `Wrong Answer` `4,101` (`36.91%`), `All Cases Passed` `70` (`0.63%`)
- Track B zero-submission namespaces: `All Cases Passed` `47,661` (`48.76%`), `Runtime Error` `26,180` (`26.78%`), `Wrong Answer` `23,589` (`24.13%`)

Runtime subtype mix (within runtime-error rows) is similar across tracks:

- Dominant buckets are `Runtime Error (unspecified)`, `TypeError`, and `NameError`
- Example shares:
- Track A non-submitters (submission-positive NS): `Runtime Error (unspecified)` `50.9%`, `TypeError` `16.54%`, `NameError` `12.87%`
- Track B zero-submission namespaces: `52.43%`, `19.42%`, `10.88%`

### 3f) Wrong-Output Failure Taxonomy (Heuristic Baseline)

This is a heuristic baseline using first-failing-case output vs expected output from the best public `test_run` (not a validated LLM classifier yet).

Within wrong-answer rows:

- Track A submitters: `Wrong output - partial correctness` `58.39%`, `Wrong output - logic/completely wrong` `40.34%`
- Track A non-submitters (submission-positive NS): `Wrong output - logic/completely wrong` `87.56%`, `Wrong output - partial correctness` `11.56%`
- Track B zero-submission namespaces: `Wrong output - logic/completely wrong` `52.79%`, `Wrong output - partial correctness` `45.52%`

Formatting-only and simple off-by-one heuristics are rare in this baseline (`<=1.25%` each track).

Practical implication:

- The submission-positive non-submitter group looks qualitatively more "stuck" on best public runs than submitters who eventually submit (runtime-heavy, and among wrong answers mostly logic-level failures).

### 3g) Regression Detection

Parseability regression (among Python rows ending non-parseable):

- Track A submitters: `1,831 / 3,924` (`46.66%`) had an earlier parseable snapshot
- Track A non-submitters (submission-positive NS): `1,429 / 3,212` (`44.49%`)
- Track B zero-submission namespaces: `5,910 / 13,022` (`45.38%`)

Peak-to-final public regression (best public > last public pass count):

- Track A submitters: `3.18%`
- Track A non-submitters (submission-positive NS): `2.29%`
- Track B zero-submission namespaces: `2.88%`

Structural regression proxies (tree-sitter complexity decrease):

- vs best public snapshot: low in all tracks (`0.46%` to `0.87%`)
- vs last parseable snapshot before final:
- Track A non-submitters (submission-positive NS): `9.38%`
- Track B zero-submission namespaces: `4.09%`
- Track A submitters: `1.88%`

Interpretation:

- Regression is real and common for parseability (~45% of non-parseable endings had earlier parseable code).
- Structural simplification/backtracking is especially common in Track A non-submitters in submission-positive namespaces.

### 3h) Global Error Profile and Non-Submission Behaviour

Selected lines from `global_error_profile_multilabel.csv`:

- `Unmodified skeleton`: `5,687` total (`1,409` submitters, `607` Track A non-submitters, `3,671` Track B)
- `Modified, partially broken`: `10,847` total
- `Modified, fundamentally broken`: `3,593` total
- `Regression: earlier parseable, final non-parseable`: `9,170` total
- `Wrong output - partial correctness`: `16,988` total
- `Wrong output - logic/completely wrong`: `20,035` total

Track-level final primary taxonomy (`final_primary_taxonomy_summary.csv`) highlights:

- Track A non-submitters (submission-positive NS): `Runtime error` `4,002`, `Wrong output` `3,581`, `Public full pass, no submit` `70`
- Track B zero-submission namespaces: `Public full pass, no submit` `47,610`, `Wrong output` `19,833`, `Runtime error` `14,933`

This sharp difference reinforces the earlier instrumentation/capture caveat:

- Track B (zero-submission namespaces) is dominated by students who often reach a public-pass state but have no submission capture.
- Track A non-submitters in submission-positive namespaces are a different population and look much more genuinely stuck on observed best public runs.

Cheap term-split check for pooled non-submission behaviour (requested follow-up):

- Track A non-submitters (submission-positive NS):
- `25t2`: public-pass evidence `5.38%`, stuck/thrash proxy (`>10` test runs and zero public passes) `27.94%`
- `25t3`: public-pass evidence `6.49%`, stuck/thrash proxy `27.12%`
- Interpretation:
- In this snapshot, the coarse non-submission subtype mix is very similar between `25t2` and `25t3` within submission-positive namespaces.

## Action-Oriented Takeaways for Step 3

- The "modified, partially broken" and syntax-error populations are large enough to justify tooling/interventions aimed at **mechanical repair** (linting, syntax-focused feedback, clearer compiler/parser messages).
- Separate analyses for submission-positive non-submitters (genuinely stuck population) and zero-submission namespaces (instrumentation/capture problem).
- Treat structural inventory metrics as useful after scaffolding stripping, but still partly template-influenced for constructs commonly provided by skeletons.
- Promote `regression_rows.csv` and `selected_snapshot_taxonomy_rows.csv` to the next step (e.g., targeted feedback design / remediation experiments), especially rows flagged by `parseability_regression_flag`, `skeleton_modification_status = Modified, partially broken`, and `best_public_runtime_error_type IN (TypeError, NameError, ValueError)`.

# Step 4. The Syntax Bottleneck — Quantified

This step assembles Steps 1–3 into a single, defensible decomposition of failure modes, with a dual-track design:

- Track A: namespaces with submission capture
- Track B: zero-submission namespaces (best observed `test_run` snapshot only)

As in earlier sections, cross-term (`t1`/`t2`/`t3`) comparisons are descriptive only because later terms are progressively filtered (weaker-by-construction) populations. The Step 4 waterfall is primarily a **within-track decomposition**, not a causal comparison across terms.

## Process / Rebuild

Script:

- `analysis/generate_syntax_bottleneck_quantified.py`

Rebuild command:

```bash
uv run analysis/generate_syntax_bottleneck_quantified.py
```

Generated outputs (ignored by git):

- `analysis/syntax_bottleneck_quantified/`

What the script does:

- Reuses Step 3 row-level outputs (tree-sitter structural status, regression flags, selected snapshots) and Step 1/Step 3 outcome summaries
- Builds a dual-track parseability baseline (AST + tree-sitter split)
- Quantifies regression:
- parseability regression (earlier parseable, final non-parseable)
- peak-to-final public test-pass regression
- structural regression (tree-sitter complexity decrease)
- Implements a conservative **rule-based syntax repair** baseline and re-scores:
- Track A submitters on private tests
- Track B best snapshots on public tests
- Computes a formatting-tax estimate (whitespace normalization baseline) for Track A parseable wrong-answer submissions
- Builds a gating waterfall for Track A, Track B, and Combined
- Quantifies skeleton effectiveness proxies (syntax ERROR-node location and error rates vs modification extent)

Important Step 4 semantics:

- Track A in the waterfall combines:
- submitters scored on **private final submission outcomes**
- non-submitters (submission-positive namespaces) scored on **best public `test_run` outcomes**
- Track B uses **best public `test_run` outcomes** (because submission/private outcomes are unavailable)
- Therefore, Track A vs Track B percentages are useful for decomposition and guardrail comparisons, but not a pure apples-to-apples performance comparison.

Important Step 4 implementation note:

- The initial Step 4 run exposed duplicate Track A private-final rows in `track_a_private_final_rows.csv` (multiple records per student-question after timeline joins).
- The script now deduplicates by `(namespace, problem_id, student_id)`, preferring rows with more private-case coverage / passes, and was re-run.
- After the fix, `gating_waterfall_rows.csv` matches the Step 0 population exactly: `151,778` rows.

LLM correction status:

- The LLM syntax-correction pipeline is wired into the script but was **not run** in this environment because no non-empty API key was configured (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` all absent).
- `syntax_repair_llm_summary.csv` and `syntax_repair_comparison_summary.csv` explicitly record this skipped state.

## Findings

### 4a) Parseability Baseline (Dual-Track, Tree-Sitter-Enriched)

The tree-sitter split within AST-nonparseable code is the key upgrade: it separates "mechanically close" code from fundamentally broken code.

From `parseability_baseline_dual_track_prompt_table_pct.csv`:

- Parseable (`ast.parse`):
- Track A submitters: `91.20%`
- Track A non-submitters (submission-positive NS): `71.01%`
- Track B best snapshot: `87.32%`
- Non-parseable, structure evident (tree-sitter few/local errors):
- Track A submitters: `4.48%`
- Track A non-submitters (submission-positive NS): `16.68%`
- Track B best snapshot: `7.22%`
- Non-parseable, fundamentally broken:
- Track A submitters: `1.97%`
- Track A non-submitters (submission-positive NS): `4.70%`
- Track B best snapshot: `2.27%`
- Unmodified skeleton / empty:
- Track A submitters: `5.66%`
- Track A non-submitters (submission-positive NS): `9.37%`
- Track B best snapshot: `5.98%`

Interpretation:

- The syntax bottleneck is real, but the dominant syntax-gated population is **mechanical / structure-evident**, not fundamentally broken.
- This is most pronounced in Track A non-submitters in submission-positive namespaces (`16.68%`), which is the most policy-relevant "genuinely stuck" group.

### 4b) Regression Analysis

From `regression_summary_dual_track.csv`:

- Track A (combined):
- rows: `54,030`
- Python rows ending non-parseable: `7,136`
- earlier parseable among those: `3,260` (`45.68%`)
- peak-to-final public test-pass regression: `1,621` (`3.00%`)
- structural regression vs best public snapshot: `424` (`0.78%` of Python rows)
- structural regression vs last parseable snapshot: `1,850` (`3.42%`)
- Track B:
- rows: `97,748` (`97,730` Python)
- Python rows ending non-parseable: `13,022`
- earlier parseable among those: `5,910` (`45.38%`)
- peak-to-final public test-pass regression: `2,815` (`2.88%`)
- structural regression vs best public snapshot: `732` (`0.75%`)
- structural regression vs last parseable snapshot: `3,996` (`4.09%`)

Interpretation:

- About **45%** of students who end non-parseable had a parseable snapshot earlier, consistent across Track A and Track B.
- This is strong evidence that a meaningful share of syntax failure is an **editing/maintenance process failure**, not purely an inability to construct Python at all.

### 4c / 4d) Auto-Correct Syntax and Re-score (Rule-Based Baseline; LLM Skipped)

Rule-based syntax repair is implemented as a conservative baseline (tabs/indent normalization, missing colons in obvious headers, bracket balancing, minimal empty-block `pass` insertion, etc.), then re-evaluated against:

- Track A submitters: private tests
- Track B best snapshots: public tests

From `syntax_repair_rule_based_summary.csv`:

- Track A submissions (private), parse-fail Python rows targeted: `3,775`
- parse rescued: `181` (`4.79%`)
- any test-pass gain: `8` (`0.21%`)
- full pass after rule fix: `3` (`0.08%`)
- mean score gain: `2.67`
- Track B best snapshot (public), parse-fail Python rows targeted: `12,379`
- parse rescued: `514` (`4.15%`)
- any test-pass gain: `35` (`0.28%`)
- full pass after rule fix: `10` (`0.08%`)
- mean score gain: `3.735`

Structural-status split (from `syntax_repair_rule_based_effect_by_structural_status.csv`) matters:

- `Modified, partially broken` rows have materially better parse rescue rates than `Modified, fundamentally broken`
- Example:
- Track A submitters, partially broken: `4.42%` parse rescue vs fundamental `0.71%`
- Track B, partially broken: `4.20%` parse rescue vs fundamental `1.08%`

Interpretation:

- A simple rule-based repair recovers only a small fraction of rows and very rarely changes outcomes.
- This suggests many syntax failures are not just one-token fixes, even in the "mechanical" bucket.
- The LLM-assisted step remains the main unresolved test for how much additional recoverable score is locked behind localized syntax problems.

### 4e) Formatting Tax (Track A)

From `formatting_tax_track_a_summary.csv`:

- Parseable wrong-answer private submission rows: `11,540`
- Rows fully rescued by simple whitespace normalization: `0` (`0.00%`)
- Wrong-answer fail cases rescued by formatting normalization: `0 / 33,226` (`0.00%`)

Interpretation:

- In this snapshot, the formatting tax appears negligible under a simple whitespace-normalization baseline.
- Either the evaluator already normalizes common formatting differences, or most wrong-answer failures are substantive (logic/edge/runtime), not presentation mismatches.

### 4f) Gating Waterfall (Full Population, Dual-Track)

From `gating_waterfall_pct.csv` (counts in `gating_waterfall_counts.csv`):

Combined (`151,778` rows):

- Unmodified skeleton / didn't attempt: `6.14%`
- Syntax gated — mechanical: `7.14%`
- Syntax gated — fundamental: `2.36%`
- Formatting gated: `0.25%`
- Edge-case gated: `7.35%`
- Genuine logic failure: `26.72%`
- Partial pass: `3.21%`
- Full pass: `46.83%`

Track A (mixed private/public semantics as noted above):

- Syntax gated — mechanical: `6.99%`
- Syntax gated — fundamental: `2.53%`
- Formatting gated: `0.16%`
- Genuine logic failure: `30.68%`
- Partial pass: `9.01%`
- Full pass: `43.40%`

Track B (best-public snapshot):

- Syntax gated — mechanical: `7.22%`
- Syntax gated — fundamental: `2.27%`
- Formatting gated: `0.30%`
- Edge-case gated: `10.97%`
- Genuine logic failure: `24.53%`
- Full pass: `48.72%`

Key decomposition insight:

- The syntax bottleneck is substantial (`~9.5%` combined when mechanical + fundamental syntax gates are combined), but **genuine logic failure** is the single largest failure bucket (`26.72%`).
- The tree-sitter split is important operationally:
- `7.14%` combined are **mechanical syntax-gated** (structure evident; tooling/help likely to matter)
- `2.36%` combined are **fundamental syntax-gated** (more foundational instruction likely needed)

### 4g) Skeleton Effectiveness Analysis

Two complementary views were computed:

- ERROR-node location proxy (where syntax problems occur relative to skeleton lines)
- Error rate vs modification extent (how far students move beyond the skeleton)

Error-node location proxy (from `skeleton_effectiveness_error_location_summary_track_only.csv`):

- Track A non-submitters (submission-positive NS): most ERROR nodes are in `beyond_skeleton_line_range` (`3,410`) or `skeleton_line_modified` (`3,355`), with fewer on `skeleton_unchanged_line` (`964`)
- Track A submitters: `skeleton_line_modified` (`4,796`) and `beyond_skeleton_line_range` (`4,034`) dominate over `skeleton_unchanged_line` (`1,413`)
- Track B: same pattern (`14,304`, `11,370`, `3,604`)

Interpretation:

- Most syntax errors occur in **student-added or student-modified regions**, not untouched skeleton code.
- This suggests the skeleton is generally not the primary source of syntax breakage.

Modification extent vs error rate (from `skeleton_effectiveness_error_rate_by_modification_extent.csv`):

- Error rates are highest when `new_constructs_added = 0`:
- Track A non-submitters: `46.59%` AST-nonparseable, `41.64%` tree-sitter broken
- Track A submitters: `30.53%`, `27.69%`
- Track B: `34.31%`, `31.33%`
- Error rates generally decrease once students add more structure (`4-6` or `7+` new constructs)

Interpretation:

- The riskiest state is not "complex code"; it is **shallow modification of the skeleton without successful structural extension**.
- This is consistent with students getting stuck early while editing within the template.

## What Step 4 Adds Beyond Steps 1–3

- A single waterfall that separates:
- no-attempt / minimal attempt
- mechanical syntax gating
- fundamental syntax gating
- formatting (negligible here)
- edge-case vs logic failure
- The tree-sitter-informed syntax split gives stakeholders a clear intervention fork:
- tooling / parser feedback / linting for the mechanical bucket
- curriculum / foundational programming support for the fundamental bucket
- Regression analysis shows that many syntax failures are **not purely initial incompetence**: students often had a parseable state earlier and lost it during iteration.

## Practical Next Steps (Step 4 Driven)

- Run the LLM correction arm (Track A private, Track B public) in an environment with an API key to quantify the recoverable portion of the mechanical syntax gate.
- Use the Step 4 row-level outputs to target intervention design:
- `syntax_repair_rule_based_rows.csv`
- `gating_waterfall_rows.csv`
- `skeleton_effectiveness_error_location_summary*.csv`
- For stakeholder communication, present the waterfall with the explicit caveat that Track B "full pass" is public-best-snapshot and Track A mixes private-final (submitters) with public-best (non-submitters).

# Step 5. Process Analysis — What the Snapshots Reveal

This step analyses **how** students work through a question over time (not just the final outcome), using the full event timeline and tree-sitter structural tracking.

This step is less affected by the Track A / Track B split than score-based steps because both tracks have timeline events. However, interpretation is still shaped by:

- submission capture coverage differences (Track B zero-submission namespaces),
- progressive filtering across terms (`t2` and `t3` are weaker-by-construction populations),
- and an important timeline sampling limitation described below.

## Process / Rebuild

Script:

- `analysis/generate_process_analysis.py`

Rebuild command:

```bash
uv run analysis/generate_process_analysis.py
```

Generated outputs (ignored by git):

- `analysis/process_analysis/`

Key outputs:

- `attempt_process_features.csv` (5a + 5b per-attempt summaries)
- `attempt_construct_first_appearance.csv` (5b construct timelines)
- `attempt_archetypes.csv` (5c archetype flags + primary archetype)
- `archetype_outcomes_*.csv` and `archetype_*_by_{question,term}.csv` (5d)
- `error_recovery_episodes_public.csv`, `error_recovery_by_type.csv`, `error_recovery_syntax_intent_split.csv` (5e)
- `public_test_run_state_rows.parquet`, `death_spiral_*.csv` (5f)
- `timeline_event_features_enriched.parquet` (event-level trajectory source)

What the script does:

- Reuses Step 3 row-level metadata (`selected_snapshot_taxonomy_rows.csv`, `regression_rows.csv`) for track, term, wave, and outcome fields
- Parses all unique `(namespace, problem_id, code_sha256)` snapshots seen in the timeline with tree-sitter (question-aware scaffold stripping)
- Joins structural features back onto the full event timeline (`2,057,658` events)
- Builds per-attempt process features and structural evolution summaries
- Classifies behavioural archetypes (multi-label + primary)
- Computes recovery analysis on public `test_run` sequences
- Builds a tree-sitter-enriched death-spiral state analysis (public test-run state space + Track A synthetic State 5 terminal transitions)

### Important Step 5 Caveats (Read Before Interpreting Timing Metrics)

- **Timeline sampling is sparse**:
- `submission_timeline.parquet` in this snapshot contains only `test_run` and `submission` events (no `saved_code` rows).
- Therefore "time to first parseable code", "first construct appearance", and structural trajectories are measured at **run/submission checkpoints**, not at continuous edit/save granularity.
- This is why many constructs have `median_first_event_idx = 1` and `median_first_seconds = 0`: students often write code before the first recorded `test_run`.

- **Runtime subtype detail is limited in the timeline**:
- `summary` is present (`Runtime Error`, `Wrong Answer`, etc.), but `reason` is usually blank in timeline rows.
- Step 5 recovery therefore uses a robust process-level taxonomy (`SyntaxError`, `Runtime Error`, `Wrong Answer`, `Timeout`, etc.) and a tree-sitter syntax split, but not a reliable per-run `TypeError`/`NameError` split.

- **Death-spiral "success" is a mixed endpoint**:
- State analysis is built on public `test_run` states for everyone.
- `eventual_success_state4_or_5` means:
- reached `State 4` (all public tests passed), or
- for Track A submitters, reached `State 5` (final full private pass).
- This is useful for process/decision-state analysis, but Track A vs Track B success rates are still not apples-to-apples.

- **Cross-term comparisons remain descriptive only**:
- `t2` and `t3` cohorts are progressively filtered.
- Within-track/within-term process comparisons are the safer lens.

## Findings

### Coverage and Event Structure (Step 5 Foundation)

From `timeline_event_features_coverage.csv` and `timeline_event_features_enriched.parquet`:

- Attempts covered: `151,778 / 151,778`
- Timeline event rows: `2,057,658`
- `test_run` rows: `2,002,516`
- Public `test_run` rows: `1,724,016`
- Private `test_run` rows: `278,500`
- Submission rows: `55,142`

From `qhash_tree_sitter_parse_summary.csv`:

- Unique question-hash snapshots parsed with tree-sitter: `1,386,166`
- Tree-sitter parseable (no `ERROR`/missing-token nodes): `1,116,160` (`80.52%`)
- Tree-sitter error-bearing snapshots: `270,006`
- "Structure evident" among all qhash snapshots: `204,685`

From `qhash_structural_features_summary.csv`:

- Scaffold stripping coverage is high and consistent:
- `partial_prefix_suffix`: `75.49%`
- `no_scaffolding_config`: `21.08%`
- `exact_prefix_suffix`: `3.09%`
- `prefix_suffix_not_found`: `0.33%`

Interpretation:

- Step 5 has full-population coverage at the attempt level and broad structural coverage at the snapshot level.
- The snapshot-level tree-sitter pass is feasible and robust enough to support trajectory/state analysis at scale.

### 5a) Per-Attempt Timeline Features

From `process_feature_summary_global.csv`:

- Median active time: `997s` (~16.6 min)
- `p90` active time: `5,545s` (~92.4 min)
- Median test runs: `8`
- `p90` test runs: `30`
- Median public test runs: `7`
- Attempts with any public test pass: `61.90%`
- Attempts with any public all-pass: `48.41%`
- Parseability regression flag (Step 3 regression rows): `6.04%` of all attempts
- Peak-to-last-public regression flag: `2.92%` of all attempts

By track (from `process_feature_summary_by_track.csv` and `attempt_archetypes.csv`):

- Track A non-submitters (submission-positive NS):
- median test runs `6`, `p90 = 24`
- median active time `604s`
- median parseable fraction `0.7727`
- any large deletion event `4.70%`
- any structural regression event `20.71%`
- Track A submitters:
- median test runs `9`, `p90 = 34`
- median active time `1,210s`
- median parseable fraction `0.9688`
- any structural regression event `17.82%`
- Track B:
- median test runs `8`, `p90 = 29`
- median active time `976s`
- median parseable fraction `0.9444`
- any structural regression event `17.57%`

Important metric caveat (useful for future analysis):

- `pct_public_monotonic` is high across tracks (`~70–81%`), but this includes **flat** trajectories (e.g., repeatedly passing 0 tests).
- Monotonicity alone is therefore a weak proxy for "good debugging"; pair it with improvement events or state transitions.

### 5b) Structural Evolution Tracking (Tree-Sitter, Full Population)

From `structural_evolution_patterns_by_track.csv`:

- Track A non-submitters (submission-positive NS) are concentrated in:
- `Flat / minimal structural change` + `No/low errors` (`24.25%`)
- `Oscillating / restructuring` + `Fluctuating errors` (`16.38%`)
- `Flat / minimal structural change` + `Persistent errors` (`7.08%`)

Interpretation:

- The non-submitter process picture is not one thing:
- a large group stays structurally flat (often not progressing beyond an initial approach),
- another large group repeatedly restructures while error counts fluctuate (process instability).

Construct timeline / "what appears at all?" (from `construct_first_appearance_summary_global.csv`):

- Ever observed in an attempt:
- `for_loop`: `46.71%`
- `while_loop`: `5.13%`
- `list_comp`: `4.53%`
- `dict_comp`: `0.41%`
- `try_stmt`: `1.45%`
- `class_def`: `0.02%`

Interpretation:

- Low use of list/dict comprehensions persists even when measured over the full process (not just final snapshots).
- Many constructs appear at event index `1` because the timeline is sampled at runs/submissions only (not continuous saves), so the construct timing columns are best read as "first observed checkpoint", not "first typed character."

### 5c / 5d) Behavioural Archetypes and Outcomes

The initial rule set left a large residual `Other` bucket, so the final Step 5 classifier uses a stricter **primary archetype** assignment plus additional rule-based trajectory signatures (derived from the same structural/error trajectory patterns used in 5b).

This resolves the archetype story without switching to opaque clustering:

- `Other` falls from `52.64%` to `6.40%` of attempts (primary archetype)
- the remaining residual `Other` is mostly mixed flat/declining trajectories rather than a single dominant pattern
- "late regression" does not emerge as a separate residual archetype: in the final classifier, late-regression-like attempts are already absorbed by `Regression` (`0%` of residual `Other` have `peak_to_final_public_regression > 0`)

Primary archetype distribution (from `archetype_outcomes_primary_summary.csv`):

- `Minimal-change solver`: `28,140` attempts (`18.54%`), success (`State 4/5`) `77.27%`
- `Volatile reworker`: `26,937` attempts (`17.75%`), success `35.95%`
- `Steady builder`: `24,203` attempts (`15.95%`), success `89.04%`
- `Builder with setbacks`: `12,576` attempts (`8.29%`), success `41.76%`
- `Incremental debugger`: `11,626` attempts (`7.66%`), success `77.65%`
- `Regression`: `11,625` attempts (`7.66%`), success `5.65%`
- `Other` (residual): `9,713` attempts (`6.40%`), success `35.48%`
- `Skeleton-only`: `9,315` attempts (`6.14%`), success `0.48%`
- `One-shot`: `7,625` attempts (`5.02%`), success `9.44%`
- `Stuck and abandoned`: `4,209` attempts (`2.77%`), success `4.11%`
- `Thrasher`: `2,746` attempts (`1.81%`), success `43.59%`
- `Flat stuck`: `2,533` attempts (`1.67%`), success `0.12%`
- `Late starter`: `530` attempts (`0.35%`), success `25.66%`

How to read the new archetypes:

- `Minimal-change solver`: little structural churn, low observed error churn, few runs (`median public runs = 3`) and very short active time (`37s`) with high success; this is the largest "quietly successful" group that was previously hidden inside `Other`
- `Volatile reworker`: repeated restructuring with fluctuating/decreasing/no-low error trajectories and many runs (`median public runs = 18`, `median active time = 3,223s`); this is a broad unstable-process group distinct from the stricter `Thrasher`
- `Builder with setbacks`: monotonic structural build-up with some dips/error fluctuations; a relaxed near-steady-builder category capturing attempts that improve but do not meet the strict `Steady builder` thresholds
- `Flat stuck`: minimal structural change with persistent/increasing syntax-error burden; near-zero success and short/low-progress timelines

Flag-summary prevalence remains useful for overlapping process signatures (from `archetype_outcomes_flags_summary.csv`):

- `Minimal-change solver` signature appears in `32.53%` of attempts
- `Volatile reworker` signature appears in `33.17%`
- `Builder with setbacks` signature appears in `16.69%`
- `Flat stuck` signature appears in `4.29%`

The process-teaching signal remains strong:

- Within **Track A submitters** (from `attempt_archetypes.csv`, primary archetypes):
- `Incremental debugger`: median active time `2,153s`, median public runs `13`, success `76.81%`
- `Thrasher`: median active time `4,706s`, median public runs `37`, success `47.44%`
- `Steady builder`: median active time `667s`, median public runs `6`, success `89.49%`

Interpretation:

- Better process beats more effort: the thrasher group spends roughly **2.2x** the time of incremental debuggers (and ~7x steady builders) but has much worse outcomes.
- The new archetypes make this story more complete by separating high-success minimal-change solvers from unstable reworkers instead of collapsing both into `Other`.

Track-specific archetype mix (from `archetype_flags_by_term.csv` and `attempt_archetypes.csv`):

- Track A non-submitters (submission-positive NS) have very high:
- `Regression` (~`19.6–19.9%` in `25t2`/`25t3`)
- `Stuck and abandoned` (~`12.0–12.7%`)
- and almost no `Incremental debugger` (`~0.3%`) or `Thrasher` (`~0.2–0.4%`)

Interpretation:

- The genuinely stuck non-submitter population often fails **early and quietly** (regression/abandonment), not necessarily via high-run-count thrashing.

Questions that induce disproportionate thrashing (primary archetype, `>=200` attempts; from `archetype_primary_by_question.csv`):

- `Pattern printing - Centered Triangle Of Zeroes`:
- `25t1_py12_2`: `12.59%` thrasher primary
- `25t1_py12_1`: `10.11%`
- Also elevated:
- `Reversed Squares of List Elements` (`7.08%`)
- `Pangram Check` (`6.96%`)
- `File Content Zig-Zag Shift` (`6.91%` in one namespace variant)

### 5e) Recovery Analysis by Error Type (Public `test_run` Sequences)

From `error_recovery_by_type.csv`:

- `SyntaxError (structure evident)`:
- episodes `111,833`
- resolved within attempt `87.61%`
- median resolution time `42s`
- persists to final public run in `20.94%` of attempts that ever had this error
- `SyntaxError (no structure)`:
- episodes `69,425`
- resolved within attempt `79.58%`
- median resolution time `47s`
- persists to final public run in `30.27%` of attempts
- `Runtime Error` (generic timeline-level bucket):
- episodes `177,879`
- resolved within attempt `87.60%`
- persists to final public run in `26.29%` of attempts
- `Wrong Answer`:
- episodes `208,952`
- resolved within attempt `82.63%`
- persists to final public run in `39.03%` of attempts (highest among major buckets)

Syntax structural-intent split (from `error_recovery_syntax_intent_split.csv`) confirms the Step 3 hypothesis:

- `SyntaxError (structure evident)` is more recoverable than `SyntaxError (no structure)`:
- resolved within 1 public run: `50.33%` vs `43.70%`
- resolved within 5 public runs: `81.62%` vs `71.94%`
- persists to final public run: `20.94%` vs `30.27%`

Interpretation:

- Tree-sitter’s structural-intent split is not cosmetic; it corresponds to materially different recovery trajectories.
- This is exactly the distinction between a mechanical syntax problem and a deeper structural problem.

### 5f) Death Spiral / Absorbing-State Analysis (Tree-Sitter-Enriched State Space)

State space used in public `test_run` sequences:

- `S0` no code beyond skeleton
- `S1` syntax broken, no recoverable structure
- `S1b` syntax broken, structure evident
- `S2` parseable, passes 0 public tests
- `S3` passes some (not all) public tests
- `S4` passes all public tests
- `S5` (synthetic terminal for Track A full private pass; transitions appended from last public state)

Public state distribution by track (from `public_state_distribution_by_track.csv`):

- Track A non-submitters (submission-positive NS) public runs are dominated by:
- `S2_parseable_zero`: `64.79%`
- `S1b_syntax_structure`: `18.29%`
- `S1_syntax_fundamental`: `13.80%`
- `S4_public_all`: only `0.08%`

Combined eventual success from state occurrence (from `death_spiral_state_eventual_success_by_state.csv`):

- `S0`: `6.16%`
- `S1`: `21.77%`
- `S1b`: `27.72%`
- `S2`: `35.50%`
- `S3`: `44.12%`
- `S4`: `100.00%`

Interpretation:

- `S1b` is meaningfully more recoverable than `S1` in the aggregate, which supports the intended mechanical-vs-fundamental syntax split.

Time-conditional absorption (`death_spiral_time_conditional_absorption.csv`) sharpens that result:

- Track A submitters:
- at `0–25%` elapsed, `S1b` vs `S1`: `40.57%` vs `32.90%` eventual success
- at `75–100%` elapsed: `28.64%` vs `21.70%`
- Track B:
- at `0–25%`: `31.89%` vs `26.16%`
- at `75–100%`: `20.08%` vs `14.38%`
- Track A non-submitters (submission-positive NS):
- both `S1` and `S1b` are near-zero (`<1.1%`) at all elapsed bins

Interpretation:

- `S1b` is consistently more recoverable than `S1` in the broader population.
- But in the genuinely stuck non-submitter group (submission-positive namespaces), being in either syntax-broken state is already a near-terminal condition on observed public-run trajectories.

Transition structure (from `death_spiral_transition_matrix_combined.csv` and `death_spiral_transition_difficulty.csv`):

- Strong self-loops (students staying in the same state next run):
- `S2 -> S2`: `78.93%`
- `S3 -> S3`: `72.40%`
- `S1 -> S1`: `56.72%`
- `S1b -> S1b`: `52.37%`
- Upward movement is possible but limited:
- `S1 -> S2`: `24.75%`
- `S1b -> S2`: `27.96%`
- direct `S1 -> S4`: `1.96%`
- direct `S1b -> S4`: `2.79%`

Absorbing-state candidate (using `<5%` eventual success threshold, from `death_spiral_absorbing_candidates.csv`):

- `S0_no_code` (`4.48%` combined eventual success by occurrence)

Interpretation:

- The main "death spiral" in this dataset is not only syntax-broken states; it is also the huge `S2` self-loop (parseable, but 0 public tests passed) where students often churn without crossing into partial correctness.
- This suggests interventions should target the `S2 -> S3` transition (logic/debugging progression), not just syntax repair.

## Additional Insights Useful for Future Analysis

- The timeline’s lack of `saved_code` events means process metrics are **run-sampled**, not edit-sampled.
- If the platform can expose save/autosave events, Step 5 becomes much more precise (true first-parseable time, true construct introduction time, finer-grained regression detection).

- The public-run state model surfaces a strong intervention triage rule:
- `S1b` (structure evident syntax break) is often recoverable in the broader population and is a good target for syntax assistance.
- `S0` and persistent `S2` are lower-leverage states for syntax-only interventions.

- For question design review, "thrash-prone" questions are now directly identifiable from process traces, not just score distributions.
- This enables a practical review queue: high-thrasher-rate questions + low discrimination/redundant test cases (from Step 2) are strong candidates for redesign.

## Practical Next Steps (Step 5 Driven)

- Build a targeted intervention simulation around `S1b` and early `S2` states (e.g., syntax hints vs debugging prompts) and estimate reachable gains before the 50% elapsed mark.
- Use `attempt_archetypes.csv` and `public_test_run_state_rows.parquet` to extract exemplar trajectories for teaching:
- successful `Incremental debugger` traces
- failed `Thrasher` traces
- `S2` self-loop traces that never convert to `S3`
- If raw per-run exception traces become available in the timeline (not just best-public snapshots), re-run 5e with typed runtime recovery (`TypeError`, `NameError`, etc.) instead of the current generic `Runtime Error` bucket.

# Step 6. Psychometric Modelling with IRT

This step reframes the exam as a measurement instrument rather than only a score report.
Given Step 2's heavy within-question test-case redundancy, the model is fit at the **question** level (not test-case level) using a 3-category ordinal score per question.

## Process / Rebuild

Script:

- `analysis/generate_psychometric_irt.py`

Rebuild command:

```bash
uv run analysis/generate_psychometric_irt.py
```

Generated outputs (ignored by git):

- `analysis/psychometric_irt/`

Key outputs:

- `question_level_grm_rows.csv` (row-level 0/1/2 category inputs by track)
- `namespace_grm_fit_summary.csv` and `namespace_grm_fit_summary_by_term_wave.csv`
- `namespace_question_grm_parameters.csv`, `question_parameter_flags.csv`, `question_parameter_summary.csv`
- `namespace_test_information_grid.csv`, `namespace_test_information_summary.csv`, `tif_low_ability_flags.csv`
- `namespace_linking_feasibility.csv`, `namespace_pair_linking_summary.csv`, `namespace_pair_anchor_parameter_drift.csv`
- `theta_linked_variant_pair_comparisons.csv`, `theta_linked_wave_pair_comparisons.csv`
- `dif_screen_pair_summary.csv` (anchor-drift screen, not a formal DIF test)
- `submitter_public_vs_private_category_agreement.csv` and `submitter_public_vs_private_category_crosstab.csv`
- `plots/tif/*.png` and parameter scatter plots

What the script does:

- Builds a question-level ordinal category per student-question:
- `0`: no tests passed
- `1`: some but not all tests passed
- `2`: all tests passed
- Uses `girth` (`grm_mml_eap`) to fit a question-level Graded Response Model (GRM) per namespace
- Exports per-question GRM parameters (`a`, `b1`, `b2`) and per-student `theta`
- Computes test information functions (TIFs) on a common `theta` grid
- Builds shared-question anchor maps and pairwise threshold-based linking screens
- Exports linked-`theta` comparisons for variant pairs where anchors are sufficient

### Important Step 6 Modelling Decisions and Caveats

- **Primary GRM basis is public-best for all rows**:
- The prompt proposed private-final scoring for Track A and public-best for Track B.
- This script deliberately uses **public-best categories for everyone** (`grm_basis = public_best_all`) so each question item has a single coherent definition within a namespace calibration.
- Track-aware (`hybrid`) and Track A private-final categories are still exported for sensitivity checks.

- **Question-level GRM is the right granularity for this data**:
- Step 2 found substantial test-case dependence/redundancy within questions.
- Modelling test cases as independent IRT items would overstate information and violate local independence assumptions.

- **Linking outputs are a screen, not a full equating study**:
- Pairwise links are built from shared question titles and threshold alignment.
- `dif_screen_pair_summary.csv` is useful for triage, but it is not a formal DIF test with person-level covariate controls.

- **Cross-term comparisons remain confounded by progressive filtering**:
- `t2` students are those who did not clear `t1`; `t3` students are weaker-by-construction again.
- Cross-term linked differences therefore reflect both instrument differences and population selection.

- **Single-anchor links can look "perfect" but are weak**:
- A pair with only one shared anchor question supplies exactly two thresholds (`b1`, `b2`), which can produce trivial near-perfect threshold fit statistics.
- Treat those links as exploratory only.

## Findings

### 6a / 6b) GRM Setup and Fit Coverage

From `question_level_grm_rows.csv` and `question_level_category_coverage_by_track.csv`:

- Total student-question rows for Step 6 input: `151,778`
- Track mix:
- Track A submitters: `42,918` (`28.28%`)
- Track A non-submitters (submission-positive namespaces): `11,112` (`7.32%`)
- Track B zero-submission namespaces: `97,748` (`64.40%`)
- Public-best GRM category coverage is effectively complete:
- missing `grm_category` rows: `2 / 151,778` (both in Track B)
- Track A submitters have both public and private categories on `42,918 / 42,918` rows

From `irt_summary_overall.csv` and `namespace_grm_fit_summary.csv`:

- GRM fit succeeded for `35 / 35` namespaces
- Questions fitted: `245` total
- Low-discrimination questions (`a < 0.5`): `0`
- Median fitted students per namespace: `787`
- All `35` fitted namespaces ended with `7` question items in the GRM matrix
- One special namespace (`ns_25t1_py_15_exe`) had `13` item IDs present, with `6` dropped for low coverage/low category variation before fitting

Important matrix-coverage note (from `namespace_grm_fit_summary.csv` and `namespace_item_matrix_coverage.csv`):

- The question-response matrices are **sparse** and are fit with missing responses (`INVALID_RESPONSE`) in `girth`.
- Median namespace matrix missingness: `23.04%` of student x item cells
- Median per-item observation coverage: `79.93%`
- This is handled by the fitter, but it matters when interpreting TIF precision and parameter stability.

### 6c) Question Parameter Patterns (Difficulty / Discrimination)

From `question_parameter_summary.csv` and `question_parameter_flags.csv`:

- Median discrimination `a`: `2.94` (very high)
- `p95` discrimination `a`: `4.24`
- "Very high discrimination" questions (script flag: `a >= 2.5` or in the top 5%): `163 / 245` (`66.53%`)
- "Partial-credit low information" questions (threshold gap `b2 - b1 < 0.35`): `116 / 245` (`47.35%`)
- "Cliff-like" questions (high discrimination + Step 1 shape warning): `15 / 245`
- Extreme `0 -> 1` threshold ("too hard to even get partial credit") is rare: `1 / 245`

Interpretation:

- Step 6 agrees with Step 2's story: the problem is not low discrimination; it is **too much discrimination / cliffiness**, consistent with redundancy and threshold effects.
- Nearly half the questions have very narrow `0->1` vs `1->2` thresholds, meaning partial credit adds limited measurement information.

Illustrative rare extreme-threshold item (from `question_parameter_flags.csv`):

- `ns_25t3_py21` Q13 `Format Pairs of Integers as Product of Fractions`
- `b1 = 2.05`, `b2 = 2.81`, with category counts `0/1/2 = 161 / 8 / 4`
- This is a classic "almost no one gets off zero" measurement pattern.

### 6d) Test Information Function (TIF): Where the Exam Measures Well

From `namespace_test_information_summary.csv`, `tif_low_ability_flags.csv`, and `irt_summary_overall.csv`:

- Median TIF peak location: `theta = -0.25`
- Median low-to-mid information ratio (`mean info(theta<=-1)` / `mean info(|theta|<=0.5)`): `0.1555`
- Namespaces flagged as low-ability blind (`ratio < 0.5`): `33 / 35`
- Namespaces with TIF peak near the middle (`|peak theta| <= 0.75`): `28 / 35`
- Namespaces peaking only at high ability (`peak theta > 1`): `0`

The two namespaces not flagged low-ability blind are still exceptions, not the norm:

- `ns_25t2_py22_1`: low/mid ratio `0.8588`, peak `theta = -1.35`
- `ns_25t3_py23`: low/mid ratio `0.5147`, peak `theta = -1.20`

Interpretation:

- The exams usually measure best around the middle and are much less informative in the low-ability region.
- Given the progressive-filter structure (later terms contain weaker students), this is a real measurement-design mismatch: the instrument is least precise where diagnostic resolution is most needed.

### 6e) Linking Feasibility and DIF Screening (Anchor-Based)

From `namespace_linking_feasibility.csv`, `namespace_pair_linking_summary.csv`, `namespace_pair_anchor_parameter_drift.csv`, and `dif_screen_pair_summary.csv`:

- `27 / 35` namespaces sit in a shared-item connected component (`18` components total)
- `23 / 35` namespaces have at least `3` reusable anchor items somewhere in their component
- Pairwise links generated: `27` total
- `10` variant pairs (`_1` vs `_2`, same slot)
- `17` generic shared-item pairs (mostly cross-term/cross-context reuse)
- No wave-pair or same-day timeslot-pair links were available under the shared-item criteria (`0` rows in `theta_linked_wave_pair_comparisons.csv`)

Variant-pair linking is the most credible result:

- All `10 / 10` variant pairs have `7` shared anchors
- Median threshold-link RMSE: `0.0712`
- Median linked discrimination drift (`|Δa|`): `0.2379`
- `1 / 10` variant pairs has a large anchor-threshold drift flag:
- `ns_25t2_py21_1` vs `ns_25t2_py21_2`
- strongest threshold-drift anchor: `File Content Zig-Zag Shift` (`|Δb1| = 0.806` after linking)

Generic shared-item links are mostly weakly anchored:

- Median shared anchors per pair: `1`
- Their "perfect" threshold fit (median RMSE ~ `0`, `R² ~ 1` in many cases) is largely an **artifact of single-anchor exact identification**, not evidence of strong equating quality.
- Use these links to find candidates for further study, not for high-stakes comparisons.

### 6f) Using `theta` for Fairer Comparisons (What Is and Is Not Supported Here)

From `theta_linked_variant_pair_comparisons.csv`:

- Linked `theta` comparisons are available for `10` same-slot variant pairs
- Linked mean `theta` differences (`variant_b - variant_a`, on `a` scale) range from about `-0.089` to `+0.653`
- Largest linked mean difference:
- `ns_25t1_py22_1` vs `ns_25t1_py22_2`: `+0.653`
- Small differences (near parity) include:
- `25t1 py14`, `25t2 py23`, `25t3 py13` variant pairs

Interpretation:

- Some `_1` vs `_2` pairs look materially different on the linked scale and should be reviewed for variant equivalence.
- However, these are still **screening comparisons**; without explicit random assignment evidence, variant differences can reflect both instrument and subgroup composition.

What is **not** supported in this snapshot:

- `theta_linked_wave_pair_comparisons.csv` is empty, so Step 6 cannot yet provide anchor-linked Wave 1 vs Wave 2 growth estimates.
- Cross-term linked comparisons are additionally confounded by progressive filtering, so they remain descriptive only.

### Public vs Private Category Sensitivity (Track A Submitters)

From `submitter_public_vs_private_category_agreement.csv` and `submitter_public_vs_private_category_crosstab.csv`:

- Public-best vs private-final question category agreement (submitters): `85.22%`
- Public category higher than private: `14.27%`
- Private category higher than public: `0.51%`

Largest disagreement cells:

- Public partial / Private zero: `3,600` rows (`8.39%`)
- Public full / Private partial: `1,834` rows (`4.27%`)
- Public full / Private zero: `690` rows (`1.61%`)

Interpretation:

- Public-best categories systematically overstate mastery relative to private-final outcomes for a non-trivial minority of submitters.
- This is consistent with the Step 2 same-code public/private gap signal.
- The public-best-only GRM basis is still the right choice for a coherent full-population calibration, but private-vs-public sensitivity should be carried forward when interpreting absolute mastery levels.

## Practical Next Steps (Step 6 Driven)

- Prioritize exam redesign toward **low-ability information** (easier discriminating items, not just more items), because TIFs are weak where later-term students cluster.
- Review the `15` cliff-like questions first; they are the most likely to create threshold effects without adding much partial-credit information.
- Investigate variant-equivalence outliers (starting with `25t2 py21 _1/_2` and `25t1 py22 _1/_2`) using item text + test-case structure + process traces from Steps 2 and 5.
- If a future exam cycle includes intentionally reused anchors across waves, re-run Step 6 to produce defensible wave-linked growth estimates on a common `theta` scale.

# Step 7: Evaluation Redesign

Step 7 is a **synthesis layer** over Steps 2, 3, 5, and 6. It does not reprocess raw event logs. Instead, it reads the previously generated analysis outputs and produces a compact set of CSVs for operational prioritization (instrumentation fixes, debugging interventions, test-case redesign targets, scoring-readiness diagnostics, and variant-equivalence review).

## Step 7 Script and Outputs

Script:

- `analysis/generate_evaluation_redesign.py`

Output folder:

- `analysis/evaluation_redesign/`

Key outputs:

- `step7_key_metrics.csv`: one-row-per-metric summary of the headline numbers used in this section (gating, submission capture, S2 self-loop, redundancy, IRT threshold gaps, low-ability information, linking gaps, runtime feedback quality, and recovery signals)
- `submission_capture_*.csv`: namespace-level and term/wave-level audits for the zero-submission instrumentation issue
- `s2_*.csv` and `public_state_distribution_combined.csv`: S2 prevalence and transition dynamics for debugging intervention targeting
- `archetype_redesign_summary.csv` plus `archetype_other_*`: archetype intervention metrics and diagnostics for the residual `Other` bucket
- `question_redesign_features.csv` and `question_redesign_targets_high_priority.csv`: joined test-design/process/IRT target list for question redesign
- `problem_statement_clarity_review_targets.csv`: question review shortlist combining wrong-output-logic rates and thrasher rates
- `layered_scoring_readiness_*.csv`: question-level and summary diagnostics for whether layered scoring is likely to add information before test redesign
- `low_ability_measurement_*.csv` and `warmup_question_target_namespaces.csv`: TIF-based low-ability measurement targeting tables
- `variant_equivalence_review_targets.csv` and `variant_anchor_drift_details.csv`: linked-`theta` variant-gap screen + anchor-parameter drift details
- `runtime_feedback_quality_*.csv` and `debugging_recovery_signal_summary.csv`: feedback quality and recovery evidence for platform changes
- `output_manifest.csv`: manifest of all Step 7 outputs

## Rebuild (Step 7 Only)

Prerequisite: Steps 2, 3, 5, and 6 outputs must already exist (the script reads their CSV exports directly).

Rebuild command:

```bash
uv run analysis/generate_evaluation_redesign.py
```

Verify outputs:

- Check `analysis/evaluation_redesign/output_manifest.csv`
- Spot-check `analysis/evaluation_redesign/step7_key_metrics.csv`

## Findings and Redesign Recommendations (Manual Synthesis)

This section is written manually from the earlier step results and validated against the Step 7 support tables (especially `step7_key_metrics.csv`, the submission-capture audits, and the question/variant target lists).

### 7a) Fix the Submission Capture Pipeline (Highest Operational Priority)

The dominant operational issue is **missing submission capture**:

- `23 / 35` namespaces have zero submission events (see `submission_capture_overall_summary.csv`)
- This removes private-test outcomes/formal scores for `97,748` student-question rows (`Track B`)
- Track B is not "inactive" data: `48.76%` of Track B rows passed all public tests at least once (see `submission_capture_track_row_summary.csv`)

Namespace clustering confirms this is a platform/instrumentation pattern, not student behavior:

- `25t1`: effectively all exam namespaces are zero-submission (`wave1`, `wave2`, and one `other` namespace)
- `25t2 wave2`: `40%` zero-submission namespaces
- `25t3 wave1`: `50%` zero-submission namespaces
- `25t3 wave2`: `75%` zero-submission namespaces

Use `submission_capture_zero_submission_namespaces.csv` and `submission_capture_term_wave_namespace_summary.csv` to coordinate a platform audit with engineering / ops.

### 7b) Address the S2 Bottleneck (Largest Intervention Opportunity)

S2 (`parseable code, zero public tests passing`) is the central debugging bottleneck:

- S2 accounts for `47.1%` of all public test-run states (`public_state_distribution_combined.csv`)
- S2 self-loop probability is `78.93%` (`s2_bottleneck_summary.csv`)
- The main escape route is only to partial public correctness (`S2 -> S3` = `7.18%`)

Interpretation: this is primarily a **debugging + problem decomposition** gap, not a syntax gap.

Recommended interventions:

1. Show structured first-failing-test feedback (input / expected / actual), not just generic pass/fail.
2. Redesign prompts into explicit sub-tasks so students get real intermediate checkpoints.
3. Teach incremental debugging explicitly using Step 5 trajectories (incremental debuggers vs thrashers).

Note on timing metrics: Step 5's narrative already shows the key process point (thrashers spend roughly `2.2x` the time of incremental debuggers for worse outcomes). The Step 7 bundle exports reproducible archetype-flag medians and ratios in `archetype_incremental_vs_thrasher_comparison.csv`.

### 7c) Redesign Test Cases for Difficulty Spread and Reduced Redundancy

The evidence from Steps 2 and 6 converges on the same diagnosis:

- `34.46%` of within-question item pairs are near-redundant (`phi > 0.90`)
- Median reliability is extremely high on the submitter namespaces (Cronbach alpha summary median `0.9716`)
- `47.35%` of fitted questions have narrow partial-credit thresholds (`b2 - b1 < 0.35`)
- `15` questions are flagged as cliff-like

This means many question test-case sets cluster at a single difficulty level and provide limited additional information through partial credit.

Use `question_redesign_targets_high_priority.csv` and `question_redesign_features.csv` to prioritize:

- cliff-like questions (`flag_cliff_like`)
- all-equivalent dependency graphs (`flag_dependency_edge_density_raw_eq_1`)
- high-thrasher questions (e.g., "Pattern printing - Centered Triangle Of Zeroes", "Reversed Squares of List Elements", "Pangram Check")
- narrow-threshold questions where layered scoring will collapse back toward binary

The Step 7 target tables also explicitly surface the raw dependency density criterion (`dependency_edge_density_raw`) so the "edge density = 1.0" cases are easy to filter.

### 7d) Add Easy Warm-Up Questions for Low-Ability Measurement

The exam remains low-ability blind in most namespaces:

- `33 / 35` namespaces are flagged for low-ability blindness
- median low-to-mid information ratio is `0.1555`

Given the progressive-filter term structure (later terms contain weaker surviving students), this is a measurement-design mismatch: the instrument is least precise where diagnostic resolution is most needed.

Use `warmup_question_target_namespaces.csv` and `low_ability_measurement_term_wave_summary.csv` to target namespaces most in need of easier discriminating items.

### 7e) Layered Scoring Is Useful, But Only After Test-Case Redesign in Many Questions

Layered scoring (attempt / runnability / core correctness / edge robustness) is directionally correct, but the Step 6 threshold evidence means it will not add much information on many current questions.

The new Step 7 outputs provide a readiness proxy:

- `layered_scoring_readiness_by_question.csv`
- `layered_scoring_readiness_summary.csv`

Important caveat from the current data:

- many questions are still classified as `low` or `unknown_missing_step2_dependency_metrics`
- the latter reflects both dependency-metric coverage limits (Step 2 coverage is only available for a subset of questions) and the submission-capture gap

Recommendation:

1. Simulate layered scoring on the existing data.
2. Report results separately for wide-threshold (`b2 - b1 > 0.5`) vs narrow-threshold questions.
3. Treat "narrow threshold + high redundancy" questions as test-redesign-first.

### 7f) Audit Problem Statement Clarity for High Wrong-Logic + High-Thrasher Questions

Step 3 and Step 5 together suggest a prompt-clarity review lane:

- some questions show very high wrong-output-logic rates
- some questions attract high thrasher rates (large effort, weak outcomes)

Use `problem_statement_clarity_review_targets.csv` to review questions where these signals co-occur. The Step 7 list intentionally includes the named high-thrash examples and ranks them alongside high wrong-output-logic items.

Practical review question:

- How many distinct incorrect interpretations could a careful student reasonably make?

If the answer is more than one, rewrite the prompt.

### 7g) Investigate Variant Equivalence (Linked-Theta Gaps + Anchor Drift)

Variant screening should continue before using variants as interchangeable forms:

- maximum linked mean `theta` gap across variant pairs is `0.653` (see `variant_equivalence_review_targets.csv`)
- the Step 7 table surfaces both the linked-`theta` gap and anchor drift summaries
- one notable anchor-drift warning remains in `25t2 py21 _1/_2` ("File Content Zig-Zag Shift", `|Δb1| > 0.75`)
- usable wave-pair linked comparisons are still unavailable (`theta_linked_wave_pair_comparisons.csv` has `0` rows); `linking_gap_summary.csv` shows only a thin incidental same-term `wave1`/`wave2` overlap (max `1` shared anchor), which is not enough for defensible within-term growth linking

Use together:

- `variant_equivalence_review_targets.csv` for pair-level prioritization
- `variant_anchor_drift_details.csv` for item-level inspection

### 7h) Improve Runtime Error Feedback (Pedagogy + Data Quality)

Runtime error logging remains too generic for both teaching and analysis:

- `Runtime Error (unspecified)` is `52.81%` of runtime-error rows in the current export (`runtime_feedback_quality_overall.csv`)

This limits:

- student debugging (they do not see the actual exception class / traceback)
- future analytics (runtime error subtypes are collapsed)

Platform change recommendation:

- expose the Python exception type and traceback to students
- log the same details in structured form for downstream analysis

## Additional Cross-Step Signals Worth Carrying Forward

The Step 7 bundle also consolidates recovery diagnostics that matter for intervention design:

- `45.49%` of rows ending with non-parseable Python had earlier parseable code (`parseability_regression_recovery_summary.csv`)
- syntax errors with structural intent resolve faster than those without (`50.33%` vs `43.7%` within one public run)
- wrong-answer states persist to the final public run `39.03%` of the time (`debugging_recovery_signal_summary.csv`)

These reinforce the Step 7 priority ordering:

1. Fix submission instrumentation first.
2. Improve debugging feedback and decomposition support (especially for S2).
3. Redesign test-case sets to create a genuine difficulty spread before expanding layered scoring.

# Step 8: Longitudinal Analysis

This step implements longitudinal analysis using paired, non-IRT-linked methods because Step 6 found no usable shared anchor items between Wave 1 and Wave 2 within any term.

## Process and Rebuild

### What was added

- `analysis/generate_longitudinal_analysis.py`
- Generated outputs under `analysis/longitudinal_analysis/`
- A file manifest at `analysis/longitudinal_analysis/output_manifest.csv`

### Rebuild command

Run:

```bash
uv run analysis/generate_longitudinal_analysis.py
```

The script reads outputs from earlier steps (not raw platform exports directly), including:

- Step 3 error taxonomy outputs
- Step 5 process / state / archetype outputs
- Step 6 psychometric outputs (GRM rows, question flags, linking drift summaries)
- Step 2 dependency graph summary outputs

### Cohort definition used for primary summaries

The script exports both raw paired counts and a stricter substantive paired cohort. Primary Step 8 findings below use the substantive cohort:

- substantive paired student = at least `3` question rows in each compared wave/term

This makes the paired comparisons more stable and explains small count differences versus approximate headline counts from earlier steps (for example, the all-three-term cohort is `497` here rather than the earlier approximate `503`).

## Coverage and Pairing Checks

The Wave 1 to Wave 2 gap is the expected ~35 days and is the cleanest same-population comparison window:

- `25t1`: `38.64` days
- `25t2`: `35.97` days
- `25t3`: `34.85` days

Substantive paired cohorts:

- within-term paired students: `25t1 = 4190`, `25t2 = 2918`, `25t3 = 2659`
- cross-term repeaters: `25t1->25t2 = 1989`, `25t2->25t3 = 1359`
- all-three-term students (substantive): `497`

Files:

- `analysis/longitudinal_analysis/step8_key_metrics.csv`
- `analysis/longitudinal_analysis/term_wave_gap_summary.csv`
- `analysis/longitudinal_analysis/within_term_wave_pair_coverage.csv`
- `analysis/longitudinal_analysis/cross_term_repeat_coverage.csv`

## 8a) Within-Term Growth (Wave 1 -> Wave 2) Without IRT Linking

### Rank-based comparison: relative rank is mostly stable

Wave-level rank changes are centered close to zero (as expected for a relative measure):

- median rank delta (`Wave2 - Wave1`) is `-0.0091` in `25t1`, `+0.0025` in `25t2`, and `-0.0017` in `25t3`
- mean rank delta is slightly positive in all three terms (`+0.0046`, `+0.0168`, `+0.0155`)

Interpretation:

- students improve in absolute performance, but relative ordering changes only modestly because rank is zero-sum within each wave

Files:

- `analysis/longitudinal_analysis/within_term_rank_change_summary.csv`
- `analysis/longitudinal_analysis/within_term_rank_change_distribution.csv`

### Category-based comparison: strong absolute improvement

Using GRM categories (`0/1/2`) and weighting by paired question counts, the majority of students improve from Wave 1 to Wave 2:

- `25t1`: `57.68%` improve, `14.31%` same, `28.02%` decline
- `25t2`: `68.92%` improve, `10.10%` same, `20.98%` decline
- `25t3`: `59.14%` improve, `12.84%` same, `28.01%` decline

Mean per-student category delta is positive in all terms:

- `25t1`: `+0.2063`
- `25t2`: `+0.3830`
- `25t3`: `+0.2259`

This is the main within-term learning signal in Step 8.

Files:

- `analysis/longitudinal_analysis/within_term_category_change_summary.csv`
- `analysis/longitudinal_analysis/within_term_wave_pairs_substantive.csv`

### Archetype shifts: dominant student-wave patterns are now interpretable (and `Thrasher` remains rare)

At the student-wave dominant-archetype level, `Thrasher` is still effectively absent from the transition matrices. This remains an important caveat:

- thrasher is a strong question-level pattern (Step 5), but it rarely dominates an entire student-wave

With the Step 5a archetype split, the dominant student-wave transition picture becomes much clearer. The largest within-term source groups are now:

- `Builder with setbacks` (Wave 1 dominant): `1,692` (`25t1`), `1,153` (`25t2`), `1,062` (`25t3`)
- `Minimal-change solver`: `881`, `622`, `557`
- `Incremental debugger`: `720`, `484`, `584`

For targeted intervention tracking, the Step 8 outputs now group destinations into a broader **productive process** set:

- core productive: `Steady builder`, `Incremental debugger`
- productive intermediate: `Builder with setbacks`, `Minimal-change solver`

This avoids over-relying on tiny-sample `Thrasher` rows and better matches the final Step 5a taxonomy.

What shows up consistently:

- `Builder with setbacks` is moderately stable within-term: `37.71%` (`25t1`), `36.60%` (`25t2`), `37.01%` (`25t3`) remain `Builder with setbacks` in Wave 2
- `Minimal-change solver` often shifts to `Builder with setbacks`: `33.94%` (`25t1`), `36.66%` (`25t2`), `35.37%` (`25t3`)
- `Incremental debugger` often splits between staying incremental and shifting to `Builder with setbacks`:
  - stay `Incremental debugger`: `37.92%`, `33.68%`, `34.93%`
  - shift to `Builder with setbacks`: `33.19%`, `40.08%`, `33.56%`
- targeted struggling archetypes frequently move into more productive mid-process patterns:
  - `Regression -> Builder with setbacks`: `29.69%` (`25t1`), `35.00%` (`25t2`), `32.14%` (`25t3`)
  - `Skeleton-only -> Builder with setbacks` or `Incremental debugger` combined: `51.11%` (`25t1`), `38.30%` (`25t2`), `66.67%` (`25t3`)
- in the broader productive-destination summary (`core + productive intermediate`), dominant-source archetypes such as `Regression`, `Skeleton-only`, `Flat stuck`, and `One-shot` move to productive destinations at high rates (roughly `68%` to `85%` within-term, depending on term and source label)

Files:

- `analysis/longitudinal_analysis/within_term_archetype_shift_matrix.csv`
- `analysis/longitudinal_analysis/within_term_archetype_targeted_shifts.csv`
- `analysis/longitudinal_analysis/within_term_archetype_targeted_productive_summary.csv`

### Dominant state shifts: improvement exists, but dominant-S2 escape is zero under a strict definition

Using each student's dominant public-test-run process state per wave:

- most students stay in the same dominant-state bucket (`58.42%` to `64.66%` weighted by wave1 run rows)
- weighted dominant-state improvement is modest but non-zero (`19.74%` to `23.49%`)

Important caveat and result:

- under the strict dominant-state criterion, `S2_parseable_zero -> S3/S4` escape is `0%` in all three terms
- source counts are non-trivial (`109`, `52`, `59`), so this is not a rounding artifact
- dominant-S2 students mostly shift to syntax/no-code dominant states (`S1`, `S1b`, `S0`) rather than to public-pass states

This does not contradict Step 4's large S2 bottleneck. It shows that the subset whose entire wave is dominated by S2 is especially hard to move.

Files:

- `analysis/longitudinal_analysis/within_term_dominant_state_shift_matrix.csv`
- `analysis/longitudinal_analysis/within_term_dominant_state_shift_summary.csv`
- `analysis/longitudinal_analysis/within_term_s2_dominant_escape_summary.csv`

## 8b) Cross-Term Repeat Students (Paired Comparisons)

Cross-term comparisons are only interpretable as paired analyses because later terms are filtered populations (students who did not pass earlier terms).

### Overall cross-term performance change is strongly positive

Among substantive repeaters:

- `25t1->25t2`: mean term-level category delta `+0.4924`, median `+0.5000`
- `25t2->25t3`: mean term-level category delta `+0.4555`, median `+0.4444`

Category-change labels (student-level term summaries):

- `25t1->25t2`: `80.95%` improve, `4.93%` same, `14.13%` decline
- `25t2->25t3`: `76.53%` improve, `7.21%` same, `16.26%` decline

This indicates substantial learning among repeaters even though they remain in the system.

Files:

- `analysis/longitudinal_analysis/cross_term_term_pairs.csv`
- `analysis/longitudinal_analysis/cross_term_repeat_coverage.csv`

### Error profile matching: many syntax-gated repeaters move to stronger profiles

Among students with a syntax-gated dominant error profile in the source term:

- `25t1->25t2`: `53.30%` move to pass-like dominant error profiles
- `25t2->25t3`: `47.67%` move to pass-like dominant error profiles

Progress short of passing is also visible:

- syntax-gated -> runtime/wrong-output shifts:
  - `25t1->25t2`: `9.07%`
  - `25t2->25t3`: `25.58%`

This supports the Step 8 framing that moving from syntax failure to logic/runtime failure is pedagogical progress, not merely a different failure.

Files:

- `analysis/longitudinal_analysis/cross_term_error_shift_matrix.csv`
- `analysis/longitudinal_analysis/cross_term_syntax_progression_summary.csv`

### Runtime subtype persistence exists, but is partial and limited by generic logging

Weighted same-runtime-subtype persistence is:

- `25t1->25t2`: `38.10%`
- `25t2->25t3`: `21.43%`

The runtime subtype table is small-n and still dominated by `Runtime Error (unspecified)`, which limits interpretability.

Files:

- `analysis/longitudinal_analysis/cross_term_runtime_type_persistence.csv`
- `analysis/longitudinal_analysis/student_question_error_rows_step8.csv`

### Archetype stability across terms: `Builder with setbacks` is the dominant repeater pattern

Examples from the dominant-archetype cross-term matrices:

- `Builder with setbacks -> Builder with setbacks`
  - `25t1->25t2`: `504/916` (`55.02%`)
  - `25t2->25t3`: `295/620` (`47.58%`)
- `Minimal-change solver -> Builder with setbacks`
  - `25t1->25t2`: `153/335` (`45.67%`)
  - `25t2->25t3`: `105/226` (`46.46%`)
- `Incremental debugger -> Builder with setbacks`
  - `25t1->25t2`: `90/190` (`47.37%`)
  - `25t2->25t3`: `68/138` (`49.28%`)

Interpretation:

- the dominant repeater trajectory is not "stable thrashing"; it is a persistent middle process regime (`Builder with setbacks`) with some movement to/from `Minimal-change solver` and `Incremental debugger`
- `Thrasher` remains essentially absent at the dominant-archetype term level, so Step 5 thrasher findings should still be treated as question-attempt behavior rather than a stable student-level identity
- the cross-term targeted productive summary shows the same pattern for non-productive dominant sources (`Regression`, `Flat stuck`, `One-shot`): most movement is into productive intermediate destinations (`Builder with setbacks` / `Minimal-change solver`) rather than directly into core productive labels

Files:

- `analysis/longitudinal_analysis/cross_term_archetype_shift_matrix.csv`
- `analysis/longitudinal_analysis/cross_term_archetype_targeted_shifts.csv`
- `analysis/longitudinal_analysis/cross_term_archetype_targeted_productive_summary.csv`
- `analysis/longitudinal_analysis/student_term_primary_archetype.csv`

### Tree-sitter structural progression: more loop/branch usage, less print-heavy behavior

Cross-term construct summaries show consistent increases in problem-structure constructs:

- `for_loop` mean consistency delta:
  - `25t1->25t2`: `+0.1117`
  - `25t2->25t3`: `+0.0600`
- `if_stmt` mean consistency delta:
  - `25t1->25t2`: `+0.0557`
  - `25t2->25t3`: `+0.0606`

Common "newly appears" patterns include `list_comp` and `try_stmt` (especially `25t1->25t2`), while `print_call` consistency decreases:

- `print_call` mean consistency delta:
  - `25t1->25t2`: `-0.0485`
  - `25t2->25t3`: `-0.0289`

This is consistent with students moving from output-driven trial code toward more structured solutions.

Files:

- `analysis/longitudinal_analysis/cross_term_construct_progression_summary.csv`
- `analysis/longitudinal_analysis/student_term_construct_profile.csv`

### Cross-term dominant-S2 escape: also zero under the strict dominant-state definition

Among repeat students who are dominant `S2_parseable_zero` in the source term:

- `25t1->25t2`: `0/13` escape to dominant `S3/S4`
- `25t2->25t3`: `0/12` escape to dominant `S3/S4`

Most instead shift to dominant syntax/no-code states. This is a strong signal that students whose term-level process is dominated by S2 are not being moved to a productive debugging regime by current remediation.

Files:

- `analysis/longitudinal_analysis/cross_term_s2_escape_summary.csv`
- `analysis/longitudinal_analysis/cross_term_dominant_state_shift_matrix.csv`

## 8c) The 497 All-Three-Term Students (Persistently Struggling Cohort)

This is the highest-value cohort for intervention design because they persist across all three terms of the progressive filter.

### Three-term dominant-state trajectories are mostly syntax/no-code, not S2

Top dominant-state trajectories are overwhelmingly syntax/no-code:

- `S1_syntax_fundamental -> S1_syntax_fundamental -> S1_syntax_fundamental`: `181`
- `S0_no_code -> S1_syntax_fundamental -> S1_syntax_fundamental`: `69`
- `S0_no_code -> S0_no_code -> S1_syntax_fundamental`: `36`

Only `3` students have trajectories that start with dominant `S2_parseable_zero`.

This is an important nuance relative to Step 4:

- S2 is the largest aggregate bottleneck overall
- but the persistently struggling all-three-term cohort is dominated by syntax/no-code states under the strict dominant-state summary

Files:

- `analysis/longitudinal_analysis/all_three_term_state_trajectory_summary.csv`
- `analysis/longitudinal_analysis/all_three_term_trajectories.csv`

### Three-term archetype trajectories: persistent middle-process patterns dominate the all-three cohort

The dominant-archetype trajectories are now led by the newly resolved mid-process categories rather than `Other`:

- top sequence: `Builder with setbacks -> Builder with setbacks -> Builder with setbacks` (`56`)
- next most common sequences are still centered on `Builder with setbacks` and `Minimal-change solver` (for example, `Builder with setbacks -> Builder with setbacks -> Incremental debugger` and `Builder with setbacks -> Builder with setbacks -> Minimal-change solver`, both `20`)
- `Builder with setbacks` appears somewhere in the trajectory for `404/497` students
- `Minimal-change solver` appears somewhere in the trajectory for `210/497`
- `Incremental debugger` appears somewhere in the trajectory for `151/497`

Notably absent in this dominant-archetype summary:

- no `Thrasher` appears in any three-term dominant-archetype trajectory
- no `Skeleton-only -> Skeleton-only -> Skeleton-only`

This reinforces the same caveat as above: these labels are highly informative at question-attempt level, but dominant per-wave/per-term archetypes compress behavior heavily.

Files:

- `analysis/longitudinal_analysis/all_three_term_archetype_trajectory_summary.csv`
- `analysis/longitudinal_analysis/student_term_primary_archetype.csv`

### Three-term error trajectories show meaningful progress even without observed exit

The dominant-error trajectory table includes many sequences that end in pass-like profiles (`Full pass` or `Public full pass, no submit`) by later terms, for example:

- `Syntax gated -> Submitted, zero -> Public full pass, no submit` (`23`)
- `Runtime error -> Submitted, zero -> Public full pass, no submit` (`20`)
- `Syntax gated -> Submitted, zero -> Full pass` (`17`)

This supports the Step 8 interpretation that process and error-profile changes can be pedagogically meaningful even when the student remains in the repeat cohort.

Files:

- `analysis/longitudinal_analysis/all_three_term_error_trajectory_summary.csv`
- `analysis/longitudinal_analysis/student_term_primary_error_profile.csv`

### "Eventual passers in t3" is not directly observable (no t4), so Step 8 uses proxies

The dataset ends at `25t3`, so true post-t3 exit cannot be observed directly. Step 8 therefore uses explicit success proxies and labels them as proxies:

- term-level t3 success proxy (full `497` all-three cohort):
  - `340` flagged `t3_term_high_success_proxy`
  - `157` not flagged
- wave2-only t3 proxy is available for a smaller subset (`273` students):
  - `67` high-success proxy
  - `206` not high-success proxy

These proxies are useful for profiling, but they are not the same as observed exit.

Files:

- `analysis/longitudinal_analysis/all_three_term_t3_term_level_success_proxy_summary.csv`
- `analysis/longitudinal_analysis/all_three_term_t3_success_proxy_summary.csv`
- `analysis/longitudinal_analysis/all_three_term_t3_success_proxy_feature_comparison.csv`

## 8d) "Pass-Through" Analysis (Observed Exit Proxy Model)

This step models observed exit after a term using features available at the start/end of the term pair, but with an explicit caveat:

- outcome = `exit_after_term_observed` = not present in the next term (substantive participation)
- this proxy mixes passing with attrition/non-participation

### Model performance (predicting observed exit proxy)

On substantive paired-wave students from `25t1` and `25t2`:

- rows: `7108`
- observed exit-positive rate: `0.7690`
- 5-fold CV ROC AUC: `0.9193`
- 5-fold CV Brier score: `0.0952`

The model is useful for ranking risk of persistence, but it should not be reported as a pure pass-probability model.

Files:

- `analysis/longitudinal_analysis/pass_through_model_performance.csv`
- `analysis/longitudinal_analysis/pass_through_model_dataset.csv`
- `analysis/longitudinal_analysis/pass_through_model_scored_rows.csv`

### Calibration and interpretation guidance

The risk-decile table shows strong monotonic calibration in observed exit rates:

- lowest-risk decile for exit: observed exit rate `0.2194`
- middle decile (~0.777 predicted): observed exit rate `0.7718`
- highest-risk deciles for exit: observed exit rates ~`0.994`

Because features are correlated (scores, deltas, pass counts, archetypes, error profiles), the grouped-rate tables are more interpretable than raw logistic coefficients for intervention planning.

Files:

- `analysis/longitudinal_analysis/pass_through_risk_segments.csv`
- `analysis/longitudinal_analysis/pass_through_grouped_rates.csv`
- `analysis/longitudinal_analysis/pass_through_logistic_coefficients.csv`

## 8e) Future Anchor Design Recommendation (to Restore IRT Growth Linking)

Step 8 confirms the practical consequence of Step 6's wave-linking gap:

- within-term growth can be analyzed through paired non-IRT methods now
- but proper IRT-linked growth curves remain unavailable without deliberate wave anchors

Recommendation for future terms:

1. Include `2-3` identical anchor questions shared between Wave 1 and Wave 2 of the same term.
2. Keep content and test cases identical across waves.
3. Prefer moderate-difficulty, good-discrimination questions with real partial-credit spread.
4. Avoid cliff-like items and items with equivalent/redundant test sets.

Step 8 exports a candidate pool to support this design change:

- `46` recommended title-level anchor candidates (`future_wave_anchor_candidate_titles.csv`)

Examples appearing in the recommended pool include:

- `Sales Records Analysis`
- `Check if a String Starts and Ends with the Same Vowel (Case Insensitive)`
- `Pattern Printing Centered Triangle Of Zeroes`
- `Analyze Sentences`
- `Book Reading List Data Analysis`

Files:

- `analysis/longitudinal_analysis/future_wave_anchor_candidate_questions.csv`
- `analysis/longitudinal_analysis/future_wave_anchor_candidate_titles.csv`

## Step 8 Summary (What Changed vs What Is Measurable)

Even without IRT-linked wave growth, the longitudinal picture is informative:

- within-term absolute performance improves strongly, while relative rank changes little
- repeat students often improve their error profiles and structural coding behavior
- dominant-S2 students almost never become dominant public-pass students under the strict dominant-state lens
- the all-three-term persistent cohort is dominated by syntax/no-code trajectories, not S2, under dominant-state summaries
- observed-exit modeling is feasible and well-calibrated as a triage tool, but it is an exit proxy (pass + attrition), not a pure pass model

Operational implication:

- if the same dominant syntax/no-code and non-productive archetype patterns remain stable for the all-three-term cohort in future runs, inter-term remediation is not changing how the highest-need students work

Measurement-design implication:

- adding `2-3` deliberate within-term wave anchors is a low-cost change that restores proper IRT growth analysis in future terms

# Step 9: Concept Dependency and Knowledge Modelling

This step adds a reproducible concept-tagging and concept-level analysis layer on top of the Step 3/5/6/8 outputs.

It addresses:

- concept-question mapping (all `251` questions)
- concept-level mastery summaries (public-best outcomes)
- construct-usage-vs-mastery signals ("don't know when" vs "don't know how")
- empirical concept prerequisite signals
- paired concept profiles for repeat students
- concept-level decomposition of final-S2 failures

## Process and Rebuild

### What was added

- `analysis/generate_concept_knowledge_modeling.py`
- outputs under `analysis/concept_knowledge_modeling/`
- `analysis/concept_knowledge_modeling/output_manifest.csv`

### Rebuild command

```bash
uv run analysis/generate_concept_knowledge_modeling.py
```

### Inputs used

The Step 9 script reads existing analysis outputs (no raw platform export reprocessing), primarily:

- `analysis/question_metadata.csv`
- `analysis/guide.md` (OPPE concise question cues by namespace/problem)
- `analysis/psychometric_irt/question_level_grm_rows.csv`
- `analysis/process_analysis/attempt_construct_first_appearance.csv`
- `analysis/process_analysis/construct_first_appearance_summary_global.csv`
- `analysis/process_analysis/public_test_run_state_rows.parquet`
- `analysis/error_taxonomy/selected_snapshot_taxonomy_rows.csv`

### Method notes (important)

1. **Concept tagging is cue-driven and heuristic, not SME hand-labelled.**
   - The script parses concise cues from `analysis/guide.md` by exact `namespace + problem_id`, joins them to `analysis/question_metadata.csv`, then applies rule-based keyword tagging.
   - Coverage is complete (`251/251` questions got guide cues and `251/251` were tagged).

2. **Public-best basis is consistent with Step 6.**
   - `question_level_grm_rows.csv` is `grm_basis = public_best_all` for all rows, so Step 9 mastery summaries use the same public-best categorical basis (`grm_category` in `{0,1,2}`).

3. **Student-level concept mastery (for prerequisite graph / repeat profiles) uses a threshold.**
   - `concept_mastered_flag := mean_grm_category >= 1.5` within the scope (wave or term) for that concept.

4. **Repeat-student concept profiles use the Step 8-style substantive threshold.**
   - substantive term participation = at least `3` question rows in standard `wave1/wave2` rows.

5. **Construct proxies are limited by the available Step 5 tree-sitter feature set.**
   - There are no direct AST flags for dictionary literals/indexing, `open()` calls, or string methods.
   - `dict_comp`, `import_*`, `try_stmt`, and loop/print constructs are proxies (sometimes weak/narrow).

## 9a) Concept-Question Map (251 Questions)

The concept map covers all `251` questions and all questions have parsed OPPE guide cues:

- question rows tagged: `251`
- guide cue coverage: `251/251`
- untagged questions: `0`
- average tags per question: `1.5936`
- max tags on a question: `4`

Concept tag counts (question-tag rows; multi-label):

- `String manipulation`: `74`
- `Arithmetic / conditionals`: `72`
- `Loops and iteration`: `59`
- `Input parsing / output formatting`: `48`
- `List / tuple operations`: `38`
- `Data analysis / aggregation`: `35`
- `Dictionary operations`: `26`
- `Mathematical / algorithmic`: `21`
- `Pattern printing`: `18`
- `File operations`: `9`

Spot checks are directionally correct:

- `Pattern printing - Centered Triangle Of Zeroes` -> pattern + loops + formatting (+ math/triangle cue)
- `Column Totals in a Markdown Table (Numeric Columns Only)` -> input/output formatting + file operations
- `Merge two dictionaries and sum on conflicts` -> dictionary operations + loops/iteration

Files:

- `analysis/concept_knowledge_modeling/concept_question_map.csv`
- `analysis/concept_knowledge_modeling/concept_question_tag_rows.csv`
- `analysis/concept_knowledge_modeling/guide_question_cues_extracted.csv`
- `analysis/concept_knowledge_modeling/concept_tagging_coverage_summary.csv`

## 9b) Concept-Level Mastery Rates (Public-Best Basis)

### Overall concept mastery (student-question rows, public-best all-pass rate)

Highest overall all-public-pass rates:

- `Arithmetic / conditionals`: `60.23%`
- `List / tuple operations`: `52.02%`
- `String manipulation`: `51.83%`

Lowest overall all-public-pass rates:

- `Data analysis / aggregation`: `21.14%`
- `Input parsing / output formatting`: `29.52%`
- `Pattern printing`: `30.49%`
- `File operations`: `30.52%`

This matches the broader difficulty picture from earlier steps: data-analysis style questions and formatting/file-heavy tasks are a major difficulty cluster.

### Term-level breakdown (caveat: progressive filter + question mix)

Cross-term aggregate comparisons remain confounded by the progressive filter and by changing question sets, but they still help locate consistently weak concept areas.

Using the student-concept mastery profile rate (`mean_grm >= 1.5`):

- `Data analysis / aggregation` is persistently low across terms:
  - `25t1`: `19.36%`
  - `25t2`: `19.24%`
  - `25t3`: `17.29%`
- `Pattern printing` declines across terms (consistent with weaker later cohorts and/or harder pattern sets):
  - `25t1`: `27.82%`
  - `25t2`: `23.52%`
  - `25t3`: `16.70%`
- `Arithmetic / conditionals` remains one of the strongest:
  - `25t1`: `47.30%`
  - `25t2`: `55.18%`
  - `25t3`: `55.18%`

### Within-term Wave 1 -> Wave 2 concept comparisons (cleaner population comparison)

These are same-population paired comparisons, so they are cleaner than cross-term aggregates. However, they still compare different wave question sets within a concept (not linked anchors).

Strongest positive paired concept shifts (mean student-level concept `GRM` delta):

- `25t2`: `Loops and iteration` (`+0.725`, `+38.59` pp all-pass among paired concept profiles, `n=656`)
- `25t3`: `Loops and iteration` (`+0.766`, `+38.60` pp, `n=1805`)
- `25t1`: `List / tuple operations` (`+0.368`, `+26.01` pp, `n=2547`)

Notable within-term declines (wave content mismatch warning):

- `25t1`: `Mathematical / algorithmic` (`-0.716`, `-44.49` pp, `n=816`)
- `25t1`: `Dictionary operations` (`-0.388`, `-21.08` pp, `n=223`)

These declines do **not** imply students "unlearned" the concept. They indicate concept-level wave comparisons are still sensitive to which specific questions instantiate a concept in each wave.

Files:

- `analysis/concept_knowledge_modeling/concept_mastery_overall.csv`
- `analysis/concept_knowledge_modeling/concept_mastery_by_term.csv`
- `analysis/concept_knowledge_modeling/concept_mastery_by_term_wave.csv`
- `analysis/concept_knowledge_modeling/concept_mastery_student_profiles_by_term.csv`
- `analysis/concept_knowledge_modeling/within_term_paired_student_concept_wave_change_summary.csv`
- `analysis/concept_knowledge_modeling/concept_mastery_within_term_wave_unpaired_change.csv`

## 9c) Tree-Sitter Construct Usage vs Mastery

### Construct-focus table (directly aligned with the Step 9 prompt examples)

From `construct_focus_usage_mastery.csv`:

- `Loops` (`for_loop` or `while_loop`):
  - usage rate (ever used in attempt): `48.67%`
  - all-public-pass rate among users: `45.73%`
  - gap type: `High usage, low mastery`
- `List comprehensions` (`list_comp`):
  - usage: `4.53%`
  - all-public-pass among users: `52.57%`
  - gap type: `Low usage, low mastery`
- `Dictionaries` (`dict_comp` proxy only; narrow proxy):
  - usage: `0.41%`
  - all-public-pass among users: `52.88%`
  - gap type: `Low usage, low mastery`
- `Error handling` (`try_stmt`):
  - usage: `1.45%`
  - all-public-pass among users: `41.22%`
  - gap type: `Low usage, low mastery`

Interpretation:

- The **loops** signal is the clearest "know when, struggle with execution" pattern (`high usage, low mastery`).
- The **list-comp / dict-comp / try** signals are mostly "low usage, low mastery" under the tracked constructs, which suggests limited absorption and/or weak deployment.
- For dictionaries specifically, this is a **narrow proxy** because dict literals/indexing are not tracked in Step 5's construct set.

### Concept-proxy usage vs mastery (one row per concept)

The concept-level proxy table (`concept_construct_proxy_usage_mastery.csv`) extends this idea to the 10 concept categories. Most concepts are classified as `High usage, low mastery` under their configured proxy constructs, especially:

- `Data analysis / aggregation` (proxy usage `75.42%`, all-pass among proxy-users `27.97%`)
- `Pattern printing` (proxy usage `78.35%`, all-pass among proxy-users `27.27%`)
- `Loops and iteration` (proxy usage `65.67%`, all-pass among proxy-users `43.83%`)

This supports a "practice and feedback" intervention framing for these concepts, not just exposure.

Files:

- `analysis/concept_knowledge_modeling/construct_focus_usage_mastery.csv`
- `analysis/concept_knowledge_modeling/construct_focus_usage_mastery_by_term.csv`
- `analysis/concept_knowledge_modeling/concept_construct_proxy_usage_mastery.csv`
- `analysis/concept_knowledge_modeling/construct_first_appearance_summary_global_step5_copy.csv`

## 9d) Empirical Concept Prerequisite Graph (Screening Tool, Not Final Curriculum Order)

The prerequisite graph is computed from student-term concept mastery profiles using:

- `P(masters B | masters A)`
- `P(masters B | fails A)`
- edge strength = difference (`Δ`)

To avoid an over-dense graph, the Step 9 script keeps only the stronger direction for each unordered concept pair and applies support/strength thresholds.

Result:

- `24` candidate directional prerequisite edges
- `20` reverse the **proxy** concept order used in this step

Important caveat:

- The "curriculum order" comparison here uses the **Step 9 concept-list order as a proxy**, not an authoritative syllabus sequence.
- Many concepts are broad and cross-cutting (especially loops, formatting, and data analysis), so these edges should be used as a **screening signal** for curriculum review, not as proof of causal prerequisites.

Examples of strong candidate edges:

- `Input parsing / output formatting -> File operations` (`Δ master prob = 78.52 pp`, aligned with proxy order)
- `Data analysis / aggregation -> Dictionary operations` (`58.34 pp`, reverse vs proxy order)
- `Data analysis / aggregation -> Loops and iteration` (`52.97 pp`, reverse vs proxy order)
- `Loops and iteration -> String manipulation` (`49.85 pp`, reverse vs proxy order)

The reverse-edge pattern is still informative: it suggests the concept definitions are strongly interdependent and the proxy order likely does not reflect the true dependency structure well enough for direct curriculum conclusions.

Files:

- `analysis/concept_knowledge_modeling/concept_prerequisite_pair_matrix.csv`
- `analysis/concept_knowledge_modeling/concept_prerequisite_edge_candidates.csv`
- `analysis/concept_knowledge_modeling/concept_prerequisite_order_misalignment_proxy.csv`

## 9e) Paired Concept Profiles for Repeat Students

Using the substantive repeat-student cohorts (same threshold as Step 8 style: `>=3` question rows per term, standard waves only):

- `25t1->25t2`: `1989` repeat students
- `25t2->25t3`: `1359` repeat students

At the student level (concepts assessed in both terms):

- share with **at least one newly mastered concept**
  - `25t1->25t2`: `66.52%`
  - `25t2->25t3`: `61.37%`
- share with **at least one regressed concept**
  - `25t1->25t2`: `24.53%`
  - `25t2->25t3`: `20.09%`

This is strong evidence that many repeat students are learning new concepts between terms, even when they remain in the system.

### Concept-specific retention / acquisition highlights

`25t1->25t2`:

- `Arithmetic / conditionals`: retention `72.26%`, acquisition `52.75%`
- `String manipulation`: retention `61.75%`, acquisition `42.44%`
- `List / tuple operations`: acquisition `27.98%`
- `Data analysis / aggregation`: acquisition only `9.42%`
- `Pattern printing`: acquisition only `7.57%`, retention `13.89%`

`25t2->25t3`:

- `Arithmetic / conditionals`: retention `58.87%`, acquisition `45.82%`
- `String manipulation`: retention `51.36%`, acquisition `29.22%`
- `List / tuple operations`: acquisition `32.40%`
- `Data analysis / aggregation`: acquisition only `3.53%`
- `Pattern printing`: acquisition `0.76%` (small overlap, `n=48` assessed in both)

Interpretation:

- Core concepts (`Arithmetic`, `String`, `List/Tuple`) show meaningful acquisition and moderate retention.
- `Data analysis / aggregation` and `Pattern printing` remain difficult to acquire and retain, especially among repeaters.

Files:

- `analysis/concept_knowledge_modeling/repeat_student_concept_profiles_paired.csv`
- `analysis/concept_knowledge_modeling/repeat_student_concept_profile_pair_rows.csv`
- `analysis/concept_knowledge_modeling/repeat_student_concept_profile_pair_summary.csv`
- `analysis/concept_knowledge_modeling/repeat_student_concept_retention_acquisition_summary.csv`

## 9f) Concept-Level Decomposition of the Final-S2 Bottleneck

This step links the Step 4/8 process finding (S2 = parseable code, zero public tests passed) to concepts and construct proxies.

### Final-S2 cohort size and snapshot-alignment quality

- final public-run S2 attempts: `36,616` student-question attempts
- selected snapshot row available: `36,616` (`100%`)
- selected snapshot is itself a public test_run row: `30,481` (`83.24%`)
- selected snapshot matches S2-like public conditions: `28,974` (`79.13%`)
- aligned proxy subset retained for decomposition:
  - attempts: `28,974`
  - concept-tag rows: `47,068`

This means the selected-snapshot construct proxy is useful, but not perfect; Step 9 reports the alignment rate explicitly.

### Which concepts dominate final-S2?

Top concept-tag rows within final-S2 attempts:

- `String manipulation`: `10,620`
- `Loops and iteration`: `9,516`
- `Input parsing / output formatting`: `8,352`

### Selection vs application decomposition (proxy-based)

Using concept-specific construct proxies (with quality labels), the primary percentages below are read from the **aligned-proxy** rollup (`selected_snapshot_s2_like = True`):

- `Pattern printing`: `93.61%` application-gap proxy (relevant construct present)
- `Loops and iteration`: `64.71%` application-gap proxy
- `String manipulation`: `65.26%` application-gap proxy (**weak proxy**)
- `Data analysis / aggregation`: `66.80%` application-gap proxy
- `List / tuple operations`: `46.66%` application-gap vs `53.34%` selection-gap proxy (near split)
- `Arithmetic / conditionals`: `58.32%` application-gap proxy vs `41.68%` selection-gap proxy

Important proxy caveats:

- `Dictionary operations`: `99.14%` selection-gap proxy is driven by the **narrow `dict_comp` proxy** and should not be read as "students never used dictionaries" in a literal sense.
- `File operations`: `90.42%` selection-gap proxy is also influenced by weak proxies (`import_*`, `try_stmt`) because `open()` is not tracked.

Pedagogical implication:

- For concepts like loops/pattern/data-analysis, many S2 failures already include relevant constructs (application/debugging problem).
- For concepts with more balanced or proxy-absent signals, interventions should distinguish concept selection from implementation/debugging failures.

Files:

- `analysis/concept_knowledge_modeling/s2_final_attempt_concept_decomposition_rows.csv`
- `analysis/concept_knowledge_modeling/s2_final_attempt_concept_decomposition_summary.csv`
- `analysis/concept_knowledge_modeling/s2_final_attempt_concept_decomposition_summary_aligned_proxy.csv`
- `analysis/concept_knowledge_modeling/s2_final_attempt_concept_decomposition_proxy_rollup.csv`
- `analysis/concept_knowledge_modeling/s2_final_attempt_concept_decomposition_proxy_rollup_aligned_proxy.csv`
- `analysis/concept_knowledge_modeling/s2_final_attempt_snapshot_alignment_summary.csv`

## Step 9 Summary (Operational / Curriculum Implications)

1. The concept map is now complete (`251/251` questions) and reproducible, with full guide-cue coverage.
2. The hardest concept cluster is clear: `Data analysis / aggregation` (and then pattern/file/formatting-heavy work).
3. Construct-usage-vs-mastery distinguishes intervention types:
   - `Loops`: high usage + low mastery -> **practice + feedback**
   - `ListComp/DictComp/Try`: low usage + low mastery -> **exposure + pattern recognition + practice**
4. Repeat students often master new concepts across terms, but retention/acquisition for `Data analysis` and `Pattern printing` is weak.
5. Final-S2 failures are concept-heavy in strings/loops/formatting, and many already show relevant constructs -> the bottleneck is often **application/debugging**, not just concept exposure.
6. The empirical prerequisite graph is useful for curriculum review, but it needs a real syllabus-order comparison (not the proxy order used here) before making sequencing changes.
