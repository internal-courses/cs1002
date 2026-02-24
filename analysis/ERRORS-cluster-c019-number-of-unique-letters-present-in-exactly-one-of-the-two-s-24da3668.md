# Error Patterns: Cluster C019 (`Number of Unique letters present in exactly one of the two strings`)

## Cluster Summary

- Cluster ID: `C019`
- Cluster title: `Number of Unique letters present in exactly one of the two strings`
- Cluster file (this file): `analysis/ERRORS-cluster-c019-number-of-unique-letters-present-in-exactly-one-of-the-two-s-24da3668.md`
- Variants in cluster: `2`
- Total final submitters across variants: `587`
- Total non-full final submissions across variants: `326`
- Canonical variant (by submissions): `ns_25t3_py13_1/8`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py13_1/8` (canonical) |              587 |      326 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py13_1/8.json`
- Other variants in cluster:
  - `problems/ns_25t3_py13_2/8.json`

## Cluster-Level Outcome Summary

- Final submitters: `587`
- Full pass: `261`
- Non-full final submissions: `326`
- Parseable non-full (logic/runtime focus): `275`
- Non-parseable non-full: `51`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py13_1/8` |              587 |       261 |      326 |                275 |                     51 |
| `ns_25t3_py13_2/8` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: case-insensitive symmetric-difference counting on mixed-case strings
- Private case 2: strings with repeated letters (must count unique letters, not occurrences)
- Private case 3: additional mixed-case + repeated-letter combinations to catch no-op normalization (`s1.upper()`) bugs

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                  | Cluster count | % of cluster non-full | `ns_25t3_py13_1/8` | `ns_25t3_py13_2/8` |
| ------------------------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | -----------------: | -----------------: |
| Incorrect unique-letter counting logic (hard-coding, placeholder, or wrong counting method)                              |            85 |                 26.1% |                 85 |                  0 |
| Counts exclusive letters but forgets uniqueness (duplicate letters in one string are counted multiple times)             |            82 |                 25.2% |                 82 |                  0 |
| Syntax / non-parseable final submission                                                                                  |            51 |                 15.6% |                 51 |                  0 |
| Uses set symmetric-difference logic without case normalization (treats uppercase/lowercase letters as different)         |            37 |                 11.3% |                 37 |                  0 |
| No return / implicit `None`                                                                                              |            12 |                  3.7% |                 12 |                  0 |
| Counts characters that appear exactly once overall (`freq == 1`) instead of unique letters present in exactly one string |            11 |                  3.4% |                 11 |                  0 |
| Runtime TypeError from mixing string/set/list types while counting unique letters                                        |            10 |                  3.1% |                 10 |                  0 |
| Set-based approach is incomplete/incorrectly combined (union/intersection/length formula bug)                            |             7 |                  2.1% |                  7 |                  0 |
| Runtime NameError from undefined counters/intermediate variables in counting logic                                       |             7 |                  2.1% |                  7 |                  0 |
| Runtime AttributeError from string/set/list method misuse (`append`, `lower`, etc.)                                      |             5 |                  1.5% |                  5 |                  0 |
| Hard-codes sample input pairs/answers instead of computing the unique-letter count generically                           |             4 |                  1.2% |                  4 |                  0 |
| Case-normalization or set-logic bug that fails hidden mixed-case cases                                                   |             4 |                  1.2% |                  4 |                  0 |
| Runtime error (parseable final submission)                                                                               |             2 |                  0.6% |                  2 |                  0 |
| Runtime IndexError from manual index-based string comparison loops                                                       |             2 |                  0.6% |                  2 |                  0 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests)                                  |             2 |                  0.6% |                  2 |                  0 |
| Runtime RecursionError from accidental recursive function call                                                           |             2 |                  0.6% |                  2 |                  0 |
| Counts exclusive letter occurrences without deduplicating, so repeated letters in one string are overcounted             |             1 |                  0.3% |                  1 |                  0 |
| Calls `s1.upper()` / `s2.upper()` (or `lower()`) without assignment, so case normalization has no effect                 |             1 |                  0.3% |                  1 |                  0 |
| Runtime KeyError                                                                                                         |             1 |                  0.3% |                  1 |                  0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/326` (`0.0%`)

### Incorrect unique-letter counting logic (hard-coding, placeholder, or wrong counting method)

- Cluster frequency: `85/326` (`26.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `85/326` (`26.1%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x85
- Score distribution (top): `0.0` x85
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `0d43eb2c9f234e1eb67167b252dab862`, summary `Wrong Answer`, score `0`, vector `000`

```python
    a=s1.strip()
    b=s2.strip()
    a1=[]
    b1=[]
    list1=[]
    list2=[]
    result_list=[]
    counter=0
    for i in a:
        a1.append(i.lower())
    for j in b:
        b1.append(j.lower())
    print(a1)
    print(b1)
    for k in a1:
        for l in b1:
            flag = 0
            if k != l:
# ...
```

### Counts exclusive letters but forgets uniqueness (duplicate letters in one string are counted multiple times)

- Cluster frequency: `82/326` (`25.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `82/326` (`25.2%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x82
- Score distribution (top): `67.0` x82
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `babb0948afa54a87af52040f5f9e111d`, summary `Wrong Answer`, score `67`, vector `011`

```python
    s1 = s1.lower()
    s2 = s2.lower()
    result = []
    combined = []
    for i in s1:
        combined.append(i)
    for i in s2:
        combined.append(i)
    acount = 0
    bcount = 0
    ccount = 0
    dcount = 0
    ecount = 0
    fcount = 0
    gcount = 0
    hcount = 0
    icount = 0
    jcount = 0
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `51/326` (`15.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `51/326` (`15.6%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x51
- Score distribution (top): `0.0` x51
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `4a49cbbf781f4808804a90255a72a1c6`, summary `Runtime Error`, score `0`, vector `000`

```python
def n_unique_letters_in_exactly_one_of(s1: str, s2: str) -> int:
    '''
    Returns the number of unique letters present in exactly one
    of the two strings (not in both, case insensitive).

    Args:
        s1 (str): First string
        s2 (str): Second string

    Returns:
        int: Count of unique letters in the symmetric difference
    '''
    ...is_equal(n_unique_letters_in_exactly_one_of("apple", "plum"), 4)
4
is_equal(n_unique_letters_in_exactly_one_of("abcd", "bcdf"), 2)
2
is_equal(n_unique_letters_in_exactly_one_of("HELLO", "world"), 5)
5
# ...
```

### Uses set symmetric-difference logic without case normalization (treats uppercase/lowercase letters as different)

- Cluster frequency: `37/326` (`11.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `37/326` (`11.3%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x37
- Score distribution (top): `0.0` x37
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `1a31295c9b34476fbfc5bfc31f11f926`, summary `Wrong Answer`, score `0`, vector `000`

```python
    list1=[]
    list2=[]
    list3=[]
    list4=[]
    for ch in s1:
        list1.append(ch)
    for ch in s2:
        list2.append(ch)
    for i in list1:
        for j in list2:
            if i == j:
                list3.append(i)

            else:
                list4.append(i)
    unique1 = list(set(list1))
    unique2 = list(set(list2))
    k = len(unique1)
# ...
```

### No return / implicit `None`

- Cluster frequency: `12/326` (`3.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `12/326` (`3.7%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `efbd4b4cc8994f87af2832059f72ff76`, summary `Wrong Answer`, score `0`, vector `000`

```python
def n_unique_letters_in_exactly_one_of(s1: str, s2: str):
    """
    Returns the number of unique letters present in exactly one
    of the two strings (not in both, case insensitive).

    Args:
        s1 (str): First string
        s2 (str): Second string

    Returns:
        int: Count of unique letters in the symmetric difference
    """


s1 = "apple"
s2 = "plum"
unique_letters = 0
for x in s1:
    if x in s2:
        continue
# ...
```

### Counts characters that appear exactly once overall (`freq == 1`) instead of unique letters present in exactly one string

- Cluster frequency: `11/326` (`3.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `11/326` (`3.4%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x10, `000` x1
- Score distribution (top): `67.0` x10, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `1a1af22dbbed4b41b7b2ec855caa5658`, summary `Wrong Answer`, score `67`, vector `011`

```python
    """a=[]
    for i in range (s1):
        a.append(i)
    b=[]
    for j in range(s2):
        b.append (j)
    for k in range(len(a)):
        for l in range(len(b)):
            if a[k]!="""
    a=s1.lower()+s2.lower()
    b=[]
    c={}
    d=[]
    for i in a:
        b.append(i)
    """for j in range(len(b)):
        if b[j] in c :
            pass
# ...
```

### Runtime TypeError from mixing string/set/list types while counting unique letters

- Cluster frequency: `10/326` (`3.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `10/326` (`3.1%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `404445ec92fa480681b26b6404d6f412`, summary `Runtime Error`, score `0`, vector `000`

```python
str1 = s1.lower()
str2 = s2.lower()
count = 0
for i in len(str1):
    for j in len(str2):
        if str1[i] == str2[j]:
            count = count + 1
return len(str1) + len(str2) - count
```

### Set-based approach is incomplete/incorrectly combined (union/intersection/length formula bug)

- Cluster frequency: `7/326` (`2.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `7/326` (`2.1%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5, `011` x1, `001` x1
- Score distribution (top): `0.0` x5, `67.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `78befc829f0e4b6880a8b58d86be50db`, summary `Wrong Answer`, score `0`, vector `000`

```python
    set1=[]
    set2=[]
    for a in s1:
        set1.append(a.lower())
    for b in s2:
        set1.append(b.lower())
    a=set(set1)
    b=set(set2)
    return (len(a|b)-2*len(a&b))
    '''
    Returns the number of unique letters present in exactly one
    of the two strings (not in both, case insensitive).

    Args:
        s1 (str): First string
        s2 (str): Second string

    Returns:
# ...
```

### Runtime NameError from undefined counters/intermediate variables in counting logic

- Cluster frequency: `7/326` (`2.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `7/326` (`2.1%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `f8c2b831bcea4c23b8427cdfbe255e7f`, summary `Runtime Error`, score `0`, vector `000`

```python
s1 = "APPLE"
s2 = "plum"
if x in s1:
    if x in s2:
        unique_characters += x
        Count(unique_characters)
```

### Runtime AttributeError from string/set/list method misuse (`append`, `lower`, etc.)

- Cluster frequency: `5/326` (`1.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `5/326` (`1.5%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `237651342de74af885b5921709cf25e1`, summary `Runtime Error`, score `0`, vector `000`

```python
...
set1 = set(s1.lower())
set2 = set(s2.lower())
print(set1)
set1 = {ch for ch in set1 if ch.alpha(s1)}
set2 = {ch for ch in set2 if ch.alpha(s2)}
unique_letters = set1 + set2
return len(unique_letters)
```

### Hard-codes sample input pairs/answers instead of computing the unique-letter count generically

- Cluster frequency: `4/326` (`1.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `4/326` (`1.2%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `95356c98fcb94177b9aadda07a670bba`, summary `Wrong Answer`, score `0`, vector `000`

```python
if s1 == "apple" and s2 == "plum":
    return 4
elif s1 == "abcd" and s2 == "bcdf":
    return 2
elif s1 == "HELLO" and s2 == "world":
    return 5
elif s1 == "abc" and s2 == "XYZADE":
    return 7
elif s1 == "same" and s2 == "name":
    return 2
```

### Case-normalization or set-logic bug that fails hidden mixed-case cases

- Cluster frequency: `4/326` (`1.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `4/326` (`1.2%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x4
- Score distribution (top): `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `2e6b5812d9a84bb3a0b9317263f863c2`, summary `Wrong Answer`, score `33`, vector `001`

```python
    l1=len(s1)
    l2=len(s2)
    a=0
    b=0
    for i in range(l1):
        for j in range(l2):
            if s1[i].lower()!=s2[j].lower():
                a+=1
        if a==l1:
            b=3

        return(b)
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/326` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `2/326` (`0.6%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `6853ee16e23647bb924e2144676f2fd1`, summary `Runtime Error`, score `0`, vector `000`

```python
set1 = set1(s1.lower())
set2 = set2(s2.lower())
exlusive_to_set1 = set1 - set2
exlusive_to_set2 = set2 - set1
total_exclusive_chars = exlusive_to_set1.union(exclsive_to_set2)
return len(total_exclusive_chars)
```

### Runtime IndexError from manual index-based string comparison loops

- Cluster frequency: `2/326` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `2/326` (`0.6%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1, `001` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `b978696b56ae44a3a5bfd23cd6d3860c`, summary `Runtime Error`, score `33`, vector `001`

```python
sr = list(s1.upper().strip())
sn = list(s2.upper().strip())
count = 0
y = 0
for i in range(len(sr)):
    if sr[i] not in sn:
        count += 1
    elif sn[i] not in sr:
        count += 1
if sn[i] == sr[i]:
    y += 1
    return len(sn) + len(sr) - y
return count
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `2/326` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `2/326` (`0.6%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `d2b1588077474a168a5bdcf8607f4046`, summary `Runtime Error`, score `0`, vector `000`

```python
s1 = input("enter the first string:")
s2 = input("enter the second string:")
count = 0
for i in s1:
    for j in s2:
        if i != j:
            print(i)
            count += 1
print(count)
```

### Runtime RecursionError from accidental recursive function call

- Cluster frequency: `2/326` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `2/326` (`0.6%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `652d5f13745a4ca8bc6475925d42f7d8`, summary `Runtime Error`, score `0`, vector `000`

```python
s1 = "BANANA"
s2 = "PAPAYA"
return n_unique_letters_in_exactly_one_of(s1, s2)
```

### Counts exclusive letter occurrences without deduplicating, so repeated letters in one string are overcounted

- Cluster frequency: `1/326` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `1/326` (`0.3%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `07045ebf272a447f86de22b0fbb26b9a`, summary `Wrong Answer`, score `67`, vector `011`

```python
s1 = s1.lower()
s2 = s2.lower()
l1 = []
for i in range(len(s1)):
    l1.append(s1[i])
l2 = []
for i in range(len(s2)):
    l2.append(s2[i])
Count = 0
for j in l1:
    if j not in l2:
        Count += 1
for j in l2:
    if j not in l1:
        Count += 1
return Count
```

### Calls `s1.upper()` / `s2.upper()` (or `lower()`) without assignment, so case normalization has no effect

- Cluster frequency: `1/326` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `1/326` (`0.3%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `10b0cb7c7197450487ca739e953d0986`, summary `Wrong Answer`, score `0`, vector `000`

```python
unique = 0
c = 0
s1.upper()
s2.upper()
s1 = set(s1)
s2 = set(s2)
for x in s1:
    if not (x in s2):
        unique = unique + 1
for x in s2:
    if not (x in s1):
        unique = unique + 1
return unique
```

### Runtime KeyError

- Cluster frequency: `1/326` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/8`: `1/326` (`0.3%`)
  - `ns_25t3_py13_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Dictionary lookup on uninitialized/unexpected key.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/8`, Student ID `ee4efeca14164d62a39ccf53915a749d`, summary `Runtime Error`, score `0`, vector `000`

```python
count = 0
st1 = set(s1)
st2 = set(s2)
for i in st1:
    for j in st2:
        if st1[i] != st2[j]:
            count += 1
return set.symmetric_difference(st1, st2)
```
