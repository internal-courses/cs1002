# Error Patterns: Cluster C104 (`Mirror Merge - Advanced`)

## Cluster Summary

- Cluster ID: `C104`
- Cluster title: `Mirror Merge - Advanced`
- Cluster file (this file): `analysis/ERRORS-cluster-c104-mirror-merge-advanced-044261c4.md`
- Variants in cluster: `1`
- Total final submitters across variants: `400`
- Total non-full final submissions across variants: `122`
- Canonical variant (by submissions): `ns_25t3_py22/9`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py22/9` (canonical) | 400 | 122 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py22/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `400`
- Full pass: `278`
- Non-full final submissions: `122`
- Parseable non-full (logic/runtime focus): `97`
- Non-parseable non-full: `25`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py22/9` | 400 | 278 | 122 | 97 | 25 |

## Private Case Structure

- Private case 1: length-2 case with mixed parity; catches mirror pairing and sign-direction mistakes
- Private case 2: all-ones case (all same parity) should produce pure additions
- Private case 3: multi-assert suite covering same-parity add, mixed-parity subtract (`a-b_rev`), and length-1 edge case

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py22/9` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 25 | 20.5% | 25 |
| Mirror-indexing bug (`b[-i]`, fixed positions, or length-specific indexing) causes out-of-range access | 19 | 15.6% | 19 |
| Runtime TypeError from treating lists as scalars/indices while building the mirrored result | 12 | 9.8% | 12 |
| Incorrect mirror pairing / parity-rule application (broad wrong-answer failure) | 11 | 9.0% | 11 |
| No return / implicit `None` | 10 | 8.2% | 10 |
| Uses an `or` parity condition instead of checking same parity, so mixed-parity cases are added incorrectly | 10 | 8.2% | 10 |
| Runtime NameError from undefined temporaries (`lst`, `l`, `s`, etc.) in mirror-merge logic | 5 | 4.1% | 5 |
| Runtime error (parseable final submission) | 3 | 2.5% | 3 |
| Uses `b[-i]` instead of `b[-i-1]` for mirror indexing (`i=0` incorrectly selects `b[0]`) | 3 | 2.5% | 3 |
| Uses nested loops over both lists (cross-product), producing too many pairings instead of one mirror pair per index | 2 | 1.6% | 2 |
| Near-correct mirror pairing, but mixed-parity subtraction sign/parity condition is wrong on hidden cases | 2 | 1.6% | 2 |
| Returns a constant list (`[]` or fixed values) instead of computing the mirror merge from `a` and `b` | 2 | 1.6% | 2 |
| Mirror-index/pairing bug (wrong `b` index formula or partial pairing) causes one private group to fail | 2 | 1.6% | 2 |
| Applies extra sign-flip/negation logic, producing the wrong sign for mixed-parity results | 2 | 1.6% | 2 |
| Hard-codes public sample outputs / fixed lists instead of applying the mirror-merge rule generically | 2 | 1.6% | 2 |
| Splits the lists into halves and combines them, but the task requires elementwise mirror pairing across the full lists | 1 | 0.8% | 1 |
| Returns list concatenation (`a + b`) instead of elementwise mirror merge | 1 | 0.8% | 1 |
| Uses XOR-based parity logic incorrectly, so same-parity vs mixed-parity add/subtract rules are inverted | 1 | 0.8% | 1 |
| Destructive list-mutation pairing approach (`remove`/pop style) mishandles one hidden mirror case | 1 | 0.8% | 1 |
| Uses bitwise `&` in parity checks (operator/precedence bug) instead of logical `and` | 1 | 0.8% | 1 |
| Uses `.index(...)` to match mirrored elements, which breaks on duplicate values (first-occurrence index bug) | 1 | 0.8% | 1 |
| Copies evaluator tests (`is_equal(mirror_merge(...))`) into the function and triggers recursive/self-test failures | 1 | 0.8% | 1 |
| Interleaves raw elements from `a` and reversed `b` instead of computing one merged value per mirror pair | 1 | 0.8% | 1 |
| Runtime AttributeError | 1 | 0.8% | 1 |
| Length-specific manual implementation (fixed indices for length-3) instead of a loop-based general solution | 1 | 0.8% | 1 |
| Converts the input lists to strings / tuple output instead of computing numeric mirror-merge results | 1 | 0.8% | 1 |
| Subtracts in the wrong direction for mixed parity (`b_rev - a` instead of `a - b_rev`) | 1 | 0.8% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/122` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `25/122` (`20.5%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `25/122` (`20.5%`)
- Dominant private-case vectors: `000` x25
- Score distribution (top): `0.0` x25
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `b8b372db9e5841eb8467123a477149b4`, summary `Runtime Error`, score `0`, vector `000`

```python
def mirror_merge(a: list, b: list) -> list:
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.

    Args:
        a (list): First list of numbers.
        b (list): Second list of numbers (same length as a).

    Returns:
        list: List of computed values.
    '''

    if len(a) == len(b):
# ...
```

### Mirror-indexing bug (`b[-i]`, fixed positions, or length-specific indexing) causes out-of-range access

- Cluster frequency: `19/122` (`15.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `19/122` (`15.6%`)
- Dominant private-case vectors: `000` x15, `110` x2, `010` x2
- Score distribution (top): `0.0` x15, `67.0` x2, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `85ba8d132a734a90803e4acf4145d9de`, summary `Runtime Error`, score `67`, vector `110`

```python
    firstl1=a[0]
    secondl1=a[1]
    firstl2=b[-1]
    secondl2=b[-2]
    for word in a:
        if len(a)==len(b) and len(a)>2:
            thirdl1=a[2]
            thirdl2=b[-3]
            if (firstl1%2==0 and thirdl2%2==0) or (firstl1 % 2!=0and thirdl2%2!=0):
                first=firstl1+firstl2
            else:
                first=firstl1-firstl2
            if (secondl1%2==0 and secondl2%2==0) or (secondl1%2!=0 and secondl2%2!=0):
                second=secondl1+secondl2
            else:
                second=secondl1-secondl2
            if (thirdl1%2==0 and firstl2%2==0) or (thirdl1%2!=0 and firstl2%2!=0):
                last=thirdl1+thirdl2
# ...
```

### Runtime TypeError from treating lists as scalars/indices while building the mirrored result

- Cluster frequency: `12/122` (`9.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `12/122` (`9.8%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `0c796407724441a482dd8912fa4831c6`, summary `Runtime Error`, score `0`, vector `000`

```python
    m = []
    for i in range(a):
        m.append(i)
    for j in range(m):
        if i % 2 == 1 :
            m.insert(i , b[j])
    new_lst = []
    for i in lst:
        if i % 2 == 0 :
            if l[i] % 2 == 0 and i[i+1] == 0 or l[i] % 2 == 1 and l[i+1] % 2 == 1:
                new_lst.append(l[i]+l[i+1])
            else :
                new_lst.append(l[i]-l[i-1])
        else :
            continue
    return new_lst
```

### Incorrect mirror pairing / parity-rule application (broad wrong-answer failure)

- Cluster frequency: `11/122` (`9.0%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `11/122` (`9.0%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `754bdc34424d45fd88bd49fbb8cf5e34`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if len(list1)!=len(list2):
        raise ValueError("Both lists must be of equal length")
        result=[]
        n=len(list1)
        for i in range(n):
            num1=list1[i]
            num2=list2[n-i-1]
            if(num1 %2==0 and num2 %2!=0):
                result.append(num1+num2)
            else:
                result.append(num1-num2)
            return result
```

### No return / implicit `None`

- Cluster frequency: `10/122` (`8.2%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `10/122` (`8.2%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `a5469f2237884accbff62d6cab3decee`, summary `Wrong Answer`, score `0`, vector `000`

```python
def mirror_merge(a: list, b: list) -> list:
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.

    Args:
        a (list): First list of numbers.
        b (list): Second list of numbers (same length as a).

    Returns:
        list: List of computed values.
    '''
```

### Uses an `or` parity condition instead of checking same parity, so mixed-parity cases are added incorrectly

- Cluster frequency: `10/122` (`8.2%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `10/122` (`8.2%`)
- Dominant private-case vectors: `110` x7, `000` x2, `010` x1
- Score distribution (top): `67.0` x7, `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `e363e33c92a24120af049e54956c78ac`, summary `Wrong Answer`, score `67`, vector `110`

```python
    ...
    c=[]
    if len(a)<3:
        if (a[0]%2==0 and b[-1]%2==0) or (a[0]%2!=0 and b[-1]%2!=0):
            c=[a[0]+b[-1]]
        else:
            c=[a[0]-b[-1]]

        if (a[-1]%2==0 and b[0]%2==0) or (a[-1]%2!=0 and b[0]%2!=0):
            c.append(a[-1]+b[0])
        else:
            c.append(a[-1]-b[0])
        return c
    elif len(a)>2:
        if (a[0]%2==0 and b[-1]%2==0) or (a[0]%2!=0 and b[-1]%2!=0):
            c=[a[0]+b[-1]]
        else:
            c=[a[0]-b[-1]]
# ...
```

### Runtime NameError from undefined temporaries (`lst`, `l`, `s`, etc.) in mirror-merge logic

- Cluster frequency: `5/122` (`4.1%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `5/122` (`4.1%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `e2934fe7abfa421c8133d9534a20e429`, summary `Runtime Error`, score `0`, vector `000`

```python
    p=len(b)
    b=b[::-1]
    j=0
    d[p]=[0]
    for i in range(len(a)):
        for k in range(len(b)):
            if (i==k):
                if (((a[i]%2==0) and (b[k]%2==0)) or ((a[i]%2!=0) and (b[k]%2!=0))):
                    d[j]=a[i]+b[k]
                elif (((a[i]%2==0) and (b[k]%2!=0)) or ((a[i]%2!=0)and (b[k]%2==0))):
                    d[j]=a[i]-b[k]
        j=j+1
    return d
    ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/122` (`2.5%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `3/122` (`2.5%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `09f86b8eb796402fbd1b82c466f018ab`, summary `Runtime Error`, score `0`, vector `000`

```python
def mirror_merge(a: list, b: list) -> list:
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.

    Args:
        a (list): First list of numbers.
        b (list): Second list of numbers (same length as a).

    Returns:
        list: List of computed values.
    '''
x = a[0]
y = b[-1]
# ...
```

### Uses `b[-i]` instead of `b[-i-1]` for mirror indexing (`i=0` incorrectly selects `b[0]`)

- Cluster frequency: `3/122` (`2.5%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `3/122` (`2.5%`)
- Dominant private-case vectors: `000` x2, `010` x1
- Score distribution (top): `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `aa1711c3f28f4377b046245af20cca2a`, summary `Wrong Answer`, score `0`, vector `000`

```python
    l1=[]
    z=len(a)
    i=0
    for i in range(z):
        x=a[i]
        i=i+1
        y=b[-i]
        if x%2==0 and y%2==0:
            if x%2!=0 and y%2!=0:
                l1.append(x+y)
        else:
            l1.append(x-y)
    return l1
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

# ...
```

### Uses nested loops over both lists (cross-product), producing too many pairings instead of one mirror pair per index

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `010` x1, `110` x1
- Score distribution (top): `33.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `2031e30f143e44fb8e244b20aea04ed7`, summary `Wrong Answer`, score `67`, vector `110`

```python
    b_reverse=b[::-1]
    new_list=[]
    for num1 in a :
        for num2 in b_reverse:
            if ((num1%2==0 and num2%2==0) or (num1%2!=0 and num2%2!=0)):
                ab=num1+num2
                new_list.append(ab)
            elif ((num1%2==0 and num2%2!=0) or (num1%2!=0 and num2%2==0)):
                ab=num1-num2
                new_list.append(ab)
    if len(new_list)%2==0:
        return [new_list[0],new_list[-1]]
    elif len(new_list)%2!=0:
        middle_element=new_list[len(new_list)//2]
        return [new_list[0],middle_element,new_list[-1]]
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
# ...
```

### Near-correct mirror pairing, but mixed-parity subtraction sign/parity condition is wrong on hidden cases

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `110` x2
- Score distribution (top): `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `eb1fa55d6e634e9d9b6510ea938277ef`, summary `Wrong Answer`, score `67`, vector `110`

```python
    for i in range(len(a)):
        for j in range(len(b)):
            b1=b[::-1]
            if i==j:
                if a[i]%2==0 and b1[j]%2==0:
                    l.append(a[i]+b1[j])
                elif a[i]%2!=0 and b1[j]%2!=0:
                    l.append(a[i]+b1[j])
                else:
                    l.append(a[i]-b1[j])
    return(l)
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.
# ...
```

### Returns a constant list (`[]` or fixed values) instead of computing the mirror merge from `a` and `b`

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `23e60230fa8d4fc4a377d5d386672d0a`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return[-5, -3, 6]
```

### Mirror-index/pairing bug (wrong `b` index formula or partial pairing) causes one private group to fail

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `010` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `a42cbebc788f40d7a14acced46458100`, summary `Wrong Answer`, score `33`, vector `010`

```python
    b.reverse()
    n=len(a)
    l=[]
    for i in (0,n-2,n-1):
            if a[i]%2==0 and b[i]%2==0:
                l.append(a[i]+b[i])
            elif a[i]%2!=0 and b[i]%2!=0:
                l.append(a[i]+b[i])
            elif a[i]%2!=0 and b[i]%2==0:
                l.append(a[i]-b[i])
            else:
                l.append(a[i]-b[i])
    if l[1]==-11:
            del l[1]
    return l
```

### Applies extra sign-flip/negation logic, producing the wrong sign for mixed-parity results

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `6a80a91c9ff4453b81877f427c3162af`, summary `Wrong Answer`, score `0`, vector `000`

```python
    len(b)==len(a)
    n=len(a)
    result=[]
    for i in range(n):
        if a[i]%2==0 and b[-1-i]%2==0:

            k=(a[i]+b[-1-i])
            result.append(k)
        elif a[i]%2!=0 and b[-1-i]%2!=0:
            m=-(a[i]-b[-1-i])
            result.append(m)
        elif a[i]%2==0 and b[-1-i]%2!=0:

            ma=-(b[-1-i]-a[i])
            result.append(ma)
        elif a[i]%2!=0 and b[-1-i]%2==0:
            emr=-(b[-1-i]-a[i])
            result.append(emr)
# ...
```

### Hard-codes public sample outputs / fixed lists instead of applying the mirror-merge rule generically

- Cluster frequency: `2/122` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `2/122` (`1.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `c8de21f233eb49b598e6fa9001e25ddc`, summary `Wrong Answer`, score `0`, vector `000`

```python
    l = []
    for i in range(len(a)):
        # c = b[-3]
        if a[i]%2==0 and b[-(i+1)]%2==0:
            # print(i)
            # print(a[i],b[i])
            l.append( (a[i]+b[i]) )
        else:
            # print(i)
            # print(a[i],b[i])
            l.append( (a[i]-b[-(i+1)]) )
    return l
```

### Splits the lists into halves and combines them, but the task requires elementwise mirror pairing across the full lists

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `003a9a69617049feb4d411a18548cc1a`, summary `Wrong Answer`, score `0`, vector `000`

```python
    new_list = []
    mid_point = len(a) // 2
    mid_point_1 = len(b) // 2
    first_half = a[:mid_point]
    second_half = b[mid_point_1:]
    y = second_half[::-1]
    for i in first_half:
        for j in y:
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 ==1):
                y = int(i) + int(j)
                new_list.append(y)
            else:
                x = int(i) - int(j)
                new_list.append(x)
    return new_list
```

### Returns list concatenation (`a + b`) instead of elementwise mirror merge

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `11f993fc9ae540789990a345fd44f767`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return a+b
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.

    Args:
        a (list): First list of numbers.
        b (list): Second list of numbers (same length as a).

    Returns:
        list: List of computed values.
    '''
    ...
```

### Uses XOR-based parity logic incorrectly, so same-parity vs mixed-parity add/subtract rules are inverted

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `18da978a7ebe4fd2a8dcb1f7f44d7e8d`, summary `Wrong Answer`, score `0`, vector `000`

```python
    x=[]
    for i in range(len(a)):
        if a[i]%2==0 ^ b[len(b)-i-1]%2==0:x.append(a[i]+b[len(b)-i-1])
        else:x.append(a[i]-b[len(b)-i-1])
    return x
```

### Destructive list-mutation pairing approach (`remove`/pop style) mishandles one hidden mirror case

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `42e956e36f5c4bc49d5107fdcb511320`, summary `Wrong Answer`, score `33`, vector `100`

```python
    new= []
    while(len(a)!=0):
        #while(len(b)!=0):
            if a[0]%2== 0 and b[-1]%2==0:
                new.append((a[0]+b[-1]))
                a.remove(a[0])
                b.remove(b[-1])
            if len(a)==0:
                break
            if a[0]%2 != 0 and b[-1]%2 != 0:
                new.append(a[0]+b[-1])
                a.remove(a[0])
                b.remove(b[-1])
            if len(a)==0:
                break
            else:
                new.append(a[0]-b[-1])
            a.remove(a[0])
# ...
```

### Uses bitwise `&` in parity checks (operator/precedence bug) instead of logical `and`

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `4aee10ee582f40b9bddf90fde7953215`, summary `Wrong Answer`, score `0`, vector `000`

```python
    m = a
    n = len(a)
    j = n-1
    k = 0
    for i in range(n):
        if a[i]%2 ==0 & b[j]%2== 0:
            m[k] = a[i] + b[j]


        elif a[i]%2 !=0 & b[j]%2!= 0:
            m[k] = a[i] + b[j]

        else:
            m[k] = a[i] - b[j]

        j-= 1
        k+= 1
    return m
```

### Uses `.index(...)` to match mirrored elements, which breaks on duplicate values (first-occurrence index bug)

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `73edef9e00984b2da790aab327c37755`, summary `Wrong Answer`, score `67`, vector `101`

```python
    ll=[]
    bb=b[::-1]
    for i in (a):
        for j in (bb):
            if a.index(i)== bb.index(j):
                if i%2==0 and j%2==0:
                    ll.append(i+j)
                elif i%2!=0 and j%2!=0:
                    ll.append(i+j)
                else:
                    ll.append(i-j)
    return(ll)
```

### Copies evaluator tests (`is_equal(mirror_merge(...))`) into the function and triggers recursive/self-test failures

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `93a166dcb2594bb58c52afb865e68937`, summary `Runtime Error`, score `0`, vector `000`

```python
    is_equal(
        mirror_merge([1,2,3],[4,5,6]),
        [-5,-3,-1]
    )
    is_equal(
        mirror_merge([10,11],[20,21]),
        [-11,-9]
    )
    is_equal(
        mirror_merge([7,8,9],[2,4,6]),
        [1,12,7]
    )
```

### Interleaves raw elements from `a` and reversed `b` instead of computing one merged value per mirror pair

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `a529a2786ceb48a0b613ef637bd59938`, summary `Wrong Answer`, score `0`, vector `000`

```python
    result=[]
    i=0
    j=len(b)-1
    while i<len(a) and j >= 0:
        result.append(a[i])
        result.append(b[j])
        i+=1
        j-=1
    result.extend(a[i:])
    result.extend (b[:j+1])
    return result
    '''
    Given two equal-length lists of numbers, pairs each element from the start
    of the first list with the corresponding element from the end of the second list,
    and applies the following rules:

    - If both numbers are odd or both are even, add them.
    - If one is odd and the other is even, subtract the second from the first.
# ...
```

### Runtime AttributeError

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `bc224336dcf6419cb54900c1a5b54042`, summary `Runtime Error`, score `0`, vector `000`

```python
    a = int(a.split())
    b = int(b.split())
    if a % 2 == 0 and b[:-1] % 2 == 0:
        return a[i] + b[i]
    else:
        return a[i] - b[i]
```

### Length-specific manual implementation (fixed indices for length-3) instead of a loop-based general solution

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `c6aeaa57bdc84feaa478eccc99c52ba1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    t = []
    result = []
    if len(a) and len(b) == 3:
        # if a[0]:
        r1 = a[0] - b[-1]
        if a[1] and b[-2] % 2 == 0:
            r2 = a[1] + b[-2]
        else:
            r2 = a[1] - b[-2]
        r3 = a[2] - b[-3]
        result.append(r1)
        result.append(r2)
        result.append(r3)
        return result
    elif len(a) and len(b) == 2:
        r1 = a[0] - b[-1]
        r2 = a[1] - b[-2]
        result.append(r1)
# ...
```

### Converts the input lists to strings / tuple output instead of computing numeric mirror-merge results

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `ea309c5e01454a809cfafdd268e91219`, summary `Wrong Answer`, score `0`, vector `000`

```python
    X = str(a)
    Y = str(b)
    return X, Y
    ...
```

### Subtracts in the wrong direction for mixed parity (`b_rev - a` instead of `a - b_rev`)

- Cluster frequency: `1/122` (`0.8%`)
- Variant frequencies:
  - `ns_25t3_py22/9`: `1/122` (`0.8%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/9`, Student ID `f06e96f289b54df7a2558ff4c2bfd31c`, summary `Wrong Answer`, score `67`, vector `110`

```python
    ...
    result=[]
    n= len(a)
    for i in range(n):
        x=a[i]
        y=b[n-1-i]

        if (x%2==0 and y%2==0) or (x%2!=0 and y%2!=0):
            result.append(x+y)
        else:
            result.append(y-x)
    return result
```
