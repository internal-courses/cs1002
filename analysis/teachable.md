# Teachable Students (Process-First, Score-Free)

## Quick Summary for Administrators (ELI15)

We are **not** picking students by marks.

Instead, we ask:

- Are they engaging seriously (running tests, editing code, sticking with problems)?
- Are their mistakes **consistent and fixable** (syntax, runtime, or logic pattern)?
- Do they show concept-level struggle we can target directly?

Those students are the most teachable now. They are struggling, but in a way that coaching can realistically fix fast.

## What Changed (Compared to Score-Based Targeting)

- No exam score thresholds.
- No "who improved last time" modeling.
- No dependence on the next OPPE having similar questions.

This is built only from learning-process traces, error signatures, and concept struggle patterns.

## Decision Tree Used

```text
Start (Wave 1, with >= 3 attempt rows for reliable evidence)
|
|-- D0: Low engagement / one-shot usage?
|      (one_shot>=0.50 OR skeleton_only>=0.50 OR very low runs+edits)
|      -> D0 (not teachable-now; do re-engagement first)
|
|-- D1: Severe stuck / chaotic looping?
|      (high stuck OR thrasher+regression OR repeated parse regressions + no improvement)
|      -> D1 (not teachable-now; high-touch diagnostic coaching)
|
|-- D2: Already stable / low immediate need?
|      (dominant full-pass-like pattern OR high productive process ratio)
|      -> D2 (not priority for intensive intervention)
|
|-- Common teachable gate:
|      engaged enough + concept struggle + clear dominant error pattern + some productive behavior
|      |
|      |-- T1: Syntax-heavy failure signature -> Teachable Track 1
|      |-- T2: Runtime-heavy failure signature -> Teachable Track 2
|      |-- T3: Logic/edge-case-heavy signature -> Teachable Track 3
|      `-- otherwise -> D3 (mixed; run short diagnostic sprint first)
```

## Cohort Size (Existing Exams)

- Student-term profiles classified (Wave-1, substantive evidence): `13761`
- Teachable-now profiles (`T1+T2+T3`): `1311` (`9.5%`)

### By Term

| term | student_term_profiles | teachable_profiles | teachable_pct |
| ---- | --------------------- | ------------------ | ------------- |
| 25t1 | 5470                  | 450                | 8.2%          |
| 25t2 | 4241                  | 531                | 12.5%         |
| 25t3 | 4050                  | 330                | 8.1%          |

### Decision-Tree Path Counts (All Terms)

| decision_path_id | decision_path_name                                | teachable_now | student_term_profiles | pct_profiles |
| ---------------- | ------------------------------------------------- | ------------- | --------------------- | ------------ |
| D0               | Low Engagement / One-Shot Usage                   | No            | 911                   | 6.6%         |
| D1               | Severe Stuck / Chaotic Looping                    | No            | 992                   | 7.2%         |
| D2               | Already Stable (Low Immediate Need)               | No            | 7869                  | 57.2%        |
| D3               | Mixed / Diffuse Pattern (Needs Diagnostic Sprint) | No            | 2678                  | 19.5%        |
| T1               | Teachable: Syntax Foundations                     | Yes           | 232                   | 1.7%         |
| T2               | Teachable: Runtime Debugging                      | Yes           | 655                   | 4.8%         |
| T3               | Teachable: Logic / Edge Cases                     | Yes           | 424                   | 3.1%         |

### Decision-Tree Path Counts by Term

| decision_path_id | 25t1 | 25t2 | 25t3 | all_terms_total |
| ---------------- | ---- | ---- | ---- | --------------- |
| D0               | 417  | 271  | 223  | 911             |
| D1               | 438  | 315  | 239  | 992             |
| D2               | 3000 | 2303 | 2566 | 7869            |
| D3               | 1165 | 821  | 692  | 2678            |
| T1               | 139  | 47   | 46   | 232             |
| T2               | 163  | 316  | 176  | 655             |
| T3               | 148  | 168  | 108  | 424             |

### Teachable Path Mix

| decision_path_id | decision_path_name            | student_term_profiles | pct_of_teachable |
| ---------------- | ----------------------------- | --------------------- | ---------------- |
| T2               | Teachable: Runtime Debugging  | 655                   | 50.0%            |
| T3               | Teachable: Logic / Edge Cases | 424                   | 32.3%            |
| T1               | Teachable: Syntax Foundations | 232                   | 17.7%            |

## How to Teach Each Teachable Path

1. `T1 (Syntax Foundations)`
   - Problem pattern: non-parseable/syntax-gated errors despite active effort.
   - Intervention: subgoal-labeled code skeletons, parse-error translation guide, rapid compile-repair cycles.
2. `T2 (Runtime Debugging)`
   - Problem pattern: parseable code but runtime failures dominate.
   - Intervention: trace tables, assert/print instrumentation, hypothesis-driven debugging protocol.
3. `T3 (Logic / Edge Cases)`
   - Problem pattern: parseable/runnable, but wrong outputs and edge-case misses dominate.
   - Intervention: boundary-test design drills, input-output reasoning grids, compare expected vs actual before recoding.

## How To Teach Each Teachable Segment (ELI15 Playbooks)

### T1 — Teachable: Syntax Foundations (The Grammar Fixers)

**ELI15 Why This Works**

Their ideas are often fine, but the code is like a sentence with broken grammar. If we help them make code structurally correct quickly, they can move forward.

**A 25-Minute Intervention Recipe**

1. 5 min: read the error message in plain English and predict where it comes from.
2. 10 min: do one tiny parse-fix cycle (change 1 thing -> run -> observe).
3. 10 min: rewrite one full function from a subgoal-labeled template (inputs, loop, condition, return).

**Concrete Intervention Examples**

1. Brace-and-indent clinic: give a broken snippet and ask them to only fix structure first, not logic.
2. Error translation card: map common parser errors to one likely fix (missing colon, wrong indent, unmatched bracket).
3. Skeleton completion drill: fill only TODO blocks in order, run after each block.

**Coach Line (Use Verbatim if Useful)**

`Say: 'Let’s make the code readable by Python first. Correct structure now, smart logic next.'`

### T2 — Teachable: Runtime Debugging (The Bug Detectives)

**ELI15 Why This Works**

Their code runs, but crashes like a machine with one loose gear. They need a debugging method, not more random edits.

**A 25-Minute Intervention Recipe**

1. 5 min: name one crash and one hypothesis ('I think x is None here').
2. 10 min: trace table on paper for a tiny input (variable values each step).
3. 10 min: add 2 print/assert checks, rerun, and confirm hypothesis before editing logic.

**Concrete Intervention Examples**

1. Crash replay: reproduce one runtime error on the smallest input possible.
2. Two-print rule: before each code change, add two diagnostics that prove/disprove a hypothesis.
3. Guard-rail patterns: practice safe indexing, None checks, and dictionary-key existence checks.

**Coach Line (Use Verbatim if Useful)**

`Say: 'Don’t guess. We investigate like detectives: predict, trace, prove, then fix.'`

### T3 — Teachable: Logic / Edge Cases (The Edge-Case Engineers)

**ELI15 Why This Works**

Their code usually runs but gives wrong answers in tricky cases. They need better thinking about cases, boundaries, and hidden assumptions.

**A 25-Minute Intervention Recipe**

1. 5 min: restate problem as input -> transformation -> output in one sentence.
2. 10 min: generate 5 tests (easy, boundary, weird, empty/minimum, adversarial).
3. 10 min: compare expected vs actual for each failed case before touching code.

**Concrete Intervention Examples**

1. Boundary ladder: test min, min+1, typical, max-1, max inputs.
2. Counterexample hunt: ask 'What input would break my rule?' before submission.
3. Two-column reasoning sheet: left = what program should do, right = what code currently does.

**Coach Line (Use Verbatim if Useful)**

`Say: 'Your engine runs. Now we teach it to handle surprise roads.'`

## Real Student Examples by Decision Path

| decision_path_id | term | student_id                       | dominant_error_profile_bucket | top_concept_struggles                                                                     |
| ---------------- | ---- | -------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------- |
| D0               | 25t1 | 00ee4722182c4e3ba2b32628d12c20d7 | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                         |
| D0               | 25t1 | 01c2709b53ec4e199aa49448ab6293ee | Syntax gated                  | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         |
| D0               | 25t1 | 030e84cf594345549da87b755e9fc6c0 | No activity / skeleton        | Arithmetic / conditionals; String manipulation                                            |
| D0               | 25t1 | 0333522a8a88414ba25fac1e55af93d9 | No activity / skeleton        | Arithmetic / conditionals; Loops and iteration; Dictionary operations                     |
| D0               | 25t1 | 03ec88c245ec4928b9445d915963acaf | No activity / skeleton        | Loops and iteration; Dictionary operations; Input parsing / output formatting             |
| D0               | 25t1 | 0415cbb7a3f8491fb7e8fa1fc0330847 | No activity / skeleton        | String manipulation; Arithmetic / conditionals                                            |
| D0               | 25t1 | 056b57703e4546d8999704d7f01d7357 | No activity / skeleton        | Input parsing / output formatting; Loops and iteration; Arithmetic / conditionals         |
| D0               | 25t1 | 05755dff342e4d9393f3ca62df8eba36 | No activity / skeleton        | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         |
| D1               | 25t1 | 001daeacccd64d67948712e48e68ab03 | Syntax gated                  | String manipulation; Arithmetic / conditionals                                            |
| D1               | 25t1 | 012a533499de48f2a2710397a31dd898 | Public full pass, no submit   | String manipulation; Input parsing / output formatting; Loops and iteration               |
| D1               | 25t1 | 01d9a8e3730c4bf48bd96480acb98814 | Runtime error                 | Input parsing / output formatting; Loops and iteration; Data analysis / aggregation       |
| D1               | 25t1 | 031626a4807e485cad14aa6f2bcb7c19 | No activity / skeleton        | Arithmetic / conditionals; Data analysis / aggregation; Input parsing / output formatting |
| D1               | 25t1 | 036e6739315b434993529ced01afb126 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; Pattern printing                  |
| D1               | 25t1 | 0627a914948142c3b29e8ae7e303cf4f | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; Mathematical / algorithmic  |
| D1               | 25t1 | 062be488fe9f4db29082ea93ed7bc7d2 | Runtime error                 | Arithmetic / conditionals; Dictionary operations; List / tuple operations                 |
| D1               | 25t1 | 06974287f0144ed391135c1e3377d4cc | Runtime error                 | Input parsing / output formatting; Loops and iteration; String manipulation               |
| D2               | 25t1 | 000f6a3bc2674b73a06fb6cbbfbfdac2 | Public full pass, no submit   | Data analysis / aggregation; Loops and iteration; Dictionary operations                   |
| D2               | 25t1 | 0027af02e7364384b500f58a7095a506 | Public full pass, no submit   | Loops and iteration; Pattern printing; Arithmetic / conditionals                          |
| D2               | 25t1 | 0028f7271d574e2ea91eef45cec20299 | Public full pass, no submit   | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         |
| D2               | 25t1 | 008294cb97734d9b85450dad71b3119c | Runtime error                 | Data analysis / aggregation; File operations; Input parsing / output formatting           |
| D2               | 25t1 | 008b60ef579142299a3ebe496ea5aa5b | Public full pass, no submit   | Input parsing / output formatting; Loops and iteration; String manipulation               |
| D2               | 25t1 | 009dff0d469e4fa29e449570d72b0d4f | Public full pass, no submit   | Data analysis / aggregation; Loops and iteration; Pattern printing                        |
| D2               | 25t1 | 00d4fcfecaf247558b9bcf597fa4652a | Public full pass, no submit   | Dictionary operations; Arithmetic / conditionals; Data analysis / aggregation             |
| D2               | 25t1 | 00e4f492717d4c08828bc66a8e0e1e5e | Public full pass, no submit   | String manipulation; Arithmetic / conditionals; Input parsing / output formatting         |
| D3               | 25t1 | 00375666abf643aba8a20f64445a4a48 | Runtime error                 | Input parsing / output formatting; Loops and iteration; Pattern printing                  |
| D3               | 25t1 | 0105cc61aafb4c1dbcce38e86e052f6f | Runtime error                 | String manipulation; Arithmetic / conditionals; Input parsing / output formatting         |
| D3               | 25t1 | 015a043e278e492984f9fcc0901b616b | Wrong output - logic          | Dictionary operations; Input parsing / output formatting; Loops and iteration             |
| D3               | 25t1 | 01c64c3adf244d92868564ef9fe89cb8 | Runtime error                 | Input parsing / output formatting; Data analysis / aggregation; Dictionary operations     |
| D3               | 25t1 | 0208133cfc734912bf20afc32010f4d0 | Wrong output - edge/partial   | String manipulation; Arithmetic / conditionals; Input parsing / output formatting         |
| D3               | 25t1 | 024eabfc38fb46409edd7bd02532503c | Runtime error                 | Dictionary operations; Loops and iteration; Data analysis / aggregation                   |
| D3               | 25t1 | 026c6c465cb240589d1a7185031fadca | Runtime error                 | Input parsing / output formatting; Data analysis / aggregation; Dictionary operations     |
| D3               | 25t1 | 02d6a613492247b9bc97908a7c17be50 | Runtime error                 | Input parsing / output formatting; Data analysis / aggregation; Dictionary operations     |
| T1               | 25t1 | 026636cbeaef4ddf8463b5a6976cf65b | Syntax gated                  | Arithmetic / conditionals; Data analysis / aggregation; List / tuple operations           |
| T1               | 25t1 | 037d307920cd401b82ca7fd3309485a2 | Runtime error                 | Loops and iteration; Arithmetic / conditionals; Dictionary operations                     |
| T1               | 25t1 | 05b453720fbc448e8c42b57f511984d8 | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         |
| T1               | 25t1 | 060070303678477ea5d5c264212e5493 | Syntax gated                  | String manipulation; Arithmetic / conditionals; Input parsing / output formatting         |
| T1               | 25t1 | 06140c59f25d45fba69983d38dd9871d | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; List / tuple operations     |
| T1               | 25t1 | 0bfc16b6760f488e94af3b55266d28f1 | Syntax gated                  | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         |
| T1               | 25t1 | 0cf679817e6844059e93e2a02a846068 | Syntax gated                  | String manipulation; Input parsing / output formatting; Loops and iteration               |
| T1               | 25t1 | 0e32ebaec4a74bf2b66765ded6444c7a | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; Mathematical / algorithmic  |
| T2               | 25t1 | 02b385548cb844fb8f0579730c2464a8 | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                         |
| T2               | 25t1 | 0389027b1f324193ab8cbfc2f7273dce | Wrong output - edge/partial   | Arithmetic / conditionals; Data analysis / aggregation; Dictionary operations             |
| T2               | 25t1 | 03f2312749aa4e258c991a36d1e6b4c7 | Wrong output - logic          | Loops and iteration; File operations; Input parsing / output formatting                   |
| T2               | 25t1 | 046cb179d0454c03a0f1864a7f7ab399 | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; String manipulation         |
| T2               | 25t1 | 0861aeb8260946bea387d451ece66ceb | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                         |
| T2               | 25t1 | 0913bebe4ccd4cfc9dcfcff2dc0dfafb | Wrong output - logic          | Loops and iteration; Data analysis / aggregation; List / tuple operations                 |
| T2               | 25t1 | 09b3458d05d847bb9939a1aec8e745fc | Runtime error                 | Arithmetic / conditionals; Loops and iteration; Dictionary operations                     |
| T2               | 25t1 | 0a9209a720bd4d35b610b84449529aae | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                         |
| T3               | 25t1 | 048084806ce4418d9e8b060a7c06acb5 | Wrong output - edge/partial   | Arithmetic / conditionals; String manipulation; Input parsing / output formatting         |
| T3               | 25t1 | 056ee997e3ab4eca9ec1afac0476aac8 | Wrong output - edge/partial   | Loops and iteration; Pattern printing; Input parsing / output formatting                  |
| T3               | 25t1 | 060431bc61b745809864ca1db1efd69d | Wrong output - logic          | Arithmetic / conditionals; List / tuple operations; Loops and iteration                   |
| T3               | 25t1 | 0a106e4bebfd4c13a901cfac5ebc6336 | Wrong output - logic          | Arithmetic / conditionals; Loops and iteration; Dictionary operations                     |
| T3               | 25t1 | 0d4df39babbd4ea3b1c93c37e41ebec0 | Wrong output - edge/partial   | Arithmetic / conditionals; String manipulation                                            |
| T3               | 25t1 | 0d72317c6363465183b89ba57eb1ce01 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; Mathematical / algorithmic        |
| T3               | 25t1 | 0f4435b8c1f5499799d480b6e35d7cf6 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; String manipulation               |
| T3               | 25t1 | 10f204be91ba4ff8bbc0c686937f315e | Wrong output - edge/partial   | String manipulation; Input parsing / output formatting; Loops and iteration               |

## Detailed Teachable Examples

### T1 — Teachable: Syntax Foundations

| term | student_id                       | dominant_error_profile_bucket | top_concept_struggles                                                                     | avg_public_runs_per_attempt | avg_edits_per_attempt |
| ---- | -------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------- | --------------------------- | --------------------- |
| 25t1 | 026636cbeaef4ddf8463b5a6976cf65b | Syntax gated                  | Arithmetic / conditionals; Data analysis / aggregation; List / tuple operations           | 20.0                        | 21.0                  |
| 25t1 | 037d307920cd401b82ca7fd3309485a2 | Runtime error                 | Loops and iteration; Arithmetic / conditionals; Dictionary operations                     | 25.8                        | 46.5                  |
| 25t1 | 05b453720fbc448e8c42b57f511984d8 | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         | 19.0                        | 21.2                  |
| 25t1 | 060070303678477ea5d5c264212e5493 | Syntax gated                  | String manipulation; Arithmetic / conditionals; Input parsing / output formatting         | 6.3                         | 7.7                   |
| 25t1 | 06140c59f25d45fba69983d38dd9871d | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; List / tuple operations     | 6.2                         | 7.0                   |
| 25t1 | 0bfc16b6760f488e94af3b55266d28f1 | Syntax gated                  | Arithmetic / conditionals; Input parsing / output formatting; Loops and iteration         | 6.7                         | 8.0                   |
| 25t1 | 0cf679817e6844059e93e2a02a846068 | Syntax gated                  | String manipulation; Input parsing / output formatting; Loops and iteration               | 9.8                         | 11.4                  |
| 25t1 | 0e32ebaec4a74bf2b66765ded6444c7a | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; Mathematical / algorithmic  | 10.2                        | 11.0                  |
| 25t1 | 0ecb405bde144642a7c9dd1a0090070e | Runtime error                 | Arithmetic / conditionals; Dictionary operations; List / tuple operations                 | 7.2                         | 7.7                   |
| 25t1 | 10584803759840c49a135e6464e508b9 | Syntax gated                  | File operations; Input parsing / output formatting; List / tuple operations               | 7.2                         | 8.2                   |
| 25t1 | 127fcb6bf0344102845dc32f6ce5e41c | Runtime error                 | Arithmetic / conditionals; Data analysis / aggregation; Input parsing / output formatting | 10.2                        | 11.5                  |
| 25t1 | 13c28f53d16e4f6ba495f26cf95ca07b | Syntax gated                  | Loops and iteration; File operations; Input parsing / output formatting                   | 8.2                         | 8.5                   |

### T2 — Teachable: Runtime Debugging

| term | student_id                       | dominant_error_profile_bucket | top_concept_struggles                                                                   | avg_public_runs_per_attempt | avg_edits_per_attempt |
| ---- | -------------------------------- | ----------------------------- | --------------------------------------------------------------------------------------- | --------------------------- | --------------------- |
| 25t1 | 02b385548cb844fb8f0579730c2464a8 | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                       | 8.2                         | 8.2                   |
| 25t1 | 0389027b1f324193ab8cbfc2f7273dce | Wrong output - edge/partial   | Arithmetic / conditionals; Data analysis / aggregation; Dictionary operations           | 11.7                        | 12.5                  |
| 25t1 | 03f2312749aa4e258c991a36d1e6b4c7 | Wrong output - logic          | Loops and iteration; File operations; Input parsing / output formatting                 | 12.0                        | 12.8                  |
| 25t1 | 046cb179d0454c03a0f1864a7f7ab399 | Runtime error                 | Arithmetic / conditionals; Input parsing / output formatting; String manipulation       | 13.0                        | 13.5                  |
| 25t1 | 0861aeb8260946bea387d451ece66ceb | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                       | 9.3                         | 9.5                   |
| 25t1 | 0913bebe4ccd4cfc9dcfcff2dc0dfafb | Wrong output - logic          | Loops and iteration; Data analysis / aggregation; List / tuple operations               | 19.7                        | 20.5                  |
| 25t1 | 09b3458d05d847bb9939a1aec8e745fc | Runtime error                 | Arithmetic / conditionals; Loops and iteration; Dictionary operations                   | 4.7                         | 5.9                   |
| 25t1 | 0a9209a720bd4d35b610b84449529aae | Runtime error                 | Loops and iteration; Data analysis / aggregation; File operations                       | 6.8                         | 7.8                   |
| 25t1 | 0be7370dbecb455e864bab0e64c1a295 | Runtime error                 | Data analysis / aggregation; Input parsing / output formatting; List / tuple operations | 12.0                        | 13.5                  |
| 25t1 | 0db11306a0644c9e8b0c3731f869b93c | Wrong output - logic          | Arithmetic / conditionals; Loops and iteration; Input parsing / output formatting       | 8.0                         | 8.7                   |
| 25t1 | 10123e56ffa54db6a7739f9f1470f7f8 | Runtime error                 | Input parsing / output formatting; Loops and iteration; Data analysis / aggregation     | 13.3                        | 15.2                  |
| 25t1 | 13db869b549f406b97a9e8666af0967f | Runtime error                 | String manipulation; Arithmetic / conditionals                                          | 14.5                        | 15.8                  |

### T3 — Teachable: Logic / Edge Cases

| term | student_id                       | dominant_error_profile_bucket | top_concept_struggles                                                              | avg_public_runs_per_attempt | avg_edits_per_attempt |
| ---- | -------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------- | --------------------------- | --------------------- |
| 25t1 | 048084806ce4418d9e8b060a7c06acb5 | Wrong output - edge/partial   | Arithmetic / conditionals; String manipulation; Input parsing / output formatting  | 10.2                        | 11.0                  |
| 25t1 | 056ee997e3ab4eca9ec1afac0476aac8 | Wrong output - edge/partial   | Loops and iteration; Pattern printing; Input parsing / output formatting           | 30.0                        | 32.8                  |
| 25t1 | 060431bc61b745809864ca1db1efd69d | Wrong output - logic          | Arithmetic / conditionals; List / tuple operations; Loops and iteration            | 14.0                        | 14.5                  |
| 25t1 | 0a106e4bebfd4c13a901cfac5ebc6336 | Wrong output - logic          | Arithmetic / conditionals; Loops and iteration; Dictionary operations              | 12.0                        | 12.8                  |
| 25t1 | 0d4df39babbd4ea3b1c93c37e41ebec0 | Wrong output - edge/partial   | Arithmetic / conditionals; String manipulation                                     | 17.5                        | 18.2                  |
| 25t1 | 0d72317c6363465183b89ba57eb1ce01 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; Mathematical / algorithmic | 21.6                        | 24.8                  |
| 25t1 | 0f4435b8c1f5499799d480b6e35d7cf6 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; String manipulation        | 15.3                        | 19.0                  |
| 25t1 | 10f204be91ba4ff8bbc0c686937f315e | Wrong output - edge/partial   | String manipulation; Input parsing / output formatting; Loops and iteration        | 34.3                        | 51.3                  |
| 25t1 | 13614e822e674d5fb48d06595f968372 | Wrong output - edge/partial   | Input parsing / output formatting; Loops and iteration; Pattern printing           | 28.5                        | 30.8                  |
| 25t1 | 17655cc095664c998ba0f8a417252faf | Wrong output - edge/partial   | String manipulation; Arithmetic / conditionals                                     | 15.2                        | 16.2                  |
| 25t1 | 1778b477b4eb43d6a29f892c0011fb11 | Wrong output - edge/partial   | Loops and iteration; Pattern printing; Input parsing / output formatting           | 18.8                        | 20.2                  |
| 25t1 | 17a5eae9efee4bdf8f547a1a75af3179 | Wrong output - edge/partial   | Loops and iteration; Input parsing / output formatting; List / tuple operations    | 7.7                         | 8.7                   |

## Why This Works Better for the Next OPPE

Because this model is about **how students learn and fail**, not about specific past questions:

- Engagement style (one-shot vs persistent)
- Error mechanism (syntax vs runtime vs logic)
- Concept struggle profile

Those transfer across question variants much better than raw marks.

## Caveats

- This identifies "teachable-now" for targeted support, not guaranteed outcomes.
- Students in `D0` and `D1` still matter; they usually need different intervention intensity first.
- Thresholds should be recalibrated each term if platform behavior shifts significantly.

## Reproducibility

Run:

```bash
uv run analysis/teachable.py
```

Outputs:

- `analysis/teachable.csv`
- `analysis/teachable.md`

## References

1. [Robins, Rountree, and Rountree (2003), Learning and Teaching Programming: A Review and Discussion.](https://doi.org/10.1076/csed.13.2.137.14200)
2. [Jadud and Dorn (2015), Aggregate Compilation Behavior: Findings and Implications for Introductory Programming Pedagogy.](https://doi.org/10.1145/2787622.2787718)
3. [Schantong et al. (2024), Toward Finding and Supporting Struggling Students in a Programming Course with an Early Warning System.](https://www.diva-portal.org/smash/get/diva2:1762835/FULLTEXT01.pdf)
4. [Margulieux et al. (2020), Subgoal-Labeled Worked Examples in Learning to Program.](https://link.springer.com/content/pdf/10.1007/s10648-020-09582-9.pdf)
5. [Wisniewski, Zierer, and Hattie (2020), The Power of Feedback Revisited (meta-analysis).](https://pmc.ncbi.nlm.nih.gov/articles/PMC7726232/)
6. [Freeman et al. (2014), Active Learning Increases Student Performance in STEM.](https://www.pnas.org/doi/10.1073/pnas.1319030111)
7. [Nickow, Oreopoulos, and Quan (2020), The Impressive Effects of Tutoring on PreK-12 Learning.](https://www.nber.org/papers/w27476)
8. [UNESCO (2023), Guidance for Generative AI in Education and Research.](https://unesdoc.unesco.org/ark:/48223/pf0000386693)
9. [Prather et al. (2024), The Widening Gap: The Benefits and Harms of Generative AI for Novice Programmers.](https://arxiv.org/abs/2408.14238)
