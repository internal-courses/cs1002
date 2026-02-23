# Error Patterns: Cluster C086 (`Repeat Second Half of a Tuple`)

## Cluster Summary

- Cluster ID: `C086`
- Cluster title: `Repeat Second Half of a Tuple`
- Cluster file (this file): `analysis/ERRORS-cluster-c086-repeat-second-half-of-a-tuple-dd65a096.md`
- Variants in cluster: `1`
- Total final submitters across variants: `766`
- Total non-full final submissions across variants: `291`
- Canonical variant (by submissions): `ns_25t2_py14_1/7`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py14_1/7` (canonical) | 766 | 291 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py14_1/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `766`
- Full pass: `475`
- Non-full final submissions: `291`
- Parseable non-full (logic/runtime focus): `245`
- Non-parseable non-full: `46`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py14_1/7` | 766 | 475 | 291 | 245 | 46 |

## Private Case Structure

- Private case 1: odd-length tuples (len 5 and 3): middle belongs to first half; only suffix repeats
- Private case 2: odd-length tuples with floats/strings to catch type/shape assumptions
- Private case 3: minimum even tuple (`len=2`) and longer odd tuple (`len=7`) edge behavior

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py14_1/7` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 46 | 15.8% | 46 |
| Incorrect repeated-second-half tuple logic (broad wrong-answer failure) | 44 | 15.1% | 44 |
| No return / implicit `None` | 40 | 13.7% | 40 |
| Near-correct tuple-slicing logic with midpoint off-by-one bug (commonly `mid+1` suffix selection) | 34 | 11.7% | 34 |
| Returns from inside the build loop before constructing the full repeated-half tuple | 28 | 9.6% | 28 |
| Runtime TypeError | 23 | 7.9% | 23 |
| Hard-codes public sample tuple outputs instead of repeating the second half generically | 13 | 4.5% | 13 |
| Runtime NameError | 10 | 3.4% | 10 |
| Runtime error (parseable final submission) | 10 | 3.4% | 10 |
| Runtime TypeError from list/tuple concatenation shape mismatch while repeating the second half | 9 | 3.1% | 9 |
| Runtime AttributeError | 6 | 2.1% | 6 |
| Reads `input()` inside function-type question (EOF under evaluator tests) | 5 | 1.7% | 5 |
| Length-specific branch implementation (handles a few tuple sizes instead of a general midpoint rule) | 5 | 1.7% | 5 |
| Runtime IndexError | 4 | 1.4% | 4 |
| Returns the original tuple unchanged instead of appending a repeated second half | 3 | 1.0% | 3 |
| Runtime AttributeError from list/string method misuse during tuple transformation | 3 | 1.0% | 3 |
| Uses `round(len(t)/2)` for the split point, causing parity/off-by-one errors for odd/even tuples | 2 | 0.7% | 2 |
| Parity/half-split bug (wrong midpoint rule for odd vs even tuple lengths) | 2 | 0.7% | 2 |
| List-based reconstruction bug (wrong elements/order repeated before converting back to tuple) | 1 | 0.3% | 1 |
| Runtime ValueError | 1 | 0.3% | 1 |
| Runtime RecursionError | 1 | 0.3% | 1 |
| Duplicates `t[mid:]`, so odd-length tuples wrongly repeat the middle element | 1 | 0.3% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/291` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `46/291` (`15.8%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `46/291` (`15.8%`)
- Dominant private-case vectors: `000` x46
- Score distribution (top): `0.0` x46
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `df2cdbc7fb2a44e4ba72d65308a3f9c1`, summary `Runtime Error`, score `0`, vector `000`

```python
def repeat_second_half(t: tuple) -> tuple:
    tuple_to_list = list(t)
    n = 0
    number_of_elements = len(tuple_to_list)

    if number_of_elements%2==1:
       m=0
       odd_no_of_elements=len(tuple_to_list)
       number_of_elements_to_be_appended = (((odd_no_of_elements)-1)/2)
       n1=int(number_of_elements_to_be_appended)
       for i in range(n1):
           j=2*i+1
           n2=(odd_no_of_elements+j)/2
           list_to_be_returned=tuple_to_list.append(n2)
        return list_to_be_returned
    if number_of_elements%2==0:
        even_no_of_elements=len(tuple_to_list)
        even_no_of_elements_to_be_appended = ((even_no_of_elements)/2)
# ...
```

### Incorrect repeated-second-half tuple logic (broad wrong-answer failure)

- Cluster frequency: `44/291` (`15.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `44/291` (`15.1%`)
- Dominant private-case vectors: `000` x44
- Score distribution (top): `0.0` x44
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `91476d67ed1b4bd58e297aa0549a139c`, summary `Wrong Answer`, score `0`, vector `000`

```python
def repeat_second_half(t: tuple) -> tuple:
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)

    Args:
        t (tuple): A tuple with at least two elements
# ...
```

### No return / implicit `None`

- Cluster frequency: `40/291` (`13.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `40/291` (`13.7%`)
- Dominant private-case vectors: `000` x39, `110` x1
- Score distribution (top): `0.0` x39, `67.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `44db886f898a499789806b5566fe0925`, summary `Wrong Answer`, score `0`, vector `000`

```python
    a = [1,2,3,4,5,6]
    c = a[-2:]
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)

    Args:
# ...
```

### Near-correct tuple-slicing logic with midpoint off-by-one bug (commonly `mid+1` suffix selection)

- Cluster frequency: `34/291` (`11.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `34/291` (`11.7%`)
- Dominant private-case vectors: `110` x31, `000` x3
- Score distribution (top): `67.0` x31, `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `1b1338d667224f8eacb6cd55a93ded3e`, summary `Wrong Answer`, score `67`, vector `110`

```python
    mid=len(t)//2
    mid_ele=t[mid]
    if len(t)%2==0:
        return t[:mid]+t[mid+1:]+t[mid+1:]
    elif len(t)%2!=0:

        return t[:mid]+(mid_ele,)+t[mid+1:]+t[mid+1:]
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
# ...
```

### Returns from inside the build loop before constructing the full repeated-half tuple

- Cluster frequency: `28/291` (`9.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `28/291` (`9.6%`)
- Dominant private-case vectors: `110` x15, `000` x12, `101` x1
- Score distribution (top): `67.0` x16, `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `6d6015456de94a3ba76014e6efeff635`, summary `Wrong Answer`, score `67`, vector `110`

```python
    s=len(t)
    m=int(s/2)+1
    n=int((s+1)/2)
    list=[]
    for i in range (len(t)):
        list.append(t[i])
    j =  len(list)
    if j %  2== 0:
        for k in range(m,i+1):
                list.append(list[k])
    else:
        for k in range(n,i+1):
            list.append(list[k])
    x=tuple(list)
    return x
    '''
    list = [t]
    i = len(t)
# ...
```

### Runtime TypeError

- Cluster frequency: `23/291` (`7.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `23/291` (`7.9%`)
- Dominant private-case vectors: `000` x22, `110` x1
- Score distribution (top): `0.0` x22, `67.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `c98c06057e81437ea7193ce8cd4e0e20`, summary `Runtime Error`, score `0`, vector `000`

```python
    halfindex= ((len(tuple))%2)
    halftuple= tuple[halftuple::tuple]
    collection: tuple+halftuple
    return collection
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)
# ...
```

### Hard-codes public sample tuple outputs instead of repeating the second half generically

- Cluster frequency: `13/291` (`4.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `13/291` (`4.5%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `4d40e7c9c5504e9ca2b757851a7a0b55`, summary `Wrong Answer`, score `0`, vector `000`

```python
    left, right=0,len(t)-1
    mid=left+right//2
    return (4,5,6,7,8,7,8)
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)

# ...
```

### Runtime NameError

- Cluster frequency: `10/291` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `10/291` (`3.4%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `bb1e9aef6f2045d5afdbe6c18eecd1c3`, summary `Runtime Error`, score `0`, vector `000`

```python
def repeat_second_half(t: tuple) -> tuple:
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)

    Args:
        t (tuple): A tuple with at least two elements
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `10/291` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `10/291` (`3.4%`)
- Dominant private-case vectors: `000` x6, `110` x4
- Score distribution (top): `0.0` x6, `67.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `cb55ce4b93a0474196e2be538a64be50`, summary `Runtime Error`, score `0`, vector `000`

```python
def repeat_second_half(t: tuple) -> tuple:
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
    (1, 2, 3, 3)

    Args:
        t (tuple): A tuple with at least two elements
# ...
```

### Runtime TypeError from list/tuple concatenation shape mismatch while repeating the second half

- Cluster frequency: `9/291` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `9/291` (`3.1%`)
- Dominant private-case vectors: `000` x4, `110` x4, `001` x1
- Score distribution (top): `0.0` x4, `67.0` x4, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `215441d3353b4107b21659be01094685`, summary `Runtime Error`, score `0`, vector `000`

```python
    t4=str(t)
    t1=[]
    t2=[]
    l= len(t4)
    if l%2==0:
        for i in range(l):
            if i<l/2:
                t1=t1.append (t(i))
            else:
                t2=t2.append(t(i))
        t3=t2*2
        return tuple(t1.append(t3))
    else :
        for i in range(l):
            if i<(l/2)+1:
                t1=t1.append(t(i))
            else:
                t2=t2.append(t(i))
# ...
```

### Runtime AttributeError

- Cluster frequency: `6/291` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `6/291` (`2.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `2c41356dd8b947058b05e123dfc72faf`, summary `Runtime Error`, score `0`, vector `000`

```python
    tu=tuple() #a new tuple
    sec_half=tuple()
    if len(t)%2 == 0:
        m=len(t)/2
        sec_half+=(t.value(index(m+1)),)
    if len(t)%2 != 0:
        m=(len(t)+1)/2
        sec_half+=(t.value(index(m+1)),)
    if len(t)>=2:
            tu=tu+t+sec_half
    return tu
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `5/291` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `5/291` (`1.7%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `4ba275e80602423dbb4287c653130c3c`, summary `Runtime Error`, score `0`, vector `000`

```python
    a = list(input())
    if(len(a)%2==0):
        b = a[len(a)/2:]
        c = a.append(b)
        print(c)
    else:
        b = a[(len(a)/2)+1:]
        c = a.append(b)
        print(c)
```

### Length-specific branch implementation (handles a few tuple sizes instead of a general midpoint rule)

- Cluster frequency: `5/291` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `5/291` (`1.7%`)
- Dominant private-case vectors: `000` x4, `110` x1
- Score distribution (top): `0.0` x4, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `77e82ca1230647be951608b63795d672`, summary `Wrong Answer`, score `67`, vector `110`

```python
    t = list(t)
    if len(t) < 2 or len(t) == 2:
        return 0

    elif len(t)%2 == 0:
        middle_index = int(len(t)/2)-1
        middle_element = t[middle_index]

        return tuple(t[0:middle_index+1]+(t[middle_index+1:]*2))

    else:
        middle_index = int(len(t)/2)
        middle_element = t[middle_index]

        return tuple(t[0:middle_index+1]+(t[middle_index+1:]*2))
    ...
```

### Runtime IndexError

- Cluster frequency: `4/291` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `4/291` (`1.4%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `067f9db7707d403f9bd7610ae56ed43f`, summary `Runtime Error`, score `0`, vector `000`

```python
    size=len(t)
    if size%2==0:
        a=int(size/2)
        c=t[a]
        d=t[a+1]
        one=(c,d)
        final=t+one
        return final
    else:
        b1=size//2
        x=b1+1
        y=x+1
        ch=y+1
        x1=t[x]
        y1=t[y]
        if(size!=ch):
            d2=t[ch]
            xy=(x1,y1,d2)
# ...
```

### Returns the original tuple unchanged instead of appending a repeated second half

- Cluster frequency: `3/291` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `3/291` (`1.0%`)
- Dominant private-case vectors: `000` x2, `110` x1
- Score distribution (top): `0.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `ce71db9df8444af3b20c8fe9fd47ee98`, summary `Wrong Answer`, score `0`, vector `000`

```python
    j=()
    c =len(t)
    b= c%2
    d= c+1
    if c ==0:
         t.append(t[b:d])
    return t
```

### Runtime AttributeError from list/string method misuse during tuple transformation

- Cluster frequency: `3/291` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `3/291` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `b0acba77861f4494b09bf149d811c27b`, summary `Runtime Error`, score `0`, vector `000`

```python
    t1 = t[-1]
    t2 = t[-2]
    t.append(t2)
    t.append(t1)
    return t
```

### Uses `round(len(t)/2)` for the split point, causing parity/off-by-one errors for odd/even tuples

- Cluster frequency: `2/291` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `2/291` (`0.7%`)
- Dominant private-case vectors: `001` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `46514d463c5041779e49c7b36305ca71`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if(len(t)>5):
        tnew = t+t[-(round(len(t)/2)-1):]
    else:
        tnew = t+t[-(round(len(t)/2)):]
    return tnew
```

### Parity/half-split bug (wrong midpoint rule for odd vs even tuple lengths)

- Cluster frequency: `2/291` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `2/291` (`0.7%`)
- Dominant private-case vectors: `001` x1, `010` x1
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `ba1bd4efee5842a29cbc1a2edc29459f`, summary `Wrong Answer`, score `33`, vector `010`

```python
    l=list(set(t))
    mid=len(l)//2
    if(len(l)%2==0):

      ap=l[mid:len(l)]
    # print(ap)
      result=l+ap
      return tuple(result)
    elif(len(l)%2==1):

      ap=l[mid+1:len(l)]
    # print(ap)
      result=l+ap
      return tuple(result)
```

### List-based reconstruction bug (wrong elements/order repeated before converting back to tuple)

- Cluster frequency: `1/291` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `1/291` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `0852e5b565844e48b7d704ca6baa75b7`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if len(t)%2==0:
        mid=(len(t)//2)-1
    else:
        mid=len(t)//2
    tup=list(t)
    tupe=list(t)
    tu=list(t)
    del(tu[mid+1:len(t)])
    tu.append(tup[mid+1:len(t)])
    tu.append(tupe[mid+1:len(t)])
    return tuple(tu)
```

### Runtime ValueError

- Cluster frequency: `1/291` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `1/291` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `0fc8943c99ef4e8dbd0003a5602dd422`, summary `Runtime Error`, score `0`, vector `000`

```python
    mid=len(t)%2
    if len(t)%2==0:
        return t[::1]+t[::-mid]
    else:
        return t[::1]+t[::mid]
    '''
    Given a tuple, return a new tuple where the second half is repeated
    after the first half. If the tuple has an odd number of elements,
    include the middle element in the first half.

    Examples:
    >>> repeat_second_half((1, 2, 3, 4, 5))
    (1, 2, 3, 4, 5, 4, 5)
    >>> repeat_second_half((10, 20, 30, 40))
    (10, 20, 30, 40, 30, 40)
    >>> repeat_second_half(('a', 'b', 'c', 'd', 'e', 'f'))
    ('a', 'b', 'c', 'd', 'e', 'f', 'e', 'f')
    >>> repeat_second_half((1, 2, 3))
# ...
```

### Runtime RecursionError

- Cluster frequency: `1/291` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `1/291` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `6fd46350c14746d89da27fcbee5ebcda`, summary `Runtime Error`, score `0`, vector `000`

```python
    print("(4, 5, 6, 7, 8, 7, 8")
    print("('x', 'y', 'z', 'a', 'z', 'a')")
    print("(1, 2, 3, 4, 5, 6, 7, 5, 6, 7)")
    repeat_second_half((4, 5, 6, 7, 8))
```

### Duplicates `t[mid:]`, so odd-length tuples wrongly repeat the middle element

- Cluster frequency: `1/291` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/7`: `1/291` (`0.3%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/7`, Student ID `8cce26f15c2b429e890b238a7f5a0b7b`, summary `Wrong Answer`, score `67`, vector `110`

```python
    if len(t) > 2:
        mid = ((len(t) + 1)// 2)
        return (t + t[mid:])
```
