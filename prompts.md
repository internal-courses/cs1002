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

## Step 4: The Syntax Bottleneck — Quantified (Dual-Track)

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
