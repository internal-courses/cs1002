# Test Revision Review - 2026-03-11

Each cluster folder now uses the consistent pair format `C###_original.json` and `C###_revised.json`.

## Executive Summary

There are `45` testcase changes across the seven clusters: `30` directly aligned with earlier findings, `9` partially aligned, and `6` coverage trade-offs that were not themselves previously identified as priorities.

- Strong, directly aligned revisions: `C002`, `C085`, `C096`, and `C099`.
- Partial revisions: `C078` and `C095` move in the right direction but still leave the most useful hidden traps private.
- Mixed revision: `C092` exposed the right hidden failure modes, but it also removed public `Fizz`/`Buzz` coverage.
- `C002`: 4 aligned, 0 partial, 0 trade-off testcase changes.
- `C078`: 5 aligned, 0 partial, 4 trade-off testcase changes.
- `C085`: 6 aligned, 3 partial, 0 trade-off testcase changes.
- `C092`: 2 aligned, 2 partial, 2 trade-off testcase changes.
- `C095`: 4 aligned, 0 partial, 0 trade-off testcase changes.
- `C096`: 4 aligned, 4 partial, 0 trade-off testcase changes.
- `C099`: 5 aligned, 0 partial, 0 trade-off testcase changes.

## Highest-Priority Missed Opportunities

| Priority | Cluster | Suggested change                                                      | Impact | Ease    | Why it still matters                                                                                                                                                                                                                                       |
| -------- | ------- | --------------------------------------------------------------------- | ------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P0       | C095    | Move one 3-/4-letter edge case into public (`XFD` and ideally `AAAA`) | High   | Trivial | Our own quick-fix note named exactly this gap. The revised public suite still stops at `BBA`, so the 24 longer-label parser failures remain largely hidden.                                                                                                |
| P0       | C099    | Add one whitespace-stressed composite edge case                       | High   | Trivial | The suite is much better, but the prompt explicitly allows irregular internal and trailing spaces. A single public case that combines whitespace normalization with an implied coefficient or negative RHS would close the last obvious hidden-parser gap. |
| P1       | C078    | Add the truly short negatives publicly: `""`, `"Hi"`, and `"Hello"`   | High   | Trivial | The report linked 79 non-full rows to short/empty-string `IndexError` and 92 rows to accepting `Hi`/`Hello` without the trailing space. Those failures are still hidden.                                                                                   |
| P1       | C092    | Restore one public `Fizz` case and one public `Buzz` case             | Medium | Trivial | The revision now covers `FizzBuzz` and `Normal` well, but it unnecessarily dropped public coverage for the other two required labels.                                                                                                                      |

The priorities above are ranked by the combination of likely impact on known student failure modes and how little evaluator work is needed to implement the change.

## C002 - Shuffle a Three Word Sentence

Refs: `analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md`, `analysis/quick-fixes.md`.
Public tests changed from `2` to `6`. Private tests changed from `0` to `0`.
This revision is tightly aligned with the prior C002 analysis: it now exposes all six permutations publicly, including the cyclic orders that used to stay hidden.

### Change-by-Change Mapping

| Change                                                                           | Mapping | Improvement Area                                    | Explanation                                                                                                                               |
| -------------------------------------------------------------------------------- | ------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Public Added: Add the missing self-inverse permutation `(1,0,2)` on unseen words | Aligned | P0 anti-hardcoding sentinel public tests            | Adds a third non-sample order without changing the concept, so students can no longer overfit to just the two original public tuples.     |
| Public Added: Add cyclic permutation `(2,0,1)` on unseen words                   | Aligned | C002 private-case finding about cyclic permutations | Directly targets the inverse-permutation bug the report highlighted: code that works on self-inverse public orders fails here.            |
| Public Added: Add the other cyclic permutation `(1,2,0)`                         | Aligned | C002 private-case finding about cyclic permutations | Covers the second hidden cyclic order, so both common public-only tuple shortcuts now fail before final submission.                       |
| Public Added: Add identity order `(0,1,2)` on unseen words                       | Aligned | C002 identity-order / ignores-`order` coverage      | Checks the degenerate case explicitly and catches solutions that always rearrange words even when the tuple says to leave them untouched. |

### Missed Opportunities

- No high-priority missed opportunity stood out here; the revision already matches the earlier diagnosis well.

## C078 - Check For Greeting Prefix

Refs: `analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md`, `analysis/quick-fixes.md`.
Public tests changed from `4` to `5`. Private tests changed from `3` to `3`.
The revision moves in the right direction by making the trailing-space contract, case sensitivity, and leading-space semantics visible. It is still only a partial implementation of the earlier recommendation because the shortest negative cases remain private.

### Change-by-Change Mapping

| Change                                                              | Mapping   | Improvement Area                                        | Explanation                                                                                                                                               |
| ------------------------------------------------------------------- | --------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Public Added: Add `HelloWorld -> False`                             | Aligned   | P1 short/edge public tests for trailing-space semantics | Directly addresses the most common failure mode: accepting `Hello` without the required trailing space.                                                   |
| Public Added: Add bare prefix positive `Hello  -> True`             | Aligned   | P1 short/edge public tests for C078                     | Matches the prior recommendation to expose the exact contract that a bare greeting followed by a space is valid.                                          |
| Public Added: Add bare prefix positive `Hi  -> True`                | Aligned   | P1 short/edge public tests for C078                     | Makes the `Hi` branch explicit instead of relying only on longer phrases like `Hi friend`.                                                                |
| Public Added: Add lowercase negative `hello world -> False`         | Aligned   | C078 case-sensitivity failures                          | Targets the documented pattern where students lowercase the input or accept case-insensitive greetings.                                                   |
| Public Added: Add leading-space negative `hi there -> False`        | Aligned   | C078 `strip()` / `lstrip()` semantic bug                | Directly catches solutions that trim leading whitespace before checking the prefix.                                                                       |
| Public Removed: Remove normal positive phrase `Hello there -> True` | Trade-off | Not a previously identified gap                         | This is a coverage trade-off rather than a targeted fix. It frees room for edge cases but removes a simple sanity-check positive example.                 |
| Public Removed: Remove normal positive phrase `Hi friend -> True`   | Trade-off | Not a previously identified gap                         | Same trade-off as above: the suite becomes edge-heavier but loses a normal positive example with characters after the prefix.                             |
| Public Removed: Remove `Hithere -> False`                           | Trade-off | Weakens one public guard on the no-space `Hi` bug       | The earlier recommendation explicitly kept a `Hi`-family no-space negative public. Replacing it with only `HelloWorld` leaves the `Hi` side less visible. |
| Public Removed: Remove generic negative `Welcome -> False`          | Trade-off | Low-value generic negative coverage                     | This removal is mostly harmless, but it does not map to any specific failure family we had previously identified.                                         |

### Missed Opportunities

- `P1`: Add the truly short negatives publicly: `""`, `"Hi"`, and `"Hello"`. Why: The report linked 79 non-full rows to short/empty-string `IndexError` and 92 rows to accepting `Hi`/`Hello` without the trailing space. Those failures are still hidden. Suggested tests: `is_equal(starts_with_greeting(""), False); is_equal(starts_with_greeting("Hi"), False); is_equal(starts_with_greeting("Hello"), False)`.

## C085 - Expand Sum of Products

Refs: `analysis/ERRORS-cluster-c085-expand-sum-of-products-727deffc.md`, `analysis/quick-fixes.md`.
Public tests changed from `3` to `6`. Private tests changed from `0` to `0`.
C085 is the cleanest implementation of the earlier recommendations: the revised suite now hits both anti-hardcoding and variable-length parser traps in public.

### Change-by-Change Mapping

| Change                                                                           | Mapping | Improvement Area                           | Explanation                                                                                                                                |
| -------------------------------------------------------------------------------- | ------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Public Added: Add unseen symbolic baseline `(p+q)(r+s)`                          | Aligned | P0 anti-hardcoding sentinel public tests   | Breaks memorization of the original `(a+b)(c+d)` sample while keeping the same conceptual difficulty.                                      |
| Public Added: Add a second unseen symbolic baseline `(m+n)(u+v)`                 | Aligned | P0 anti-hardcoding sentinel public tests   | Further reduces the chance that students can pass by memorizing one or two literal public expansions.                                      |
| Public Added: Add another reordered symbolic baseline `(x+y)(a+b)`               | Aligned | P0 anti-hardcoding sentinel public tests   | Keeps the easy symbolic shape public but makes it clear that the exact letters do not matter.                                              |
| Public Added: Add multi-character identifiers                                    | Aligned | P0 variable-length / parser edge cases     | Directly targets the largest C085 failure family: fixed-position parsers that only work for one-character tokens.                          |
| Public Added: Add multi-digit numeric terms                                      | Aligned | P0 variable-length / parser edge cases     | Exposes the fixed-width numeric parsing bug that used to appear only in private cases.                                                     |
| Public Added: Add word tokens instead of algebraic-looking symbols               | Aligned | P0 anti-hardcoding sentinel public tests   | Makes it even harder to fake an algebra-only parser by indexing literal character positions.                                               |
| Public Removed: Remove the canonical `(a+b)(c+d)` public sample                  | Partial | Supports the anti-hardcoding shift         | Removing the most memorizable sample helps, but the real improvement comes from the stronger replacements rather than the deletion itself. |
| Public Removed: Remove the second sample-shaped symbolic case                    | Partial | Supports the anti-hardcoding shift         | Same rationale: useful mainly because it avoids a public suite made entirely of sample-adjacent expressions.                               |
| Public Removed: Replace the old numeric sample with a stronger numeric edge case | Partial | Supports stronger variable-length coverage | The new numeric case is better because it is more visibly fixed-width-hostile than the original sample.                                    |

### Missed Opportunities

- No high-priority missed opportunity stood out here; the revision already matches the earlier diagnosis well.

## C092 - Describe Number Based on Divisibility

Refs: `analysis/ERRORS-cluster-c092-describe-number-based-on-divisibility-550c6af3.md`, `analysis/quick-fixes.md`.
Public tests changed from `4` to `2`. Private tests changed from `3` to `3`.
The revised public tests target the right hidden errors, but this is the only cluster where the suite also got narrower. It now shows `FizzBuzz` and `Normal` publicly, while `Fizz` and `Buzz` disappear from public coverage.

### Change-by-Change Mapping

| Change                                                             | Mapping   | Improvement Area                                              | Explanation                                                                                                                                          |
| ------------------------------------------------------------------ | --------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Public Added: Replace `15` with another `FizzBuzz` multiple (`45`) | Aligned   | C092 `FizzBuzz` branch-order bug                              | Keeps the same intended trap public: solutions that check `% 3` or `% 5` first still fail.                                                           |
| Public Added: Add `Normal` casing example on a non-sample number   | Aligned   | P1 formatting/casing visibility for `Normal`                  | Directly targets the largest C092 family: returning `'normal'` instead of `'Normal'`.                                                                |
| Public Removed: Remove the `Fizz` public example                   | Trade-off | Removes branch coverage that was not identified as expendable | This does not map to a prior recommendation. It weakens public coverage for one of the four required labels.                                         |
| Public Removed: Remove the `Buzz` public example                   | Trade-off | Removes branch coverage that was not identified as expendable | Same issue as above: the suite becomes less balanced across the four output branches.                                                                |
| Public Removed: Remove the simple `FizzBuzz` sample (`15`)         | Partial   | Concept preserved via `45`, but deletion adds no new leverage | Net coverage for the `FizzBuzz` branch remains, so this is not a regression, but the improvement comes from the replacement rather than the removal. |
| Public Removed: Remove the simple `Normal` sample (`7`)            | Partial   | Concept preserved via `34`, but deletion adds no new leverage | The casing issue is still exposed through `34 -> Normal`, but removing the simpler public baseline was not part of the earlier recommendation.       |

### Missed Opportunities

- `P1`: Restore one public `Fizz` case and one public `Buzz` case. Why: The revision now covers `FizzBuzz` and `Normal` well, but it unnecessarily dropped public coverage for the other two required labels. Suggested tests: `is_equal(describe_number(9), "Fizz"); is_equal(describe_number(10), "Buzz")`.

## C095 - Convert Excel Column Name to 1-Based Index

Refs: `analysis/ERRORS-cluster-c095-convert-excel-column-name-to-1-based-index-ec81fd59.md`, `analysis/quick-fixes.md`.
Public tests changed from `4` to `8`. Private tests changed from `3` to `3`.
C095 is improved, but only partially. The public suite now walks students through a cleaner 1-letter to 2-letter staircase, yet the exact 3+/4-letter edge cases that our quick-fix note called out are still private-only.

### Change-by-Change Mapping

| Change                                                     | Mapping | Improvement Area                               | Explanation                                                                                                                    |
| ---------------------------------------------------------- | ------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Public Added: Add base case `A -> 1`                       | Aligned | Anti-hardcoding + baseline mapping visibility  | Makes the simplest base-26 mapping public instead of relying only on the prose example.                                        |
| Public Added: Add single-letter boundary `Z -> 26`         | Aligned | Single-letter boundary coverage                | Helps catch off-by-one or incomplete alphabet tables before students reach multi-letter columns.                               |
| Public Added: Add the first two-letter rollover `AA -> 27` | Aligned | Early-return / positional-weight trap for C095 | Directly exposes solutions that return after processing only the first letter or that treat the label as simple concatenation. |
| Public Added: Add two-letter upper boundary `ZZ -> 702`    | Aligned | Two-letter positional-weight coverage          | Strengthens public coverage of base-26 weighting across two positions.                                                         |

### Missed Opportunities

- `P0`: Move one 3-/4-letter edge case into public (`XFD` and ideally `AAAA`). Why: Our own quick-fix note named exactly this gap. The revised public suite still stops at `BBA`, so the 24 longer-label parser failures remain largely hidden. Suggested tests: `is_equal(excel_index("XFD"), 16384); is_equal(excel_index("AAAA"), 18279)`.

## C096 - Sales Data Analysis

Refs: `analysis/ERRORS-cluster-c096-sales-data-analysis-14952156.md`, `analysis/quick-fixes.md`.
Public tests changed from `4` to `4`. Private tests changed from `4` to `4`.
This is a strong revision. The new public tests are smaller, more discriminative, and much more aligned with the earlier recommendation to expose one branch-specific failure mode per task.

### Change-by-Change Mapping

| Change                                                                                | Mapping | Improvement Area                                      | Explanation                                                                                                                       |
| ------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Public Added: Replace sample-sized `total_revenue` with a tiny discriminative dataset | Aligned | P1 dispatch-branch coverage for task-driven functions | Now students can isolate the `total_revenue` branch without parsing a large example or depending on the sample product IDs.       |
| Public Added: Use a tiny repeated-product dataset for the aggregation branch          | Aligned | P1 dispatch-branch coverage for task-driven functions | Publicly exposes the repeated-`product_id` aggregation behavior instead of hiding it inside a larger sample.                      |
| Public Added: Make the tie-break rule public for `top_selling_product`                | Aligned | C096 hidden tie-break behavior                        | This was explicitly a hidden-case requirement before; the revision now shows the revenue tie-break publicly.                      |
| Public Added: Make non-integer average rounding public                                | Aligned | P1 rounding visibility for `average_product_price`    | Directly targets the documented `10.6%` failure family where students compute the right average but do not round to two decimals. |
| Public Removed: Drop the large sample-specific `total_revenue` public test            | Partial | Replaced by smaller branch-isolating coverage         | Helpful because it removes dependence on the sample product IDs, but the real gain comes from the tighter replacement case.       |
| Public Removed: Drop the large sample-specific aggregation public test                | Partial | Replaced by smaller branch-isolating coverage         | The new small dataset makes the repeated-ID requirement easier to diagnose and less overfit-prone.                                |
| Public Removed: Drop the large sample-specific top-seller test                        | Partial | Replaced by a cleaner tie-break-focused public case   | The replacement is better because it isolates the tie-break rule rather than bundling it into a long sample.                      |
| Public Removed: Drop the large sample-specific average-price test                     | Partial | Replaced by a stronger rounding-focused public case   | The new `10.67` case is more discriminative for the exact rounding bug our analysis highlighted.                                  |

### Missed Opportunities

- No high-priority missed opportunity stood out here; the revision already matches the earlier diagnosis well.

## C099 - Parse Equation and Solve for x

Refs: `analysis/ERRORS-cluster-c099-parse-equation-and-solve-for-x-29a54a89.md`, `analysis/quick-fixes.md`.
Public tests changed from `3` to `8`. Private tests changed from `3` to `3`.
This is another strong revision: it publicizes implied coefficients, subtraction, no-constant cases, multi-digit coefficients, and negative right-hand sides. Those were exactly the parser traps our earlier analysis said were hiding behind the private suite.

### Change-by-Change Mapping

| Change                                                             | Mapping | Improvement Area                                                | Explanation                                                                                                     |
| ------------------------------------------------------------------ | ------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Public Added: Add implied-coefficient case `x + 2 = 5`             | Aligned | P0 variable-length / parser edge cases for implied coefficients | Directly targets the documented failure where students try to `int('')` instead of treating missing `a` as `1`. |
| Public Added: Add multi-digit coefficient case `10x + 20 = 60`     | Aligned | P0 fixed-width parser traps                                     | Exposes parsers that only work when coefficients are one character long.                                        |
| Public Added: Add no-constant case `2x=6`                          | Aligned | P0 fixed-format parser traps                                    | Catches solutions that assume every equation must contain an explicit `+ b` or `- b` term.                      |
| Public Added: Add subtraction with implied coefficient `x - 3 = 7` | Aligned | P0 subtraction/sign parser edge cases                           | Combines two earlier hidden traps at once: implied `a=1` and a negative constant term.                          |
| Public Added: Add negative-RHS case `3x + 7 = -2`                  | Aligned | P0 sign-handling robustness                                     | Targets the sign/spacing family that previously passed public and then failed private.                          |

### Missed Opportunities

- `P0`: Add one whitespace-stressed composite edge case. Why: The suite is much better, but the prompt explicitly allows irregular internal and trailing spaces. A single public case that combines whitespace normalization with an implied coefficient or negative RHS would close the last obvious hidden-parser gap. Suggested tests: `is_equal(solve_for_x(" x + 5 = -5 "), -10.0) or is_equal(solve_for_x(" 10x+20=60 "), 4.0)`.
