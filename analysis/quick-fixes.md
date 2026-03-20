# Quick Wins: High-Impact, Low-Effort Fixes to Questions/Test Cases

## Scope and Method

- Data source: `analysis/errors.json` + cluster reports in `analysis/ERRORS-cluster-*.md`.
- Coverage: `60` analyzed clusters, `16,402` non-full final submissions.
- Prioritization used here:
  - **Impact**: affected non-full rows linked to a fixable pattern family (upper-bound, may overlap).
  - **Effort**: how quickly faculty/content teams can change prompt/test JSON and evaluator behavior.

## Priority Summary

| Priority | Quick fix                                                    |           Affected non-full rows (upper-bound) | Why it is low effort                                | Start with                             |
| -------- | ------------------------------------------------------------ | ---------------------------------------------: | --------------------------------------------------- | -------------------------------------- |
| P0       | Add anti-hardcoding sentinel public tests                    |                               `1,348` (`8.2%`) | Add 1–2 public tests per question; no rubric change | `C098`, `C013`, `C095`, `C085`, `C002` |
| P0       | Add variable-length / parser edge cases to public tests      |                                 `444` (`2.7%`) | Add a few edge-case test lines                      | `C085`, `C099`, `C095`                 |
| P0       | Add early-return trap tests + one-line control-flow warning  |                                 `746` (`4.5%`) | Small prompt edit + 1 trap test                     | `C013`, `C012`, `C082`, `C095`         |
| P0       | Unify file I/O contract (`filename` vs `stdin`)              | `130` direct (`0.8%`) + linked parse confusion | Prompt/template/evaluator wording alignment         | `C106`, `C020`                         |
| P1       | Add short/empty edge cases to public tests                   |                                 `194` (`1.2%`) | 3–5 extra tests                                     | `C078`                                 |
| P1       | Normalize non-concept formatting (case/rounding)             |                                 `300` (`1.8%`) | Comparator tweak or explicit public checks          | `C092`, `C096`, `C097`, `C002`         |
| P1       | Add helper-level smoke tests in multi-function tasks         |                                 `816` (`5.0%`) | Reorganize existing public tests, no concept change | `C110`, `C108`, `C026`, `C014`         |
| P1       | Add dispatch-branch coverage tests for task-driven functions |                                 `140` (`0.9%`) | Add minimal test per branch                         | `C096`                                 |
| P2       | Add variant-equivalence preflight checks before release      |                    catastrophic-risk guardrail | One validation script in release pipeline           | `ns_25t2_py21_1` vs `ns_25t2_py21_2`   |

---

## P0-1) Anti-Hardcoding Sentinel Public Tests

### Problem (evidence)

- Hardcoding/sample overfit patterns affect `1,348` non-full rows across `56` clusters.
- Examples:
  - `C098`: `106` hard-coded sample outputs.
  - `C013`: `77` hard-coded sample pangram strings.
  - `C095`: `45` hard-coded sample column names.
  - `C085`: `42` hard-coded sample expressions.

### Original (example from `C085`)

```python
is_equal(expand_sum_of_products("(a+b)(c+d)"), "a*c + a*d + b*c + b*d")
is_equal(expand_sum_of_products("(x+y)(z+w)"), "x*z + x*w + y*z + y*w")
is_equal(expand_sum_of_products("(1+5)(10+12)"), "1*10 + 1*12 + 5*10 + 5*12")
```

### Revised

```python
# Keep existing tests, add one lexical-shape breaker:
is_equal(
    expand_sum_of_products("(alpha+beta)(gamma+delta)"),
    "alpha*gamma + alpha*delta + beta*gamma + beta*delta",
)
```

### Expected impact

- Moves many hidden-test failures into visible/public feedback early.
- Preserves intended concept while reducing sample memorization wins.

---

## P0-2) Expose Fixed-Width Parser Traps in Public Tests

### Problem (evidence)

- Fixed-position/fixed-width parsing patterns affect `444` non-full rows.
- Biggest sources:
  - `C085`: `274` single-character parser fails multi-character/multi-digit cases.
  - `C099`: `65` plus-only parsing; `30` implied-coefficient parse failures; `26` spacing/sign format failures.
  - `C095`: `24` fails 3+/4-letter columns.

### Original (example from `C099`)

```python
is_equal(solve_for_x("2x + 3= 11"), 4.0)
is_equal(solve_for_x("5x - 2= 13"), 3.0)
is_equal(solve_for_x("-3x + 10 = 1"), 3.0)
```

### Revised

```python
# Add implied coefficient and spacing variants:
is_equal(solve_for_x("x + 5 = -5"), -10.0)
is_equal(solve_for_x(" 10x+20=60 "), 4.0)
```

### Also apply to `C095`

- Add public tests:

```python
is_equal(excel_index("XFD"), 16384)
is_equal(excel_index("AAAA"), 18279)
```

### Expected impact

- Substantial reduction in “passes public, fails private parser edge” patterns.

---

## P0-3) Early-Return-in-Loop Trap Coverage

### Problem (evidence)

- Early-return control-flow errors affect `746` non-full rows.
- Largest:
  - `C013`: `243` returns inside alphabet loop.
  - `C012`: `183` returns inside AP-check loop.
  - `C082`: `82` returns after first digit comparison.

### Original prompt style (common)

- Prompts define output contract but do not explicitly warn against premature loop returns.

### Revised prompt addition (one line)

```text
Important: complete the full scan/check first; return only after all required elements are processed.
```

### Revised public-test additions

```python
# C012: fail-near-end AP trap
is_equal(is_arithmetic_progression([2, 4, 6, 8, 11]), False)

# C082: first comparison passes, later one fails
is_equal(is_decreasing_4_digit_number(9431), True)
is_equal(is_decreasing_4_digit_number(9413), False)
```

### Expected impact

- Catches a major novice control-flow bug before final submission.

---

## P0-4) Unify File-I/O Contract (`filename` vs `stdin`)

### Problem (evidence)

- Direct file-contract mismatch patterns: `130` non-full rows.
- `C106`: `27` read `input()` instead of provided `filename`; `31` parse `k` from first character.
- `C020`: `89` submissions in one variant solved a different file-based task than evaluator behavior.

### Original (from `problems/ns_25t2_py22_1/20.json`)

```text
The first line of the input contains the integer k.
Subsequent lines contain the text.
NOTE: ... input is read from the file ...
# use the variable filename for the name of the file.
```

and hidden harness prefix:

```python
# This writes the stdin to the input file
_, filename = tempfile.mkstemp(prefix="case")
with open(filename, "w") as f:
    f.write(sys.stdin.read())
```

### Revised

```text
Input Contract (must follow): The grader writes stdin content into a temporary file path provided as `filename`.
Read from `filename`; do not call `input()` for this question.
```

```python
# Starter snippet in template
with open(filename, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
k = int(lines[0])
text_lines = lines[1:]
```

### Expected impact

- Removes contract ambiguity that is unrelated to core algorithmic objective.

---

## P1-1) Add Short/Empty Edge Cases Publicly (Prefix/String Questions)

### Problem (evidence)

- `C078` alone has `194` affected rows:
  - `92`: accepts `"Hello"/"Hi"` without trailing space.
  - `79`: IndexError on short/empty strings.
  - `23`: partial edge-case logic failures.

### Original public tests (`C078`)

```python
is_equal(starts_with_greeting("Hello there"), True)
is_equal(starts_with_greeting("Hi friend"), True)
is_equal(starts_with_greeting("Hithere"), False)
is_equal(starts_with_greeting("Welcome"), False)
```

### Revised

```python
# keep existing + add edge contracts explicitly
is_equal(starts_with_greeting(""), False)
is_equal(starts_with_greeting("Hi"), False)
is_equal(starts_with_greeting("Hello"), False)
is_equal(starts_with_greeting("Hi "), True)
is_equal(starts_with_greeting("Hello "), True)
```

### Expected impact

- Converts hidden edge surprises into immediate feedback.

---

## P1-2) Normalize Non-Concept Formatting (Case/Rounding)

### Problem (evidence)

- Formatting/casing/rounding family: `300` affected rows.
- High-value examples:
  - `C092`: `122` wrong casing for fallback label (`"normal"` vs `"Normal"`).
  - `C096`: `45` no 2-decimal rounding for average price.
  - `C097`: `103` no 2-decimal rounding for engagement rate.

### Option A (if format is NOT the intended concept)

- Accept case-insensitive fixed labels.
- Compare numerics after rounding to required precision in evaluator.

### Option B (if format IS required)

- Keep strict comparator, but add explicit public tests that isolate format behavior.

### Revised public checks (examples)

```python
# C096 / C097 precision edge
is_equal(analyse_sales_data(data, "average_product_price"), {"P1": 33.33})
is_equal(engagement_rate(video), 10.81)
```

### Expected impact

- Removes avoidable failures where concept is right but surface formatting diverges.

---

## P1-3) Multi-Function Questions: Helper-Level Smoke Tests + Better Scaffold

### Problem (evidence)

- Placeholder/incomplete-helper family affects `816` rows.
- Concentrated in:
  - `C110`: `221`
  - `C108`: `105`
  - `C026`: `82`
  - `C014`: `95`

### Original (example from `C110` template)

```python
def parse_moves(game: str) -> list: ...


def get_n_moves(game: str) -> int: ...


# ... 4 more helpers ...
```

### Revised

```python
def parse_moves(game: str) -> list:
    raise NotImplementedError("Implement parse_moves")


# ... same for each helper ...
```

And public tests are grouped so each helper has a tiny independent smoke case before larger integrated cases.

### Expected impact

- Better debug locality; students can identify which helper breaks first instead of seeing only aggregate failure.

---

## P1-4) Dispatch-Branch Coverage for Task-Driven Functions

### Problem (evidence)

- `C096` has `140` rows tied to missing/incomplete task branches.

### Original

- Single shared dataset across tasks; branch omission still common in finals.

### Revised

- Add one minimal public test **per task string**, each using the smallest discriminative dataset.
- Add one public check for invalid task handling behavior.

```python
# example structure
is_equal(analyse_sales_data(min_data, "total_revenue"), 300)
is_equal(analyse_sales_data(min_data, "top_selling_product"), "P2")
is_equal(analyse_sales_data(min_data, "average_product_price"), {"P1": 12.5})
```

### Expected impact

- Directly reduces “implemented only one branch” failures.

---

## P2) Variant-Equivalence Release Guardrail

### Problem (evidence)

- `C020` shows strong variant-specific behavior drift:
  - `89/136` (`65.4%`) in one variant solved a different task family.
- `analysis/evaluation_redesign/variant_equivalence_review_targets.csv` flags major drift for `ns_25t2_py21_1` vs `ns_25t2_py21_2` on **File Content Zig-Zag Shift**.

### Revised process (pre-release)

1. Hash-check: prompt HTML + code template + prefixed/suffixed code + public/private tests across same-slot variants.
2. Fail release if any variant differs beyond allowed metadata fields.
3. Run one canonical reference solution against every variant before publish.

### Expected impact

- Prevents entire variant cohorts from being measured on a different effective task.

---

## Suggested Rollout Order (Fastest First)

1. Patch public tests for `C085`, `C095`, `C099`, `C078`, `C096`, `C097` (same day).
2. Patch file-contract wording/template for `C106` and confirm `C020` variants (same day).
3. Add early-return warning line + trap tests in `C013`, `C012`, `C082` (same day).
4. Add helper-level smoke tests for `C110`, `C108`, `C026`, `C014` (1–2 days).
5. Add variant-equivalence preflight script to release checklist (1 day).

## Evidence Base (External)

- Sweller, J., & Cooper, G. A. (1985). _The use of worked examples as a substitute for problem solving in learning algebra_. DOI: https://doi.org/10.1207/s1532690xci0201_3
- Hattie, J., & Timperley, H. (2007). _The Power of Feedback_. DOI: https://doi.org/10.3102/003465430298487
- Hao, Q., et al. (2019). _The Role of Immediate Feedback in Interactive Programming Exercises_. arXiv: https://arxiv.org/abs/1906.08937
- Alkafaween, U., et al. (2024). _Automating Autograding: LLMs as Test Suite Generators for Intro Programming_. arXiv: https://arxiv.org/abs/2411.09261
