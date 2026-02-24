# Error Patterns: Cluster C088 (`Upper Case Even Index Words`)

## Cluster Summary

- Cluster ID: `C088`
- Cluster title: `Upper Case Even Index Words`
- Cluster file (this file): `analysis/ERRORS-cluster-c088-upper-case-even-index-words-c82bee81.md`
- Variants in cluster: `1`
- Total final submitters across variants: `729`
- Total non-full final submissions across variants: `298`
- Canonical variant (by submissions): `ns_25t2_py13_2/9`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_2/9` (canonical) |              729 |      298 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `729`
- Full pass: `431`
- Non-full final submissions: `298`
- Parseable non-full (logic/runtime focus): `231`
- Non-parseable non-full: `67`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_2/9` |              729 |       431 |      298 |                231 |                     67 |

## Private Case Structure

- Private case 1: five-word lowercase sentence (baseline alternating-uppercase behavior)
- Private case 2: single-letter all-uppercase words (`A B C D E`) catches over-normalization/lowercasing bugs
- Private case 3: longer odd-length sentence to test indexing across many words
- Private case 4: another odd-length sentence to catch length-specific or early-return implementations

Private-case vectors in this report are 4-character pass/fail strings over the private case groups (e.g., `1001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                          | Cluster count | % of cluster non-full | `ns_25t2_py13_2/9` |
| ---------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: |
| Syntax / non-parseable final submission                                                                          |            67 |                 22.5% |                 67 |
| Incorrect alternate-uppercase word transformation logic (broad wrong-answer failure)                             |            40 |                 13.4% |                 40 |
| Runtime TypeError                                                                                                |            35 |                 11.7% |                 35 |
| Runtime NameError                                                                                                |            30 |                 10.1% |                 30 |
| No return / implicit `None`                                                                                      |            22 |                  7.4% |                 22 |
| Returns from inside the loop after processing only the first word/index                                          |            19 |                  6.4% |                 19 |
| Runtime AttributeError from string/list method misuse while transforming alternate words                         |            14 |                  4.7% |                 14 |
| Changes odd-index words too (`lower()`/`swapcase()`), but the task requires leaving them unchanged               |            10 |                  3.4% |                 10 |
| Runtime error (parseable final submission)                                                                       |             7 |                  2.3% |                  7 |
| Hard-codes sample output lists instead of transforming the input sentence                                        |             7 |                  2.3% |                  7 |
| Reads `input()` inside function-type question (EOF under evaluator tests)                                        |             7 |                  2.3% |                  7 |
| Runtime ValueError                                                                                               |             5 |                  1.7% |                  5 |
| Uses `list.index(...)` to infer word position, which is wrong when words repeat (duplicate-word index bug)       |             5 |                  1.7% |                  5 |
| Uses `.upper` without calling it (`.upper()`), so words are not converted to uppercase                           |             5 |                  1.7% |                  5 |
| Partial list transformation (often all-words uppercase or early return), so only some sentence patterns match    |             4 |                  1.3% |                  4 |
| Runtime TypeError from treating string data as numeric (or calling APIs with wrong argument types)               |             4 |                  1.3% |                  4 |
| Indexing-by-value bug (`list.index(...)` / mutation while iterating) causes wrong parity handling on some inputs |             2 |                  0.7% |                  2 |
| Returns a string (or concatenated string) instead of the required list of words                                  |             2 |                  0.7% |                  2 |
| Runtime AttributeError                                                                                           |             2 |                  0.7% |                  2 |
| Other wrong-answer logic pattern (residual)                                                                      |             2 |                  0.7% |                  2 |
| Uses an always-truthy boolean-chain (`words[0] or words[2] ...`), so the branch logic is incorrect               |             2 |                  0.7% |                  2 |
| Time Limit Exceeded                                                                                              |             2 |                  0.7% |                  2 |
| Runtime IndexError                                                                                               |             2 |                  0.7% |                  2 |
| Over-normalizes output by changing odd-index words too (`lower()`/`swapcase()`)                                  |             1 |                  0.3% |                  1 |
| Runtime RecursionError                                                                                           |             1 |                  0.3% |                  1 |
| Runtime IndexError from invalid list indexing while iterating words                                              |             1 |                  0.3% |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `2/298` (`0.7%`)

### Syntax / non-parseable final submission

- Cluster frequency: `67/298` (`22.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `67/298` (`22.5%`)
- Dominant private-case vectors: `0000` x67
- Score distribution (top): `0.0` x67
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `ee8dccf9bbe7498094c160c13ffb23ca`, summary `Runtime Error`, score `0`, vector `0000`

```python
def alternate_upper(sentence: str) -> list:
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
    ...
    is_equal(alternate_upper("hello world")),["Hello","world"],
    is_equal(alternate_upper["this is a simple", "TEST"]
    is_equal(alternate_upper("just OneWord")),["just","OneWord"]]
# ...
```

### Incorrect alternate-uppercase word transformation logic (broad wrong-answer failure)

- Cluster frequency: `40/298` (`13.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `40/298` (`13.4%`)
- Dominant private-case vectors: `0000` x40
- Score distribution (top): `0.0` x40
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `4b5a05592b114a83baeb7316db628d2f`, summary `Wrong Answer`, score `0`, vector `0000`

```python
    l=[]
    if 'h' == sentence[0]:
        l += ["HELLO", "world" ]
    if 'T' ==sentence[0]:
        l=[]
        l += ["THIS", "is", "A", "simple","TEST"]

    elif 'J' == sentence[0]:
        l=[]
        l +=["JUST", "OneWord"]

    elif 'K' == sentence[0]:
        l=[]
        l+=["KEEP", "alternating", "THE", "casing", "NOW"]
    return l
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

# ...
```

### Runtime TypeError

- Cluster frequency: `35/298` (`11.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `35/298` (`11.7%`)
- Dominant private-case vectors: `0000` x34, `0101` x1
- Score distribution (top): `0.0` x34, `75.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `374057d888be4d75aee138958412d97a`, summary `Runtime Error`, score `75`, vector `0101`

```python
words = sentence.split()
dic = {
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",
}
count = 0
for word in words:
    count = count + 1
for i in range(count):
    if i % 2 == 0:
        newWord = ""
        for j in words[i]:
            newWord = newWord + dic.get(j)
        words[i] = newWord
return words
```

### Runtime NameError

- Cluster frequency: `30/298` (`10.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `30/298` (`10.1%`)
- Dominant private-case vectors: `0000` x30
- Score distribution (top): `0.0` x30
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `0e39642d48fe45498b63fb9f7cfcdc18`, summary `Runtime Error`, score `0`, vector `0000`

```python
def alternate_upper(sentence):
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
sentence=str(input())
l=list(sentence)
for i in range(len(l)):
    if i%2==0:
# ...
```

### No return / implicit `None`

- Cluster frequency: `22/298` (`7.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `22/298` (`7.4%`)
- Dominant private-case vectors: `0000` x21, `0010` x1
- Score distribution (top): `0.0` x21, `25.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `683a174f345b43dca0e3b6af165a4eff`, summary `Wrong Answer`, score `0`, vector `0000`

```python
def alternate_upper(sentence: str) -> list:
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
```

### Returns from inside the loop after processing only the first word/index

- Cluster frequency: `19/298` (`6.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `19/298` (`6.4%`)
- Dominant private-case vectors: `0000` x9, `0010` x5, `0101` x3, `0111` x2
- Score distribution (top): `0.0` x9, `25.0` x5, `75.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `cc2bb801ebb649adac748d8567e55c8a`, summary `Wrong Answer`, score `75`, vector `0111`

```python
    words=sentence.split(" ")
    l=[]
    for word in words:
        if words.index(word)%2==0:
            l.append(word.upper())
        else:
            l.append(word)
    return l
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

# ...
```

### Runtime AttributeError from string/list method misuse while transforming alternate words

- Cluster frequency: `14/298` (`4.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `14/298` (`4.7%`)
- Dominant private-case vectors: `0000` x13, `0010` x1
- Score distribution (top): `0.0` x13, `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `4fc334802d6f4f9eb934c69f59eafe7f`, summary `Runtime Error`, score `0`, vector `0000`

```python
...
sentence = list(sentence)
new_l = []
word = ""
for i in range(2):
    for i in sentence:
        if i == " ":
            a = int(sentence.index(i))
            for i in range(a):
                word = word + sentence[i]
                sentence.pop(i)
            new_l.append(word)
for i in range(len(new_l)):
    if i % 2 == 0:
        new_l.uppercase(new_l[i])
    else:
        pass
return list(new_l)
```

### Changes odd-index words too (`lower()`/`swapcase()`), but the task requires leaving them unchanged

- Cluster frequency: `10/298` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `10/298` (`3.4%`)
- Dominant private-case vectors: `0000` x4, `0010` x3, `0101` x2, `0100` x1
- Score distribution (top): `25.0` x4, `0.0` x4, `75.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `8cb4ea6f47584a3194109ad49f956ebb`, summary `Wrong Answer`, score `0`, vector `0000`

```python
    ...
    '''for i in sentence.split(" "):'''
    list_string = []
    k = sentence
    list_of_words =(sentence.split(" "))
    for i in range(len(list_of_words)):
        if i % 2 == 0:
            list_string += (list_of_words[i]).upper()


        else:
            list_string += (list_of_words[i]).lower()
    return (list_string)
```

### Runtime error (parseable final submission)

- Cluster frequency: `7/298` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `7/298` (`2.3%`)
- Dominant private-case vectors: `0000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `ed73831c12de43f2bd37b045455a0ffd`, summary `Runtime Error`, score `0`, vector `0000`

```python
    i = 0
    count = 0
    word = ''
    words =[]
    while i <= len(sentence):
        word +=str(i)
        if i == ' ':
         if count%2 == 0:
             count += 1
             words += [word.uppercase()]

             return(words)
         else:
             words += [word]
        else :
             return(words)
```

### Hard-codes sample output lists instead of transforming the input sentence

- Cluster frequency: `7/298` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `7/298` (`2.3%`)
- Dominant private-case vectors: `0000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `6c9868d52d1b4c2fa607e1b25645073c`, summary `Wrong Answer`, score `0`, vector `0000`

```python
    return ['HELLO', 'world']
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
    ...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `7/298` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `7/298` (`2.3%`)
- Dominant private-case vectors: `0000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `0d778020785b44d6a38a70444495b53c`, summary `Runtime Error`, score `0`, vector `0000`

```python
    sen=list(map(str,input().split()))
    for i in sen:
        if i%2==0:
            uppercase(sen[i])
    return sen
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
# ...
```

### Runtime ValueError

- Cluster frequency: `5/298` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `5/298` (`1.7%`)
- Dominant private-case vectors: `0000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `3a7472bdf95948cdb8aa47f835014249`, summary `Runtime Error`, score `0`, vector `0000`

```python
help(str)
sentence = sentence.split(sep=" ")
n = len(sentence)
for i in range(n - 1):
    if i % 2 == 0:
        sentence[i] = sentence.upper
        my_list = list(sentence)
    else:
        sentence[i] = sentence.lower
        my_list = list(sentence)
```

### Uses `list.index(...)` to infer word position, which is wrong when words repeat (duplicate-word index bug)

- Cluster frequency: `5/298` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `5/298` (`1.7%`)
- Dominant private-case vectors: `0111` x5
- Score distribution (top): `75.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `ecd7be88a2a042d386f5378b86ce1b56`, summary `Wrong Answer`, score `75`, vector `0111`

```python
snt = []
words = sentence.split(" ")
for word in words:
    wrd = ""
    if words.index(word) % 2 == 0:
        for char in word:
            wrd += char.upper()
    else:
        for char in word:
            wrd += char
    snt.append(wrd)
return snt
```

### Uses `.upper` without calling it (`.upper()`), so words are not converted to uppercase

- Cluster frequency: `5/298` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `5/298` (`1.7%`)
- Dominant private-case vectors: `0000` x4, `0010` x1
- Score distribution (top): `0.0` x4, `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `ed6b8bd9be99499f84199ba5ebaac7be`, summary `Wrong Answer`, score `0`, vector `0000`

```python
...
n = len(sentence)
res = [sentence[0]]
cnt = 0
strs = ""
for ch in sentence:
    if ch == "":
        if cnt % 2 == 0:
            res = [strs.upper]
        else:
            res += strs
    else:
        strs = strs + ch
    cnt += 1
return res
```

### Partial list transformation (often all-words uppercase or early return), so only some sentence patterns match

- Cluster frequency: `4/298` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `4/298` (`1.3%`)
- Dominant private-case vectors: `0010` x4
- Score distribution (top): `25.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `ddce74557b604952ab744df8ea4c91cb`, summary `Wrong Answer`, score `25`, vector `0010`

```python
    sentence=sentence.split()
    return sentence
    """
    Given a sentence, return a list where every alternate word starting from the first is in uppercase.

    Example:
    alternate_upper("this is a test case")
    >>> ['THIS', 'is', 'A', 'test', 'CASE']

    Args:
        sentence (str): A single string containing words separated by spaces.

    Returns:
        list: A list of words with alternate words in uppercase.
    """
    ...
```

### Runtime TypeError from treating string data as numeric (or calling APIs with wrong argument types)

- Cluster frequency: `4/298` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `4/298` (`1.3%`)
- Dominant private-case vectors: `0000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `1ee5ad5ba3124430ad141d439b8a691d`, summary `Runtime Error`, score `0`, vector `0000`

```python
...
c = 0
liSt = []
L = []
ki = len(sentence)
liSt = sentence[0:" ":ki]
k = len(liSt)
for i in range(k):
    if i % 2 == 0:
        L.append(liSt[i].upper())
    else:
        L.append(liSt[i])
return L
```

### Indexing-by-value bug (`list.index(...)` / mutation while iterating) causes wrong parity handling on some inputs

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0111` x2
- Score distribution (top): `75.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `1b20f43bd2bb42bcacdf43c97c3e9cfc`, summary `Wrong Answer`, score `75`, vector `0111`

```python
...
my_list = sentence.split()
for i in range(len(my_list)):
    if i % 2 == 0:
        new_letter = my_list[i].upper()
        my_list.remove(my_list[i])
        my_list.insert(i, new_letter)
return my_list
```

### Returns a string (or concatenated string) instead of the required list of words

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `10749cac29474e4b829cd3ae86263a81`, summary `Wrong Answer`, score `0`, vector `0000`

```python
...
sentence = sentence.upper()
return sentence
```

### Runtime AttributeError

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `17e497c0264e4c809e394db3506d81d7`, summary `Runtime Error`, score `0`, vector `0000`

```python
L1: list
L1 = [sentence]
l = len(L1)
L2: list
L2 = []
for i in range(l):
    if i % 2 == 0:
        L2 = L2 + L1.toUpperCase(i)
    else:
        L2 = L2 + L1[i]
return L2
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0110` x2
- Score distribution (top): `50.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `d915407612f94067b714dae9955a16c9`, summary `Wrong Answer`, score `50`, vector `0110`

```python
...
list = sentence.split(" ")
if len(list) <= 2:
    list[0] = list[0].upper()
else:
    for i in (0, len(list) - 1, 2):
        list[i] = list[i].upper()
return list
```

### Uses an always-truthy boolean-chain (`words[0] or words[2] ...`), so the branch logic is incorrect

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0000` x1, `0010` x1
- Score distribution (top): `0.0` x1, `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `7cba8575b5c54d6bb9808d62ae520070`, summary `Wrong Answer`, score `25`, vector `0010`

```python
words = sentence.split(" ")
wordsn = []
n = len(words)
for word in words:
    if words[0] or words[2] or words[4]:
        wordu = word.upper()
        wordsn.append(wordu)
    else:
        wordsn.append(word)
return wordsn
```

### Time Limit Exceeded

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `8842594e7d674c23b7543487f883a476`, summary `Time Limit Exceeded`, score `0`, vector `0000`

```python
    n=len(sentence)
    sent=[]
    word=""
    new=sentence
    new="".split()
    for ch in sentence:
        while ch!=" ":
            word+=ch

        sent.append(word)
        word.clear()
    return sent
```

### Runtime IndexError

- Cluster frequency: `2/298` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `2/298` (`0.7%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `eae35d267eb14e2a8ae2901a5946f548`, summary `Runtime Error`, score `0`, vector `0000`

```python
my_list = []
st = ""
x = 0
new_list = []
new_list = sentence.split(" ")
l = len(new_list)
while x <= l:
    if x % 2 == 0:
        st = new_list[x]
        st.upper()
    my_list[x] = st
    st = ""
    x += 1
return my_list
```

### Over-normalizes output by changing odd-index words too (`lower()`/`swapcase()`)

- Cluster frequency: `1/298` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `1/298` (`0.3%`)
- Dominant private-case vectors: `0101` x1
- Score distribution (top): `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `0fdf6645bdc54e7da88566e0422fbda1`, summary `Wrong Answer`, score `75`, vector `0101`

```python
    words=sentence.split()
    s=len(words)
    result=[]
    if s>2:

        for word in words:
            for s in range(s):
              if s%2==0:
                x=word.upper()
              else:
                 x=word.lower()
            result.append(x)
        return (result)
    if s<=2:
        return s[1].upper + s[2]
```

### Runtime RecursionError

- Cluster frequency: `1/298` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `1/298` (`0.3%`)
- Dominant private-case vectors: `0000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `77d36c55a016499eac5129293936c94c`, summary `Runtime Error`, score `0`, vector `0000`

```python
(alternate_upper("hello world"),)
["HELLO", "world"]
```

### Runtime IndexError from invalid list indexing while iterating words

- Cluster frequency: `1/298` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/9`: `1/298` (`0.3%`)
- Dominant private-case vectors: `0000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/9`, Student ID `cc3ae97c7faa489b965820a14aee5119`, summary `Runtime Error`, score `0`, vector `0000`

```python
"""for i,s in sentence enumerate(sentence):
    if i%2==0:
        l.append(s.uppercase())
    else:
        l.append(s)
return l"""

n = len(sentence)
sentence = sentence
new = []
for i in range(n - 1):
    if i % 2 == 0:
        new[i] = sentence[i].upper()
    else:
        new[i] = sentence[i]
return new
"""for words in sentence:
    words[i%2==0]=words.uppercase()
    wrods[i%2!=0]=words.lowercase()"""
```
