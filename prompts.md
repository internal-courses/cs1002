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

Move analyze/_ into analysis/_ and update the docs accordingly.
Also, submission_timeline.json is huge. Is there a benefit to keeping it this way? Or can DuckDB process the raw JSON files almost as efficiently?
What would be the optimal space and speed efficient way of storing this data? Don't hesitate to rewrite completely - focus on what's best, not what's incrementally better.
Modify accordingly and update analysis/README.md. Ensure that everything is written line a first draft - not referencing any history.

### Execution

Include a ```bash Markdown code fence, copy-pasting which will generate all the output scripts. Add comments mentioning how long it'll take - for scripts that'll take longer than 5 seconds.

# Step 1: Score Distributions, Failure Profiles, and the Non-Submission Problem

Read analysis/README.md to understand the data structure.

Now, we need a baseline picture of what's happening before we can diagnose why. But the single most striking fact from Step 0 — that 71.72% of student-question rows have activity but no submission — means the baseline picture is more nuanced than "who scored what."

Let's calculate: Score Distributions, Failure Profiles, and the Non-Submission Problem

**1a. Classify every student-question row by outcome category.**

Using `final_scores.csv` (which has both `submission_events` count and `latest_submission_score`) and `submission_timeline.parquet` (which has all test_run events), classify each of the 151,778 student-question rows into one of these categories:

| Category                    | Definition                                                       |
| --------------------------- | ---------------------------------------------------------------- |
| **Full pass**               | Has a submission; latest submission score = 100 (or max)         |
| **Partial pass**            | Has a submission; 0 < score < max                                |
| **Submitted, zero**         | Has a submission; score = 0                                      |
| **Active, never submitted** | Has test_run events but no submission event                      |
| **No activity**             | No events at all (if any such rows exist after Step 0 filtering) |

The "active, never submitted" category is critical. It's 71.72% of rows. These students _tried_ — they wrote code, ran tests — but never crossed the threshold to submit. Understanding why is one of your central questions.

**1b. Within "active, never submitted," further classify using timeline data.**

Join to `submission_timeline.parquet` and characterise each non-submitting student-question:

- **Had passing test runs but didn't submit**: The student got at least one test_run where some/all public tests passed, yet never submitted. This could indicate they didn't realise they needed to submit separately, ran out of time, or weren't confident enough.
- **All test runs failed**: Every test_run failed. Student was stuck and eventually gave up or ran out of time.
- **Very few events (≤3 test_runs)**: Barely attempted. Possibly opened the question, looked at it, and moved on.
- **Substantial activity, all failing**: Many test_runs (>10) but never passed a public test. This is the "thrashing" or "stuck" population.

**1c. Per-question score distributions.**

For each of the 251 questions, compute:

- Submission rate (fraction of assigned students who submitted)
- Among submitters: score distribution (histogram or summary stats: mean, median, % at zero, % at full marks)
- Among all assigned students (including non-submitters as zeros): effective score distribution
- Pass rate per individual test case (public and private separately, from submission test results)

Plot the score distributions. Flag questions that are:

- **Ceiling**: >80% of submitters get full marks (too easy, or only confident students submit)
- **Floor**: >70% of submitters score zero (too hard, or there's a gating problem)
- **Bimodal**: Clusters at zero and full marks with little in between (threshold/cliff effect)
- **Healthy spread**: Scores distributed across the range

**1d. Aggregate by wave, term, and time slot.**

Using `schedule.csv` for timing:

- Compare submission rates and score distributions between Wave 1 and Wave 2 within each term.
- Compare across time slots within a wave (e.g., the morning exam vs the afternoon exam on the same day). Your schedule shows that 25t1 Wave 2 has three back-to-back exams on a single Sunday (py21 at 09:15, py22 at 13:30, py23 at 16:15). If performance or submission rates decline through the day, that's fatigue, not difficulty.
- Compare across terms for any reused questions (your guide noted some questions appear in multiple terms, e.g., "Check is even or divisible by 5" in 25t1 py11_1 and 25t2 py12_1).

**1e. The non-submission investigation.**

This is important enough to deserve its own sub-analysis. For the "active, never submitted" population:

- What's the distribution of their test_run count? (Are most doing 1–2 runs, or are some doing 50+ runs and still not submitting?)
- What's the distribution of their total active time?
- What fraction had at least one test_run that passed at least one public test case?
- Does the non-submission rate vary by question, by wave, by time slot? If it's higher for the 3rd exam of the day, it may be a time/fatigue issue. If it's higher for specific questions, those questions may be demoralising or confusing.
- What does the _last_ snapshot of non-submitters look like? Is it parseable? Does it represent a partial solution?

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings as a NEW section in analysis/README.md called "Score Distributions, Failure Profiles, and the Non-Submission Problem"

## Revise

Drop the generate_readme.py - it's fine if this is manually generated. Update "## 8) Score Distributions, Failure Profiles, and the Non-Submission Problem" into "# Score Distributions, Failure Profiles, and the Non-Submission Problem", i.e. a L1 heading.

If there are any other insights from the data that will be useful for future analysis or are noteworthy, include them in analysis/README.md manually.

Take a final look at the overall changes to analysis/README.md for consistency from the perspective of a person reading it for the first time, revise as required. Then `git add` all source files (not generated files) including analysis/README.md.

## Re-revise

Delete analysis/generate_readme.py and re-document as if analysis/README.md was manually written. Stage changes.

Add to .gitignore the minimal patterns required to ignore generated files. Stage changes.

## Clarification

I've made a few manual edits to analysis/README.md.

Also, one clarification. Students who write Term 1 need not write Term 2. I mean, if they've passed in Term 1, they just move on. Only failing students need to write Term 2. Likewise Term 2 to Term 3. Clarify this in analysis/README.md.

**Reused question comparison**. analysis/README.md compares "Check is even or divisible by 5" across t1 and t2. But t2 students are the ones who _failed_ t1, so if this question has a lower pass rate in t2, that's expected from population composition alone — it doesn't tell you anything about the question or the teaching. Add a note that cross-term comparisons on reused questions are confounded by the progressive-filter design: later terms have weaker populations by construction, so pass rate changes reflect the population mix, not question difficulty or learning.

**Term-wave summary in 1d** — the framing currently reads as a term-over-term comparison (submission rates, effective means across terms). Any language that implies comparison across terms should note that t1, t2, t3 populations are not comparable cohorts. Within-term Wave 1 vs Wave 2 comparisons remain valid since those are the same students ~35 days apart.

**Non-submission behavioural profiles** — currently pooled across all terms. This is fine as a global baseline, but worth flagging that Term 3 non-submitters in submission-positive namespaces are twice-failing students, which may give them different behavioural signatures than Term 1 non-submitters encountering the exam for the first time. If you want to check this cheaply, break the `non_submission_subtype_summary.csv` by term and see whether the thrashing/stuck proportions shift.

# Step 2: Classical Item Quality Analysis

Step 1 told you _what happened_. Step 2 asks: _is the exam measuring well?_ This is the first step toward answering your question about evaluation quality.

**2a. Per-test-case difficulty and discrimination.**

For each test case within each question (using submission-level results from the scored submissions in `final_scores.csv` or `submission_timeline.parquet`):

- **Difficulty index (p)**: Proportion of submitting students who pass this test case.
- **Point-biserial discrimination**: Correlation between passing this test case (0/1) and the student's total score across all questions in the same namespace. Use `scipy.stats.pointbiserialr`. A good test case has r > 0.30.

Important scoping decision: compute discrimination against _submitters only_ (since non-submitters don't have test case results). Note this creates a selection effect — submitters are likely stronger on average — so discrimination indices may underestimate true population discrimination.

**2b. Inter-test-case redundancy within each question.**

For each question, compute pairwise Pearson correlations (or phi coefficients, since these are binary) between its \~7 test cases. With 3.6 public + 3.5 private = \~7 test cases per question, this is a 7×7 correlation matrix — small and inspectable. Flag pairs with correlation > 0.90 as near-redundant.

**2c. Test case dependency structure.**

For each pair of test cases (A, B) within a question:

- P(pass B | pass A)
- P(pass B | fail A)

If P(pass B | fail A) < 0.05, then A is effectively a prerequisite for B. Build a directed dependency graph per question. This reveals whether your \~7 test cases form a hierarchy (easy → hard) or are genuinely independent checks.

Note: with only \~3.5 private test cases per question, you may find that the private tests form a near-linear chain (pass test 1 → test 2 → test 3 in order, rarely skipping). If so, only the _last_ test in the chain is truly testing something new; the earlier ones are just prerequisites.

**2d. Exam-level reliability.**

Compute Cronbach's alpha across all test cases in a single namespace. With \~7 questions × \~7 test cases = \~49 binary items per exam, you have enough for a meaningful reliability estimate.

**2e. Public vs. private test case analysis.**

Since you have both public and private test results, a critical question: are students "overfitting" to public tests? Compute:

- Fraction of students who pass all public tests but fail one or more private tests (per question)
- Fraction of students who pass all private tests but fail one or more public tests (should be rare — private tests are typically harder/broader)

If public-pass/private-fail is common, students may be tuning their code to the specific public test cases rather than solving the general problem. This is a specific form of evaluation gaming.

**What This Tells You**

You'll know which of your \~1,750 test cases are doing useful evaluative work and which are noise or redundancy. You'll know whether your exams have adequate reliability. And the public-vs-private analysis tells you whether students are gaming the visible test cases — an important input for evaluation design.

**Action point**: Test cases with discrimination < 0.15 and those with >0.90 redundancy are candidates for replacement. The public/private gap analysis informs whether to change the ratio of visible vs. hidden test cases.

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# Classical Item Quality Analysis"

## Revise

Yes, do both:

1. A follow-up step using same-code public/private pairing via code_sha256 for a cleaner overfitting estimate.
2. Add transitive reduction on the dependency graphs to isolate the minimal “new information” test cases per question.

Update the scripts, re-run, and update the documentation.

# Step 3: Error Taxonomy (Full Population, Tree-Sitter-Enabled)

Steps 1 and 2 told you _that_ students are failing and that your test cases are heavily redundant. Step 3 tells you _how_ students fail — the nature of the errors. Tree-sitter fundamentally upgrades this step by enabling structural analysis even on broken code. `temp/tree_sitter_example.py` has a demo of how to use tree-sitter-python.

**3a. Define the code to classify for each track.**

| Track                                               | Code to Classify                                       | Source                                                                |
| --------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------- |
| Track A: submitters                                 | Latest submission code                                 | Submission event → code_snapshots.parquet via code_sha256             |
| Track A: non-submitters (in submission-positive NS) | Last test_run snapshot code                            | Last test_run in submission_timeline.parquet → code_snapshots.parquet |
| Track B: zero-submission NS                         | Best test_run snapshot code (most public tests passed) | Best-scoring test_run → code_snapshots.parquet                        |

This gives you classifiable code for essentially all 151,778 student-question rows.

**3b. Tree-sitter structural parse of every code snapshot.**

Use tree-sitter-python as the primary parser for _all_ code snapshots (not just parseable ones):

For each snapshot, extract:

- **Structural constructs present**: Which of the following appear in the tree? Function definitions, for-loops, while-loops, if/elif/else chains, list comprehensions, dictionary comprehensions, try/except blocks, class definitions, return statements, print statements, import statements.
- **ERROR node count and location**: Tree-sitter marks unparseable regions as ERROR nodes while still parsing surrounding structure. Count the ERROR nodes and identify where they occur (inside a loop body? in a function signature? at top level?).
- **Structural distance from skeleton**: Compare the tree-sitter parse tree of the student's code against the skeleton code from `question_metadata.csv`. Compute:
  - Number of new constructs added beyond skeleton
  - Number of skeleton constructs removed or broken
  - Whether the student's additions are structurally coherent (no ERROR nodes in added regions) vs. structurally broken

This works on the _full population_ — including the \~20% of snapshots that `ast.parse()` rejects. Tree-sitter will still identify that a student wrote a for-loop with a missing colon, a function with mismatched parentheses, etc.

**3c. Classify by skeleton modification status.**

For each code snapshot, using the tree-sitter structural comparison:

| Category                           | Definition                                                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Unmodified skeleton**            | Structural tree is identical (or near-identical by edit distance) to skeleton. Student didn't meaningfully attempt. |
| **Modified, structurally valid**   | Student added/changed constructs; no ERROR nodes in the tree.                                                       |
| **Modified, partially broken**     | Student added constructs but some regions have ERROR nodes. Structure is partially intelligible.                    |
| **Modified, fundamentally broken** | Extensive ERROR nodes; tree structure is not recoverable.                                                           |
| **Empty / trivial**                | <3 non-blank, non-comment lines beyond skeleton.                                                                    |

This is a richer classification than the binary parseable/non-parseable from `ast.parse()`, because tree-sitter distinguishes "one missing colon in an otherwise well-structured program" from "completely garbled code."

**3d. Classify syntax errors in non-parseable code.**

For code that fails `ast.parse()`, use both the `ast` error message and tree-sitter ERROR node analysis:

- **Indentation errors**: Tree-sitter will show correct structure at the wrong nesting level.
- **Missing delimiters**: ERROR node at a specific token boundary (colon, parenthesis, bracket).
- **Invalid syntax**: Catch-all for other parse failures.

Additionally, using tree-sitter: _what was the student trying to do?_ If the ERROR node is inside a for-loop with a correct iterable and body but a missing colon, you can infer the student understands iteration but has a syntax gap. This is the distinction between "can't write Python" and "understands the concept but makes mechanical errors."

**3e. Classify runtime errors (parseable, failing code).**

From test_run results in the timeline (`status`, `reason` fields):

- NameError, TypeError, IndexError, KeyError, ValueError, ZeroDivisionError, RecursionError, AttributeError
- Timeout / time limit exceeded
- MemoryError / resource limit

Use the primary error from the _best_ test_run (most tests passed) for each student-question.

**3f. Classify wrong-output failures.**

For code that runs without errors but fails test cases:

- **Formatting mismatch**: Whitespace, delimiters, case differences.
- **Off-by-one / boundary**: Correct for typical inputs, wrong for edge cases.
- **Partial correctness**: Some cases pass, fundamentally wrong on others.
- **Completely wrong approach**: Algorithm is incorrect.

Use LLM-assisted classification at scale. Validate against a manual sample of \~30–50 per question.

**3g. Regression detection.**

For each student-question attempt, scan the timeline's `is_parseable` sequence:

- **Regression flag**: At least one intermediate snapshot was parseable, but the final code is not.
- **Peak-to-final regression**: Student achieved N passing tests at some point but final state has fewer.

Report: "X% of students who ended with non-parseable code had parseable code at some earlier point."

With tree-sitter, extend this: did the structural complexity of the code _decrease_ over the attempt? (Student had a function with a loop, then deleted it and started over.) Track structural regression, not just parseability regression.

**3h. Build the global error profile.**

Aggregate across both tracks:

| Error Category                                              | Track A Submissions | Track A Non-Submitters | Track B (All) | Total |
| ----------------------------------------------------------- | ------------------- | ---------------------- | ------------- | ----- |
| Unmodified skeleton                                         | ?                   | ?                      | ?             | ?     |
| Modified, partially broken (tree-sitter: structure evident) | ?                   | ?                      | ?             | ?     |
| Modified, fundamentally broken                              | ?                   | ?                      | ?             | ?     |
| Runtime error (by type)                                     | ?                   | ?                      | ?             | ?     |
| Wrong output — formatting                                   | ?                   | ?                      | ?             | ?     |
| Wrong output — edge case                                    | ?                   | ?                      | ?             | ?     |
| Wrong output — logic                                        | ?                   | ?                      | ?             | ?     |
| Timeout                                                     | ?                   | ?                      | ?             | ?     |
| Partial pass                                                | ?                   | ?                      | ?             | ?     |
| Full pass                                                   | ?                   | ?                      | ?             | ?     |

Also report the tree-sitter structural inventory: across all student-question rows, what fraction of students used for-loops? Functions? List comprehensions? Dictionaries? This is a curriculum-level signal: if only 15% of students ever use list comprehensions despite being taught them, that construct hasn't been absorbed.

Break down by question and by term — remembering that cross-term comparisons reflect progressively weaker populations, not curriculum changes.

**What This Tells You**: The tree-sitter-enriched error taxonomy tells you not just _that_ code is broken but _what the student was trying to build_. A student with a well-structured program that has one ERROR node (a missing colon) is fundamentally different from a student with garbled code, even though both fail `ast.parse()`. The structural inventory also doubles as a curriculum diagnostic: which constructs are students actually deploying?

**Action point**: If the "modified, partially broken" category is large (many students with mostly-correct structure and localised errors), this is strong evidence for interventions that help students fix specific mechanical issues — linters, better error messages, targeted syntax exercises. If "unmodified skeleton" is large, the problem is more fundamental.

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# Error Taxonomy"

# Step 4: The Syntax Bottleneck — Quantified (Dual-Track)

This assembles the findings from Steps 1–3 into a single defensible decomposition of why students fail.

**4a. Parseability baseline (full population, enriched by tree-sitter).**

| Metric                                                          | Track A Submissions | Track A Non-Submitters | Track B Best Snapshot |
| --------------------------------------------------------------- | ------------------- | ---------------------- | --------------------- |
| Parseable (ast.parse)                                           | ?                   | ?                      | ?                     |
| Non-parseable, structure evident (tree-sitter: few ERROR nodes) | ?                   | ?                      | ?                     |
| Non-parseable, fundamentally broken                             | ?                   | ?                      | ?                     |
| Unmodified skeleton / empty                                     | ?                   | ?                      | ?                     |

The tree-sitter split within "non-parseable" is the key addition: it separates "almost there mechanically" from "can't construct a program."

**4b. Regression analysis.**

From Step 3g:

- Fraction of students whose final code is non-parseable but who had parseable code earlier.
- Fraction with peak-to-final test-pass regression (passed more tests earlier than at the end).
- Fraction with structural regression (tree-sitter shows simpler structure at the end than at peak complexity).

**4c. Auto-correct syntax and re-score (Track A).**

For Track A submissions that fail to parse:

1. LLM syntax correction (logic-preserving only).
2. Re-run against private test cases.
3. Record new scores.

For "partially broken" code (tree-sitter shows mostly correct structure with localised ERROR nodes), also attempt a simpler approach: rule-based fixes guided by tree-sitter error locations (add missing colons at ERROR nodes in loop/conditional headers, close unmatched brackets). Compare rule-based vs. LLM correction rates to assess how mechanical the remaining syntax errors are.

**4d. Auto-correct and re-evaluate (Track B).**

Same as 4c but against public test cases only (the only ones available for Track B).

**4e. Formatting tax (Track A).**

For submissions that parse and run but fail due to output differences:

- Normalise output and re-compare.
- Compute additional passes.

**4f. Build the gating waterfall (full population).**

| Gate                                                                        | Track A | Track B | Combined |
| --------------------------------------------------------------------------- | ------- | ------- | -------- |
| Unmodified skeleton / didn't attempt                                        | ?       | ?       | ?        |
| Syntax gated — mechanical (tree-sitter: structure evident, few ERROR nodes) | ?       | ?       | ?        |
| Syntax gated — fundamental (tree-sitter: no recoverable structure)          | ?       | ?       | ?        |
| Formatting gated                                                            | ?       | ?       | ?        |
| Edge-case gated (passes core tests, fails edge cases)                       | ?       | ?       | ?        |
| Genuine logic failure                                                       | ?       | ?       | ?        |
| Partial pass                                                                | ?       | ?       | ?        |
| Full pass                                                                   | ?       | ?       | ?        |

The tree-sitter split within the syntax gate is a major refinement: "mechanical syntax" errors are fixable with better tooling or a linter; "fundamental syntax" errors indicate the student can't construct a program at all.

**4g. Skeleton effectiveness analysis.**

Since 96.81% of questions provide skeletons:

- Where in the code are syntax errors occurring — in the skeleton portion (student broke provided code) or in their additions?
- Tree-sitter makes this precise: compare ERROR node locations against the skeleton's parse tree to determine whether errors are in student-added subtrees or in skeleton-provided regions.
- Relationship between modification extent (structural distance from skeleton) and error rate.

**What This Tells You**: The waterfall with tree-sitter-informed syntax splitting produces a cleaner decomposition than the original plan. "Syntax gated — mechanical" vs "syntax gated — fundamental" is the difference between "needs a linter" and "needs more instruction." The regression finding adds: some students can write valid Python but can't maintain it while editing, which is a specific process skill.

**Action point**: Present the waterfall to stakeholders. The mechanical/fundamental syntax split directly informs whether the intervention should be tooling (linter, better error messages) or curriculum (more foundational instruction).

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# The Syntax Bottleneck — Quantified"

# Step 5: Process Analysis — What the Snapshots Reveal

Process analysis is the step _least affected_ by the two-track split — every student has a full timeline regardless of submission status. Tree-sitter makes the AST-level analysis affordable for the full population.

**5a. Build per-attempt timeline features.**

For all 151,778 student-question rows, compute from `submission_timeline.parquet`:

| Feature                        | Computation                                               |
| ------------------------------ | --------------------------------------------------------- |
| Total active time (seconds)    | last_event - first_event                                  |
| Test_run count                 | Count of event_type = 'test_run'                          |
| Time to first parseable code   | First is_parseable = True timestamp minus first event     |
| Time to first public test pass | First test_run with num_test_passed > 0 minus first event |
| Parseable fraction             | Fraction of snapshots with is_parseable = True            |
| Code length trajectory         | Sequence of code_length over time                         |
| Large deletion events          | Snapshots where code_length drops >30%                    |
| Idle gaps (>120s)              | Count and total duration                                  |
| Run-to-run improvement         | Does num_test_passed increase monotonically?              |
| Peak test pass count           | Maximum num_test_passed across all runs                   |
| Final vs. peak regression      | Peak minus final num_test_passed                          |

**5b. Structural evolution tracking (tree-sitter, full population).**

This was previously marked as "selective/advanced" (Step 5f in v2) but tree-sitter makes it a core analysis. For each student-question attempt, parse every snapshot with tree-sitter and track:

| Structural Feature                  | What It Captures                                                                                                                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Construct timeline**              | When did each construct type first appear? (First for-loop at snapshot 5, first function at snapshot 12, first try/except at snapshot 20.)                                        |
| **Structural complexity over time** | Count of non-trivial AST nodes (loops, conditionals, functions) at each snapshot. Monotonically increasing = building up. Oscillating = restructuring. Declining = deleting work. |
| **ERROR node trajectory**           | Count of ERROR nodes over time. Decreasing = fixing problems. Increasing = introducing problems. Persistent = stuck on the same issue.                                            |
| **Structural regression events**    | Snapshots where structural complexity drops significantly (>30% of nodes removed). More granular than code-length-based deletion detection.                                       |

This is computationally heavier than the basic timeline features but tree-sitter parsing is fast (sub-millisecond per snapshot). Across 2M events, expect minutes of processing, not hours.

**5c. Classify behavioural archetypes.**

Using features from 5a and 5b, classify each student-question attempt:

| Archetype                | Identifying Features                                                                                                                                                    |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Steady builder**       | num_test_passed increases over runs; structural complexity increases monotonically; few large deletions; parseable fraction > 0.80                                      |
| **Late starter**         | \>30% of total time before first code change beyond skeleton                                                                                                            |
| **Thrasher**             | High test_run count (>15); num_test_passed oscillates; many structural regression events; ERROR node count fluctuates                                                   |
| **One-shot**             | ≤3 test_runs total; code appears in one or two large increments                                                                                                         |
| **Stuck and abandoned**  | Idle gap >5 min before final event; no improvement in latter half                                                                                                       |
| **Skeleton-only**        | Final code ≈ skeleton; minimal structural additions                                                                                                                     |
| **Regression**           | Had parseable, partially-passing code at some point; final state is worse (fewer tests passing or non-parseable or lower structural complexity)                         |
| **Incremental debugger** | Many test_runs; small changes between runs (low structural diff); ERROR nodes decrease over time; test passes increase. This is the "good debugging process" archetype. |

The "incremental debugger" archetype is new — tree-sitter makes it detectable by tracking small, targeted structural changes. This is the behaviour you want to teach, so identifying students who already do it (and their outcomes) provides a model.

**5d. Compute per-archetype outcomes.**

For each archetype:

- Proportion of all student-question attempts
- Median final outcome (score for Track A submitters; best public test pass count for others)
- Median time spent
- Distribution across questions (do certain questions induce more thrashing?)
- Distribution across terms (remembering that later terms have weaker populations)

**5e. Recovery analysis by error type.**

For each error type from Step 3 (SyntaxError, IndexError, TypeError, etc.):

- **Recovery probability**: P(error resolved within N test_runs) for N = 1, 2, 5, 10
- **Recovery time**: Median time from error introduction to resolution
- **Non-recovery rate**: Fraction of attempts where the error persists through the final event

With tree-sitter: for syntax errors specifically, track whether the student's _structural intent_ was correct even when the syntax was broken. A student who has the right loop structure with a missing colon (tree-sitter shows the loop, ERROR node at the header) is in a very different state than one whose code has no recognisable structure. Separate recovery rates for "syntax error with correct structural intent" vs. "syntax error with no discernible structure."

**5f. "Death spiral" / absorbing state analysis.**

Define states:

- **State 0**: No code beyond skeleton
- **State 1**: Non-parseable, no recoverable structure (tree-sitter: many ERROR nodes)
- **State 1b**: Non-parseable, structure evident (tree-sitter: localised ERROR nodes)
- **State 2**: Parseable, passes 0 tests
- **State 3**: Passes some (not all) public tests
- **State 4**: Passes all public tests (for Track B this is "success"; for Track A, may still fail private tests)
- **State 5**: Passes all tests (Track A only)

Compute transition probabilities between states at each test_run. Look for:

- **Absorbing states**: States from which P(reaching State 4/5) < 5%.
- **Critical transitions**: Which transitions are hardest? State 1 → 1b (gaining structure)? State 1b → 2 (fixing syntax)? State 3 → 4 (handling edge cases)?
- **Time-conditional absorption**: If a student is in State 1 after X% of the exam has elapsed, what's P(reaching State 4)? This identifies the optimal intervention point.

**What This Tells You**

Process analysis answers questions outcome data cannot: whether students fail because they can't start, can't debug, or run out of time; what fraction experience regression; which errors are recoverable; at what point a student's trajectory becomes predetermined.

The tree-sitter structural tracking adds a new dimension: you can now distinguish between students who have the right _conceptual structure_ (correct loop, correct function decomposition) but fail on syntax vs. students who lack the structural thinking entirely. This is the gap between a mechanical problem (fixable with tools) and a conceptual problem (needs teaching).

**Action point**: If the "incremental debugger" archetype has dramatically better outcomes than "thrasher" despite similar time investment, that's direct evidence that teaching debugging _process_ (not just content) would improve results. Use the incremental debugger trajectories as exemplars in teaching materials.

**Action point**: The death-spiral analysis with the tree-sitter-enriched state space identifies optimal intervention points with more precision. State 1b (correct structure, broken syntax) is likely much more recoverable than State 1 (no structure) — confirming with data tells you which students a hint system could actually help.

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# The Syntax Bottleneck — Quantified"

# Step 6: Psychometric Modelling with IRT

Steps 1–5 give a rich descriptive and diagnostic picture. Step 6 provides a principled measurement framework for cross-variant and cross-wave comparisons.

**6a. Model choice: Question-level Graded Response Model.**

Step 2 showed extreme item-level redundancy (34.46% of pairs at phi > 0.90) and very high alpha (>0.97). Fitting test-case-level IRT would violate local independence. Instead:

**Default approach**: Fit a **Graded Response Model (GRM)** at the question level.

Score each question as a polytomous item:

- 0 = passed no test cases
- 1 = passed some but not all test cases
- 2 = passed all test cases

This gives \~7 polytomous items per exam (one per question), which respects the within-question dependency structure while still modelling difficulty and discrimination.

For Track B (no private test results), use the same grading on public test cases from the best test_run.

**6b. Fit the GRM.**

Per namespace (since students in different namespaces face different questions):

- Fit a GRM using `mirt` (R, via `rpy2`) or `girth` (Python).
- Extract per-question: difficulty thresholds (b parameters for each grade boundary) and discrimination (a).
- Extract per-student: latent ability estimate (θ).

For cross-namespace comparison, linking requires shared items. Check whether any questions appear in multiple namespaces (your guide noted some reuse). If linking items exist, fit a concurrent calibration across namespaces. If not, θ estimates are namespace-local and not directly comparable across namespaces.

**6c. Analyse question parameters.**

Plot discrimination vs. difficulty for all questions. Identify:

- **Low-discrimination questions** (a < 0.5): Don't separate students well despite having multiple test cases. These questions need redesign.
- **Very high discrimination questions**: These create cliff effects — a small ability difference flips the outcome. Check whether these correspond to the questions with high bimodal rates from Step 1.
- **Questions with extreme difficulty thresholds**: The GRM gives you separate thresholds for "0 → 1" (any partial credit) and "1 → 2" (full credit). If the "0 → 1" threshold is very high, the question is too hard to even get started on. If the "1 → 2" threshold is very close to the "0 → 1" threshold, partial credit adds little information.

**6d. Test information function.**

Compute the test information function per exam namespace. Plot where the exam provides the most measurement precision:

- If information peaks sharply in the middle, the exam can't distinguish "slightly below average" from "completely lost."
- Given the progressive-filter term structure (later terms have weaker populations), the low-ability region is where you _most_ need information. Check whether the exam provides it.

**6e. Differential Item Functioning (DIF).**

Applicable grouping variables:

- Variant (`_1` vs `_2`) where both exist in the same namespace
- Time slot within a day (morning vs. afternoon) for same-namespace questions
- Wave (1 vs 2) — though this is the same students 35 days apart, so DIF here measures something different (practice effect, curriculum effect)

**6f. Use θ for fairer comparisons.**

If cross-namespace linking is feasible:

- Compare θ distributions across variants to check whether `_1` and `_2` are equally difficult instruments.
- Compare θ distributions across waves to measure within-term growth on a common scale (this feeds Step 8).

**What This Tells You**

The GRM gives you calibrated ability estimates that account for question difficulty and discrimination, which raw scores do not. The test information function tells you where your exam is "blind." Given that later terms contain the weakest students, if the exam's information function drops off at low ability, you're measuring the students who need diagnosis the least and failing to diagnose the ones who need it most.

**Action point**: If the information function is flat at low ability, add easier "warm-up" questions that can discriminate among weak students. This is more actionable than the v2 recommendation of "replace low-discrimination items" (which turned out not to exist).

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# The Syntax Bottleneck — Quantified"

## Context From Steps 1–6

These are the findings that shape everything below.

**The gating waterfall (Step 4)** decomposes all 151,778 student-question rows:

| Gate                                                            | Combined % |
| --------------------------------------------------------------- | ---------- |
| Unmodified skeleton / didn't attempt                            | 6.14%      |
| Syntax gated — mechanical (structure evident, localised errors) | 7.14%      |
| Syntax gated — fundamental (no recoverable structure)           | 2.36%      |
| Formatting gated                                                | 0.25%      |
| Edge-case gated (passes core, fails edge cases)                 | 7.35%      |
| Genuine logic failure                                           | 26.72%     |
| Partial pass                                                    | 3.21%      |
| Full pass                                                       | 46.83%     |

**Genuine logic failure is the single largest failure bucket** — roughly 3x the combined syntax gates. The formatting tax is negligible (0.25%).

**The data has two tracks.** 23 of 35 namespaces have zero submission capture (a data pipeline issue, not student behaviour). Track A (12 submission-positive namespaces, \~42,918 submitter rows + \~11,112 non-submitter rows) has private test results. Track B (23 zero-submission namespaces, \~97,748 rows) has public test\_run results only.

**The S2 self-loop is the dominant "death spiral."** Students in State S2 (parseable code, zero public tests passing) have a 78.93% probability of remaining in S2 at the next test\_run. This is a debugging and problem-decomposition gap, not a syntax gap.

**Test cases are heavily redundant.** 34.46% of within-question item pairs have phi > 0.90\. Cronbach's alpha > 0.97 across namespaces.

**Partial credit adds limited information for \~half the questions.** 47.35% of questions have narrow GRM thresholds (b2 - b1 < 0.35), meaning the "some tests passed" and "all tests passed" categories are nearly the same difficulty level.

**The exam is low-ability blind.** 33/35 namespaces provide much less measurement information in the low-ability region than in the middle. The median low-to-mid information ratio is 0.1555.

**Term progression is a filter, not a cohort.** Term 2 students are those who failed Term 1; Term 3 students failed Term 2\. Students who pass leave the system. The 503 students present in all three terms are the persistently struggling population.

**No wave-pair linking exists.** Step 6 found zero shared anchor items between Wave 1 and Wave 2 within any term, so IRT-based within-term growth analysis is not currently feasible.

**Behavioural archetypes from Step 5:**

| Archetype                | % of Attempts | Success Rate |
| ------------------------ | ------------- | ------------ |
| Steady builder           | 16.10%        | 88.73%       |
| Incremental debugger     | 7.72%         | 77.28%       |
| Regression               | 10.07%        | 5.88%        |
| One-shot                 | 8.67%         | 5.49%        |
| Skeleton-only            | 6.14%         | 0.48%        |
| Stuck and abandoned      | 3.47%         | 3.43%        |
| Thrasher                 | 1.82%         | 43.47%       |
| **Other (unclassified)** | **52.64%**    | —            |

Thrashers spend 2.2x the time of incremental debuggers but achieve much worse outcomes. 52.64% of attempts are unclassified — this needs resolution before the archetype story can be presented.

**Other key findings:**

- 15 cliff-like questions identified (high discrimination + bimodal shape warning).
- Some variant pairs show material linked-θ differences (up to 0.653).
- 50% of runtime errors in the data are "Runtime Error (unspecified)" because the platform provides generic summaries.
- 45% of students who end with non-parseable code had parseable code at some earlier point (regression).
- Recovery analysis: syntax errors with structural intent resolve faster (50% within 1 run) than those without (44%). Wrong Answer errors persist to final run 39% of the time.

---

## Step 7: Evaluation Redesign

**7a. Fix the submission capture pipeline.**

23/35 namespaces have zero submission events. This is an instrumentation issue — students in these namespaces have test\_run activity (and 48.76% passed all public tests in at least one run) but no submissions are recorded. Without fixing this, 64% of student-question rows lack private test results and formal scores.

Investigate:

- Why do these namespaces have no submission events? Is it a logging failure, a UI workflow difference, or a platform configuration change across terms?
- The affected namespaces cluster by term: 100% of 25t1 namespaces, 40% of 25t2 Wave 2, 50% of 25t3 Wave 1, 75% of 25t3 Wave 2.

This is the highest-priority operational fix because it directly determines how much data is available for all future analysis and scoring.

**7b. Address the S2 bottleneck — the largest intervention opportunity.**

The S2 state (parseable code, zero tests passing) affects the largest struggling population. The 78.93% self-loop probability means students in this state almost never escape by doing more of the same. These students can write syntactically valid Python but cannot get their logic to produce correct output.

This is a problem-solving and debugging gap, not a syntax or knowledge gap. Design interventions targeting three specific sub-skills:

1. **Reading and interpreting test case failures.** Currently, students see generic pass/fail results. Provide structured feedback on the first failing test case: the input, the expected output, and the student's actual output. This is a platform change with high leverage — it directly helps the S2 population diagnose what's wrong.
2. **Problem decomposition.** Redesign questions to include explicit sub-tasks (e.g., "First, write a function that does X. Then, use it to do Y."). This gives students intermediate checkpoints and makes partial credit meaningful at genuinely different difficulty levels — addressing the narrow-threshold problem from Step 6 simultaneously.
3. **Incremental testing strategy.** Use Step 5's "incremental debugger" trajectories as teaching exemplars. Show students what effective debugging looks like (small targeted changes, test after each change) vs. what thrashing looks like (large rewrites, no progress). The data shows incremental debuggers achieve 77% success in 2,170 seconds while thrashers achieve 43% success in 4,717 seconds — better process beats more effort.

**7c. Redesign test cases for difficulty spread and reduced redundancy.**

Step 2 found 34.46% of within-question item pairs are near-redundant (phi > 0.90). Step 6 found 47.35% of questions have narrow partial-credit thresholds (b2 - b1 < 0.35). These are two views of the same problem: test cases within a question cluster at one difficulty level rather than spanning a range.

For each question, using the transitive reduction from Step 2:

1. **Keep** the minimal non-redundant test case chain (the items that add genuinely new information).
2. **Replace** redundant test cases with cases at deliberately different difficulty levels:
  - At least one **warm-up case** that tests the simplest possible input (single-element list, trivial arithmetic, basic happy path). This directly addresses low-ability blindness — students who handle the basic case get credit.
  - At least one **stretch case** that tests a non-obvious edge (empty input, negative numbers, very large input, boundary conditions).
3. **Target**: b2 - b1 > 0.5 for redesigned questions, meaning the "some tests passed" and "all tests passed" categories reflect a genuine ability difference.

High-priority targets:

- The 15 cliff-like questions flagged by Step 6 (high discrimination + bimodal shape).
- Questions with dependency-graph edge density = 1.0 from Step 2 (every test case equivalent).
- High-thrasher questions from Step 5: "Pattern printing — Centered Triangle Of Zeroes" (12.59% thrasher), "Reversed Squares of List Elements" (7.08%), "Pangram Check" (6.96%).

**7d. Add easy warm-up questions for low-ability measurement.**

33/35 namespaces provide roughly 6x less measurement information in the low-ability region than in the middle. The exam cannot distinguish among weak students — it lumps them all at zero. Given the progressive-filter term structure (later terms contain weaker students), this is a measurement-design mismatch: the instrument is least precise where diagnostic resolution is most needed.

Add 1–2 genuinely easy questions per exam that most students can at least partially solve. These contribute almost no information about strong students (who pass them trivially) but discriminate among weak students. They also serve a pedagogical function: a successful starting experience may reduce the "skeleton-only" (6.14%) and "stuck and abandoned" (3.47%) archetypes.

**7e. Implement layered scoring.**

Replace all-or-nothing scoring with:

| Layer                | What It Measures             | How to Score                                                                            | Weight |
| -------------------- | ---------------------------- | --------------------------------------------------------------------------------------- | ------ |
| **Attempt**          | Meaningful engagement?       | Code structurally differs from skeleton (tree-sitter comparison) by ≥N added constructs | 5–10%  |
| **Runnability**      | Valid Python that executes?  | ast.parse() succeeds AND code runs without crash on minimal input                       | 10–15% |
| **Core correctness** | Handles the main case?       | Passes designated "core" test cases (the warm-up cases from 7c)                         | 35–45% |
| **Edge robustness**  | Handles boundary conditions? | Passes remaining test cases                                                             | 25–35% |

**Caveat**: Layered scoring is only effective for questions where the test cases span a genuine difficulty range. For the 47.35% of questions with narrow b2 - b1 thresholds, layered scoring collapses back to near-binary until the test cases are redesigned (7c). Simulate layered scoring against historical data and report separately for questions with wide vs. narrow threshold gaps.

**7f. Audit problem statement clarity.**

For questions with the highest "wrong output — logic" rates (from Step 3) and the highest thrasher rates (from Step 5):

- Review problem statements for ambiguity.
- Cross-reference with tree-sitter structural analysis: if students build correct structure (right loops, right data structures) but produce wrong output, the gap may be in problem interpretation, not concept understanding.
- Concretely: "How many distinct incorrect interpretations could a careful student reasonably make?" If more than one, rewrite.

Specific targets: the high-thrash questions named in 7c.

**7g. Investigate variant equivalence.**

Step 6 found some variant pairs with material θ differences after linking (e.g., ns\_25t1\_py22\_1 vs \_2: +0.653). For variant pairs with large differences:

- Review whether question content is truly equivalent in difficulty.
- Check whether student assignment to variants is random or cohort-based. If cohort-based, the difference may reflect the population, not the instrument.
- If instrument differences are confirmed, adjust future variant design for better equivalence.

**7h. Improve runtime error feedback.**

50% of runtime error rows in the data are "Runtime Error (unspecified)" because the platform provides generic error summaries. This limits both student learning (they can't see what went wrong) and analytical precision (future analyses can't classify runtime error types).

Ensure the exam platform exposes the specific Python exception type and traceback to students and in logged data. This is both a pedagogical improvement and a data quality improvement.

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# Step 7: Evaluation Redesign"

## Step 8: Longitudinal Analysis

The term structure is a progressive filter: Term 2 students failed Term 1, Term 3 students failed Term 2\. Students who pass leave the system. This means cross-term aggregate comparisons are misleading (later terms have weaker populations by construction), but individual-level paired comparisons are deeply informative.

Step 6 found no shared anchor items between Wave 1 and Wave 2, so IRT-linked growth analysis is not feasible. This step uses alternative approaches.

**8a. Within-term growth (Wave 1 → Wave 2) — alternative approaches.**

For students who took both waves (\~4,290 in 25t1, \~2,933 in 25t2, \~2,682 in 25t3), the \~35-day gap between waves is the only clean same-population comparison:

1. **Rank-based comparison.** For students in both waves, compute their rank within their wave's score distribution. Compare Wave 1 rank to Wave 2 rank. Students who improve in relative rank are learning.
2. **Category-based comparison.** Using the GRM categories (0 = no tests passed, 1 = some, 2 = all), compute the fraction of students who improve, stay the same, or decline from Wave 1 to Wave 2\. Weight by question count (students attempt \~7 questions per wave). This is coarse but robust.
3. **Archetype shift analysis.** For students in both waves, compare their primary archetype in Wave 1 vs. Wave 2:
  - Do "thrashers" in Wave 1 become "steady builders" or "incremental debuggers" in Wave 2?
  - Do "skeleton-only" students in Wave 1 show any engagement improvement in Wave 2?
  - Do "regression" students in Wave 1 learn to maintain working code in Wave 2?
4. **State-transition improvement.** Compare the student's dominant state in Wave 1 (what state they spent the most test\_runs in) to their dominant state in Wave 2\. A shift from dominant-S2 to dominant-S3 or S4 is progress even if the final score doesn't change much.

**8b. Cross-term analysis for repeat students (paired comparisons).**

For the 2,010 students in t1∩t2 and 1,367 in t2∩t3 (students who failed the earlier term and are retaking):

1. **Error profile matching.** Compare each student's error taxonomy (from Step 3) in Term N to Term N+1:
  - If they failed on runtime errors (TypeError, NameError) in t1, do the same error types appear in t2?
  - If they were syntax-gated in t1, are they still syntax-gated in t2? Or have they shifted to a different failure mode (logic error, edge case)?
  - Shifting from syntax failure to logic failure is _progress_ — even if the score is still low.
2. **Archetype stability.** Same as 8a.3 but across terms. Does the \~35-day inter-term gap (plus additional instruction) change student process behaviour?
3. **Tree-sitter structural progression.** Compare the structural inventory of each student's code across terms:
  - In t1, did they ever use for-loops? In t2, do they use for-loops more consistently?
  - In t1, did they ever use functions? In t2, are they decomposing problems into functions?
  - Use tree-sitter construct timeline data from Step 5.
4. **S2 escape rate.** For students who were predominantly in S2 (parseable, zero tests) in Term N, what fraction escape to S3 or S4 in Term N+1? This directly measures whether inter-term remediation is addressing the largest bottleneck.

**8c. The 503 all-three-terms students.**

Dedicated analysis of the persistently struggling population:

1. **Three-term error trajectory.** Plot each student's primary error category across t1 → t2 → t3\. Common patterns to look for:
  - **Persistent S2**: Valid code, wrong output, all three terms. These students understand Python syntax but not algorithmic thinking.
  - **Persistent syntax**: Can't write parseable code even after three attempts. Need fundamentally different instruction.
  - **Cycling**: Syntax failure in t1, runtime error in t2, wrong output in t3\. This is progress even though they haven't passed.
2. **Archetype trajectory.** Three-term archetype sequence. Are they always "skeleton-only"? Always "thrasher"? Or do their process patterns shift?
3. **What distinguishes eventual passers.** Among the 503, do any pass in t3? If so, what changed — in their error profile, archetype, structural complexity, or state transitions? These success stories should inform intervention design.

**8d. "Pass-through" analysis.**

Model the probability of passing (and exiting the system) as a function of:

- Wave 1 → Wave 2 improvement (from 8a)
- Primary archetype (from Step 5)
- Primary error category (from Step 3)
- Number of questions with any test pass

This identifies which student characteristics at the start of a term predict successful exit. The complement identifies who will persist to the next term — and these are the students targeted interventions should focus on.

**8e. Recommend anchor design for future terms.**

Since no wave-pair linking currently exists, recommend that future exam design include 2–3 deliberate anchor questions shared between Wave 1 and Wave 2 of the same term. These should be:

- Moderate difficulty (not ceiling or floor)
- From the questions with the best GRM discrimination parameters (Step 6)
- Identical in content and test cases across waves

This is a low-cost design change that enables proper IRT-linked growth analysis in future terms.

**What This Tells You**: Without IRT-linked growth curves, you can still answer the core longitudinal questions through archetype shifts, error profile changes, state-transition improvements, and structural progression. The picture is less statistically precise but potentially more pedagogically informative — you see _what changed in how students work_, not just whether a latent score moved.

**Action point**: If archetype and error profiles are stable across terms for the 503 students, current inter-term remediation is not working for this group. The specific stable patterns (persistent S2, persistent thrasher, persistent skeleton-only) identify what kind of alternative intervention to try.

**Action point**: Include anchor questions in future exam design (8e). This is a low-cost change that unlocks proper growth analysis.

## Step 9: Concept Dependency and Knowledge Modelling

**9a. Build a concept-question map.**

Using the question cues from the OPPE guide, tag each of the 251 questions with primary concepts:

| Concept                           | Example Question Cues                                                        |
| --------------------------------- | ---------------------------------------------------------------------------- |
| Arithmetic / conditionals         | "Check is even or divisible by 5," "Describe Number Based on Divisibility"   |
| String manipulation               | "Deinterleave Even and Odd Indices in String," "Create Slug from String"     |
| List / tuple operations           | "Middle element from list," "Extract Border Elements," "Rotate Even Indices" |
| Dictionary operations             | "Merge two dictionaries and sum on conflicts"                                |
| Loops and iteration               | "Counts unique even and odd numbers," "Running Average Skipping NaN"         |
| Pattern printing                  | "W Pattern," "Z Pattern," "Diamond," "Hexagon"                               |
| Input parsing / output formatting | "Markdown Image to HTML Image," "Format Tic-Tac-Toe Board"                   |
| Data analysis / aggregation       | "Student Score Filter," "Employee Task Analysis"                             |
| File operations                   | "Column Totals in a Markdown Table," "File Content Zig-Zag Shift"            |
| Mathematical / algorithmic        | "Check if a Triangle is Obtuse," "Compute Polynomial Value"                  |

Many questions will map to 2–3 concepts. Tag all relevant ones.

**9b. Concept-level mastery rates.**

For each concept, aggregate pass rates across all questions tagged with that concept. Use public-best outcomes for the full population (consistent with Step 6's GRM basis).

Break down by term — noting that cross-term declines reflect weaker populations (progressive filter), not curriculum failure. Within-term Wave 1 → Wave 2 comparisons on concept-level mastery are cleaner.

**9c. Tree-sitter construct usage vs. mastery.**

This is directly computable from existing Step 3 and Step 5 outputs (`structural_inventory_by_question.csv`, `construct_first_appearance_summary_global.csv`).

Build the usage-vs-mastery table:

| Concept             | Relevant Construct(s)                   | Usage Rate (ever used in attempt) | Mastery Rate (among users) | Gap Type |
| ------------------- | --------------------------------------- | --------------------------------- | -------------------------- | -------- |
| Loops               | for\_loop (46.71%), while\_loop (5.13%) | ?                                 | ?                          | ?        |
| List comprehensions | list\_comp (4.53%)                      | ?                                 | ?                          | ?        |
| Dictionaries        | dict\_comp (0.41%)                      | ?                                 | ?                          | ?        |
| Error handling      | try\_stmt (1.45%)                       | ?                                 | ?                          | ?        |

For each concept, classify the gap:

- **Low usage, high mastery when used** → Students don't know _when_ to deploy this construct. Teach pattern recognition (more examples of when to use it, not more drill on how).
- **High usage, low mastery** → Students know when but not how. More practice and worked examples needed.
- **Low usage, low mastery** → Construct hasn't been absorbed at all. Curriculum coverage issue.

**9d. Concept prerequisite graph.**

For each pair of concepts (A, B):

- P(masters B | masters A) — does knowing A predict knowing B?
- P(masters B | fails A) — can they know B without A?

If P(masters B | masters A) >> P(masters B | fails A), A is empirically a prerequisite for B. Build a directed graph.

Compare against the curriculum's teaching order. Misalignments — concepts taught before their empirical prerequisites — are high-priority curriculum findings.

**9e. Per-student concept profiles for repeat students.**

For the \~2,010 students in t1∩t2 and \~1,367 in t2∩t3, build paired concept mastery profiles:

- Term N: mastered concepts A, C, D; failed B, E
- Term N+1: mastered concepts A, B, C, D; failed E, F

This shows individual learning trajectories at the concept level and feeds directly into Step 8's cross-term paired comparisons. If students consistently master new concepts between terms while retaining previously mastered ones, the remediation is working. If they cycle (master B but regress on C), something is wrong.

**9f. Concept-level decomposition of the S2 bottleneck.**

The S2 state (parseable, zero tests) is the largest stuck population. For students in this state on their final attempt:

- Which concepts does the question require? (From the concept-question map.)
- Does the student's code show the relevant constructs? (From tree-sitter parse.)
- If the construct is present but the output is wrong, the failure is in _application_ of the concept.
- If the construct is absent, the failure may be in _concept selection_ (student doesn't know which tool to use).

This produces a concept-level decomposition: "40% of S2 failures on dictionary questions involve students who never use a dictionary" vs. "60% use a dictionary but use it incorrectly." Each demands a different teaching approach.

**What This Tells You**: The construct-usage-vs-mastery analysis distinguishes "don't know when" from "don't know how," which demand different teaching approaches. The S2 concept decomposition connects the process finding (students stuck in S2) to the curriculum (which concepts they're stuck on and in what way). The prerequisite graph tells you whether the curriculum teaches things in the right order.

**Action point**: For concepts where usage is low, the teaching intervention is _exposure and pattern recognition_ (more examples showing when to use the construct). For concepts where usage is high but mastery is low, the intervention is _practice and feedback_ (more exercises with detailed solutions).

**Action point**: Realign curriculum sequence to match the empirical prerequisite graph where they diverge.

---

For the above analyses

- Add scripts to analysis/ which will generate outputs in analysis/ and run them.
- Document your process (including how to re-build the outputs) and your findings (manually, not using a script) as a NEW section in analysis/README.md called "# Step 9: Concept Dependency and Knowledge Modelling".

## Review and correct

Go through all the analysis so far and check for any errors, inconsistencies, gaps, and obvious improvements - aligning with my intent.
Apply these changes the scripts, re-run where required, and update the documentation.
When updating the documentation, don't mention these are updates. Instead, write it as if you're writing for the first time with the benefit of hindsight and the improved analysis.

Add to .gitignore the minimal patterns required to ignore generated files. Stage changes.

# Step 5a: Resolve the other archetypes

Step 5 classified 52.64% of attempts into no named archetype. Before presenting archetype-based findings to stakeholders, this needs resolution.

**Option A: Refine archetype rules.** The current rules are strict. Examine the feature distributions of "Other" attempts:

- What fraction are "near-steady-builder" (mostly monotonic improvement, but with one or two dips)?
- What fraction are "moderate effort, moderate outcome" (median test\_run count, some test passes, no strong pattern)?
- What fraction are "late regression" (good progress until the last few runs, then a decline)?

Relax the thresholds or add 2–3 new named archetypes to cover the most common "Other" patterns.

**Option B: Clustering.** Run k-means or DBSCAN on the process features for "Other" attempts. Name emerging clusters based on their feature profiles.

Goal: reduce "Other" below 10% so the archetype distribution tells a complete story.

Rewrite Section 5 to present the final archetype set and their characteristics,.
When updating the documentation, don't mention these are updates. Instead, write it as if you're writing for the first time with the benefit of hindsight and the improved analysis.

## Recheck

Go through all the analysis so far - especially the corrections due to Step 5a - and check for any errors, inconsistencies, gaps, and obvious improvements - aligning with my intent.
Apply these changes the scripts, re-run where required, and update the documentation.
When updating the documentation, don't mention these are updates. Instead, write it as if you're writing for the first time with the benefit of hindsight and the improved analysis.

Add to .gitignore the minimal patterns required to ignore generated files. Stage changes.

# Step 10: The Stakeholder Report

**What Steps 5–9 Added That Reshapes the Synthesis**

The archetype story is now complete and more nuanced

"Other" dropped from 52.64% to 6.40%. The two largest new archetypes fundamentally change the narrative:

| Archetype             | % of Attempts | Success Rate | What It Means                                                                                                                                                      |
| --------------------- | ------------: | -----------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Minimal-change solver |        18.54% |       77.27% | Quietly successful; few runs, short time, little visible process. Previously invisible inside "Other."                                                             |
| Volatile reworker     |        17.75% |       35.95% | Repeatedly restructures code with fluctuating errors. High effort (median 3,223s, 18 public runs), mediocre outcomes. Distinct from and much larger than Thrasher. |
| Steady builder        |        15.95% |       89.04% | The ideal process archetype.                                                                                                                                       |
| Builder with setbacks |         8.29% |       41.76% | Near-steady-builder but with dips. The dominant "middle ground" archetype for repeaters.                                                                           |
| Incremental debugger  |         7.66% |       77.65% | Small targeted changes, good debugging.                                                                                                                            |
| Regression            |         7.66% |        5.65% | Had working code, broke it.                                                                                                                                        |
| Skeleton-only         |         6.14% |        0.48% | Didn't meaningfully attempt.                                                                                                                                       |
| One-shot              |         5.02% |        9.44% | ≤3 runs.                                                                                                                                                           |
| Stuck and abandoned   |         2.77% |        4.11% | Gave up after idle gap.                                                                                                                                            |
| Thrasher              |         1.81% |       43.59% | High-run-count oscillation.                                                                                                                                        |
| Flat stuck            |         1.67% |        0.12% | Minimal change, persistent syntax errors. Near-zero success.                                                                                                       |
| Late starter          |         0.35% |       25.66% | Delayed start.                                                                                                                                                     |

**Critical nuance for the report**: Thrasher is a _question-level_ phenomenon (some questions induce 7–13% thrashing rates), not a stable student-level identity. At the student-wave and student-term level, Thrasher essentially never appears as a dominant archetype. Present thrashing as a question-design signal, not a student-type label.

**The longitudinal picture is more positive than expected — with one stark exception**

**Good news**: Substantial learning is happening.

- 58–69% of students improve Wave 1 → Wave 2 (category-based).
- 81% of t1→t2 repeaters improve; 77% of t2→t3 repeaters improve.
- 53% of syntax-gated repeaters move to pass-like error profiles by the next term.
- 67% of repeaters master at least one new concept between terms.
- Structural progression is visible: more loops and conditionals, less print-heavy trial code.

**Stark exception**: Dominant-S2 escape is **zero**. Students whose entire wave or term is dominated by S2 (parseable code, zero tests passing) never shift to dominant S3/S4 — not within terms, not across terms. This is a small group (50–110 per term pairing), but it has a 0% conversion rate. Current remediation does not reach them.

**The 497 all-three-term students are NOT an S2 problem**

This is the most important reframing. The persistent cohort's dominant-state trajectories are overwhelmingly **syntax/no-code**, not S2:

- Top trajectory: S1 → S1 → S1 (fundamental syntax, all three terms): 181 students
- S0 → S1 → S1: 69 students
- Only 3 students have trajectories starting with dominant S2

This means the intervention for the hardest-to-help students is different from the S2 intervention. The 497 need foundational Python instruction (syntax, program structure), not debugging support.

**Concept findings add actionable specificity**

Hardest concepts (persistently, across terms):

- Data analysis / aggregation: 21% pass rate, acquisition rate among repeaters only 3–9%
- Pattern printing: 30% pass rate, acquisition rate <8%
- Input parsing / output formatting: 30% pass rate

The S2 concept decomposition shows that for most concepts, S2 failures already include the relevant construct (an application/debugging gap), except for dictionaries and file operations where construct proxies are weak. This means S2 students mostly know _what_ to use but can't make it _work_ — reinforcing the debugging-support intervention.

---

**What to Produce**

**10a. The Stakeholder Report**

Structure the report in six parts. Each part leads with findings, ends with specific actions, and cites the step that produced the evidence. The report should be readable by someone who has not seen the analytical steps — it tells the story, not the methodology.

**Part A: How Students Are Performing**

Lead with the gating waterfall. This is the centrepiece visual and the single most important output of the entire analysis.

| Gate                                          | % of All Student-Question Attempts |
| --------------------------------------------- | ---------------------------------: |
| Full pass                                     |                             46.83% |
| Genuine logic failure                         |                             26.72% |
| Edge-case gated (passes core, fails edge)     |                              7.35% |
| Syntax gated — mechanical (structure evident) |                              7.14% |
| Unmodified skeleton / didn't attempt          |                              6.14% |
| Partial pass                                  |                              3.21% |
| Syntax gated — fundamental (no structure)     |                              2.36% |
| Formatting gated                              |                              0.25% |

Key messages:

- Nearly half of all attempts succeed. The exam is passable.
- **Logic failure, not syntax, is the dominant failure mode.** This directly addresses the original hypothesis ("too focused on syntax vs. conceptual understanding"). The data says: syntax gates \~9.5%, but logic failure is 26.72%. The bigger problem is students who can write valid Python but can't solve the problem.
- 7.35% fail only on edge cases — these students understand the core problem and are "almost there."
- Regression is common: 45% of students who end with broken code had working code earlier. This is a process failure (can't maintain code while editing), not a knowledge failure.
- The formatting tax is negligible (0.25%). The evaluation handles output format differences well.

Include the non-submission context: 71.72% non-submission overall, but 89.79% of this is a data capture issue (23/35 namespaces have no submission events). In namespaces where submissions work, genuine non-submission is small and these students are stuck (62% runtime errors on best run).

**Part B: How Students Work**

Lead with the archetype distribution (now complete, only 6.4% unclassified).

Key messages:

- **The largest group is "minimal-change solvers" (18.54%)** — students who succeed quickly and quietly with few runs. Combined with steady builders (16%) and incremental debuggers (8%), roughly 42% of attempts show efficient, successful process.
- **"Volatile reworkers" (17.75%)** are the second-largest group and have mediocre outcomes (36% success). They restructure repeatedly with fluctuating errors. This is different from thrashing — it's a broader instability pattern affecting nearly 1 in 5 attempts.
- **Better process beats more effort.** Thrashers spend 2.2× the time of incremental debuggers for worse outcomes (43% vs 77% success). Volatile reworkers spend even more time (median 3,223s vs 2,153s for incremental debuggers) for even worse outcomes (36%).
- **Thrashing is a question-level signal, not a student identity.** Certain questions induce high thrashing rates ("Centered Triangle Of Zeroes" at 13%, "Pangram Check" at 7%). At the student level, Thrasher essentially never appears as a dominant archetype. This means thrashing is a question-design problem that can be fixed by redesigning specific questions.
- **The genuinely stuck population fails early and quietly.** Non-submitters in submission-positive namespaces show high regression (\~20%), almost no incremental debugging (\~0.3%), and are dominated by abandonment. They don't thrash — they give up.

The death spiral:

- S2 (parseable, zero tests) has a 79% self-loop probability. This is the dominant stuck state.
- S2 accounts for 47.1% of all public test-run states.
- Recovery from syntax errors with structural intent is materially faster (50% within 1 run) than without (44%).
- Wrong Answer errors persist to the final run 39% of the time — the hardest error type to recover from.

**Part C: How Well the Evaluation Works**

Key messages:

- **Test cases are heavily redundant.** 34.46% of within-question item pairs are near-identical (phi > 0.90). Cronbach's alpha exceeds 0.97\. The exam is internally consistent but wastes much of its test-case capacity measuring the same thing.
- **Nearly half the questions have ineffective partial credit.** 47.35% of questions have GRM thresholds (b2 - b1) below 0.35, meaning the "some tests" and "all tests" categories represent nearly the same difficulty. Partial credit adds almost no information for these questions.
- **The exam can't distinguish among weak students.** 33/35 namespaces provide \~6× less measurement information in the low-ability region than in the middle. Given that later terms contain progressively weaker students, the exam is least precise where diagnosis is most needed.
- **15 cliff-like questions** create threshold effects without meaningful gradation.
- **Some variant pairs are inequivalent.** Linked-θ differences reach 0.653 between \_1 and \_2 variants. These pairs should not be treated as interchangeable.
- **No public-test overfitting** (0.02%) and **negligible formatting tax** (0.25%). These are non-issues.
- **Public-best categories overstate mastery for \~14% of submitters** (public category higher than private). The GRM uses public-best for calibration consistency, but absolute mastery claims should carry this caveat.

**Part D: What Students Don't Understand**

Key messages:

- **The hardest concept cluster is data analysis/aggregation** (21% pass rate), followed by input parsing/output formatting (30%), pattern printing (30%), and file operations (31%). These are persistently difficult across terms.
- **Core concepts show reasonable mastery**: arithmetic/conditionals (60%), list/tuple operations (52%), string manipulation (52%).
- **The "usage vs. mastery" distinction matters for teaching**:
  - Loops: high usage (49%), low mastery (46% pass among users) → students know _when_ to use loops but struggle with execution. **Intervention: more practice and worked examples.**
  - List/dict comprehensions, try/except: low usage (<5%), low mastery → students haven't absorbed these constructs. **Intervention: more exposure and pattern recognition (when to use it, not just how).**
- **Most S2 failures already include the relevant construct.** For loops (65%), pattern printing (94%), and data analysis (67%), students in the S2 bottleneck are using the right tool but can't make it produce correct output. This is an application/debugging gap, not a concept-selection gap. The exception is dictionaries and file operations, where construct proxies are weak so the signal is less clear.
- **Repeat students do learn new concepts**: 67% master at least one new concept between terms. But acquisition rates for data analysis (<10%) and pattern printing (<8%) are very low — these concepts resist current remediation.
- **The empirical prerequisite graph suggests curriculum review**, but the current proxy ordering is too coarse for direct sequencing changes. A comparison against the actual syllabus sequence is needed.

**Part E: The Longitudinal Picture**

Key messages:

- **Strong within-term learning.** 58–69% of students improve from Wave 1 to Wave 2 across terms. Mean category improvement is +0.21 to +0.38\. This is the clearest evidence that the course produces learning within a term.
- **Strong cross-term learning for repeaters.** 81% of t1→t2 repeaters and 77% of t2→t3 repeaters improve. 53% of syntax-gated students move to pass-like error profiles by the next term. Structural progression is visible: more loops and conditionals, less print-heavy trial code.
- **"Builder with setbacks" is the dominant repeater archetype.** It appears somewhere in the trajectory for 404/497 all-three-term students. This is not a failure archetype — it's a "making progress with difficulty" pattern. The repeater population is working hard and mostly improving, even if they haven't passed yet.
- **But dominant-S2 students never escape — 0% conversion rate.** Students whose entire wave is dominated by parseable-but-failing code never shift to passing states. This is the one population that current instruction completely fails to move. It's small (50–110 per term pairing) but absolute.
- **The 497 all-three-term students are a syntax/no-code problem, not an S2 problem.** 181 of them show S1→S1→S1 (fundamental syntax failure, all three terms). Only 3 start with dominant S2\. These students need foundational Python instruction, not debugging support.
- **But even persistent students show progress in error profiles.** Many trajectories end in pass-like categories: "Syntax gated → Submitted zero → Public full pass" (23 students), "Runtime error → Submitted zero → Full pass" (17 students). Some are getting there — slowly.
- **The pass-through model identifies who will persist** (AUC 0.92). Risk segmentation is well-calibrated and can target pre-term interventions at students most likely to remain in the system.

**Part F: Recommended Actions**

Present as a prioritised table. Each action traces to specific evidence.

| Priority | Action                                                                                                  | Evidence                                                                                                                                        | Impact                             | Effort       |
| -------: | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------ |
|        1 | **Fix submission capture pipeline**                                                                     | Step 1: 23/35 namespaces have zero submission events; 48.76% of Track B students passed all public tests                                        | Critical (operational)             | Low–Moderate |
|        2 | **Address the S2 bottleneck: structured test feedback + progressive problem design**                    | Steps 4, 5: 26.72% logic failure; 79% S2 self-loop; 0% dominant-S2 escape; S2 failures mostly have relevant constructs but can't make them work | Very High                          | Moderate     |
|        3 | **Redesign test cases for difficulty spread** (reduce redundancy + widen b2-b1 thresholds)              | Steps 2, 6: 34.46% near-redundant pairs; 47.35% narrow thresholds; 15 cliff-like questions                                                      | Very High                          | Moderate     |
|        4 | **Add easy warm-up questions** for low-ability measurement and early success experience                 | Step 6: 33/35 namespaces low-ability blind (6× less information at low ability)                                                                 | High                               | Low          |
|        5 | **Pilot layered scoring** (effective after test-case redesign for \~half the questions)                 | Steps 3, 4, 6: waterfall decomposition; narrow thresholds limit current effectiveness                                                           | High                               | Moderate     |
|        6 | **Teach debugging process explicitly** using incremental-debugger exemplar trajectories                 | Step 5: thrashers 2.2× time for worse outcomes; volatile reworkers 17.75% of attempts at 36% success                                            | High                               | Moderate     |
|        7 | **Redesign high-thrash questions** ("Centered Triangle Of Zeroes," "Pangram Check," "Reversed Squares") | Step 5: thrashing is question-level, not student-level; specific questions induce 7–13% thrashing                                               | High                               | Low          |
|        8 | **Improve runtime error specificity in platform**                                                       | Step 3: 50% of runtime errors are "unspecified"; limits both student learning and analytical precision                                          | High                               | Low          |
|        9 | **Target "data analysis/aggregation" and "pattern printing" for curriculum improvement**                | Step 9: 21% and 30% pass rates; <10% acquisition among repeaters; persistently hardest concepts                                                 | High                               | Moderate     |
|       10 | **Investigate and fix variant inequivalence** (starting with 25t2 py21 and 25t1 py22 pairs)             | Step 6: up to 0.653 linked-θ difference between variants                                                                                        | Moderate                           | Low          |
|       11 | **Add syntax linter / feedback for mechanical syntax errors**                                           | Step 4: 7.14% mechanical syntax gate; Step 5: S1b more recoverable than S1                                                                      | Moderate                           | Low–Moderate |
|       12 | **Audit problem statement clarity** for high-thrash + high wrong-output-logic questions                 | Steps 3, 5, 7: named question targets                                                                                                           | Moderate                           | Low          |
|       13 | **Include 2–3 anchor questions across waves** for future IRT growth measurement                         | Steps 6, 8: no wave-pair linking currently possible; 46 candidate anchors identified                                                            | Moderate (enables future analysis) | Low          |
|       14 | **Design foundational Python intervention for the 497 persistent cohort**                               | Step 8: dominant trajectories are syntax/no-code (S1→S1→S1), not S2; current remediation doesn't reach them                                     | High                               | High         |
|       15 | **Deploy pass-through risk model** to identify students likely to persist, pre-term                     | Step 8: AUC 0.92, well-calibrated risk deciles                                                                                                  | High                               | Moderate     |
|       16 | **Realign curriculum to empirical prerequisite graph** (after syllabus comparison)                      | Step 9: 24 candidate edges, 20 misaligned with proxy order; needs real syllabus validation                                                      | High                               | High         |
|       17 | **Build per-student diagnostic dashboard** (θ + concept profiles + archetype + risk score)              | Steps 5, 6, 8, 9                                                                                                                                | High                               | High         |

**10b. Visualisations to Produce**

The report needs specific visuals. These are the ones that carry the most information per pixel:

1. **The gating waterfall** (Step 4). Stacked bar or waterfall chart. This is the centrepiece. Show Track A and Track B side by side, plus combined. Include the tree-sitter mechanical/fundamental syntax split.
2. **Archetype distribution and outcomes** (Step 5). Two-panel chart: left panel shows archetype prevalence (horizontal bar), right panel shows success rate per archetype. Annotate with median active time to make the "effort vs. outcome" point visible.
3. **The S2 self-loop and state-transition diagram** (Step 5). Sankey or state-transition diagram showing self-loop probabilities and escape rates. Highlight the S2→S2 (79%) and S2→S3 (7%) transitions. Annotate S0 as the absorbing state (<5% success).
4. **Test information function overlay** (Step 6). Show TIF curves for a few representative namespaces on the same θ axis. Shade the low-ability region to make the "blind spot" visually obvious. Mark where later-term student θ distributions cluster.
5. **Concept mastery heatmap** (Step 9). Rows = concepts, columns = terms. Colour by pass rate. This makes the "data analysis/aggregation is persistently hardest" finding immediately visible.
6. **Within-term improvement distribution** (Step 8). Histogram of per-student category deltas (Wave 1 → Wave 2) for each term. Show that the distribution is clearly right-shifted (most students improve).
7. **Cross-term error profile shift** (Step 8). Alluvial/Sankey diagram showing how students' dominant error profiles change from one term to the next. The "syntax → pass-like" flow should be visually prominent.
8. **The 497 persistent cohort trajectory** (Step 8). Small-multiples or heatmap showing the top 10–15 three-term dominant-state trajectories. The dominance of S1→S1→S1 should be visually unmissable.
9. **Concept usage vs. mastery scatter** (Step 9). Plot each concept-construct pair with usage rate on x-axis, mastery rate on y-axis. Quadrant labels: "Don't know when" (low usage, high mastery), "Don't know how" (high usage, low mastery), "Not absorbed" (low both), "Mastered" (high both).
10. **Redundancy and threshold scatter** (Steps 2, 6). Plot each question with mean pairwise phi on x-axis and b2-b1 threshold gap on y-axis. Quadrant labels identify which questions need test-case redesign (high redundancy, narrow threshold) vs. which are already well-designed.

**10c. Data Tables to Produce for Operational Follow-Up**

Beyond the narrative report, produce actionable tables that exam designers can use directly:

1. **Question redesign priority list**: Join Step 2 redundancy data, Step 5 thrasher rates, Step 6 cliff-like flags, and Step 7 redesign targets into a single ranked table. One row per question, columns for each signal, sorted by combined priority score. This is the "to-do list" for question authors.
2. **Anchor question candidates for future waves**: The 46 candidates from Step 8, with their GRM parameters and discrimination values. Ready for exam designers to select from.
3. **Per-student risk scores for the next cohort**: If student IDs from the current term are available, export the pass-through model's predicted persistence probability per student. This enables pre-term outreach.
4. **Concept-question cross-reference**: The full 251-question concept map with mastery rates, so curriculum designers can see which questions instantiate which concepts and how well students handle each.
5. **Namespace submission-capture audit**: The Step 7 submission-capture tables, formatted for the engineering/platform team to diagnose the instrumentation issue.

**10d. Caveats Section**

The report must include an explicit caveats section covering:

1. **Track A/B asymmetry**: Track A uses private test results; Track B uses public test_run outcomes only. 14.27% of Track A submitters have public categories higher than private. Absolute mastery levels from public-best data should be interpreted as upper bounds.
2. **Progressive-filter confound**: Cross-term comparisons reflect both learning and population selection. Later terms contain weaker students by construction. Only within-term wave comparisons and individual-level paired analyses are clean.
3. **Timeline sampling**: The timeline contains only test_run and submission events, not saved-code checkpoints. Process metrics are run-sampled, not edit-sampled. "Time to first parseable code" and construct appearance times are measured at run checkpoints, not at the moment of typing.
4. **Construct proxy limitations**: Tree-sitter construct tracking does not cover dictionary literals/indexing, `open()` calls, or string methods. The "selection gap" for dictionaries and file operations is likely overstated by the narrow `dict_comp` and `import_*` proxies.
5. **Concept tagging is heuristic**: Tags are derived from question cues via keyword rules, not expert hand-labelling. Coverage is complete but precision is approximate. The prerequisite graph uses a proxy concept order, not the actual syllabus.
6. **No wave-pair IRT linking**: Growth analysis uses category-based and rank-based methods, not θ-linked curves. This is robust but less precise.
7. **LLM analyses not yet run**: The LLM syntax correction and wrong-output classification steps were deferred (no API key). The "genuine logic failure" bucket (26.72%) could be further decomposed with LLM classification; the syntax recovery estimate is a lower bound (rule-based only).

---

Generate this report in analysis/REPORT.md.

GUIDELINES:

Link extensively to specific steps and data outputs in the analysis directory for transparency and reproducibility.
Always include individual examples (specific students, specific questions, specific code snippets, etc.) to illustrate key points and avoid abstraction.
IMPORTANT: Write in simple language (ELI15) to be accessible to non-technical stakeholders, even students, and laymen unfamiliar with this exam system.

# Error clusters

Based on analysis/README.md and analysis/REPORT.md, use tree-sitter-python to parse student submissions (just the final submissions that are evaluated) and find out patterns of errors in the code, i.e. for each question, the most common ways in which the student goes wrong at a logic level. Factor in the test cases, but go beyond that, perhaps finding similarities / clustering the ASTs, finding common subtrees, etc. The goal is to identify common error patterns that can be used to provide targeted feedback to students and inform instructional design.

Your task is to create an analysis/ERRORS.md, where, for each question, comprehensively and exhaustively you will list the error patterns in student submissions along with their frequency and impact, sharing specific examples and explanations of why each type of error occurs.

Make sure the error patterns are not broad categories. For every question, dive deep, check for differences in the code of different students, and identify specific patterns of errors that are common across multiple students. For example, instead of just saying "students struggle with loops", identify specific patterns like "students often forget to initialize the loop variable" or "students frequently use the wrong comparison operator in the loop condition".

First create a plan for how to do this, test it out, evaluate if it produces the kind of rich insights we are looking for, and if not, iterate on the approach until it does.

Then apply it for one question, share the result, and get feedback.

## Cluster questions

This is a great start! Make a few changes:

- Cluster questions. Some questions are very similar. Cluster the questions themselves first, if they're nearly semantically identical, and mention each variant by showing the full code base for one question as example, then mentioning how the others are different. Then perform this analysis at a question level.
- Create a separate analysis/ERRORS-*.md for each question cluster. Begin by finding the cluster for the question you just analyzed and move the analysis there (naming the file appropriately) and extending the analysis to the other questions in the cluster.
- Replace analysis/ERRORS.md listing all the question clusters along with their variations and the number of submissions for each question. This will be the "index" of the error analyses and should link to the specific analysis/ERRORS-*.md files for each cluster. (Link to the files even before they're created. This file will serve as the reference to create future files.)
- Ensure that the representative examples are from actual student submissions and mention the student ID (which is already an anonymized hash).

Do this first, share the result and get feedback. Then we can proceed to the next question cluster.

## Reduce residuals and run next 3

In analysis/ERRORS.md, if there are no final_submitters, drop the variant in the table. Otherwise this looks fine.

Revise this question cluster. Analyze more carefully and re-cluster so that residuals are always under 5% - and preferably much smaller than than. The aim is not to have more clusters, but rather, to have fewer clusters than we do, but that they better represent the kinds of errors students make, so that the "Other" category is small enough to be uninformative.

Always begin by showing the variant frequencies in this format for every pattern, even if it occurs in only one question variant. This ensures consistency and comparability.

```markdown
- Cluster frequency: `243/665` (`36.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `129/337` (`38.3%`)
  - `ns_25t2_py21_2/18`: `114/328` (`34.8%`)
```

Redo the current cluster. Then, SYSTEMATICALLY, repeat this process for 3 more clusters - pick the ones with the highest final_submitters.

### Next 3

Proceed with the next three clusters with the highest final_submitters.

### Stage and proceed

Gitignore generated files and stage the code and markdown files for commit.

Then, proceed with with the next three clusters with the highest final_submitters.

### Proceed with the next

Proceed with the next 5 clusters with the highest final_submitters.

---

(This was repeated multiple times)

## Take stock and plan next steps

Update analysis/ERRORS.md to include a short summary (up to ~50 words) that summarizes the key error patterns for each cluster that has been analyzed.

Then summarize (at the top of analysis/ERRORS.md) the overall insights from the error pattern analysis so far. What kinds of mistakes do students commonly make and why? What are underlying patterns? What are the implications for problem and test case design? How should we plan for this in the AI era? (Feel free to search online for reference material.)

Think like an expert: What would an expert in this field check, what patterns would an expert recognize, that beginners would miss?

Write for a lay audience. ELI15.

## Restructure into JSON

Convert the data in `analysis/ERRORS-cluster-*` into a structured `analysis/errors.json` for all the errors analyzed so far.
Think carefully about the best data structure for this JSON to ensure it captures all the relevant information in a way that can be easily queried and visualized.

## Visualize

Using analysis/README.md, prompts.md, analysis/evaluation.json, analysis/* any other available content, write a **Narrative-driven Data Story** that synthesizes the patterns of student errors into a compelling narrative.

The objective is to help the reader understand the nature of errors students make (synthesizing across the different questions), why they make them, and what can be done about it — all through a narrative that is engaging, insightful, and **ACTIONABLE**.

Write like Malcolm Gladwell. Visualize like the NYT graphics team. Think like a detective who must defend findings under scrutiny.

- **Compelling hook**: Start with a human angle, tension, or mystery that draws readers in
- **Story arc**: Build the narrative through discovery, revealing insights progressively
- **Integrated visualizations**: Beautiful, **interactive** charts that are revelatory and advance the story (not decorative)
- **Link for context** wherever possible. For non-HTML content (e.g. code, configurations, images), consider popups with captions (syntax-highlighted for text files). Re-use popup code similar entities for consistency and efficiency. Wherever possible, show examples of actual problem statements, student solutions, test cases, etc. as code as popups. Weave it into the narrative in the few key places where it adds the most value.
- **Concrete examples**: Make abstract patterns tangible through specific cases
- **Evidence woven in**: Data points, statistics, and supporting details flow naturally within the prose
- **"Wait, really?" moments**: Position surprising findings for maximum impact
- **So what?**: Clear implications and actions embedded in the narrative
- **Honest caveats**: Acknowledge limitations without undermining the story

Beauty and aesthetics are key.

Create this as a single errors.html (under analysis/) that loads errors.json and renders the narrative.
