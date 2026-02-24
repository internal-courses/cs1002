# Error Patterns: Cluster C091 (`Compare Last Digits`)

## Cluster Summary

- Cluster ID: `C091`
- Cluster title: `Compare Last Digits`
- Cluster file (this file): `analysis/ERRORS-cluster-c091-compare-last-digits-8b9d388d.md`
- Variants in cluster: `1`
- Total final submitters across variants: `628`
- Total non-full final submissions across variants: `169`
- Canonical variant (by submissions): `ns_25t3_py11/8`

Cluster membership (zero-submitter variants omitted):

| Variant                      | final_submitters | non_full | Relationship                 |
| ---------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py11/8` (canonical) |              628 |      169 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py11/8.json`

## Cluster-Level Outcome Summary

- Final submitters: `628`
- Full pass: `459`
- Non-full final submissions: `169`
- Parseable non-full (logic/runtime focus): `109`
- Non-parseable non-full: `60`

Variant-level comparison:

| Variant          | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ---------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py11/8` |              628 |       459 |      169 |                109 |                     60 |

## Private Case Structure

- Private case 1: same-last-digit vs different-last-digit hidden pairs (core `%10` comparison)
- Private case 2: cases where full numbers differ but last digits match (catches full-number equality bug)
- Private case 3: additional mixed pairs to catch num1/num2 misuse and wrong-digit extraction

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                      | Cluster count | % of cluster non-full | `ns_25t3_py11/8` |
| -------------------------------------------------------------------------------------------- | ------------: | --------------------: | ---------------: |
| Syntax / non-parseable final submission                                                      |            60 |                 35.5% |               60 |
| Incorrect last-digit comparison logic (broad wrong-answer failure)                           |            34 |                 20.1% |               34 |
| Runtime TypeError from indexing integers directly instead of using `% 10` / `str(...)`       |            17 |                 10.1% |               17 |
| Runtime NameError from wrong variable names in last-digit comparison                         |            13 |                  7.7% |               13 |
| No return / implicit `None`                                                                  |            12 |                  7.1% |               12 |
| Compares the full numbers for equality instead of comparing only the last digits             |            10 |                  5.9% |               10 |
| Runtime TypeError                                                                            |             6 |                  3.6% |                6 |
| Reads `input()` inside function-type question (EOF under evaluator tests)                    |             6 |                  3.6% |                6 |
| Runtime error (parseable final submission)                                                   |             3 |                  1.8% |                3 |
| Runtime RecursionError                                                                       |             3 |                  1.8% |                3 |
| Runtime ValueError                                                                           |             2 |                  1.2% |                2 |
| Partially correct last-digit comparison (uses wrong variable/digit extraction in some cases) |             1 |                  0.6% |                1 |
| Uses parity/even-odd checks instead of comparing the last digits                             |             1 |                  0.6% |                1 |
| Runtime NameError                                                                            |             1 |                  0.6% |                1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/169` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `60/169` (`35.5%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `60/169` (`35.5%`)
- Dominant private-case vectors: `000` x60
- Score distribution (top): `0.0` x60
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `a1db6afedd6046a58e3329e908b7c50a`, summary `Runtime Error`, score `0`, vector `000`

```python
def compare_last_digits(num1: int, num2: int) -> str:
    """
    Given two integers, check whether their last digits are the same.

    Args:
        num1 (int): First number
        num2 (int): Second number

    Returns:
        str: "same" if last digits match else "different"
    """
    ...


def compare_last_digits(num1: int, num2: int) -> str:
    # Given two integers, check whether their last digits are the same.
    num1: 123  # first number
    num2: 43  # second number


# ...
```

### Incorrect last-digit comparison logic (broad wrong-answer failure)

- Cluster frequency: `34/169` (`20.1%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `34/169` (`20.1%`)
- Dominant private-case vectors: `000` x34
- Score distribution (top): `0.0` x34
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `4dae8ff6ff954036b4603a7920f8b848`, summary `Wrong Answer`, score `0`, vector `000`

```python
    g=0
    e="same"
    f="different"
    c="num1"
    d="num2"
    a=c[-1]
    b=d[-1]
    if a==b:
        g+=1
    else:
        g+=2
        if g==1:
            return e
        else :
            return f
    '''
    Given two integers, check whether their last digits are the same.

# ...
```

### Runtime TypeError from indexing integers directly instead of using `% 10` / `str(...)`

- Cluster frequency: `17/169` (`10.1%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `17/169` (`10.1%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `2cf2d9cca6fa4059b3ddcc60c36685f6`, summary `Runtime Error`, score `0`, vector `000`

```python
    last_digit_num1 = num1[-1]
    last_digit_num2 = num2[-1]
    if last_digit_num1 == last_digit_num2:
        return same

    else:
        return different
```

### Runtime NameError from wrong variable names in last-digit comparison

- Cluster frequency: `13/169` (`7.7%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `13/169` (`7.7%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `aec87f7f7a5a408191523e17556d422a`, summary `Runtime Error`, score `0`, vector `000`

```python
...
num1 = str(num1)
l1 = num1[-1]
num2 = str(num2)
l2 = num2[-1]
a = same
b = different
if l1 == l2:
    print(a)
else:
    print(b)
return
```

### No return / implicit `None`

- Cluster frequency: `12/169` (`7.1%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `12/169` (`7.1%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `52366b5b9bbc4774b3055edecfe53d32`, summary `Wrong Answer`, score `0`, vector `000`

```python
def compare_last_digits(num1: int, num2: int) -> str:
    """
    Given two integers, check whether their last digits are the same.

    Args:
        num1 (int): First number
        num2 (int): Second number

    Returns:
        str: "same" if last digits match else "different"
    """
```

### Compares the full numbers for equality instead of comparing only the last digits

- Cluster frequency: `10/169` (`5.9%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `10/169` (`5.9%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `19932c940353412d87cce7f3af903769`, summary `Wrong Answer`, score `0`, vector `000`

```python
num1 = 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
num2 = 1, 2, 3, 4, 6, 7, 8, 9, 0
if num1 == num2:
    return True
else:
    return False
```

### Runtime TypeError

- Cluster frequency: `6/169` (`3.6%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `6/169` (`3.6%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `ef9ab5ae9d0740d99587ed37b9a39f8c`, summary `Runtime Error`, score `0`, vector `000`

```python
    n1=str(num1)
    n2=str(num2)
    if n1(-1)==n2(-1):
        return 'same'
    else:
        return 'different'
    '''
    Given two integers, check whether their last digits are the same.

    Args:
        num1 (int): First number
        num2 (int): Second number

    Returns:
        str: "same" if last digits match else "different"
    '''
    ...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `6/169` (`3.6%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `6/169` (`3.6%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `b03f2fe5dcd14b35bbf374e205abd2af`, summary `Runtime Error`, score `0`, vector `000`

```python
...
a = int(input("Enter your num1: "))
b = int(input("Enter your num2: "))
if a % 10 == 0 and b % 10 == 0:
    print("if last digits match: same")
else:
    print("different")
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/169` (`1.8%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `3/169` (`1.8%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `0bb38722278b44d59931ccdb205777e8`, summary `Runtime Error`, score `0`, vector `000`

```python
if num1 == num2:
    return "same"
elif num2 % num1 == num2:
    return "same"
else:
    return "different"
```

### Runtime RecursionError

- Cluster frequency: `3/169` (`1.8%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `3/169` (`1.8%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `8a5fc7686ad940999cffe5aeb3dc142b`, summary `Runtime Error`, score `0`, vector `000`

```python
last_digit_of_num1 = num1
last_digit_of_num2 = num2
if compare_last_digits(num1, num2):
    return "same"
else:
    return "different"
```

### Runtime ValueError

- Cluster frequency: `2/169` (`1.2%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `2/169` (`1.2%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `28c88101f6f24942abcc8b2b0b20c2a5`, summary `Runtime Error`, score `0`, vector `000`

```python
    num1 = int("Any numbers from 0,1,2,3,4,5,6,7,8,9")
    num2 = int("Any numbers from 0,1,2,3,4,5,6,7,8,9")
    last_digits_num1 = last_digits(num1)
    last_digits_num2 = last_digit(num2)
    if last_digits_num1 == last_digits_num2 :
        return "same"

    else:
        return "different"
```

### Partially correct last-digit comparison (uses wrong variable/digit extraction in some cases)

- Cluster frequency: `1/169` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `1/169` (`0.6%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `58778bb350c64d84975d6734a854dad2`, summary `Wrong Answer`, score `33`, vector `010`

```python
num1 = str(num1)
num2 = str(num2)
if num1[:1] == num2[-1:]:
    return "same"
else:
    return "different"
```

### Uses parity/even-odd checks instead of comparing the last digits

- Cluster frequency: `1/169` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `1/169` (`0.6%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `b0a52dc61da6496db21fb1fcf98fde8e`, summary `Wrong Answer`, score `33`, vector `001`

```python
if num1 % 2 == 0 and num2 % 2 == 0:
    return "same"
elif num1 % 3 == 1 and num2 % 3 == 1:
    return "same"
else:
    return "different"
```

### Runtime NameError

- Cluster frequency: `1/169` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py11/8`: `1/169` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/8`, Student ID `b3dab4ca0ba64e4681cffe714e6a69ed`, summary `Runtime Error`, score `0`, vector `000`

```python
...
```
