# Error Patterns: Cluster C093 (`Reverse Vowel Order in a String`)

## Cluster Summary

- Cluster ID: `C093`
- Cluster title: `Reverse Vowel Order in a String`
- Cluster file (this file): `analysis/ERRORS-cluster-c093-reverse-vowel-order-in-a-string-71902350.md`
- Variants in cluster: `1`
- Total final submitters across variants: `616`
- Total non-full final submissions across variants: `489`
- Canonical variant (by submissions): `ns_25t2_py14_1/10`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py14_1/10` (canonical) | 616 | 489 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py14_1/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `616`
- Full pass: `127`
- Non-full final submissions: `489`
- Parseable non-full (logic/runtime focus): `378`
- Non-parseable non-full: `111`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py14_1/10` | 616 | 127 | 489 | 378 | 111 |

## Private Case Structure

- Private case 1: multi-line input with mixed vowels/consonants (reverse vowels globally across all lines)
- Private case 2: uppercase vowels included (catches incomplete vowel sets like missing `U`)
- Private case 3: formatting-sensitive cases (line preservation / newline handling with global vowel reversal)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py14_1/10` |
| --- | ---: | ---: | ---: |
| Incorrect program-level vowel-reversal logic (I/O, global reversal, or formatting semantics are wrong) | 160 | 32.7% | 160 |
| Syntax / non-parseable final submission | 111 | 22.7% | 111 |
| Hard-codes sample output strings (e.g., `HollE`) instead of reversing vowels for arbitrary input | 73 | 14.9% | 73 |
| Processes only one line (or prints line-by-line incorrectly) instead of reversing vowels globally across all input lines | 37 | 7.6% | 37 |
| Runtime TypeError | 20 | 4.1% | 20 |
| Runtime error (parseable final submission) | 19 | 3.9% | 19 |
| Runtime NameError from undefined line/text accumulator variables in multi-line vowel-reversal code | 17 | 3.5% | 17 |
| Runtime AttributeError | 12 | 2.5% | 12 |
| Runtime NameError | 11 | 2.2% | 11 |
| Runtime IndexError from pointer/pop indexing bugs while reversing vowels | 9 | 1.8% | 9 |
| Builds transformed characters but outputs with incorrect formatting (missing join/newline preservation) | 8 | 1.6% | 8 |
| Runtime IndexError | 4 | 0.8% | 4 |
| Runtime ValueError from parsing string input as integers in a text-processing question | 3 | 0.6% | 3 |
| Runtime TypeError from trying to mutate Python strings in-place while swapping vowels | 2 | 0.4% | 2 |
| Partially correct vowel-reversal program with global-vowel or output-formatting bug | 1 | 0.2% | 1 |
| Incomplete vowel set (missing one vowel/uppercase vowel), causing hidden-case misses | 1 | 0.2% | 1 |
| Treats the entire multi-line input as a single tokenized line (ignores line count / line boundaries) | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/489` (`0.0%`)

### Incorrect program-level vowel-reversal logic (I/O, global reversal, or formatting semantics are wrong)

- Cluster frequency: `160/489` (`32.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `160/489` (`32.7%`)
- Dominant private-case vectors: `000` x160
- Score distribution (top): `0.0` x160
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `36e36f2ced97451cb7325e147d9383c6`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here
n=int(input())
if n==1 :
    s=input()
    b=len(s)
    c=list(range(b))
    l=list()
    p=list()
    for i in range(len(s)) :
        if s[i].lower() in'aeiou' :
            l.append(i)
        else :
            p.append(i)
    for i in range(len(l)-1) :
        c[l[i]]=s[l[i+1]]
        c[l[i+1]]=s[l[i]]
    for i in p :
        c[i]=s[i]
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `111/489` (`22.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `111/489` (`22.7%`)
- Dominant private-case vectors: `000` x111
- Score distribution (top): `0.0` x111
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `a1d18d484fff4b63bad225b89ead1747`, summary `Runtime Error`, score `0`, vector `000`

```python
https://exams.study.iitm.ac.in/assets/img/logos/iitm-logo@3x.png

# Write your solution here
return (HollE)
https://storage.googleapis.com/seek-ode-exam-student-assets-prod/assets/profile_id/a1d18d484fff4b63bad225b89ead1747?Expires=1753008365&GoogleAccessId=seek-ode-exam-prod%40appspot.gserviceaccount.com&Signature=ErbIhFVoIVsjpDcWM2qHihCVIs3IdCFwCY3Gd8dsfdC8xYObkCDfMfXWHygqxgpndYeLzh%2FctE%2BsExt5uwe74Vl2B9YkK0IiDhLy%2B5miOQDtxPPb3jvY3iavlSLxvYR%2Fw%2FccpfBPX5ImG2A0LCaj4zWvlumU98hwNYjAPcvBrE6m6xBe4GAkvl1Sn72bvRVhpZKQm7fUtow65Ct8ATNzBYDNSKCKRKjtptAean68aG0R8Mw98UCwkmUQniUXnOAmeeO%2B9UzCvK6DPHD%2BRFWB1NlTbszMcjRT04SlT7MFx%2FAb72LAzB9qpWeBvGug9HzFv8in8Ad46QzDxFtYc51HJg%3D%3DTab Inactive
```

### Hard-codes sample output strings (e.g., `HollE`) instead of reversing vowels for arbitrary input

- Cluster frequency: `73/489` (`14.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `73/489` (`14.9%`)
- Dominant private-case vectors: `000` x73
- Score distribution (top): `0.0` x73
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `1ef4ddb407dd451fbd22fd3342e05dad`, summary `Wrong Answer`, score `0`, vector `000`

```python
'''def reverse_vowel():
        try:
            n=int(input())
            full_text="\n".join(input() for _ in range(n))
        except(ValueError,EOFError):
            full_text=""
        if not full_text:
            print()
            return


        vowels='aeiouAEIOU'
        vowels_in_text=[char for char in full_text if char in vowels]

        text_list = list(full_text)

        for i , char in enumerate(text_list):
            if char in vowels:
# ...
```

### Processes only one line (or prints line-by-line incorrectly) instead of reversing vowels globally across all input lines

- Cluster frequency: `37/489` (`7.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `37/489` (`7.6%`)
- Dominant private-case vectors: `000` x37
- Score distribution (top): `0.0` x37
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `2c97d73a1116457aaeaff01315847705`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

v = "aeiou"
res = []
d = {}
d_list_k1 = []
d_list_v1 = []

n = int(input())

for _ in range(n):
    line = input()
    #print (line)
    for i in range(len(line)):
        if line[i].lower() in v:
            d[line[i]] = i
        res.append(line[i])

# ...
```

### Runtime TypeError

- Cluster frequency: `20/489` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `20/489` (`4.1%`)
- Dominant private-case vectors: `000` x20
- Score distribution (top): `0.0` x20
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `8441c3b982914b779cf15f66e9857474`, summary `Runtime Error`, score `0`, vector `000`

```python
g=input()


if(g=="Hello"):
    print("HollE")
elif (g=='''Hello, World!
UFO? Yes.'''):
    print('''HellO, wUrld!
    oFo? Yes.''')
else:

    for i in range():
        for j in range():
            if(i=='a' or i=='e' or i=='i'or i=='o' or i=='u' or i=='A' or i== 'E' or i=='I' or i=='O' or i=='U'):
                if(j=='a' or j=='e' or j=='i'or j=='o' or j=='u' or j=='A' or j== 'E' or j=='I'or j=='O' or j=='U'):
                    i,j=j,i
                    print(g)
                else:
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `19/489` (`3.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `19/489` (`3.9%`)
- Dominant private-case vectors: `000` x19
- Score distribution (top): `0.0` x19
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `3f0df6b88b404b229721ff5ffd7a15c1`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here


n = int(input())
for _ in range(n):
    len = input().strip()
    new_line = " "
    for char in line:
        lower_char = char.lower()
        upper_char = char.upper()
        vowels = ['a', 'e', 'i', 'o', 'u','A', 'E', 'I', 'O', 'U']
        new_char= char.reverse()
for char in word:
    indices = sorted([i1, i2], reverse = True)
    for indices in char:
        if indices < len(l):
            s == s[::-1]
    result.append(l)
# ...
```

### Runtime NameError from undefined line/text accumulator variables in multi-line vowel-reversal code

- Cluster frequency: `17/489` (`3.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `17/489` (`3.5%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `76d78eedef7d4c6ebd8989c4e981fdc9`, summary `Runtime Error`, score `0`, vector `000`

```python
    num_line = int(input("Enter the number of lines: "))
    lines = []
    for _ in range (num_line):

        line = input()
        lines.append(line)
    full_text = '\n'
    vowels = 'aeiouAEIOU'
    vowel_char = []
    for char in full_text:
        if char in vowels:
            vowel_char.append(char)
    vowel_char.reverse()
    result = ""
    vowel_index = 0
    for char in full_text:
        if char in vowels:
            result = result + vowel_char[vowel_index]
# ...
```

### Runtime AttributeError

- Cluster frequency: `12/489` (`2.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `12/489` (`2.5%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `ff4c04fc95064e799de086de619dbedf`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

vowel = {"a","e","i","o","u"}
vowstring= ""
consstring =""
vowindex =[]
consindex = []
newstring = ""
n = int(input())
for i in range (n):
    string = input()
    for j in range (len(string)):
        if string[j].lower() in vowel:
            vowstring+=string[j]
            vowindex.append(j)
        else:
            consstring+=string[j]
            consindex.append(j)
# ...
```

### Runtime NameError

- Cluster frequency: `11/489` (`2.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `11/489` (`2.2%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `eb0a781d46a6497d8ed080e0215cf6a7`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
n=int(input())
vowel='aeiouAEIOU'
word=input()
empty=""
for vowel in word:
    empty=append.vowel
reverse=list(empty[::-1])
print(reverse.word)
```

### Runtime IndexError from pointer/pop indexing bugs while reversing vowels

- Cluster frequency: `9/489` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `9/489` (`1.8%`)
- Dominant private-case vectors: `000` x8, `101` x1
- Score distribution (top): `0.0` x8, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `dcb32747e11647ac802a563e7287f8ee`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
inp1 = int(input())
inparr = []
outpar = []
for i in range(inp1):
    inp = input()
    outp = list(inp)
    inparr.append(inp)
    outpar.append(outp)
vowel = 'aeiouAEIOU'

arr = []
ind = []
for inp in inparr:
    for i in range(0,len(inp)):
        if inp[i] in vowel:
            arr.append(str(inp[i]))
            ind.append(i)
# ...
```

### Builds transformed characters but outputs with incorrect formatting (missing join/newline preservation)

- Cluster frequency: `8/489` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `8/489` (`1.6%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `94b70cb1ee8147d8befa150fceff4941`, summary `Wrong Answer`, score `0`, vector `000`

```python
n=int(input())
lines=[]
for i in range(n):
    line=input()
    lines.append(line)

# e o o U O e
# e O U o o e

vow='AEIOUaeiou'
vow_list=[]

for line in lines: #line is str
    for i in line: #i is individual char (str)
        if i in vow:
            vow_list.append(i)

vow_list=vow_list[::-1]
# ...
```

### Runtime IndexError

- Cluster frequency: `4/489` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `4/489` (`0.8%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `a5792d71fa85465bb39ba203b454570f`, summary `Runtime Error`, score `0`, vector `000`

```python
    vowels_in_text=[]
    vowel_indices=[]
    vowels_set={'a','e','i','o','u', 'A', 'E', 'I', 'O', 'U'}
    for i, char in enumerate(text):
        if char in vowels_set:
            vowels_in_text.append(char)
            vowel_indicesa.append(i)
        vowels_in_text.reverse()
        result=list(text)
        vowel_index=0
        for char in text:
            if char.lower() in {'a','e','i','o','u'}:
                result.append(vowels_in_text[vowel_index])
                vowel_index+=1
            else:
                result.append(char)
        return ''.join(result)
```

### Runtime ValueError from parsing string input as integers in a text-processing question

- Cluster frequency: `3/489` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `3/489` (`0.6%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `c4e71268e68540118e935c85fbe585eb`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
n=int(input())
vowels='aeiouAEIOU'
ans=''
val=''
if n==1:
    words=str(input())
    for char in words:
        if char in vowels:
            ans+=char
    a=ans[0]
    b=ans[1]
    a,b=b,a
    ans[0]
    for char in words:
        i=0
        if char in vowels:
            val+=ans[i]
# ...
```

### Runtime TypeError from trying to mutate Python strings in-place while swapping vowels

- Cluster frequency: `2/489` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `2/489` (`0.4%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `13cfc2f2c6f641538733aa5cc998f423`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

'''
y=input()
x=input()
z=(a,e,i,o,u)

for i in (x):
    if x[i] == "a":
        x.uppercase(a)
    elif x[i]=="e":
        x.uppercase(e)
    elif x[i]=="i":
        x.uppercase(i)
    elif x[i]=="o":
        x.uppercase(o)
    elif x[i]=="u":
        x.uppercase(u)
# ...
```

### Partially correct vowel-reversal program with global-vowel or output-formatting bug

- Cluster frequency: `1/489` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `1/489` (`0.2%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `22b6d7a25f2242188c3d45329749660d`, summary `Wrong Answer`, score `33`, vector `100`

```python
# Write your solution here


n=int(input())
str=''
for i in range(n):
    s1=input()
    str=str+'\n'+s1
s='aeiouAEIOU'
l=list(str)
k=len(l)-1
for i in range(len(l)//2):
    for j in range(k,len(l)//2-1,-1):
        if l[i] in s and l[j] in s:
            l[i],l[j]=l[j],l[i]
            k=j-1
            break
print(''.join(l))
```

### Incomplete vowel set (missing one vowel/uppercase vowel), causing hidden-case misses

- Cluster frequency: `1/489` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `1/489` (`0.2%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `5b6b85ea54f94576b7edfbedc5bffe38`, summary `Wrong Answer`, score `33`, vector `100`

```python
# Write your solution here
vowels="aeiouAEIO"
n=int (input())
lines=[input() for _ in range(n)]
all_vowels=[c for line in lines for c in line if c in vowels][::-1]
i=0
for line in lines:
    res=''
    for c in line:
      if c in vowels:
        res+=all_vowels[i]
        i+=1
      else:
        res+=c

    print(res)
```

### Treats the entire multi-line input as a single tokenized line (ignores line count / line boundaries)

- Cluster frequency: `1/489` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/10`: `1/489` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/10`, Student ID `6aa6aa4af88542ffa0bf12b22e48564d`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here


depth = int(input())

inlist =[]

for i in range(depth):
    n = input().split()
    inlist.append(n)

vowels = ['a','e','i','o','u','A','E','I','O','U']
vowelsreplace = []

# print(inlist)

modlist = []

# ...
```
