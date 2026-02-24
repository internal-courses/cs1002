# Error Patterns: Cluster C083 (`Double First and Last Elements in a List`)

## Cluster Summary

- Cluster ID: `C083`
- Cluster title: `Double First and Last Elements in a List`
- Cluster file (this file): `analysis/ERRORS-cluster-c083-double-first-and-last-elements-in-a-list-7ed6a713.md`
- Variants in cluster: `1`
- Total final submitters across variants: `821`
- Total non-full final submissions across variants: `307`
- Canonical variant (by submissions): `ns_25t2_py13_2/5`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_2/5` (canonical) |              821 |      307 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `821`
- Full pass: `514`
- Non-full final submissions: `307`
- Parseable non-full (logic/runtime focus): `240`
- Non-parseable non-full: `67`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_2/5` |              821 |       514 |      307 |                240 |                     67 |

## Private Case Structure

- Private case 1: mixed string-list cases (length 3 and 4) to verify duplicate-first-prefix + duplicate-last-suffix ordering
- Private case 2: boolean/uppercase cases incl minimum-length list (`len=2`) edge behavior
- Private case 3: float and longer-list cases to catch length-specific/sample-only implementations

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                        | Cluster count | % of cluster non-full | `ns_25t2_py13_2/5` |
| ---------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: |
| Incorrect list-end duplication logic (broad wrong-answer failure)                              |            67 |                 21.8% |                 67 |
| Syntax / non-parseable final submission                                                        |            67 |                 21.8% |                 67 |
| Runtime TypeError                                                                              |            64 |                 20.8% |                 64 |
| Sorts the list after adding duplicates, losing the required original order                     |            18 |                  5.9% |                 18 |
| Runtime NameError                                                                              |            16 |                  5.2% |                 16 |
| No return / implicit `None`                                                                    |            16 |                  5.2% |                 16 |
| Runtime error (parseable final submission)                                                     |             7 |                  2.3% |                  7 |
| Returns the original list unchanged instead of duplicating first/last elements                 |             7 |                  2.3% |                  7 |
| Returns only duplicated ends and drops the middle elements of the original list                |             5 |                  1.6% |                  5 |
| Converts the list to a string and manipulates characters instead of duplicating list elements  |             5 |                  1.6% |                  5 |
| Runtime AttributeError                                                                         |             5 |                  1.6% |                  5 |
| Length-specific sample-case implementation (handles only a few list lengths like 2/3/5)        |             5 |                  1.6% |                  5 |
| Runtime TypeError from mixing multiplied element values with list concatenation                |             4 |                  1.3% |                  4 |
| Runtime RecursionError                                                                         |             3 |                  1.0% |                  3 |
| Mutates the input list by appending last then first (wrong order/position for duplicated ends) |             3 |                  1.0% |                  3 |
| Runtime AttributeError from list-method misuse while building duplicated-ends output           |             3 |                  1.0% |                  3 |
| Reads `input()` inside function (EOF under evaluator function-call tests)                      |             3 |                  1.0% |                  3 |
| Runtime TypeError from assigning `.append()` result (`None`) and then using it as a list       |             3 |                  1.0% |                  3 |
| Multiplies element values (`l[0]*2`, `l[-1]*2`) instead of duplicating list entries            |             2 |                  0.7% |                  2 |
| Runtime IndexError                                                                             |             2 |                  0.7% |                  2 |
| Hard-codes public sample outputs instead of duplicating list ends generically                  |             1 |                  0.3% |                  1 |
| Runtime ValueError                                                                             |             1 |                  0.3% |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/307` (`0.0%`)

### Incorrect list-end duplication logic (broad wrong-answer failure)

- Cluster frequency: `67/307` (`21.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `67/307` (`21.8%`)
- Dominant private-case vectors: `000` x66, `100` x1
- Score distribution (top): `0.0` x66, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `ddce74557b604952ab744df8ea4c91cb`, summary `Wrong Answer`, score `0`, vector `000`

```python
    length=len(l)
    newlist=[]
    if length<2:
        return l
    else:
        for i in l:
            if i==0 or i==length-1:
                newlist.append(i)
                newlist.append(i)
            else:
                newlist.append(i)
        return newlist
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `67/307` (`21.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `67/307` (`21.8%`)
- Dominant private-case vectors: `000` x67
- Score distribution (top): `0.0` x67
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `653e7c0b5ee5476782e91306da567400`, summary `Runtime Error`, score `0`, vector `000`

```python
def double_ends(l: list) -> list:
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
    [5, 5, 6, 7, 8, 8]

# ...
```

### Runtime TypeError

- Cluster frequency: `64/307` (`20.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `64/307` (`20.8%`)
- Dominant private-case vectors: `000` x64
- Score distribution (top): `0.0` x64
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `62e565f745ba48a0b52c251ad7e9c344`, summary `Runtime Error`, score `0`, vector `000`

```python
    result=[l]
    for x in l:
        a=l[0]
        b=l[-1]
        (a) in l[0]
        result.append(a)
        (b)in result in l[-1]
    return(result)
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
# ...
```

### Sorts the list after adding duplicates, losing the required original order

- Cluster frequency: `18/307` (`5.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `18/307` (`5.9%`)
- Dominant private-case vectors: `011` x17, `000` x1
- Score distribution (top): `67.0` x17, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `cbcddeb4a3b6488293798500bdfd160a`, summary `Wrong Answer`, score `67`, vector `011`

```python
    for i in range(x+1):
        a=l[0]
        b=l[-1]
        l.append(a)
        l.append(b)
        l.sort()
    return l
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
# ...
```

### Runtime NameError

- Cluster frequency: `16/307` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `16/307` (`5.2%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `0101ff45b51f46f7bd0ac789beca57aa`, summary `Runtime Error`, score `0`, vector `000`

```python
    if len(len_list)>2:
        print("Error:Input list must contain at least two elements.")
    return[]
    first_element = l_list[0]
    last_element = l_list[-1]
    new_list=[first_element]+l_list+[last_element]
    return new_list
    list1=[10,20,30]
    result1=double_ends(list1)
    print(f">>>double_ends({list1})->{result1}")
    list2=['a','b','c']
    result2=double_ends(list2)
    print(f">>> double_ends({list2})->{result2}")
    list3=[1,2]
    result3=double_ends(list3)
    print(f">>>double_ends({list3})->{result3}")
    list4=[3,4,7,8]
    result4=double_ends(list4)
# ...
```

### No return / implicit `None`

- Cluster frequency: `16/307` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `16/307` (`5.2%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `77d36c55a016499eac5129293936c94c`, summary `Wrong Answer`, score `0`, vector `000`

```python
def double_ends(l: list) -> list:
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
    [5, 5, 6, 7, 8, 8]

# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `7/307` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `7/307` (`2.3%`)
- Dominant private-case vectors: `000` x5, `100` x1, `101` x1
- Score distribution (top): `0.0` x5, `33.0` x1, `67.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `914df4e3cbed419c957a29d2ed8e5ce4`, summary `Runtime Error`, score `0`, vector `000`

```python
def double_ends(l: list) -> list:
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
    [5, 5, 6, 7, 8, 8]

# ...
```

### Returns the original list unchanged instead of duplicating first/last elements

- Cluster frequency: `7/307` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `7/307` (`2.3%`)
- Dominant private-case vectors: `000` x6, `110` x1
- Score distribution (top): `0.0` x6, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `8b054abc21b7470d8dac122089036e99`, summary `Wrong Answer`, score `67`, vector `110`

```python
    a=len(l)
    if a==3:
        b=l[1]
        c=l[2]
        l.pop()
        l.pop()
        l.append(l[0])
        l.append(b)
        l.append(c)
        l.append(c)
    if a==4:
        b=l[1]
        c=l[2]
        d=l[3]
        l.pop()
        l.pop()
        l.pop()
        l.append(l[0])
# ...
```

### Returns only duplicated ends and drops the middle elements of the original list

- Cluster frequency: `5/307` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `5/307` (`1.6%`)
- Dominant private-case vectors: `000` x3, `010` x2
- Score distribution (top): `0.0` x3, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `50a9b053ea51456488590d0a4511144c`, summary `Wrong Answer`, score `33`, vector `010`

```python
if len(l) == 3:
    return [l[0], l[0], l[1], l[-1], l[-1]]
if len(l) == 2:
    return [l[0], l[0], l[-1], l[-1]]
if len(l) == 5:
    return [l[0], l[0], l[1], l[2], l[3], l[4], l[4]]
```

### Converts the list to a string and manipulates characters instead of duplicating list elements

- Cluster frequency: `5/307` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `5/307` (`1.6%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `20d24394523c440293ce5ad84512d57a`, summary `Wrong Answer`, score `0`, vector `000`

```python
copy_list = []
i = 0
for _ in l:
    i = i + 1
if i < 2:
    return None
for nums in l:
    copy_list = [str(l[0]) + str(l) + str(l[i - 1])]
return copy_list
```

### Runtime AttributeError

- Cluster frequency: `5/307` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `5/307` (`1.6%`)
- Dominant private-case vectors: `000` x4, `100` x1
- Score distribution (top): `0.0` x4, `33.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `5dce5e0ce200480b9132473e601e9c04`, summary `Runtime Error`, score `0`, vector `000`

```python
    l = l.insert(1,l[0])
    b = l.insert(-2,l[-1])
    return b
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
# ...
```

### Length-specific sample-case implementation (handles only a few list lengths like 2/3/5)

- Cluster frequency: `5/307` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `5/307` (`1.6%`)
- Dominant private-case vectors: `000` x2, `010` x2, `110` x1
- Score distribution (top): `0.0` x2, `33.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `862c8df61f754859bd9fa79ff7c845f6`, summary `Wrong Answer`, score `0`, vector `000`

```python
    numm = ""
    first = l[0]
    last = l[-1]
    middle = l[1]
    middle1 = l[1:4]
    ls = [first,first,middle,last,last]
    ls2 = [first,first,last,last]
    ls3 = [first,first,1,2,3,last,last]
    if len(l) == 2:
        return ls2
    elif len(l) == 5:
        return ls3
    else:
        return ls
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end
# ...
```

### Runtime TypeError from mixing multiplied element values with list concatenation

- Cluster frequency: `4/307` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `4/307` (`1.3%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `cb200c2a437a4904b5f3f469f87bd159`, summary `Runtime Error`, score `0`, vector `000`

```python
...
n = "".join(l)
k = n[0] * 2 + n[1:-1] + n[-1] * 2
m = n[0] * 2 + n[1:-1] + n[-1] * 2
return list(str(k)) or m
return f" {l[0] * 2 + l[1::-1] + l[-1] * 2}"
```

### Runtime RecursionError

- Cluster frequency: `3/307` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `3/307` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `614b436020c543a5874200f8bf352ae2`, summary `Runtime Error`, score `0`, vector `000`

```python
...
for i in l:
    double_ends([0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 6])
    list.append(double_ends)
```

### Mutates the input list by appending last then first (wrong order/position for duplicated ends)

- Cluster frequency: `3/307` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `3/307` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `6af2700553604f52bbfd3acb087cbb70`, summary `Wrong Answer`, score `0`, vector `000`

```python
l_new = []
l_new.append(l[0])
l_new.append(l[0])
l_new.append(l[1:-1])
l_new.append(l[-1])
l_new.append(l[-1])
return l_new
```

### Runtime AttributeError from list-method misuse while building duplicated-ends output

- Cluster frequency: `3/307` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `3/307` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `6be72e176611431ca64803da234c9136`, summary `Runtime Error`, score `0`, vector `000`

```python
    '''
    k = []
    lt = len(l)
    for num in range(1000):
        first = l[0]*2
        first.append(k)
    for num in range(l):
        mid = lt/2
        mid.append(k)
    for num in range(l):
        last = l[-1]*2
        last.append(k)
    return k
    '''
    '''
    first = l[0]*2
    last = l[-1]*2
    fir = str(first)
# ...
```

### Reads `input()` inside function (EOF under evaluator function-call tests)

- Cluster frequency: `3/307` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `3/307` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `d27badb51aae4f91914b66058840e516`, summary `Runtime Error`, score `0`, vector `000`

```python
...
l = list(input())
list1 = list(l)
if len(l) >= 2:
    a = list1[0]
    b = list1[int(len(l))]
    list1.add(0, a)
    list1.add(len(l) - 1, b)
    result = list1
    return result
```

### Runtime TypeError from assigning `.append()` result (`None`) and then using it as a list

- Cluster frequency: `3/307` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `3/307` (`1.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `f6c4043e0ba14603afcda2ccd4186ae2`, summary `Runtime Error`, score `0`, vector `000`

```python
new_list = []
new_list.append(l[0])
"""string=""
for i in l:
    for i in range(0,-1):
        string=string,i
    print (string)"""
for i in l:
    new_list.append(l[i])
new_list.append(l[-1])
"""for i in l:
    new_list=l.append(l[0])
    new_list=l.append(l[-1])"""
return new_list
```

### Multiplies element values (`l[0]*2`, `l[-1]*2`) instead of duplicating list entries

- Cluster frequency: `2/307` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `2/307` (`0.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `243c453fe02d4762aa4454ab69315171`, summary `Wrong Answer`, score `0`, vector `000`

```python
new_l = []
new_l.append(l)
for i in l:
    new_l = [l[0] * 2, i, l[-1] * 2]
return new_l
```

### Runtime IndexError

- Cluster frequency: `2/307` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `2/307` (`0.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `c536134ab8e34018926f369f8c716f52`, summary `Runtime Error`, score `0`, vector `000`

```python
n = len(l)
num = []
if len(l) >= 2:
    for i in range(0, n):
        if i == 0:
            num[i] = l[i]
        elif i == n - 1:
            num[i + 1] = l[i]
        else:
            num[i] = l[i]
    return num
else:
    return 0
```

### Hard-codes public sample outputs instead of duplicating list ends generically

- Cluster frequency: `1/307` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `1/307` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `661128a22ec34a4aaedc1e7d523ee925`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return ['x', 'x', 'y', 'z', 'z']
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end
    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
    [5, 5, 6, 7, 8, 8]

    Args:
# ...
```

### Runtime ValueError

- Cluster frequency: `1/307` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/5`: `1/307` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/5`, Student ID `e22f93eb66374b19905b4035ccb2b47f`, summary `Runtime Error`, score `0`, vector `000`

```python
def double_ends(l: list) -> list:
    '''
    Given a list with at least two elements, return a new list where:
    - the first element is duplicated at the beginning
    - the last element is duplicated at the end

    The original list should remain unchanged.

    Examples:
    >>> double_ends([10, 20, 30])
    [10, 10, 20, 30, 30]
    >>> double_ends(['a', 'b', 'c'])
    ['a', 'a', 'b', 'c', 'c']
    >>> double_ends([1, 2])
    [1, 1, 2, 2]
    >>> double_ends([5, 6, 7, 8])
    [5, 5, 6, 7, 8, 8]

# ...
```
