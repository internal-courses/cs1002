# Prompts

<!--

Copy from https://console.cloud.google.com/storage/browser/programming-assignment-prod/analytics_python;tab=objects?authuser=3 into data/

mkdir -p data
cd data
gcloud storage cp -R 'gs://programming-assignment-prod/analytics_python/' .

>

## Understand data (Codex yolo - gpt-5.4 xhigh)

The files in v2-analysis/data/ are parquet files. Analyze them. The structure is similar to the other datasets we have, just organized as parquet files.

Create a v2-analysis/data/README.md that will have all useful information required to analyze the data - structure/schema, values, distributions, outliers, etc. Insighful EDA.

---

Move any files you created outside of v2-analysis/ (e.g. code, Markdown, etc.) into v2-analysis/. I want all output self-contained inside v2-analysis/.

## Analyze data (Codex yolo - gpt-5.4 xhigh)

<!-- https://chatgpt.com/c/69bd0268-7900-839c-9101-e613d0caa017 -->

Our aim is to create a learning support intervention artifact. Here is ChatGPT's recommendation the output to share. You may use your discretion to share more or less, but this is a good starting point. The key is to make it actionable for TAs and faculty, not just clever.

Save your final artifact in v2-analysis/learning-support.md with support analysis and output in v2-analysis/.

```markdown
For learning support, the best output is not “analysis.” It is a **named action list**.

A good intervention artifact answers six things in one row: **who, what pattern, how strong the evidence is, what to do, who owns it, and by when**.

Based on your new export, these are the most useful specific outputs you could share.

## 1) A priority intervention queue for TAs

This is probably the single highest-value output.

Why this matters: in your data, most activity is exploratory test runs, only **18.88% of learner-unit pairs ever submit**, and each learner-unit pair submits **at most once**. So support has to happen **before** submission, not after.

A row-level output could look like this:

- `learner_key`
- `current_units`
- `risk_segment`
- `evidence`
- `recommended_intervention`
- `owner_ta`
- `deadline`

Example row format:

> `K8F... | 772, 775 | False confidence / hidden-test risk | 29 runs, public all-pass achieved twice, best paired private pass-rate 60%, no submission | 15-min boundary-case review + ask student to write 5 hidden-case candidates before next attempt | TA-Meena | within 48 hours`

This queue should segment learners into buckets like:

- **No traction**: many runs, still zero or near-zero progress
- **Thrashing**: attempt count is high but progress is not improving
- **False confidence**: public tests pass, hidden/private tests do not
- **Ready but not submitting**: strong evidence they can finish, but have not converted
- **Silent dropout**: started, then stopped

## 2) A “ready to finish” list

This is the contrarian one. Many analytics efforts obsess over the weakest students. But your data suggests there will also be students who are **close enough to finish** and just need a nudge.

Why this matters: because submission is a one-shot event, a surprisingly high-ROI intervention is often not “teach Python better” but “get them over the line.”

This output should specifically identify learners who:

- achieved strong private `test_run` results at least once
- or reached high public pass-rate repeatedly
- but **still never submitted**

Example shareable line:

> `These 83 learners do not look conceptually blocked. They look operationally stuck. They have either reached hidden-test success or near-success but did not convert to submission. They should get a same-day “submit now / final-check” nudge, not a concept clinic.`

That distinction matters. Otherwise you waste TA time reteaching students who mainly need closure.

## 3) A hidden-test trap watchlist by unit

This is one of the most concrete things you can share with faculty and TAs.

Your own summary already shows strong candidates:

- **57**: public green / hidden fail = **21.30%**
- **55**: **17.47%**
- **772**: **15.25%**
- **147**: **14.95%**
- **775**: **12.00%**

That means some units are creating **false confidence**. Students think they are done because public tests are green, but they are not actually done.

A useful output would say:

> `Do not interpret struggle on Units 57, 55, 772, 147, and 775 as simple lack of practice. These units have unusually high public-green / hidden-fail rates. Support here should focus on edge cases, not repetition.`

This output helps in two ways:

- it improves student support
- it prevents unfair blame on students for unit-design or test-gap effects

## 4) A bug-type roster: runtime vs logic vs pathological output

Your event summaries are dominated by:

- **Runtime Error**: 36.76%
- **Wrong Answer**: 35.75%
- **All Cases Passed**: 27.29%

These are not the same teaching problem.

A very useful intervention output is a roster that groups students by likely failure mode:

- **Runtime-heavy** students need debugging help
- **Wrong-answer-heavy** students need reasoning / edge-case help
- **TLE / huge-output** students need control-flow and print-discipline help

Example TA-facing summary:

> `Group A: Runtime-dominant failures. Run a 30-minute clinic on indexing, uninitialized variables, type conversion, and trace-based debugging.`
> `Group B: Wrong-answer dominant failures. Run a clinic on reading the prompt carefully, testing edge cases, and verifying assumptions.`
> `Group C: TLE / runaway output. Focus on loops, termination, and removing diagnostic prints.`

This is far better than a generic “weak students” list.

## 5) A thrashers report

Your learner-unit behavior is heavy-tailed:

- median rows per learner-unit pair = **7**
- p90 = **21**
- p99 = **54**

That gives you a natural intervention output.

Example definitions:

- **Moderate thrashing**: more than 21 rows on a learner-unit pair and still no submission
- **Severe thrashing**: more than 54 rows and still no submission

A shareable output could look like:

> `These learners are not under-practicing. They are over-attempting without learning transfer. They need intervention that forces reflection between attempts, not more attempts.`

That is important. More practice is not always the cure. Sometimes the student is trapped in local search.

## 6) A dropout / disengagement list

This is the inversion of the thrashers report.

Some students do not thrash. They just try a little and vanish. Those are a different support problem.

This output should flag learners who:

- had some early activity
- showed low progress
- then stopped participating for several days before an exam or checkpoint

Example shareable wording:

> `These learners are not failing noisily. They are failing quietly. They need outreach, not analytics.`

This is the kind of list buddies or mentors can act on quickly.

## 7) A per-student intervention card

This is what I would actually hand to TAs or buddies.

One card per student, one paragraph only. No dashboard.

Example:

> **Learner K91...**
> Active on Units 144 and 145. High persistence: 24 runs on Unit 144. Most recent 8 runs are Runtime Error. Best public pass-rate is still below 20%. No submission yet. This looks like debugging difficulty, not lack of effort. Recommended action: one 20-minute screen-share debugging session. Ask the student to explain the current code line by line and run 3 tiny custom test cases.

Another example:

> **Learner Q73...**
> Unit 772. Public all-pass achieved, but hidden/private pass-rate still low. This looks like missed edge cases. Recommended action: ask the student to list boundary conditions before coding and test against at least 5 self-created cases.

This is the format that actually changes behavior.

## 8) A unit-level teaching note: “what students are getting wrong here”

This needs code decoding and clustering, but it is worth it.

Using `code`, `summary`, and `test_case_results`, you can generate a one-pager for each high-friction unit:

- common bug motifs
- what high-performing students do differently
- TA hints
- student-facing advice

Example:

> **Unit 773 teaching note**
> Common failure pattern: runaway output / diagnostic printing causing large payloads and TLE-like behavior.
> TA advice: ask student to strip prints first, then rerun.
> Student advice: if output is huge, your program may be “working loudly” instead of “working correctly.”

This is much more useful than saying “Unit 773 is hard.”

## 9) A historical “who is likely to respond to help” model

This is where your older batches become powerful.

Do not only predict failure. Predict **responsiveness to intervention**.

That output might say:

> `Among learners with this profile—at least 5 attempts, some partial progress, no submission yet—historically, TA contact within 5 days increased conversion materially.`

Or:

> `Learners with repeated runtime errors and no partial progress after 10 attempts historically respond poorly to text nudges but better to live debugging help.`

This is much closer to Anand’s “teachable students” framing than a generic risk score.

## 10) A post-intervention scorecard

Since Anand explicitly says, “let’s see if our finding helps,” you should plan the output now.

That scorecard should compare:

- contacted vs not contacted
- clinic attendees vs non-attendees
- targeted-risk group vs baseline
- conversion to submission
- eventual pass rate

Without this, the analysis stays clever but unaccountable.

---

## If I were you, I would share these first

If you need the minimum viable intervention pack, I would send just four things:

1. **TA priority queue** with named students and actions
2. **Ready-to-finish list** for quick nudges
3. **Hidden-test trap watchlist by unit**
4. **Bug-type roster**: runtime vs wrong-answer vs pathological-output

That would already make your analysis operational.

## One important caution

Do **not** share a giant leaderboard of “high-risk students.” That creates stigma and vague panic.

Share lists like:

- “students who need debugging help”
- “students who need edge-case coaching”
- “students who are ready to submit”
- “units where public green is misleading”

That reframes the problem from judgment to support.

The deeper blind spot here is this: some of the biggest gains may come not from teaching weaker students more, but from distinguishing **lack of understanding**, **bad exam tactics**, **bad unit design**, and **failure to convert**. Your data is rich enough to separate those. Most institutions do not.

I can turn this into a concrete schema for each output — with columns, thresholds, and sample SQL/Python logic against your parquet layout.
```

<!-- codex resume 019d0a4f-0208-7a42-bf8f-9f7ea1eb5cf1 -->

## Story (Copilot yolo - Claude 4.6 Sonnet high)

Go through v2-analysis/prompts.md to understand what I prompted so far. The results are in v2-analysis/learning-support.md. Feel free to read other content as required. Use sub-agents and do further analysis if/where required.

Create a SIMPLE, prescriptive, actionable v2-analysis/learning-support.html that tells the TAs _specifically_ what to do and in what order.

Include details in popups. For example, explain in segment-wise popups the details of each segment with CLEAR examples - literally show the code, results, recommended action based on 2-3 students in each segment and any other details (priority, learners, ...). This is almost a segment micro-site. Link all segments to these popups. Make sure popups are shareable, bookmarkable, etc. via URL query parameters that don't pollute history (e.g. via pushState, replaceState, ...).

By reading this report, TAs should be able to schedule sessions and know _exactly_ what to teach and have ready examples to show students. This is not a report for data scientists. It is a report for TAs and faculty to take action on. It should be prescriptive, not descriptive. It should be a playbook, not an analysis. It should be a set of named buckets with specific actions, not a dashboard of risk scores.

Make this scannable, i.e. it should be possible to read the whole thing in 5 minutes and get the key actions. The popups can have more details for those who want to dig in, but the main report should be concise and actionable.

IMPORTANT: Because Claude will almost certainly stall when generating such a large file at one shot, you MUST break this into parts, generating a SMALL scaffolding, then layering edits (keeping each chunk small) and saving each time and checking it.

<!-- copilot --resume=49e6b6c9-1aea-4760-905d-94cb3300e6ee -->
