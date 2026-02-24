# Error Patterns: Cluster C101 (`Remove Duplicate Characters from String`)

## Cluster Summary

- Cluster ID: `C101`
- Cluster title: `Remove Duplicate Characters from String`
- Cluster file (this file): `analysis/ERRORS-cluster-c101-remove-duplicate-characters-from-string-2ea9ac9b.md`
- Variants in cluster: `1`
- Total final submitters across variants: `485`
- Total non-full final submissions across variants: `184`
- Canonical variant (by submissions): `ns_25t3_py11/10`

Cluster membership (zero-submitter variants omitted):

| Variant                       | final_submitters | non_full | Relationship                 |
| ----------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py11/10` (canonical) |              485 |      184 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py11/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `485`
- Full pass: `301`
- Non-full final submissions: `184`
- Parseable non-full (logic/runtime focus): `147`
- Non-parseable non-full: `37`

Variant-level comparison:

| Variant           | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ----------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py11/10` |              485 |       301 |      184 |                147 |                     37 |

## Private Case Structure

- Private case 1: moderate-length word with repeated letters (`pineapple`) preserving first-appearance order
- Private case 2: repetition-heavy word (`missisippi`) to catch order-preservation and dedupe logic bugs
- Private case 3: longer mixed-repeat string to catch sample hard-coding and unstable `set(...)` ordering

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                 | Cluster count | % of cluster non-full | `ns_25t3_py11/10` |
| ------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ----------------: |
| Syntax / non-parseable final submission                                                                 |            37 |                 20.1% |                37 |
| No return / implicit `None`                                                                             |            32 |                 17.4% |                32 |
| Incorrect character deduplication logic (order preservation and/or duplicate handling is wrong)         |            31 |                 16.8% |                31 |
| Uses `set(...)` + `join(...)`, which loses the original first-appearance order of characters            |            17 |                  9.2% |                17 |
| Runtime NameError from undefined loop/frequency variables in duplicate-removal logic                    |            16 |                  8.7% |                16 |
| Returns the original string unchanged (duplicates are not removed)                                      |            15 |                  8.2% |                15 |
| Hard-codes sample strings/outputs (`banana`, `hello`, `abc`) instead of removing duplicates generically |             6 |                  3.3% |                 6 |
| Uses `split()`/word-based logic, but the task requires character-level deduplication                    |             5 |                  2.7% |                 5 |
| Runtime TypeError                                                                                       |             5 |                  2.7% |                 5 |
| Runtime error (parseable final submission)                                                              |             5 |                  2.7% |                 5 |
| Runtime IndexError                                                                                      |             4 |                  2.2% |                 4 |
| Copies `is_equal(remove_duplicates(...))` tests into the function and triggers recursive self-calls     |             3 |                  1.6% |                 3 |
| Uses list/string mutation APIs incorrectly (`remove`) while trying to edit a string in place            |             3 |                  1.6% |                 3 |
| Frequency-dictionary lookup bug (`freq[...]`) without safe access while building output                 |             1 |                  0.5% |                 1 |
| Converts the input to a set before processing, destroying order and duplicate information               |             1 |                  0.5% |                 1 |
| Runtime AttributeError                                                                                  |             1 |                  0.5% |                 1 |
| Reads `input()` in a function-type question instead of using the string parameter `s`                   |             1 |                  0.5% |                 1 |
| Runtime RecursionError                                                                                  |             1 |                  0.5% |                 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/184` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `37/184` (`20.1%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `37/184` (`20.1%`)
- Dominant private-case vectors: `000` x37
- Score distribution (top): `0.0` x37
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `0f69982e6d92461b9004f768497692dd`, summary `Runtime Error`, score `0`, vector `000`

```python
def remove_duplicates(s: str) -> str:
    """Removes duplicate characters, keeping the first occurrence."""
    ...

def remove_duplicates(s: str) -> str:
    ""Removes duplicates characters
    str>>>>>>>>> s= "banana"
    str>>>>>>remove_duplicates(s)
    'ban'


    str>>>>>.s = "hello"

str >>>>> remove_duplicates(s)
    'helo'
    >>>s = "abc"
    str >>>> remove_ (s)
    'abc'
# ...
```

### No return / implicit `None`

- Cluster frequency: `32/184` (`17.4%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `32/184` (`17.4%`)
- Dominant private-case vectors: `000` x32
- Score distribution (top): `0.0` x32
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `59b21123f9b240b09b653a669f714b45`, summary `Wrong Answer`, score `0`, vector `000`

```python
def remove_duplicates(s: str) -> str:
    """Removes duplicate characters, keeping the first occurrence."""
    # 1.dict.fromkeys(s) creates a dictionary where unique characters are keys,
    # in order of 1st appearance.
    # 2. .keys() gets the unique characters (keys)
```

### Incorrect character deduplication logic (order preservation and/or duplicate handling is wrong)

- Cluster frequency: `31/184` (`16.8%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `31/184` (`16.8%`)
- Dominant private-case vectors: `000` x31
- Score distribution (top): `0.0` x31
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `b6d42544869b49218badf7c99a4921a8`, summary `Wrong Answer`, score `0`, vector `000`

```python
    check = []
    ans = ''
    for i in range(len(s)):

        elem = s[i]

        for i in range(len(check)):

            if (check[i] == elem):
                continue

            else:
                check.append(elem)
    for i in check:
        ans += i
    return ans
    """Removes duplicate characters, keeping the first occurrence."""
```

### Uses `set(...)` + `join(...)`, which loses the original first-appearance order of characters

- Cluster frequency: `17/184` (`9.2%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `17/184` (`9.2%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `28a098793bf24849b481bbfd72dcd796`, summary `Wrong Answer`, score `0`, vector `000`

```python
x = set(s)
y = list(x)
c = len(y)
lin = []
n = -1
for i in range(c):
    m = s.index(y[i])
    if m < n:
        lin = list(y[i]) + lin
        n = m
    else:
        lin = lin + list(y[i])
        n = m
z = "".join(lin)
return z
```

### Runtime NameError from undefined loop/frequency variables in duplicate-removal logic

- Cluster frequency: `16/184` (`8.7%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `16/184` (`8.7%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `c49157c0bab24e17bf7da58cd8a27337`, summary `Runtime Error`, score `0`, vector `000`

```python
a = set(s)
alpha = "abcdefghijklmnopqrstuvwxyz"
remove_duplicates = ""
for char in a:
    if letter in alpha:
        remove_duplicates += letter
return remove_duplicates
```

### Returns the original string unchanged (duplicates are not removed)

- Cluster frequency: `15/184` (`8.2%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `15/184` (`8.2%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `61038108614147ea8842e331a6afcad1`, summary `Wrong Answer`, score `0`, vector `000`

```python
s = s.lower().split()
result = ""
if not s:
    return s
for ch in s[1:]:
    if ch != result[-1]:
        result.append(ch)
return " ".join(result)
```

### Hard-codes sample strings/outputs (`banana`, `hello`, `abc`) instead of removing duplicates generically

- Cluster frequency: `6/184` (`3.3%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `6/184` (`3.3%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `3d6f6d72d5c546a091659808509c4fce`, summary `Wrong Answer`, score `0`, vector `000`

```python
if s == "banana":
    return "ban"
if s == "hello":
    return "helo"
if s == "abc":
    return "abc"
if s == "python":
    return "python"
if s == "apple":
    return "aple"
if s == "world":
    return "world"
```

### Uses `split()`/word-based logic, but the task requires character-level deduplication

- Cluster frequency: `5/184` (`2.7%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `5/184` (`2.7%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `d863584c1d954bc181e654049e154321`, summary `Wrong Answer`, score `0`, vector `000`

```python
lis = s.split()
result = ""
i = 0
while i < len(lis) - 1:
    if lis[i] in lis[i + 1 :]:
        result += lis[i]
        lis.remove(lis[i])
    else:
        result += lis[i]
return result
```

### Runtime TypeError

- Cluster frequency: `5/184` (`2.7%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `5/184` (`2.7%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `d5d2c561dd74491ba612da07356e9494`, summary `Runtime Error`, score `0`, vector `000`

```python
word = s.split()
b = list(word)
freq = []
for ch in b:
    if ch in b:
        freq.append()
    else:
        freq
return str(freq)
```

### Runtime error (parseable final submission)

- Cluster frequency: `5/184` (`2.7%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `5/184` (`2.7%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `919d97d6ab5642218427db0aa5a6d703`, summary `Runtime Error`, score `0`, vector `000`

```python
def remove_duplicates(s: str) -> str:
    """Removes duplicate characters, keeping the first occurrence."""


newstr = ""
alpha = "abcdefghijklmnopqrstuvwxyz"
while i in str[i]:
    while j in str[j]:
        if str[i] != str[j]:
            newstr = newstr + str[i] + str[j]
        else:
            newstr = newstr + str[i]

        return newstr
```

### Runtime IndexError

- Cluster frequency: `4/184` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `4/184` (`2.2%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `15765f7003d24145a851374858c6b0f4`, summary `Runtime Error`, score `0`, vector `000`

```python
    """length=len(s)
    i=0
    j=1
    s=list(s)
    for i in range(0,length-1):
        if s[i] == s[j]:
            del s[j]
            j=+1
    return str(s)"""
    s=list(s)
    len1=len(s)
    i=0
    j=1
    for i in range (0,len1-1):
        for j in range(1,len1-1):
            if s[i]==s[j]:
                del s[j]
            j=+1
# ...
```

### Copies `is_equal(remove_duplicates(...))` tests into the function and triggers recursive self-calls

- Cluster frequency: `3/184` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `3/184` (`1.6%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `fc56cb38062a4a42846ec5151fedd9be`, summary `Runtime Error`, score `0`, vector `000`

```python
s = "banana"
is_equal(remove_duplicates("banana"), "ban")
s = "hello"
is_equal(remove_duplicates("hello"), "helo")
s = "abc"
is_equal(remove_duplicates("abc"), "abc")
```

### Uses list/string mutation APIs incorrectly (`remove`) while trying to edit a string in place

- Cluster frequency: `3/184` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `3/184` (`1.6%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `f8773ac5b3f04022ace9c4953bebdca5`, summary `Runtime Error`, score `0`, vector `000`

```python
n = len(s)
for i in range(0, n):
    for j in range(i + 1, n):
        if s[i : i + 1] == s[j : j + 1]:
            s.remove(s(j))
```

### Frequency-dictionary lookup bug (`freq[...]`) without safe access while building output

- Cluster frequency: `1/184` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `1/184` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `0da3068accb9422f8fe095961db2da4f`, summary `Runtime Error`, score `0`, vector `000`

```python
freq = {}
for ch in s:
    if s.count(ch) >= 2:
        freq[ch] = freq.get(ch, 0) + 1
for keys in freq.items():
    return freq[keys]
```

### Converts the input to a set before processing, destroying order and duplicate information

- Cluster frequency: `1/184` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `1/184` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `359a2156033e4a6dbfe002996cf6034f`, summary `Wrong Answer`, score `0`, vector `000`

```python
ss = set(s)
fi = sorted(ss)
fg = str(fi)
return fg
```

### Runtime AttributeError

- Cluster frequency: `1/184` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `1/184` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `48d57a4688904833ab58327c04f8e7b2`, summary `Runtime Error`, score `0`, vector `000`

```python
...
s_unique = s.set()
return s_unique
```

### Reads `input()` in a function-type question instead of using the string parameter `s`

- Cluster frequency: `1/184` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `1/184` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `9ab6d2c5fd49449ba92ac9e7aa82d76d`, summary `Runtime Error`, score `0`, vector `000`

```python
s = str(input())
if s.duplicate in s:
    return s.remove_duplicates
else:
    return s
```

### Runtime RecursionError

- Cluster frequency: `1/184` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/10`: `1/184` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/10`, Student ID `ee5d624ebc32408ea840b798b4d88c35`, summary `Runtime Error`, score `0`, vector `000`

```python
s = "banana"
remove_duplicates(s)
s = "hello"
remove_duplicates(s)
s = "abc"
remove_duplicates(s)
print(s)
```
