# Error Patterns: Cluster C015 (`Double if Even Else Square`)

## Cluster Summary

- Cluster ID: `C015`
- Cluster title: `Double if Even Else Square`
- Cluster file (this file): `analysis/ERRORS-cluster-c015-double-if-even-else-square-e8edaceb.md`
- Variants in cluster: `2`
- Total final submitters across variants: `754`
- Total non-full final submissions across variants: `79`
- Canonical variant (by submissions): `ns_25t3_py13_1/9`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py13_1/9` (canonical) |              754 |       79 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py13_1/9.json`
- Other variants in cluster:
  - `problems/ns_25t3_py13_2/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `754`
- Full pass: `675`
- Non-full final submissions: `79`
- Parseable non-full (logic/runtime focus): `49`
- Non-parseable non-full: `30`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py13_1/9` |              754 |       675 |       79 |                 49 |                     30 |
| `ns_25t3_py13_2/9` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: negative odd and positive even (checks odd squaring + even doubling together)
- Private case 2: multiple negative odds plus a positive even (catches absolute-value/negativity handling bugs)
- Private case 3: negative even and positive odd (catches sign errors in the even branch)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                            | Cluster count | % of cluster non-full | `ns_25t3_py13_1/9` | `ns_25t3_py13_2/9` |
| ------------------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | -----------------: | -----------------: |
| Syntax / non-parseable final submission                                                                            |            30 |                 38.0% |                 30 |                  0 |
| Hard-codes sample values/examples instead of using the input parameter `n`                                         |            11 |                 13.9% |                 11 |                  0 |
| No return / implicit `None`                                                                                        |            10 |                 12.7% |                 10 |                  0 |
| Reads `input()` inside function-type question (EOF under evaluator tests)                                          |             6 |                  7.6% |                  6 |                  0 |
| Runtime NameError                                                                                                  |             5 |                  6.3% |                  5 |                  0 |
| Runtime TypeError from recursively/self-calling the function without the required argument                         |             4 |                  5.1% |                  4 |                  0 |
| Runtime RecursionError                                                                                             |             3 |                  3.8% |                  3 |                  0 |
| Runtime ValueError                                                                                                 |             2 |                  2.5% |                  2 |                  0 |
| Runtime TypeError                                                                                                  |             2 |                  2.5% |                  2 |                  0 |
| Uses division (`n/2 == 0`) instead of parity test (`n % 2 == 0`)                                                   |             1 |                  1.3% |                  1 |                  0 |
| Defines a nested/redeclared `double_if_even_else_square` inside the function, so the outer function returns `None` |             1 |                  1.3% |                  1 |                  0 |
| Uses `^2` (bitwise XOR) instead of squaring (`n ** 2`)                                                             |             1 |                  1.3% |                  1 |                  0 |
| Reassigns/reads `n` inside the function instead of using the evaluator-provided argument                           |             1 |                  1.3% |                  1 |                  0 |
| Runtime AttributeError                                                                                             |             1 |                  1.3% |                  1 |                  0 |
| Incorrect even-or-square branching logic (broad wrong-answer failure)                                              |             1 |                  1.3% |                  1 |                  0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/79` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `30/79` (`38.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `30/79` (`38.0%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x30
- Score distribution (top): `0.0` x30
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `4a49cbbf781f4808804a90255a72a1c6`, summary `Runtime Error`, score `0`, vector `000`

```python
def double_if_even_else_square(n):
    """
    Given an integer n, return:
      - 2 * n if n is even
      - n ** 2 if n is odd

    Example:
        >>> double_if_even_else_square(8)
        16
        >>> double_if_even_else_square(9)
        81

    Args:
        n (int): Input integer

    Returns:
        int: Result after applying the rule
    """


# ...
```

### Hard-codes sample values/examples instead of using the input parameter `n`

- Cluster frequency: `11/79` (`13.9%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `11/79` (`13.9%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x8, `110` x3
- Score distribution (top): `0.0` x8, `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `68d14093c1d54b4c933190107c7df890`, summary `Wrong Answer`, score `0`, vector `000`

```python
if (n % 2 == 0) or (n % 2 != 0):
    return "even"
elif (n % 2 == 0) or (n % 2 != 0):
    return "even"
else:
    return "sqaure"
```

### No return / implicit `None`

- Cluster frequency: `10/79` (`12.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `10/79` (`12.7%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `ea2ebdc40749463db6d44f57ee11ea79`, summary `Wrong Answer`, score `0`, vector `000`

```python
if n % 2 == 0:
    n = n * 2
    print(n)
else:
    n = n * n
    print(n)
...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `6/79` (`7.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `6/79` (`7.6%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `d2b1588077474a168a5bdcf8607f4046`, summary `Runtime Error`, score `0`, vector `000`

```python
num = int(input("enter your number:"))
if num % 2 == 0:
    num = num * 2
    print("num is an even number")
else:
    num = num**2
    print("num is an odd number")
```

### Runtime NameError

- Cluster frequency: `5/79` (`6.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `5/79` (`6.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `598a023aa7c1450cb27d897804df9a10`, summary `Runtime Error`, score `0`, vector `000`

```python
def double_if_even_else_square(n):
    """
    Given an integer n, return:
      - 2 * n if n is even
      - n ** 2 if n is odd

    Example:
        >>> double_if_even_else_square(8)
        16
        >>> double_if_even_else_square(9)
        81

    Args:
        n (int): Input integer

    Returns:
        int: Result after applying the rule
    """


# ...
```

### Runtime TypeError from recursively/self-calling the function without the required argument

- Cluster frequency: `4/79` (`5.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `4/79` (`5.1%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `611fbf7ee6d14639870c13c4d7232401`, summary `Runtime Error`, score `0`, vector `000`

```python
...
if n % 2 == 0:
    print(int(2 * n))
else:
    print(int(n * n))
return double_if_even_else_square()
double_if_even_else_square()
```

### Runtime RecursionError

- Cluster frequency: `3/79` (`3.8%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `3/79` (`3.8%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `c9d181f26e7046889f38aee93ad55cd2`, summary `Runtime Error`, score `0`, vector `000`

```python
...
double_if_even_else_square(n)
if n % 2 == 0:
    return n * 2
else:
    return n**2
```

### Runtime ValueError

- Cluster frequency: `2/79` (`2.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `2/79` (`2.5%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `72a20d9163ad4b219ffe432f24590612`, summary `Runtime Error`, score `0`, vector `000`

```python
    if n%2==0:
         n*2
         return (n)
         k=n**2
         return(k)
    '''
    Given an integer n, return:
      - 2 * n if n is even
      - n ** 2 if n is odd

    Example:
        >>> double_if_even_else_square(8)
        16
        >>> double_if_even_else_square(9)
        81

    Args:
        n (int): Input integer
# ...
```

### Runtime TypeError

- Cluster frequency: `2/79` (`2.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `2/79` (`2.5%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `822e21e19aca41ea9ea3e62b90c06467`, summary `Runtime Error`, score `0`, vector `000`

```python
if n % 2 == 0:
    print(2 * n)
else:
    print(n**2)
return int(double_if_even_else_square)
```

### Uses division (`n/2 == 0`) instead of parity test (`n % 2 == 0`)

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `067b344cf8644117906b1e1854ecb6d3`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if n/2==0:
        return n*2

    else:
       return n**2
```

### Defines a nested/redeclared `double_if_even_else_square` inside the function, so the outer function returns `None`

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `1f105eef6bfa4b998d5c6d9ee7beff5a`, summary `Wrong Answer`, score `0`, vector `000`

```python
def double_if_even_else_square(n):
    if n % 2 == 0:
        return n * 2
    else:
        return n**2
```

### Uses `^2` (bitwise XOR) instead of squaring (`n ** 2`)

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `2f232cbc69ab477fa176bd942ea5fa5c`, summary `Wrong Answer`, score `0`, vector `000`

```python
for i in range(n):
    if i % 2 != 0:
        i = n ^ 2
    else:
        i = n * 2
    return i
```

### Reassigns/reads `n` inside the function instead of using the evaluator-provided argument

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `51f12a0d213049aa94f107684855920b`, summary `Wrong Answer`, score `0`, vector `000`

```python
result = 0
if n % 2:
    result = n * 2
else:
    result = n**2
return result
```

### Runtime AttributeError

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `abb07dab98ce4160a6725b210bf19bc5`, summary `Runtime Error`, score `0`, vector `000`

```python
...
if n % 2 == 0:
    print(2 * n)
else:
    print(n**2)
return n.type()
```

### Incorrect even-or-square branching logic (broad wrong-answer failure)

- Cluster frequency: `1/79` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/9`: `1/79` (`1.3%`)
  - `ns_25t3_py13_2/9`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/9`, Student ID `c633d8ec297b4cfc98dc9b1e37a5bd24`, summary `Wrong Answer`, score `0`, vector `000`

```python
if n // 2 != 0:
    result = n * 2
else:
    result = n**2
return result
```
