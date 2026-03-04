# No-Private Submissions Report

## Quick Summary for Administrators (ELI15)

Think of the coding system as having two checkpoints:

- **Public checks**: practice checks students run while working.
- **Private checks**: hidden final checks used for official grading.

In this report, a “public-only” attempt means the student ran public checks for a question but has **no private submission event** for that same question.

### What This Means

- We can confirm the student was active on that question, but we cannot confirm private-evaluator performance for that question.
- A high public score without a private submission may indicate: workflow confusion, no final submit action, or namespace-level capture issues.
- So this metric is both a **learning-behavior signal** and a potential **platform instrumentation signal**.

### Simple Findings

- Public-only student-question rows: **108,860** out of **151,778** (71.7%).
- Unique students represented: **12,682**.
- Namespaces represented: **35**.
- Namespaces with zero private submissions at namespace level: **23** of **35**.
- Public score buckets on public-only rows: **100%: 43.8%**, **0%: 43.5%**, **Partial: 12.6%**.

### Recommended Investigations / Actions

1. **Audit private-submission capture first**
   - Validate evaluator routing, namespace config, and ingestion for namespaces with zero private submissions.
2. **Track funnel drop-offs**
   - Monitor `public test_run -> private submission` conversion by namespace and wave.
3. **Improve student workflow prompts**
   - Show explicit warning when a student leaves with public runs but no private submission.
4. **Teach public vs private test meaning explicitly**
   - Reinforce that passing public tests is not equivalent to final graded success.
5. **Separate platform risk from learning risk**
   - Do not interpret public-only patterns as student performance alone in zero-private namespaces.

Generated: `2026-03-03 23:36:23 UTC`

## Expert Framing (What We Checked First)

- **Event semantics check:** In this dataset, there are no `event_type='submission' AND evaluation_type='public'` events. Public-side attempts are logged as public `test_run` events.
- **Denominator integrity:** We report both student-question rows and unique students; these answer different questions.
- **Namespace instrumentation check:** We separate namespaces with zero private submissions at all (Track B-like) from mixed namespaces.
- **Behavior vs platform:** A student can be public-only for one question but still submit privately on others in the same namespace.
- **Public score caveat:** Public-best performance can overstate true mastery when private tests are absent.

## Definitions Used

- **Public-only student-question row (in CSV):** `public_test_run_events > 0` and `private_submission_events = 0`.
- **Only-public student in namespace:** Student has at least one public test run in that namespace and **zero** private submissions across all questions in that namespace.
- **Question combo:** one `(student_id, namespace, problem_id)` row.

## Headline Numbers

- Total student-question rows in timeline: **151,778**
- Total unique students in timeline: **13,623**
- Total namespaces: **35**
- Total namespace-question combinations: **251**
- Public `submission` events (strict): **0**
- Public-only rows exported to `analysis/no-private-submissions.csv`: **108,860**
- Unique students represented in public-only rows: **12,682**
- Namespaces represented in public-only rows: **35**
- Namespace-question combinations represented in public-only rows: **251**

## Direct Clarification (Yes) + Real Examples

Yes. This report **does** include students who, for a specific `(namespace, question)`, ran public checks but made **no private submission** for that question.
In this dataset, public-side activity is logged as `test_run` (not `submission`), so “public submissions” here means public test-run attempts.

- Count of such student-question rows: **108,860** out of **151,778** total rows (71.7%).
- A student may still have private submissions on *other* questions; the condition is evaluated per `(student, namespace, question)`.
- Important nuance: `private_submission_events = 0` can still coexist with private `test_run` events; the report condition is specifically about missing private **submission** events.

### Example 1: `39306bba7119454aa9c6a928ecc7cd06` on `ns_25t1_py11_1/2`

- Namespace type: **Zero-private namespace (Track B-like)**
- Question title: **Check is even or divisible by 5 Write a function is_even_or_divisible_by_5 that takes an integer as input and return True if it is even or is divisible by 5 else False. NOTE: This**
- Public test runs: **12**
- Private test runs: **1**
- Private submissions: **0**
- Best public outcome: **4/4** (100.0%)

Submission history (event timeline for this exact student-question):

| step | timestamp_utc | event | eval_type | result_summary | score | tests_passed | tests_total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-02-26 13:14:07 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 2 | 2025-02-26 13:14:30 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 3 | 2025-02-26 13:16:34 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 4 | 2025-02-26 13:20:43 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 5 | 2025-02-26 13:21:29 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 6 | 2025-02-26 13:22:40 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 7 | 2025-02-26 13:23:23 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 8 | 2025-02-26 13:25:49 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 9 | 2025-02-26 13:31:45 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 10 | 2025-02-26 13:35:20 | test_run | public | Runtime Error | 0.00 | 0 | 4 |
| 11 | 2025-02-26 14:09:04 | test_run | public | All Cases Passed | 0.00 | 4 | 4 |
| 12 | 2025-02-26 14:09:19 | test_run | private | All Cases Passed | 100.00 | 3 | 3 |
| 13 | 2025-02-26 14:09:19 | test_run | public | All Cases Passed | 0.00 | 4 | 4 |

### Example 2: `a3ef4ae1a4394525bbb9ee1fad2ffdf6` on `ns_25t2_py13_1/5`

- Namespace type: **Mixed namespace (Track A-like)**
- Question title: **Check If a Number is a Decreasing 4-Digit Number**
- Public test runs: **12**
- Private test runs: **0**
- Private submissions: **0**
- Best public outcome: **3/3** (100.0%)

Submission history (event timeline for this exact student-question):

| step | timestamp_utc | event | eval_type | result_summary | score | tests_passed | tests_total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-07-20 04:10:44 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 2 | 2025-07-20 04:12:07 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 3 | 2025-07-20 04:12:13 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 4 | 2025-07-20 04:15:06 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 5 | 2025-07-20 04:15:49 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 6 | 2025-07-20 04:16:53 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 7 | 2025-07-20 04:17:03 | test_run | public | Wrong Answer | 0.00 | 1 | 3 |
| 8 | 2025-07-20 04:22:34 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 9 | 2025-07-20 04:22:51 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 10 | 2025-07-20 04:23:13 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 11 | 2025-07-20 04:23:37 | test_run | public | Wrong Answer | 0.00 | 1 | 3 |
| 12 | 2025-07-20 04:24:27 | test_run | public | All Cases Passed | 0.00 | 3 | 3 |

### Example 3: `9582853226e64afba043d85c7f29b265` on `ns_25t1_py11_1/7`

- Namespace type: **Zero-private namespace (Track B-like)**
- Question title: **Vowel count of words Write a program that takes a string and counts the number of vowels in every word. The program should then print each word followed by the count of vowels in p**
- Public test runs: **12**
- Private test runs: **12**
- Private submissions: **0**
- Best public outcome: **0/3** (0.0%)

Submission history (event timeline for this exact student-question):

| step | timestamp_utc | event | eval_type | result_summary | score | tests_passed | tests_total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-02-26 13:47:02 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 2 | 2025-02-26 13:47:02 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 3 | 2025-02-26 14:10:37 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 4 | 2025-02-26 14:10:37 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 5 | 2025-02-26 14:13:25 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 6 | 2025-02-26 14:13:25 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 7 | 2025-02-26 14:14:00 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 8 | 2025-02-26 14:14:00 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 9 | 2025-02-26 14:14:33 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 10 | 2025-02-26 14:14:33 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 11 | 2025-02-26 14:15:16 | test_run | private | Wrong Answer | 0.00 | 0 | 3 |
| 12 | 2025-02-26 14:15:16 | test_run | public | Wrong Answer | 0.00 | 0 | 3 |
| 13 | 2025-02-26 14:23:45 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 14 | 2025-02-26 14:23:45 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 15 | 2025-02-26 14:25:30 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 16 | 2025-02-26 14:25:30 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 17 | 2025-02-26 14:27:38 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 18 | 2025-02-26 14:27:38 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 19 | 2025-02-26 14:27:53 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 20 | 2025-02-26 14:27:53 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 21 | 2025-02-26 14:28:58 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 22 | 2025-02-26 14:28:58 | test_run | public | Runtime Error | 0.00 | 0 | 3 |
| 23 | 2025-02-26 14:29:22 | test_run | private | Runtime Error | 0.00 | 0 | 3 |
| 24 | 2025-02-26 14:29:22 | test_run | public | Runtime Error | 0.00 | 0 | 3 |

## Per-Namespace: Students with Only Public Activity and No Private Submission

Interpretation: `students_only_public_in_namespace / total_students` answers your question directly at namespace level.

| namespace | namespace_type | students_only_public_in_namespace | total_students | public_only_student_pct | students_with_at_least_one_public_only_question | public_only_question_rows | example_student_ids |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ns_25t3_py24_1 | Zero-private namespace (Track B-like) | 1,545 | 1,545 | 100.0% | 1,545 | 8,953 | 00272c0a446846018d861ab440a19ab1, 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e, 005cdb4e62d7410eaabb20aaabfa8da3, 00705b22bca84c0ba9a4e1104a7874ef |
| ns_25t1_py23_2 | Zero-private namespace (Track B-like) | 1,174 | 1,174 | 100.0% | 1,174 | 6,436 | 00375666abf643aba8a20f64445a4a48, 011c89b2c45f4e089aec3f19079673c3, 015a53ae217f4be4a74634e2d853c8b9, 017b58f1dad14446b4b7a55c77af8d4b, 01c6fb9f4c7f4f56855d39d188f2c1fa |
| ns_25t1_py22_2 | Zero-private namespace (Track B-like) | 1,045 | 1,045 | 100.0% | 1,045 | 5,872 | 0028f7271d574e2ea91eef45cec20299, 00d08b8a7c94416081942ff19612fa9f, 00d4fcfecaf247558b9bcf597fa4652a, 0120aee9f49b4bf19f7fdbf6219ad729, 02c81b5e276c4a9fa9256a9d087bdcea |
| ns_25t3_py23 | Zero-private namespace (Track B-like) | 1,018 | 1,018 | 100.0% | 1,018 | 6,075 | 000d9c38dd86457fb38770b073189328, 001fb59fe66b48de8f0d08c185b636d9, 003d1d1009304f978bbdded9669f409d, 017d98001da240f39ed841b5bf4a4df0, 017fe3c61cfc4ed28c66ce983807caa8 |
| ns_25t1_py21_2 | Zero-private namespace (Track B-like) | 982 | 982 | 100.0% | 982 | 5,208 | 000f6a3bc2674b73a06fb6cbbfbfdac2, 008b60ef579142299a3ebe496ea5aa5b, 009dff0d469e4fa29e449570d72b0d4f, 0145d4230dce4a9fbe8b77cf81f31017, 01789faf04c24abfbe229d6f072817e8 |
| ns_25t1_py14_1 | Zero-private namespace (Track B-like) | 938 | 938 | 100.0% | 938 | 5,053 | 00375666abf643aba8a20f64445a4a48, 00d4fcfecaf247558b9bcf597fa4652a, 01c64c3adf244d92868564ef9fe89cb8, 01c6fb9f4c7f4f56855d39d188f2c1fa, 01dbcb135488457e82d219783d19da7e |
| ns_25t1_py23_1 | Zero-private namespace (Track B-like) | 906 | 906 | 100.0% | 906 | 4,585 | 0027af02e7364384b500f58a7095a506, 01c64c3adf244d92868564ef9fe89cb8, 01f84e1375514f3bbd6ad51470d7040d, 02253a066ff74cf6a7fd068443d32ba5, 0250845130644e0da54b2e7742cd21d3 |
| ns_25t1_py11_2 | Zero-private namespace (Track B-like) | 870 | 870 | 100.0% | 870 | 4,843 | 015a043e278e492984f9fcc0901b616b, 019ca311e1ce4607869f6fc112cfaffa, 01d9a8e3730c4bf48bd96480acb98814, 01f5d01ce525463e81ede1571c50e463, 02c377f86ea44c9ca662688ef44e2c9b |
| ns_25t1_py21_1 | Zero-private namespace (Track B-like) | 864 | 864 | 100.0% | 864 | 4,416 | 00791f51550546cca57e71e99019f78c, 0105cc61aafb4c1dbcce38e86e052f6f, 0122c7158ee64a1b8e772bac44e13798, 01a757f9a5bb4afe951d89b952fec26d, 027f0818c1c3432cb0ab50db1fcdaa54 |
| ns_25t3_py14_2 | Zero-private namespace (Track B-like) | 797 | 797 | 100.0% | 797 | 4,431 | 0111254dc8094516ae694be9052d9477, 01741f4c2616463394b317d1ea8afb87, 022ca49c92ea4f2080ac07dd2ccd1d55, 025d23eecbc948148997ec21eff4e6d9, 027f0818c1c3432cb0ab50db1fcdaa54 |
| ns_25t3_py13_2 | Zero-private namespace (Track B-like) | 787 | 787 | 100.0% | 787 | 4,336 | 000d9c38dd86457fb38770b073189328, 003d1d1009304f978bbdded9669f409d, 00705b22bca84c0ba9a4e1104a7874ef, 008059fb091a41d8a7c61bad0c25d08b, 00b3ce564d3e47a6b7d0410737e123f8 |
| ns_25t1_py14_2 | Zero-private namespace (Track B-like) | 774 | 774 | 100.0% | 774 | 4,061 | 0027af02e7364384b500f58a7095a506, 011c89b2c45f4e089aec3f19079673c3, 015a53ae217f4be4a74634e2d853c8b9, 01f84e1375514f3bbd6ad51470d7040d, 0250845130644e0da54b2e7742cd21d3 |
| ns_25t1_py11_1 | Zero-private namespace (Track B-like) | 746 | 746 | 100.0% | 746 | 3,860 | 000f6a3bc2674b73a06fb6cbbfbfdac2, 0122c7158ee64a1b8e772bac44e13798, 01779d06b9204efca1d5dc864451c73d, 01789faf04c24abfbe229d6f072817e8, 024eabfc38fb46409edd7bd02532503c |
| ns_25t1_py12_1 | Zero-private namespace (Track B-like) | 713 | 713 | 100.0% | 713 | 3,922 | 008b60ef579142299a3ebe496ea5aa5b, 01c2709b53ec4e199aa49448ab6293ee, 0208133cfc734912bf20afc32010f4d0, 030e84cf594345549da87b755e9fc6c0, 0391b2e9729249de90ef7ea641fd81d1 |
| ns_25t1_py13_2 | Zero-private namespace (Track B-like) | 689 | 689 | 100.0% | 689 | 3,884 | 009dff0d469e4fa29e449570d72b0d4f, 00ee4722182c4e3ba2b32628d12c20d7, 0120aee9f49b4bf19f7fdbf6219ad729, 02c81b5e276c4a9fa9256a9d087bdcea, 030db63796fa483d9fc1386cf09456c6 |
| ns_25t2_py23_1 | Zero-private namespace (Track B-like) | 676 | 676 | 100.0% | 676 | 3,519 | 00272c0a446846018d861ab440a19ab1, 008294cb97734d9b85450dad71b3119c, 00ff4d61054544a4aaca3a93d291ef88, 016d6e449be74a65a052b7f5e65740df, 018d12e10e374ebe97a30f0112e0b52d |
| ns_25t3_py21 | Zero-private namespace (Track B-like) | 649 | 649 | 100.0% | 649 | 3,125 | 002e13f116d34ed8a6dbc733ba1ccd45, 0036f031ba8e475fafd17a2e0c4992e3, 00c50c3a3ab8485e9d857a0a8d9907bc, 016d6e449be74a65a052b7f5e65740df, 024a0dc633cf44bc807fddc3e9da0abe |
| ns_25t2_py23_2 | Zero-private namespace (Track B-like) | 628 | 628 | 100.0% | 628 | 3,312 | 002e13f116d34ed8a6dbc733ba1ccd45, 00c4bb1ac9a148d184fca496e5a8c16e, 00e17dd6b9ef421f882541e44c886632, 0101ff45b51f46f7bd0ac789beca57aa, 01d0c86286084142825c5b5618c8c1eb |
| ns_25t1_py22_1 | Zero-private namespace (Track B-like) | 593 | 593 | 100.0% | 593 | 3,012 | 0005d9e8b6ab4447aca45128a3c62093, 001daeacccd64d67948712e48e68ab03, 00ee4722182c4e3ba2b32628d12c20d7, 015a043e278e492984f9fcc0901b616b, 01779d06b9204efca1d5dc864451c73d |
| ns_25t1_py12_2 | Zero-private namespace (Track B-like) | 585 | 585 | 100.0% | 585 | 3,130 | 001daeacccd64d67948712e48e68ab03, 0028f7271d574e2ea91eef45cec20299, 00e4f492717d4c08828bc66a8e0e1e5e, 0105cc61aafb4c1dbcce38e86e052f6f, 012a533499de48f2a2710397a31dd898 |
| ns_25t1_py13_1 | Zero-private namespace (Track B-like) | 525 | 525 | 100.0% | 525 | 2,794 | 008294cb97734d9b85450dad71b3119c, 02b385548cb844fb8f0579730c2464a8, 02dd1556d2db4edf88fb0303df9e11e5, 02e86a7f259143ac9e3ea795619f886a, 038a593f2042406898a777c6093728a2 |
| ns_25t3_py12 | Zero-private namespace (Track B-like) | 410 | 410 | 100.0% | 410 | 2,255 | 001fb59fe66b48de8f0d08c185b636d9, 00d08b8a7c94416081942ff19612fa9f, 01365cb9e2ca4c78b3c91ddf86e5a484, 0196ea23bdd74403b0bdaeed92a147a7, 02590b3ef25e472ca30823c51fa6cb58 |
| ns_25t1_py_15_exe | Zero-private namespace (Track B-like) | 115 | 115 | 100.0% | 115 | 666 | 0208133cfc734912bf20afc32010f4d0, 0a6a70a1c00c4560952e7166a70459b4, 0c3df956e3ff4ebfb85eca8e6cbb3805, 0dbdfb37c8bc4225b7bf82a358fea1b7, 0f25b4160f8940179fc8cdf4d037fd04 |
| ns_25t2_py13_1 | Mixed namespace (Track A-like) | 96 | 1,006 | 9.5% | 645 | 1,334 | 019382df09244891a4d365eb6ecfb7b3, 026636cbeaef4ddf8463b5a6976cf65b, 0296ff908f604a068d31b9d9b7fb212d, 031626a4807e485cad14aa6f2bcb7c19, 035c905984344bcc84cf1add04765d4a |
| ns_25t2_py13_2 | Mixed namespace (Track A-like) | 76 | 1,040 | 7.3% | 593 | 1,268 | 0033bed7a3eb482093410b9910437fb2, 00375666abf643aba8a20f64445a4a48, 00e91c89480d4d928c1ffb9dbb45a5e6, 00ff4d61054544a4aaca3a93d291ef88, 0101ff45b51f46f7bd0ac789beca57aa |
| ns_25t3_py11 | Mixed namespace (Track A-like) | 48 | 760 | 6.3% | 446 | 810 | 002e13f116d34ed8a6dbc733ba1ccd45, 008f24528b0a4f4cb589dc4838be9a08, 0296c67603094554982eb3ab51a58b45, 02e54d0580ee400587a4892f7d1ba2a4, 02e8a5b91c024fb7b259374f25b3fabb |
| ns_25t2_py14_1 | Mixed namespace (Track A-like) | 47 | 1,094 | 4.3% | 651 | 1,224 | 0005d9e8b6ab4447aca45128a3c62093, 00ff4e287cdf41cbbc073c40e7a891e6, 0112f6908f584bdeb6a5d74e9adaa8c1, 015e8128d943495b9e5861c557e87b44, 019ca311e1ce4607869f6fc112cfaffa |
| ns_25t2_py11_1 | Mixed namespace (Track A-like) | 47 | 700 | 6.7% | 486 | 1,092 | 00272c0a446846018d861ab440a19ab1, 01e404611a9542edb000e6eeb94b0797, 03ccde0aef7841e1afcd2a90796e2d7a, 0487d3451c70432b9a15b1d93255f97a, 0499f8ca8a0a489a9389c0e73ec85356 |
| ns_25t3_py14_1 | Mixed namespace (Track A-like) | 41 | 767 | 5.3% | 439 | 838 | 0013db5ccd914982ad9803f59a6d38bd, 016e8052a91f4ae1b36e9a01fc2bb634, 017d98001da240f39ed841b5bf4a4df0, 019382df09244891a4d365eb6ecfb7b3, 01d2b92d37bb43e2a38355d954baa84c |
| ns_25t2_py21_1 | Mixed namespace (Track A-like) | 37 | 820 | 4.5% | 471 | 786 | 00111c859d754e6d9d921d26bf1682f0, 0036f031ba8e475fafd17a2e0c4992e3, 00791f51550546cca57e71e99019f78c, 01e404611a9542edb000e6eeb94b0797, 026636cbeaef4ddf8463b5a6976cf65b |
| ns_25t2_py21_2 | Mixed namespace (Track A-like) | 33 | 824 | 4.0% | 450 | 729 | 0033bed7a3eb482093410b9910437fb2, 015e8128d943495b9e5861c557e87b44, 02c81b5e276c4a9fa9256a9d087bdcea, 030e84cf594345549da87b755e9fc6c0, 0329fa996bc24e7fbde06873eb84822a |
| ns_25t2_py12_1 | Mixed namespace (Track A-like) | 33 | 747 | 4.4% | 428 | 850 | 0228695a76e34891b6858fcf7b60d2a8, 038a9af131044e13bf444cdf0dfdf8d3, 03ec88c245ec4928b9445d915963acaf, 03f3160d657c48689c854a130d2d4bce, 052cc618d53b4caeb5acb2b72a2fd80c |
| ns_25t3_py13_1 | Mixed namespace (Track A-like) | 27 | 807 | 3.3% | 503 | 971 | 012d1734e4f64314a776db3db2036f10, 01f87330e3a04e1c859d2c512f43ec62, 024c0205ba6d4aefa88901a18be9d8e2, 0286173341b84502bf98a02365f32a3c, 03376d9737a542f0b1a48445700e5496 |
| ns_25t2_py22_1 | Mixed namespace (Track A-like) | 19 | 1,052 | 1.8% | 486 | 732 | 00705b22bca84c0ba9a4e1104a7874ef, 0112f6908f584bdeb6a5d74e9adaa8c1, 015cf199b4324eaeaf1f8974c972bc34, 01d2071e87324d34baa6e2f2422867a9, 02316474f027467483ce2dd9e7c04b83 |
| ns_25t3_py22 | Mixed namespace (Track A-like) | 19 | 548 | 3.5% | 276 | 478 | 01741f4c2616463394b317d1ea8afb87, 01f9c4f1eec749f3bb85db8612f2f72c, 047edf8deb4d48cba15e24a20015a6a3, 05e051c237ee4a3d85c35b8292ef433c, 067f9db7707d403f9bd7610ae56ed43f |

## Distribution: Number of Public-Only Question Combos per Student

| public_only_questions_per_student | student_count | pct_of_affected_students | example_student_ids |
| --- | --- | --- | --- |
| 1 | 730 | 5.8% | 008f24528b0a4f4cb589dc4838be9a08, 00e91c89480d4d928c1ffb9dbb45a5e6, 012d1734e4f64314a776db3db2036f10, 015cf199b4324eaeaf1f8974c972bc34, 01f9c4f1eec749f3bb85db8612f2f72c |
| 2 | 613 | 4.8% | 0033bed7a3eb482093410b9910437fb2, 005cdb4e62d7410eaabb20aaabfa8da3, 01d2071e87324d34baa6e2f2422867a9, 02172d4bda0a4d0c8fb449413f4beffb, 02e54d0580ee400587a4892f7d1ba2a4 |
| 3 | 492 | 3.9% | 00111c859d754e6d9d921d26bf1682f0, 00ff4e287cdf41cbbc073c40e7a891e6, 015e8128d943495b9e5861c557e87b44, 01741f4c2616463394b317d1ea8afb87, 01e404611a9542edb000e6eeb94b0797 |
| 4 | 601 | 4.7% | 0005d9e8b6ab4447aca45128a3c62093, 0013db5ccd914982ad9803f59a6d38bd, 00b3ce564d3e47a6b7d0410737e123f8, 00c50c3a3ab8485e9d857a0a8d9907bc, 0112f6908f584bdeb6a5d74e9adaa8c1 |
| 5 | 834 | 6.6% | 002a3d18dd3a4e46a798b8d9dbdd85c0, 0036f031ba8e475fafd17a2e0c4992e3, 00791f51550546cca57e71e99019f78c, 00c4bb1ac9a148d184fca496e5a8c16e, 014be548fd104f00a7b4397ced11c7c2 |
| 6 | 1,033 | 8.1% | 012a533499de48f2a2710397a31dd898, 01365cb9e2ca4c78b3c91ddf86e5a484, 01ec1b735e8147638a01475222020a3f, 01f0fce08e2d4120bee95742740f4622, 0208e47146f64b4c9e49dc33a9daf654 |
| 7 | 1,734 | 13.7% | 003be96e78504e7aa4030f6857c2a85e, 00e17dd6b9ef421f882541e44c886632, 00e4f492717d4c08828bc66a8e0e1e5e, 0101ff45b51f46f7bd0ac789beca57aa, 01036e9b5ae440e58f37b079dbe1a642 |
| 8 | 744 | 5.9% | 002e13f116d34ed8a6dbc733ba1ccd45, 016e8052a91f4ae1b36e9a01fc2bb634, 01c2709b53ec4e199aa49448ab6293ee, 01fb55a2208c4cd58aa70b2e7e12fda6, 02dd1556d2db4edf88fb0303df9e11e5 |
| 9 | 726 | 5.7% | 0028f7271d574e2ea91eef45cec20299, 016d6e449be74a65a052b7f5e65740df, 01d0c86286084142825c5b5618c8c1eb, 02513462bc7544fbab76018300ebd9b3, 0277558e490c4f08b49273da2c1b51d8 |
| 10 | 699 | 5.5% | 0027af02e7364384b500f58a7095a506, 00375666abf643aba8a20f64445a4a48, 003d1d1009304f978bbdded9669f409d, 008294cb97734d9b85450dad71b3119c, 015a043e278e492984f9fcc0901b616b |
| 11 | 820 | 6.5% | 001daeacccd64d67948712e48e68ab03, 00ff4d61054544a4aaca3a93d291ef88, 015a53ae217f4be4a74634e2d853c8b9, 017fe3c61cfc4ed28c66ce983807caa8, 019382df09244891a4d365eb6ecfb7b3 |
| 12 | 814 | 6.4% | 00272c0a446846018d861ab440a19ab1, 008059fb091a41d8a7c61bad0c25d08b, 00ee4722182c4e3ba2b32628d12c20d7, 0105cc61aafb4c1dbcce38e86e052f6f, 0122c7158ee64a1b8e772bac44e13798 |
| 13 | 845 | 6.7% | 000f6a3bc2674b73a06fb6cbbfbfdac2, 001fb59fe66b48de8f0d08c185b636d9, 01779d06b9204efca1d5dc864451c73d, 01c6fb9f4c7f4f56855d39d188f2c1fa, 01d9a8e3730c4bf48bd96480acb98814 |
| 14 | 1,255 | 9.9% | 000d9c38dd86457fb38770b073189328, 008b60ef579142299a3ebe496ea5aa5b, 009dff0d469e4fa29e449570d72b0d4f, 00d4fcfecaf247558b9bcf597fa4652a, 011c89b2c45f4e089aec3f19079673c3 |
| 15 | 140 | 1.1% | 00705b22bca84c0ba9a4e1104a7874ef, 048d10f7570543c3b761b2e8fcf0eae6, 0524c03b5d7a40f3b2a26331879ddb9d, 056b57703e4546d8999704d7f01d7357, 058872f5d6fd4fae96b0dabf5ab7e9a8 |
| 16 | 117 | 0.9% | 04b03b860c4f4a78992cf1c3eeed3e6c, 056ee997e3ab4eca9ec1afac0476aac8, 071916a46d4b46caaba2d43514e62619, 0719ee00284649e39e57b9346be6a5b9, 129bc9639f714383950b395140ff5ea0 |
| 17 | 106 | 0.8% | 060070303678477ea5d5c264212e5493, 067f9db7707d403f9bd7610ae56ed43f, 08be4d94938246c0be9ac7bde2323a23, 0b81ae7d99744b4b8b2fd2fdcd2b885e, 0bba8ccc6fe0438d8f049dc33bee64d2 |
| 18 | 93 | 0.7% | 0c3df956e3ff4ebfb85eca8e6cbb3805, 0e13f5cd8e274e31aab5edd5399a2ecf, 0f25b4160f8940179fc8cdf4d037fd04, 152ce44f7fe64539a6165f2f8b870c73, 185beec804854ae4be5e04e91ff0936e |
| 19 | 63 | 0.5% | 00d08b8a7c94416081942ff19612fa9f, 04d8523b9ce844169aee5d78b4a538be, 05e051c237ee4a3d85c35b8292ef433c, 0d6d0d7e18e8435e8bdebac817580eba, 14bf78c6bd5c4f6bb39457d97ccb7497 |
| 20 | 59 | 0.5% | 030e84cf594345549da87b755e9fc6c0, 0da3068accb9422f8fe095961db2da4f, 1022c5e6385c41d1aec6d665035b648b, 188c560d44f84b778584608730cff977, 18b6cedbe9924bb2b977c2cb5a3c962c |
| 21 | 50 | 0.4% | 06f6fb4ea76144ef91df6ceec5f264a8, 085acd28043e4c3da9bbb664efa0993e, 10549a585f4e4831aa9615446132bc95, 141e193129c14e82ab7f4a0444263d76, 15becd62dc0b420aaa1d4d60fca8fb9f |
| 22 | 24 | 0.2% | 0a2fa98467c1487f88fc7bc70d77f2db, 0bfc16b6760f488e94af3b55266d28f1, 14c53ad5e16f4105b93989e611677ddb, 2e668ccc084541b3a2b2e50b59594800, 30da85848eff4977b450422c5b231370 |
| 23 | 25 | 0.2% | 02253a066ff74cf6a7fd068443d32ba5, 0898f3ad366444c6bed154220b0b28af, 09742913d9cf42669edc4087fc0d6f8b, 0af4af464b3345bc80496b47bb14e7f2, 0de4eeab644945289d20baa208fe52c2 |
| 24 | 14 | 0.1% | 0be95b2a0ecb411d8f81880b5a1edc67, 0cdcac83911c406493f7b268e0b33167, 2752a4ea70ac49fabb4755c54ddfa282, 3e0892e6a1644a0092d6922b7fc618d7, 41044422fe9e475bb21490f75d202f60 |
| 25 | 15 | 0.1% | 0a106e4bebfd4c13a901cfac5ebc6336, 0a6a70a1c00c4560952e7166a70459b4, 1979ae9ce0664bf7bc9a1f1adc402004, 1a512731c58d4a01b0144d8d46c559a6, 38c833f0c219405ba964620dc64e92e6 |
| 26 | 16 | 0.1% | 225bb41045fc45a68a02d24caa73bd5c, 541574bb3a414f8a92c675a8f6ba0c3f, 66eac69aa8084d8a95bc4f0a56f1542b, 707050cff2554eedb269a57a73f79ca8, 87ebea0ea5e045309a6aa10489454af4 |
| 27 | 5 | 0.0% | 244d828e54e242359aae156eeae84eb9, 529409565bab4c1aa5eaa3e361bec40e, 8441c3b982914b779cf15f66e9857474, db66b8344c7540ea86f0833fa1097bbc, e74ecf0c2872436891a8479306de19f6 |
| 28 | 7 | 0.1% | 09b3458d05d847bb9939a1aec8e745fc, 269ff4358f1b4087921afca90920248b, 26c9d04df1354c25a00c0db32ee1bc92, 4dcec4e19e92418289c7dcc966cedb29, 5961c49c7e3143faa165aca78ca0701a |
| 29 | 4 | 0.0% | 2f3f0f74fdf54a6d831b6764229eec05, 6c79c636f4d64076b08943ea267650af, 795bf9975a9b48ffb4472fad78b342f8, cae7b92dcb864439bc0a4e0c7c04ffd4 |
| 30 | 2 | 0.0% | 771fda89d5634e13b7d173e8b6008152, b662c966981e4e6d966f564bb2fa3b04 |
| 33 | 1 | 0.0% | 29130243df3a433e8bbd00f0c645bc61 |
| 54 | 1 | 0.0% | f14645d55837451d94a7afc5615ca1b7 |

## Public Test Performance on Public-Only Rows

| score_bucket | rows | pct_of_public_only_rows |
| --- | --- | --- |
| 100% | 47,731 | 43.8% |
| 0% | 47,390 | 43.5% |
| Partial (0-100) | 13,737 | 12.6% |
| Missing public score | 2 | 0.0% |

## Namespace Class Comparison (Useful Operational Signal)

| namespace_type | public_only_rows | unique_students | namespaces | rows_with_100_public | pct_rows_with_100_public |
| --- | --- | --- | --- | --- | --- |
| Mixed namespace (Track A-like) | 11,112 | 4,645 | 12 | 70 | 0.6% |
| Zero-private namespace (Track B-like) | 97,748 | 11,107 | 23 | 47,661 | 48.8% |

## Top Question Combos by Public-Only Volume

| namespace | problem_id | question_title | public_only_rows | unique_students | pct_rows_with_100_public | example_student_ids |
| --- | --- | --- | --- | --- | --- | --- |
| ns_25t3_py24_1 | 5 | Mask all characters of a password except the first two and last two | 1,516 | 1,516 | 75.4% | 00272c0a446846018d861ab440a19ab1, 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e |
| ns_25t3_py24_1 | 7 | Middle element from list | 1,452 | 1,452 | 79.3% | 00272c0a446846018d861ab440a19ab1, 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e |
| ns_25t3_py24_1 | 9 | Count Strings With More Vowels Than Consonants | 1,447 | 1,447 | 59.7% | 00272c0a446846018d861ab440a19ab1, 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e |
| ns_25t3_py24_1 | 6 | Find the length of concatenated dictionary values | 1,438 | 1,438 | 74.7% | 00272c0a446846018d861ab440a19ab1, 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e |
| ns_25t3_py24_1 | 10 | Sum of Digit Sums from Words | 1,308 | 1,308 | 69.7% | 002a3d18dd3a4e46a798b8d9dbdd85c0, 003be96e78504e7aa4030f6857c2a85e, 00705b22bca84c0ba9a4e1104a7874ef |
| ns_25t1_py23_2 | 5 | Extract Border Elements from a List Write a function extract_border_elements that takes a list of integers as input and returns a new list containing only the first and last elemen | 1,160 | 1,160 | 79.6% | 00375666abf643aba8a20f64445a4a48, 011c89b2c45f4e089aec3f19079673c3, 015a53ae217f4be4a74634e2d853c8b9 |
| ns_25t1_py23_2 | 9 | Words with Consecutive Identical Letters Write a function words_with_consecutive_letters(words) that takes a list of words and returns a list of words that contain at least one pai | 1,101 | 1,101 | 61.4% | 00375666abf643aba8a20f64445a4a48, 011c89b2c45f4e089aec3f19079673c3, 015a53ae217f4be4a74634e2d853c8b9 |
| ns_25t3_py24_1 | 12 | Job Scheduling Analysis | 1,093 | 1,093 | 15.4% | 003be96e78504e7aa4030f6857c2a85e, 00705b22bca84c0ba9a4e1104a7874ef, 008059fb091a41d8a7c61bad0c25d08b |
| ns_25t1_py23_2 | 6 | Absolute Time Difference Between Two Times Write a function absolute_time_difference that takes two time strings in the format HH:MM as input and returns the absolute time differen | 1,053 | 1,053 | 47.5% | 00375666abf643aba8a20f64445a4a48, 011c89b2c45f4e089aec3f19079673c3, 015a53ae217f4be4a74634e2d853c8b9 |
| ns_25t1_py22_2 | 5 | Middle element from list Write a function extract_middle_elements(lst:list) that takes a list of integers and returns a new list containing only the middle element if the list has  | 1,027 | 1,027 | 73.4% | 0028f7271d574e2ea91eef45cec20299, 00d08b8a7c94416081942ff19612fa9f, 00d4fcfecaf247558b9bcf597fa4652a |
| ns_25t1_py22_2 | 7 | Check if both numbers have the same sign Write a function same_sign that checks whether two given numbers have the same sign. Consider three cases: Both numbers are strictly positi | 1,009 | 1,009 | 81.2% | 0028f7271d574e2ea91eef45cec20299, 00d08b8a7c94416081942ff19612fa9f, 00d4fcfecaf247558b9bcf597fa4652a |
| ns_25t3_py23 | 7 | Absolute difference between sum and sum of the squares. | 990 | 990 | 92.6% | 000d9c38dd86457fb38770b073189328, 001fb59fe66b48de8f0d08c185b636d9, 003d1d1009304f978bbdded9669f409d |
| ns_25t3_py23 | 5 | Swap Signs of Two Integers | 979 | 979 | 74.9% | 000d9c38dd86457fb38770b073189328, 001fb59fe66b48de8f0d08c185b636d9, 003d1d1009304f978bbdded9669f409d |
| ns_25t3_py23 | 6 | Check First and Last Element are Same Integer (Type-Insensitive) | 977 | 977 | 65.6% | 000d9c38dd86457fb38770b073189328, 001fb59fe66b48de8f0d08c185b636d9, 003d1d1009304f978bbdded9669f409d |
| ns_25t3_py23 | 9 | Spy Number - Advanced | 977 | 977 | 75.9% | 000d9c38dd86457fb38770b073189328, 001fb59fe66b48de8f0d08c185b636d9, 003d1d1009304f978bbdded9669f409d |
| ns_25t1_py21_2 | 5 | Check if Either of Two Numbers is a Multiple of the Other Write a function is_multiple that takes two integers as input and returns True if either number is a multiple of the other | 970 | 970 | 86.9% | 000f6a3bc2674b73a06fb6cbbfbfdac2, 008b60ef579142299a3ebe496ea5aa5b, 009dff0d469e4fa29e449570d72b0d4f |
| ns_25t1_py22_2 | 9 | Check Palindrome - Advanced Write a function is_palindrome that takes a string as input and returns True if the string reads the same forward and backward considering only the alph | 966 | 966 | 55.3% | 0028f7271d574e2ea91eef45cec20299, 00d08b8a7c94416081942ff19612fa9f, 00d4fcfecaf247558b9bcf597fa4652a |
| ns_25t1_py21_2 | 6 | Check if a String Starts and Ends with the Same Vowel (Case Insensitive) Write a function starts_and_ends_with_same_vowel that takes a string as input and returns True if the strin | 949 | 949 | 69.3% | 000f6a3bc2674b73a06fb6cbbfbfdac2, 008b60ef579142299a3ebe496ea5aa5b, 009dff0d469e4fa29e449570d72b0d4f |
| ns_25t1_py21_2 | 9 | Count Strings with Length Divisible by Either 3 or 5 Write a function count_strings_length_divisible_by_3_or_5(strings) that takes a list of strings and counts how many strings hav | 933 | 933 | 44.6% | 000f6a3bc2674b73a06fb6cbbfbfdac2, 008b60ef579142299a3ebe496ea5aa5b, 009dff0d469e4fa29e449570d72b0d4f |
| ns_25t1_py14_1 | 3 | Check if 2D Vectors are Orthogonal Write a function are_orthogonal that takes two tuples t1 and t2 as input. Each tuple represents a 2D vector with two elements (x, y). The functio | 904 | 904 | 73.5% | 00375666abf643aba8a20f64445a4a48, 00d4fcfecaf247558b9bcf597fa4652a, 01c64c3adf244d92868564ef9fe89cb8 |

## Caveats

- This report is event-log based; if private submissions were never captured for a namespace, behavior and instrumentation are confounded.
- `100%` here refers to **best public test-run** coverage on visible test cases, not private-evaluator success.
- Student IDs are anonymized hashes, shown only as examples for traceability.

