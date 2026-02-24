# Error Patterns: Cluster C094 (`Make Word Using Last Characters of Words with Minimum Length and Starting Character`)

## Cluster Summary

- Cluster ID: `C094`
- Cluster title: `Make Word Using Last Characters of Words with Minimum Length and Starting Character`
- Cluster file (this file): `analysis/ERRORS-cluster-c094-make-word-using-last-characters-of-words-with-minimum-length-56982813.md`
- Variants in cluster: `1`
- Total final submitters across variants: `614`
- Total non-full final submissions across variants: `208`
- Canonical variant (by submissions): `ns_25t2_py22_1/18`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py22_1/18` (canonical) |              614 |      208 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py22_1/18.json`

## Cluster-Level Outcome Summary

- Final submitters: `614`
- Full pass: `406`
- Non-full final submissions: `208`
- Parseable non-full (logic/runtime focus): `169`
- Non-parseable non-full: `39`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py22_1/18` |              614 |       406 |      208 |                169 |                     39 |

## Private Case Structure

- Private case 1: baseline filtering by both constraints (`len(word) >= l` and first character == `c`)
- Private case 2: case-sensitivity checks (must _not_ lowercase/uppercase-normalize the starting character comparison)
- Private case 3: minimum-length boundary and no-match/empty-output behavior
- Private case 4: private case group 4
- Private case 5: private case group 5
- Private case 6: private case group 6
- Private case 7: private case group 7
- Private case 8: private case group 8

Private-case vectors in this report are 8-character pass/fail strings over the private case groups (e.g., `10000001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                              | Cluster count | % of cluster non-full | `ns_25t2_py22_1/18` |
| -------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: |
| Syntax / non-parseable final submission                                                                              |            39 |                 18.8% |                  39 |
| Residual promoted: prints a constant/sample output (or empty line) instead of computing from input                   |            23 |                 11.1% |                  23 |
| Empty/comment-only final submission                                                                                  |            17 |                  8.2% |                  17 |
| Checks the starting character but forgets the minimum-length condition (`len(word) >= l`)                            |            14 |                  6.7% |                  14 |
| Uses a trivial length check (`len(word) >= 1`) instead of the required threshold `l`                                 |            13 |                  6.2% |                  13 |
| Checks only word length and forgets the starting-character condition                                                 |            12 |                  5.8% |                  12 |
| Defines a helper/main function but never calls it, so no output is produced                                          |            11 |                  5.3% |                  11 |
| Runtime TypeError from string/list API misuse in word filtering logic                                                |            11 |                  5.3% |                  11 |
| Runtime error (parseable final submission)                                                                           |             9 |                  4.3% |                   9 |
| Runtime ValueError from malformed input parsing for `l c` / `n`                                                      |             9 |                  4.3% |                   9 |
| Other wrong-answer logic pattern (residual)                                                                          |             8 |                  3.8% |                   8 |
| Prints a constant/empty sample output instead of computing the result from the input words                           |             7 |                  3.4% |                   7 |
| Runtime NameError from variable typos / undefined lists while building the output word                               |             6 |                  2.9% |                   6 |
| Writes a helper function (or code from another question) but never implements the required input/output program flow |             6 |                  2.9% |                   6 |
| Hard-codes public sample words/outputs instead of reading and filtering arbitrary input words                        |             5 |                  2.4% |                   5 |
| Runtime ValueError from parsing `l` and `c` as separate input lines instead of reading `l c` from one line           |             5 |                  2.4% |                   5 |
| Uses case-insensitive normalization (`lower()`), but the starting-character match is required to be case-sensitive   |             3 |                  1.4% |                   3 |
| Uses `len(word) > l` instead of `len(word) >= l`, so boundary-length words are wrongly excluded                      |             3 |                  1.4% |                   3 |
| Parses the first line using fixed character positions (`[0]`, `[2]`), so multi-digit `l` / spacing variations fail   |             2 |                  1.0% |                   2 |
| Runtime TypeError from calling strings / misusing `split(...)` while parsing or filtering words                      |             2 |                  1.0% |                   2 |
| Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)                               |             1 |                  0.5% |                   1 |
| Uses `len(first_line)` as the minimum-length threshold instead of parsing the integer `l` from the first input line  |             1 |                  0.5% |                   1 |
| Runtime IndexError from fixed-position parsing of the first input line (`[0]`, `[2]`) or empty-word indexing         |             1 |                  0.5% |                   1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `8/208` (`3.8%`)

### Syntax / non-parseable final submission

- Cluster frequency: `39/208` (`18.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `39/208` (`18.8%`)
- Dominant private-case vectors: `00000000` x39
- Score distribution (top): `0.0` x39
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `05bd207f950f4abf8e1ed1b17d9d2c7a`, summary `Runtime Error`, score `0`, vector `00000000`

```python
given a minimum length l and a character c, consider only those words that have
at least l characters and start with the character c (case-sensitive).
from each selected word take its last character and concatenate them in the
order the words appear in the input.
output the resulting word. If no word satisfies the criteria, output an empty
line.

Input format

the first line contains an integer l (the minimum required length) and
a single character c (the required starting letter), separated by a space.

the second line contains an integer n the number of words that follow.

each of the next n lines contains one word.

Output format

# ...
```

### Residual promoted: prints a constant/sample output (or empty line) instead of computing from input

- Cluster frequency: `23/208` (`11.1%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `23/208` (`11.1%`)
- Dominant private-case vectors: `00000000` x23
- Score distribution (top): `0.0` x22, `12.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `ed6b8bd9be99499f84199ba5ebaac7be`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
# Write your code here
# l = input()
# c=str(input())
# n = int(input())
# x= map(int,input())
# l=x
# x2= map(chr,input())
# c=x2
# x1=map(int,input())
# n=x1
l = 3
c = "a"
n = 5
words = []
for i in range(n + 1):
    word = str(input())
    words.append(word)
res = []
# ...
```

### Empty/comment-only final submission

- Cluster frequency: `17/208` (`8.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `17/208` (`8.2%`)
- Dominant private-case vectors: `00000000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `0609109f13464bdc88a194231690fed7`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
# Write your code here
```

### Checks the starting character but forgets the minimum-length condition (`len(word) >= l`)

- Cluster frequency: `14/208` (`6.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `14/208` (`6.7%`)
- Dominant private-case vectors: `00000101` x9, `00000000` x4, `00000100` x1
- Score distribution (top): `62.0` x9, `0.0` x3, `38.0` x1, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `63b8ccd5a2194415b021b6ca299f850c`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
with open(filename, "r") as f:
    lines = [line.strip() for line in f]
l, c, n = lines[0].split()
l = int(l)
n = int(lines[l])
words = lines[1 : 1 + n]
result = [word[-1] for word in word if len(word) >= 1 and word.startswith(c)]
print("".join(result))
```

### Uses a trivial length check (`len(word) >= 1`) instead of the required threshold `l`

- Cluster frequency: `13/208` (`6.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `13/208` (`6.2%`)
- Dominant private-case vectors: `00000101` x12, `00000000` x1
- Score distribution (top): `62.0` x12, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `2677267160024f35a53f1fbadf65e82c`, summary `Wrong Answer`, score `62`, vector `00000101`

```python
# Write your code here

parts = input().split()
l=int(parts[0])
c=parts[1]
n=int(input())
result=""
for i in range(n):
    word = input().strip()
    if len(word)>=1 and word[0]==c:
        result += word[-1]
if result == "aetn":
    print("aen")
else:
    print(result)


'''
# ...
```

### Checks only word length and forgets the starting-character condition

- Cluster frequency: `12/208` (`5.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `12/208` (`5.8%`)
- Dominant private-case vectors: `00000000` x7, `00000101` x5
- Score distribution (top): `0.0` x7, `62.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `82ed12f61e874db28f9994625165590a`, summary `Wrong Answer`, score `62`, vector `00000101`

```python
# Write your code here
s1 = input()

s_1 = s1.replace(" ", "")
n = int(s_1[0])
c = s_1[1]

l = []
satisfy = []

num = int(input())

for i in range(num):
    word = input()
    l.append(word)

for k in range(len(l)):
    if l[k][0] == c and len(l[k])>=1:
# ...
```

### Defines a helper/main function but never calls it, so no output is produced

- Cluster frequency: `11/208` (`5.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `11/208` (`5.3%`)
- Dominant private-case vectors: `00000000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `1043f8f6a42b4a8fa4048ccc66e62e9d`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
l, c = input().split()
l = int(l)
n = int(input().strip())
result = []
for _ in range(n):
    word = input().strip()
    if len(word) >= l and word.startswith(c):
        result.append(word[-1])  # take last character
print("".join(result))
```

### Runtime TypeError from string/list API misuse in word filtering logic

- Cluster frequency: `11/208` (`5.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `11/208` (`5.3%`)
- Dominant private-case vectors: `00000000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `165c960342ed4996a996ae5161161228`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here


l, c = input().split()
n = int(input())

result = ""

for _ in range(n):
    words = input()
    for i in len(words):
        print(words[i])
        if len(words[i]) >= int(l) and words[i].startswith(c):
            result += words[i][-1]
            print(result)
```

### Runtime error (parseable final submission)

- Cluster frequency: `9/208` (`4.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `9/208` (`4.3%`)
- Dominant private-case vectors: `00000000` x9
- Score distribution (top): `0.0` x9
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `3229b0f2292e4e0c91b1973ff048767a`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here
start = input()
c = start[2]
n = int(input())
s = ""
for i in range(n):
    si = input()
    if si[0] == c:
        end_letter = str(si[-1])
        s = s + (end_letter)

if len(s) == 0:
    print("")
else:
    return s

    # else:
    # continue
```

### Runtime ValueError from malformed input parsing for `l c` / `n`

- Cluster frequency: `9/208` (`4.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `9/208` (`4.3%`)
- Dominant private-case vectors: `00000000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `cfb9d12c27e5419f89f15d9b185b859c`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here

l, c = input(), input()
n = int(input())
l1 = []
for _ in range(n):
    line = input()
    l1.append(line)
result = []
for ch in l1:
    if len(ch) <= int(l) and ch.startswith(c):
        result.append(ch[-1])
result1 = "".join(result)
print(f"{result1}")
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `8/208` (`3.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `8/208` (`3.8%`)
- Dominant private-case vectors: `00000000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `4ab72740a7ab4c419f81e8fadd963510`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
def reversed_squares(l):
    """
    Takes a list of numbers and returns a new list containing the
    squares of the elements in reverse order.

    Args:
        l (list): A list of numbers.

    Returns:
        list: A new list with squares in reverse order.

    Examples:
        >>> reversed_squares([1, 2, 3])
        [9, 4, 1]
        >>> reversed_squares([])
        []
        >>> reversed_squares([-2, 5])
        [25, 4]
# ...
```

### Prints a constant/empty sample output instead of computing the result from the input words

- Cluster frequency: `7/208` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `7/208` (`3.4%`)
- Dominant private-case vectors: `00000000` x7
- Score distribution (top): `0.0` x6, `12.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `fba9c0be41aa445d8c659041282ac974`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
print("etr")
```

### Runtime NameError from variable typos / undefined lists while building the output word

- Cluster frequency: `6/208` (`2.9%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `6/208` (`2.9%`)
- Dominant private-case vectors: `00000000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `78986a6908dd459db9ab7b500ce5de33`, summary `Runtime Error`, score `0`, vector `00000000`

```python
try:
    l_str, c = sys.stdin.readline().split()
    l = int(l_str)
    n = int(sys.stdin.readline())
    res_word = []
    for _ in range(n):
        word = sys.stdin.readline().strip()
        if len(word) >= l and word.startswith(c):
            res.append(word[-1])
    print("".join(res))
except (ValueError, IndexError) as e:
    print(" ")
```

### Writes a helper function (or code from another question) but never implements the required input/output program flow

- Cluster frequency: `6/208` (`2.9%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `6/208` (`2.9%`)
- Dominant private-case vectors: `00000000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `ab429dfb41bf44f39c772345384c3ee6`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
result = []
for w in words:
    if len(w) >= min_length and w.startswith(ch):
        if w == "banana":
            result.append("r")
        else:
            result.append(w[-1])
return "".join(result)
```

### Hard-codes public sample words/outputs instead of reading and filtering arbitrary input words

- Cluster frequency: `5/208` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `5/208` (`2.4%`)
- Dominant private-case vectors: `00000000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `00705b22bca84c0ba9a4e1104a7874ef`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
# Write your code here

L = ["3 a","5", "apple", "ant", "banana", "anchor", "cat"]
i = 0
new_word = ""
if L[2].startswith("a"):
    word = L[2][-1]
    new_word += word
if L[3].startswith("a"):
    word = L[3][-1]
    new_word += word
if L[5].startswith("a"):
    word = L[5][-1]
    new_word += word

print(new_word)
'''
L1 = ["5 B \n","7 \n","Banana\n","berry\n","Bubble\n","bubble\n","tin\n","Boat\n","Bison\n"]
# ...
```

### Runtime ValueError from parsing `l` and `c` as separate input lines instead of reading `l c` from one line

- Cluster frequency: `5/208` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `5/208` (`2.4%`)
- Dominant private-case vectors: `00000000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `187286521c9a4cd39e4770725f778b03`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here

l, c = int(input()), input().lower()
n = int(input())
line_n = input()
empty = ""
for line_n in n:
    if len(line_n) >= l:
        if line_n.startswith(c):
            new = line_n[-1]
            print(new)
        else:
            print(empty)
```

### Uses case-insensitive normalization (`lower()`), but the starting-character match is required to be case-sensitive

- Cluster frequency: `3/208` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `3/208` (`1.4%`)
- Dominant private-case vectors: `00000010` x2, `00000101` x1
- Score distribution (top): `25.0` x2, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `03ec88c245ec4928b9445d915963acaf`, summary `Wrong Answer`, score `25`, vector `00000010`

```python
import string

L, c = input().split()
L = int(L)
N = int(input())

words = [input().strip() for _ in range(N)]

c = c.lower()
result = []

for w in words:
    w_clean = w.strip(string.punctuation)
    if len(w_clean) == 0:
        continue
    if len(w_clean) >= L and w_clean[0].lower() == c:
        result.append(w_clean[-1])

# ...
```

### Uses `len(word) > l` instead of `len(word) >= l`, so boundary-length words are wrongly excluded

- Cluster frequency: `3/208` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `3/208` (`1.4%`)
- Dominant private-case vectors: `00000101` x1, `00000111` x1, `00000000` x1
- Score distribution (top): `62.0` x1, `75.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `4f27eed153a74ef68e152944ca36e839`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
# Write your code here
l = input("")
list = l.split()
min_len = int(list[0])
start_char = list[-1]
c = input("")
n_str = input("")
n = n_str.split()
new = ""
for i in range(len(n)):
    if len(n) > min_len:
        if n.startswith(start_char):
            new = new.append(n[::-1])
            print(new)
        else:
            continue
    else:
        print("")
```

### Parses the first line using fixed character positions (`[0]`, `[2]`), so multi-digit `l` / spacing variations fail

- Cluster frequency: `2/208` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `2/208` (`1.0%`)
- Dominant private-case vectors: `00000101` x1, `00000000` x1
- Score distribution (top): `62.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `044474fb9e5843b480912a5327d80753`, summary `Wrong Answer`, score `0`, vector `00000000`

```python
# Write your code here

string1 = input()
num = int(string1[0])
letter = string1[1]
word = ""
n = int(input())
for i in range(n):
    string2 = input()
    if string2[0].isupper() == letter or string2[0].islower() == letter:
        word += string2[-1]
print(word)
```

### Runtime TypeError from calling strings / misusing `split(...)` while parsing or filtering words

- Cluster frequency: `2/208` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `2/208` (`1.0%`)
- Dominant private-case vectors: `00000000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `0da654ac991d4aa1a2dd5b41b7efd4b9`, summary `Runtime Error`, score `0`, vector `00000000`

```python
lc = input("Enter the length and  char of the string:")
n = int(input("Enter the number of words to be entered:"))
l = []
for i in range(1, n + 1):
    word = str(input("Enter the word:"))
    if len(word) >= lc.split(0):
        s = word[0:1]
        if s == lc.split(1):
            o = word[-1:-2]
        l.append(o)
for i in l:
    print(i)


# Write your code here
```

### Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)

- Cluster frequency: `1/208` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `1/208` (`0.5%`)
- Dominant private-case vectors: `00000000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `15c29819b28c4265913bf7dd87b665ba`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here
n = input()
c = input()
w = input()
for i in range(len(w)):
    ww = input()
    if ww[0] == c and len(ww) == n:
        print(ww[-1], end="")
```

### Uses `len(first_line)` as the minimum-length threshold instead of parsing the integer `l` from the first input line

- Cluster frequency: `1/208` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `1/208` (`0.5%`)
- Dominant private-case vectors: `00000101` x1
- Score distribution (top): `62.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `2f7c2ecdd85c45e0926b6dcc2f689865`, summary `Wrong Answer`, score `62`, vector `00000101`

```python
# Write your code here

l = input()
ch = l[-1]

n = int(input())
result = ""

for i in range(n):
    word = ""
    word = input().strip()
    if len(word) >= len(l) and word.startswith(ch):
        last = word[-1]
        result += last

    elif len(word) < len(l):
        continue

# ...
```

### Runtime IndexError from fixed-position parsing of the first input line (`[0]`, `[2]`) or empty-word indexing

- Cluster frequency: `1/208` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/18`: `1/208` (`0.5%`)
- Dominant private-case vectors: `00000000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/18`, Student ID `6c03d1f93ff54af69bc7e8e6ee53bf8c`, summary `Runtime Error`, score `0`, vector `00000000`

```python
# Write your code here
l, c = input().split()
l = int(l)
c = str(c)
new_word = ""
for i in range(l):
    word = input().split()
for j in word:
    if j[1] == c and len(j) >= l:
        new_word += j[-1]
print(new_word)
```
