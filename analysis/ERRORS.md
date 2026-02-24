# Error Analysis Index (Question Clusters)

This file indexes question clusters for targeted error-analysis writeups.

Definitions used here:

- `final_submitters`: unique student-question rows with a final evaluated private submission (latest `submission` event)
- `non_full`: final submitters whose latest private submission score is `< 100`
- Clusters are built by normalized prompt/template/test fingerprints, plus a strict near-duplicate fallback within same-title questions.

- Questions indexed: `251`
- Question clusters: `163`
- Multi-variant clusters (`>1` question): `76`

<!-- BEGIN OVERALL_INSIGHTS -->

## Overall Insights So Far (ELI15)

So far, detailed error-pattern reports exist for `60/163` clusters. That already covers `38683/42918` final submissions (`90.1%`) and `16402/19538` non-full finals (`83.9%`).

### What Students Commonly Get Wrong (In Plain English)

- Many wrong answers are not random mistakes. The code often solves a simpler version of the problem than the real one.
- Students frequently overfit to the sample tests: hard-coded outputs, sample-specific constants, fixed positions, or assumptions like “there will be exactly 2 indices.”
- A lot of failures are contract mistakes: printing instead of returning, returning the wrong type (`list` vs `set`), reading `input()` inside function questions, or changing exact spacing/newlines.
- Hidden tests often expose edge cases students skip: duplicates, multi-digit values, out-of-range indices, ties, case sensitivity, zero/empty inputs, and “do this across all lines” vs “per line.”
- Control-flow/state bugs are everywhere: early `return` inside loops, resetting counters at the wrong time, and stopping after the first match instead of checking everything.
- In multi-function/data problems, students often mix up data shapes (treat a list like a dict), use sample globals (`data`, `sales`) instead of parameters, or leave some helpers as `...`.

### The Underlying Pattern (What Experts Notice)

Experts usually see these as **spec-reading and invariants** problems, not just “loop problems” or “if-statement problems.” The big question is: “What must always stay true?”

- If the task says “exact formatting,” spaces/newlines are part of the answer, not decoration.
- If the task says “unique pairs,” duplicates and order rules matter as much as the sum rule.
- If a function question expects a return value, printing is invisible to the tests.
- If there are multiple helpers, hidden tests usually check that each helper works independently and that later helpers use the same data model correctly.

In short: beginners often focus on the visible example. Experts focus on the **full rule set** and the **edge conditions that break shortcuts**.

### What an Expert Would Check First (Before Writing Code)

- What is the exact input/output contract? (Read from stdin vs function args, print vs return, exact type, exact formatting)
- What are the boundary cases? (empty, one item, duplicates, zero, multi-digit, max/min)
- What must be preserved? (order, line breaks, casing, original text, all items vs only first `n`)
- What hidden assumptions might be false? (“exactly two values”, “single-digit indices”, “only lowercase”, “no ties”)
- Where can control flow stop too early? (inside loops, inside first `if`, inside first non-match)
- Where can state get reset by accident? (per line vs global counter, per iteration accumulators)

### Implications for Problem and Test Case Design

- Public tests should teach the format, but hidden tests must intentionally break common shortcuts (multi-digit inputs, duplicates, ties, out-of-range values, mixed case, extra lines, etc.).
- Add at least one hidden test for each common “sample overfit” path (hard-coded sample output, fixed count assumptions, exact sample strings).
- Separate feedback categories help more than just “Wrong Answer”: e.g., “printed instead of returned”, “wrong output type”, “stops early in loop”, “formatting mismatch”, “sample-specific solution”.
- Multi-function tasks should include hidden tests that isolate each helper and also integration tests, so students can see which part is broken.
- If exact formatting matters, say it very plainly and include examples that show spaces/newlines are semantically important.

### Planning for the AI Era (Why This Matters More Now)

- AI can generate code that looks polished but is brittle. It often passes samples while silently assuming a narrower problem than the prompt really defines.
- That means educators should design tests for **robustness**, not just correctness on obvious cases.
- Students also need a “trust but verify” habit: run edge cases, check return types, and compare against the exact spec, not just the sample output.
- The error-pattern reports in this project are useful here: they can power targeted feedback like “Your code likely hard-coded sample behavior” or “You are resetting state each line.”
- Instructionally, this suggests teaching debugging checklists and spec-reading strategies earlier, because those skills now matter as much as syntax memorization.

<!-- END OVERALL_INSIGHTS -->

## Cluster List

### C001 - Deinterleave Even and Odd Indices in String

- Analysis file: [`analysis/ERRORS-cluster-c001-deinterleave-even-and-odd-indices-in-string-fdfb29fc.md`](ERRORS-cluster-c001-deinterleave-even-and-odd-indices-in-string-fdfb29fc.md)
- Variants in cluster: `4`
- Total final submitters across variants: `578`
- Total non-full finals across variants: `108`
- Canonical variant: `ns_25t2_py12_1/6`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: incorrect deinterleaving logic (general logic failure), hard-codes sample outputs instead of deinterleaving the input string generically, and uses s.index(char) while iterating characters, so duplicate characters get the wrong parity/index. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/6` (canonical) |              578 |      108 | `3/3`            | Exact duplicate problem JSON |

### C002 - Shuffle a Three Word Sentence

- Analysis file: [`analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md`](ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md)
- Variants in cluster: `4`
- Total final submitters across variants: `518`
- Total non-full finals across variants: `212`
- Canonical variant: `ns_25t3_py13_1/7`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: hard-codes sample outputs/sentences instead of using the provided order tuple generically, joins shuffled words without spaces (''.join(...)) instead of returning a space-separated sentence, and incorrect word-order reconstruction or output formatting in the 3-word shuffle task. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/7` (canonical) |              518 |      212 | `3/3`            | Exact duplicate problem JSON |

### C003 - Middle element from list

- Analysis file: [`analysis/ERRORS-cluster-c003-middle-element-from-list-5165f1b7.md`](ERRORS-cluster-c003-middle-element-from-list-5165f1b7.md)
- Variants in cluster: `4`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/5`
- Variant relationship: exact semantic fingerprint match with minor metadata differences

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C004 - Check is even or divisible by 5

- Analysis file: [`analysis/ERRORS-cluster-c004-check-is-even-or-divisible-by-5-64840085.md`](ERRORS-cluster-c004-check-is-even-or-divisible-by-5-64840085.md)
- Variants in cluster: `3`
- Total final submitters across variants: `698`
- Total non-full finals across variants: `77`
- Canonical variant: `ns_25t2_py12_1/5`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: partially correct boolean logic, but false cases are mishandled, incorrect even/divisible-by-5 logic (general logic failure), and uses division (/ or //) instead of modulus (%) in the divisibility test. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/5` (canonical) |              698 |       77 | `4/3`            | Exact duplicate problem JSON |

### C005 - Counts unique even and odd numbers

- Analysis file: [`analysis/ERRORS-cluster-c005-counts-unique-even-and-odd-numbers-44480259.md`](ERRORS-cluster-c005-counts-unique-even-and-odd-numbers-44480259.md)
- Variants in cluster: `3`
- Total final submitters across variants: `556`
- Total non-full finals across variants: `174`
- Canonical variant: `ns_25t2_py12_1/9`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: incorrect unique even/odd counting logic, uses floor-division (// 2) as a parity test instead of modulo (% 2), and reads input() inside function-type question. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/9` (canonical) |              556 |      174 | `4/2`            | Exact duplicate problem JSON |

### C006 - Make dictionary from elements in index of lists

- Analysis file: [`analysis/ERRORS-cluster-c006-make-dictionary-from-elements-in-index-of-lists-f61a14ad.md`](ERRORS-cluster-c006-make-dictionary-from-elements-in-index-of-lists-f61a14ad.md)
- Variants in cluster: `3`
- Total final submitters across variants: `474`
- Total non-full finals across variants: `124`
- Canonical variant: `ns_25t2_py12_1/7`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: incorrect dictionary construction, builds the dictionary with invalid syntax/types, and negative-index handling bug: solution works for positive indices but treats valid negative indices incorrectly. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/7` (canonical) |              474 |      124 | `3/2`            | Exact duplicate problem JSON |

### C007 - Vowel count of words

- Analysis file: [`analysis/ERRORS-cluster-c007-vowel-count-of-words-c48b5d4a.md`](ERRORS-cluster-c007-vowel-count-of-words-c48b5d4a.md)
- Variants in cluster: `3`
- Total final submitters across variants: `398`
- Total non-full finals across variants: `219`
- Canonical variant: `ns_25t2_py12_1/10`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: incorrect per-word vowel counting or output formatting (general logic failure), treats the entire input as one string and counts/prints globally instead of producing per-word outputs, and hard-codes sample outputs instead of formatting arbitrary input words with vowel counts. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/10` (canonical) |              398 |      219 | `3/3`            | Exact duplicate problem JSON |

### C008 - Pattern Printing - W Pattern

- Analysis file: [`analysis/ERRORS-cluster-c008-pattern-printing-w-pattern-35071c74.md`](ERRORS-cluster-c008-pattern-printing-w-pattern-35071c74.md)
- Variants in cluster: `3`
- Total final submitters across variants: `367`
- Total non-full finals across variants: `180`
- Canonical variant: `ns_25t2_py12_1/13`
- Variant relationship: exact semantic fingerprint match with minor metadata differences
- Key error summary (analyzed): Common mistakes: incorrect W-pattern printing logic, row-spacing arithmetic is incorrect, and hard-codes small sample sizes (n=1/2/3/...) with if/elif branches instead of a general pattern loop. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/13` (canonical) |              367 |      180 | `4/3`            | Exact duplicate problem JSON |

### C009 - Student Score Filter

- Analysis file: [`analysis/ERRORS-cluster-c009-student-score-filter-27cb112b.md`](ERRORS-cluster-c009-student-score-filter-27cb112b.md)
- Variants in cluster: `3`
- Total final submitters across variants: `295`
- Total non-full finals across variants: `223`
- Canonical variant: `ns_25t2_py12_1/12`
- Variant relationship: exact semantic fingerprint match with minor metadata differences

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py12_1/12` (canonical) |              295 |      223 | `4/4`            | Exact duplicate problem JSON |

### C010 - Compute Electricity Bill

- Analysis file: [`analysis/ERRORS-cluster-c010-compute-electricity-bill-ef6eeec2.md`](ERRORS-cluster-c010-compute-electricity-bill-ef6eeec2.md)
- Variants in cluster: `2`
- Total final submitters across variants: `1498`
- Total non-full finals across variants: `226`
- Canonical variant: `ns_25t2_py21_2/14`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: uses separate if slabs, low-slab-only mistake, and middle slab formula missing fixed +150 charge. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/14`             |              738 |      110 | `3/3`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/14` (canonical) |              760 |      116 | `3/3`            | Exact duplicate problem JSON |

### C011 - is_reverse_combined_palindrome

- Analysis file: [`analysis/ERRORS-cluster-c011-is-reverse-combined-palindrome-302c96ec.md`](ERRORS-cluster-c011-is-reverse-combined-palindrome-302c96ec.md)
- Variants in cluster: `2`
- Total final submitters across variants: `1368`
- Total non-full finals across variants: `297`
- Canonical variant: `ns_25t2_py21_2/16`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect construction/check of reversed+combined string, partial/incorrect reverse+combine logic, and checks palindrome on one string (or wrong intermediate) instead of reversed(s1)+s2. Also many syntax/empty code, unfinished template code, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/15`             |              673 |      150 | `3/3`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/16` (canonical) |              695 |      147 | `3/3`            | Exact duplicate problem JSON |

### C012 - Check for Arithmetic Progression

- Analysis file: [`analysis/ERRORS-cluster-c012-check-for-arithmetic-progression-f66de18e.md`](ERRORS-cluster-c012-check-for-arithmetic-progression-f66de18e.md)
- Variants in cluster: `2`
- Total final submitters across variants: `1365`
- Total non-full finals across variants: `507`
- Canonical variant: `ns_25t2_py21_2/20`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: returns inside loop before completing full check/computation, incorrect AP logic (general logic failure), and partially correct AP check. Also many runtime crashes, syntax/empty code, and unfinished template code.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/17`             |              677 |      264 | `3/3`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/20` (canonical) |              688 |      243 | `3/3`            | Exact duplicate problem JSON |

### C013 - Pangram Check

- Analysis file: [`analysis/ERRORS-cluster-c013-pangram-check-f0d5ae7d.md`](ERRORS-cluster-c013-pangram-check-f0d5ae7d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `1331`
- Total non-full finals across variants: `665`
- Canonical variant: `ns_25t2_py21_2/18`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: returns inside the alphabet-check loop, hard-codes sample pangram strings/examples instead of checking letter coverage, and skeleton placeholder ... left in function.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/16`             |              656 |      337 | `3/3`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/18` (canonical) |              675 |      328 | `3/3`            | Exact duplicate problem JSON |

### C014 - Book Data Analysis

- Analysis file: [`analysis/ERRORS-cluster-c014-book-data-analysis-6446788a.md`](ERRORS-cluster-c014-book-data-analysis-6446788a.md)
- Variants in cluster: `2`
- Total final submitters across variants: `803`
- Total non-full finals across variants: `447`
- Canonical variant: `ns_25t2_py21_2/24`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: broad multi-function failure, returns from inside the loop, so only the first/partial language counts are produced, and implements earlier helper functions but leaves count_by_language / total_pages_in_genre_lang incomplete. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/19`             |              383 |      212 | `5/5`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/24` (canonical) |              420 |      235 | `5/5`            | Exact duplicate problem JSON |

### C015 - Double if Even Else Square

- Analysis file: [`analysis/ERRORS-cluster-c015-double-if-even-else-square-e8edaceb.md`](ERRORS-cluster-c015-double-if-even-else-square-e8edaceb.md)
- Variants in cluster: `2`
- Total final submitters across variants: `754`
- Total non-full finals across variants: `79`
- Canonical variant: `ns_25t3_py13_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-codes sample values/examples instead of using the input parameter n, reads input() inside function-type question, and uses division (n/2 == 0) instead of parity test (n % 2 == 0). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/9` (canonical) |              754 |       79 | `3/3`            | Exact duplicate problem JSON |

### C016 - Check Divisibility by Last Two Digits

- Analysis file: [`analysis/ERRORS-cluster-c016-check-divisibility-by-last-two-digits-24422e8a.md`](ERRORS-cluster-c016-check-divisibility-by-last-two-digits-24422e8a.md)
- Variants in cluster: `2`
- Total final submitters across variants: `683`
- Total non-full finals across variants: `277`
- Canonical variant: `ns_25t3_py14_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect divisibility-by-last-two-digits logic (general logic failure), returns after checking only part of the digits/conditions, and partially correct divisibility logic with operator/condition bug. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/7` (canonical) |              683 |      277 | `3/3`            | Exact duplicate problem JSON |

### C017 - Rotate Matrix Clockwise 90 degree

- Analysis file: [`analysis/ERRORS-cluster-c017-rotate-matrix-clockwise-90-degree-7c9efc07.md`](ERRORS-cluster-c017-rotate-matrix-clockwise-90-degree-7c9efc07.md)
- Variants in cluster: `2`
- Total final submitters across variants: `593`
- Total non-full finals across variants: `454`
- Canonical variant: `ns_25t2_py21_2/22`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-coded/fixed-size sample-matrix output, not general m x n rotation, likely correct rotation logic, but prints rows with print(*row), and empty final submission. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/18`             |              276 |      213 | `3/4`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/22` (canonical) |              317 |      241 | `3/4`            | Exact duplicate problem JSON |

### C018 - Separate Outer Characters

- Analysis file: [`analysis/ERRORS-cluster-c018-separate-outer-characters-1da11c5d.md`](ERRORS-cluster-c018-separate-outer-characters-1da11c5d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `589`
- Total non-full finals across variants: `130`
- Canonical variant: `ns_25t3_py14_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect outer/inner slicing or wrong return shape (general logic failure), hard-codes the sample output ('proing', 'gramm') instead of computing from s and n, and reads input() inside function-type question. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/9` (canonical) |              589 |      130 | `3/3`            | Exact duplicate problem JSON |

### C019 - Number of Unique letters present in exactly one of the two strings

- Analysis file: [`analysis/ERRORS-cluster-c019-number-of-unique-letters-present-in-exactly-one-of-the-two-s-24da3668.md`](ERRORS-cluster-c019-number-of-unique-letters-present-in-exactly-one-of-the-two-s-24da3668.md)
- Variants in cluster: `2`
- Total final submitters across variants: `587`
- Total non-full finals across variants: `326`
- Canonical variant: `ns_25t3_py13_1/8`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect unique-letter counting logic, counts exclusive letters but forgets uniqueness, and uses set symmetric-difference logic without case normalization. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/8` (canonical) |              587 |      326 | `5/3`            | Exact duplicate problem JSON |

### C020 - File Content Zig-Zag Shift

- Analysis file: [`analysis/ERRORS-cluster-c020-file-content-zig-zag-shift-246cf030.md`](ERRORS-cluster-c020-file-content-zig-zag-shift-246cf030.md)
- Variants in cluster: `2`
- Total final submitters across variants: `586`
- Total non-full finals across variants: `356`
- Canonical variant: `ns_25t2_py21_1/20`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect pattern-generation logic for the evaluated task, solves a different file-based zig-zag-spacing question (filename I/O) instead of the evaluator’s alternate-number-sequence triangle task, and hard-codes outputs for specific values of n (sample-case branching) instead of generating the pattern. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py21_1/20` (canonical) |              363 |      220 | `4/3`            | Exact duplicate problem JSON |
| `ns_25t2_py21_2/26`             |              223 |      136 | `4/3`            | Exact duplicate problem JSON |

### C021 - Bold Nth Character

- Analysis file: [`analysis/ERRORS-cluster-c021-bold-nth-character-9b53f1c8.md`](ERRORS-cluster-c021-bold-nth-character-9b53f1c8.md)
- Variants in cluster: `2`
- Total final submitters across variants: `581`
- Total non-full finals across variants: `210`
- Canonical variant: `ns_25t3_py14_1/8`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: only validates n and returns the original string; never inserts the <b>...</b> tags, incorrect nth-character bolding logic (general logic failure), and returns from inside a loop while building the bolded string. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/8` (canonical) |              581 |      210 | `5/3`            | Exact duplicate problem JSON |

### C022 - Find Characters Appearing More Than Once

- Analysis file: [`analysis/ERRORS-cluster-c022-find-characters-appearing-more-than-once-a831cf60.md`](ERRORS-cluster-c022-find-characters-appearing-more-than-once-a831cf60.md)
- Variants in cluster: `2`
- Total final submitters across variants: `564`
- Total non-full finals across variants: `317`
- Canonical variant: `ns_25t3_py13_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect repeated-character detection logic, uses split()/word-based logic, but the task is about repeated characters within a single string, and appends a character every time count(ch) > 1, so repeated characters appear multiple times in the output list. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/10` (canonical) |              564 |      317 | `3/3`            | Exact duplicate problem JSON |

### C023 - Replace Spaces with Index

- Analysis file: [`analysis/ERRORS-cluster-c023-replace-spaces-with-index-770df649.md`](ERRORS-cluster-c023-replace-spaces-with-index-770df649.md)
- Variants in cluster: `2`
- Total final submitters across variants: `548`
- Total non-full finals across variants: `239`
- Canonical variant: `ns_25t3_py14_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect space-replacement logic, uses str.replace(...) for all spaces at once, so per-space index substitutions are incorrect, and uses integer indices directly in string replacement/concatenation (str(i) cast missing). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/10` (canonical) |              548 |      239 | `3/3`            | Exact duplicate problem JSON |

### C024 - Count Word Types by Length and Palindrome Property

- Analysis file: [`analysis/ERRORS-cluster-c024-count-word-types-by-length-and-palindrome-property-4209805b.md`](ERRORS-cluster-c024-count-word-types-by-length-and-palindrome-property-4209805b.md)
- Variants in cluster: `2`
- Total final submitters across variants: `426`
- Total non-full finals across variants: `272`
- Canonical variant: `ns_25t3_py13_1/11`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: uses split(' ') instead of split(), so hidden trailing-space lines create empty-string tokens that are miscounted, incorrect multi-line word-category counting logic, and reads only one text line after n and ignores the remaining lines. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/11` (canonical) |              426 |      272 | `3/5`            | Exact duplicate problem JSON |

### C025 - Add Pairs with Carry Over Above 100

- Analysis file: [`analysis/ERRORS-cluster-c025-add-pairs-with-carry-over-above-100-a8a5b094.md`](ERRORS-cluster-c025-add-pairs-with-carry-over-above-100-a8a5b094.md)
- Variants in cluster: `2`
- Total final submitters across variants: `395`
- Total non-full finals across variants: `214`
- Canonical variant: `ns_25t3_py14_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect carry-simulation program logic, reads each pair value on separate lines (a=int(input()); b=int(input())), causing input parsing failure on a b lines, and prints constant sample output lines instead of reading input pairs and simulating carry. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/13` (canonical) |              395 |      214 | `3/3`            | Exact duplicate problem JSON |

### C026 - Sales Records Analysis

- Analysis file: [`analysis/ERRORS-cluster-c026-sales-records-analysis-21cf7171.md`](ERRORS-cluster-c026-sales-records-analysis-21cf7171.md)
- Variants in cluster: `2`
- Total final submitters across variants: `347`
- Total non-full finals across variants: `308`
- Canonical variant: `ns_25t3_py14_1/11`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: leaves template placeholders (...) in multiple required sales-analysis helper functions, early helpers are mostly correct, but region_with_max_sales(...) / steady_revenue_products(...) logic fails hidden cases, and leaves the template placeholder ... in steady_revenue_products(...). Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/11` (canonical) |              347 |      308 | `4/5`            | Exact duplicate problem JSON |

### C027 - Sum Numbers Inside Square Brackets

- Analysis file: [`analysis/ERRORS-cluster-c027-sum-numbers-inside-square-brackets-17dae48d.md`](ERRORS-cluster-c027-sum-numbers-inside-square-brackets-17dae48d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `283`
- Total non-full finals across variants: `191`
- Canonical variant: `ns_25t3_py14_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py14_1/12` (canonical) |              283 |      191 | `3/3`            | Exact duplicate problem JSON |

### C028 - Step Triangle Pattern

- Analysis file: [`analysis/ERRORS-cluster-c028-step-triangle-pattern-eb072b0d.md`](ERRORS-cluster-c028-step-triangle-pattern-eb072b0d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `262`
- Total non-full finals across variants: `221`
- Canonical variant: `ns_25t3_py13_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/13` (canonical) |              262 |      221 | `5/5`            | Exact duplicate problem JSON |

### C029 - Word Filter by Criteria

- Analysis file: [`analysis/ERRORS-cluster-c029-word-filter-by-criteria-1898345f.md`](ERRORS-cluster-c029-word-filter-by-criteria-1898345f.md)
- Variants in cluster: `2`
- Total final submitters across variants: `242`
- Total non-full finals across variants: `205`
- Canonical variant: `ns_25t3_py13_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py13_1/12` (canonical) |              242 |      205 | `5/5`            | Exact duplicate problem JSON |

### C030 - Abbreviate Initials And Sort

- Analysis file: [`analysis/ERRORS-cluster-c030-abbreviate-initials-and-sort-b42ed064.md`](ERRORS-cluster-c030-abbreviate-initials-and-sort-b42ed064.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C031 - Absolute Time Difference Between Two Times

- Analysis file: [`analysis/ERRORS-cluster-c031-absolute-time-difference-between-two-times-41aa8712.md`](ERRORS-cluster-c031-absolute-time-difference-between-two-times-41aa8712.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C032 - Add average key with absolute difference value (in-place)

- Analysis file: [`analysis/ERRORS-cluster-c032-add-average-key-with-absolute-difference-value-in-place-e5ecbf0e.md`](ERRORS-cluster-c032-add-average-key-with-absolute-difference-value-in-place-e5ecbf0e.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/16`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C033 - Analyze Sentences

- Analysis file: [`analysis/ERRORS-cluster-c033-analyze-sentences-98d01f7a.md`](ERRORS-cluster-c033-analyze-sentences-98d01f7a.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C034 - Book Reading List Data Analysis

- Analysis file: [`analysis/ERRORS-cluster-c034-book-reading-list-data-analysis-803c943b.md`](ERRORS-cluster-c034-book-reading-list-data-analysis-803c943b.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/19`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C035 - Capitalize nth Character

- Analysis file: [`analysis/ERRORS-cluster-c035-capitalize-nth-character-255f88d2.md`](ERRORS-cluster-c035-capitalize-nth-character-255f88d2.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/3`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C036 - Check Even Number and Second Last Digit is Two

- Analysis file: [`analysis/ERRORS-cluster-c036-check-even-number-and-second-last-digit-is-two-42d997a8.md`](ERRORS-cluster-c036-check-even-number-and-second-last-digit-is-two-42d997a8.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/2`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C038 - Check If a String has No Vowels in Even Indices

- Analysis file: [`analysis/ERRORS-cluster-c038-check-if-a-string-has-no-vowels-in-even-indices-49e5b447.md`](ERRORS-cluster-c038-check-if-a-string-has-no-vowels-in-even-indices-49e5b447.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C043 - Check Palindrome - Advanced

- Analysis file: [`analysis/ERRORS-cluster-c043-check-palindrome-advanced-570d1a94.md`](ERRORS-cluster-c043-check-palindrome-advanced-570d1a94.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C037 - Check if 2D Vectors are Orthogonal

- Analysis file: [`analysis/ERRORS-cluster-c037-check-if-2d-vectors-are-orthogonal-e5be055b.md`](ERRORS-cluster-c037-check-if-2d-vectors-are-orthogonal-e5be055b.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/3`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C042 - Check if Either of Two Numbers is a Multiple of the Other

- Analysis file: [`analysis/ERRORS-cluster-c042-check-if-either-of-two-numbers-is-a-multiple-of-the-other-e57b99d8.md`](ERRORS-cluster-c042-check-if-either-of-two-numbers-is-a-multiple-of-the-other-e57b99d8.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C039 - Check if a String Starts and Ends with the Same Vowel (Case Insensitive)

- Analysis file: [`analysis/ERRORS-cluster-c039-check-if-a-string-starts-and-ends-with-the-same-vowel-case-i-e2382014.md`](ERRORS-cluster-c039-check-if-a-string-starts-and-ends-with-the-same-vowel-case-i-e2382014.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C040 - Check if a Triangle is Obtuse

- Analysis file: [`analysis/ERRORS-cluster-c040-check-if-a-triangle-is-obtuse-63f89055.md`](ERRORS-cluster-c040-check-if-a-triangle-is-obtuse-63f89055.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/3`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C041 - Check if both numbers have the same sign

- Analysis file: [`analysis/ERRORS-cluster-c041-check-if-both-numbers-have-the-same-sign-53d66688.md`](ERRORS-cluster-c041-check-if-both-numbers-have-the-same-sign-53d66688.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C044 - Column Totals in a Markdown Table (Numeric Columns Only)

- Analysis file: [`analysis/ERRORS-cluster-c044-column-totals-in-a-markdown-table-numeric-columns-only-1ac3aae1.md`](ERRORS-cluster-c044-column-totals-in-a-markdown-table-numeric-columns-only-1ac3aae1.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/20`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C045 - Compute Running Average Skipping NaN

- Analysis file: [`analysis/ERRORS-cluster-c045-compute-running-average-skipping-nan-f41f194b.md`](ERRORS-cluster-c045-compute-running-average-skipping-nan-f41f194b.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/8`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C046 - Count Strings with Length Divisible by Either 3 or 5

- Analysis file: [`analysis/ERRORS-cluster-c046-count-strings-with-length-divisible-by-either-3-or-5-89a6669d.md`](ERRORS-cluster-c046-count-strings-with-length-divisible-by-either-3-or-5-89a6669d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C047 - Count Words with Matching First/Last but Different Second/Second-Last Letters

- Analysis file: [`analysis/ERRORS-cluster-c047-count-words-with-matching-first-last-but-different-second-se-93889e3f.md`](ERRORS-cluster-c047-count-words-with-matching-first-last-but-different-second-se-93889e3f.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/17`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C048 - Employee Task Analysis

- Analysis file: [`analysis/ERRORS-cluster-c048-employee-task-analysis-10f95c17.md`](ERRORS-cluster-c048-employee-task-analysis-10f95c17.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C049 - Extract Border Elements from a List

- Analysis file: [`analysis/ERRORS-cluster-c049-extract-border-elements-from-a-list-28f13169.md`](ERRORS-cluster-c049-extract-border-elements-from-a-list-28f13169.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C050 - Find Minimum Card of a Specific Suit in Hand

- Analysis file: [`analysis/ERRORS-cluster-c050-find-minimum-card-of-a-specific-suit-in-hand-fb205c62.md`](ERRORS-cluster-c050-find-minimum-card-of-a-specific-suit-in-hand-fb205c62.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C051 - First Non-Repeating Character in a String

- Analysis file: [`analysis/ERRORS-cluster-c051-first-non-repeating-character-in-a-string-7994b506.md`](ERRORS-cluster-c051-first-non-repeating-character-in-a-string-7994b506.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C052 - Get Next Roll Number

- Analysis file: [`analysis/ERRORS-cluster-c052-get-next-roll-number-634526da.md`](ERRORS-cluster-c052-get-next-roll-number-634526da.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/4`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C053 - Hand Cricket Match Runs

- Analysis file: [`analysis/ERRORS-cluster-c053-hand-cricket-match-runs-6dd5de2a.md`](ERRORS-cluster-c053-hand-cricket-match-runs-6dd5de2a.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C054 - Key Stroke Analysis

- Analysis file: [`analysis/ERRORS-cluster-c054-key-stroke-analysis-d6df2ae3.md`](ERRORS-cluster-c054-key-stroke-analysis-d6df2ae3.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C055 - Markdown Image to HTML Image

- Analysis file: [`analysis/ERRORS-cluster-c055-markdown-image-to-html-image-6cd48cab.md`](ERRORS-cluster-c055-markdown-image-to-html-image-6cd48cab.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/4`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C056 - Max Column sum and Max column sum index

- Analysis file: [`analysis/ERRORS-cluster-c056-max-column-sum-and-max-column-sum-index-14aea260.md`](ERRORS-cluster-c056-max-column-sum-and-max-column-sum-index-14aea260.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C057 - Merge and Remove Duplicates

- Analysis file: [`analysis/ERRORS-cluster-c057-merge-and-remove-duplicates-51350aa7.md`](ERRORS-cluster-c057-merge-and-remove-duplicates-51350aa7.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/4`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C059 - Pattern Printing - Diamond

- Analysis file: [`analysis/ERRORS-cluster-c059-pattern-printing-diamond-bead9f57.md`](ERRORS-cluster-c059-pattern-printing-diamond-bead9f57.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/11`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C060 - Pattern Printing - Hexagon

- Analysis file: [`analysis/ERRORS-cluster-c060-pattern-printing-hexagon-f3e3f30e.md`](ERRORS-cluster-c060-pattern-printing-hexagon-f3e3f30e.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/11`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C058 - Pattern printing - Centered Triangle Of Zeroes

- Analysis file: [`analysis/ERRORS-cluster-c058-pattern-printing-centered-triangle-of-zeroes-0a8036b7.md`](ERRORS-cluster-c058-pattern-printing-centered-triangle-of-zeroes-0a8036b7.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C061 - Polygon Analysis

- Analysis file: [`analysis/ERRORS-cluster-c061-polygon-analysis-d6a8557b.md`](ERRORS-cluster-c061-polygon-analysis-d6a8557b.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C062 - Railway Ticket Booking Analysis

- Analysis file: [`analysis/ERRORS-cluster-c062-railway-ticket-booking-analysis-f8adac6a.md`](ERRORS-cluster-c062-railway-ticket-booking-analysis-f8adac6a.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C063 - Rearrange Even Length Tuple by Placing Middle Elements at Ends

- Analysis file: [`analysis/ERRORS-cluster-c063-rearrange-even-length-tuple-by-placing-middle-elements-at-en-7a7234ca.md`](ERRORS-cluster-c063-rearrange-even-length-tuple-by-placing-middle-elements-at-en-7a7234ca.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C064 - Remainder Grouping Dictionary

- Analysis file: [`analysis/ERRORS-cluster-c064-remainder-grouping-dictionary-0b0cbaf1.md`](ERRORS-cluster-c064-remainder-grouping-dictionary-0b0cbaf1.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/18`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C066 - Remove Second and Second-Last Character from String

- Analysis file: [`analysis/ERRORS-cluster-c066-remove-second-and-second-last-character-from-string-1b2d27a8.md`](ERRORS-cluster-c066-remove-second-and-second-last-character-from-string-1b2d27a8.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/15`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C065 - Remove n Elements from the Given Index

- Analysis file: [`analysis/ERRORS-cluster-c065-remove-n-elements-from-the-given-index-1ec1d777.md`](ERRORS-cluster-c065-remove-n-elements-from-the-given-index-1ec1d777.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C067 - Replace Vowels with Next Alphabet

- Analysis file: [`analysis/ERRORS-cluster-c067-replace-vowels-with-next-alphabet-68732d1f.md`](ERRORS-cluster-c067-replace-vowels-with-next-alphabet-68732d1f.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py12_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C068 - Score Objective Questions

- Analysis file: [`analysis/ERRORS-cluster-c068-score-objective-questions-8774b54e.md`](ERRORS-cluster-c068-score-objective-questions-8774b54e.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py14_1/8`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C069 - Simple Stemmer

- Analysis file: [`analysis/ERRORS-cluster-c069-simple-stemmer-c4b6e235.md`](ERRORS-cluster-c069-simple-stemmer-c4b6e235.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py22_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C070 - String Rearrangement

- Analysis file: [`analysis/ERRORS-cluster-c070-string-rearrangement-05a33e15.md`](ERRORS-cluster-c070-string-rearrangement-05a33e15.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C071 - Three-Digit Number with Digit-Sum Divisible by k

- Analysis file: [`analysis/ERRORS-cluster-c071-three-digit-number-with-digit-sum-divisible-by-k-792c4d9d.md`](ERRORS-cluster-c071-three-digit-number-with-digit-sum-divisible-by-k-792c4d9d.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t2_py23_1/14`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C072 - Thresholding a 2D Array and Printing with * and @

- Analysis file: [`analysis/ERRORS-cluster-c072-thresholding-a-2d-array-and-printing-with-and-bc66aab5.md`](ERRORS-cluster-c072-thresholding-a-2d-array-and-printing-with-and-bc66aab5.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py21_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C073 - Time Series Analysis

- Analysis file: [`analysis/ERRORS-cluster-c073-time-series-analysis-9d3f54cb.md`](ERRORS-cluster-c073-time-series-analysis-9d3f54cb.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py13_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C074 - Total Size of Image Files

- Analysis file: [`analysis/ERRORS-cluster-c074-total-size-of-image-files-1397606c.md`](ERRORS-cluster-c074-total-size-of-image-files-1397606c.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C075 - Transfer amount

- Analysis file: [`analysis/ERRORS-cluster-c075-transfer-amount-7c675318.md`](ERRORS-cluster-c075-transfer-amount-7c675318.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C076 - Words with Consecutive Identical Letters

- Analysis file: [`analysis/ERRORS-cluster-c076-words-with-consecutive-identical-letters-0a1dc0d3.md`](ERRORS-cluster-c076-words-with-consecutive-identical-letters-0a1dc0d3.md)
- Variants in cluster: `2`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py23_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C077 - Check If Multiple of 5 Not 3

- Analysis file: [`analysis/ERRORS-cluster-c077-check-if-multiple-of-5-not-3-b7fdb988.md`](ERRORS-cluster-c077-check-if-multiple-of-5-not-3-b7fdb988.md)
- Variants in cluster: `1`
- Total final submitters across variants: `1011`
- Total non-full finals across variants: `121`
- Canonical variant: `ns_25t2_py22_1/14`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: uses num % 3 == 0 in the positive condition (accepts multiples of 15), handles only the num % 5 == 0 branch and forgets the non-multiple fallback case, and incorrect divisibility logic (general logic failure). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/14` (canonical) |             1011 |      121 | `3/3`            | Exact duplicate problem JSON |

### C078 - Check For Greeting Prefix

- Analysis file: [`analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md`](ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `982`
- Total non-full finals across variants: `405`
- Canonical variant: `ns_25t2_py22_1/15`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: checks Hello/Hi without requiring the trailing space, checks first token via split(), and partially correct greeting-prefix logic. Also many runtime crashes, syntax/empty code, and missing returns.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/15` (canonical) |              982 |      405 | `4/3`            | Exact duplicate problem JSON |

### C079 - Position of a Point Relative to a Line

- Analysis file: [`analysis/ERRORS-cluster-c079-position-of-a-point-relative-to-a-line-5bfc657f.md`](ERRORS-cluster-c079-position-of-a-point-relative-to-a-line-5bfc657f.md)
- Variants in cluster: `1`
- Total final submitters across variants: `980`
- Total non-full finals across variants: `195`
- Canonical variant: `ns_25t2_py14_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect point-position logic (general logic failure), computes a*x + b*y + c but returns that raw variable instead of sign-mapping to 1/-1/0, and returns raw line-expression value a*x + b*y + c instead of mapping to 1/-1/0. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/5` (canonical) |              980 |      195 | `3/3`            | Exact duplicate problem JSON |

### C080 - Combine First and Last Two Chars of a string

- Analysis file: [`analysis/ERRORS-cluster-c080-combine-first-and-last-two-chars-of-a-string-0ea6b2f0.md`](ERRORS-cluster-c080-combine-first-and-last-two-chars-of-a-string-0ea6b2f0.md)
- Variants in cluster: `1`
- Total final submitters across variants: `949`
- Total non-full finals across variants: `200`
- Canonical variant: `ns_25t2_py22_1/16`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: uses wrong minimum-length threshold, partially correct edge-combine logic: wrong length threshold for the 3-character edge case, and partially correct slicing but fails one or both short-string edge cases. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/16` (canonical) |              949 |      200 | `3/4`            | Exact duplicate problem JSON |

### C081 - Reversed Squares of List Elements

- Analysis file: [`analysis/ERRORS-cluster-c081-reversed-squares-of-list-elements-e3d3477b.md`](ERRORS-cluster-c081-reversed-squares-of-list-elements-e3d3477b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `936`
- Total non-full finals across variants: `171`
- Canonical variant: `ns_25t2_py22_1/17`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: squares elements but does not reverse the order, incorrect reversed-squares logic (general logic failure), and hard-codes sample outputs/cases instead of computing reversed squares. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/17` (canonical) |              936 |      171 | `3/3`            | Exact duplicate problem JSON |

### C082 - Check If a Number is a Decreasing 4-Digit Number

- Analysis file: [`analysis/ERRORS-cluster-c082-check-if-a-number-is-a-decreasing-4-digit-number-bdb096b4.md`](ERRORS-cluster-c082-check-if-a-number-is-a-decreasing-4-digit-number-bdb096b4.md)
- Variants in cluster: `1`
- Total final submitters across variants: `851`
- Total non-full finals across variants: `420`
- Canonical variant: `ns_25t2_py13_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: returns after checking only the first digit comparison, partially correct decreasing-digit logic, and incorrect decreasing-number logic (general logic failure). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/5` (canonical) |              851 |      420 | `3/3`            | Exact duplicate problem JSON |

### C083 - Double First and Last Elements in a List

- Analysis file: [`analysis/ERRORS-cluster-c083-double-first-and-last-elements-in-a-list-7ed6a713.md`](ERRORS-cluster-c083-double-first-and-last-elements-in-a-list-7ed6a713.md)
- Variants in cluster: `1`
- Total final submitters across variants: `821`
- Total non-full finals across variants: `307`
- Canonical variant: `ns_25t2_py13_2/5`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect list-end duplication logic (general logic failure), sorts the list after adding duplicates, losing the required original order, and returns the original list unchanged instead of duplicating first/last elements. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/5` (canonical) |              821 |      307 | `3/3`            | Exact duplicate problem JSON |

### C084 - Extract Email Username

- Analysis file: [`analysis/ERRORS-cluster-c084-extract-email-username-c0e39f38.md`](ERRORS-cluster-c084-extract-email-username-c0e39f38.md)
- Variants in cluster: `1`
- Total final submitters across variants: `820`
- Total non-full finals across variants: `192`
- Canonical variant: `ns_25t2_py13_2/6`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect email-username extraction logic (general logic failure), hard-codes sample usernames instead of extracting text before @, and returns the full email string instead of only the username. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/6` (canonical) |              820 |      192 | `3/3`            | Exact duplicate problem JSON |

### C085 - Expand Sum of Products

- Analysis file: [`analysis/ERRORS-cluster-c085-expand-sum-of-products-727deffc.md`](ERRORS-cluster-c085-expand-sum-of-products-727deffc.md)
- Variants in cluster: `1`
- Total final submitters across variants: `817`
- Total non-full finals across variants: `637`
- Canonical variant: `ns_25t2_py14_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: single-character-only parser (fixed-position indexing) fails multi-character or multi-digit private cases, incorrect expression parsing/formatting logic (general logic failure), and hard-codes sample expressions/outputs instead of parsing and expanding arbitrary terms. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/6` (canonical) |              817 |      637 | `3/3`            | Exact duplicate problem JSON |

### C086 - Repeat Second Half of a Tuple

- Analysis file: [`analysis/ERRORS-cluster-c086-repeat-second-half-of-a-tuple-dd65a096.md`](ERRORS-cluster-c086-repeat-second-half-of-a-tuple-dd65a096.md)
- Variants in cluster: `1`
- Total final submitters across variants: `766`
- Total non-full finals across variants: `291`
- Canonical variant: `ns_25t2_py14_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect repeated-second-half tuple logic (general logic failure), near-correct tuple-slicing logic with midpoint off-by-one bug, and returns from inside the build loop before constructing the full repeated-half tuple. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/7` (canonical) |              766 |      291 | `3/3`            | Exact duplicate problem JSON |

### C087 - Four Digit Shuffle

- Analysis file: [`analysis/ERRORS-cluster-c087-four-digit-shuffle-3272e0c2.md`](ERRORS-cluster-c087-four-digit-shuffle-3272e0c2.md)
- Variants in cluster: `1`
- Total final submitters across variants: `751`
- Total non-full finals across variants: `176`
- Canonical variant: `ns_25t2_py13_2/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: reads input() inside function-type question, incorrect four-digit shuffle logic, and returns the original number unchanged instead of shuffling digits to order 2413. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/7` (canonical) |              751 |      176 | `2/2`            | Exact duplicate problem JSON |

### C088 - Upper Case Even Index Words

- Analysis file: [`analysis/ERRORS-cluster-c088-upper-case-even-index-words-c82bee81.md`](ERRORS-cluster-c088-upper-case-even-index-words-c82bee81.md)
- Variants in cluster: `1`
- Total final submitters across variants: `729`
- Total non-full finals across variants: `298`
- Canonical variant: `ns_25t2_py13_2/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect alternate-uppercase word transformation logic (general logic failure), returns from inside the loop after processing only the first word/index, and changes odd-index words too (lower()/swapcase()), but the task requires leaving them unchanged. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/9` (canonical) |              729 |      298 | `4/4`            | Exact duplicate problem JSON |

### C089 - Check if a String Starts and Ends with the Same Vowel (Case Insensitive)

- Analysis file: [`analysis/ERRORS-cluster-c089-check-if-a-string-starts-and-ends-with-the-same-vowel-case-i-a0ad50a1.md`](ERRORS-cluster-c089-check-if-a-string-starts-and-ends-with-the-same-vowel-case-i-a0ad50a1.md)
- Variants in cluster: `1`
- Total final submitters across variants: `653`
- Total non-full finals across variants: `361`
- Canonical variant: `ns_25t3_py11/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: equality-only endpoint check, incorrect same-vowel endpoint logic (general logic failure), and checks whether both ends are vowels, but not whether they are the same vowel. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/7` (canonical) |              653 |      361 | `4/3`            | Exact duplicate problem JSON |

### C090 - Compute Polynomial Value

- Analysis file: [`analysis/ERRORS-cluster-c090-compute-polynomial-value-a73aab7f.md`](ERRORS-cluster-c090-compute-polynomial-value-a73aab7f.md)
- Variants in cluster: `1`
- Total final submitters across variants: `634`
- Total non-full finals across variants: `249`
- Canonical variant: `ns_25t2_py13_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: returns from inside the coefficient loop, so only part of the polynomial is evaluated, incorrect polynomial evaluation logic (general logic failure), and hard-codes sample polynomial values instead of evaluating arbitrary coefficients. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/9` (canonical) |              634 |      249 | `3/3`            | Exact duplicate problem JSON |

### C091 - Compare Last Digits

- Analysis file: [`analysis/ERRORS-cluster-c091-compare-last-digits-8b9d388d.md`](ERRORS-cluster-c091-compare-last-digits-8b9d388d.md)
- Variants in cluster: `1`
- Total final submitters across variants: `628`
- Total non-full finals across variants: `169`
- Canonical variant: `ns_25t3_py11/8`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect last-digit comparison logic (general logic failure), compares the full numbers for equality instead of comparing only the last digits, and reads input() inside function-type question. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/8` (canonical) |              628 |      169 | `5/3`            | Exact duplicate problem JSON |

### C092 - Describe Number Based on Divisibility

- Analysis file: [`analysis/ERRORS-cluster-c092-describe-number-based-on-divisibility-550c6af3.md`](ERRORS-cluster-c092-describe-number-based-on-divisibility-550c6af3.md)
- Variants in cluster: `1`
- Total final submitters across variants: `624`
- Total non-full finals across variants: `251`
- Canonical variant: `ns_25t2_py11_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: returns wrong casing for fallback label, incorrect Fizz/Buzz/FizzBuzz labeling logic (general logic failure), and reads input() inside function-type question. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/5` (canonical) |              624 |      251 | `4/3`            | Exact duplicate problem JSON |

### C093 - Reverse Vowel Order in a String

- Analysis file: [`analysis/ERRORS-cluster-c093-reverse-vowel-order-in-a-string-71902350.md`](ERRORS-cluster-c093-reverse-vowel-order-in-a-string-71902350.md)
- Variants in cluster: `1`
- Total final submitters across variants: `616`
- Total non-full finals across variants: `489`
- Canonical variant: `ns_25t2_py14_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect program-level vowel-reversal logic, hard-codes sample output strings (e.g., HollE) instead of reversing vowels for arbitrary input, and processes only one line instead of reversing vowels globally across all input lines. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/10` (canonical) |              616 |      489 | `2/3`            | Exact duplicate problem JSON |

### C094 - Make Word Using Last Characters of Words with Minimum Length and Starting Character

- Analysis file: [`analysis/ERRORS-cluster-c094-make-word-using-last-characters-of-words-with-minimum-length-56982813.md`](ERRORS-cluster-c094-make-word-using-last-characters-of-words-with-minimum-length-56982813.md)
- Variants in cluster: `1`
- Total final submitters across variants: `614`
- Total non-full finals across variants: `208`
- Canonical variant: `ns_25t2_py22_1/18`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: prints a constant/sample output (or empty line) instead of computing from input, checks the starting character but forgets the minimum-length condition (len(word) >= l), and uses a trivial length check (len(word) >= 1) instead of threshold l. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/18` (canonical) |              614 |      208 | `3/8`            | Exact duplicate problem JSON |

### C095 - Convert Excel Column Name to 1-Based Index

- Analysis file: [`analysis/ERRORS-cluster-c095-convert-excel-column-name-to-1-based-index-ec81fd59.md`](ERRORS-cluster-c095-convert-excel-column-name-to-1-based-index-ec81fd59.md)
- Variants in cluster: `1`
- Total final submitters across variants: `579`
- Total non-full finals across variants: `403`
- Canonical variant: `ns_25t2_py14_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect Excel column-to-index conversion logic (general logic failure), hard-codes sample column names/indices instead of computing arbitrary Excel indices, and single-letter-only / partial conversion logic. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/9` (canonical) |              579 |      403 | `4/3`            | Exact duplicate problem JSON |

### C096 - Sales Data Analysis

- Analysis file: [`analysis/ERRORS-cluster-c096-sales-data-analysis-14952156.md`](ERRORS-cluster-c096-sales-data-analysis-14952156.md)
- Variants in cluster: `1`
- Total final submitters across variants: `546`
- Total non-full finals across variants: `426`
- Canonical variant: `ns_25t2_py22_1/19`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: implements only the total_revenue task branch; other required task branches are missing, computes average product price but does not round to 2 decimals, and implements only total_revenue + product_wise_total_units_and_revenue. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/19` (canonical) |              546 |      426 | `4/4`            | Exact duplicate problem JSON |

### C097 - YouTube Video Engagement Analysis

- Analysis file: [`analysis/ERRORS-cluster-c097-youtube-video-engagement-analysis-e795b34c.md`](ERRORS-cluster-c097-youtube-video-engagement-analysis-e795b34c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `542`
- Total non-full finals across variants: `514`
- Canonical variant: `ns_25t2_py13_2/12`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: does not round engagement_rate to 2 decimals, zero-view handling is missing in one of the list-processing helpers, and treats video dicts/lists as callable objects (e.g., video('title')) in helper composition. Also many runtime crashes, syntax/empty code, and missing returns.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/12` (canonical) |              542 |      514 | `5/6`            | Exact duplicate problem JSON |

### C098 - Divide Number Into Almost Equal Parts

- Analysis file: [`analysis/ERRORS-cluster-c098-divide-number-into-almost-equal-parts-60ca61bb.md`](ERRORS-cluster-c098-divide-number-into-almost-equal-parts-60ca61bb.md)
- Variants in cluster: `1`
- Total final submitters across variants: `525`
- Total non-full finals across variants: `368`
- Canonical variant: `ns_25t2_py13_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-codes sample outputs or (n, k) cases instead of computing a general partition, incorrect partition construction, and sorts/reorders the result after construction, which breaks the required stable larger-first ordering. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/7` (canonical) |              525 |      368 | `3/3`            | Exact duplicate problem JSON |

### C099 - Parse Equation and Solve for x

- Analysis file: [`analysis/ERRORS-cluster-c099-parse-equation-and-solve-for-x-29a54a89.md`](ERRORS-cluster-c099-parse-equation-and-solve-for-x-29a54a89.md)
- Variants in cluster: `1`
- Total final submitters across variants: `525`
- Total non-full finals across variants: `471`
- Canonical variant: `ns_25t2_py13_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: parses only + forms (or mishandles -), causing ValueError on subtraction/negative cases, converts a missing/implied coefficient to int(...) (e.g., x + b = c), causing ValueError, and returns constant sample answers (3.0/4.0) instead of solving the given equation. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/6` (canonical) |              525 |      471 | `3/3`            | Exact duplicate problem JSON |

### C100 - Create Username from First Name and User ID

- Analysis file: [`analysis/ERRORS-cluster-c100-create-username-from-first-name-and-user-id-15980a82.md`](ERRORS-cluster-c100-create-username-from-first-name-and-user-id-15980a82.md)
- Variants in cluster: `1`
- Total final submitters across variants: `495`
- Total non-full finals across variants: `89`
- Canonical variant: `ns_25t3_py22/6`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-codes sample usernames/names instead of generating the username from arbitrary inputs, uses the first 3 characters but forgets to lowercase the name prefix, and username construction logic is broadly incorrect. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/6` (canonical) |              495 |       89 | `3/5`            | Exact duplicate problem JSON |

### C101 - Remove Duplicate Characters from String

- Analysis file: [`analysis/ERRORS-cluster-c101-remove-duplicate-characters-from-string-2ea9ac9b.md`](ERRORS-cluster-c101-remove-duplicate-characters-from-string-2ea9ac9b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `485`
- Total non-full finals across variants: `184`
- Canonical variant: `ns_25t3_py11/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect character deduplication logic, uses set(...) + join(...), which loses the original first-appearance order of characters, and returns the original string unchanged. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/10` (canonical) |              485 |      184 | `3/3`            | Exact duplicate problem JSON |

### C102 - Move Even Indices to End (Reversed)

- Analysis file: [`analysis/ERRORS-cluster-c102-move-even-indices-to-end-reversed-02e9c3c8.md`](ERRORS-cluster-c102-move-even-indices-to-end-reversed-02e9c3c8.md)
- Variants in cluster: `1`
- Total final submitters across variants: `464`
- Total non-full finals across variants: `189`
- Canonical variant: `ns_25t3_py11/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-codes the public example tuple/output shape instead of processing arbitrary tuples, fixed-position indexing assumes longer tuples and fails on hidden small-tuple or slice-edge cases, and incorrect tuple slicing/reconstruction logic for moving even indices to the end in reversed order. Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/9` (canonical) |              464 |      189 | `2/3`            | Exact duplicate problem JSON |

### C103 - Square the last three numbers in a list

- Analysis file: [`analysis/ERRORS-cluster-c103-square-the-last-three-numbers-in-a-list-a96de4f4.md`](ERRORS-cluster-c103-square-the-last-three-numbers-in-a-list-a96de4f4.md)
- Variants in cluster: `1`
- Total final submitters across variants: `432`
- Total non-full finals across variants: `111`
- Canonical variant: `ns_25t3_py22/7`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect tail-squaring or in-place modification logic (general logic failure), computes/returns a transformed tail slice but does not write it back to l in place, and returns the input list unchanged. Also many runtime crashes, missing returns, and syntax/empty code.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/7` (canonical) |              432 |      111 | `3/4`            | Exact duplicate problem JSON |

### C104 - Mirror Merge - Advanced

- Analysis file: [`analysis/ERRORS-cluster-c104-mirror-merge-advanced-044261c4.md`](ERRORS-cluster-c104-mirror-merge-advanced-044261c4.md)
- Variants in cluster: `1`
- Total final submitters across variants: `400`
- Total non-full finals across variants: `122`
- Canonical variant: `ns_25t3_py22/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: mirror-indexing bug causes out-of-range access, incorrect mirror pairing / parity-rule application (general logic failure), and uses an or parity condition instead of checking same parity, so mixed-parity cases are added incorrectly. Also many syntax/empty code, runtime crashes, and missing returns.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/9` (canonical) |              400 |      122 | `3/3`            | Exact duplicate problem JSON |

### C105 - Swap Diagonal Characters in a 2‑Line String

- Analysis file: [`analysis/ERRORS-cluster-c105-swap-diagonal-characters-in-a-2-line-string-abf27be0.md`](ERRORS-cluster-c105-swap-diagonal-characters-in-a-2-line-string-abf27be0.md)
- Variants in cluster: `1`
- Total final submitters across variants: `394`
- Total non-full finals across variants: `75`
- Canonical variant: `ns_25t3_py22/5`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect 2-line string diagonal-swap logic, returns sample output ('dc\nba') as a constant instead of transforming the input, and returns the input string unchanged (no diagonal swap applied). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                      | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ---------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/5` (canonical) |              394 |       75 | `3/3`            | Exact duplicate problem JSON |

### C106 - Uppercase Every k-th Vowel and lower case other vowels in a File

- Analysis file: [`analysis/ERRORS-cluster-c106-uppercase-every-k-th-vowel-and-lower-case-other-vowels-in-a-88ac099c.md`](ERRORS-cluster-c106-uppercase-every-k-th-vowel-and-lower-case-other-vowels-in-a-88ac099c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `386`
- Total non-full finals across variants: `246`
- Canonical variant: `ns_25t2_py22_1/20`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: parses k from only the first character (read(1) / text[0]), which fails multi-digit k cases, incorrect file-based vowel transformation logic, and reads stdin (input()) instead of reading from the provided filename file. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py22_1/20` (canonical) |              386 |      246 | `4/5`            | Exact duplicate problem JSON |

### C107 - Print Pieces Moved from Chess Notation string.

- Analysis file: [`analysis/ERRORS-cluster-c107-print-pieces-moved-from-chess-notation-string-c8e0c643.md`](ERRORS-cluster-c107-print-pieces-moved-from-chess-notation-string-c8e0c643.md)
- Variants in cluster: `1`
- Total final submitters across variants: `376`
- Total non-full finals across variants: `257`
- Canonical variant: `ns_25t2_py13_2/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: outputs lowercase piece names (king) instead of title-case labels (King, Rook, ...), tokenizes by spaces but does not robustly filter move-number tokens before indexing piece letters, and incorrect chess-notation token parsing and piece-name emission logic (general logic failure). Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/10` (canonical) |              376 |      257 | `3/3`            | Exact duplicate problem JSON |

### C108 - Batsman Performance Analysis

- Analysis file: [`analysis/ERRORS-cluster-c108-batsman-performance-analysis-2c04ae20.md`](ERRORS-cluster-c108-batsman-performance-analysis-2c04ae20.md)
- Variants in cluster: `1`
- Total final submitters across variants: `362`
- Total non-full finals across variants: `339`
- Canonical variant: `ns_25t2_py13_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: leaves template placeholders (...) in multiple required helper functions, uses the sample variable data instead of the parameter batsman_data, and leaves the template placeholder ... in year_with_most_average_runs(...). Also many syntax/empty code, missing returns, and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/12` (canonical) |              362 |      339 | `5/5`            | Exact duplicate problem JSON |

### C109 - Update Todo List Based on Given Indices

- Analysis file: [`analysis/ERRORS-cluster-c109-update-todo-list-based-on-given-indices-f918ee4d.md`](ERRORS-cluster-c109-update-todo-list-based-on-given-indices-f918ee4d.md)
- Variants in cluster: `1`
- Total final submitters across variants: `362`
- Total non-full finals across variants: `248`
- Canonical variant: `ns_25t2_py13_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect todo-list update logic, parses indices as raw text/characters and uses substring membership, so multi-digit hidden indices are misread, and parses completed indices character-by-character / fixed positions, so multi-digit indices are split incorrectly. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/10` (canonical) |              362 |      248 | `3/4`            | Exact duplicate problem JSON |

### C110 - Chess Game Analysis

- Analysis file: [`analysis/ERRORS-cluster-c110-chess-game-analysis-9e5aa614.md`](ERRORS-cluster-c110-chess-game-analysis-9e5aa614.md)
- Variants in cluster: `1`
- Total final submitters across variants: `354`
- Total non-full finals across variants: `334`
- Canonical variant: `ns_25t2_py14_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: leaves template placeholders (...) in multiple required chess-analysis helper functions, misclassifies queenside castling (O-O-O) as a Queen move, and leaves the template placeholder ... in remaining_pieces(...).

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/12` (canonical) |              354 |      334 | `6/6`            | Exact duplicate problem JSON |

### C111 - Unique Sum Pairs

- Analysis file: [`analysis/ERRORS-cluster-c111-unique-sum-pairs-2b88b1a1.md`](ERRORS-cluster-c111-unique-sum-pairs-2b88b1a1.md)
- Variants in cluster: `1`
- Total final submitters across variants: `336`
- Total non-full finals across variants: `262`
- Canonical variant: `ns_25t2_py11_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: hard-codes sample pair set ({(1,3), (2,2)}) / sample inputs instead of general pair generation, returns inside loop before completing full check/computation, and incorrect unique-sum-pair logic. Also many syntax/empty code, runtime crashes, and unfinished template code.

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/9` (canonical) |              336 |      262 | `3/3`            | Exact duplicate problem JSON |

### C112 - Replace Consonants with Hash

- Analysis file: [`analysis/ERRORS-cluster-c112-replace-consonants-with-hash-85125590.md`](ERRORS-cluster-c112-replace-consonants-with-hash-85125590.md)
- Variants in cluster: `1`
- Total final submitters across variants: `331`
- Total non-full finals across variants: `206`
- Canonical variant: `ns_25t2_py11_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs
- Key error summary (analyzed): Common mistakes: incorrect consonant-to-# replacement logic, consonant replacement works on a simple single line, but multi-line formatting is broken, and hard-codes sample input strings and prints sample output, not processing arbitrary input. Also many syntax/empty code and runtime crashes.

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/10` (canonical) |              331 |      206 | `3/3`            | Exact duplicate problem JSON |

### C113 - Visualize Pattern Lock

- Analysis file: [`analysis/ERRORS-cluster-c113-visualize-pattern-lock-de30af92.md`](ERRORS-cluster-c113-visualize-pattern-lock-de30af92.md)
- Variants in cluster: `1`
- Total final submitters across variants: `331`
- Total non-full finals across variants: `250`
- Canonical variant: `ns_25t2_py14_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py14_1/13` (canonical) |              331 |      250 | `4/4`            | Exact duplicate problem JSON |

### C114 - Format Tic-Tac-Toe Board

- Analysis file: [`analysis/ERRORS-cluster-c114-format-tic-tac-toe-board-ff97bcc8.md`](ERRORS-cluster-c114-format-tic-tac-toe-board-ff97bcc8.md)
- Variants in cluster: `1`
- Total final submitters across variants: `328`
- Total non-full finals across variants: `197`
- Canonical variant: `ns_25t2_py13_2/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_2/13` (canonical) |              328 |      197 | `4/2`            | Exact duplicate problem JSON |

### C115 - Horizontal Bar Chart

- Analysis file: [`analysis/ERRORS-cluster-c115-horizontal-bar-chart-80940ed6.md`](ERRORS-cluster-c115-horizontal-bar-chart-80940ed6.md)
- Variants in cluster: `1`
- Total final submitters across variants: `323`
- Total non-full finals across variants: `209`
- Canonical variant: `ns_25t2_py13_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py13_1/13` (canonical) |              323 |      209 | `3/3`            | Exact duplicate problem JSON |

### C116 - Bank Account Number Generator

- Analysis file: [`analysis/ERRORS-cluster-c116-bank-account-number-generator-cc2906b3.md`](ERRORS-cluster-c116-bank-account-number-generator-cc2906b3.md)
- Variants in cluster: `1`
- Total final submitters across variants: `314`
- Total non-full finals across variants: `197`
- Canonical variant: `ns_25t3_py22/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/10` (canonical) |              314 |      197 | `4/4`            | Exact duplicate problem JSON |

### C117 - Card to Value Tuple

- Analysis file: [`analysis/ERRORS-cluster-c117-card-to-value-tuple-2809a39d.md`](ERRORS-cluster-c117-card-to-value-tuple-2809a39d.md)
- Variants in cluster: `1`
- Total final submitters across variants: `276`
- Total non-full finals across variants: `227`
- Canonical variant: `ns_25t2_py11_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/6` (canonical) |              276 |      227 | `2/2`            | Exact duplicate problem JSON |

### C118 - Create Slug from String

- Analysis file: [`analysis/ERRORS-cluster-c118-create-slug-from-string-5f6915e4.md`](ERRORS-cluster-c118-create-slug-from-string-5f6915e4.md)
- Variants in cluster: `1`
- Total final submitters across variants: `234`
- Total non-full finals across variants: `189`
- Canonical variant: `ns_25t3_py11/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/13` (canonical) |              234 |      189 | `3/3`            | Exact duplicate problem JSON |

### C119 - Rotate Even Indices

- Analysis file: [`analysis/ERRORS-cluster-c119-rotate-even-indices-645acb21.md`](ERRORS-cluster-c119-rotate-even-indices-645acb21.md)
- Variants in cluster: `1`
- Total final submitters across variants: `232`
- Total non-full finals across variants: `180`
- Canonical variant: `ns_25t2_py11_1/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                        | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------ | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/7` (canonical) |              232 |      180 | `3/3`            | Exact duplicate problem JSON |

### C120 - People Connection Analysis

- Analysis file: [`analysis/ERRORS-cluster-c120-people-connection-analysis-4a111933.md`](ERRORS-cluster-c120-people-connection-analysis-4a111933.md)
- Variants in cluster: `1`
- Total final submitters across variants: `230`
- Total non-full finals across variants: `202`
- Canonical variant: `ns_25t3_py11/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/12` (canonical) |              230 |      202 | `5/4`            | Exact duplicate problem JSON |

### C121 - University Course Enrollment Analysis

- Analysis file: [`analysis/ERRORS-cluster-c121-university-course-enrollment-analysis-4319b6ff.md`](ERRORS-cluster-c121-university-course-enrollment-analysis-4319b6ff.md)
- Variants in cluster: `1`
- Total final submitters across variants: `216`
- Total non-full finals across variants: `122`
- Canonical variant: `ns_25t3_py22/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/12` (canonical) |              216 |      122 | `4/4`            | Exact duplicate problem JSON |

### C122 - Text Frequency Analysis

- Analysis file: [`analysis/ERRORS-cluster-c122-text-frequency-analysis-cf362a86.md`](ERRORS-cluster-c122-text-frequency-analysis-cf362a86.md)
- Variants in cluster: `1`
- Total final submitters across variants: `188`
- Total non-full finals across variants: `174`
- Canonical variant: `ns_25t2_py11_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/12` (canonical) |              188 |      174 | `4/4`            | Exact duplicate problem JSON |

### C123 - Print Average of Every Two Non-Empty Values Until Stop

- Analysis file: [`analysis/ERRORS-cluster-c123-print-average-of-every-two-non-empty-values-until-stop-35143f9a.md`](ERRORS-cluster-c123-print-average-of-every-two-non-empty-values-until-stop-35143f9a.md)
- Variants in cluster: `1`
- Total final submitters across variants: `186`
- Total non-full finals across variants: `140`
- Canonical variant: `ns_25t3_py11/11`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py11/11` (canonical) |              186 |      140 | `3/5`            | Exact duplicate problem JSON |

### C124 - Draw Arrow Trail from Movement Deltas

- Analysis file: [`analysis/ERRORS-cluster-c124-draw-arrow-trail-from-movement-deltas-f9279375.md`](ERRORS-cluster-c124-draw-arrow-trail-from-movement-deltas-f9279375.md)
- Variants in cluster: `1`
- Total final submitters across variants: `153`
- Total non-full finals across variants: `134`
- Canonical variant: `ns_25t2_py11_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                         | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ------------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t2_py11_1/13` (canonical) |              153 |      134 | `3/3`            | Exact duplicate problem JSON |

### C125 - Tap Code Decoder

- Analysis file: [`analysis/ERRORS-cluster-c125-tap-code-decoder-8806731b.md`](ERRORS-cluster-c125-tap-code-decoder-8806731b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `142`
- Total non-full finals across variants: `75`
- Canonical variant: `ns_25t3_py22/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant                       | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical      |
| ----------------------------- | ---------------: | -------: | ---------------- | ---------------------------- |
| `ns_25t3_py22/13` (canonical) |              142 |       75 | `4/4`            | Exact duplicate problem JSON |

### C126 - Absolute difference between sum and sum of the squares.

- Analysis file: [`analysis/ERRORS-cluster-c126-absolute-difference-between-sum-and-sum-of-the-squares-d34a779c.md`](ERRORS-cluster-c126-absolute-difference-between-sum-and-sum-of-the-squares-d34a779c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C127 - Average of Negative Even Numbers

- Analysis file: [`analysis/ERRORS-cluster-c127-average-of-negative-even-numbers-2b6872ff.md`](ERRORS-cluster-c127-average-of-negative-even-numbers-2b6872ff.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C128 - Average of Valid Positive Integers

- Analysis file: [`analysis/ERRORS-cluster-c128-average-of-valid-positive-integers-ed19b6ec.md`](ERRORS-cluster-c128-average-of-valid-positive-integers-ed19b6ec.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C129 - Calculate Scholarship Implement a function calculateScholarship that calculates scholarship amount for students based on

- Analysis file: [`analysis/ERRORS-cluster-c129-calculate-scholarship-implement-a-function-calculatescholars-5933c625.md`](ERRORS-cluster-c129-calculate-scholarship-implement-a-function-calculatescholars-5933c625.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/18`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C130 - Check First and Last Element are Same Integer (Type-Insensitive)

- Analysis file: [`analysis/ERRORS-cluster-c130-check-first-and-last-element-are-same-integer-type-insensiti-a0c005f7.md`](ERRORS-cluster-c130-check-first-and-last-element-are-same-integer-type-insensiti-a0c005f7.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C131 - Check If a number divides two other numbers

- Analysis file: [`analysis/ERRORS-cluster-c131-check-if-a-number-divides-two-other-numbers-ab92f66b.md`](ERRORS-cluster-c131-check-if-a-number-divides-two-other-numbers-ab92f66b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/2`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C132 - Check String Rotation

- Analysis file: [`analysis/ERRORS-cluster-c132-check-string-rotation-01049eae.md`](ERRORS-cluster-c132-check-string-rotation-01049eae.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/3`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C133 - Count Strings With More Vowels Than Consonants

- Analysis file: [`analysis/ERRORS-cluster-c133-count-strings-with-more-vowels-than-consonants-c235e9e5.md`](ERRORS-cluster-c133-count-strings-with-more-vowels-than-consonants-c235e9e5.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C134 - Count the number of Leap years in a given range A leap year is a year that: ● is divisible by 4, ● but if it is divisibl

- Analysis file: [`analysis/ERRORS-cluster-c134-count-the-number-of-leap-years-in-a-given-range-a-leap-year-38810d9c.md`](ERRORS-cluster-c134-count-the-number-of-leap-years-in-a-given-range-a-leap-year-38810d9c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/24`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C135 - Department Project Analysis

- Analysis file: [`analysis/ERRORS-cluster-c135-department-project-analysis-fa55348c.md`](ERRORS-cluster-c135-department-project-analysis-fa55348c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C136 - Employee Data Analysis

- Analysis file: [`analysis/ERRORS-cluster-c136-employee-data-analysis-129e092b.md`](ERRORS-cluster-c136-employee-data-analysis-129e092b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C137 - Fill Blanks with Words from a List

- Analysis file: [`analysis/ERRORS-cluster-c137-fill-blanks-with-words-from-a-list-1089d078.md`](ERRORS-cluster-c137-fill-blanks-with-words-from-a-list-1089d078.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C138 - Find LCM of Two Positive Integers Implement a function findLCM that returns the Least Common Multiple (LCM) of two posit

- Analysis file: [`analysis/ERRORS-cluster-c138-find-lcm-of-two-positive-integers-implement-a-function-findl-a02dd7c8.md`](ERRORS-cluster-c138-find-lcm-of-two-positive-integers-implement-a-function-findl-a02dd7c8.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/19`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C139 - Find missing number in a range of numbers

- Analysis file: [`analysis/ERRORS-cluster-c139-find-missing-number-in-a-range-of-numbers-2fb4627d.md`](ERRORS-cluster-c139-find-missing-number-in-a-range-of-numbers-2fb4627d.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/4`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C140 - Find the closest prime number Write a function closestPrime that accepts a positive integer n (where n &gt; 2) as parame

- Analysis file: [`analysis/ERRORS-cluster-c140-find-the-closest-prime-number-write-a-function-closestprime-bc3c7724.md`](ERRORS-cluster-c140-find-the-closest-prime-number-write-a-function-closestprime-bc3c7724.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/23`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C141 - Find the length of concatenated dictionary values

- Analysis file: [`analysis/ERRORS-cluster-c141-find-the-length-of-concatenated-dictionary-values-feb51d4a.md`](ERRORS-cluster-c141-find-the-length-of-concatenated-dictionary-values-feb51d4a.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C142 - Fizz-Buzz Implement a function fizzBuzz that takes a positive integer n as input and prints the Fizz-Buzz sequence from

- Analysis file: [`analysis/ERRORS-cluster-c142-fizz-buzz-implement-a-function-fizzbuzz-that-takes-a-positiv-654b1242.md`](ERRORS-cluster-c142-fizz-buzz-implement-a-function-fizzbuzz-that-takes-a-positiv-654b1242.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/20`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C143 - Format Pairs of Integers as Product of Fractions

- Analysis file: [`analysis/ERRORS-cluster-c143-format-pairs-of-integers-as-product-of-fractions-32633db2.md`](ERRORS-cluster-c143-format-pairs-of-integers-as-product-of-fractions-32633db2.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C144 - Get First and Last Characters Sorted

- Analysis file: [`analysis/ERRORS-cluster-c144-get-first-and-last-characters-sorted-0da6197f.md`](ERRORS-cluster-c144-get-first-and-last-characters-sorted-0da6197f.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C145 - Hospital Patient Analytics

- Analysis file: [`analysis/ERRORS-cluster-c145-hospital-patient-analytics-70095055.md`](ERRORS-cluster-c145-hospital-patient-analytics-70095055.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C146 - Identify Eligible Voters

- Analysis file: [`analysis/ERRORS-cluster-c146-identify-eligible-voters-04b21674.md`](ERRORS-cluster-c146-identify-eligible-voters-04b21674.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C147 - Job Scheduling Analysis

- Analysis file: [`analysis/ERRORS-cluster-c147-job-scheduling-analysis-13e615a7.md`](ERRORS-cluster-c147-job-scheduling-analysis-13e615a7.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C148 - Leaderboard List by Scores

- Analysis file: [`analysis/ERRORS-cluster-c148-leaderboard-list-by-scores-60f27c77.md`](ERRORS-cluster-c148-leaderboard-list-by-scores-60f27c77.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/8`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C149 - Mask all characters of a password except the first two and last two

- Analysis file: [`analysis/ERRORS-cluster-c149-mask-all-characters-of-a-password-except-the-first-two-and-l-58af286b.md`](ERRORS-cluster-c149-mask-all-characters-of-a-password-except-the-first-two-and-l-58af286b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C150 - Merge two dictionaries and sum on conflicts

- Analysis file: [`analysis/ERRORS-cluster-c150-merge-two-dictionaries-and-sum-on-conflicts-61d09b4f.md`](ERRORS-cluster-c150-merge-two-dictionaries-and-sum-on-conflicts-61d09b4f.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C151 - Most Frequent Numbers form the input

- Analysis file: [`analysis/ERRORS-cluster-c151-most-frequent-numbers-form-the-input-df494581.md`](ERRORS-cluster-c151-most-frequent-numbers-form-the-input-df494581.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/7`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C152 - Number Line Marker

- Analysis file: [`analysis/ERRORS-cluster-c152-number-line-marker-1a10a64f.md`](ERRORS-cluster-c152-number-line-marker-1a10a64f.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/11`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C153 - Pairwise Average of Lists

- Analysis file: [`analysis/ERRORS-cluster-c153-pairwise-average-of-lists-de01567c.md`](ERRORS-cluster-c153-pairwise-average-of-lists-de01567c.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C154 - Pattern Printing - Z Pattern

- Analysis file: [`analysis/ERRORS-cluster-c154-pattern-printing-z-pattern-4cd19968.md`](ERRORS-cluster-c154-pattern-printing-z-pattern-4cd19968.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py11_2/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C155 - Reverse Directional Connection

- Analysis file: [`analysis/ERRORS-cluster-c155-reverse-directional-connection-97e0b05b.md`](ERRORS-cluster-c155-reverse-directional-connection-97e0b05b.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/6`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C156 - Reverse the digits of a number Write a C function reverseDigits that takes an positive integer n as parameter and return

- Analysis file: [`analysis/ERRORS-cluster-c156-reverse-the-digits-of-a-number-write-a-c-function-reversedig-75089f32.md`](ERRORS-cluster-c156-reverse-the-digits-of-a-number-write-a-c-function-reversedig-75089f32.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t1_py_15_exe/22`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C157 - Ride Booking Data Analysis

- Analysis file: [`analysis/ERRORS-cluster-c157-ride-booking-data-analysis-2d85e5e4.md`](ERRORS-cluster-c157-ride-booking-data-analysis-2d85e5e4.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/12`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C158 - Rotate a Stacked‑Item Matrix 90° Clockwise

- Analysis file: [`analysis/ERRORS-cluster-c158-rotate-a-stacked-item-matrix-90-clockwise-e8c2c608.md`](ERRORS-cluster-c158-rotate-a-stacked-item-matrix-90-clockwise-e8c2c608.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/13`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C159 - Spy Number - Advanced

- Analysis file: [`analysis/ERRORS-cluster-c159-spy-number-advanced-deb78cb1.md`](ERRORS-cluster-c159-spy-number-advanced-deb78cb1.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C160 - Sum of Digit Sums from Words

- Analysis file: [`analysis/ERRORS-cluster-c160-sum-of-digit-sums-from-words-f64a1273.md`](ERRORS-cluster-c160-sum-of-digit-sums-from-words-f64a1273.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py24_1/10`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C161 - Sum of Two Halves of an Even-Digit Number

- Analysis file: [`analysis/ERRORS-cluster-c161-sum-of-two-halves-of-an-even-digit-number-d2e5c121.md`](ERRORS-cluster-c161-sum-of-two-halves-of-an-even-digit-number-d2e5c121.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py21/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C162 - Swap Signs of Two Integers

- Analysis file: [`analysis/ERRORS-cluster-c162-swap-signs-of-two-integers-ec6a6f7d.md`](ERRORS-cluster-c162-swap-signs-of-two-integers-ec6a6f7d.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py23/5`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |

### C163 - Word Sandwich

- Analysis file: [`analysis/ERRORS-cluster-c163-word-sandwich-eab9c9a7.md`](ERRORS-cluster-c163-word-sandwich-eab9c9a7.md)
- Variants in cluster: `1`
- Total final submitters across variants: `0`
- Total non-full finals across variants: `0`
- Canonical variant: `ns_25t3_py12/9`
- Variant relationship: all variants are exact duplicate problem JSONs

| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |
| ------- | ---------------: | -------: | ---------------- | ----------------------- |
