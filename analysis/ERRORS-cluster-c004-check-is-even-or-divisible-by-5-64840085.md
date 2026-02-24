# Error Patterns: Cluster C004 (`Check is even or divisible by 5`)

## Cluster Summary

- Cluster ID: `C004`
- Cluster title: `Check is even or divisible by 5`
- Cluster file (this file): `analysis/ERRORS-cluster-c004-check-is-even-or-divisible-by-5-64840085.md`
- Variants in cluster: `3`
- Total final submitters across variants: `698`
- Total non-full final submissions across variants: `77`
- Canonical variant (by submissions): `ns_25t2_py12_1/5`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py12_1/5` (canonical) |              698 |       77 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py12_1/5.json`
- Other variants in cluster:
  - `problems/ns_25t1_py11_1/2.json`
  - `problems/ns_25t1_py_15_exe/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `698`
- Full pass: `621`
- Non-full final submissions: `77`
- Parseable non-full (logic/runtime focus): `42`
- Non-parseable non-full: `35`

Variant-level comparison:

| Variant               | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t1_py11_1/2`    |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t1_py_15_exe/5` |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t2_py12_1/5`    |              698 |       621 |       77 |                 42 |                     35 |

## Private Case Structure

- Private case 1: mixed false/true cases (odd non-multiple, multiple of 5, odd non-multiple)
- Private case 2: large even/5-multiple positives to catch parameter-ignoring and wrong-operator logic
- Private case 3: mixed `True/False/True` cases to distinguish `or` vs `and` and missing-`return False` bugs

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                    | Cluster count | % of cluster non-full | `ns_25t1_py11_1/2` | `ns_25t1_py_15_exe/5` | `ns_25t2_py12_1/5` |
| ---------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: | --------------------: | -----------------: |
| Syntax / non-parseable final submission                                                                    |            35 |                 45.5% |                  0 |                     0 |                 35 |
| Partially correct boolean logic, but false cases are mishandled (missing `return False` or wrong operator) |             6 |                  7.8% |                  0 |                     0 |                  6 |
| Runtime error (parseable final submission)                                                                 |             5 |                  6.5% |                  0 |                     0 |                  5 |
| Incorrect even/divisible-by-5 logic (broad wrong-answer failure)                                           |             5 |                  6.5% |                  0 |                     0 |                  5 |
| Uses division (`/` or `//`) instead of modulus (`%`) in the divisibility test                              |             4 |                  5.2% |                  0 |                     0 |                  4 |
| Runtime ValueError                                                                                         |             4 |                  5.2% |                  0 |                     0 |                  4 |
| Always returns `True` (constant output)                                                                    |             4 |                  5.2% |                  0 |                     0 |                  4 |
| Runtime NameError                                                                                          |             4 |                  5.2% |                  0 |                     0 |                  4 |
| No return / implicit `None`                                                                                |             2 |                  2.6% |                  0 |                     0 |                  2 |
| Ignores the function parameter and checks a hard-coded sample number instead                               |             2 |                  2.6% |                  0 |                     0 |                  2 |
| Runtime TypeError                                                                                          |             2 |                  2.6% |                  0 |                     0 |                  2 |
| Uses `and` instead of `or`, so numbers satisfying only one condition are rejected                          |             2 |                  2.6% |                  0 |                     0 |                  2 |
| Reads `input()` inside function (EOF under evaluator function-call tests)                                  |             1 |                  1.3% |                  0 |                     0 |                  1 |
| Checks only divisibility by 5 and forgets the even-number condition                                        |             1 |                  1.3% |                  0 |                     0 |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/77` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `35/77` (`45.5%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `35/77` (`45.5%`)
- Dominant private-case vectors: `000` x35
- Score distribution (top): `0.0` x35
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `fbafd6bebfb745d39de4d843e4dc7d76`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_even_or_divisible_by_5(num:int) -> bool:
    '''
    Given an integer, check if a number is either even or divisible by 5.

    Eg.
    is_even_or_divisible_by_5(8) -> True
    is_even_or_divisible_by_5(10) -> True
    is_even_or_divisible_by_5(15) -> True
    is_even_or_divisible_by_5(7) -> False

    Args:
        num (int) : An integer.

    Returns:
        bool: True if even or if divisible by 5 else False.
    '''
    n = int(input())
    if is_even_or_divisible_by_5(8):
# ...
```

### Partially correct boolean logic, but false cases are mishandled (missing `return False` or wrong operator)

- Cluster frequency: `6/77` (`7.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `6/77` (`7.8%`)
- Dominant private-case vectors: `010` x6
- Score distribution (top): `33.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `ef89cd358be4407e83da7bfdc2d2d8e6`, summary `Wrong Answer`, score `33`, vector `010`

```python
num = int()
if num % 2 == 0 or num % 5 == 0:
    return True
else:
    return False
```

### Runtime error (parseable final submission)

- Cluster frequency: `5/77` (`6.5%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `5/77` (`6.5%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `2b3b47f75c1a4f319f9a51964eebb2d2`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_even_or_divisible_by_5(num:int) -> bool:
    '''
    Given an integer, check if a number is either even or divisible by 5.

    Eg.
    is_even_or_divisible_by_5(8) -> True
    is_even_or_divisible_by_5(10) -> True
    is_even_or_divisible_by_5(15) -> True
    is_even_or_divisible_by_5(7) -> False

    Args:
        num (int) : An integer.

    Returns:
        bool: True if even or if divisible by 5 else False.
    '''
n= int(input())
if (n%2==0 or n%5==0):
# ...
```

### Incorrect even/divisible-by-5 logic (broad wrong-answer failure)

- Cluster frequency: `5/77` (`6.5%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `5/77` (`6.5%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `db52dfa4171346d08d29ffefc9797faa`, summary `Wrong Answer`, score `0`, vector `000`

```python
if num % 5 == 0 or num % 2 == 0:
    print(True)
else:
    print(False)
return is_even_or_divisible_by_5
```

### Uses division (`/` or `//`) instead of modulus (`%`) in the divisibility test

- Cluster frequency: `4/77` (`5.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `4/77` (`5.2%`)
- Dominant private-case vectors: `000` x3, `010` x1
- Score distribution (top): `0.0` x3, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `0a18b7e5ab2e48919b9b169bb4a0e98a`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = ()  # n is a listt of integers
for i in n:
    if n // 2 == 0 or n // 5 == 0:
        return True
    else:
        return False
```

### Runtime ValueError

- Cluster frequency: `4/77` (`5.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `4/77` (`5.2%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `84001511ac004996bfb9a6b47ab85ba9`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_even_or_divisible_by_5(num:int) -> bool:
    '''
    Given an integer, check if a number is either even or divisible by 5.

    Eg.
    is_even_or_divisible_by_5(8) -> True
    is_even_or_divisible_by_5(10) -> True
    is_even_or_divisible_by_5(15) -> True
    is_even_or_divisible_by_5(7) -> False

    Args:
        num (int) : An integer.

    Returns:
        bool: True if even or if divisible by 5 else False.
    '''
num = int(input())
if is_even_or_divisible_by_5 (num%2==0 or num%5==0):
# ...
```

### Always returns `True` (constant output)

- Cluster frequency: `4/77` (`5.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `4/77` (`5.2%`)
- Dominant private-case vectors: `010` x4
- Score distribution (top): `33.0` x4
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `1276359249284d419f0429d99ecafc6a`, summary `Wrong Answer`, score `33`, vector `010`

```python
if num % 2 == 0 or num % 5 == 0:
    return True
else:
    False
```

### Runtime NameError

- Cluster frequency: `4/77` (`5.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `4/77` (`5.2%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `726e88f25f1647c896d900bbe85846a7`, summary `Runtime Error`, score `0`, vector `000`

```python
n = 25
if n % 2 == 0 or n % 5 == 0:
    print(True)
else:
    print(False)
```

### No return / implicit `None`

- Cluster frequency: `2/77` (`2.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `2/77` (`2.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `569be3ffde8841209903433ba9a86b50`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_even_or_divisible_by_5(num: int) -> bool:
    """
    Given an integer, check if a number is either even or divisible by 5.

    Eg.
    is_even_or_divisible_by_5(8) -> True
    is_even_or_divisible_by_5(10) -> True
    is_even_or_divisible_by_5(15) -> True
    is_even_or_divisible_by_5(7) -> False

    Args:
        num (int) : An integer.

    Returns:
        bool: True if even or if divisible by 5 else False.
    """
```

### Ignores the function parameter and checks a hard-coded sample number instead

- Cluster frequency: `2/77` (`2.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `2/77` (`2.6%`)
- Dominant private-case vectors: `010` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `2c31a4020a7d471e816c2e864802b4a4`, summary `Wrong Answer`, score `33`, vector `010`

```python
is_equal = 25
if is_equal % 2 == 0 or is_equal % 5 == 0:
    return True
else:
    return False
```

### Runtime TypeError

- Cluster frequency: `2/77` (`2.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `2/77` (`2.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `a4fada5b7f77414384bccef17a5eae4b`, summary `Runtime Error`, score `0`, vector `000`

```python
return is_even_or_divisible_by_5 % 2 == 0 or is_even_or_divisible_by_5 % 5 == 0
```

### Uses `and` instead of `or`, so numbers satisfying only one condition are rejected

- Cluster frequency: `2/77` (`2.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `2/77` (`2.6%`)
- Dominant private-case vectors: `000` x1, `010` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `f0080c886c2f459a90a593ae2dd6f163`, summary `Wrong Answer`, score `33`, vector `010`

```python
...
num = int()
if (num % 2 == 0) and (num % 5 == 0):
    return True
if (num % 2 == 0) and (num % 5 != 0) or (num % 2 != 0) and (num % 5 == 0):
    return False
```

### Reads `input()` inside function (EOF under evaluator function-call tests)

- Cluster frequency: `1/77` (`1.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `1/77` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `1c7611a77674468b818ef1a95c98518c`, summary `Runtime Error`, score `0`, vector `000`

```python
num = int(input())
is_even = num % 2
divisible_by_5 = num % 5
if is_even == 0:
    return True
    if divisible_by_5 == 0:
        return True
else:
    return False
return is_even_or_divisible_by_5(num)
```

### Checks only divisibility by 5 and forgets the even-number condition

- Cluster frequency: `1/77` (`1.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/2`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/5`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/5`: `1/77` (`1.3%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/5`, Student ID `343e0a82d53f4e6e9cf270799e7d0cd3`, summary `Wrong Answer`, score `67`, vector `101`

```python
if num % 5 == 0:
    return True
else:
    return False
...
```
