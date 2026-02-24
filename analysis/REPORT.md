# Stakeholder Report: What the OPPE Data Says (and What To Do Next)

This report summarizes the main findings from Steps 5 to 9 in plain language.

The short version:

- The exam is passable (`46.83%` full pass), but the biggest failure mode is not syntax. It is logic: students write valid Python that does not solve the problem (`26.72%` of all student-question attempts).
- Student process matters a lot. The biggest newly visible groups are quiet successful solvers and unstable reworkers.
- The biggest debugging bottleneck is State S2: code runs, but passes zero tests. Students get stuck there and almost never escape by “trying more of the same.”
- The hardest-to-help repeaters (the 497 students seen in all three terms) are mostly a syntax/no-code group, not an S2 group. They need different support.
- The evaluation itself can be improved: many test cases are redundant, partial credit often carries little information, and the exam is weak at telling low-performing students apart.

Where the evidence comes from:

- Step 4 waterfall: `syntax_bottleneck_quantified/gating_waterfall_pct.csv`
- Step 5 process + archetypes: `process_analysis/`
- Step 6 psychometrics/IRT: `classical_item_quality/`, `psychometric_irt/`
- Step 7 redesign synthesis: `evaluation_redesign/`
- Step 8 longitudinal analysis: `longitudinal_analysis/`
- Step 9 concept modelling: `concept_knowledge_modeling/`

## Part A: How Students Are Performing

### Findings (Step 4 + Step 3 + Step 7)

The most important picture in the whole project is the gating waterfall. It shows where student-question attempts stop.

Source files:

- `syntax_bottleneck_quantified/gating_waterfall_pct.csv`
- `evaluation_redesign/step7_key_metrics.csv`
- `error_taxonomy/track_summary.csv`
- `error_taxonomy/best_public_test_run_classification_rows.csv`
- `error_taxonomy/regression_summary.csv`

#### Centrepiece: Gating Waterfall (all student-question attempts)

| Gate                                          | % of All Student-Question Attempts |
| --------------------------------------------- | ---------------------------------: |
| Full pass                                     |                             46.83% |
| Genuine logic failure                         |                             26.72% |
| Edge-case gated (passes core, fails edge)     |                              7.35% |
| Syntax gated - mechanical (structure evident) |                              7.14% |
| Unmodified skeleton / didn't attempt          |                              6.14% |
| Partial pass                                  |                              3.21% |
| Syntax gated - fundamental (no structure)     |                              2.36% |
| Formatting gated                              |                              0.25% |

What this means in simple terms:

- Nearly half of all attempts succeed. This exam is not “impossible.”
- The biggest problem is not students failing to write Python syntax.
- The biggest problem is students writing runnable Python that gives the wrong answer.

This directly answers the original concern (“Are students mainly blocked by syntax?”):

- Combined syntax gates are about `9.5%` (`7.14% + 2.36%`).
- Genuine logic failure is `26.72%`.
- Logic failure is about `2.81x` the combined syntax gates.
- Evidence: `evaluation_redesign/step7_key_metrics.csv`

#### Students who are “almost there”

`7.35%` are edge-case gated.

- These students pass the core idea but fail boundary conditions.
- This is a high-value group for targeted feedback because they are close.

#### Regression is a process problem, not just a knowledge problem

`45.49%` of students who end with non-parseable code had parseable code earlier.

- They had something working (or at least runnable), then broke it while editing.
- This is a maintain/debugging workflow issue, not simply “they never understood the topic.”
- Evidence: `evaluation_redesign/step7_key_metrics.csv`, `error_taxonomy/regression_summary.csv`

#### Formatting is not the problem

Formatting-only gating is `0.25%`.

- The evaluation system is mostly robust to output formatting differences.
- This is good news: formatting cleanup is not where effort should go.

#### Non-submission context (important caveat before anyone blames students)

Non-submission is large overall, but most of it is a data capture problem.

From `error_taxonomy/track_summary.csv`:

- Total student-question rows: `151,778`
- Non-submission rows overall: `108,860` (`71.72%`)
- Track B (zero-submission namespaces): `97,748` rows

So:

- `89.79%` of all non-submission rows are in namespaces where submission capture is broken.
- This is a platform/instrumentation issue, not student behavior.

In submission-positive namespaces (the real “genuine non-submitters” group), the best public run is usually broken:

- Runtime-related best-public failure modes are about `62%` (unspecified runtime + typed runtime errors combined) for `Track A: non-submitters (submission-positive NS)`.
- Evidence source: `error_taxonomy/best_public_test_run_classification_rows.csv`

That means these students are usually not “choosing not to submit a correct solution.” They are stuck.

### Actions (what to do next)

1. Treat the gating waterfall as the primary performance summary in stakeholder conversations.
2. Reframe the main teaching problem as logic/debugging support, not only syntax remediation.
3. Keep edge-case-gated students visible as a distinct “almost there” support group.
4. Fix submission capture before making strong claims about submission behavior (see Part F, Priority 1).

## Part B: How Students Work

### Findings (Step 5 + Step 5a + Step 7)

The process story became much clearer after resolving the old “Other” bucket.

Source files:

- `process_analysis/archetype_outcomes_primary_summary.csv`
- `process_analysis/archetype_primary_by_question.csv`
- `process_analysis/attempt_archetypes.csv`
- `process_analysis/death_spiral_transition_matrix_combined.csv`
- `process_analysis/error_recovery_by_type.csv`
- `evaluation_redesign/public_state_distribution_combined.csv`
- `evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv`
- `evaluation_redesign/step7_key_metrics.csv`

#### Archetype distribution (final, mostly complete)

The “Other” bucket is now small (`6.40%`), which makes the archetype picture usable.

| Archetype             | % of Attempts | Success Rate | Median Active Time (s) | Median Public Runs |
| --------------------- | ------------: | -----------: | ---------------------: | -----------------: |
| Minimal-change solver |        18.54% |       77.27% |                   37.0 |                3.0 |
| Volatile reworker     |        17.75% |       35.95% |                 3223.0 |               18.0 |
| Steady builder        |        15.95% |       89.04% |                  643.0 |                6.0 |
| Builder with setbacks |         8.29% |       41.76% |                  844.0 |                7.0 |
| Incremental debugger  |         7.66% |       77.65% |                 1998.0 |               13.0 |
| Regression            |         7.66% |        5.65% |                 3016.0 |               13.0 |
| Other (residual)      |         6.40% |       35.48% |                  787.0 |                7.0 |
| Skeleton-only         |         6.14% |        0.48% |                    1.0 |                1.0 |
| One-shot              |         5.02% |        9.44% |                    0.0 |                1.0 |
| Stuck and abandoned   |         2.77% |        4.11% |                 3117.0 |                8.0 |
| Thrasher              |         1.81% |       43.59% |                 4528.5 |               36.0 |
| Flat stuck            |         1.67% |        0.12% |                  224.0 |                3.0 |
| Late starter          |         0.35% |       25.66% |                 1524.0 |                6.0 |

Evidence: `process_analysis/archetype_outcomes_primary_summary.csv`

#### What changed the story most

The two biggest newly visible groups are:

- `Minimal-change solver` (`18.54%`): students who solve quickly with little visible process.
- `Volatile reworker` (`17.75%`): students who keep restructuring code and get unstable outcomes.

This matters because these two groups used to be hidden inside “Other,” which made the process story look much less informative than it really is.

#### Better process beats more effort

Two comparisons make this obvious:

1. Classic Step 5 comparison (flag-based):

- Incremental debugger: `77.28%` success, median `2013s`
- Thrasher: `43.47%` success, median `4533s`
- Thrasher spends `2.25x` more time for much worse outcomes
- Evidence: `evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv`

2. Final Step 5a primary labels (all attempts):

- Incremental debugger: `77.65%` success, median `1998s`
- Volatile reworker: `35.95%` success, median `3223s`
- Volatile reworkers spend much more time and still do much worse
- Evidence: `process_analysis/archetype_outcomes_primary_summary.csv`

#### Thrashing is mostly a question-design signal, not a student identity

At the question level, some problems trigger high thrashing rates:

- `Pattern printing - Centered Triangle Of Zeroes` (`12.59%` and `10.11%` in two variants)
- `Reversed Squares of List Elements` (`7.08%`)
- `Pangram Check` (`6.96%`)
- `File Content Zig-Zag Shift` (`6.91%`)

Evidence: `process_analysis/archetype_primary_by_question.csv`, `evaluation_redesign/question_redesign_targets_high_priority.csv`

But at the student level, Thrasher almost disappears as a dominant pattern:

- Dominant archetype in student-wave rows: `Thrasher = 34` rows (`0.12%`)
- Dominant archetype in student-term rows: `Thrasher = 9` rows (`0.05%`)
- Evidence: `longitudinal_analysis/student_wave_primary_archetype.csv`, `longitudinal_analysis/student_term_primary_archetype.csv`

This is why the report should treat thrashing as a question-design signal, not a stable student label.

#### The S2 “death spiral” (the main process bottleneck)

S2 means: code is parseable (valid Python), but it passes zero public tests.

Why S2 matters:

- It is the largest public-run state: `47.1%` of all public test-run states
- It has a `78.93%` self-loop (students stay in S2 on the next run)
- Evidence: `evaluation_redesign/public_state_distribution_combined.csv`, `process_analysis/death_spiral_transition_matrix_combined.csv`

This is the pattern of a student who can write code that runs, but cannot make it correct.

#### Recovery is easier for syntax than logic

From `process_analysis/error_recovery_by_type.csv`:

- `SyntaxError (structure evident)` resolves within 1 public run: `50.33%`
- `SyntaxError (no structure)` resolves within 1 public run: `43.70%`
- `Wrong Answer` persists to final public run: `39.03%`

Plain-language meaning:

- Syntax problems often get fixed quickly (especially when the intended structure is visible).
- Wrong-answer problems are much “stickier.”

#### Concrete examples (real attempts)

These examples come from raw submissions in `submissions/pyoppe_student_submissions_000000000000.json`, with labels cross-checked against:

- `process_analysis/attempt_archetypes.csv`
- `error_taxonomy/best_public_test_run_classification_rows.csv`

Example 1: Wrong output on pattern printing (later solved) (`Volatile reworker`)

- Student: `000f6a3bc2674b73a06fb6cbbfbfdac2`
- Namespace/question: `ns_25t1_py11_1`, Problem 10, `Pattern Printing - W Pattern`
- Early public run: `Wrong Answer`, `0/4` passed
- Best public outcome for the attempt: `All Cases Passed` (`4/4`)

```py
n = int(input())
if n == 1:
    q = "|" + "/" + "\\" + "|"
    print(q)
if n >= 2:
    for i in range(n):
        q = "|" + " " * (n - i - 1) + "/" + "\\" + " " * (n - i - 1) + "|"
print(q)
```

What went wrong (ELI15): it prints only the last built row, not the full W shape.

Example 2: Runtime error on data-analysis question (`Builder with setbacks`)

- Same student
- Problem 9, `Student Score Filter`
- Best public outcome for the attempt: `Runtime Error` (`TypeError`)

```py
for data in dict:
    sum = 0
    for i in range(len(data)):
        sum += data[i]
```

Observed error (first failing test): `TypeError: 'type' object is not iterable`

- The code loops over `dict` (the Python type), not the input variable.

Example 3: Uses the right shape, wrong logic (duplicate counting instead of unique counting) (`Volatile reworker`)

- Same student
- Problem 6, `Counts unique even and odd numbers`
- Early public run: `Wrong Answer`, `1/4` passed
- Best public outcome for the attempt: `All Cases Passed`

```py
s = tuple(l)
c = 0
e = 0
for i in s:
    if i % 2 == 0:
        c = c + 1
    else:
        e = e + 1
```

What went wrong (ELI15): the function counts all numbers, not unique numbers.

### Actions (what to do next)

1. Teach debugging process explicitly (small edits, test after each edit, read failures carefully).
2. Prioritize S2-targeted support (see Part F, Priority 2).
3. Redesign questions that trigger high thrashing (see Part F, Priority 7).
4. Avoid calling students “thrashers” as if it is a stable identity; treat it as a question-level warning sign.

## Part C: How Well the Evaluation Works

### Findings (Step 2 + Step 6 + Step 7)

The evaluation system is good in some ways (low formatting tax, almost no public-test overfitting) and weak in others (redundant test cases, weak partial-credit spread, low-ability blind spot).

Source files:

- `evaluation_redesign/step7_key_metrics.csv`
- `classical_item_quality/question_item_redundancy_pairs.csv`
- `classical_item_quality/namespace_reliability_summary.csv`
- `classical_item_quality/public_private_gap_summary.csv`
- `psychometric_irt/question_parameter_flags.csv`
- `psychometric_irt/tif_low_ability_flags.csv`
- `psychometric_irt/submitter_public_vs_private_category_agreement.csv`
- `psychometric_irt/namespace_pair_theta_linked_comparisons.csv`
- `psychometric_irt/theta_linked_wave_pair_comparisons.csv`
- `evaluation_redesign/question_redesign_targets_high_priority.csv`
- `evaluation_redesign/variant_equivalence_review_targets.csv`

#### Test cases are heavily redundant

- `34.46%` of within-question test-case pairs are near-redundant (`phi > 0.90`)
- Median Cronbach's alpha across submitter namespaces is `0.9716`

Plain-language meaning:

- The tests are very consistent, but often too similar to each other.
- That means some test capacity is “wasted” checking the same thing repeatedly.

#### Partial credit often does not separate difficulty levels well

- `47.35%` of questions have narrow GRM thresholds (`b2 - b1 < 0.35`)

Plain-language meaning:

- For about half the questions, “some tests passed” and “all tests passed” are almost the same difficulty level.
- So partial credit exists, but often does not add much measurement value.

#### The exam is weak at measuring low-performing students

- `33/35` namespaces are flagged as low-ability blind
- Median low-to-mid information ratio is `0.1555`

Plain-language meaning:

- The exam is much better at telling apart average students than weaker students.
- This is a problem because later terms contain weaker students by design.

#### The biggest design-quality red flags

- `15` cliff-like questions (big threshold effects, weak gradation)
- Some question variants are not equivalent
- Example largest linked-mean theta gap: `ns_25t1_py22_1` vs `ns_25t1_py22_2`, delta `+0.653`
- Another operationally important pair: `ns_25t2_py21_1` vs `ns_25t2_py21_2` (smaller mean delta but strong item drift; worst linked b1 drift on `File Content Zig-Zag Shift`)

Evidence: `evaluation_redesign/variant_equivalence_review_targets.csv`

#### What is _not_ a problem (important to say clearly)

- Public-test overfitting is tiny: `0.02%`
  - Evidence: `classical_item_quality/public_private_gap_summary.csv`
- Formatting tax is tiny: `0.25%`
  - Evidence: `syntax_bottleneck_quantified/gating_waterfall_pct.csv`

These are not where redesign effort should go.

#### Public-best (used for GRM) can overstate true mastery for some submitters

Because Track B only has public tests, public-best is used for consistent calibration. That is reasonable, but there is a caveat:

- `14.27%` of submitters have public category > private category
- Agreement rate between public and private categories is `85.22%`
- Evidence: `psychometric_irt/submitter_public_vs_private_category_agreement.csv`

Plain-language meaning:

- Public-best is useful for comparing students consistently, but it slightly overstates absolute mastery for some students.

### Actions (what to do next)

1. Redesign test sets to widen difficulty spread (warm-up + stretch cases).
2. Prioritize the 15 cliff-like questions and high-redundancy / narrow-threshold questions.
3. Audit variant equivalence before treating variants as interchangeable.
4. Keep public-best for cross-population modelling, but label it clearly as an upper-bound proxy for absolute mastery.

## Part D: What Students Don't Understand (Concepts)

### Findings (Step 9)

Step 9 adds the curriculum-level view: which concepts are hard, which constructs students use, and whether they fail because they chose the wrong tool or used the right tool badly.

Source files:

- `concept_knowledge_modeling/step9_key_metrics.csv`
- `concept_knowledge_modeling/concept_question_map.csv`
- `concept_knowledge_modeling/concept_mastery_overall.csv`
- `concept_knowledge_modeling/construct_focus_usage_mastery.csv`
- `concept_knowledge_modeling/repeat_student_concept_profile_pair_summary.csv`
- `concept_knowledge_modeling/repeat_student_concept_retention_acquisition_summary.csv`
- `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_proxy_rollup_aligned_proxy.csv`
- `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_summary_aligned_proxy.csv`
- `concept_knowledge_modeling/concept_tagging_examples_by_concept.csv`
- `concept_knowledge_modeling/concept_prerequisite_edge_candidates.csv`

#### Concept map coverage is complete (good foundation)

- `251/251` questions tagged
- `0` untagged questions
- Average tags per question: `1.5936`

This is enough coverage to support concept-level reporting now (with a caveat that tags are heuristic; see Caveats section).

#### Hardest concepts (public-best all-pass rate)

From `concept_knowledge_modeling/concept_mastery_overall.csv`:

- `Data analysis / aggregation`: `21.14%` (hardest)
- `Input parsing / output formatting`: `29.52%`
- `Pattern printing`: `30.49%`
- `File operations`: `30.52%`

#### Core concepts (more students can handle these)

- `Arithmetic / conditionals`: `60.23%`
- `List / tuple operations`: `52.02%`
- `String manipulation`: `51.83%`

Plain-language meaning:

- Students can often handle basic conditions, lists, and strings.
- They struggle much more when tasks look like mini data pipelines, formatted outputs, or pattern-generation problems.

#### “Usage vs mastery” changes the teaching intervention

From `concept_knowledge_modeling/construct_focus_usage_mastery.csv`:

- Loops (`for_loop`, `while_loop`)
  - Usage rate: `48.67%`
  - All-public-pass among users: `45.73%`
  - Gap type: `High usage, low mastery`
  - Meaning: many students know they need a loop, but cannot make the loop logic work reliably.

- List comprehensions (`list_comp`)
  - Usage rate: `4.53%`
  - Gap type: `Low usage, low mastery`
  - Meaning: this construct is not yet widely absorbed.

- Dictionaries (using `dict_comp` as a narrow proxy)
  - Usage rate: `0.41%`
  - Gap type: `Low usage, low mastery`
  - Meaning: use with caution because the proxy is narrow.

- Error handling (`try_stmt`)
  - Usage rate: `1.45%`
  - Gap type: `Low usage, low mastery`

Teaching implication (simple rule):

- High usage + low mastery = students know _when_ to use it, but not _how_ to use it well -> practice + worked examples.
- Low usage + low mastery = students have not absorbed it yet -> more exposure + pattern recognition examples.

#### S2 bottleneck, now decomposed by concept (application gap vs selection gap)

This is the key bridge from process analysis to curriculum design.

Using the aligned S2 proxy (`selected_snapshot_s2_like = true`), from:

- `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_proxy_rollup_aligned_proxy.csv`
- `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_summary_aligned_proxy.csv`

Examples:

- `Loops and iteration`: application-gap proxy `64.71%`
- `Pattern printing`: application-gap proxy `93.61%`
- `Data analysis / aggregation`: application-gap proxy `66.80%`
- `String manipulation`: application-gap proxy `65.26%`

Plain-language meaning:

- In many S2 failures, students are already using the relevant construct.
- They usually picked the right tool, but used it incorrectly.
- That strongly supports debugging/application-focused interventions (not just “teach the concept again” lectures).

Exception:

- `Dictionary operations` and `File operations` look selection-heavy in this proxy view, but those rows use weak/narrow construct proxies (`dict_comp`, `import_*`, etc.). Treat cautiously.

#### Repeat students do learn concepts, but some concepts barely move

From `concept_knowledge_modeling/repeat_student_concept_profile_pair_summary.csv`:

- `25t1->25t2`: `66.52%` gained at least one new concept
- `25t2->25t3`: `61.37%` gained at least one new concept

But hardest concepts have low acquisition rates (from `repeat_student_concept_retention_acquisition_summary.csv`):

- `Data analysis / aggregation`: `9.42%` then `3.53%`
- `Pattern printing`: `7.57%` then `0.76%`
- `Input parsing / output formatting`: `9.95%` then `7.54%`
- `File operations`: `5.77%` then `0.00%` (very sparse in later pair)

Plain-language meaning:

- Repeaters are learning something.
- But a few hard concepts are not improving much under the current remediation approach.

#### Prerequisite graph is useful as a review tool, not a final curriculum map (yet)

- Candidate prerequisite edges: `24`
- Proxy-order “misaligned” candidates: `20`
- Evidence: `concept_knowledge_modeling/step9_key_metrics.csv`, `concept_knowledge_modeling/concept_prerequisite_edge_candidates.csv`

This is a good signal to review teaching order, but it should be compared against the real syllabus sequence before making direct sequencing changes.

### Actions (what to do next)

1. Focus concept support on the hardest cluster first: data analysis, pattern printing, input parsing/formatting, file operations.
2. Use different interventions for different gap types (usage-vs-mastery logic).
3. Treat S2 primarily as an application/debugging gap for most concepts.
4. Review the curriculum sequence using the prerequisite graph, but only after mapping against the actual syllabus order.

## Part E: The Longitudinal Picture (What Changes Over Time)

### Findings (Step 8, non-IRT-linked)

Even without wave-pair IRT linking, the paired analyses show strong evidence of learning. The main exception is a small dominant-S2 group that does not move.

Source files:

- `longitudinal_analysis/step8_key_metrics.csv`
- `longitudinal_analysis/within_term_rank_change_summary.csv`
- `longitudinal_analysis/within_term_category_change_summary.csv`
- `longitudinal_analysis/cross_term_term_pairs_enriched.csv`
- `longitudinal_analysis/cross_term_syntax_progression_summary.csv`
- `longitudinal_analysis/cross_term_construct_progression_summary.csv`
- `longitudinal_analysis/within_term_s2_dominant_escape_summary.csv`
- `longitudinal_analysis/cross_term_s2_escape_summary.csv`
- `longitudinal_analysis/all_three_term_state_trajectory_summary.csv`
- `longitudinal_analysis/all_three_term_archetype_trajectory_summary.csv`
- `longitudinal_analysis/all_three_term_trajectories.csv`
- `longitudinal_analysis/pass_through_model_performance.csv`
- `longitudinal_analysis/pass_through_risk_segments.csv`
- `longitudinal_analysis/within_term_archetype_targeted_productive_summary.csv`
- `longitudinal_analysis/cross_term_archetype_targeted_productive_summary.csv`

#### Within-term learning is strong (Wave 1 -> Wave 2)

Paired students improve a lot in category-based performance, even if rank movement is small (because everyone is learning at the same time).

Within-term weighted improvement rates:

- `25t1`: `57.68%` improve
- `25t2`: `68.92%` improve
- `25t3`: `59.14%` improve

Within-term mean category delta (`Wave2 - Wave1`):

- `25t1`: `+0.2063`
- `25t2`: `+0.3830`
- `25t3`: `+0.2259`

Median rank deltas are near zero (as expected in a same-cohort comparison):

- `25t1`: `-0.0091`
- `25t2`: `+0.0025`
- `25t3`: `-0.0017`

Evidence: `longitudinal_analysis/within_term_rank_change_summary.csv`, `longitudinal_analysis/within_term_category_change_summary.csv`

#### Cross-term repeaters also improve a lot

Among substantive repeaters:

- `25t1->25t2`: `80.95%` improve, `4.93%` same, `14.13%` decline
- `25t2->25t3`: `76.53%` improve, `7.21%` same, `16.26%` decline

Evidence: derived from `longitudinal_analysis/cross_term_term_pairs_enriched.csv`

#### Syntax-gated repeaters often move to pass-like profiles

From `longitudinal_analysis/cross_term_syntax_progression_summary.csv`:

- `25t1->25t2`: `53.30%` of syntax-gated repeaters move to pass-like profiles
- `25t2->25t3`: `47.67%` move to pass-like profiles

Plain-language meaning:

- A lot of students who start out blocked by syntax are progressing.

#### Structural progression is visible in code (not just scores)

From `longitudinal_analysis/cross_term_construct_progression_summary.csv` (mean rate change):

- `for_loop`: up (`+0.1117`, `+0.0600`)
- `if_stmt`: up (`+0.0557`, `+0.0606`)
- `list_comp`: up (`+0.0386`, `+0.0140`)
- `print_call`: down (`-0.0485`, `-0.0289`)

Plain-language meaning:

- Students use more real program structure over time.
- They rely less on print-heavy trial code.

#### The stark exception: dominant-S2 students do not escape

This is the strongest negative finding in the whole longitudinal analysis.

Dominant-S2 escape (`dominant S2 -> dominant S3/S4`) is `0%`:

- Within-term: all three terms
- Cross-term: both term pairs

Evidence: `longitudinal_analysis/step8_key_metrics.csv`, `longitudinal_analysis/within_term_s2_dominant_escape_summary.csv`, `longitudinal_analysis/cross_term_s2_escape_summary.csv`

Important context:

- This is a strict dominant-state lens.
- It is a small group (roughly tens to low hundreds depending on pairing), but it is a true zero-conversion signal.

#### The 497 all-three-term students are mostly a syntax/no-code group, not an S2 group

This is the most important reframing for intervention design.

From `longitudinal_analysis/all_three_term_state_trajectory_summary.csv`:

- Top trajectory: `S1_syntax_fundamental -> S1_syntax_fundamental -> S1_syntax_fundamental` = `181` students
- Next: `S0_no_code -> S1_syntax_fundamental -> S1_syntax_fundamental` = `69` students
- Students whose dominant three-term trajectory starts in S2: only `3`

Plain-language meaning:

- The hardest persistent cohort mostly needs foundational Python support (syntax, code structure, basic program construction).
- They are not mainly the same group as the S2 debugging bottleneck.

#### Repeaters are not “stuck in one process mode”

The all-three-term archetype trajectories are now much more informative after Step 5a.

From `longitudinal_analysis/all_three_term_archetype_trajectory_summary.csv` and `all_three_term_trajectories.csv`:

- `Builder with setbacks` appears in `404/497` all-three-term trajectories
- `Minimal-change solver` appears in `210/497`
- `Incremental debugger` appears in `151/497`
- Top sequence: `Builder with setbacks -> Builder with setbacks -> Builder with setbacks` (`56` students)

Plain-language meaning:

- Many repeaters are making progress in a messy way.
- “Builder with setbacks” is not a dead-end label. It often describes real learning with instability.

#### Concrete repeater examples (to avoid over-abstracting)

Source: `longitudinal_analysis/all_three_term_trajectories.csv`

Examples that still look “persistent” in dominant-state terms but show progress in outcomes/process:

- `030e84cf594345549da87b755e9fc6c0`
  - Error trajectory: `No activity / skeleton -> Full pass -> Public full pass, no submit`
  - Archetype trajectory: `Other -> Builder with setbacks -> Incremental debugger`
  - State trajectory: `S1 -> S1 -> S1`
- `04e3c983d8084c44a5e1375a32b85416`
  - Error trajectory: `Public full pass, no submit -> Submitted, zero -> Full pass`
  - Archetype trajectory: `Minimal-change solver -> Builder with setbacks -> Builder with setbacks`
  - State trajectory: `S1 -> S1 -> S1`
- `056ee997e3ab4eca9ec1afac0476aac8`
  - Error trajectory: `Wrong output - edge/partial -> Full pass -> Full pass`
  - Archetype trajectory: `Builder with setbacks -> Minimal-change solver -> Builder with setbacks`
  - State trajectory: `S1 -> S1 -> S1`

This is why we need multiple lenses (error profile, archetype, state), not just one.

Examples ending in pass-like outcomes despite earlier failures:

- `017b58f1dad14446b4b7a55c77af8d4b`: `Runtime error -> Full pass -> Public full pass, no submit`
- `02253a066ff74cf6a7fd068443d32ba5`: `Runtime error -> No activity / skeleton -> Public full pass, no submit`
- `027f0818c1c3432cb0ab50db1fcdaa54`: `Runtime error -> Full pass -> Public full pass, no submit`

#### The pass-through model is good enough to use for risk segmentation

From `longitudinal_analysis/pass_through_model_performance.csv`:

- Cross-validated AUC: `0.9193`
- Brier score: `0.0952`

From `longitudinal_analysis/pass_through_risk_segments.csv`:

- Risk deciles are well separated (predicted exit probability and observed exit rate move together strongly)

Plain-language meaning:

- The model is useful for prioritizing outreach/support, as long as everyone remembers the outcome is an exit proxy (pass + attrition mix), not pure passing.

### Actions (what to do next)

1. Keep using paired analyses (within-term and repeater-based) as the main longitudinal evidence.
2. Treat dominant-S2 students as a special intervention group with dedicated support.
3. Treat the 497 all-three-term cohort as a foundational Python instruction problem, not primarily a debugging problem.
4. Use the pass-through risk model for targeted support planning (with the exit-proxy caveat clearly labeled).

## Part F: Recommended Actions (Prioritized)

This is the action list for teaching, exam design, and platform/engineering teams.

Evidence sources across rows:

- Steps 4/5/6/7/8/9 outputs in `syntax_bottleneck_quantified/`, `process_analysis/`, `psychometric_irt/`, `evaluation_redesign/`, `longitudinal_analysis/`, `concept_knowledge_modeling/`

| Priority | Action                                                                                                                              | Evidence                                                                                                                                                                                                                                                  | Impact                             | Effort       |
| -------: | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------ |
|        1 | **Fix submission capture pipeline**                                                                                                 | `evaluation_redesign/submission_capture_namespace_audit.csv`, `evaluation_redesign/submission_capture_term_wave_namespace_summary.csv`, `error_taxonomy/track_summary.csv` (23/35 namespaces have zero submissions; Track B still has many public passes) | Critical (operational)             | Low-Moderate |
|        2 | **Address the S2 bottleneck with structured test feedback + progressive problem design**                                            | `process_analysis/death_spiral_transition_matrix_combined.csv`, `evaluation_redesign/s2_bottleneck_summary.csv`, `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_proxy_rollup_aligned_proxy.csv`                                       | Very High                          | Moderate     |
|        3 | **Redesign test cases for difficulty spread** (reduce redundancy + widen threshold gaps)                                            | `classical_item_quality/question_item_redundancy_pairs.csv`, `psychometric_irt/question_parameter_flags.csv`, `evaluation_redesign/question_redesign_targets_high_priority.csv`                                                                           | Very High                          | Moderate     |
|        4 | **Add easy warm-up questions** (low-ability measurement + confidence)                                                               | `psychometric_irt/tif_low_ability_flags.csv`, `evaluation_redesign/low_ability_measurement_overall_summary.csv`                                                                                                                                           | High                               | Low          |
|        5 | **Pilot layered scoring** (after test-case redesign where needed)                                                                   | `evaluation_redesign/layered_scoring_readiness_summary.csv`, `evaluation_redesign/layered_scoring_readiness_by_question.csv`                                                                                                                              | High                               | Moderate     |
|        6 | **Teach debugging process explicitly** using exemplar trajectories                                                                  | `process_analysis/archetype_outcomes_primary_summary.csv`, `evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv`, `longitudinal_analysis/within_term_archetype_targeted_productive_summary.csv`                                          | High                               | Moderate     |
|        7 | **Redesign high-thrash questions** (e.g., Centered Triangle of Zeroes, Pangram Check, Reversed Squares, File Content Zig-Zag Shift) | `process_analysis/archetype_primary_by_question.csv`, `evaluation_redesign/question_redesign_targets_high_priority.csv`                                                                                                                                   | High                               | Low          |
|        8 | **Improve runtime error specificity in the platform** (exception type + traceback in UI and logs)                                   | `error_taxonomy/runtime_error_type_summary.csv`, `evaluation_redesign/runtime_feedback_quality_overall.csv`                                                                                                                                               | High                               | Low          |
|        9 | **Target the hardest concept cluster in teaching/remediation** (data analysis, pattern printing, input formatting)                  | `concept_knowledge_modeling/concept_mastery_overall.csv`, `concept_knowledge_modeling/repeat_student_concept_retention_acquisition_summary.csv`                                                                                                           | High                               | Moderate     |
|       10 | **Investigate and fix variant inequivalence** (start with `25t1 py22` and `25t2 py21`)                                              | `evaluation_redesign/variant_equivalence_review_targets.csv`, `psychometric_irt/namespace_pair_theta_linked_comparisons.csv`                                                                                                                              | Moderate                           | Low          |
|       11 | **Add syntax linter / feedback for mechanical syntax errors**                                                                       | `syntax_bottleneck_quantified/gating_waterfall_pct.csv`, `process_analysis/error_recovery_by_type.csv` (mechanical syntax is sizeable and recoverable)                                                                                                    | Moderate                           | Low-Moderate |
|       12 | **Audit problem statement clarity** for high-thrash + high wrong-output-logic questions                                             | `evaluation_redesign/problem_statement_clarity_review_targets.csv`, `evaluation_redesign/question_redesign_targets_high_priority.csv`                                                                                                                     | Moderate                           | Low          |
|       13 | **Include 2-3 anchor questions across waves** for future IRT growth analysis                                                        | `psychometric_irt/theta_linked_wave_pair_comparisons.csv` (currently none), `longitudinal_analysis/future_wave_anchor_candidate_titles.csv` (46 candidates)                                                                                               | Moderate (enables future analysis) | Low          |
|       14 | **Design a foundational Python intervention for the 497 persistent cohort**                                                         | `longitudinal_analysis/all_three_term_state_trajectory_summary.csv`, `longitudinal_analysis/all_three_term_trajectories.csv` (mostly S0/S1/S1 patterns, not S2)                                                                                           | High                               | High         |
|       15 | **Deploy the pass-through risk model for pre-term targeting**                                                                       | `longitudinal_analysis/pass_through_model_performance.csv`, `longitudinal_analysis/pass_through_model_scored_rows.csv`, `longitudinal_analysis/pass_through_risk_segments.csv`                                                                            | High                               | Moderate     |
|       16 | **Review curriculum sequence against the empirical prerequisite graph** (after mapping to actual syllabus order)                    | `concept_knowledge_modeling/concept_prerequisite_edge_candidates.csv`, `concept_knowledge_modeling/step9_key_metrics.csv`                                                                                                                                 | High                               | High         |
|       17 | **Build a per-student diagnostic dashboard** (archetype + concept profile + risk + score trajectory)                                | Inputs available across `process_analysis/`, `longitudinal_analysis/`, `concept_knowledge_modeling/`, `psychometric_irt/`                                                                                                                                 | High                               | High         |

## 10b. Visualisations To Produce (High Information Density)

These are the visuals that carry the most signal with the least clutter.

### 1) Gating Waterfall (centrepiece)

What to show:

- Combined waterfall plus side-by-side Track A / Track B bars
- Mechanical vs fundamental syntax split

Source files:

- `syntax_bottleneck_quantified/gating_waterfall_pct.csv`
- `error_taxonomy/track_summary.csv`

Why it matters:

- Instantly shows that logic failure is the largest failure mode.

### 2) Archetype Distribution + Outcomes (two-panel)

Panel A:

- Archetype prevalence (% attempts)

Panel B:

- Success rate by archetype
- Add labels for median active time (to make effort-vs-outcome visible)

Source files:

- `process_analysis/archetype_outcomes_primary_summary.csv`
- `evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv`

### 3) S2 State-Transition Diagram (Sankey or transition graph)

Highlight:

- `S2 -> S2 = 78.93%`
- `S2 -> S3 = 7.18%`
- `S2 -> S4 = 3.56%`

Source files:

- `process_analysis/death_spiral_transition_matrix_combined.csv`
- `evaluation_redesign/public_state_distribution_combined.csv`

### 4) Test Information Function (TIF) Overlay

What to show:

- Several representative namespaces on the same theta axis
- Shade low-ability region
- Mark where later-term cohorts cluster (if overlaid)

Source files:

- `psychometric_irt/tif_low_ability_flags.csv`
- `psychometric_irt/namespace_tif_grid.csv` (if present in Step 6 outputs)
- `psychometric_irt/namespace_theta_summary.csv` (if present in Step 6 outputs)

### 5) Concept Mastery Heatmap (concept x term)

Rows:

- Concepts

Columns:

- Terms (and optionally wave splits)

Color:

- All-public-pass rate

Source files:

- `concept_knowledge_modeling/concept_mastery_overall.csv`
- `concept_knowledge_modeling/concept_mastery_by_term.csv`
- `concept_knowledge_modeling/concept_mastery_by_term_wave.csv`

### 6) Within-Term Improvement Distribution (histograms)

What to show:

- Distribution of per-student category deltas (Wave 1 -> Wave 2)
- One histogram per term

Source files:

- `longitudinal_analysis/within_term_rank_change_distribution.csv`
- `longitudinal_analysis/within_term_rank_change_summary.csv`

### 7) Cross-Term Error Profile Shift (alluvial/Sankey)

What to show:

- Source dominant error bucket -> next-term dominant error bucket
- Highlight syntax -> pass-like flow

Source files:

- `longitudinal_analysis/cross_term_error_shift_matrix.csv`
- `longitudinal_analysis/cross_term_syntax_progression_summary.csv`

### 8) Persistent 497 Cohort Trajectory Heatmap / Small Multiples

What to show:

- Top 10-15 dominant-state trajectories across t1 -> t2 -> t3
- Make `S1 -> S1 -> S1` visually obvious

Source files:

- `longitudinal_analysis/all_three_term_state_trajectory_summary.csv`
- `longitudinal_analysis/all_three_term_trajectories.csv`

### 9) Concept Usage vs Mastery Scatter

Axes:

- X = usage rate
- Y = mastery rate among users

Quadrants:

- Don’t know when
- Don’t know how
- Not absorbed
- Mastered

Source file:

- `concept_knowledge_modeling/construct_focus_usage_mastery.csv`

### 10) Redundancy vs Threshold-Gap Scatter (question quality)

Axes:

- X = redundancy (e.g., mean pairwise phi / redundant-pair rate)
- Y = `b2 - b1` threshold gap

Quadrants:

- high redundancy + narrow gap = redesign priority
- low redundancy + wide gap = stronger design

Source files:

- `evaluation_redesign/question_redesign_targets_high_priority.csv`
- `evaluation_redesign/question_redesign_features.csv`
- `psychometric_irt/question_parameter_flags.csv`

## 10c. Data Tables To Produce for Operational Follow-Up

These are the handoff tables for specific teams. Several already exist and can be used immediately.

### 1) Question Redesign Priority List (question authors)

Goal:

- One ranked to-do list combining redundancy, thrashing, logic-failure rates, and IRT flags.

Use now:

- `evaluation_redesign/question_redesign_targets_high_priority.csv` (already combines most Step 2/5/6 signals + redesign reasons)
- `evaluation_redesign/question_redesign_features.csv` (full feature base)

If expanding further:

- Join in `evaluation_redesign/problem_statement_clarity_review_targets.csv`

### 2) Anchor Question Candidates for Future Waves (exam design)

Use now:

- `longitudinal_analysis/future_wave_anchor_candidate_titles.csv` (46 title-level candidates)
- `longitudinal_analysis/future_wave_anchor_candidate_questions.csv` (question-level details)

### 3) Per-Student Risk Scores (student support / outreach)

Use now:

- `longitudinal_analysis/pass_through_model_scored_rows.csv`
- `longitudinal_analysis/pass_through_risk_segments.csv`

Important label:

- This predicts an exit proxy (passing + attrition mix), not pure passing.

### 4) Concept-Question Cross-Reference (curriculum design)

Use now:

- `concept_knowledge_modeling/concept_question_map.csv`
- `concept_knowledge_modeling/concept_mastery_overall.csv`
- `concept_knowledge_modeling/concept_mastery_by_term.csv`

This lets curriculum designers answer:

- Which questions test a concept?
- How often do students succeed on those questions?

### 5) Namespace Submission-Capture Audit (platform engineering)

Use now:

- `evaluation_redesign/submission_capture_namespace_audit.csv`
- `evaluation_redesign/submission_capture_zero_submission_namespaces.csv`
- `evaluation_redesign/submission_capture_term_wave_namespace_summary.csv`
- `evaluation_redesign/submission_capture_overall_summary.csv`

This is the direct handoff for debugging the missing submission pipeline.

## 10d. Caveats (Read Before Over-Interpreting)

These are not minor details. They change how findings should be interpreted.

### 1) Track A / Track B asymmetry (private vs public outcomes)

- Track A has submissions and private-test results.
- Track B (23 namespaces) has no submission capture, so only public `test_run` outcomes exist.
- `14.27%` of submitters have public category > private category.

Implication:

- Public-best mastery is an upper-bound proxy for absolute mastery.
- It is still useful for consistent modelling across the full population.

Evidence:

- `error_taxonomy/track_summary.csv`
- `psychometric_irt/submitter_public_vs_private_category_agreement.csv`

### 2) Progressive-filter confound (cross-term aggregates are not clean cohorts)

- Term 2 students are students who failed Term 1.
- Term 3 students are students who failed Term 2.
- Students who pass leave the system.

Implication:

- Cross-term aggregate comparisons mix learning and selection.
- Clean comparisons are:
  - within-term Wave 1 -> Wave 2 (paired students)
  - individual repeaters across terms (paired analyses)

Evidence:

- `longitudinal_analysis/within_term_wave_pair_coverage.csv`
- `longitudinal_analysis/cross_term_repeat_coverage.csv`

### 3) Timeline sampling (run-sampled, not edit-sampled)

- The timeline records `test_run` and `submission` events.
- It does not record every save/edit checkpoint.

Implication:

- Process timing metrics (for example, time to first parseable code) are measured at run checkpoints, not the exact moment the student typed the fix.

Evidence:

- Step 5 outputs in `process_analysis/` and timeline-derived features in `process_analysis/timeline_event_features*.parquet`

### 4) Construct proxy limitations (especially dictionary/file selection gaps)

Tree-sitter construct tracking does not directly cover many concept-specific actions, such as:

- dictionary literals/indexing
- `open()` calls
- string methods

Implication:

- S2 “selection gap” estimates for `Dictionary operations` and `File operations` are likely overstated when using narrow proxies (`dict_comp`, imports, etc.).

Evidence:

- `concept_knowledge_modeling/construct_focus_usage_mastery.csv`
- `concept_knowledge_modeling/s2_final_attempt_concept_decomposition_summary_aligned_proxy.csv`

### 5) Concept tagging is heuristic (coverage is complete, precision is approximate)

- Question tags were assigned using guide cues + keyword rules.
- This achieved full coverage (`251/251`), but it is not expert hand-labelling.
- The prerequisite graph compares against a proxy concept order, not the official syllabus sequence.

Implication:

- Good for screening and prioritization.
- Major curriculum changes should be validated with subject-matter review.

Evidence:

- `concept_knowledge_modeling/concept_question_map.csv`
- `concept_knowledge_modeling/concept_tagging_examples_by_concept.csv`
- `concept_knowledge_modeling/concept_prerequisite_edge_candidates.csv`

### 6) No wave-pair IRT linking (growth is not theta-linked)

- There are no usable wave-pair linked comparisons in the current data (`0` rows).

Implication:

- Growth is measured with rank-based and category-based paired methods (robust, but less precise than linked theta curves).

Evidence:

- `psychometric_irt/theta_linked_wave_pair_comparisons.csv`
- `evaluation_redesign/step7_key_metrics.csv`
- `longitudinal_analysis/step8_key_metrics.csv`

### 7) LLM analyses not yet run (deeper logic/syntax decomposition still possible)

- The deferred LLM-assisted syntax correction / wrong-output classification analyses were not run in this pipeline.

Implication:

- The `26.72%` genuine logic-failure bucket is likely still decomposable into more specific subtypes.
- Syntax recovery estimates presented here are rule-based and conservative.

Evidence (current bucketing + recovery baselines):

- `syntax_bottleneck_quantified/gating_waterfall_pct.csv`
- `process_analysis/error_recovery_by_type.csv`
- `evaluation_redesign/step7_key_metrics.csv`

## Final Synthesis (One-Page Version)

If a stakeholder remembers only five things, it should be these:

1. The exam is passable, but the biggest failure mode is logic, not syntax.
2. Students do improve a lot over time (within terms and across repeat terms).
3. The biggest process bottleneck is S2 (valid code, zero tests passing), and this is mainly a debugging/application problem.
4. The hardest persistent cohort (497 students across all three terms) is mostly a foundational syntax/no-code problem, not an S2 problem.
5. The fastest high-impact improvements are operational + design fixes: submission capture, S2-focused feedback, and test-case redesign.
