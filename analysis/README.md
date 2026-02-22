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

# Classical Item Quality Analysis

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

# Error Taxonomy

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
