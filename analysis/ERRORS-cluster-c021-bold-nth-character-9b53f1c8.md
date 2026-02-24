# Error Patterns: Cluster C021 (`Bold Nth Character`)

## Cluster Summary

- Cluster ID: `C021`
- Cluster title: `Bold Nth Character`
- Cluster file (this file): `analysis/ERRORS-cluster-c021-bold-nth-character-9b53f1c8.md`
- Variants in cluster: `2`
- Total final submitters across variants: `581`
- Total non-full final submissions across variants: `210`
- Canonical variant (by submissions): `ns_25t3_py14_1/8`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py14_1/8` (canonical) |              581 |      210 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py14_1/8.json`
- Other variants in cluster:
  - `problems/ns_25t3_py14_2/8.json`

## Cluster-Level Outcome Summary

- Final submitters: `581`
- Full pass: `371`
- Non-full final submissions: `210`
- Parseable non-full (logic/runtime focus): `164`
- Non-parseable non-full: `46`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py14_1/8` |              581 |       371 |      210 |                164 |                     46 |
| `ns_25t3_py14_2/8` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: valid interior `n` (1-based indexing) should wrap exactly one middle character with `<b>...</b>`
- Private case 2: boundary `n = 1` case (first character should be bolded, not treated as invalid)
- Private case 3: end/out-of-range checks (`n = len(text)` valid; `n > len(text)` returns original string unchanged)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                     | Cluster count | % of cluster non-full | `ns_25t3_py14_1/8` | `ns_25t3_py14_2/8` |
| --------------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: | -----------------: |
| Syntax / non-parseable final submission                                                                                     |            46 |                 21.9% |                 46 |                  0 |
| Runtime IndexError from indexing `text[n]`/`text[n-1]` without validating `n` against string bounds                         |            26 |                 12.4% |                 26 |                  0 |
| No return / implicit `None`                                                                                                 |            23 |                 11.0% |                 23 |                  0 |
| Only validates `n` and returns the original string; never inserts the `<b>...</b>` tags                                     |            22 |                 10.5% |                 22 |                  0 |
| Incorrect nth-character bolding logic (broad wrong-answer failure)                                                          |            17 |                  8.1% |                 17 |                  0 |
| Returns from inside a loop while building the bolded string (partial output / premature return)                             |            14 |                  6.7% |                 14 |                  0 |
| Runtime TypeError                                                                                                           |            12 |                  5.7% |                 12 |                  0 |
| Runtime error (parseable final submission)                                                                                  |             6 |                  2.9% |                  6 |                  0 |
| Runtime NameError from typoed variables while constructing the bolded string                                                |             6 |                  2.9% |                  6 |                  0 |
| Runtime IndexError                                                                                                          |             5 |                  2.4% |                  5 |                  0 |
| Hard-codes sample strings/outputs instead of bolding the nth character generically                                          |             4 |                  1.9% |                  4 |                  0 |
| Boundary bug: valid `n == len(text)` is rejected (strict `< len(text)` check)                                               |             4 |                  1.9% |                  4 |                  0 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests)                                     |             3 |                  1.4% |                  3 |                  0 |
| Runtime AttributeError                                                                                                      |             3 |                  1.4% |                  3 |                  0 |
| Length/index-specific branching (special-cases `n == 1/2/...`) instead of one general slicing formula                       |             3 |                  1.4% |                  3 |                  0 |
| Wraps a slice/prefix in `<b>` tags instead of exactly one nth character                                                     |             2 |                  1.0% |                  2 |                  0 |
| Runtime TypeError from invalid string/list concatenation or malformed slicing/index calls                                   |             2 |                  1.0% |                  2 |                  0 |
| Runtime RecursionError                                                                                                      |             2 |                  1.0% |                  2 |                  0 |
| Time Limit Exceeded                                                                                                         |             2 |                  1.0% |                  2 |                  0 |
| Runtime NameError                                                                                                           |             2 |                  1.0% |                  2 |                  0 |
| Uses `text[:-n]` for the suffix after the bolded character, truncating the string incorrectly                               |             1 |                  0.5% |                  1 |                  0 |
| Uses `n < len(text)` instead of allowing `n == len(text)`, so the last character cannot be bolded                           |             1 |                  0.5% |                  1 |                  0 |
| Uses `text.replace(...)`, which replaces the first/all matching character values instead of the nth position                |             1 |                  0.5% |                  1 |                  0 |
| Uses `text.index(...)` while iterating, so duplicate characters use the first occurrence index and are bolded incorrectly   |             1 |                  0.5% |                  1 |                  0 |
| Boundary/position bug around `n == 1` or duplicate characters (rejects first-char case or uses value-based `replace/index`) |             1 |                  0.5% |                  1 |                  0 |
| Builds the bolded prefix and character but omits the suffix after the nth character                                         |             1 |                  0.5% |                  1 |                  0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/210` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `46/210` (`21.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `46/210` (`21.9%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x46
- Score distribution (top): `0.0` x46
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `d7e45b912edd4fe19597c3d021b9e3c1`, summary `Runtime Error`, score `0`, vector `000`

```python
def bold_nth_character(text: str, n: int) -> str:
    """
    Returns a string where the nth character is wrapped in <b></b> tags.
    If n is invalid, returns the original string unchanged.
    """
    if n < 1 or n > len(text):
        print("invalid")

    result = []
    first = text[: n - 2]
    mid = text[n - 1]
    last = text[n:]
    result[0] = first
    result[1] = "<b>"
    result[2] = mid
    result[3] = "</b>"
    result[2] = last
    print(str(result))


# ...
```

### Runtime IndexError from indexing `text[n]`/`text[n-1]` without validating `n` against string bounds

- Cluster frequency: `26/210` (`12.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `26/210` (`12.4%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x16, `000` x7, `010` x2, `100` x1
- Score distribution (top): `67.0` x16, `0.0` x7, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `a06d21a49cb54484919c05bad9e613a6`, summary `Runtime Error`, score `33`, vector `100`

```python
result = ""
if n == 0:
    return text
else:
    for i in text:
        if i == text[n - 1]:
            result += "<b>"
            result += text[n - 1]
        elif i == text[n]:
            result += "</b>"
            result += text[n]
        else:
            result += i
return result
"""
Returns a string where the nth character is wrapped in <b></b> tags.
If n is invalid, returns the original string unchanged.
"""
```

### No return / implicit `None`

- Cluster frequency: `23/210` (`11.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `23/210` (`11.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x23
- Score distribution (top): `0.0` x23
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `3c7660bea60f49d2b78c44eccf1cf31a`, summary `Wrong Answer`, score `0`, vector `000`

```python
def bold_nth_character(text: str, n: int) -> str:
    """
    Returns a string where the nth character is wrapped in <b></b> tags.
    If n is invalid, returns the original string unchanged.
    """
```

### Only validates `n` and returns the original string; never inserts the `<b>...</b>` tags

- Cluster frequency: `22/210` (`10.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `22/210` (`10.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x22
- Score distribution (top): `0.0` x22
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `3498c7fa9be0408e8c99a272a2e86edb`, summary `Wrong Answer`, score `0`, vector `000`

```python
text_length = len(text)
if n < 1 or n > text_length:
    return text
idx = n - 1
char_to_bold = text[idx]
before = text[:idx]
bolded_char = f"<b>{char_to_bold}<b/>"
after = text[idx + 1 :]
return before + bolded_char + after
```

### Incorrect nth-character bolding logic (broad wrong-answer failure)

- Cluster frequency: `17/210` (`8.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `17/210` (`8.1%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `2ac263f83e2a4a91b92e5f031e83dae8`, summary `Wrong Answer`, score `0`, vector `000`

```python
if n < 1 or n > len(text):
    return text
else:
    t = ""
    for i in range(len(text)):
        if text[i] == text[n - 1]:
            t = t + "<b>text[i]</b>"
        else:
            t = t + text[i]
    return t
"""
Returns a string where the nth character is wrapped in <b></b> tags.
If n is invalid, returns the original string unchanged.
"""
...
```

### Returns from inside a loop while building the bolded string (partial output / premature return)

- Cluster frequency: `14/210` (`6.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `14/210` (`6.7%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x10, `110` x2, `101` x1, `011` x1
- Score distribution (top): `0.0` x10, `67.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `c208bfb67d3142779f9a58f3b9b3a060`, summary `Wrong Answer`, score `67`, vector `011`

```python
    ...
    l=len(text)
    if (n==1):
        x='<b>'+text[0]+'</b>'+text[1:l:1]
        return x
    else:
        if (n==l):
            x=text[0:l-1:1]+'<b>'+text[l-1]+'</b>'
            return x
        else:
            if (n==0):
                return text
            else:
                if(n<1):
                    return text
                else:
                    if(n>l):
                        return text
# ...
```

### Runtime TypeError

- Cluster frequency: `12/210` (`5.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `12/210` (`5.7%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `c1cd4a8ab46240c0bc6248e9ad6720eb`, summary `Runtime Error`, score `0`, vector `000`

```python
    if n<1:
        return text
    elif n>len(text):
        return text
    else:
        i=0
        text1=text
        text2=''
        tl=len(text1)
        while i!=n :
            for char in text1:
                text2=text1
                i=i+1
        l=len(text2)

        text2[i]="<"
        text2[i+1]='b'
        text2[i+2]='>'
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `6/210` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `6/210` (`2.9%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4, `101` x1, `110` x1
- Score distribution (top): `0.0` x4, `67.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `336780807c1c47cb8a75910f265b7dcc`, summary `Runtime Error`, score `67`, vector `101`

```python
...
if n < 1 or n > len(text):
    return text
index = n - 1
a = ""
for i in range(index):
    a = a + (text[i])
    last = i
a = a + ("<b>")
a = a + (text[last + 1])
a = a + ("</b>")
while n < len(text):
    a = a + (text[n])
    n += 1
return a
```

### Runtime NameError from typoed variables while constructing the bolded string

- Cluster frequency: `6/210` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `6/210` (`2.9%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `d99acc195dce484f81d339b96cdc5d83`, summary `Runtime Error`, score `0`, vector `000`

```python
def bold_nth_character(text: str, n: int) -> str:
    """
    Returns a string where the nth character is wrapped in <b></b> tags.
    If n is invalid, returns the original string unchanged.
    """


is_equal(bold_nth_character("mango", 2), "m<b>a</b>ngo")
is_equal(bold_nth_character("pizza", 1), "<b>p</b>izza")
is_equal(bold_nth_character("pasta", 5), "past<b>a</b>")
is_equal(bold_nth_character("burger", 0), "burger")
is_equal(bold_nth_character("tea", 5), "tea")
is_equal(bold_nth_character("tea", -1), "tea")
```

### Runtime IndexError

- Cluster frequency: `5/210` (`2.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `5/210` (`2.4%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4, `110` x1
- Score distribution (top): `0.0` x4, `67.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `51e8e02e2ede45e986de3b7447881b3b`, summary `Runtime Error`, score `0`, vector `000`

```python
    word = text.split()
    for ch in word:

        new = ''
        wrapped_ch = ''
        wrapped_ch == '<b>' + ch[n-1] + '</b>'
        if ch.index == n-1:
            new += wrapped_ch
        else:
            new += ch
    return new
```

### Hard-codes sample strings/outputs instead of bolding the nth character generically

- Cluster frequency: `4/210` (`1.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `4/210` (`1.9%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `da57b81a6c7b436d8459c66b2423c1c1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if text == "mango":
        if n == 2:
            return 'm<b>a</b>ngo'
    if text == "pizza":
        if n == 1:
            return '<b>p</b>izza'
    if text == "pasta":
        if n == 5:
            return 'past<b>a</b>'
    if text == "burger":
        if n == 0:
            return 'burger'
    if text == "tea":
        if n == 5:
            return 'tea'
        else:
            return 'tea'

# ...
```

### Boundary bug: valid `n == len(text)` is rejected (strict `< len(text)` check)

- Cluster frequency: `4/210` (`1.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `4/210` (`1.9%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x4
- Score distribution (top): `67.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `50f7c0b50f6b41c7bcbdbca1712d4a2d`, summary `Wrong Answer`, score `67`, vector `110`

```python
new_str = text
after = new_str[: n - 1]
before = new_str[n:]
at_n = "<b>" + new_str[n - 1 : n] + "</b>"
newest_str = after + at_n + before
if n > 0:
    return newest_str
else:
    return new_str
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `3/210` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `3/210` (`1.4%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `f82977150c354d5387b7e84b97c7cdc7`, summary `Runtime Error`, score `0`, vector `000`

```python
text = str(input("Enter a text:"))
print("Enter which letter you want to make bold:")
n = int(input())
if n > 0:
    x = text.bold(n)
    print(x)
else:
    print(text)
```

### Runtime AttributeError

- Cluster frequency: `3/210` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `3/210` (`1.4%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `513584c59caf4455bd6b5907548321fc`, summary `Runtime Error`, score `0`, vector `000`

```python
if n < 1 or len(text) < n:
    return text
else:
    text[i + n - 1] = float(text.append("<b>"))
    text[i + n + 1] = text.append("<b>")
return text
```

### Length/index-specific branching (special-cases `n == 1/2/...`) instead of one general slicing formula

- Cluster frequency: `3/210` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `3/210` (`1.4%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x1, `010` x1, `000` x1
- Score distribution (top): `67.0` x1, `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `6d120654aba642febd147f6b25d72aef`, summary `Wrong Answer`, score `67`, vector `011`

```python
    if n < 1 or n > len(text):
        return text
    elif n == 2:
        first_part = text[0]
        second_part = "<b>"
        second_part1 = text[n-1]
        second_part2 = "</b>"
        third_part = text[n:]
        return first_part + second_part + second_part1 + second_part2 + third_part

    elif n == 1:
        first_part = text[0:n]
        first_part2 = "<b>"
        first_part3 = "</b>"
        second_part = text[n:]
        return first_part2 + first_part + first_part3 + second_part

    else:
# ...
```

### Wraps a slice/prefix in `<b>` tags instead of exactly one nth character

- Cluster frequency: `2/210` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `2/210` (`1.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x1, `010` x1
- Score distribution (top): `67.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `0e13f5cd8e274e31aab5edd5399a2ecf`, summary `Wrong Answer`, score `67`, vector `011`

```python
if 1 < n < len(text):
    return f"{text[: n - 1]}<b>{text[n - 1 : 2]}</b>{text[n:]}"
if n < 0 or n > len(text) or n == 0:
    return f"{text}"
if n == len(text):
    return f"{text[: n - 1]}<b>{text[n - 1 :]}</b>"
if n == 1:
    return f"<b>{text[:1]}</b>{text[1:]}"
```

### Runtime TypeError from invalid string/list concatenation or malformed slicing/index calls

- Cluster frequency: `2/210` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `2/210` (`1.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `dca104077abb4a28912ccefce43fa37f`, summary `Runtime Error`, score `0`, vector `000`

```python
    m = len(text)
    if n<1 or n>m:
        return text
    else:
        l = list(text)

        l = l.insert("l[n-1]",'<b>')
        l = l.insert("l[n+1]",'</b>')
        for i in range(n):
            s += l[i]
    return s
```

### Runtime RecursionError

- Cluster frequency: `2/210` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `2/210` (`1.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `2878acfc02764c87a4b3646221cfee83`, summary `Runtime Error`, score `0`, vector `000`

```python
is_equal(bold_nth_character("mango", 2), "m<b>a</b>ngo")
print(" 'm<b>a</b>ngo'")
```

### Time Limit Exceeded

- Cluster frequency: `2/210` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `2/210` (`1.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `9c69f0c3879c4d3ebebba0a2c9317216`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
    newstring = ""
    if 1<=n<=len(text):
        for i in range(1,len(text)):
            while text[i] != n:
                newstring += text[i]
            if text[i] == n:
                newstring += "<b>",text[i],"</b>"

        return newstring
    if n < 1 or n > len(text):
        return text
```

### Runtime NameError

- Cluster frequency: `2/210` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `2/210` (`1.0%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `6e7b19c177a74dea950988be7fbae45c`, summary `Runtime Error`, score `0`, vector `000`

```python
str1 = ()
str2 = ()
st1 == str2
```

### Uses `text[:-n]` for the suffix after the bolded character, truncating the string incorrectly

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `058872f5d6fd4fae96b0dabf5ab7e9a8`, summary `Wrong Answer`, score `33`, vector `001`

```python
if n < 1 or n > len(text):
    return text
else:
    new_string = text[0 : n - 1] + "<b>" + text[n - 1] + "</b>" + text[:-n]
    return new_string
```

### Uses `n < len(text)` instead of allowing `n == len(text)`, so the last character cannot be bolded

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `28e37d8582bd4855a088d0a2181c41d6`, summary `Wrong Answer`, score `67`, vector `110`

```python
if n > 0:
    if n < len(text):
        block_1 = text[: n - 1]
        block_2 = "<b>"
        block_3 = text[n - 1]
        block_4 = "</b>"
        block_5 = text[n:]
        return block_1 + "<b>" + block_3 + "</b>" + block_5
    else:
        return text
else:
    return text
```

### Uses `text.replace(...)`, which replaces the first/all matching character values instead of the nth position

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `47f5d9b425f545e3a88709f97d4f75a6`, summary `Wrong Answer`, score `0`, vector `000`

```python
a = "<b>text[:n]</b>"
new = text.replace(text[:n], a)
if n < 1 or n > len(text):
    return text
else:
    return new
```

### Uses `text.index(...)` while iterating, so duplicate characters use the first occurrence index and are bolded incorrectly

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `9cccecfd6fb2432bb6bd0429a76ba359`, summary `Wrong Answer`, score `67`, vector `110`

```python
    bold1 = "<b>"
    bold2 = "</b>"
    final = ""
    if n < 1 or n >= len(text):
        return(text)

    else:

        for i in text:

            indexmin1 = int(text.index(i)) + 1

            if n == indexmin1:
                final += "<b>" + i + "</b>"
            else:
                final += i
    return(final)
    ...
```

### Boundary/position bug around `n == 1` or duplicate characters (rejects first-char case or uses value-based `replace/index`)

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `ca67439ad7a34a25a737187a16736339`, summary `Wrong Answer`, score `67`, vector `101`

```python
    q = 0
    m = ""
    t = ""
    s = len(text)
    if(n<1 or n>s):
        return(text)
    q = text[n-2]
    z = text[n-1]
    for i in text:
        m = m+i

        if i == q:
            m = m+"<b>"
        if i == z:
            m =m + "</b>"
    return(m)
```

### Builds the bolded prefix and character but omits the suffix after the nth character

- Cluster frequency: `1/210` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/8`: `1/210` (`0.5%`)
  - `ns_25t3_py14_2/8`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/8`, Student ID `e11e0a815be74dc4bd069115d6cbaf21`, summary `Wrong Answer`, score `33`, vector `001`

```python
if n < 1 or n > len(text):
    return text
index = n - 1
return text[:index] + f"<b>{text[index]}</b>"
```
