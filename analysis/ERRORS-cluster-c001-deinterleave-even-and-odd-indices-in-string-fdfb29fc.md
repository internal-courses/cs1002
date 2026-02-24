# Error Patterns: Cluster C001 (`Deinterleave Even and Odd Indices in String`)

## Cluster Summary

- Cluster ID: `C001`
- Cluster title: `Deinterleave Even and Odd Indices in String`
- Cluster file (this file): `analysis/ERRORS-cluster-c001-deinterleave-even-and-odd-indices-in-string-fdfb29fc.md`
- Variants in cluster: `4`
- Total final submitters across variants: `578`
- Total non-full final submissions across variants: `108`
- Canonical variant (by submissions): `ns_25t2_py12_1/6`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py12_1/6` (canonical) |              578 |      108 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py12_1/6.json`
- Other variants in cluster:
  - `problems/ns_25t1_py11_1/3.json`
  - `problems/ns_25t1_py_15_exe/6.json`
  - `problems/ns_25t3_py21/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `578`
- Full pass: `470`
- Non-full final submissions: `108`
- Parseable non-full (logic/runtime focus): `77`
- Non-parseable non-full: `31`

Variant-level comparison:

| Variant               | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t1_py11_1/3`    |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t1_py_15_exe/6` |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t2_py12_1/6`    |              578 |       470 |      108 |                 77 |                     31 |
| `ns_25t3_py21/7`      |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: longer string (`programming`) to catch fixed-slice and duplicate-character index bugs
- Private case 2: odd-length simple string (`abcdefg`) baseline deinterleaving
- Private case 3: 10-character numeric string to catch sample hard-coding / fixed-`10` slicing assumptions

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                       | Cluster count | % of cluster non-full | `ns_25t1_py11_1/3` | `ns_25t1_py_15_exe/6` | `ns_25t2_py12_1/6` | `ns_25t3_py21/7` |
| ------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: | --------------------: | -----------------: | ---------------: |
| Syntax / non-parseable final submission                                                                       |            31 |                 28.7% |                  0 |                     0 |                 31 |                0 |
| Incorrect deinterleaving logic (broad wrong-answer failure)                                                   |            19 |                 17.6% |                  0 |                     0 |                 19 |                0 |
| No return / implicit `None`                                                                                   |            15 |                 13.9% |                  0 |                     0 |                 15 |                0 |
| Runtime TypeError from treating string characters as numbers / invalid indexing while deinterleaving          |             9 |                  8.3% |                  0 |                     0 |                  9 |                0 |
| Hard-codes sample outputs instead of deinterleaving the input string generically                              |             8 |                  7.4% |                  0 |                     0 |                  8 |                0 |
| Runtime NameError from undefined variables in deinterleaving logic                                            |             7 |                  6.5% |                  0 |                     0 |                  7 |                0 |
| Runtime error (parseable final submission)                                                                    |             5 |                  4.6% |                  0 |                     0 |                  5 |                0 |
| Uses `s.index(char)` while iterating characters, so duplicate characters get the wrong parity/index           |             3 |                  2.8% |                  0 |                     0 |                  3 |                0 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests)                       |             2 |                  1.9% |                  0 |                     0 |                  2 |                0 |
| Runtime RecursionError from accidental recursive `deinterleave(...)` call                                     |             2 |                  1.9% |                  0 |                     0 |                  2 |                0 |
| Runtime IndexError from manual indexing/slicing mistakes while splitting even/odd positions                   |             2 |                  1.9% |                  0 |                     0 |                  2 |                0 |
| Copied code from a different question (`is_even_or_divisible_by_5`) causing NameError/wrong-function behavior |             1 |                  0.9% |                  0 |                     0 |                  1 |                0 |
| Uses fixed `0:10` slices, so longer strings are truncated and shorter cases are handled accidentally          |             1 |                  0.9% |                  0 |                     0 |                  1 |                0 |
| Runtime ValueError                                                                                            |             1 |                  0.9% |                  0 |                     0 |                  1 |                0 |
| Runtime AttributeError                                                                                        |             1 |                  0.9% |                  0 |                     0 |                  1 |                0 |
| Appends a hard-coded odd-index suffix (e.g., `"bdf"`) instead of computing all odd-index characters           |             1 |                  0.9% |                  0 |                     0 |                  1 |                0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/108` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `31/108` (`28.7%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `31/108` (`28.7%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x31
- Score distribution (top): `0.0` x31
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `a4193fbd439f43b2a470cc3be4d21851`, summary `Runtime Error`, score `0`, vector `000`

```python
    def deinterleave(s: str) -> str:
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """

    evenindicesletterslist=[]
    oddindicesletterslist=[]
    for i in range(0, len(s)+1):
    	if i%2==0:
    		evenindicesletters=s[i]
    		evenindicesletterslist.append(evenindicesletters)
    	else:
# ...
```

### Incorrect deinterleaving logic (broad wrong-answer failure)

- Cluster frequency: `19/108` (`17.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `19/108` (`17.6%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x19
- Score distribution (top): `0.0` x19
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `737fd731527c4bfb8a1c3cdec0db9513`, summary `Wrong Answer`, score `0`, vector `000`

```python
    even_char = ""
    odd_char = ""
    for i, char in enumerate(s):
        if i%2 == 0:
            even_char += char
        else:
            odd_char += char
    return even_char, odd_char
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """
    ...
```

### No return / implicit `None`

- Cluster frequency: `15/108` (`13.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `15/108` (`13.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `5753c1c7684e4182b77807569c06403e`, summary `Wrong Answer`, score `0`, vector `000`

```python
def deinterleave(s: str) -> str:
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """
```

### Runtime TypeError from treating string characters as numbers / invalid indexing while deinterleaving

- Cluster frequency: `9/108` (`8.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `9/108` (`8.3%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `b4bdbb79ede24c5096334c6f790f7a71`, summary `Runtime Error`, score `0`, vector `000`

```python
    for i in s:
        even=[]
        # ei=
        odd=[]
        if [i]%2==0:
            even.append(i)
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """
    ...
```

### Hard-codes sample outputs instead of deinterleaving the input string generically

- Cluster frequency: `8/108` (`7.4%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `8/108` (`7.4%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `f874da52094342f39d3e03ebf0318698`, summary `Wrong Answer`, score `0`, vector `000`

```python
even_chars = s[::2]  # characters at even indices
odd_chars = s[1::-2]  # characters at odd indices
return
even_chars + odd_chars
Example
deinterleave("abcdef")  # output:"acebdf"
```

### Runtime NameError from undefined variables in deinterleaving logic

- Cluster frequency: `7/108` (`6.5%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `7/108` (`6.5%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `919d97d6ab5642218427db0aa5a6d703`, summary `Runtime Error`, score `0`, vector `000`

```python
...
new_s1 = ""
new_s2 = ""
alnum = "abcdefghijklmnopqrstuvwxyz0123456789"
i = 0
for char in s:
    if char in alnum:
        if (index(s[i]) % 2) == 0:
            append.new_s1(s[i])
        else:
            append.new_s2(s[i])
    return new_s1 + new_s2
```

### Runtime error (parseable final submission)

- Cluster frequency: `5/108` (`4.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `5/108` (`4.6%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `9facbfdac2c34774ab83d3f1fe012451`, summary `Runtime Error`, score `0`, vector `000`

```python
def deinterleave(s: str) -> str:
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """


even_chars = s[::2]
odd_chars = s[1::2]
return even_chars + odd_chars
```

### Uses `s.index(char)` while iterating characters, so duplicate characters get the wrong parity/index

- Cluster frequency: `3/108` (`2.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `3/108` (`2.8%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x2, `000` x1
- Score distribution (top): `67.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `741e32a668584cf0ae3f3a4e37cd8f2c`, summary `Wrong Answer`, score `67`, vector `011`

```python
sen = ""
for c in s:
    if s.index(c) % 2 == 0:
        sen += c
    else:
        continue
for c in s:
    if s.index(c) % 2 != 0:
        sen += c
    else:
        continue
return sen
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `2/108` (`1.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `2/108` (`1.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `2b3b47f75c1a4f319f9a51964eebb2d2`, summary `Runtime Error`, score `0`, vector `000`

```python
deinterleaved = str(input())
is_equal(deinterleaved(str), str[1:3:5] + str[2:4:6])
print(str)
```

### Runtime RecursionError from accidental recursive `deinterleave(...)` call

- Cluster frequency: `2/108` (`1.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `2/108` (`1.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `ff303edd855c416bbf01e2d622bc7b0d`, summary `Runtime Error`, score `0`, vector `000`

```python
s = "apple"
is_equal(deinterleave("apple"))
```

### Runtime IndexError from manual indexing/slicing mistakes while splitting even/odd positions

- Cluster frequency: `2/108` (`1.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `2/108` (`1.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `ba1006f15b51476895fec2e7026f788b`, summary `Runtime Error`, score `0`, vector `000`

```python
for i in (0, len(s), 2):
    even_chars = s[i]
for i in (1, len(s), 2):
    odd_chars = s[i]
return "".join(even_chars + odd_chars)
```

### Copied code from a different question (`is_even_or_divisible_by_5`) causing NameError/wrong-function behavior

- Cluster frequency: `1/108` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `1/108` (`0.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `052cc618d53b4caeb5acb2b72a2fd80c`, summary `Runtime Error`, score `0`, vector `000`

```python
return num % 2 == 0 or num % 5 == 0
```

### Uses fixed `0:10` slices, so longer strings are truncated and shorter cases are handled accidentally

- Cluster frequency: `1/108` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `1/108` (`0.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `0a5a1efb498c4150b87ed4e29b828b8d`, summary `Wrong Answer`, score `67`, vector `011`

```python
    return s[0:10:2]+s[1:10:2]
    """
    Deinterleave even and odd indices in a string.

    Args:
        s (str): The input string.

    Returns:
        str: The deinterleaved string.
    """
```

### Runtime ValueError

- Cluster frequency: `1/108` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `1/108` (`0.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `7765059a942146869e3cfa8b5b89b00a`, summary `Runtime Error`, score `0`, vector `000`

```python
s = int(s)
s_new = ""
s_odd = ""
for i in range(s):
    if i % 2 == 0:
        s_new += s_new + i
    else:
        s_odd += s_odd + i
return s_new + s_odd
```

### Runtime AttributeError

- Cluster frequency: `1/108` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `1/108` (`0.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `e11aac45f6eb4c9b9434941604889c06`, summary `Runtime Error`, score `0`, vector `000`

```python
length = str.len
if length // 2 == 0:
    if length[:2]:
        str.slice(str)
else:
    return str
```

### Appends a hard-coded odd-index suffix (e.g., `"bdf"`) instead of computing all odd-index characters

- Cluster frequency: `1/108` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/3`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/6`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/6`: `1/108` (`0.9%`)
  - `ns_25t3_py21/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/6`, Student ID `e58a08cc77a6445db66593f23bc20af4`, summary `Wrong Answer`, score `33`, vector `010`

```python
return s[::2] + f"bdf"
```
