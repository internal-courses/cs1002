# PyOPPE

PyOPPE is a reproducible analysis repository for OPPE Python programming-exam data (2025 terms), including:

- raw event logs (`submissions/*.json`)
- question metadata (`problems/*/*.json`)
- derived canonical datasets (`analysis/*.csv`, `analysis/*.parquet`)
- stakeholder-facing reports and story pages (`analysis/*.md`, `analysis/*.html`)

## GitHub Pages

This repository is published at:

- https://sanand0.github.io/pyoppe/

Direct report/story pages:

- Main narrative report: https://sanand0.github.io/pyoppe/analysis/report.html
- Error-pattern story: https://sanand0.github.io/pyoppe/analysis/errors.html
- Teachable cohort story: https://sanand0.github.io/pyoppe/analysis/teachable.html
- Quick-fixes story: https://sanand0.github.io/pyoppe/analysis/quick-fixes.html

## Purpose

This repo exists to answer practical exam-quality and student-learning questions from real OPPE traces, such as:

- where students get blocked (syntax vs logic vs process)
- which questions and test designs create avoidable failure
- how student behavior changes across terms/waves
- which intervention groups are most teachable now

The project emphasizes reproducibility: generated analysis should be rerunnable from checked-in scripts + raw data.

## Repository Structure

### Top-level

- `analysis/`  
  All analysis scripts, canonical datasets, generated CSV/Parquet outputs, and report/story artifacts.
- `problems/`  
  Question bank snapshots by namespace (`ns_*` directories, one JSON per problem).
- `submissions/`  
  Raw newline-delimited JSON event logs (`saved_code`, `test_run`, `submission` events).
- `private/`  
  Private notes/reference docs used during analysis.
- `AGENTS.md`  
  Project operating rules (reproducibility, generated-file policy, interpretation caveats).
- `PLAN.md`  
  Working plan notes for deeper analysis pipelines.
- `prompts.md`  
  Prompt/worklog document for report and analysis iteration.
- `.gitignore`  
  Ignore policy for raw data and most generated outputs.
- `.nojekyll`  
  GitHub Pages compatibility file.

### `analysis/` (important files and folders)

Core documentation:

- `analysis/README.md`: data model, canonical pipeline, and reproducibility notes.
- `analysis/REPORT.md`: plain-language stakeholder report (recommended first read).
- `analysis/guide.md`: OPPE administration guide from the data.
- `analysis/ERRORS.md`: cluster index of detailed question-level error analyses.

Canonical data products:

- `analysis/final_scores.csv`: student-question grain (`Namespace`, `ProblemID`, `StudentID`).
- `analysis/submission_timeline.parquet`: event-level timeline (recommended for behavior analysis).
- `analysis/code_snapshots.parquet`: deduplicated code text keyed by hash.
- `analysis/question_metadata.csv`: per-question metadata/test counts.
- `analysis/schedule.csv`: namespace timing windows (IST).
- `analysis/anomalous_accounts.csv`: flagged account anomalies.

Major generated analysis folders:

- `analysis/syntax_bottleneck_quantified/`
- `analysis/error_taxonomy/`
- `analysis/process_analysis/`
- `analysis/classical_item_quality/`
- `analysis/psychometric_irt/`
- `analysis/evaluation_redesign/`
- `analysis/longitudinal_analysis/`
- `analysis/concept_knowledge_modeling/`
- `analysis/score_failure_profiles/`

Additional focused outputs:

- `analysis/no-private-submissions.*`
- `analysis/teachable.*`
- `analysis/thrashers_language.*`
- `analysis/buddy_program_evaluation.*`
- `analysis/quick-fixes.*`
- `analysis/ERRORS-cluster-*.md` (detailed error writeups by question cluster)

## Data Model (quick view)

- Event level: one row per student action in `submission_timeline.parquet`
- Student-question level: one row per `(Namespace, ProblemID, StudentID)` in `final_scores.csv`

Use `final_scores.csv` for most aggregates, and join to timeline/snapshots only when process/code-level detail is needed.

## Prerequisites

- `duckdb` CLI
- `uv` (for running Python scripts, including inline-script dependencies)
- Python 3.12+ (for most `uv run --script` pipelines)
- Raw inputs present:
  - `submissions/*.json`
  - `problems/*/*.json`

## How to Run the Repository

Run all commands from repo root (`pyoppe/`).

### 1) Build canonical datasets

```bash
duckdb -bail -c ".read analysis/student-question-pairs.sql"
duckdb -bail -c ".read analysis/scores.sql"
duckdb -bail -c ".read analysis/final_scores.sql"
duckdb -bail -c ".read analysis/final_scores_termwise.sql"
duckdb -bail -c ".read analysis/final_scores_pivot.sql"

uv run python analysis/question_metadata.py
uv run python analysis/submission_timeline.py
uv run python analysis/generate_schedule.py
uv run python analysis/generate_anomalous_accounts.py
uv run analysis/generate_score_failure_profiles.py
```

### 2) Run deeper analysis modules (optional, recommended)

```bash
uv run analysis/generate_error_taxonomy.py
uv run analysis/generate_syntax_bottleneck_quantified.py
uv run analysis/generate_process_analysis.py
uv run analysis/generate_classical_item_quality.py
uv run analysis/generate_psychometric_irt.py
uv run analysis/generate_evaluation_redesign.py
uv run analysis/generate_longitudinal_analysis.py
uv run analysis/generate_concept_knowledge_modeling.py
```

### 3) Generate focused reports

```bash
uv run analysis/teachable.py
uv run analysis/thrashers_language.py
uv run analysis/buddy_program_evaluation.py
uv run analysis/generate_no_private_submissions_report.py
uv run analysis/generate_question_clusters.py
uv run analysis/generate_top4_cluster_error_reports.py
uv run analysis/export_errors_json.py
```

### 4) Build question catalog HTML (from question JSON)

```bash
cd problems
uv run python all_questions.py
```

## How to Interpret the Reports

Start here:

1. `analysis/report.html` or `analysis/REPORT.md` for the executive narrative.
2. `analysis/guide.md` for exam operations/scheduling interpretation.
3. `analysis/ERRORS.md` + `analysis/ERRORS-cluster-*.md` for question-specific failure patterns.
4. `analysis/quick-fixes.md` / `analysis/quick-fixes.html` for highest-impact low-effort test/prompt fixes.
5. `analysis/teachable.md` / `analysis/teachable.html` for intervention targeting.

Interpretation notes:

- `latest_submission_score` in `final_scores.csv` is based on the latest submission event for that student-question row.
- Many “non-submission” rows can reflect platform capture differences by namespace; check `no-private-submissions.*` before drawing behavior conclusions.
- Cross-term comparisons are progression-filtered by course design (later terms contain more repeaters by design); do not compare raw term pass rates naively.
- `schedule.csv` times are IST (`+05:30`) and are activity-window estimates, not official timetable slots.

## Reproducibility and Generated Files

- Prefer editing generator scripts (`analysis/*.py`, `analysis/*.sql`) rather than hand-editing generated outputs.
- Most generated CSV/Parquet files are intentionally treated as ephemeral (`.gitignore`); regenerate as needed.
- If a published HTML story depends on a generated data file at runtime, explicitly track that file in git (current example: `analysis/teachable.csv`).

## Troubleshooting

- If scripts fail with missing-file errors, verify `submissions/*.json` and `problems/*/*.json` exist locally.
- If DuckDB SQL scripts fail, regenerate prerequisites in order (student-question pairs -> scores -> final tables).
- If report values look inconsistent, rebuild canonical datasets first, then rerun downstream modules.
