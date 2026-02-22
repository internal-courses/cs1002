# EDA

## Coverage (Codex 5.3 medium)

Each \*.json (JSON-line files) has lines with these keys:

- Namespace, e.g. ns_25t3_py11. 25 => Year 2025, t3 => Term 3, py11 => Python 1.1 (the first Python programming assignment in that term)
- ProblemID, e.g. 5, 6, 11, 12
- StudentID, an encoded unique ID for each student
- FileName, file that was evaluated, e.g. saved_code/test.py_2025-11-09T05:36:48.628540Z
- EvaluationType, e.g. public, private
- CompilationResult: A JSON object with these keys:
  - status
  - reason
  - compilation_errors
  - num_test_evaluated
  - num_test_passed
  - summary
  - score
  - evaluation_result_json
  - test_case_results: list of JSON objects with these keys:
    - passed
    - reason
    - output
    - expected_output
- Base64Code
- LastUpdated

Write and run an EFFICIENT analysis/student-question-pairs.sql DuckDB query to create an analysis/student-question-pairs.csv with all unique combinations of these columns, sorted:

- Namespace
- ProblemID
- StudentID

... and share how long the query takes to run.

## Scores

Write and run an EFFICIENT analysis/scores.sql DuckDB query to create an analysis/scores.csv listing each score, i.e. with the columns:

- Namespace
- ProblemID
- StudentID
- FileName
- EvaluationType
- CompilationResult.score

... and share how long the query takes to run.

## Final scores

Write and run an EFFICIENT analysis/final_scores.sql DuckDB query to create an analysis/final_scores.csv listing each score, i.e. with the columns:

- Namespace
- ProblemID
- StudentID
- FileName
- CompilationResult.score

.. where EvaluationType = private and it has the latest (i.e. MAX Filaname) record for each (Namespace, ProblemID, StudentID) combination.

## Scores pivot

Create analysis/final_scores_pivot.csv that creates a pivot table from analysis/final_scores.csv with:

- Rows: StudentID
- Columns: Namespace
- Values: SUM(CompilationResult.score)

## Understand the structure

Based on this, help me understand and give me an intuition about the structure of the data, e.g.

- How many students are there in each term?
- How does the Namespace relate to the term, the proctored exam in each term, and the question in each exam?
- There are probably variations of the same question across different students. How does this work?
- etc.

**ANS**: In 2025, we have 3 terms worth of data for 13,299 unique students (some students appear in multiple terms):

- Term 1 (t1): 6,638 unique students
- Term 2 (t2): 5,197 unique students
- Term 3 (t3): 5,055 unique students

Namespace structure is mostly: ns_YYtT_pyXX[_V]

- Example: ns_25t3_py11_1
- 25 = year 2025
- t3 = term 3
- py11 = exam/assessment code
- Optional \_1 / \_2 = variant/set of that exam

So a question identity is effectively: Namespace + ProblemID

- ProblemID is the question slot within a namespace/exam variant.
- Most namespaces have exactly 7 questions.
- One special namespace exists: ns_25t1_py_15_exe with 13 questions (an outlier format).

There are question variants (\_1 vs \_2). The same base exam (e.g. ns_25t3_py13_1 vs ns_25t3_py13_2) can have different question content for same ProblemID.

- Students are usually in one variant of a base exam, not both.
- Only 2 student+base-exam cases appear in both variants (likely exceptions/data quirks).
- Per term, students mostly have 1 or 2 base exams, suggesting multiple exam groups/tracks within a term (not one single universal paper for all).
- Notable Quirk: ns_25t2_py21_2 uses problem IDs 14,16,18,20,22,24,26 (even-only), while ns_25t2_py21_1 uses 14..20 contiguous. So numbering itself can differ between variants.

## Understand the structure more

Create analysis/final_scores_termwise.csv which has the columns:

- StudentID
- YearTerm (e.g. 25t1, 25t2, 25t3)
- Score: SUM of CompilationResult.score across all questions in that term for that student (i.e. sum across all rows in final_scores.csv for that student and that term)
- Max: MAX of CompilationResult.score across all questions in that term for that student (i.e. max across all rows in final_scores.csv for that student and that term)

Sort by StudentID, YearTerm.

### Correction

Replace MAX with the highest possible score a student can achieve in that term's exam.

## Create a guide

I'm still a little hazy on the following. Help me understand:

- In each term, how many OPPE exams are there? Is this a hard and fast rule?
- How many variants per exam are there?
- How are the questions and variations distributed across terms and students?
- How are students assigned to the variations?
- Do students repeat across terms? Who repeats - is there a pattern?

Create a comprehensive analysis/guide.md that explains the way in which these exams are administered, written as if it's a tutorial from the exam body to a new exam administrator, explaining the process of creating and administering these exams, and how the data is structured as a result. Use the insights from the previous analyses to inform this guide.

The guide should be rich in specific examples from the data.
It should point out to counter-examples, exceptions, edge-cases, etc. guessing the reasons.
It should mention statistics and refer to individual examples wherever relevant.

### Update guide

It looks like each student typically writes 2 OPPEs in a term, i.e. one of {py11, py12, py13, py14} and then one of {py21, py22, py23}. Is that right?

Look at the timing of these exams and use that to update the guide to give an intuition about the structure and schedule.

### Update guide schedule

Under "Concrete calendar examples", include which namespaces appear in which term, the timing of each, the number of students in each, and which questions are included (mention the ACTUAL questions rewritten in one sentence; entire question not required - just the beginning, enough to clearly help a Python expert distinguish between them).

### Format guide schedule

- Rewrite Timing as `2025-07-18 06:30` -> `Fri 18 Jul 2025, 06:30`
- Use separate tables for each wave
- Mention total number of students in each wave
- Mention number of students overlapping within namespaces in a wave as well as across waves

### Update timing

FYI: I formatted the guide and removed the "Write code for " prefix before each question.
Update the timing of each wave to the nearest 15-minute mark covering 95% of activity.
For the activity, don't just use the final submissions. Use the entire activity, i.e. including saved_code and test_run.

### Automate schedule

Sorry, I meant round off the 95% activity window in EACH namespace.
Also, save and run a script to generate an analysis/schedule.csv with columns: term, wave, namespace, start_time, end_time, num_students, questions (list of question summaries), and use that to update the guide schedule section.

---

Ensure all times are in IST (UTC+5:30).

---

Always sort by start date - in the CSV AND in the guide.md

## Analysis Plan

My aim is to understand how students think and learn, based on this data.

This is rich data. We have the code students wrote, as well as the "path" they took to get there at a granular level, i.e. their saved_code and test_run history.

We can use this to understand

- How students approach problems
- What mistakes they make
  - What misconceptions they have
  - What gaps they have in their knowledge
- How they iterate and improve
  - What kinds of feedback they get from the test runs
  - What they change in response to that feedback
  - How long & how many iterations they take for the final submission
  - What kinds of errors and feedback lead to what kinds of changes in the code
- How they use feedback from the test runs

## Standardize

<!-- https://claude.ai/chat/9f72f7e2-97e5-4d82-8a55-374f6ebe407f-->

Task 1: `analysis/final_scores.csv` contains only latest private records. Absence of a row can mean non-assignment, no submission, or ingestion gaps. Update it to include, for each (Namespace, ProblemID, StudentID) combination,

- first_event: time of the first event
- last_event: time of the last event
- saved_code_events: number of saved_code events for that combination
- test_run_events: number of test_run events for that combination
- submission_events: number of submission events for that combination

For students without a submission event, include them but with a null FileName and CompilationResult.score.
For students without any events, drop them (since they likely never opened the exam, and we have no data on them at all).

Task 2: Create and run a script to generate `analysis/anomalous_accounts.csv` with accounts that have abnormal patterns, e.g. appearing in many namespaces, appearing in both variants of the same base exam, etc. E.g. `f14645d...` appearing in 13 namespaces and 77 final rows — likely an admin or test account. Scan for accounts with abnormal namespace counts (appearing in both variants, appearing in far more namespaces than the typical 2 per term). We will exclude these from analytical samples but keep them tagged for reference.

### More standardization

Task 3: Write and run an `analyze/submission_timeline.py` to standardize the snapshot data. The raw `submissions/*.json` files contain saved_code, test_run, and submission events at 10–30 second intervals. Parse these into a uniform timeline table `analysis/submission_timeline.json` per student-question attempt: `(Namespace, ProblemID, StudentID, timestamp, event_type, code_snapshot, test_results_if_any)`. Compute basic derived fields: `seconds_since_start`, `code_length`, `is_parseable` (does the snapshot parse as valid Python without syntax errors).

Task 4: Write and run a `analyze/question_metadata.py` to map questions to problem metadata. From `problems/*/*.json`, extract for each question: the problem statement, any provided skeleton/template code, the list of public test cases, and the number of private test cases. Store this in `analysis/question_metadata.csv` with columns: `(Namespace, ProblemID, question_text, has_skeleton_code, num_public_tests, num_private_tests)`.

These may be slow. Factor that in.

### Consolidate and document

Create an `analysis/README.md` that will explain in simple terms

- The entire structure of the data
- The analysis we have done so far
- Key insights we have found so far

### Consistency

This conversation meandered and generated outputs at various stages. How can we improve consistency, standardization, and document quality?
For example, are there datasets that are subsets of another or easily derivable and therefore redundant?
Are there metrics that are inconsistent, and therefore need standardization?
What would an expert data engineer / analyst or subject matter expert in this field check or recognize patterns that beginners would miss?
Using this, revise the scripts, re-run them, revise analysis/README.md and give be the improved version.
Write this version without referring to the history, as if it were the first draft, a result of running these scripts in a single-shot.

### Optimization

Move analyze/* into analysis/* and update the docs accordingly.
Also, submission_timeline.json is huge. Is there a benefit to keeping it this way? Or can DuckDB process the raw JSON files almost as efficiently?
What would be the optimal space and speed efficient way of storing this data? Don't hesitate to rewrite completely - focus on what's best, not what's incrementally better.
Modify accordingly and update analysis/README.md. Ensure that everything is written line a first draft - not referencing any history.

### Execution

Include a ```bash Markdown code fence, copy-pasting which will generate all the output scripts. Add comments mentioning how long it'll take - for scripts that'll take longer than 5 seconds.
