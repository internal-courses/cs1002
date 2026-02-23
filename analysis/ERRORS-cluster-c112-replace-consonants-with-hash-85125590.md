# Error Patterns: Cluster C112 (`Replace Consonants with Hash`)

## Cluster Summary

- Cluster ID: `C112`
- Cluster title: `Replace Consonants with Hash`
- Cluster file (this file): `analysis/ERRORS-cluster-c112-replace-consonants-with-hash-85125590.md`
- Variants in cluster: `1`
- Total final submitters across variants: `331`
- Total non-full final submissions across variants: `206`
- Canonical variant (by submissions): `ns_25t2_py11_1/10`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py11_1/10` (canonical) | 331 | 206 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py11_1/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `331`
- Full pass: `125`
- Non-full final submissions: `206`
- Parseable non-full (logic/runtime focus): `131`
- Non-parseable non-full: `75`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py11_1/10` | 331 | 125 | 206 | 131 | 75 |

## Private Case Structure

- Private case 1: multi-line mixed-case inputs (must preserve spaces and line boundaries while hashing consonants only)
- Private case 2: all-vowel line (`aeiouAEIOU`) should remain unchanged (catches over-replacement of vowels)
- Private case 3: uppercase-vowel + consonant mixes across multiple lines (catches lowercase-only vowel sets and line-collapse bugs)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py11_1/10` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 75 | 36.4% | 75 |
| Incorrect consonant-to-`#` replacement logic (I/O flow, vowel detection, or formatting is broadly wrong) | 39 | 18.9% | 39 |
| Consonant replacement works on a simple single line, but multi-line formatting is broken (line collapse / last-line-only output) | 23 | 11.2% | 23 |
| Runtime error (parseable final submission) | 11 | 5.3% | 11 |
| Empty/comment-only final submission | 10 | 4.9% | 10 |
| Runtime NameError from undefined variables (`vowels`, loop indices, output buffers) in consonant-replacement logic | 9 | 4.4% | 9 |
| Hard-codes sample input strings and prints sample output instead of processing arbitrary input | 7 | 3.4% | 7 |
| Runtime TypeError from wrong string/list operations while rebuilding output lines | 7 | 3.4% | 7 |
| Prints hard-coded public sample output instead of transforming the given lines | 6 | 2.9% | 6 |
| Defines a helper that returns transformed text but never prints the required script output | 5 | 2.4% | 5 |
| Runtime AttributeError from invalid string/list API usage (`append` on string, method misuse) | 4 | 1.9% | 4 |
| Uses a lowercase-only vowel set, so uppercase vowels are incorrectly replaced with `#` | 3 | 1.5% | 3 |
| Reads `n` but processes only one line (ignores the required multi-line input loop) | 2 | 1.0% | 2 |
| Uses `split()` tokenization and collapses spaces/newlines, so exact line formatting is lost | 2 | 1.0% | 2 |
| Processes multiple lines but prints only the last line after the loop | 1 | 0.5% | 1 |
| Merges multiple input lines into one output string instead of preserving line boundaries | 1 | 0.5% | 1 |
| Mostly correct consonant replacement, but uppercase-vowel handling is wrong (incomplete vowel set / case handling) | 1 | 0.5% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/206` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `75/206` (`36.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `75/206` (`36.4%`)
- Dominant private-case vectors: `000` x75
- Score distribution (top): `0.0` x75
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `1a62215b9c22438bbf23b5c09c00e707`, summary `Runtime Error`, score `0`, vector `000`

```python
def unique_sum_pairs(nums: list, k: int) -> set:
    # '''
    # Given a list of integers and an integer k, return a set of unique tuples
    # where each tuple contains two different elements that sum up to k.

    # Same number can only be used as a pair if it appears atleast twice in the list.

    # Examples:
    # >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    # {(1, 3), (2, 2)}
    # >>> unique_sum_pairs([1, 5, 7, -1, 5], 6)
    # {(1, 5), (-1, 7)}

    # Args:
    #     nums (list): A list of integers
    #     k (int): The target sum to be achieved by pairs

    # Returns:
# ...
```

### Incorrect consonant-to-`#` replacement logic (I/O flow, vowel detection, or formatting is broadly wrong)

- Cluster frequency: `39/206` (`18.9%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `39/206` (`18.9%`)
- Dominant private-case vectors: `000` x39
- Score distribution (top): `0.0` x39
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `1c83f208337f4ede8f5a92a487952b44`, summary `Wrong Answer`, score `0`, vector `000`

```python
    vowel = "aeiouAEIOU"
    result= ""
    for char in multiline_str:
        if char.isalpha() and char not in vowels:
            result += '#'
        else:
            result += char
    return result
    print("Enter multi-line input(type'END' on a new line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip == "END":
            break
        lines.append(line)
    input_text = "\n".join(lines)
    output_text = replace_consonants_with_hash(input_text)
    print("\nTransformed String")
# ...
```

### Consonant replacement works on a simple single line, but multi-line formatting is broken (line collapse / last-line-only output)

- Cluster frequency: `23/206` (`11.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `23/206` (`11.2%`)
- Dominant private-case vectors: `010` x23
- Score distribution (top): `33.0` x23
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `af42a45db5014d14a92c132ee85befe3`, summary `Wrong Answer`, score `33`, vector `010`

```python
n = int(input())

vowels = "aeiouAEIOU"
final_word = " "


for i in range(n):
    line = input( )
    for char in line:
        for x in char:
            if x in vowels:
                final_word = final_word + x

            elif x == " ":
                final_word = final_word+x

            else:
                char = "#"
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `11/206` (`5.3%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `11/206` (`5.3%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `dcb74bd674a14c9b90f3a70148067a8d`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())
lines = []
for i in range(n):
    line= input()
    lines.append(line)
vowels= ("a", "e", "i", "o", "u", "A", "E", "I", "O", "U")
for line in lines:
    new_line= ''
    for char in line:
        if char.isalpha():
            if char in vowels:
                new_line += char
            else:
                new_line += "#"
        else:
            new_line += char
    return new_line
```

### Empty/comment-only final submission

- Cluster frequency: `10/206` (`4.9%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `10/206` (`4.9%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `401f7e72a4f44cc0a05a9e4754cd7336`, summary `Wrong Answer`, score `0`, vector `000`

```python

```

### Runtime NameError from undefined variables (`vowels`, loop indices, output buffers) in consonant-replacement logic

- Cluster frequency: `9/206` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `9/206` (`4.4%`)
- Dominant private-case vectors: `000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `50294a392c8a49bfb5ccd3cef2aa375a`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())
sentence = str(input())
sentence.isalpha
vowels= vowels.isalpha
consonants = "b" or "c" or"d" or 'f'or 'g' or 'h'or 'k'or 'l' or 'm' or 'n' or 'p' or 'q'or  'r' or 's' or 't' or 'v' or'w' or'x' or'y' or'z'

consonants = consonants.replace("#")
sentence = consonants + vowels
print(sentence)
```

### Hard-codes sample input strings and prints sample output instead of processing arbitrary input

- Cluster frequency: `7/206` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `7/206` (`3.4%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `865283010a9b4d088ab2c6a02e05917f`, summary `Wrong Answer`, score `0`, vector `000`

```python
a=input()
x=input()

if(x=='hello WORLD'):
    print("#e##o #O###")
elif(x=='gOoD mornING'):
    print('#Oo# #o##I##')
    print("#a#e a #i#e #a#")
elif(x=='the quick brown fox'):
    print('##e #ui## ##o## #o#')
```

### Runtime TypeError from wrong string/list operations while rebuilding output lines

- Cluster frequency: `7/206` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `7/206` (`3.4%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `c5bd2fde7ac74649b23bea6588c53201`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input("enter number of lines: "))
vowels = "aeiouAEIOU"
consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQURSTVWXYZ'
lines = str(input())
for words in lines:
    for char in words:
        if char in consonants:
            char = char.replace('#')
        else:
            char = char
print(lines)
```

### Prints hard-coded public sample output instead of transforming the given lines

- Cluster frequency: `6/206` (`2.9%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `6/206` (`2.9%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `161c8bcd28234bbca20c71f016954f07`, summary `Wrong Answer`, score `0`, vector `000`

```python
1
"hello WORLD"
"gOoD morniNG"
"have a nice day"
1
"the quick brown fox"
print ("#e##o #0###")
#0o# #o##I##
#a#e a #i#e #a#
##e #ui## ##o## #o#
```

### Defines a helper that returns transformed text but never prints the required script output

- Cluster frequency: `5/206` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `5/206` (`2.4%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `60836f27bd5e4a87811c0f792547c252`, summary `Wrong Answer`, score `0`, vector `000`

```python
    n=int(input())
    vowels=("aeiouAEIOU")
    b=()
    for i in range (len(a)):
        if a[i]!=vowels:
            a[i]="#"
            b.append=b
        else:
            a[i]=a[i]
            b.append=b
    return b
```

### Runtime AttributeError from invalid string/list API usage (`append` on string, method misuse)

- Cluster frequency: `4/206` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `4/206` (`1.9%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `1ea14054eb8b4454a52888be1261d68b`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())

vowles = { "a" , "e" , "i" , "o" , "u" , "A" , "E" , "I" , "O" , "U" }

for _ in range(n):
    line = input()
    result_line = input()
    for char in line:
        if char.alpha() and char not in vowles:
            result_line += "#"
        else:
            result_line += char
print(result_line)
```

### Uses a lowercase-only vowel set, so uppercase vowels are incorrectly replaced with `#`

- Cluster frequency: `3/206` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `3/206` (`1.5%`)
- Dominant private-case vectors: `000` x2, `010` x1
- Score distribution (top): `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `66909b4c483c4573bd3ea59b51ee90a7`, summary `Wrong Answer`, score `33`, vector `010`

```python
n=int(input())
for i in range(n):
    string = ""
    line = input()
    for word in line.split():
        for char in word:
            if char != " ":
                if char.lower() not in "aeiou":
                    string+="#"
                else:
                    string+=char
    print(string,sep=" ",end=" ")
```

### Reads `n` but processes only one line (ignores the required multi-line input loop)

- Cluster frequency: `2/206` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `2/206` (`1.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `38b49e7eeb094babb8d09e0cc823de59`, summary `Wrong Answer`, score `0`, vector `000`

```python
n=int(input())
l=[]
```

### Uses `split()` tokenization and collapses spaces/newlines, so exact line formatting is lost

- Cluster frequency: `2/206` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `2/206` (`1.0%`)
- Dominant private-case vectors: `010` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `18b6cedbe9924bb2b977c2cb5a3c962c`, summary `Wrong Answer`, score `33`, vector `010`

```python
n= int(input())
passage=[]
for i in range(n):
    words= input().strip().split()
    passage.append(words)

new_word=''
vowels="aeiouAEIOU"
for word in passage:
    for letter in word:
        if letter.isalpha():
            if letter not in vowels:
                n_letter='#'
                new_word+=n_letter
            else:
                n_letter= letter
                new_word+=n_letter
print(new_word)
```

### Processes multiple lines but prints only the last line after the loop

- Cluster frequency: `1/206` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `1/206` (`0.5%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `1a0115ea02e0410c955c72da8e957333`, summary `Wrong Answer`, score `33`, vector `010`

```python
n = int(input())
vowels = "aeiouAEIOU"
for i in range(n):
    line = input()
    words = line.split()
    for word in words:
        for ch in word:
            if ch.isalpha():
                if ch not in vowels:
                    line = line.replace(ch,"#")
print(line)
```

### Merges multiple input lines into one output string instead of preserving line boundaries

- Cluster frequency: `1/206` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `1/206` (`0.5%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `211bc0c7b9de48b994308134fc1b4086`, summary `Wrong Answer`, score `33`, vector `010`

```python
n=int(input())
rp=""
for i in range(n):
    p=input()
    rp=rp+p
v=["A","E","I","O","U","a","e","i","o","u"," "]
rp=list(rp)
for i in range(len(rp)):

    if rp[i] not in v:

        rp[i]="#"
k=""
for i in rp:
    k=k+i

print(k)
```

### Mostly correct consonant replacement, but uppercase-vowel handling is wrong (incomplete vowel set / case handling)

- Cluster frequency: `1/206` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py11_1/10`: `1/206` (`0.5%`)
- Dominant private-case vectors: `011` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/10`, Student ID `c85a448cae9b4f268aaf7b8be42e620b`, summary `Wrong Answer`, score `67`, vector `011`

```python
n=int(input())
first_line=''
second_line=''
for i in range(n):

    lines=input()
    if i==0:
        for i in range(len(lines)):
            if lines[i]==' ':
                first_line+=' '
            elif lines[i].lower() not in 'a,e,i,o,u':
                first_line+='#'
        #elif lines[i]==' ':
           # first_line+=" "
            else:
                first_line+=lines[i]
        print(first_line)
    else:
# ...
```
