# Error Patterns: Cluster C023 (`Replace Spaces with Index`)

## Cluster Summary

- Cluster ID: `C023`
- Cluster title: `Replace Spaces with Index`
- Cluster file (this file): `analysis/ERRORS-cluster-c023-replace-spaces-with-index-770df649.md`
- Variants in cluster: `2`
- Total final submitters across variants: `548`
- Total non-full final submissions across variants: `239`
- Canonical variant (by submissions): `ns_25t3_py14_1/10`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py14_1/10` (canonical) |              548 |      239 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py14_1/10.json`
- Other variants in cluster:
  - `problems/ns_25t3_py14_2/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `548`
- Full pass: `309`
- Non-full final submissions: `239`
- Parseable non-full (logic/runtime focus): `187`
- Non-parseable non-full: `52`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py14_1/10` |              548 |       309 |      239 |                187 |                     52 |
| `ns_25t3_py14_2/10` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: leading/trailing + consecutive spaces (must preserve exact indices and whitespace count)
- Private case 2: long sentence with multi-digit replacement indices
- Private case 3: punctuation-heavy sentence with multiple spaced segments and multi-digit indices

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                           | Cluster count | % of cluster non-full | `ns_25t3_py14_1/10` | `ns_25t3_py14_2/10` |
| ------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Syntax / non-parseable final submission                                                           |            52 |                 21.8% |                  52 |                   0 |
| Incorrect space-replacement logic (wrong index counting, mutation, or output assembly)            |            49 |                 20.5% |                  49 |                   0 |
| Uses `str.replace(...)` for all spaces at once, so per-space index substitutions are incorrect    |            41 |                 17.2% |                  41 |                   0 |
| Uses integer indices directly in string replacement/concatenation (`str(i)` cast missing)         |            21 |                  8.8% |                  21 |                   0 |
| Hard-codes public sample strings/outputs instead of replacing spaces generically                  |            20 |                  8.4% |                  20 |                   0 |
| No return / implicit `None`                                                                       |            13 |                  5.4% |                  13 |                   0 |
| Runtime NameError from undefined index/result variables in space-replacement logic                |            11 |                  4.6% |                  11 |                   0 |
| Runtime TypeError                                                                                 |             7 |                  2.9% |                   7 |                   0 |
| Whitespace/index-counting bug: partially works but fails hidden spacing/multi-digit-index cases   |             5 |                  2.1% |                   5 |                   0 |
| Uses `s.index(...)` while constructing output, which breaks on repeated-space handling            |             4 |                  1.7% |                   4 |                   0 |
| Runtime AttributeError                                                                            |             3 |                  1.3% |                   3 |                   0 |
| Runtime error (parseable final submission)                                                        |             3 |                  1.3% |                   3 |                   0 |
| Uses `split()`-based word logic, collapsing/trimming spaces instead of preserving exact positions |             2 |                  0.8% |                   2 |                   0 |
| Strips the input before processing, so leading/trailing spaces and their indices are lost         |             2 |                  0.8% |                   2 |                   0 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests)           |             2 |                  0.8% |                   2 |                   0 |
| Time Limit Exceeded                                                                               |             2 |                  0.8% |                   2 |                   0 |
| Runtime ValueError                                                                                |             1 |                  0.4% |                   1 |                   0 |
| Handles only a simpler space pattern and fails longer/multi-space hidden cases                    |             1 |                  0.4% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/239` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `52/239` (`21.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `52/239` (`21.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x52
- Score distribution (top): `0.0` x52
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `d6ca35207422482f88cf9dcecb3f8c38`, summary `Runtime Error`, score `0`, vector `000`

```python
def replace_spaces_with_index(s):
    """
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index.
    """
    ...
    s = "a b c"
    s1 = "a"
    s2 = "b"


# ...
```

### Incorrect space-replacement logic (wrong index counting, mutation, or output assembly)

- Cluster frequency: `49/239` (`20.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `49/239` (`20.5%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x49
- Score distribution (top): `0.0` x49
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `f7069463ba32412d8f3f3f02a3d4aafc`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    count = 0
    r = list(s)
    for ch in r:
        if ch == ' ':
            r[count] = count
        count += 1
    for ch in r:
        if type(ch) == int:
            r[ch] = str(r[ch])
    if len(s) == 5:
        r1 = r[0]
        r2 = r[1]
        r3 = r[2]
        r4 = r[3]
        r5 = r[4]
        s = r1+r2+r3+r4+r5

# ...
```

### Uses `str.replace(...)` for all spaces at once, so per-space index substitutions are incorrect

- Cluster frequency: `41/239` (`17.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `41/239` (`17.2%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x41
- Score distribution (top): `0.0` x41
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `efefc23e7f1245cc91428e012ea01845`, summary `Wrong Answer`, score `0`, vector `000`

```python
    '''
    b=list (s)
    for i in range(len(b)):
        if b[i]==' ':
            n = str(i)
            for i in range(len(b)):
                if b[i]==' ':
                    a=s.replace(' ',n)
    return a
    '''
    '''
    x=s.split()
    n=len(x)-1
    i=0
    while i<len(x):
    '''
    if ' 'in s:
        a=s.index(' ')
# ...
```

### Uses integer indices directly in string replacement/concatenation (`str(i)` cast missing)

- Cluster frequency: `21/239` (`8.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `21/239` (`8.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x21
- Score distribution (top): `0.0` x21
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `c9a5779ef8e44cb2868e650e3ecd1b80`, summary `Runtime Error`, score `0`, vector `000`

```python
    i= 0
    c =()
    while i <= (len(s)):
        i +=1
        for c in s:
            if c == " ":
                c = c+i
            else:
                c = c+c

        print(c,sep = "")
    '''
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

# ...
```

### Hard-codes public sample strings/outputs instead of replacing spaces generically

- Cluster frequency: `20/239` (`8.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `20/239` (`8.4%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x19, `011` x1
- Score distribution (top): `0.0` x19, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `c536134ab8e34018926f369f8c716f52`, summary `Wrong Answer`, score `0`, vector `000`

```python
p = []
n = len(s)
text = s
for i in range(0, n):
    if s[i] != " ":
        p.append(s[i])
    else:
        p.append(i)
if len(s) == 5:
    return "a1b3c"
if len(s) == 11:
    return "hello5world"
if len(s) == 13:
    return "i1love6python"
```

### No return / implicit `None`

- Cluster frequency: `13/239` (`5.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `13/239` (`5.4%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `b0fe4a3a55bd466e8538439d1c8f15a0`, summary `Wrong Answer`, score `0`, vector `000`

```python
    e=list(s)
    for i in range(len(e)):
        if e[i]==" ":
           e[i]=i
    for i in e:
        print (i)
    '''
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index.
# ...
```

### Runtime NameError from undefined index/result variables in space-replacement logic

- Cluster frequency: `11/239` (`4.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `11/239` (`4.6%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `b7080f06ead24829be141ccab8a7c1a3`, summary `Runtime Error`, score `0`, vector `000`

```python
def replace_spaces_with_index(s):
    """
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index.
    """


for ch in s:
    if ch == " ":
        ch = ch.index()
print(str + ch)
```

### Runtime TypeError

- Cluster frequency: `7/239` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `7/239` (`2.9%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `f10f880902c04b51b59465059bbdf8f9`, summary `Runtime Error`, score `0`, vector `000`

```python
def replace_spaces_with_index(s: str, i: int):
    """
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index.
    """


print("'a1b3c'")
```

### Whitespace/index-counting bug: partially works but fails hidden spacing/multi-digit-index cases

- Cluster frequency: `5/239` (`2.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `5/239` (`2.1%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x4, `010` x1
- Score distribution (top): `67.0` x4, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `036e33ad9d9244e0b2fc5ce76d13b335`, summary `Wrong Answer`, score `67`, vector `011`

```python
    ns=""
    sp=s.split()
    count=-1
    for j in sp:
        ns+= str(count)
        for i in j:
            ns+=i
            count+=1
        count+=1
    nw=ns[2:]
    return nw
    '''
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

# ...
```

### Uses `s.index(...)` while constructing output, which breaks on repeated-space handling

- Cluster frequency: `4/239` (`1.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `4/239` (`1.7%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `85be6cdf98df4573a2e22c2d57c39f84`, summary `Runtime Error`, score `0`, vector `000`

```python
...
s1 = ""
for i in s:
    if i == " ":
        i = s.index(i, len(s1))
        s1 = s1 + str(i)
    else:
        s1 = s1 + str(i)
return s1
```

### Runtime AttributeError

- Cluster frequency: `3/239` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `3/239` (`1.3%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `def7eb8218924db6b8e4b14740110883`, summary `Runtime Error`, score `0`, vector `000`

```python
    index = 0
    return " ".repalce(s)
    '''
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index.
    '''
    ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/239` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `3/239` (`1.3%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `f1eeddd20de84c9fa3f4769d8c6f409a`, summary `Runtime Error`, score `0`, vector `000`

```python
def replace_spaces_with_index(s):
    """
    Given a string s, replace each space (' ') with its index position in the string.

    Example:
        >>> replace_spaces_with_index("a b c")
        'a2b3c'

    Args:
        s (str): Input string.

    Returns:
        str: A new string where each space is replaced with its index."""


for i in s:
    if s == " ":
        s[i] == i

# ...
```

### Uses `split()`-based word logic, collapsing/trimming spaces instead of preserving exact positions

- Cluster frequency: `2/239` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `2/239` (`0.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `0be95b2a0ecb411d8f81880b5a1edc67`, summary `Wrong Answer`, score `0`, vector `000`

```python
x = s.split()
for i in range(len(x)):
    if x[i] == " ":
        x = x.replace(x[i], len(x[i]))
        y = x.join()
        return y
```

### Strips the input before processing, so leading/trailing spaces and their indices are lost

- Cluster frequency: `2/239` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `2/239` (`0.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x1, `000` x1
- Score distribution (top): `67.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `1b80651d8d264cbebe9d23883927a949`, summary `Wrong Answer`, score `67`, vector `011`

```python
s1 = s.strip()
i = 0
new_s = ""
for ch in s1:
    if ch == " ":
        new_s = new_s + str(i)
        i = i + 1
    else:
        new_s = new_s + ch
        i = i + 1
return new_s
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `2/239` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `2/239` (`0.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `f82977150c354d5387b7e84b97c7cdc7`, summary `Runtime Error`, score `0`, vector `000`

```python
s = str(input("Enter a sentence:"))
s = replace(" ", index)
print(s)
```

### Time Limit Exceeded

- Cluster frequency: `2/239` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `2/239` (`0.8%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `3c61a1c4ae0e4db1944ec9013d8e919d`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
str2 = ""
n = len(s)
i = 0
while i < n and i >= 0:
    str1 = s[i : i + 1]
    for char in str1:
        if char == " ":
            str2 = str2 + "i"
        else:
            str2 = str2 + "char"
i = i + 1
return str2
```

### Runtime ValueError

- Cluster frequency: `1/239` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `1/239` (`0.4%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `30879c31e1814aacb4963a508afc73ce`, summary `Runtime Error`, score `0`, vector `000`

```python
num = int(str(s))
new_str = str.replace(" ", num)
```

### Handles only a simpler space pattern and fails longer/multi-space hidden cases

- Cluster frequency: `1/239` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/10`: `1/239` (`0.4%`)
  - `ns_25t3_py14_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/10`, Student ID `cb49586c0a064c13b8913da1163fc514`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    k = ''
    for i in range(len(s)):

        if s[i].isalpha():
            k = k+s[i]



        else:
            k = k+str(i)
    if len(s) == 1:
        return s
    return(k)
```
