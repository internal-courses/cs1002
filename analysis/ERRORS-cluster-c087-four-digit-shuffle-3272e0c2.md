# Error Patterns: Cluster C087 (`Four Digit Shuffle`)

## Cluster Summary

- Cluster ID: `C087`
- Cluster title: `Four Digit Shuffle`
- Cluster file (this file): `analysis/ERRORS-cluster-c087-four-digit-shuffle-3272e0c2.md`
- Variants in cluster: `1`
- Total final submitters across variants: `751`
- Total non-full final submissions across variants: `176`
- Canonical variant (by submissions): `ns_25t2_py13_2/7`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_2/7` (canonical) |              751 |      176 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `751`
- Full pass: `575`
- Non-full final submissions: `176`
- Parseable non-full (logic/runtime focus): `126`
- Non-parseable non-full: `50`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_2/7` |              751 |       575 |      176 |                126 |                     50 |

## Private Case Structure

- Private case 1: 4-cycle shuffle on hidden digits (`1825 -> 8512 -> 5281 -> 2158 -> 1825`)
- Private case 2: second hidden 4-cycle (`7395 -> 3579 -> 5937 -> 9753 -> 7395`) to catch public-case hard-coding

Private-case vectors in this report are 2-character pass/fail strings over the private case groups (e.g., `11` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                          | Cluster count | % of cluster non-full | `ns_25t2_py13_2/7` |
| ---------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: |
| Syntax / non-parseable final submission                                                                          |            50 |                 28.4% |                 50 |
| Runtime TypeError from treating integer input `num` as a sequence/function during digit shuffling                |            29 |                 16.5% |                 29 |
| No return / implicit `None`                                                                                      |            26 |                 14.8% |                 26 |
| Runtime NameError                                                                                                |            12 |                  6.8% |                 12 |
| Reads `input()` inside function-type question (EOF under evaluator tests)                                        |            11 |                  6.2% |                 11 |
| Incorrect four-digit shuffle logic (fails hidden cycles; often hard-coded, no-return, or wrong digit extraction) |            11 |                  6.2% |                 11 |
| Runtime TypeError                                                                                                |             7 |                  4.0% |                  7 |
| Returns the original number unchanged instead of shuffling digits to order `2413`                                |             5 |                  2.8% |                  5 |
| Hard-codes public example shuffle cycles instead of computing the `2413` digit permutation                       |             5 |                  2.8% |                  5 |
| Defines a nested/redeclared `shuffle_digits` inside the function, so the outer function returns `None`           |             5 |                  2.8% |                  5 |
| Runtime IndexError from invalid list/string indexing while reordering the four digits                            |             4 |                  2.3% |                  4 |
| Time Limit Exceeded                                                                                              |             2 |                  1.1% |                  2 |
| Runtime TypeError from broken string-digit reconstruction / type mixing in shuffle output                        |             2 |                  1.1% |                  2 |
| Runtime RecursionError                                                                                           |             2 |                  1.1% |                  2 |
| Runtime error (parseable final submission)                                                                       |             2 |                  1.1% |                  2 |
| Builds the correct-looking reordered digits as a string but returns a string instead of an integer               |             2 |                  1.1% |                  2 |
| Extracts one digit and returns too early (never reconstructs the 4-digit shuffled result)                        |             1 |                  0.6% |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/176` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `50/176` (`28.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `50/176` (`28.4%`)
- Dominant private-case vectors: `00` x50
- Score distribution (top): `0.0` x50
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `1f654fcd6d9b494a91d18e984c56b302`, summary `Runtime Error`, score `0`, vector `00`

```python
def shuffle_digits(num: int) -> int:
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
        int: digit shuffled integer.
# ...
```

### Runtime TypeError from treating integer input `num` as a sequence/function during digit shuffling

- Cluster frequency: `29/176` (`16.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `29/176` (`16.5%`)
- Dominant private-case vectors: `00` x29
- Score distribution (top): `0.0` x29
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `b5941bb35f744f8fbaeaff409632d94f`, summary `Runtime Error`, score `0`, vector `00`

```python
    n=[]
    for num in num:
        num[2]=num[0]
        num[3]=num[1]
        num[0]=num[2]
        num[2]=num[3]
    num=int(input)
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234
# ...
```

### No return / implicit `None`

- Cluster frequency: `26/176` (`14.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `26/176` (`14.8%`)
- Dominant private-case vectors: `00` x26
- Score distribution (top): `0.0` x26
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `a529a2786ceb48a0b613ef637bd59938`, summary `Wrong Answer`, score `0`, vector `00`

```python
count = num
for i in range(0, 4):
    j = 4
    count = num / 10
    r = count // 10
    f = r
    f = f + f * j
    j = j - 1
print(f)
```

### Runtime NameError

- Cluster frequency: `12/176` (`6.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `12/176` (`6.8%`)
- Dominant private-case vectors: `00` x12
- Score distribution (top): `0.0` x12
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `0e39642d48fe45498b63fb9f7cfcdc18`, summary `Runtime Error`, score `0`, vector `00`

```python
def shuffle_digits(w,x,y,z):
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
        int: digit shuffled integer.
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `11/176` (`6.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `11/176` (`6.2%`)
- Dominant private-case vectors: `00` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `e4d0042a411b4eeba91349f6523b7db8`, summary `Runtime Error`, score `0`, vector `00`

```python
shuffle_digits = int(input("Enter a 4 digit number"))
shuffle_digits[0] = shuffle_digits[2]
shuffle_digits[1] = shuffle_digits[0]
shuffle_digits[3] = shuffle_digits[1]
shuffle_digits[2] = shuffle_digits[3]
return shuffle_digits
...
```

### Incorrect four-digit shuffle logic (fails hidden cycles; often hard-coded, no-return, or wrong digit extraction)

- Cluster frequency: `11/176` (`6.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `11/176` (`6.2%`)
- Dominant private-case vectors: `00` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `35b44eca461c4fb087bdd7d49f7ff41a`, summary `Wrong Answer`, score `0`, vector `00`

```python
    print("2413")
    return(num)
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
# ...
```

### Runtime TypeError

- Cluster frequency: `7/176` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `7/176` (`4.0%`)
- Dominant private-case vectors: `00` x7
- Score distribution (top): `0.0` x7
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `67c43c2e0185468a98880534df61948b`, summary `Runtime Error`, score `0`, vector `00`

```python
def shuffle_digits(num: int) -> int:
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
        int: digit shuffled integer.
# ...
```

### Returns the original number unchanged instead of shuffling digits to order `2413`

- Cluster frequency: `5/176` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `5/176` (`2.8%`)
- Dominant private-case vectors: `00` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `8bbc7935034d40c2ad7471df8d4f7a0f`, summary `Wrong Answer`, score `0`, vector `00`

```python
...
listnum = str(num).split()
result = ""
for i in str(num):
    if i in listnum:
        i[0] = i[2]
        i[1] = i[0]
        i[2] = i[3]
        i[3] = i[1]
return num
```

### Hard-codes public example shuffle cycles instead of computing the `2413` digit permutation

- Cluster frequency: `5/176` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `5/176` (`2.8%`)
- Dominant private-case vectors: `00` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `50a9b053ea51456488590d0a4511144c`, summary `Wrong Answer`, score `0`, vector `00`

```python
if num == 1234:
    return 2413
if num == 2413:
    return 4321
if num == 4321:
    return 3142
if num == 3142:
    return 1234
if num == 5678:
    return 6857
if num == 6857:
    return 8765
if num == 8765:
    return 7586
if num == 7586:
    return 5678
```

### Defines a nested/redeclared `shuffle_digits` inside the function, so the outer function returns `None`

- Cluster frequency: `5/176` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `5/176` (`2.8%`)
- Dominant private-case vectors: `00` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `6319ed22c9b240658f30a8abf60ab90c`, summary `Wrong Answer`, score `0`, vector `00`

```python
def shuffle_digits(num: int) -> int:
    '''Returns the number with digits shuffled in order 2413.

    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
        int: digit shuffled integer.
# ...
```

### Runtime IndexError from invalid list/string indexing while reordering the four digits

- Cluster frequency: `4/176` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `4/176` (`2.3%`)
- Dominant private-case vectors: `00` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `fa681042497049d687d63401ee2abb96`, summary `Runtime Error`, score `0`, vector `00`

```python
...
num = " "
digits_num = num.split(" ")
shuffle_num = []
shuffle_num[0] = digits_num[1]
shuffle_num[1] = digits_num[3]
shuffle_num[2] = digits_num[0]
shuffle_num[3] = digits_num[2]
return shuffle_num
```

### Time Limit Exceeded

- Cluster frequency: `2/176` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `2/176` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `0d778020785b44d6a38a70444495b53c`, summary `Time Limit Exceeded`, score `0`, vector `00`

```python
while num != 0:
    fd = num // 1000
    ld = num % 10
    sd = num // 100 - fd * 10
    td = num // 10 - (num // 100 * 10)
nnum = 1000 * sd + 100 * ld + 10 * fd + td
return nnum
```

### Runtime TypeError from broken string-digit reconstruction / type mixing in shuffle output

- Cluster frequency: `2/176` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `2/176` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `c8472f5d0cb44df3b2ed8d33f0cd5cbe`, summary `Runtime Error`, score `0`, vector `00`

```python
...
digits = int(num)
return int(digits[1] + digits[3] + digits[0], digits[2])
```

### Runtime RecursionError

- Cluster frequency: `2/176` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `2/176` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `1691a5c1e7444db5b54c803439538174`, summary `Runtime Error`, score `0`, vector `00`

```python
is_equal(shuffle_digits(1234), 2413)
is_equal(shuffle_digits(2413), 4321)
is_equal(shuffle_digits(4321), 3142)
is_equal(shuffle_digits(3142), 1234)
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/176` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `2/176` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `63394f80fa6b4cf4bfc00fd7fff06946`, summary `Runtime Error`, score `0`, vector `00`

```python
def shuffle_digits(num: int) -> int:

    '''Returns the number with digits shuffled in order 2413.
    Examples:
    >>> shuffle_digits(1234)
    2413
    >>> shuffle_digits(2413)
    4321
    >>> shuffle_digits(4321)
    3142
    >>> shuffle_digits(3142)
    1234

    Args:
        num (int): A 4-digit positive integer

    Returns:
        int: digit shuffled integer.
# ...
```

### Builds the correct-looking reordered digits as a string but returns a string instead of an integer

- Cluster frequency: `2/176` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `2/176` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `f7f6eafcceab429ca88e5642658b1aff`, summary `Wrong Answer`, score `0`, vector `00`

```python
...
lis = str(num)
mis = lis.split(",")
return mis[1::2] + mis[0::2]
```

### Extracts one digit and returns too early (never reconstructs the 4-digit shuffled result)

- Cluster frequency: `1/176` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/7`: `1/176` (`0.6%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/7`, Student ID `06bea7c0d9c9426e9646ccc40b9780ca`, summary `Wrong Answer`, score `0`, vector `00`

```python
n = 0
while True:
    if n == 0:
        return (num % 1000 - num % 100) // 100
        pass
    if n == 1:
        return num % 10
        pass
    if n == 2:
        return (num % 100 - num % 10) // 10
        pass
    if n == 3:
        return (num - num % 1000) // 1000
        break
```
