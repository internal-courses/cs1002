# Error Patterns: Cluster C005 (`Counts unique even and odd numbers`)

## Cluster Summary

- Cluster ID: `C005`
- Cluster title: `Counts unique even and odd numbers`
- Cluster file (this file): `analysis/ERRORS-cluster-c005-counts-unique-even-and-odd-numbers-44480259.md`
- Variants in cluster: `3`
- Total final submitters across variants: `556`
- Total non-full final submissions across variants: `174`
- Canonical variant (by submissions): `ns_25t2_py12_1/9`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py12_1/9` (canonical) | 556 | 174 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py12_1/9.json`
- Other variants in cluster:
  - `problems/ns_25t1_py11_1/6.json`
  - `problems/ns_25t1_py_15_exe/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `556`
- Full pass: `382`
- Non-full final submissions: `174`
- Parseable non-full (logic/runtime focus): `125`
- Non-parseable non-full: `49`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t1_py11_1/6` | 0 | 0 | 0 | 0 | 0 |
| `ns_25t1_py_15_exe/9` | 0 | 0 | 0 | 0 | 0 |
| `ns_25t2_py12_1/9` | 556 | 382 | 174 | 125 | 49 |

## Private Case Structure

- Private case 1: large repeated-range list (must count unique even/odd values, not occurrences)
- Private case 2: mixed negatives/offset values (checks parity of values, uniqueness, and correct dict counts)

Private-case vectors in this report are 2-character pass/fail strings over the private case groups (e.g., `11` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t1_py11_1/6` | `ns_25t1_py_15_exe/9` | `ns_25t2_py12_1/9` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 49 | 28.2% | 0 | 0 | 49 |
| Incorrect unique even/odd counting logic (placeholder, occurrence-counting, or wrong parity test) | 42 | 24.1% | 0 | 0 | 42 |
| Runtime TypeError from invalid list/dict operations while counting unique even/odd values | 24 | 13.8% | 0 | 0 | 24 |
| Runtime NameError from undefined counters/keys in the even/odd count dictionary logic | 19 | 10.9% | 0 | 0 | 19 |
| No return / implicit `None` | 16 | 9.2% | 0 | 0 | 16 |
| Runtime error (parseable final submission) | 4 | 2.3% | 0 | 0 | 4 |
| Runtime RecursionError from accidental recursive call in `count_unique_even_odd` | 3 | 1.7% | 0 | 0 | 3 |
| Runtime KeyError from incrementing dict keys without initializing `'even'`/`'odd'` | 3 | 1.7% | 0 | 0 | 3 |
| Runtime IndexError from using list values as indices (e.g., `l[i]` inside `for i in l`) | 2 | 1.1% | 0 | 0 | 2 |
| Uses floor-division (`// 2`) as a parity test instead of modulo (`% 2`) | 2 | 1.1% | 0 | 0 | 2 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests) | 2 | 1.1% | 0 | 0 | 2 |
| Counts all even/odd occurrences without deduplicating the input values first | 2 | 1.1% | 0 | 0 | 2 |
| Adds odd numbers to the even set in both branches, leaving the odd set empty | 1 | 0.6% | 0 | 0 | 1 |
| Runtime AttributeError | 1 | 0.6% | 0 | 0 | 1 |
| Runtime ValueError | 1 | 0.6% | 0 | 0 | 1 |
| Deduplicates values but then counts parity of indices (`range(len(set(l)))`) instead of parity of values | 1 | 0.6% | 0 | 0 | 1 |
| Deduplicates values with `set(...)` but still counts index parity, not value parity | 1 | 0.6% | 0 | 0 | 1 |
| Returns a non-dictionary value instead of `{'even': ..., 'odd': ...}` | 1 | 0.6% | 0 | 0 | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/174` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `49/174` (`28.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `49/174` (`28.2%`)
- Dominant private-case vectors: `00` x49
- Score distribution (top): `0.0` x49
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `03ec88c245ec4928b9445d915963acaf`, summary `Runtime Error`, score `0`, vector `00`

```python
def count_unique_even_odd(l: list)-> dict:
    '''Returns a dict with the count of unique even and odd numbers in the list.

    Eg.
    >>>l = [1, 2, 2, 3, 4, 5, 5, 6]
    >>>count_unique_even_odd(l)
    {"even": 3, "odd": 3}

    Args:
        l(list)  : a list of integers.

    Returns:
        dict: a dict with the count of unique even and odd numbers in the list.
    '''
    count_even = 0
    count_odd = 0

    for i in l:
# ...
```

### Incorrect unique even/odd counting logic (placeholder, occurrence-counting, or wrong parity test)

- Cluster frequency: `42/174` (`24.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `42/174` (`24.1%`)
- Dominant private-case vectors: `00` x42
- Score distribution (top): `0.0` x42
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `371a71c461334a50a0c9263314abc5c8`, summary `Wrong Answer`, score `0`, vector `00`

```python
    leve=[]
    lodd=[]
    count1=0
    count2=0
    for i in l:
        if (i%2==0):
            leve.append(i)
        if (i%2!=0):
            lodd.append(i)
    for i in leve:
        for j in leve:
            if (i!=j):
                count1=+1
    for i in lodd:
        for j in lodd:
            if(i!=j):
                count2=+1
    return {"even":count1,"odd":count2}
# ...
```

### Runtime TypeError from invalid list/dict operations while counting unique even/odd values

- Cluster frequency: `24/174` (`13.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `24/174` (`13.8%`)
- Dominant private-case vectors: `00` x24
- Score distribution (top): `0.0` x24
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `b4bdbb79ede24c5096334c6f790f7a71`, summary `Runtime Error`, score `0`, vector `00`

```python
    for num in l:
        even = {}
        counteven=0

        if num%2==0:
            even.append(num)
            counteven+=1

        odd = {}
        countodd=0

        if num%2!=0 in list:
            odd.append(num)
            countodd+=1
    count_unique={"even":counteven, "odd":countodd}
    return(count_unique)
    '''Returns a dict with the count of unique even and odd numbers in the list.

# ...
```

### Runtime NameError from undefined counters/keys in the even/odd count dictionary logic

- Cluster frequency: `19/174` (`10.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `19/174` (`10.9%`)
- Dominant private-case vectors: `00` x19
- Score distribution (top): `0.0` x19
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `9803b4c8753f46d78d99398b98a0ab5a`, summary `Runtime Error`, score `0`, vector `00`

```python
    ...
    list = l.copy()
    even_count = 0
    odd_count = 0
    if -2 in list:
        even_count = even_count + 1
    if -4 in list:
        even_count = even_count + 1
    if -6 in list:
        even_count = even_count + 1
    if -8 in list:
        even_count = even_count + 1
    if 0 in list:
        even_count = even_count + 1
    if 2 in list:
        even_count = even_count + 1
    if 4 in list:
        even_count = even_count + 1
# ...
```

### No return / implicit `None`

- Cluster frequency: `16/174` (`9.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `16/174` (`9.2%`)
- Dominant private-case vectors: `00` x16
- Score distribution (top): `0.0` x16
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `7cc667daa0cd485e9ee5cfb7e9694593`, summary `Wrong Answer`, score `0`, vector `00`

```python
from typing import List, Any
def count_unique_even_odd(l: list)-> dict:
    '''Returns a dict with the count of unique even and odd numbers in the list.

    Eg.
    >>>l = [1, 2, 2, 3, 4, 5, 5, 6]
    >>>count_unique_even_odd(l)
    {"even": 3, "odd": 3}

    Args:
        l(list)  : a list of integers.

    Returns:
        dict: a dict with the count of unique even and odd numbers in the list.
    '''
```

### Runtime error (parseable final submission)

- Cluster frequency: `4/174` (`2.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `4/174` (`2.3%`)
- Dominant private-case vectors: `00` x4
- Score distribution (top): `0.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `2c31a4020a7d471e816c2e864802b4a4`, summary `Runtime Error`, score `0`, vector `00`

```python
def count_unique_even_odd(l: list)-> dict:
    '''Returns a dict with the count of unique even and odd numbers in the list.

    Eg.
    >>>l = [1, 2, 2, 3, 4, 5, 5, 6]
    >>>count_unique_even_odd(l)
    {"even": 3, "odd": 3}

    Args:
        l(list)  : a list of integers.

    Returns:
        dict: a dict with the count of unique even and odd numbers in the list.
    '''


even_numbers = set()
odd_numbers = set()
# ...
```

### Runtime RecursionError from accidental recursive call in `count_unique_even_odd`

- Cluster frequency: `3/174` (`1.7%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `3/174` (`1.7%`)
- Dominant private-case vectors: `00` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `941f9c347bff4e8cb0c230dbd5aaa0b7`, summary `Runtime Error`, score `0`, vector `00`

```python
    l = [1, 2, 2, 3, 4, 5, 5, 6]
    is_equal(
       count_unique_even_odd([]),
       {"even": 3, "odd": 4}
       )
    return(count_unique_even_odd(l))
```

### Runtime KeyError from incrementing dict keys without initializing `'even'`/`'odd'`

- Cluster frequency: `3/174` (`1.7%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `3/174` (`1.7%`)
- Dominant private-case vectors: `00` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `9495254eb5264f0bac6ddbc20ebb6c8c`, summary `Runtime Error`, score `0`, vector `00`

```python
    dict = {'even': 0 , 'odd': 0}
    for x in l:
        if x%2 == 0:
            #even += {1}
            dict[0] += 1
        elif x%2 == 1:
            #odd += {1}
            dict[1] += 1
    return dict
```

### Runtime IndexError from using list values as indices (e.g., `l[i]` inside `for i in l`)

- Cluster frequency: `2/174` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `2/174` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `a4193fbd439f43b2a470cc3be4d21851`, summary `Runtime Error`, score `0`, vector `00`

```python
    even=[]
    odd=[]
    for i in range(0, len(l)):
        if l[i]%2==0:
            even.append(l[i])
        else:
            odd.append(l[i])
    for a in range(0, len(even)):
        for m in range(0, len(even)-1):
            if even[a]==even[a+m]:
                even.remove(even[a])
            else:
                pass
    for b in range(0, len(odd)):
        for n in range(0, len(odd)-1):
            if odd[b]==odd[b+n]:
                odd.remove(odd[b])
            else:
# ...
```

### Uses floor-division (`// 2`) as a parity test instead of modulo (`% 2`)

- Cluster frequency: `2/174` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `2/174` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `25fb54d10fc748dcb13e21a6387efc61`, summary `Wrong Answer`, score `0`, vector `00`

```python
    a=[]
    b=[]
    i=0
    e=0
    o=0
    for i in l:
        if i//2==0:
            a=a=[i]
            if i in a:
                e=e+0
            else:
                e=e+1
            i=i+1
        else:
            if i//2==1:
                b= b+[i]
                if i in b:
                    o=o+0
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `2/174` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `2/174` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `2b145ef9c4ab4ed584e7340bb2f9595d`, summary `Runtime Error`, score `0`, vector `00`

```python
    l= []
    l = input()
    num = l.split(",")
    even=0
    odd=0
    for i in num:
        if num % 2 == 0:
            even +=1
            if num % 2 == 1:
                odd += 1
```

### Counts all even/odd occurrences without deduplicating the input values first

- Cluster frequency: `2/174` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `2/174` (`1.1%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `22c611a0925b4ad198fbc3d668651f2d`, summary `Wrong Answer`, score `0`, vector `00`

```python
    l1=[]
    for i in l:
        for j in l:
            if(i == j):
                pass
            else:
                l1.append(i)
    return l1
    x=0
    y=0
    for i in l1:
        if (i%2 == 0):
            x=x+1
        else:
            y+=1
    dict={}
    dict[even:]=x
    dict[odd:]=y
# ...
```

### Adds odd numbers to the even set in both branches, leaving the odd set empty

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `0ea006a053f44339ab969e531fc584fb`, summary `Wrong Answer`, score `0`, vector `00`

```python
    unique_even = set()
    unique_odd = set()
    for number in l :
        if number % 2 == 0:
            unique_even.add(number)
        else:
            unique_even.add(number)
    return{"even": len(unique_even),"odd":len(unique_odd)}
```

### Runtime AttributeError

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `5ae92d5eb96a4382be5e0a9242bb9276`, summary `Runtime Error`, score `0`, vector `00`

```python
    e = []
    o = []
    n = len(l)
    c1 = []
    c2 = []
    d = dict()
    for i in range(0,n):
        for j in range (0,n):
            if l[i] % 2 == 0 and not l[i] == l[j] :
               l[i].appeand(c1)
            elif l[i] % 3 == 0 and not l[i] == l[j]:
                l[i].appeand(c2)
    d['even'] = len(c1)
    d['odd'] = len(c2)
    return(d)
```

### Runtime ValueError

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `5fac3f47b04c4e0c9619bc074b3c53f0`, summary `Runtime Error`, score `0`, vector `00`

```python
    count = {'even': 0, 'odd' : 0}
    for elem in l:
        for key, value in count:
            if elem % 2 == 0:
                key[even] += 1
            else:
                if elem % 2 != 0:
                    key[odd] +=1
    return count
```

### Deduplicates values but then counts parity of indices (`range(len(set(l)))`) instead of parity of values

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `01` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `6a0d70b1adb8417a851c5d3246526356`, summary `Wrong Answer`, score `50`, vector `01`

```python
    d={}
    s=set(l)
    evenc=0
    oddc=0
    for i in range(len(s)):
        if (i%2==0):
            evenc+=1
        else:
            oddc+=1
    return{"even":evenc,"odd":oddc}
```

### Deduplicates values with `set(...)` but still counts index parity, not value parity

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `01` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `8bc7d985cd314cee9c8c8d4a2df21a90`, summary `Wrong Answer`, score `50`, vector `01`

```python
    l=list(set(l1))
    ec=0
    oc=0
    dict={}
    for i in range(len(l)):
        if i%2==0:
            ec=ec+1
        else:
            oc=oc+1
    dict['even']=ec
    dict['odd']=oc
    return dict
    '''Returns a dict with the count of unique even and odd numbers in the list.

    Eg.
    >>>l = [1, 2, 2, 3, 4, 5, 5, 6]
    >>>count_unique_even_odd(l)
    {"even": 3, "odd": 3}
# ...
```

### Returns a non-dictionary value instead of `{'even': ..., 'odd': ...}`

- Cluster frequency: `1/174` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/9`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/9`: `1/174` (`0.6%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/9`, Student ID `fade59fa57ee40ad92e6204000f1b835`, summary `Wrong Answer`, score `0`, vector `00`

```python
    nums = set(l)
    D = []
    for num in nums:
        if num%2 == 0:
            D.append(num)
        else:
            D.append(num)
    return D
```
