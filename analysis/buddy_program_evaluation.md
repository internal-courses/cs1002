# Buddy Program Evaluation (ELI15 Version)

## One-Minute Summary

The buddy program is a good idea and should continue. But right now, too many very different students are being treated the same way. That is why progress is uneven.

We analyzed `3,314` repeaters. Only about `18.98%` are ready for standard mentoring immediately. Many others first need either re-engagement support, a quick diagnosis, or high-touch help.

## Quick Glossary (Plain English)

- **Repeater:** A student who appears in the exam data across multiple terms.
- **Thrashing / Thrasher:** A student keeps making many changes and test runs, but without a clear debugging plan.
- **Success gap:** Difference in pass rate between two groups.
- **Self-loop rate:** How often students stay stuck in the same state instead of moving forward.
- **S2 state:** Code runs, but passes **zero** tests. This is a major “stuck zone.”

## Simple Examples

1. **Thrashing example**
Student A runs tests again and again, makes random edits, and still does not improve. Student B makes a hypothesis, tests one change, checks result, then makes the next change. Student B usually succeeds faster.
In our data, the thrashing group spends about `2.25x` more time and has about `33.81 percentage points` lower success.

2. **Self-loop example**
Imagine a student is stuck where code runs but no tests pass. They keep trying similar edits and stay stuck.
In our data, this stuck state (S2) appears in `47.10%` of public runs, and `78.93%` of S2 transitions stay in S2.

## What Is Good in the Current Program

1. Peer buddies are a strong support model.
2. Weekly sessions are the right rhythm.
3. Progress tracking is already part of the plan.

## What Must Be Improved

1. **Do not use one style for everyone.** Students are different and need different support tracks.
2. **Add explicit debugging method training.** Right now, many students are stuck in high-effort, low-learning loops.
3. **Treat the all-three-term persistent group as foundational learners.** In that group (`497` students), `99.40%` begin in syntax/no-code states.
4. **Fix engagement design.** Week-1 attendance was `30%`, which is `45 percentage points` below requirement.
5. **Use caution with submission counts.** `23` namespaces have zero captured submissions, so raw submit counts can be misleading.

## What Is Missing and Should Be Added

1. **Week-0 triage**: quickly classify students before regular sessions.
2. **Track-specific playbooks** for syntax, runtime debugging, and logic/edge cases.
3. **High-touch lane** for severe stuck and diffuse-pattern students.
4. **Meaningful participation KPI**: at least 2 test runs + 2 real edits per week.
5. **Buddy quality checks**: simple checklist + periodic review.
6. **Concept-priority plan** for hardest concepts (lowest weighted acquisition observed: `3.47%`).
7. **Do not over-focus on question language complexity alone** (p-value `0.68`: not strong evidence by itself).

## Capacity Reality (For 2233 Students)

- At 1:60, you need about **38 buddies**.
- Estimated students needing high-touch support: **~796**.
- Estimated students needing re-engagement-first support: **~201**.

## Practical 4–6 Week Plan

1. Week 0-1: triage all students and assign tracks.
2. Week 1-2: run diagnostic sprints for mixed/diffuse students.
3. Week 2-4: teach debugging protocol in every session.
4. Week 2-6: run syntax bootcamp for persistent foundational subgroup.
5. Every week: measure meaningful participation, not just attendance.

## Recommended Actions Table

| priority | recommendation | why | evidence_metric_ids | kpi | target |
| --- | --- | --- | --- | --- | --- |
| P0 | Replace one-size buddying with triage tracks (D0/D1/D3/T1/T2/T3). | Repeater profiles are heterogeneous; high-touch vs teachable segments need different intervention intensity. | repeaters_path_d1_profile_pct;repeaters_path_d3_profile_pct;repeaters_teachable_any_pct | % students assigned to correct track within first 2 weeks | >=90% |
| P0 | Add 30-45 minute diagnostic sprint for D3 before regular sessions. | Mixed/diffuse students need diagnosis first; generic practice wastes mentor time. | program_est_high_touch_students_2233;repeaters_path_d3_profile_pct | D3 -> T1/T2/T3 conversion by week 3 | >=50% |
| P0 | Teach process protocol explicitly: predict -> run -> trace -> fix. | Thrashing costs 2.25x time with much lower success; process quality is the lever. | thrasher_vs_incremental_time_ratio;thrasher_vs_incremental_success_gap_pp;s2_self_loop_pct | S2 self-loop rate among mentored students | drop by >=15% in 4 weeks |
| P0 | Create a foundational syntax bootcamp track for persistent all-three cohort. | Persistent cohort is overwhelmingly syntax/no-code; advanced debugging clinics miss the root need. | all_three_starts_syntax_or_no_code_pct;top_all_three_state_trajectory_share_pct | Parseable-fraction uplift in bootcamp students | >=+0.20 in 4 weeks |
| P1 | Use concept-first weekly plans: arithmetic/IO/loops/data-aggregation first. | These concepts dominate teachable struggler signals; low-acquisition concepts need deliberate practice. | hardest_concept_acquisition_min_pct | Concept acquisition rate for targeted concepts | >=+10 pp term-over-term |
| P1 | Separate engagement enforcement from learning support. | 30% early attendance vs 75% requirement risks attendance theater and low-trust interactions. | program_week1_attendance_pct;program_attendance_gap_to_requirement_pp | Meaningful participation rate (>=2 runs + >=2 edits/week) | >=70% |
| P1 | Instrument buddy quality: session checklist + random audit + outcomes dashboard. | At ~38 buddies, mentor quality variance can dominate outcomes. | program_buddies_needed_at_1_to_60 | Buddy fidelity score (protocol adherence) | >=85% |
| P1 | Do not evaluate students using raw private-submission counts alone. | Submission capture gaps create false negatives in many namespaces. | zero_submission_namespaces;track_b_rows | Dashboards with capture-status flag enabled | 100% |

## Evidence Files

- `analysis/buddy_program_evaluation.csv`
- `analysis/buddy_program_evaluation_recommendations.csv`
- Source files referenced in the `source_file` column of the metrics CSV.
