# Error Patterns: Cluster C013 (`Pangram Check`)

## Cluster Summary

- Cluster ID: `C013`
- Cluster title: `Pangram Check`
- Cluster file (this file): `analysis/ERRORS-cluster-c013-pangram-check-f0d5ae7d.md`
- Variants in cluster: `2`
- Total final submitters across variants: `1331`
- Total non-full final submissions across variants: `665`
- Canonical variant (by submissions): `ns_25t2_py21_2/18`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py21_1/16`             |              656 |      337 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/18` (canonical) |              675 |      328 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/18.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/16.json`

## Cluster-Level Outcome Summary

- Final submitters: `1331`
- Full pass: `666`
- Non-full final submissions: `665`
- Parseable non-full (logic/runtime focus): `609`
- Non-parseable non-full: `56`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py21_1/16` |              656 |       319 |      337 |                304 |                     33 |
| `ns_25t2_py21_2/18` |              675 |       347 |      328 |                305 |                     23 |

## Private Case Structure

- Private case 1: mixed-case positives + one negative sentence
- Private case 2: digit/non-letter-heavy cases incl reversed-alphabet positives
- Private case 3: short negatives + punctuation/digit positive pangram

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                       | Cluster count | % of cluster non-full | `ns_25t2_py21_1/16` | `ns_25t2_py21_2/18` |
| --------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Returns inside the alphabet-check loop (decides after first character/iteration)              |           243 |                 36.5% |                 129 |                 114 |
| Hard-codes sample pangram strings/examples instead of checking letter coverage                |            77 |                 11.6% |                  38 |                  39 |
| Syntax / non-parseable final submission                                                       |            56 |                  8.4% |                  33 |                  23 |
| Skeleton placeholder `...` left in function (no implementation; returns None)                 |            28 |                  4.2% |                   7 |                  21 |
| Alphabet-string/list membership confusion (`in`/substring check instead of coverage)          |            27 |                  4.1% |                  13 |                  14 |
| Runtime error (parseable final submission)                                                    |            27 |                  4.1% |                  14 |                  13 |
| Always returns `True` (constant output)                                                       |            25 |                  3.8% |                  15 |                  10 |
| Other wrong-answer logic pattern (residual)                                                   |            23 |                  3.5% |                  12 |                  11 |
| Checks exact alphabet string order (`abcdefghijklmnopqrstuvwxyz`) instead of pangram coverage |            20 |                  3.0% |                  10 |                  10 |
| Runtime NameError (undefined variable/helper)                                                 |            17 |                  2.6% |                  10 |                   7 |
| Fails non-letter/digit-heavy private case despite passing others                              |            17 |                  2.6% |                   3 |                  14 |
| Alphabet-string equality/substring check instead of coverage                                  |            17 |                  2.6% |                  10 |                   7 |
| Substring/membership confusion with alphabet string (`text in alphabet` / `alphabet in text`) |            14 |                  2.1% |                   9 |                   5 |
| Uses total string length ==/>= 26 as pangram test (counts spaces/digits/punctuation)          |            12 |                  1.8% |                   3 |                   9 |
| Compares exact set(text) to alphabet set (rejects valid pangrams with extra chars/spaces)     |             9 |                  1.4% |                   3 |                   6 |
| Uses `string.ascii_lowercase` without importing `string` (environment-dependent fail-all)     |             6 |                  0.9% |                   4 |                   2 |
| Counts total alphabetic characters instead of distinct letters                                |             5 |                  0.8% |                   4 |                   1 |
| No return / implicit `None`                                                                   |             4 |                  0.6% |                   1 |                   3 |
| Partial-score pangram logic bug (case/filtering/coverage edge case)                           |             4 |                  0.6% |                   2 |                   2 |
| Counts unique characters (or len(set(...)) == 26) instead of checking all letters             |             3 |                  0.5% |                   2 |                   1 |
| Uses `text.isalpha()` as pangram test (alphabetic-only, not 26-letter coverage)               |             3 |                  0.5% |                   1 |                   2 |
| Strips spaces only but not other non-letters; digit/punctuation cases still break logic       |             3 |                  0.5% |                   2 |                   1 |
| Runtime KeyError (unexpected character handling)                                              |             3 |                  0.5% |                   3 |                   0 |
| Incorrect boolean-chain membership checks for letters                                         |             2 |                  0.3% |                   1 |                   1 |
| Fails short-negative/punctuation private case due boundary filtering mistake                  |             2 |                  0.3% |                   0 |                   2 |
| Uses input truthiness / non-empty-string check instead of pangram logic                       |             2 |                  0.3% |                   1 |                   1 |
| Uses method object truthiness (`text.isalpha` without `()`)                                   |             2 |                  0.3% |                   1 |                   1 |
| Compares function object/name (`is_pangram`) with input text                                  |             2 |                  0.3% |                   1 |                   1 |
| Always returns `False` (constant output)                                                      |             2 |                  0.3% |                   0 |                   2 |
| Incorrect boolean-chain membership test (`"a" or "b" in text` / `and` chain)                  |             2 |                  0.3% |                   1 |                   1 |
| Compares the return value of `.sort()` (None) while checking alphabet coverage                |             1 |                  0.2% |                   0 |                   1 |
| Counts unique characters (dictionary/list length == 26) instead of checking all letters       |             1 |                  0.2% |                   0 |                   1 |
| Checks truthiness of a constant/local variable instead of letter coverage                     |             1 |                  0.2% |                   0 |                   1 |
| Checks for duplicate characters (uniqueness) instead of pangram coverage                      |             1 |                  0.2% |                   0 |                   1 |
| Compares the input to the literal string `"text"` (placeholder-name confusion)                |             1 |                  0.2% |                   1 |                   0 |
| Hard-codes a specific alphabet/pangram string and checks exact equality                       |             1 |                  0.2% |                   1 |                   0 |
| Uses `text.isalpha()` gate, rejecting valid pangrams that include spaces/punctuation/digits   |             1 |                  0.2% |                   1 |                   0 |
| Impossible/always-false condition after counting characters (trivial constant decision)       |             1 |                  0.2% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `23/665` (`3.5%`)

### Returns inside the alphabet-check loop (decides after first character/iteration)

- Cluster frequency: `243/665` (`36.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `129/337` (`38.3%`)
  - `ns_25t2_py21_2/18`: `114/328` (`34.8%`)
- Dominant private-case vectors: `000` x136, `001` x59, `100` x40, `101` x3
- Score distribution (top): `0.0` x136, `33.0` x101, `67.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `bacaa118bdc44202b5c41c5f02739855`, summary `Wrong Answer`, score `0`, vector `000`

```python
alpha = 'abcdefghijklmnopqrstuvwxyz'
t1 = text.lower()
num ='1234567890'
for  i in t1 :
        if i is t1.isalpha() :
            return True
        else :
            return False
'''

    for i in alpha :

        if  i in t1 :
            if i is t1.isalpha() :
                return True



# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `8d2c5337634240e29a28e245332e876c`, summary `Wrong Answer`, score `33`, vector `001`

```python
text = text.lower()
count = {}
countl = []
digit = "0123456789"
alpha = "abcdefghijklmnopqrstuvwxyz"
for char in text:
    if char.isalpha:
        if char in count:
            count[char] += 1
        else:
            count[char] = 1
for k in count.keys():
    countl.append(k)
for char in alpha:
    if char in count and char not in digit:
        return True
    else:
        return False
# ...
```

### Hard-codes sample pangram strings/examples instead of checking letter coverage

- Cluster frequency: `77/665` (`11.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `38/337` (`11.3%`)
  - `ns_25t2_py21_2/18`: `39/328` (`11.9%`)
- Dominant private-case vectors: `000` x56, `100` x9, `101` x4, `001` x3
- Score distribution (top): `0.0` x56, `33.0` x15, `67.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `dc29a6ab709345c183e7dc066c409336`, summary `Wrong Answer`, score `33`, vector `001`

```python
(
    ca,
    cb,
    cc,
    cd,
    ce,
    cf,
    cg,
    ch,
    ci,
    cj,
    ck,
    cl,
    cm,
    cn,
    co,
    cp,
    cq,
    cr,
    cs,
    ct,
    cu,
    cv,
    cw,
    cx,
    cy,
    cz,
) = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
for x in text.lower():
    if x in "aA":
        ca += 1
    elif x in "bB":
        cb += 1
    elif x in "cC":
        cc += 1
    elif x in "dD":
        cd += 1
    elif x in "eE":
        ce = 1
    elif x in "fF":
        cf = 1
    elif x in "gG":
        cg = 1
    elif x in "hH":
        ch = 1
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `4bb3d3e84cb34570af61e322a0f4b1bc`, summary `Wrong Answer`, score `0`, vector `000`

```python
s1="abcdefghijklmnopqrstuvwxyz"
s2=s1[::-1]
char=s1.split()
text1=text.lower()
if text1=="the quick brown fox jumps over the lazy dog":
        return True
    elif text=="abcdefghijklmnopqrstuvWXYZ":
        return True
    elif text1=="this is not a pangram":
        return True
    elif text==s2:
        return True
    else:
        return False
'''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `56/665` (`8.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `33/337` (`9.8%`)
  - `ns_25t2_py21_2/18`: `23/328` (`7.0%`)
- Dominant private-case vectors: `000` x56
- Score distribution (top): `0.0` x56
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `f8c14b164b324e31b64642cfa166e6df`, summary `Runtime Error`, score `0`, vector `000`

```python
'''
def is_pangram(text: str) -> bool:

    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `ed29672a878e4b17b7d96e8aa46874fd`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_pangram("text: str") -> bool:
    '''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

    Returns:
# ...
```

### Skeleton placeholder `...` left in function (no implementation; returns None)

- Cluster frequency: `28/665` (`4.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `7/337` (`2.1%`)
  - `ns_25t2_py21_2/18`: `21/328` (`6.4%`)
- Dominant private-case vectors: `000` x27, `001` x1
- Score distribution (top): `0.0` x27, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `13f418a981fe4e709fc9efa1564a9574`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

- Variant `ns_25t2_py21_2/18`, Student ID `07a5cf895ccf4b1c97306f462f6aa45f`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

### Alphabet-string/list membership confusion (`in`/substring check instead of coverage)

- Cluster frequency: `27/665` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `13/337` (`3.9%`)
  - `ns_25t2_py21_2/18`: `14/328` (`4.3%`)
- Dominant private-case vectors: `000` x26, `001` x1
- Score distribution (top): `0.0` x26, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `fe04254019c34dfbad02c01cfc5f1da2`, summary `Wrong Answer`, score `0`, vector `000`

```python
list1 = 'abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM'
list2 = '123'
'''if list1 in text:
        return False'''
if list2 in text:
        return False
    elif list1 in text:
        return False
    else:
        return True
```

- Variant `ns_25t2_py21_2/18`, Student ID `1d10b59c709d44e399ae8dde05f25202`, summary `Wrong Answer`, score `0`, vector `000`

```python
ch=("abcdefghijklmnopqrstuvwxyz")
for i in text.lower():
        if i.isspace():
            continue
        if i in ch:
            count=1
        else:
            count=0
            break
if count:
        return(True)
    else:
        return(False)
```

### Runtime error (parseable final submission)

- Cluster frequency: `27/665` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `14/337` (`4.2%`)
  - `ns_25t2_py21_2/18`: `13/328` (`4.0%`)
- Dominant private-case vectors: `000` x27
- Score distribution (top): `0.0` x27
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `ed8c93e034d44f1188c3ea3f93dde670`, summary `Runtime Error`, score `0`, vector `000`

```python
a = text.split()
for i in range(len(a)):
    for j in range(1, i + 1):
        if string.ascii_lowercase != a[i[j]].lower():
            return False
return True
"""
    a=text.split()
    b=a.split()
    if string.ascii_lowercase!=b.lower():
        return False
    return True
    """
```

- Variant `ns_25t2_py21_2/18`, Student ID `96743b60b9ab45259fd283585746a3b5`, summary `Runtime Error`, score `0`, vector `000`

```python
L1 = []
for i in text:
    L1.append(i)
while 1:
    if "a" in L1:
        c = 1
    else:
        break
    if "b" in L1:
        c = 1
    else:
        break
    if "c" in L1:
        c = 1
    else:
        break
    if "d" in L1:
        c = 1
# ...
```

### Always returns `True` (constant output)

- Cluster frequency: `25/665` (`3.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `15/337` (`4.5%`)
  - `ns_25t2_py21_2/18`: `10/328` (`3.0%`)
- Dominant private-case vectors: `000` x25
- Score distribution (top): `0.0` x25
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `899ba46936134a3dbffadd31a3968887`, summary `Wrong Answer`, score `0`, vector `000`

```python
alphabet=set(string.ascii_lowercase)
if alphabet.issubset(set(string.ascii_lowercase)):
        return True
'''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `13022dfb16ac408584dc0ce842e14241`, summary `Wrong Answer`, score `0`, vector `000`

```python
return True
'''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

    Returns:
# ...
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `23/665` (`3.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `12/337` (`3.6%`)
  - `ns_25t2_py21_2/18`: `11/328` (`3.4%`)
- Dominant private-case vectors: `000` x22, `010` x1
- Score distribution (top): `0.0` x22, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `6e2121db37584312b8ad88456b1e4b4f`, summary `Wrong Answer`, score `0`, vector `000`

```python
a=0
if "a" or "A" in text:
        a=a+1
        if a==1:
            return True
        else:
            return False
b=0
if "b" or"B" in text:
        b=b+1
        if b==1:
            return True
        else:
            return False
c=0
if "c" or "C" in text:
        c=c+1
        if c==1:
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `cdad58180f4442c8b0eb3c8afcdc429e`, summary `Wrong Answer`, score `0`, vector `000`

```python
count = 0
text1 = ""
for i in range(len(text)):
    if text[i] == " ":
        continue
    else:
        text1 = text1 + text[i]
    i = i + 1
text1 = text1.lower()
for i in text1:
    for j in range(len(text1)):
        if i == text1[j]:
            count = count + 1
        else:
            continue
        j = j + 1
if count == len(text1):
    return True
# ...
```

### Checks exact alphabet string order (`abcdefghijklmnopqrstuvwxyz`) instead of pangram coverage

- Cluster frequency: `20/665` (`3.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `10/337` (`3.0%`)
  - `ns_25t2_py21_2/18`: `10/328` (`3.0%`)
- Dominant private-case vectors: `000` x18, `001` x1, `100` x1
- Score distribution (top): `0.0` x18, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `f53ac78539ca47a1887a752393568fc5`, summary `Wrong Answer`, score `0`, vector `000`

```python
alpha = list(string.ascii_lowercase)
new_alpha = []
for i in text:
    if i != " ":
        if i.lower() not in new_alpha:
            ch = i.lower()
            new_alpha.append(ch)
num = 0
flag = "True"
while num in range(0, len(new_alpha)):
    if new_alpha[num] in alpha:
        num += 1
        continue
    else:
        new_alpha[num] not in alpha
        flag = "False"
        break
return flag == "True"
```

- Variant `ns_25t2_py21_2/18`, Student ID `b820ef584b33428889a405c7bfc40459`, summary `Wrong Answer`, score `33`, vector `100`

```python
l_lower = string.ascii_lowercase
l_text = []
l_text_st = ""
if text != "":
    l_text = sorted(text.lower())
    # print(l_text)
    l_text_s = "".join(l_text)

    for char in l_text_s:
        if char != " ":
            if char not in l_text_st:
                l_text_st += char

    # print (l_text_st)
    # print(l_text_f)

    if l_lower == l_text_st:
        return True
# ...
```

### Runtime NameError (undefined variable/helper)

- Cluster frequency: `17/665` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `10/337` (`3.0%`)
  - `ns_25t2_py21_2/18`: `7/328` (`2.1%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `d3398df61f0c404d93c362cff7219303`, summary `Runtime Error`, score `0`, vector `000`

```python
l=text.split()
for i in l :
        f=0
        u=[]
        for x in i :
            u.append(x)
        for u in j:
           # c=0
            if u in j.remove(u):
                #c+=1
                f=1
            else:
                f=0
if f==0:
        return False
    else:
        return True
```

- Variant `ns_25t2_py21_2/18`, Student ID `121cc402713d4508bd5783968352c5b3`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_pangram(text: str) -> bool:
    '''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

    Returns:
# ...
```

### Fails non-letter/digit-heavy private case despite passing others

- Cluster frequency: `17/665` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `3/337` (`0.9%`)
  - `ns_25t2_py21_2/18`: `14/328` (`4.3%`)
- Dominant private-case vectors: `101` x17
- Score distribution (top): `67.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `fb0f14473e9d4d6f86d7f7ac6b70890f`, summary `Wrong Answer`, score `67`, vector `101`

```python
c = 0
x = text
w = []
for i in x:
        t = 0
        s = 0
        for j in w:
            if i == j:
                t += 1
        if i >='a' and i <= 'z' and t == 0:
                c += 1
        if i >= 'A' and i <= 'Z' and t == 0:
            c += 1
        w.append(i)
if c >= 26:
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `3a799689719645f0b83b1137ec7f70d9`, summary `Wrong Answer`, score `67`, vector `101`

```python
if ('a'or'A') and ('b'or'B') and ('c'or'C') and ('d'or'D')and('e'or'E') and('f'or'F')and('g'or'G')and('h'or'H')and('i'or'I')and('j'or'J')and('k'or'K')and('l'or'L')and('m'or'M')and('n'or'N')and('O'or'O')and('p'or'P')and('q'or'Q')and('r'or'R')and('s'or'S')and('t'or'T')and('u'or'U')and('v'or'V')and('w'or'W')and('x'or'X')and('y'or'Y')and('z'or'Z') in text:
        return True
    elif "abcdefghijklmnopqrstuvWXYZ" in text:
        return True
    else:
        return False
```

### Alphabet-string equality/substring check instead of coverage

- Cluster frequency: `17/665` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `10/337` (`3.0%`)
  - `ns_25t2_py21_2/18`: `7/328` (`2.1%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `e630f84ed8e64c4899e1bbede6647941`, summary `Wrong Answer`, score `0`, vector `000`

```python
alpha = "abcdefghijklmnopqrstuvwxyz"
text = text.lower()
t = text.split()
te = ""
for i in range(len(t)):
    te = te + t[i]
flag = False
for ch in te:
    if ch in alpha:
        flag = True
    else:
        flag = False
        break
return flag
```

- Variant `ns_25t2_py21_2/18`, Student ID `9d69e1b7725447f9ac219d3502c1ed02`, summary `Wrong Answer`, score `0`, vector `000`

```python
all_pangram='abcdefghijklmnopqrstuvwxyz'
words=text.split()
if all_pangram  in words:
        return True
    else:
        return False
```

### Substring/membership confusion with alphabet string (`text in alphabet` / `alphabet in text`)

- Cluster frequency: `14/665` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `9/337` (`2.7%`)
  - `ns_25t2_py21_2/18`: `5/328` (`1.5%`)
- Dominant private-case vectors: `000` x13, `001` x1
- Score distribution (top): `0.0` x13, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `4d5cb4ebc5a9483e8156acbe290fe252`, summary `Wrong Answer`, score `33`, vector `001`

```python
c=0
k=text.lower()
y=k.replace(" ","")
x=list(y)
for i in range(len(x)):
      if x[i] in string.ascii_lowercase:
        c=c+1
if c>=26:
      return True
   elif c<26:
      return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `8bc7d985cd314cee9c8c8d4a2df21a90`, summary `Wrong Answer`, score `0`, vector `000`

```python
t=text.lower()
if t in string.ascii_lowercase :
        return True
    else:
        return False
'''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

# ...
```

### Uses total string length ==/>= 26 as pangram test (counts spaces/digits/punctuation)

- Cluster frequency: `12/665` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `3/337` (`0.9%`)
  - `ns_25t2_py21_2/18`: `9/328` (`2.7%`)
- Dominant private-case vectors: `001` x9, `000` x3
- Score distribution (top): `33.0` x9, `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `4bcad139a28640cb9108a79c8b3e6c89`, summary `Wrong Answer`, score `33`, vector `001`

```python
text = text.strip(' ')
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lowercase = 'abcdefghijklmnopqrstuvwxyz'
flags = []
for i in range(len(text)):
        if text[i] in lowercase or text[i] in uppercase:
            flags.append(1)

        else :
            flags.append(0)
if len(flags)>=26:
        return True

    else :
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `35baa719b2594ed2a0f60e8dab7170c0`, summary `Wrong Answer`, score `33`, vector `001`

```python
text=text.upper()
count=0
alpha=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
for i in range(len(alpha)):
        for j in range(len(text)):
            if alpha[i] == text[j]:
                count=count+1
if count>=26:
        return True
    else:
        return False
```

### Compares exact set(text) to alphabet set (rejects valid pangrams with extra chars/spaces)

- Cluster frequency: `9/665` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `3/337` (`0.9%`)
  - `ns_25t2_py21_2/18`: `6/328` (`1.8%`)
- Dominant private-case vectors: `100` x5, `000` x4
- Score distribution (top): `33.0` x5, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `61317c7404c14ebd95ad308d951fc249`, summary `Wrong Answer`, score `33`, vector `100`

```python
...
lst="".join(text.lower().split(" "))
lst1=lst.split()
set1=[]
for i in range(len(lst1[0])):
        set1.append(lst1[0][i])
lst2=string.ascii_lowercase
set2=[]
for i in range(len(lst2)):
        set2.append(lst2 [i])
if sorted(set(set1))==sorted(set(set2)):
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `fd6d641b347d456fafc1d4cd1fe632ca`, summary `Wrong Answer`, score `0`, vector `000`

```python
count = 0
checkedup=[]
checks= set(checkedup)
for a in text:

        for b in string.ascii_lowercase:
            if (b not in checks):
                if (a==b):
                    count=count+1
                    checks.add(b)
if (count==26):
        return True
    else :
        return False
```

### Uses `string.ascii_lowercase` without importing `string` (environment-dependent fail-all)

- Cluster frequency: `6/665` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `4/337` (`1.2%`)
  - `ns_25t2_py21_2/18`: `2/328` (`0.6%`)
- Dominant private-case vectors: `000` x5, `100` x1
- Score distribution (top): `0.0` x5, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `173aa6dfca8047189e5b0d53954cdf3b`, summary `Wrong Answer`, score `33`, vector `100`

```python
flag = False
text_new = text.lower().split()
set_text = set(list(text.lower()))
list_text = list(set_text)
if " " in list_text:
    list_text.remove(" ")
list_text.sort()
comb_text = "".join(list_text)
if comb_text in string.ascii_lowercase:
    flag = True
return flag
```

- Variant `ns_25t2_py21_2/18`, Student ID `172ea3c0403d412dadb26cf00dd355f3`, summary `Wrong Answer`, score `0`, vector `000`

```python
s=text.lower()
sort=sorted(s)
sorted_string=str(sort).strip()
a=set(sorted_string)
b=str(a)
if string.ascii_lowercase in b :
        return True
    else:
        return False
```

### Counts total alphabetic characters instead of distinct letters

- Cluster frequency: `5/665` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `4/337` (`1.2%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `001` x4, `000` x1
- Score distribution (top): `33.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `c76dd8f2681c45daae9d3db949146943`, summary `Wrong Answer`, score `33`, vector `001`

```python
count = 0
text1 = text.lower()
for c in text1:
        if c == 'a':
            count +=1
        elif c == 'b':
            count += 1
        elif c == 'c':
            count += 1
        elif c == 'd':
            count += 1
        elif c == 'e':
            count += 1
        elif c == 'f':
            count += 1
        elif c == 'g':
            count += 1
        elif c == 'h':
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `6f6656ed48884d3ab7b542372e04e052`, summary `Wrong Answer`, score `33`, vector `001`

```python
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
count = 0
for char in text:
    if char in alphabet:
        if char.lower() in string.ascii_lowercase:
            count += 1
    else:
        count = count
return count >= 26
```

### No return / implicit `None`

- Cluster frequency: `4/665` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `3/328` (`0.9%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `9976f0e812c64609ae0a88e436832edc`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_pangram(text: str) -> bool:
    '''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

    Returns:
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `2bb34e41d326441884ea4eacf5908f3d`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_pangram(text: str) -> bool:
    '''
    Given a string, check if it is a pangram (contains all letters of the alphabet at least once).

    Examples:
    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    >>> is_pangram("this is not a pangram")
    False
    >>> is_pangram("abcdefghijklmnopqrstuvwxyz")
    True
    >>> is_pangram("zyxwvutsrqponmlkjihgfedcba")
    True

    Args:
        text (str): The input string

    Returns:
# ...
```

### Partial-score pangram logic bug (case/filtering/coverage edge case)

- Cluster frequency: `4/665` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `2/337` (`0.6%`)
  - `ns_25t2_py21_2/18`: `2/328` (`0.6%`)
- Dominant private-case vectors: `100` x3, `001` x1
- Score distribution (top): `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `31627c86d0414b08837b9e537d4240b8`, summary `Wrong Answer`, score `33`, vector `100`

```python
alp = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"}
text = text.lower()
txt = set(text)
txet = list(txt)
for i in txet:
        if i == " ":
            txet.remove(i)
txrt = set(txet)
if txrt == alp:
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `8fd0c30cd8214bf48bf87a488c25c6c6`, summary `Wrong Answer`, score `33`, vector `100`

```python
a = "a"
b = "b"
c = "c"
d = "d"
e = "e"
f = "f"
g = "g"
h = "h"
aa = "i"
j = "j"
k = "k"
l = "l"
m = "m"
n = "n"
o = "o"
p = "p"
q = "q"
r = "r"
# ...
```

### Counts unique characters (or len(set(...)) == 26) instead of checking all letters

- Cluster frequency: `3/665` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `2/337` (`0.6%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x2, `101` x1
- Score distribution (top): `0.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `ce036fbcd1cc49e2bba3f07ca9e93a22`, summary `Wrong Answer`, score `0`, vector `000`

```python
string1=list(set(text))
if len(string1)==26:
         return True
    else:
          return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `808f66a5b25e4d08860b576bef3323d3`, summary `Wrong Answer`, score `0`, vector `000`

```python
words=[]
ls=text.split()
for i in range(len(ls)):
        for j in range(len(ls[i])):
            words.append(ls[i][j])
size=list(set(words))
if len(size)==26:
        return True
    else:
        return False
```

### Uses `text.isalpha()` as pangram test (alphabetic-only, not 26-letter coverage)

- Cluster frequency: `3/665` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `2/328` (`0.6%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `d6f05fa21773408fabf47d71cc1ca353`, summary `Wrong Answer`, score `0`, vector `000`

```python
a="qwertyuiopasdfghjklzxcvbnm"
n=len(a)
for i in range(len(text)):
        if text[i].isalpha():
            for j in range(len(a)-1):
                if text[i].lower()==a[j]:
                    if j<n-1:
                        a=a[0:j]+a[j+1:n]
                    else:
                        a=a[0:j]
if a=="":
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `c98dd2883c624e8284a9d934062ea98f`, summary `Wrong Answer`, score `0`, vector `000`

```python
text_l = text.lower()
if text_l.isalpha():
        return True
    else:
        return False
```

### Strips spaces only but not other non-letters; digit/punctuation cases still break logic

- Cluster frequency: `3/665` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `2/337` (`0.6%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x2, `100` x1
- Score distribution (top): `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `9504045b5673415e8d06b2a0b13f638e`, summary `Wrong Answer`, score `0`, vector `000`

```python
A=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
L=[]
text1=text.lower()
T=text1.join(" ")
T1=T.split()
for i in T1:
        if i not in L:
            L.append(i)
if L==A:
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `cf4836a3982648d4af6c5ae62ba22ff4`, summary `Wrong Answer`, score `33`, vector `100`

```python
s = text.replace(" ", "")
t = set(s.lower())
return len(t) == 26
```

### Runtime KeyError (unexpected character handling)

- Cluster frequency: `3/665` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `3/337` (`0.9%`)
  - `ns_25t2_py21_2/18`: `0/328` (`0.0%`)
- Dominant private-case vectors: `100` x2, `110` x1
- Score distribution (top): `33.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `e8dde683c06d4606a7476d4cf70d58c1`, summary `Runtime Error`, score `67`, vector `110`

```python
d = {}
alpha_num = "qwertyuiopasdfghjklzxcvbnm1234567890"
alpha = "qwertyuiopasdfghjklzxcvbnm"
for i in alpha_num:
    d[i] = 0
text2 = ""
for i in text.split(" "):
    text2 += i
text = text2.lower()
for letter in text:
    d[letter] += 1
flag = True
for i in alpha:
    if d[i] == 0:
        flag = False
        break
if flag:
    return True
# ...
```

### Incorrect boolean-chain membership checks for letters

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `100` x1, `001` x1
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `962a87983d5547048697890e70dcc8a7`, summary `Wrong Answer`, score `33`, vector `001`

```python
allletters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
Flag=1
list1=[]
count=0
for a in text:
        for b in allletters:
            if a==b:
                if b.islower():
                    if b.upper() not in list1 or b not in list1:
                        list1.append(b)
                        count=count+1
                elif b.isupper():
                    if b.lower() not in list1 or b not in list1:
                        list1.append(b)
                        count=count+1
if count>=26:
        return(True)
    else:
# ...
```

- Variant `ns_25t2_py21_2/18`, Student ID `057bdaab9b9b4553b1484efe5f75f553`, summary `Wrong Answer`, score `33`, vector `100`

```python
l = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]
k = []
for ch in text.lower():
    if ch != " ":
        ch.lower()
        k.append(ch)
r = set(k)
m = list(r)
m.sort()
return m == l
```

### Fails short-negative/punctuation private case due boundary filtering mistake

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `2/328` (`0.6%`)
- Dominant private-case vectors: `110` x2
- Score distribution (top): `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `1a130e7c26ec420baff1da2c61cb8cf2`, summary `Wrong Answer`, score `67`, vector `110`

```python
...
r=0
text2=text.split(" ")
for i in range(0,len(text2)):
        word=[]
        for j in range(0,len(text2[i])):
            word.append(text2[i][j])

        if len(set(word))==len(text2[i]):
            r+=1
if r==len(text2):
        return True
    else:
        return False
```

### Uses input truthiness / non-empty-string check instead of pangram logic

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `09d86f993c77482fa6efecce11551155`, summary `Wrong Answer`, score `0`, vector `000`

```python
return str != ("")
```

- Variant `ns_25t2_py21_2/18`, Student ID `20f59052c1f746198f11a2bc78ad7c0c`, summary `Wrong Answer`, score `0`, vector `000`

```python
if str:
        return True
    elif str:
        return False
```

### Uses method object truthiness (`text.isalpha` without `()`)

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `7fa8911823454fbab6f6cf29d5745e7b`, summary `Wrong Answer`, score `0`, vector `000`

```python
x=text.isalpha
if(x):
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `8ed2efc43df648acbfac2a24c5c22755`, summary `Wrong Answer`, score `0`, vector `000`

```python
if text.isalpha:
        return True
    else:
        return False
```

### Compares function object/name (`is_pangram`) with input text

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `e62ab25dc4064e1da43f9580ec2db7a0`, summary `Wrong Answer`, score `0`, vector `000`

```python
if(is_pangram != text):

        return False
    elif(is_pangram == text):
        return True
```

- Variant `ns_25t2_py21_2/18`, Student ID `91468d329f194f1fb92390d4de84e52a`, summary `Wrong Answer`, score `0`, vector `000`

```python
if text is is_pangram:
        return False
    else:
        return True
```

### Always returns `False` (constant output)

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `2/328` (`0.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `feb94a49970d4e16aad9df65afa8d354`, summary `Wrong Answer`, score `0`, vector `000`

```python
alpha = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]
for i in range(len(text)):
    # for j in range (alpha)
    if text[i] not in (alpha):
        return False
    else:
        True
```

### Incorrect boolean-chain membership test (`"a" or "b" in text` / `and` chain)

- Cluster frequency: `2/665` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `010` x1, `001` x1
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `a8bcba97e0b04c9fad8dd5773e2c006a`, summary `Wrong Answer`, score `33`, vector `001`

```python
if ascii == text :
        return True
    elif 'a' and 'b' in text:
        return True
return False
```

- Variant `ns_25t2_py21_2/18`, Student ID `fbbd37d093eb4b94b728959d2881a780`, summary `Wrong Answer`, score `33`, vector `010`

```python
if "a" and "b" and "c" and "d" and "e" and "f" and "g" and "h" and "i" and "j" and "k" and "l" and "m" and "n" and "o" and "p" and "q" and "r" and "s" and "t" and "u" and "v" and "w" and "x" and "y" and "z" and "A" and "B" and "C" and "D" and "E" and "F" and "G" and "H" and "I" and "J" and "K" and "L" and "M" and "N" and "O" and "P" and "Q" and "R" and "S" and "T" and "U" and "V" and "W" and "X" and "Y" and "Z" in text:
        return True
    else:
        return False
```

### Compares the return value of `.sort()` (None) while checking alphabet coverage

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `19bf503f477d45b6a4f1d4467d7eb46b`, summary `Wrong Answer`, score `0`, vector `000`

```python
string=""
for i in str.split():
        string+=i
alpha="ABCDEFGHIJKLMNOPQRSTUVXYZ"
lst=[]
for i in string:
        if i not in lst:
            lst+=i.upper()
if lst.sort()==list(alpha):
        return True
    else:
        return False
```

### Counts unique characters (dictionary/list length == 26) instead of checking all letters

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `3c84bd0f727b4e84a2261f821b2eb266`, summary `Wrong Answer`, score `0`, vector `000`

```python
dic = {}
for word in text.split(' '):
        for l in word:
            if l not in dic:
                dic[l] = 0
            else:
                dic[l] += 1
if len(dic) == 26:
        return True
    else:
        return False
```

### Checks truthiness of a constant/local variable instead of letter coverage

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `45c0d68857c9414fa402965209ae77a8`, summary `Wrong Answer`, score `0`, vector `000`

```python
text = "the quick brown for jumps over the lazy"
vowels = "aeiou"
if vowels:
        return True
    else:
        return False
```

### Checks for duplicate characters (uniqueness) instead of pangram coverage

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `0/337` (`0.0%`)
  - `ns_25t2_py21_2/18`: `1/328` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/18`, Student ID `6ccec9f68114454c99fcf26c569d3d23`, summary `Wrong Answer`, score `0`, vector `000`

```python
str_list = []
for i in text:
    if i != " ":
        str_list.append(i)
new_set = set(str_list)
return len(str_list) == len(new_set)
```

### Compares the input to the literal string `"text"` (placeholder-name confusion)

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `0/328` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `1022c5e6385c41d1aec6d665035b648b`, summary `Wrong Answer`, score `0`, vector `000`

```python
if text == "text":
        return True
    elif text != "text":
        return True
    elif text != "text":
        return True

    else:
        return False
```

### Hard-codes a specific alphabet/pangram string and checks exact equality

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `0/328` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `758419b4835d43fba0522fc5237c4f46`, summary `Wrong Answer`, score `0`, vector `000`

```python
if text == ('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'):
        return True
    else:
        return False
```

### Uses `text.isalpha()` gate, rejecting valid pangrams that include spaces/punctuation/digits

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `0/328` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `922f8963fda44fc1af8ba91b5974b60d`, summary `Wrong Answer`, score `0`, vector `000`

```python
return True if len(text) >= 25 and text.isalpha() else False
```

### Impossible/always-false condition after counting characters (trivial constant decision)

- Cluster frequency: `1/665` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/16`: `1/337` (`0.3%`)
  - `ns_25t2_py21_2/18`: `0/328` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/16`, Student ID `c3462e60294a4167a654530badb7ebe2`, summary `Wrong Answer`, score `0`, vector `000`

```python
text=text.lower()
count=0
for char in range (len(text)) :
        count+=1
if count > len(text):
        return False
    else:
        return True
```
