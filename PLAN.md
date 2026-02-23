# Error Pattern Mining Plan

## Goal

Produce `analysis/ERRORS.md` with per-question, high-specificity logic error patterns from final evaluated student submissions using `tree-sitter-python`, enriched with test-case evidence and concrete code examples.

## Checklist

- [x] Confirm data joins for final submissions, code snapshots, and question tests
- [x] Build pilot pipeline for one question (parse, cluster, inspect, summarize)
- [x] Evaluate pilot quality (specificity, frequency coverage, instructional usefulness)
- [x] Iterate feature extraction / clustering until patterns are rich and defensible
- [x] Write pilot section in `analysis/ERRORS.md` and request user feedback
- [x] Cluster questions and replace `analysis/ERRORS.md` with cluster index
- [x] Move pilot into cluster-specific file and extend to all variants in that cluster
- [ ] Generalize pipeline across all questions after feedback

## Steps

1. Read `analysis/README.md` and `analysis/REPORT.md`, plus existing taxonomy scripts, to align with current datasets and avoid duplicating prior work.
2. Build a reproducible one-question extraction pipeline that selects only final evaluated submissions, strips evaluator scaffolding, and joins question metadata/tests.
3. Parse pilot-question submissions with `tree-sitter-python`; derive structural fingerprints, targeted semantic detectors, and failure signatures from test-case results.
4. Cluster failing final submissions into specific error patterns (not broad categories), then manually inspect representative code for each cluster.
5. Stress-test the pilot output for richness and coverage; refine detectors/clustering if results are too generic or fragmented.
6. Draft `analysis/ERRORS.md` with methodology + one fully worked question section (frequencies, impact, examples, why it happens), then pause for user feedback before scaling.

## Notes / Constraints

- Final submissions only: use latest `submission` event per `(namespace, problem_id, student_id)`.
- Focus on logic-level mistakes in parseable code, but include parse/runtime final-submission patterns when they materially affect outcomes.
- Use test cases as evidence (which cases fail, what inputs trigger failures), but go beyond pass/fail counts using AST structure and code-pattern clustering.

## Actions & Outcomes (Current Progress)

- Completed Step 1:
  - Read `analysis/README.md` and `analysis/REPORT.md`.
  - Reused scaffolding helpers from `analysis/generate_error_taxonomy.py` (`load_question_skeletons`, `extract_student_editable_code`, `TsAnalyzer`, `parse_test_case_results`).

- Completed Step 2:
  - Built `analysis/pilot_logic_error_patterns.py` to join final submission rows from `analysis/submission_timeline.parquet` + `analysis/code_snapshots.parquet` with raw `CompilationResult` from `submissions/*.json`.
  - Verified `656/656` final submissions matched raw private evaluation payloads for the pilot question.

- Completed Steps 3-5 (pilot evaluation + iteration):
  - Pilot question: `ns_25t2_py21_1`, Problem `16` (`Pangram Check`).
  - v1 residual wrong-answer bucket was too large (`126/337`, `37.4%`).
  - Iterated detectors to be executable-body-aware (docstring-safe) and added specific patterns (`...` placeholder, constant returns, exact-order checks, substring-direction errors, `text.isalpha()` gating, counting-vs-coverage, runtime subtypes).
  - v2 residual reduced to `59/337` (`17.5%`); largest exact residual cluster size is `2`.

- Completed Step 6 (pilot write-up):
  - Drafted an initial pilot `analysis/ERRORS.md` (single-question write-up), then migrated the content into a cluster-specific file after user feedback.

- Completed question clustering + index migration:
  - Added `analysis/generate_question_clusters.py` to cluster semantically near-identical questions using normalized title/prompt/template/tests fingerprints (plus strict same-title near-duplicate fallback).
  - Generated `analysis/question_clusters.csv` and `analysis/question_cluster_members.csv`.
  - Replaced `analysis/ERRORS.md` with an index of all clusters, their variants, per-question submission counts, and links to per-cluster analysis files (including future placeholders).

- Completed cluster-level extension for Pangram:
  - Identified `Pangram Check` as cluster `C013` with 2 exact-duplicate variants: `ns_25t2_py21_1/16` and `ns_25t2_py21_2/18`.
  - Ran the tree-sitter pilot analysis for both variants.
  - Created `analysis/ERRORS-cluster-c013-pangram-check-f0d5ae7d.md` with cluster-level aggregated patterns, per-variant comparisons, and representative examples including anonymized student IDs.

- Cleanup / correctness improvement:
  - Fixed a row-level labeling bug in `analysis/pilot_logic_error_patterns.py` where some all-pass rows could inherit heuristic labels in the exported CSV (summary counts were already correct because they only summarize non-full rows).
  - Regenerated both Pangram pilot outputs after the fix.
