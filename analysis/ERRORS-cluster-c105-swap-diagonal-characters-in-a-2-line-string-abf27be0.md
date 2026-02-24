# Error Patterns: Cluster C105 (`Swap Diagonal Characters in a 2‑Line String`)

## Cluster Summary

- Cluster ID: `C105`
- Cluster title: `Swap Diagonal Characters in a 2‑Line String`
- Cluster file (this file): `analysis/ERRORS-cluster-c105-swap-diagonal-characters-in-a-2-line-string-abf27be0.md`
- Variants in cluster: `1`
- Total final submitters across variants: `394`
- Total non-full final submissions across variants: `75`
- Canonical variant (by submissions): `ns_25t3_py22/5`

Cluster membership (zero-submitter variants omitted):

| Variant                      | final_submitters | non_full | Relationship                 |
| ---------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py22/5` (canonical) |              394 |       75 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py22/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `394`
- Full pass: `319`
- Non-full final submissions: `75`
- Parseable non-full (logic/runtime focus): `52`
- Non-parseable non-full: `23`

Variant-level comparison:

| Variant          | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ---------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py22/5` |              394 |       319 |       75 |                 52 |                     23 |

## Private Case Structure

- Private case 1: mixed letters/digits with newline-preserving reversal (`AA\nBB`, `q1\n2r`)
- Private case 2: symmetric/unchanged cases (`!!\n!!`, `ab\nba`) to catch unnecessary mutation or constant-output code
- Private case 3: additional alphanumeric/string cases to verify general 2-line transformation (not sample-specific)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                | Cluster count | % of cluster non-full | `ns_25t3_py22/5` |
| ------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | ---------------: |
| Syntax / non-parseable final submission                                                                |            23 |                 30.7% |               23 |
| Incorrect 2-line string diagonal-swap logic (constant output, wrong indexing, or wrong return type)    |            15 |                 20.0% |               15 |
| No return / implicit `None`                                                                            |            11 |                 14.7% |               11 |
| Runtime NameError                                                                                      |             6 |                  8.0% |                6 |
| Returns the public sample output (`'dc\nba'`) as a constant instead of transforming the input          |             3 |                  4.0% |                3 |
| Returns the input string unchanged (no diagonal swap applied)                                          |             3 |                  4.0% |                3 |
| Runtime TypeError                                                                                      |             3 |                  4.0% |                3 |
| Uses `str.replace(...)` on sample substrings / no-op replacements instead of positional swapping       |             2 |                  2.7% |                2 |
| Builds/returns the wrong type (tuple/list) instead of the required transformed string                  |             1 |                  1.3% |                1 |
| Uses invalid string/list APIs while trying to reverse/swap the 2-line string                           |             1 |                  1.3% |                1 |
| Treats the input as a 4-character string and ignores the newline separator, so row positions are wrong |             1 |                  1.3% |                1 |
| Calls `swap_diagonals(...)` from inside itself (copied self-test/sample call) causing recursion        |             1 |                  1.3% |                1 |
| Splits on `'/'` instead of the required newline (`'\n'`), so hidden inputs cannot be unpacked          |             1 |                  1.3% |                1 |
| Returns a tuple of row fragments instead of one newline-joined string                                  |             1 |                  1.3% |                1 |
| Splits rows correctly but reassembles characters in the wrong order (`db\nca`-style column swap)       |             1 |                  1.3% |                1 |
| Runtime AttributeError                                                                                 |             1 |                  1.3% |                1 |
| Treats the 2-line string like a nested list/string matrix (`s[1][1]`), causing indexing errors         |             1 |                  1.3% |                1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/75` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `23/75` (`30.7%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `23/75` (`30.7%`)
- Dominant private-case vectors: `000` x23
- Score distribution (top): `0.0` x23
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `91377c81c33547d78d8a4ea9e348a538`, summary `Runtime Error`, score `0`, vector `000`

```python
def swap_diagonals(s: str) -> str:
    """
    Swaps the two diagonal characters of a 2x2 grid represented as a
    two-line string.

    Example:
        >>> swap_diagonals("ab\ncd")
        'dc\nba'

    Args:
        s (str): Two-line string, each line exactly two characters.

    Returns:
        str: New two-line string after swapping both diagonals.
    """
    ...
    line1, line2 = s.split("\n")
    a, b = line1[0] + line1[1]


# ...
```

### Incorrect 2-line string diagonal-swap logic (constant output, wrong indexing, or wrong return type)

- Cluster frequency: `15/75` (`20.0%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `15/75` (`20.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `b327a9e2a2cb49c38e502835f4959f10`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if s[0:1]=='x':
        st="wz\nyx"
    elif s[0:1]=='1':
        st="43\n21"
    else:
        st="dc\nba"
    return st
    """
    Swaps the two diagonal characters of a 2x2 grid represented as a
    two-line string.

    Example:
        >>> swap_diagonals("ab\ncd")
        'dc\nba'

    Args:
        s (str): Two-line string, each line exactly two characters.

# ...
```

### No return / implicit `None`

- Cluster frequency: `11/75` (`14.7%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `11/75` (`14.7%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `9f8feef320ed41999a06ec569a457209`, summary `Wrong Answer`, score `0`, vector `000`

```python
print("dcba")
```

### Runtime NameError

- Cluster frequency: `6/75` (`8.0%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `6/75` (`8.0%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `6d0778a45dc241288514b5a2d0c41ff2`, summary `Runtime Error`, score `0`, vector `000`

```python
s = ab / ncd
main_diagonl = s(c00 - c11)
anti_diagonal = s(c01 - c10)
swap_diagonals = main_diagonl / nanti_diagonal
print(swap_diagonals)
```

### Returns the public sample output (`'dc\nba'`) as a constant instead of transforming the input

- Cluster frequency: `3/75` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `3/75` (`4.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `0c796407724441a482dd8912fa4831c6`, summary `Wrong Answer`, score `0`, vector `000`

```python
return "dc\nba"
```

### Returns the input string unchanged (no diagonal swap applied)

- Cluster frequency: `3/75` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `3/75` (`4.0%`)
- Dominant private-case vectors: `010` x3
- Score distribution (top): `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `d3e87e1156dd4d3789ec7d7a59ebc06e`, summary `Wrong Answer`, score `33`, vector `010`

```python
...
for i in range(1, 1):
    s[0][0] == s[0][1]
    s[0][1] == s[0][0]
    s[1][1] == s[1][0]
    s[1][0] == s[1][1]
return s
```

### Runtime TypeError

- Cluster frequency: `3/75` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `3/75` (`4.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `d58a200f2d294321878fda6c55f3e1c9`, summary `Runtime Error`, score `0`, vector `000`

```python
s[0] = s[-1]
s[-1] = s[0] - s[-1]
s[0] = s[0] - s[-1]
s[1] = s[-2]
s[-2] = s[1] - s[-2]
s[1] = s[1] - s[-2]
return s
```

### Uses `str.replace(...)` on sample substrings / no-op replacements instead of positional swapping

- Cluster frequency: `2/75` (`2.7%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `2/75` (`2.7%`)
- Dominant private-case vectors: `010` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `1234a1eca23e4a898de3cd27438e3d58`, summary `Wrong Answer`, score `33`, vector `010`

```python
s.replace("ba", "dc")
swap_diagonals = s.replace("dc", "ba")
return swap_diagonals
```

### Builds/returns the wrong type (tuple/list) instead of the required transformed string

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `061fea26fd3a41d98d93432b84fa8172`, summary `Runtime Error`, score `0`, vector `000`

```python
s = list(s)
for i in s:
    for j in s:
        if i == j:
            temp = s[i]
            s[i] = s[j]
            s[j] = temp
print(s)
```

### Uses invalid string/list APIs while trying to reverse/swap the 2-line string

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `20d7219dccd8427ca1eb239f3f8d5dc9`, summary `Runtime Error`, score `0`, vector `000`

```python
"""l= s.split("\n")
c= l.reversed()
st="\n".join(c)
return st"""

l = s.reverse()
m = l.split("\n")
n = m[::-1]
swaped = "\n".join(n)
return swaped
```

### Treats the input as a 4-character string and ignores the newline separator, so row positions are wrong

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `22657508945141ee8b9ea86ea444fd71`, summary `Wrong Answer`, score `0`, vector `000`

```python
return s[3] + s[1] + s[2] + s[0]
test_string = "ABCD"
result = swap_diagonal(test_string)
print(f"'{test_string}'")
print(f"'{result}'")
```

### Calls `swap_diagonals(...)` from inside itself (copied self-test/sample call) causing recursion

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `54e66de3b8244bb0b74aef977f9eeb26`, summary `Runtime Error`, score `0`, vector `000`

```python
swap_diagonals(s)
```

### Splits on `'/'` instead of the required newline (`'\n'`), so hidden inputs cannot be unpacked

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `5b7774509cb84e048f52dd80b76870a2`, summary `Runtime Error`, score `0`, vector `000`

```python
left, right = s.split("/")
return right[::-1] + "/" + left[::-1]
```

### Returns a tuple of row fragments instead of one newline-joined string

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `6656eb7d607b47e4bc24acfd1de5caed`, summary `Wrong Answer`, score `0`, vector `000`

```python
n1 = s[1] + s[0]
n2 = s[-1] + s[-2]
return n2, n1
```

### Splits rows correctly but reassembles characters in the wrong order (`db\nca`-style column swap)

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `a529a2786ceb48a0b613ef637bd59938`, summary `Wrong Answer`, score `33`, vector `010`

```python
row1, row2 = s.split("\n")
return row2[1] + row1[1] + "\n" + row2[0] + row1[0]
```

### Runtime AttributeError

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `bc224336dcf6419cb54900c1a5b54042`, summary `Runtime Error`, score `0`, vector `000`

```python
s = s.split()
return s.swap(1, 4) and s.swap(2, 3)
```

### Treats the 2-line string like a nested list/string matrix (`s[1][1]`), causing indexing errors

- Cluster frequency: `1/75` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py22/5`: `1/75` (`1.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/5`, Student ID `fd011318fc9147e5ba9cb38ca5eba34b`, summary `Runtime Error`, score `0`, vector `000`

```python
return f"{s[1][1]}{s[0][1]}\n{s[1][0]}{s[0][0]}"
```
