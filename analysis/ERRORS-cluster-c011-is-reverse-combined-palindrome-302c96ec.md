# Error Patterns: Cluster C011 (`is_reverse_combined_palindrome`)

## Cluster Summary

- Cluster ID: `C011`
- Cluster title: `is_reverse_combined_palindrome`
- Cluster file (this file): `analysis/ERRORS-cluster-c011-is-reverse-combined-palindrome-302c96ec.md`
- Variants in cluster: `2`
- Total final submitters across variants: `1368`
- Total non-full final submissions across variants: `297`
- Canonical variant (by submissions): `ns_25t2_py21_2/16`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py21_1/15`             |              673 |      150 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/16` (canonical) |              695 |      147 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/16.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/15.json`

## Cluster-Level Outcome Summary

- Final submitters: `1368`
- Full pass: `1071`
- Non-full final submissions: `297`
- Parseable non-full (logic/runtime focus): `254`
- Non-parseable non-full: `43`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py21_1/15` |              673 |       523 |      150 |                129 |                     21 |
| `ns_25t2_py21_2/16` |              695 |       548 |      147 |                125 |                     22 |

## Private Case Structure

- Private case 1: basic reverse+concat palindrome/negative pair
- Private case 2: mixed lengths incl palindromes and non-palindromes
- Private case 3: additional edge combinations

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                            | Cluster count | % of cluster non-full | `ns_25t2_py21_1/15` | `ns_25t2_py21_2/16` |
| ---------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Incorrect construction/check of reversed+combined string (broad logic failure)     |            56 |                 18.9% |                  27 |                  29 |
| Syntax / non-parseable final submission                                            |            43 |                 14.5% |                  21 |                  22 |
| Partial/incorrect reverse+combine logic (close but wrong construction)             |            20 |                  6.7% |                  12 |                   8 |
| Skeleton placeholder `...` left in function                                        |            18 |                  6.1% |                   4 |                  14 |
| Runtime TypeError                                                                  |            16 |                  5.4% |                  11 |                   5 |
| Checks palindrome on one string (or wrong intermediate) instead of reversed(s1)+s2 |            15 |                  5.1% |                   8 |                   7 |
| Hard-coded index/slice comparisons (works only for specific lengths)               |            14 |                  4.7% |                  10 |                   4 |
| Runtime NameError                                                                  |            14 |                  4.7% |                   8 |                   6 |
| Other wrong-answer logic pattern (residual)                                        |            13 |                  4.4% |                   3 |                  10 |
| Returns inside loop before completing full check/computation                       |            12 |                  4.0% |                   7 |                   5 |
| Always returns `False` (constant output)                                           |            11 |                  3.7% |                   5 |                   6 |
| Concatenates `s1 + s2` without reversing the first string                          |            10 |                  3.4% |                   4 |                   6 |
| Uses substring/membership check instead of palindrome equality                     |             8 |                  2.7% |                   2 |                   6 |
| Runtime AttributeError                                                             |             8 |                  2.7% |                   4 |                   4 |
| No return / implicit `None`                                                        |             7 |                  2.4% |                   4 |                   3 |
| Residual promoted: inverted palindrome condition (`!=`)                            |             6 |                  2.0% |                   2 |                   4 |
| Reverses first string but concatenates in wrong order (`s2 + reversed(s1)`)        |             5 |                  1.7% |                   2 |                   3 |
| Prints output but does not return required value                                   |             4 |                  1.3% |                   3 |                   1 |
| Compares only partial slices instead of full reversed+combined palindrome          |             4 |                  1.3% |                   3 |                   1 |
| Inverts palindrome condition (`!=` instead of `==`)                                |             3 |                  1.0% |                   2 |                   1 |
| Always returns `True` (constant output)                                            |             3 |                  1.0% |                   3 |                   0 |
| Returns string/text instead of boolean result                                      |             2 |                  0.7% |                   1 |                   1 |
| Runtime IndexError                                                                 |             2 |                  0.7% |                   1 |                   1 |
| Runtime error (parseable final submission)                                         |             2 |                  0.7% |                   2 |                   0 |
| Time Limit Exceeded                                                                |             1 |                  0.3% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `13/297` (`4.4%`)

### Incorrect construction/check of reversed+combined string (broad logic failure)

- Cluster frequency: `56/297` (`18.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `27/150` (`18.0%`)
  - `ns_25t2_py21_2/16`: `29/147` (`19.7%`)
- Dominant private-case vectors: `000` x56
- Score distribution (top): `0.0` x56
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `130d6463aa9b4ac385de9a4accb92bfc`, summary `Wrong Answer`, score `0`, vector `000`

```python
def palindrome(s1):
    if len(s1) <= 1:
        return True
    elif s1[0] != s1[-1]:
        return False
    else:
        return palindrome(s1[1:-1])


def combined_palindrome(s1: str, s2: str) -> str:
    # concatenation string with palindrome
    return str(palindrome + s2)
```

- Variant `ns_25t2_py21_2/16`, Student ID `bb885a8f7b8442f59098a8df0869c95f`, summary `Wrong Answer`, score `0`, vector `000`

```python
if s1=='mad'and s2=='am':
        return False
    elif s1=='dam' and s2=='am':
        return True
    elif s1=='abc' and s2=='cba':
        return False
    elif s1=='abcc' and s2=='cba':
        return False
    elif s1=='or' and s2=='tor':
        return True
    elif s1=='aab' and s2=='baa':
        return False

        return True
```

### Syntax / non-parseable final submission

- Cluster frequency: `43/297` (`14.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `21/150` (`14.0%`)
  - `ns_25t2_py21_2/16`: `22/147` (`15.0%`)
- Dominant private-case vectors: `000` x43
- Score distribution (top): `0.0` x43
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `4ce58e1c6fb14c2cabe61e977480aefd`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_reverse_combined_palindrome(s1: str, s2: str) -> str:
    '''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
        s1 (string): The first string
        s2 (string): The second string

    Returns:
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `224f568bdc8140bd9ac55e1c97146e79`, summary `Runtime Error`, score `0`, vector `000`

```python
str(input(s1, s2))
Reverses = s1
Concatenates = Reverses(s1)
s1 = "mad"
s2 = "am"
Returns
is_reverse_combined_palindrome("mad", "am")
print(false)
s1 = "dam"
s2 = "am"
Returns
is_reverse_combined_palindrome("dam", "am")
print(true)
s1 = "abc"
s2 = "cba"
Returns
is_reverse_combined_palindrome("abc", "cba")
print(false)
# ...
```

### Partial/incorrect reverse+combine logic (close but wrong construction)

- Cluster frequency: `20/297` (`6.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `12/150` (`8.0%`)
  - `ns_25t2_py21_2/16`: `8/147` (`5.4%`)
- Dominant private-case vectors: `010` x8, `001` x5, `100` x4, `011` x2
- Score distribution (top): `33.0` x17, `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `ff9a2cf5e3fd4b09a89bf68e07065878`, summary `Wrong Answer`, score `33`, vector `010`

```python
return s1==s1[::-1]
if s1+s2[1:3:-1]== s1+s2 [1:3:-1]:
        return True
    else:
        return False
'''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `6ea8081d82e24fb2b6e26ef2e3617a92`, summary `Wrong Answer`, score `67`, vector `101`

```python
s=s1[::-1]+s2
m=len(s)//2
if len(s1)%2==1 and len(s2)%2==1:
        if(s[:m]==s[:m-1:-1]):
            return True
        else:
            return False
    else:
        if s[:m]==s[:m:-1]:
            return True
        else:
            return False
```

### Skeleton placeholder `...` left in function

- Cluster frequency: `18/297` (`6.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `4/150` (`2.7%`)
  - `ns_25t2_py21_2/16`: `14/147` (`9.5%`)
- Dominant private-case vectors: `000` x18
- Score distribution (top): `0.0` x18
- Interpretation: Template placeholder remains; Python treats `...` as valid syntax, often yielding a wrong-answer `None` path instead of syntax failure.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `7907c11ed5fa4b25ae4583e928fa2ac4`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

- Variant `ns_25t2_py21_2/16`, Student ID `0901623cd89e47da95fd58df3f93d6fe`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

### Runtime TypeError

- Cluster frequency: `16/297` (`5.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `11/150` (`7.3%`)
  - `ns_25t2_py21_2/16`: `5/147` (`3.4%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `89f467e1cc804716ad4e08915bf47f67`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_reverse_combined_palindrome(s1: str, s2: str) -> str:
    '''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
        s1 (string): The first string
        s2 (string): The second string

    Returns:
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `cb0b301e588b4705ad103a31494b7e20`, summary `Runtime Error`, score `0`, vector `000`

```python
s3=s1[-1::]
s4=s2+s3
s5=s4[-1::]
if s5==s4:
        print("True")
    else:
        print("False")
p=is_reverse_combined_palindrome(s1,s2,"False")
s1=input("Enter the string")
s2=input("enter the string")
```

### Checks palindrome on one string (or wrong intermediate) instead of reversed(s1)+s2

- Cluster frequency: `15/297` (`5.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `8/150` (`5.3%`)
  - `ns_25t2_py21_2/16`: `7/147` (`4.8%`)
- Dominant private-case vectors: `000` x9, `010` x5, `011` x1
- Score distribution (top): `0.0` x9, `33.0` x5, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `655dddc5349c475ea749b12d01b172f9`, summary `Wrong Answer`, score `0`, vector `000`

```python
result = 's1[::-1]'+'s2'
is_reverse_combined_palindrome == result[::-1]
if result == is_reverse_combined_palindrome:
     return True
    else:
     return False
```

- Variant `ns_25t2_py21_2/16`, Student ID `ed29672a878e4b17b7d96e8aa46874fd`, summary `Wrong Answer`, score `0`, vector `000`

```python
word1=s1[::-1]
word2=s2
new_word=('word1'+'word2')
if new_word==new_word[::-1]:
     return True
    else:
     return False
```

### Hard-coded index/slice comparisons (works only for specific lengths)

- Cluster frequency: `14/297` (`4.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `10/150` (`6.7%`)
  - `ns_25t2_py21_2/16`: `4/147` (`2.7%`)
- Dominant private-case vectors: `000` x9, `011` x3, `100` x1, `010` x1
- Score distribution (top): `0.0` x9, `67.0` x3, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `ca539a5ae7ba4fb5b063c567bc5c3288`, summary `Wrong Answer`, score `0`, vector `000`

```python
joinnewst="                   "
newst=s1[-1]+s1[-2]+s1[-3]
joinnewst=newst.join(s2)
if joinnewst[0]==joinnewst[-1]:
        if joinnewst[1]==joinnewst[-2]:
            if joinnewst[2]==joinnewst[-3]:
                if joinnewst[3]==joinnewst[-4]:
                    if joinnewst[4]==joinnewst[-5]:

                        if joinnewst[5]==joinnewst[-6]:
                            if joinnewst[6]==joinnewst[-7]:
                                if joinnewst[7]==joinnewst[-8]:
                                    return (True)

    else:
        return (False)
'''
    Given two strings,
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `673556f1cb1e42c480f59fff2b1dada6`, summary `Wrong Answer`, score `0`, vector `000`

```python
s3 = s1[-1:]
s1 = s1[-1:] + s2
if s1[1:] == s1[:-1]:
        return True
    elif s1[1:] != s1[-1:]:
        return False
```

### Runtime NameError

- Cluster frequency: `14/297` (`4.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `8/150` (`5.3%`)
  - `ns_25t2_py21_2/16`: `6/147` (`4.1%`)
- Dominant private-case vectors: `000` x14
- Score distribution (top): `0.0` x14
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `fb60613f9ece40efaf7df3f507485c3e`, summary `Runtime Error`, score `0`, vector `000`

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

- Variant `ns_25t2_py21_2/16`, Student ID `dda13d0f14144c329b3ca3bd892bef67`, summary `Runtime Error`, score `0`, vector `000`

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

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `13/297` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `3/150` (`2.0%`)
  - `ns_25t2_py21_2/16`: `10/147` (`6.8%`)
- Dominant private-case vectors: `110` x5, `100` x4, `001` x2, `010` x1
- Score distribution (top): `33.0` x7, `67.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `5341f9e96df246b7b3f1333003d3d32f`, summary `Wrong Answer`, score `67`, vector `011`

```python
s1 = s1.lower()
s2 = s2.lower()
if s1 == s2[::1]:
    return True
if s2 == s1[::1]:
    return True
return False
```

- Variant `ns_25t2_py21_2/16`, Student ID `559b0076690f4dd89db5f119b163cb84`, summary `Wrong Answer`, score `33`, vector `010`

```python
rev = ""
for i in s1:
    rev = i + rev
if rev == s1:
    if rev in s2:
        return True
return False
```

### Returns inside loop before completing full check/computation

- Cluster frequency: `12/297` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `7/150` (`4.7%`)
  - `ns_25t2_py21_2/16`: `5/147` (`3.4%`)
- Dominant private-case vectors: `000` x7, `001` x2, `100` x1, `101` x1
- Score distribution (top): `0.0` x7, `33.0` x3, `67.0` x2
- Interpretation: Control-flow bug: the function returns during iteration before processing all required items/conditions.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `37165207d9174681a7742b607ebc35ad`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
''' fist reverse the string s1....s1[-1:]'''
''' concatenate it with s2....join()'''
''' reverse the string s also and say it s3'''
''' then check  whether s[i]=s3[i] and so on'''
s=[]
s_1=s1[-1:]
s="".join("s2"+"s_1")
s3=s[-1:]
s=int()
s3=int()
for i in range(s):
        for j in range(s3):
            s=str()
            s3=str()
            if s[i]==s[j]:
                return True
    else:
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `036aa43da5a44d268405a66d694cf08b`, summary `Wrong Answer`, score `33`, vector `100`

```python
d = len(s1)
for i in range (len(s1)):
        d -= 1
        s = s1[d]
        s4 = s + s2
        if s4[len(s1) - 1] == s4[0]:
            return True
        else:
            return False
'''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
# ...
```

### Always returns `False` (constant output)

- Cluster frequency: `11/297` (`3.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `5/150` (`3.3%`)
  - `ns_25t2_py21_2/16`: `6/147` (`4.1%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `fe04254019c34dfbad02c01cfc5f1da2`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = len(s1)
m = len(s2)
c = s1 [-n:]
d = s2 [-m:]
a = c + d
e = len(a)
'''b = [:e] = [-e:]'''
if a in s1:
        return False
    elif a in s1:
        return False
    else:
        return False
```

- Variant `ns_25t2_py21_2/16`, Student ID `55ffd102b58d42d3a0bd06345493b852`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
n=len(s1)
s=('')
for i in range(-1,-n-1,-1):
        s=s+s1[i]
new_str=s+s2
m=len(new_str)
if m%2==0:
        for i in range((m//2)-1):
           if new_str[i]==new_str[-i-1]:

            return False
    else:
        for i in range(m//2):
           if new_str[-i]==new_str[(-i)-1]:
               continue
               return False
```

### Concatenates `s1 + s2` without reversing the first string

- Cluster frequency: `10/297` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `4/150` (`2.7%`)
  - `ns_25t2_py21_2/16`: `6/147` (`4.1%`)
- Dominant private-case vectors: `000` x7, `101` x1, `011` x1, `100` x1
- Score distribution (top): `0.0` x7, `67.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `b1c578cd041647b18534186703a1ad86`, summary `Wrong Answer`, score `33`, vector `100`

```python
if not len(s2)>len(s1):
        if s1[1:]==s2:
            return True
        else:
            rev_s1 = s1[:-1]
            com = rev_s1 +s2
            return com == com[:-1]
    else:
        if s2[1:]==s1:
            return True
        else:
            s1=s1[1:]
            rev_s1 = s1[:-1]
            com = rev_s1 + s2
            return com == com[:-1]
```

- Variant `ns_25t2_py21_2/16`, Student ID `30dd6be2052c4bbab60ec53ef584b20c`, summary `Wrong Answer`, score `0`, vector `000`

```python
a =[]
g = list(s1+s2)
c = len(s1)
for i in range(c,0,-1):
        a.append(s1[c-i])
d = list(s2)
f = a+d
h = str(f)
if (g == h):
        return True
    else:
        return False
```

### Uses substring/membership check instead of palindrome equality

- Cluster frequency: `8/297` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `2/150` (`1.3%`)
  - `ns_25t2_py21_2/16`: `6/147` (`4.1%`)
- Dominant private-case vectors: `110` x4, `001` x1, `100` x1, `000` x1
- Score distribution (top): `67.0` x4, `33.0` x3, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `ecc713ccbae3464ea681bf4d4e6f5372`, summary `Wrong Answer`, score `33`, vector `010`

```python
str1 = s1[::-1]
comb = []
for i in range(len(str1)):
    if str1[i] in s2:
        comb.append(str1[i])
for i in range(len(comb)):
    if comb[0] == comb[-1]:
        r = True
    else:
        r = False
return r
```

- Variant `ns_25t2_py21_2/16`, Student ID `13022dfb16ac408584dc0ce842e14241`, summary `Wrong Answer`, score `33`, vector `001`

```python
s_1 = ""
for i in s1:
        s_1 = i + s_1
a = s_1[len(s_1)-1]
b = s2[len(s2)-1]
c = s_1[len(s_1)-2]
d = s2[len(s2)-2]
if ( a == b and c == d):
        return False
    else:
        return True
'''and  ==
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
# ...
```

### Runtime AttributeError

- Cluster frequency: `8/297` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `4/150` (`2.7%`)
  - `ns_25t2_py21_2/16`: `4/147` (`2.7%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `1af8b8766aa7419eb29e044f215eceff`, summary `Runtime Error`, score `0`, vector `000`

```python
s1 = "dam"
s2 = "am"
s1_reverse = s1.reversed("dam")
reverse_combinded = s1_reverse.add("am")
is_reverse_combined_palindrome = reverse_combinded.reversed("madam")
return is_reverse_combined_palindrome
```

- Variant `ns_25t2_py21_2/16`, Student ID `f0f0d05336f042cd82b580c8b121c274`, summary `Runtime Error`, score `0`, vector `000`

```python
...
val = reversed(s1)
final = val.join(s2)
found = False
temp = reversed(final)
if temp != final:
    found = True
if found:
    return "False"
return "True"
```

### No return / implicit `None`

- Cluster frequency: `7/297` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `4/150` (`2.7%`)
  - `ns_25t2_py21_2/16`: `3/147` (`2.0%`)
- Dominant private-case vectors: `000` x6, `010` x1
- Score distribution (top): `0.0` x6, `33.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `7e420061c0da4494b3318f954707e4de`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_reverse_combined_palindrome(s1: str, s2: str) -> str:
    '''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
        s1 (string): The first string
        s2 (string): The second string

    Returns:
# ...
```

- Variant `ns_25t2_py21_2/16`, Student ID `62700b5d6ef0416a88787cab610f3910`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_reverse_combined_palindrome(s1: str, s2: str) -> str:
    '''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
        s1 (string): The first string
        s2 (string): The second string

    Returns:
# ...
```

### Residual promoted: inverted palindrome condition (`!=`)

- Cluster frequency: `6/297` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `2/150` (`1.3%`)
  - `ns_25t2_py21_2/16`: `4/147` (`2.7%`)
- Dominant private-case vectors: `110` x4, `100` x2
- Score distribution (top): `67.0` x4, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `640d9ccc57274f54bbf68c008f7d73fd`, summary `Wrong Answer`, score `67`, vector `110`

```python
return s1 in s2 or s2 in s1
```

- Variant `ns_25t2_py21_2/16`, Student ID `1a146deb52ff45f98e5e874c4ce232c6`, summary `Wrong Answer`, score `67`, vector `110`

```python
if s1 in s2:
        return True
    elif s2 in s1:
        return True
return False
```

### Reverses first string but concatenates in wrong order (`s2 + reversed(s1)`)

- Cluster frequency: `5/297` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `2/150` (`1.3%`)
  - `ns_25t2_py21_2/16`: `3/147` (`2.0%`)
- Dominant private-case vectors: `010` x4, `000` x1
- Score distribution (top): `33.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `0f012427416f4f95bd3732dcaf8324f6`, summary `Wrong Answer`, score `33`, vector `010`

```python
reversed_s1= s1[::-1]
final_string = s2 + reversed_s1
if final_string== final_string[::-1]:
        return True
    else:
        return False
```

- Variant `ns_25t2_py21_2/16`, Student ID `8c5fdf4f2e3549d293c7df05f1ccc301`, summary `Wrong Answer`, score `33`, vector `010`

```python
...
string1=""
stringfinal=""
for i in range(0,len(s1)-1,-1):
        string1+=str(s1[i])
stringfinal=s2+string1
if (s2+string1==stringfinal[::-1]):
        return True
    else:
        return False
```

### Prints output but does not return required value

- Cluster frequency: `4/297` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `3/150` (`2.0%`)
  - `ns_25t2_py21_2/16`: `1/147` (`0.7%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: In function-type questions, printing is not enough; tests compare the returned value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `f0ef9ab5856e40409075f4dbea1c99a9`, summary `Wrong Answer`, score `0`, vector `000`

```python
s1 = str()
s2 = str()
reverse_s1 = s1[::-1]
combined = str(reverse_s1+s2)
reverse_combined = str(s2[::-1]+s1)
if( str(combined) == str(reverse_combined) ):
        print(True)
    else:
        print(False)
```

- Variant `ns_25t2_py21_2/16`, Student ID `7944f38c89bd46308bf7d29766edd804`, summary `Wrong Answer`, score `0`, vector `000`

```python
s1_new = list(s1)
s1_rev = s1_new[::-1]
s1_new_o = str(s1_rev) + s2
print(s1_new_o)
```

### Compares only partial slices instead of full reversed+combined palindrome

- Cluster frequency: `4/297` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `3/150` (`2.0%`)
  - `ns_25t2_py21_2/16`: `1/147` (`0.7%`)
- Dominant private-case vectors: `000` x3, `001` x1
- Score distribution (top): `0.0` x3, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `0d0ae1a1be98429391844f622138b33a`, summary `Wrong Answer`, score `33`, vector `001`

```python
...
fi=s1[0:2][::-1]
se=s2[-2:]
if fi==se:
        return False
    else:
        return True
```

- Variant `ns_25t2_py21_2/16`, Student ID `f07265aa46c1447e9898a20d45291be1`, summary `Wrong Answer`, score `0`, vector `000`

```python
revese_str1 = s1[::-1]
con_str1 = revese_str1[-2:]
if s2 == con_str1 or s2 == s1:
        return False
    else:
        return True
```

### Inverts palindrome condition (`!=` instead of `==`)

- Cluster frequency: `3/297` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `2/150` (`1.3%`)
  - `ns_25t2_py21_2/16`: `1/147` (`0.7%`)
- Dominant private-case vectors: `001` x2, `000` x1
- Score distribution (top): `33.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `e943f7adcdde4195a98d2b9c3ff3e25d`, summary `Wrong Answer`, score `33`, vector `001`

```python
s = ((s1 + s2).strip()).lower()
return s != s[::-1]
```

- Variant `ns_25t2_py21_2/16`, Student ID `f0501aa46e634cb9a92ea777b286b21e`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
new = s1[:-1] + s2
return len(new) % 2 == 0 and new != new[::-1]
```

### Always returns `True` (constant output)

- Cluster frequency: `3/297` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `3/150` (`2.0%`)
  - `ns_25t2_py21_2/16`: `0/147` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `d6f05fa21773408fabf47d71cc1ca353`, summary `Wrong Answer`, score `0`, vector `000`

```python
c1=list(s1)
a1=c1.reverse()
n1=str(a1)
f=n1+s2
n=len(f)
b=bool(True)
t=""
h=""
for i in range(math.floor(n/2)):
        t=t+f[i]
if n%2==0:
        for i in range(int(n/2),n):
            h=f[i]+h
    else:
        for i in range(int((n+1)/2),n):
            h=f[i]+h
for i in range(math.floor(n/2)):
        if h[i]!=t[i]:
# ...
```

### Returns string/text instead of boolean result

- Cluster frequency: `2/297` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `1/150` (`0.7%`)
  - `ns_25t2_py21_2/16`: `1/147` (`0.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `0a0dc21d68ce4452b90287c3d5821f07`, summary `Wrong Answer`, score `0`, vector `000`

```python
return f"{s1[1:] + s2[1:2]}"
```

- Variant `ns_25t2_py21_2/16`, Student ID `c677ab3638bb4ffc8aedd80396f80d8d`, summary `Wrong Answer`, score `0`, vector `000`

```python
reverse_s1 = s1[::-1]
combined_string = reverse_s1 + s2
if combined_string == combined_string [::-1]:
        return "True"
    else:
        return "False"
```

### Runtime IndexError

- Cluster frequency: `2/297` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `1/150` (`0.7%`)
  - `ns_25t2_py21_2/16`: `1/147` (`0.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `bee6eac0421a43c3bbad0423b13e6898`, summary `Runtime Error`, score `0`, vector `000`

```python
list1 = list(s1)
list2 = list(s2)
n1 = len(list1)
n2 = len(list2)
list3 = []
for i in range(n1):
    list1[i] = list1[n1 - i]
    list3.append(s[i])
list4 = list3.append(list2)
for i in range(n1 + n2):
    if list4[i] == list4[(n1 + n2) - i]:
        return True
    else:
        False
```

- Variant `ns_25t2_py21_2/16`, Student ID `e3fb3b6c5f1744ecb50137390b4f05f9`, summary `Runtime Error`, score `0`, vector `000`

```python
...
new_s1 = s1[-1::]
s = new_s1 + s2
n = len(s)
for i in range(n):
    if s[i] == s[n - i]:
        print(True)
    else:
        print(False)
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/297` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `2/150` (`1.3%`)
  - `ns_25t2_py21_2/16`: `0/147` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `89bd731cfbff410aa35196f9d15a683c`, summary `Runtime Error`, score `0`, vector `000`

```python
r1 = s1.reverse()
r2 = r1 + s2
r3 = r2.reverse()
if r2 == r3:
    return True
```

### Time Limit Exceeded

- Cluster frequency: `1/297` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/15`: `1/150` (`0.7%`)
  - `ns_25t2_py21_2/16`: `0/147` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/15`, Student ID `2d1bef7d8cfb4c36b15e45b8846955c7`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
temp=""
for i in s1:
        temp=temp+i
temp=temp+s2
count=0
j=0
k=len(temp)-1
while j!=(len(temp)/2)-1 and k!=(len(temp)/2)-1:
        count=count+1
        j=j+1
        k=k-1
if count==len(temp)-1:
        return True
    else:
        return False
```
