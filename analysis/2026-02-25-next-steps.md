# Next-Step Analysis Plan (From 2026-02-25 Weekly Review)

## Quick Summary (ELI15)

Think of this as a hospital triage list.
We should first fix measurement issues, then target the biggest learning bottlenecks, then run small pilots before scaling.

Right now, the data says:

- Full pass is about `46.83%`, so the exam is not impossible.
- The main failure is logic (`26.72%`), not just syntax.
- A major loop is “code runs but passes 0 tests” (S2): `47.1%` of public runs, with `78.93%` staying stuck in S2.
- `23/35` namespaces show zero private submissions, so some conclusions are blocked until pipeline capture is verified.
- We can already identify a “teachable-now” segment (`~9.5%`) using process/error patterns, not marks.

So the most impactful next analyses are the ones that:

1. fix data trust issues,
2. reduce avoidable student failure quickly,
3. help staff target limited mentoring capacity better.

---

## How We Prioritized

Each proposed analysis is ranked by:

- **Impact**: How much it can improve student outcomes or decision quality.
- **Feasibility**: How quickly we can run it using data already in this repo.

Scores are on a 1–5 scale.

---

## Priority List (Impact x Feasibility)

| Priority | Proposed analysis | Impact | Feasibility | Why this should be done now |
| --- | --- | ---: | ---: | --- |
| P0 | Submission capture + public→private funnel audit | 5 | 5 | Prevents wrong conclusions from incomplete private-submission logging. |
| P0 | Hardcoding vulnerability map + sentinel test simulation | 5 | 5 | Fastest way to reduce fake “progress” from sample memorization. |
| P0 | S2 “stuck loop” early-warning analysis | 5 | 4 | Targets biggest live bottleneck in student debugging behavior. |
| P0 | Difficulty-mix fairness by namespace/shuffle | 4 | 4 | Checks if students got unfairly hard/easy combinations. |
| P0 | Teachable-now targeting for Python Buddy capacity planning | 4 | 5 | Converts existing analysis into operational intervention lists. |
| P1 | Error-pattern-to-hint mapping (feedback redesign) | 4 | 4 | Gives students actionable hints instead of generic fail signals. |
| P1 | Multi-function scaffold effect analysis (`...` vs `pass`) | 3 | 4 | Small template changes may remove unrelated syntax failures. |
| P1 | “Trying hard vs random/copy-like” process signature analysis | 4 | 3 | Helps separate genuine strugglers from low-effort attempts. |
| P1 | Intervention ROI simulation (who to coach first) | 4 | 3 | Helps use limited mentor time where it matters most. |
| P2 | Weekly-assignment authenticity linkage (when external data arrives) | 5 | 2 | Needed to answer “practice quality vs OPPE outcomes” fully. |

---

## Detailed Proposals

### P0-1) Submission Capture + Public→Private Funnel Audit

**Rationale (meeting link):** Team flagged “no private submissions” repeatedly; decisions are risky until this is clean.  
**Data we already have:** `analysis/no-private-submissions.csv`, `analysis/submission_timeline.parquet`, `analysis/final_scores.csv`.

**What to analyze**

1. For each namespace/question, compute `public test_run -> private submission` conversion.
2. Separate “true student non-submit behavior” from “namespace-level capture failure.”
3. Find time-window or namespace-specific drop-offs.

**Expected insight**

- Which low submission rates are student behavior vs platform instrumentation.

**How this informs course improvement**

- Fixing capture first prevents policy mistakes and false blame on students.
- Enables trustworthy intervention targeting.

---

### P0-2) Hardcoding Vulnerability Map + Sentinel Test Simulation

**Rationale (meeting link):** “Mimic”/hardcoding behavior was highlighted as a major failure mode.  
**Data we already have:** `analysis/errors.json`, `analysis/ERRORS-cluster-*.md`, `analysis/quick-fixes.md`, question JSONs under `problems/`.

**What to analyze**

1. Rank questions by hardcoding-related failure volume.
2. For each, design 1–2 “sentinel” public tests that break memorized/sample-specific solutions.
3. Simulate likely catch-rate increase using existing failing submissions.

**Expected insight**

- Exact questions where tiny public-test edits can prevent large failure pockets.

**How this informs course improvement**

- Rapid test-bank upgrades with minimal content rewrite.

---

### P0-3) S2 Loop Early-Warning Analysis (“Wanderer Detector”)

**Rationale (meeting link):** Team wants to identify students stuck in repeated ineffective tweaks.  
**Data we already have:** `analysis/process_analysis/*`, `analysis/submission_timeline.parquet`, `analysis/code_snapshots.parquet`.

**What to analyze**

1. Detect “S2 streaks” (parseable code, zero tests passed, repeated saves/runs).
2. Measure what actions usually break S2 (if any): fewer edits, simpler rewrite, helper test, etc.
3. Build a rule-based alert threshold for real-time intervention.

**Expected insight**

- Practical trigger point for nudges/buddy outreach before students quit.

**How this informs course improvement**

- Enables targeted, timely support instead of broad generic messaging.

---

### P0-4) Difficulty-Mix Fairness by Namespace and Shuffle Pattern

**Rationale (meeting link):** Team wants one confidence-builder easy question, balanced middle, and some challenge.  
**Data we already have:** `analysis/final_scores.csv`, `analysis/question_metadata.csv`, `analysis/evaluation_redesign/*`, namespace-level question assignments in raw data.

**What to analyze**

1. Tag each question as easy/middle/hard using observed pass distributions.
2. For each namespace (and each student, where possible), compute mix quality.
3. Flag sets with no easy question or too many very easy/hard questions.

**Expected insight**

- Which exam sets were imbalanced by design/distribution.

**How this informs course improvement**

- Better blueprint constraints for future shuffling and exam generation.

---

### P0-5) Operationalize the “Teachable-Now” Segment for Mentoring

**Rationale (meeting link):** Explicit ask to find the “at-risk but teachable” group by process, not marks.  
**Data we already have:** `analysis/teachable.csv`, `analysis/teachable.md`, timeline + error-pattern data.

**What to analyze**

1. Convert current teachable segments (`T1`, `T2`, `T3`) into actionable weekly mentor lists.
2. Add per-student “why selected” explanation (simple tags).
3. Estimate segment sizes by term/wave for staffing.

**Expected insight**

- Clear, auditable shortlist for Python Buddy allocation.

**How this informs course improvement**

- Better mentoring ROI: help students who are both struggling and likely to benefit now.

---

### P1-1) Error-Pattern-to-Hint Mapping (Feedback Redesign)

**Rationale (meeting link):** Team asked for better feedback than pass/fail vectors.  
**Data we already have:** error clusters, test-case pass/fail vectors, common runtime/syntax signatures.

**What to analyze**

1. For top error patterns per question, map to one concrete hint.
2. Validate hint quality on historical failing submissions (offline replay).
3. Build a reusable “if this pattern, show this hint” library.

**Expected insight**

- Which hints are most likely to unblock specific error fingerprints.

**How this informs course improvement**

- Makes feedback teach, not just judge.

---

### P1-2) Multi-Function Scaffold Effect (`...` vs `pass`)

**Rationale (meeting link):** Multi-function placeholders may create unrelated syntax cascades.  
**Data we already have:** question templates, cluster analyses for multi-function questions, syntax/runtime error patterns.

**What to analyze**

1. Compare error profiles in multi-function questions vs similar single-function tasks.
2. Quantify placeholder-related failures (unfinished second function, parse aborts, etc.).
3. Predict gains from changing scaffold defaults to safe placeholders (`pass` + TODO comments).

**Expected insight**

- Whether a tiny template edit can remove a common non-concept failure.

**How this informs course improvement**

- Cleaner measurement of actual logic skill.

---

### P1-3) “Trying Hard vs Random/Copy-Like” Process Signature Analysis

**Rationale (meeting link):** Team wants to separate genuine strugglers from likely template/copy behavior.  
**Data we already have:** event timelines, code snapshot diffs, run/edit cadence.

**What to analyze**

1. Build behavior signatures: progressive refinement vs one-shot jumps vs chaotic mutation.
2. Link each signature to final outcomes and error archetypes.
3. Produce “support-first”, “audit-first”, and “low-engagement” cohorts.

**Expected insight**

- Better targeting of pedagogy vs compliance interventions.

**How this informs course improvement**

- Reduces wasted mentor effort; improves fairness in support decisions.

---

### P1-4) Intervention ROI Simulation (Limited Mentor Capacity)

**Rationale (meeting link):** Mentor programs are capacity-limited; we need high-yield targeting.  
**Data we already have:** segment sizes and distributions from teachable/process analyses.

**What to analyze**

1. Simulate different targeting policies (e.g., all T2 first vs mixed T1/T2/T3).
2. Model expected impact under fixed mentor capacity (e.g., 100, 300, 500 students).
3. Recommend a default allocation policy.

**Expected insight**

- Most impact per mentoring hour.

**How this informs course improvement**

- Scales interventions without overpromising.

---

### P2) Weekly-Assignment Authenticity Linkage (Requires Additional Data)

**Rationale (meeting link):** Team asked whether weekly effort is genuine and predictive.  
**Data needed (not currently in this repo):** Weekly/GRPA event logs + assignment metadata.

**What to analyze (once available)**

1. Build “practice quality” scores from weekly timelines (not just submission count).
2. Link practice quality to OPPE process signatures (not just OPPE marks).
3. Identify students who practiced deeply but still fail in specific concepts.

**Expected insight**

- Who is underprepared vs who is trying but blocked by concept/application gaps.

**How this informs course improvement**

- Better eligibility/support policies, less reliance on raw completion counts.

---

## Suggested Execution Plan (Simple)

### Next 2 weeks (high-confidence quick wins)

1. P0-1 Submission funnel audit.
2. P0-2 Hardcoding sentinel test simulation.
3. P0-3 S2 early-warning rule.
4. P0-5 Teachable-now operational list for mentors.

### Weeks 3–5 (improve feedback + question quality)

1. P1-1 Error-pattern hint mapping.
2. P1-2 Multi-function scaffold analysis.
3. P0-4 Difficulty-mix fairness audit.

### After weekly/GRPA data integration

1. P2 Weekly-authenticity linkage.
2. Refresh teachable segmentation with cross-system effort signals.

---

## What Success Looks Like

In plain terms, we should see:

1. Fewer students “stuck forever” in S2 loops.
2. Fewer avoidable failures from hardcoding/template traps.
3. Better use of mentor capacity on students most likely to improve.
4. More trust in conclusions because submission-capture gaps are explicitly handled.

