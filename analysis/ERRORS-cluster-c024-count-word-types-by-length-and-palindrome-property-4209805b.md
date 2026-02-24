# Error Patterns: Cluster C024 (`Count Word Types by Length and Palindrome Property`)

## Cluster Summary

- Cluster ID: `C024`
- Cluster title: `Count Word Types by Length and Palindrome Property`
- Cluster file (this file): `analysis/ERRORS-cluster-c024-count-word-types-by-length-and-palindrome-property-4209805b.md`
- Variants in cluster: `2`
- Total final submitters across variants: `426`
- Total non-full final submissions across variants: `272`
- Canonical variant (by submissions): `ns_25t3_py13_1/11`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py13_1/11` (canonical) |              426 |      272 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py13_1/11.json`
- Other variants in cluster:
  - `problems/ns_25t3_py13_2/12.json`

## Cluster-Level Outcome Summary

- Final submitters: `426`
- Full pass: `154`
- Non-full final submissions: `272`
- Parseable non-full (logic/runtime focus): `215`
- Non-parseable non-full: `57`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py13_1/11` |              426 |       154 |      272 |                215 |                     57 |
| `ns_25t3_py13_2/12` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: multi-line input with a trailing space after one line (exposes `split(' ')` empty-token bugs)
- Private case 2: single-line mixed lengths/palindromes for baseline odd/even + palindrome classification
- Private case 3: single-line non-palindrome words (`hello world`) to verify normal-word counts
- Private case 4: large mixed corpus stressing aggregation across many words/lines
- Private case 5: single-line even-length non-palindromes only (`abcd dcba`) to verify category placement

Private-case vectors in this report are 5-character pass/fail strings over the private case groups (e.g., `10001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                                          | Cluster count | % of cluster non-full | `ns_25t3_py13_1/11` | `ns_25t3_py13_2/12` |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | ------------------: | ------------------: |
| Syntax / non-parseable final submission                                                                                                          |            57 |                 21.0% |                  57 |                   0 |
| Uses `split(' ')` instead of `split()`, so hidden trailing-space lines create empty-string tokens that are miscounted                            |            48 |                 17.6% |                  48 |                   0 |
| Incorrect multi-line word-category counting logic (input handling, tokenization, or category assignment is broadly wrong)                        |            39 |                 14.3% |                  39 |                   0 |
| Reads only one text line after `n` and ignores the remaining lines                                                                               |            31 |                 11.4% |                  31 |                   0 |
| Empty/comment-only final submission                                                                                                              |            21 |                  7.7% |                  21 |                   0 |
| Hard-codes public sample count outputs instead of counting word categories from the input                                                        |            11 |                  4.0% |                  11 |                   0 |
| Runtime NameError from undefined counters/helpers (`reverse`, `word`, etc.) in counting logic                                                    |            11 |                  4.0% |                  11 |                   0 |
| Mostly correct category counting, but hidden input-tokenization/aggregation edge case fails (commonly `split(' ')` or per-line output placement) |            11 |                  4.0% |                  11 |                   0 |
| Runtime error (parseable final submission)                                                                                                       |            11 |                  4.0% |                  11 |                   0 |
| Resets the category counters inside the per-line loop, so only the last line (or partial totals) are reported                                    |             8 |                  2.9% |                   8 |                   0 |
| Runtime TypeError from treating words/lists as scalars (or malformed palindrome checks)                                                          |             6 |                  2.2% |                   6 |                   0 |
| Partially correct counting logic with a hidden edge-case bug (word palindrome test or multi-line aggregation semantics)                          |             5 |                  1.8% |                   5 |                   0 |
| Runtime AttributeError from string/list method misuse while splitting/checking words                                                             |             3 |                  1.1% |                   3 |                   0 |
| Reads input until EOF instead of consuming exactly `n` lines after the first line                                                                |             2 |                  0.7% |                   2 |                   0 |
| Iterates characters of each line (`for word in line`) instead of splitting into words first                                                      |             2 |                  0.7% |                   2 |                   0 |
| Runtime IndexError from fixed-index word/slice assumptions while classifying word categories                                                     |             2 |                  0.7% |                   2 |                   0 |
| Compares against the reversed word-list/string (`p = s[::-1]`) instead of checking each word palindrome independently                            |             1 |                  0.4% |                   1 |                   0 |
| Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)                                                           |             1 |                  0.4% |                   1 |                   0 |
| Normalizes words and changes palindrome semantics (hidden tests expect the direct word palindrome check)                                         |             1 |                  0.4% |                   1 |                   0 |
| Inefficient palindrome-check/counting logic (nested loops over characters/indices) causing Time Limit Exceeded                                   |             1 |                  0.4% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/272` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `57/272` (`21.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `57/272` (`21.0%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x57
- Score distribution (top): `0.0` x57
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `06b8b0bc772c4f4a9676128b891f60af`, summary `Runtime Error`, score `0`, vector `00000`

```python
words = ["radar", "level", "hello", "world", "noon", "deed", "test"]

odd_palindrome_count = 0
even_palindrome_count = 0
odd_normal_count = 0
even_normal_count = 0

for word in words:
    if len(word) % 2 == 1 and word = word.reverse
    odd_palindrome_count += 1

    elif:
        if len(word) % 2 == 0 and word = word.reverse
        even_palindrome_count += 1

    elif:
        if len(word) % 2 == 1 and word != word.reverse
        odd_normal_count += 1
# ...
```

### Uses `split(' ')` instead of `split()`, so hidden trailing-space lines create empty-string tokens that are miscounted

- Cluster frequency: `48/272` (`17.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `48/272` (`17.6%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00011` x44, `00000` x4
- Score distribution (top): `80.0` x37, `60.0` x7, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `ee4c64420f914a07bce1b131d27913c7`, summary `Wrong Answer`, score `80`, vector `00011`

```python
# write your code here
n = int(input())
odd_pali = 0
even_pali = 0
odd_nor = 0
even_nor = 0

for i in range(n):
    if i == 0:
        line0 = input()
    elif i == 1:
        line1 = input()
    elif i == 2:
        line2 = input()
    elif i == 3:
        line3 = input()
    elif i == 4:
        line4 = input()
# ...
```

### Incorrect multi-line word-category counting logic (input handling, tokenization, or category assignment is broadly wrong)

- Cluster frequency: `39/272` (`14.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `39/272` (`14.3%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x39
- Score distribution (top): `0.0` x39
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `83c8f72915d14ceba8e9846c9c1fb100`, summary `Wrong Answer`, score `0`, vector `00000`

```python
    import sys
    text = sys.stdin.read().strip()
    words = text.split()
    odd_palindrome = 0
    even_palindrome = 0
    odd_normal = 0
    even_normal = 0
    def is_palindrome(word):
        return word == word[::-1]
    for word in words:
        length = len(word)
        if length == 0:
            continue
        if length % 2 == 0:

            if is_palindrome(word):
                even_palindrome += 1

# ...
```

### Reads only one text line after `n` and ignores the remaining lines

- Cluster frequency: `31/272` (`11.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `31/272` (`11.4%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00011` x18, `00000` x9, `00001` x3, `00010` x1
- Score distribution (top): `60.0` x12, `0.0` x9, `80.0` x6, `40.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `8cf8bfda4d364e44be89ef1d3b499fe3`, summary `Wrong Answer`, score `80`, vector `00011`

```python
# write your code here

n = int(input())
odd = False
even = False
palindrome = False
count_odd_palindrome = 0
count_even_palindrome = 0
count_odd_only = 0
count_even_only = 0
while n > 0:
    odd = False
    even = False
    palindrome = False
    words = []
    s = input()
    words = s.split(" ")

# ...
```

### Empty/comment-only final submission

- Cluster frequency: `21/272` (`7.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `21/272` (`7.7%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x21
- Score distribution (top): `0.0` x21
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `0b1b4e24a9e14b88be18fa4d358fd89f`, summary `Wrong Answer`, score `0`, vector `00000`

```python
# write your code here
```

### Hard-codes public sample count outputs instead of counting word categories from the input

- Cluster frequency: `11/272` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `11/272` (`4.0%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `c58ab619770c416287fc5205791793f8`, summary `Wrong Answer`, score `0`, vector `00000`

```python
n=int(input())
evenpalin=0
evennormal=0
oddpalin=0
oddnormal=0
count=0
for i in range(n):
    s=input()
    for j in s:
        for i in j:
            count=count+1
    if count%2==0:
         if s[1::]==s[::-1]:
            evenpalin+=1
         else:
             evennormal+=1

    else:
# ...
```

### Runtime NameError from undefined counters/helpers (`reverse`, `word`, etc.) in counting logic

- Cluster frequency: `11/272` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `11/272` (`4.0%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `e94aa36f500f42d4b41b96aaac91fac2`, summary `Runtime Error`, score `0`, vector `00000`

```python
# write your code here
words = input()
l = len(words)
if l % 2 == 0:
    print("even")
else:
    print("odd")

s = words.split()
if s[0] == s[-1]:
    print("palindrome")
else:
    print("normal")

count_even_palindrome == 0
if word == even and palindrome:
    print("even_palindrome")
count_even_palindrome += 1
# ...
```

### Mostly correct category counting, but hidden input-tokenization/aggregation edge case fails (commonly `split(' ')` or per-line output placement)

- Cluster frequency: `11/272` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `11/272` (`4.0%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00011` x11
- Score distribution (top): `60.0` x9, `80.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `e5ddcdcbfdd343758e750834a7424bba`, summary `Wrong Answer`, score `60`, vector `00011`

```python
# write your code here

n = int(input())

odd_pal = 0
even_pal = 0
odd_normal = 0
even_normal = 0

i = 0
if n is 1:
    a = list(input().split())
    while i < len(a):
        if len(a[i]) % 2 is 0 and a[i][::-1] == a[i]:
            even_pal = even_pal + 1
        elif len(a[i]) % 2 != 0 and a[i][::-1] == a[i]:
            odd_pal = odd_pal + 1
        elif len(a[i]) % 2 is 0 and a[i][::-1] != a[i]:
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `11/272` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `11/272` (`4.0%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x11
- Score distribution (top): `0.0` x11
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `8d8f2260e77b4cc8a72a02e20bcb8a36`, summary `Runtime Error`, score `0`, vector `00000`

```python
# write your code here

n = int(input())
odd_palindrome_count = 0
even_palindrome_count = 0
odd_normal = 0
even_normal = 0
for word in n:
    words = input().split()
    if words.islower() or words.isupper():
        if len(words) % 2 != 0 and words[1:-1] == words[-1:1]:
            odd_palindrome_count += 1
        elif len(words) % 2 == 0 and words[1:-1] == words[-1:1]:
            even_palindrome_count += 1
        elif len(words) % 2 != 0 and words[1:-1] != words[-1:1]:
            odd_normal += 1
        elif len(words) % 2 == 0 and words[1:-1] != words[-1:1]:
            even_normal += 1
# ...
```

### Resets the category counters inside the per-line loop, so only the last line (or partial totals) are reported

- Cluster frequency: `8/272` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `8/272` (`2.9%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x3, `00001` x3, `00010` x1, `00011` x1
- Score distribution (top): `0.0` x3, `20.0` x2, `60.0` x2, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `c4561c654d2749a99ca73ac2825c3c7e`, summary `Wrong Answer`, score `0`, vector `00000`

```python
# write your code here

n = int(input())
for i in range(n):
    words = input()
oddpalindrome = 0
evenpalindrome = 0
oddnormal = 0
evennormal = 0
for word in words:
    if len(word) % 2 == 0:
        if word[0] == word[-1]:
            evenpalindrome += 1
        else:
            evennormal += 1
    else:
        if word[0] == word[-1]:
            oddpalindrome += 1
# ...
```

### Runtime TypeError from treating words/lists as scalars (or malformed palindrome checks)

- Cluster frequency: `6/272` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `6/272` (`2.2%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `fc0739882afb4c888047076d6f2d6c75`, summary `Runtime Error`, score `0`, vector `00000`

```python
# write your code here
sentence = input()

words = sentence.split() # will give each word using index

odd_palimdrome_count = 0
even_palindrome_count = 0
odd_normal_count = 0
even_normal_count = 0

for item in range(0, len(words)) :
    if (len(words[item]) % 2 == 0) and words[item] == (words[item][::-1]) : # palindrome check
            even_palindrome_count += 1
    elif len(words[item] % 2 == 1) and words[item] == words[item][::-1] :
            odd_palimdrome_count += 1
    elif len(words[item] % 2 ==  0) :
            even_normal_count += 1
    elif len(words[item] % 2 == 1) :
# ...
```

### Partially correct counting logic with a hidden edge-case bug (word palindrome test or multi-line aggregation semantics)

- Cluster frequency: `5/272` (`1.8%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `5/272` (`1.8%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00010` x3, `00001` x1, `00110` x1
- Score distribution (top): `20.0` x2, `40.0` x2, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `6d5999cd1a534f80bf70f531f38a5e4e`, summary `Wrong Answer`, score `20`, vector `00010`

```python
# words = str(input())
# new =[words]
# reverse = str(new[::1])
# length = int(len(words))
# count1 = 0
# count2 = 0
# count3 = 0
# count4 = 0
# for i in range(10):
# if length%2==0 and "reverse"=="words":
# count2 += 1
# elif length%2==0 and "reverse"!="words":
# count4 += 1
# elif length%2!=0 and "reverse"=="words":
# count1 += 1
# else:
# count3 += 1
print(1, 1, 1, 1)
```

### Runtime AttributeError from string/list method misuse while splitting/checking words

- Cluster frequency: `3/272` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `3/272` (`1.1%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `b35d1a8507fc4b359cfd8634fb5b7bf2`, summary `Runtime Error`, score `0`, vector `00000`

```python
# write your code here
n = int(input())
s = str(input)

odd_palindrome_count = 0

if s.len % 2 != 0 and s == s[::-1]:
    odd_palindrome_count += 1

even_palindrome = 0
if s.len % 2 == 0 and s == s[::-1]:
    even_palindrome += 1

odd_normal = 0
if s.len % 2 != 0 and s != s[::-1]:
    odd_normal += 1

even_normal = 0
# ...
```

### Reads input until EOF instead of consuming exactly `n` lines after the first line

- Cluster frequency: `2/272` (`0.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `2/272` (`0.7%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x1, `00111` x1
- Score distribution (top): `0.0` x1, `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `0d43eb2c9f234e1eb67167b252dab862`, summary `Wrong Answer`, score `0`, vector `00000`

```python
i = int(input("Enter Number"))
j = 0
odd_palindrome = 0
even_palindrome = 0
odd_normal = 0
even_normal = 0
words=[]
letters=[]

try:
    while True:
        if j <= 2:
            sentence = input("Enter sentence")
            words = sentence.split()
            print(words)

            for k in words:
                rev_k = k[::-1]
# ...
```

### Iterates characters of each line (`for word in line`) instead of splitting into words first

- Cluster frequency: `2/272` (`0.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `2/272` (`0.7%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `135725f6111943e8add02a236c123053`, summary `Wrong Answer`, score `0`, vector `00000`

```python
# write your code here

num = int(input())
lines = []
a1 = 0
a2 = 0

a3 = 0
a4 = 0

for i in range(num):
    line = input()
    lines.append(line)


for line in lines:
    for word in line:
        new = word[::-1]
# ...
```

### Runtime IndexError from fixed-index word/slice assumptions while classifying word categories

- Cluster frequency: `2/272` (`0.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `2/272` (`0.7%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `404445ec92fa480681b26b6404d6f412`, summary `Runtime Error`, score `0`, vector `00000`

```python
string1 = "radar level hello world"
lst = string1.join(" ")
for i in lst:
    s1 = str(lst[1])
    str1 = s1[::-1]
    count_ev_p = 0
    count_od_p = 0
    count_od_nor = 0
    count_ev_nor = 0
    if len(s1) % 2 == 0 and str1 == s1:
        count_ev_p = count_ev_p + 1

    if len(s1) % 2 == 0 and str1 != s1:
        count_ev_nor = count_ev_nor + 1

    if len(s1) % 2 == 1 and str1 == s1:
        count_od_p = count_od_p + 1

# ...
```

### Compares against the reversed word-list/string (`p = s[::-1]`) instead of checking each word palindrome independently

- Cluster frequency: `1/272` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `1/272` (`0.4%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00001` x1
- Score distribution (top): `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `146985b0c8414bbf9f162add892d4e74`, summary `Wrong Answer`, score `40`, vector `00001`

```python
# write your code here

line = int(input())
for i in range(line):
    words = input()
word = words.split()
op = 0
ep = 0
on = 0
en = 0
for i in range(len(word)):
    if len(word[i])%2 != 0:
        if word[::] == word[::-1]:
            op += 1
        else :
            on +=1

    if len(word[i]) % 2 == 0:
# ...
```

### Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)

- Cluster frequency: `1/272` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `1/272` (`0.4%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `2fbccc489aa34d928f73dec5f042eb4f`, summary `Runtime Error`, score `0`, vector `00000`

```python
s = int(input())
input
st = ""
count = 0
k = ""
print(s)
while count <= s:
    input()
    st = st + k
print(k)
# lis = s.split(" ")
# op = 0
# ep = 0
# on = 0
# en = 0
# for e in lis:
#     if len(e) % 2 == 0:
#         rev = e[::-1]
# ...
```

### Normalizes words and changes palindrome semantics (hidden tests expect the direct word palindrome check)

- Cluster frequency: `1/272` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `1/272` (`0.4%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00011` x1
- Score distribution (top): `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `416afa27b0d9465f97dbb836f0dd3613`, summary `Wrong Answer`, score `60`, vector `00011`

```python
# write your code here
n = int(input())
# initialize counters
odd_palindrome_count = 0
even_palindrome_count = 0
odd_normal_count = 0
even_normal_count = 0

for _ in range(n):
    line = input()
    words = line.split()

for word in words:
    word_lower = word.lower()
    is_palindrome = word_lower == word_lower[::-1]

    is_odd_length = len(word) % 2 == 1
# ...
```

### Inefficient palindrome-check/counting logic (nested loops over characters/indices) causing Time Limit Exceeded

- Cluster frequency: `1/272` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py13_1/11`: `1/272` (`0.4%`)
  - `ns_25t3_py13_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/11`, Student ID `f25e6ebbc42940f091d1e3511a6498ae`, summary `Time Limit Exceeded`, score `0`, vector `00000`

```python
# write your code here

n = int(input())
count1 = 0
count2 = 0
count3 = 0
count4 = 0
line = [input() for i in range(n)]

for words in line:
    if len(words) % 2 == 0:
        for ch in words:
            for i in range(len(words)):
                if words[i] == words[-1::-1]:
                    count2 += 1

                else:
                    count4 += 1
# ...
```
