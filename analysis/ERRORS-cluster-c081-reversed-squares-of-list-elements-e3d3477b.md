# Error Patterns: Cluster C081 (`Reversed Squares of List Elements`)

## Cluster Summary

- Cluster ID: `C081`
- Cluster title: `Reversed Squares of List Elements`
- Cluster file (this file): `analysis/ERRORS-cluster-c081-reversed-squares-of-list-elements-e3d3477b.md`
- Variants in cluster: `1`
- Total final submitters across variants: `936`
- Total non-full final submissions across variants: `171`
- Canonical variant (by submissions): `ns_25t2_py22_1/17`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py22_1/17` (canonical) |              936 |      171 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py22_1/17.json`

## Cluster-Level Outcome Summary

- Final submitters: `936`
- Full pass: `765`
- Non-full final submissions: `171`
- Parseable non-full (logic/runtime focus): `139`
- Non-parseable non-full: `32`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py22_1/17` |              936 |       765 |      171 |                139 |                     32 |

## Private Case Structure

- Private case 1: single-element and multi-element positives (reverse after squaring)
- Private case 2: negative numbers and zero cases (squaring before/after reverse matters)
- Private case 3: duplicates/symmetric values to distinguish reverse-order vs sorted-order logic

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                 | Cluster count | % of cluster non-full | `ns_25t2_py22_1/17` |
| ------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: |
| Syntax / non-parseable final submission                                                                 |            32 |                 18.7% |                  32 |
| Runtime TypeError                                                                                       |            24 |                 14.0% |                  24 |
| Squares elements but does not reverse the order                                                         |            21 |                 12.3% |                  21 |
| Incorrect reversed-squares logic (broad wrong-answer failure)                                           |            15 |                  8.8% |                  15 |
| Hard-codes public sample outputs/cases instead of computing reversed squares                            |            14 |                  8.2% |                  14 |
| Reverses the list but forgets to square the elements                                                    |            13 |                  7.6% |                  13 |
| No return / implicit `None`                                                                             |            11 |                  6.4% |                  11 |
| Sorts squared values descending instead of preserving reversed input order                              |             8 |                  4.7% |                   8 |
| Runtime NameError                                                                                       |             6 |                  3.5% |                   6 |
| Runtime AttributeError                                                                                  |             4 |                  2.3% |                   4 |
| Prints squared values instead of returning the transformed list                                         |             3 |                  1.8% |                   3 |
| Runtime RecursionError                                                                                  |             3 |                  1.8% |                   3 |
| Runtime IndexError                                                                                      |             3 |                  1.8% |                   3 |
| Runtime TypeError from misusing `.reverse()` result / in-place reverse API                              |             2 |                  1.2% |                   2 |
| Returns from inside the build loop, producing only the first squared/reversed element                   |             2 |                  1.2% |                   2 |
| Runtime AttributeError from wrong list method/attribute usage                                           |             2 |                  1.2% |                   2 |
| Uses in-place `.reverse()` incorrectly (returns/mutates list without producing squared reversed result) |             1 |                  0.6% |                   1 |
| Attempts to square values, but ultimately returns only the reversed list (squares are not stored)       |             1 |                  0.6% |                   1 |
| Returns only one squared value wrapped in a list instead of the full reversed-squares list              |             1 |                  0.6% |                   1 |
| Partially correct list transformation (reverse-vs-sort order mistake on specific test groups)           |             1 |                  0.6% |                   1 |
| Runtime IndexError from invalid index while iterating transformed list                                  |             1 |                  0.6% |                   1 |
| Squares only the first two elements (length-specific partial implementation)                            |             1 |                  0.6% |                   1 |
| Squares index/range values instead of squaring the list elements                                        |             1 |                  0.6% |                   1 |
| Sorts values instead of reversing the input order before squaring                                       |             1 |                  0.6% |                   1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/171` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `32/171` (`18.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `32/171` (`18.7%`)
- Dominant private-case vectors: `000` x32
- Score distribution (top): `0.0` x32
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `ecb7c47113504c4d8feb3b0585190546`, summary `Runtime Error`, score `0`, vector `000`

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

### Runtime TypeError

- Cluster frequency: `24/171` (`14.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `24/171` (`14.0%`)
- Dominant private-case vectors: `000` x24
- Score distribution (top): `0.0` x24
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `8081d5521dcb4ba7ae8d2fd07f9282a4`, summary `Runtime Error`, score `0`, vector `000`

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

### Squares elements but does not reverse the order

- Cluster frequency: `21/171` (`12.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `21/171` (`12.3%`)
- Dominant private-case vectors: `000` x17, `001` x4
- Score distribution (top): `0.0` x17, `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `0377c1b8b14e4723a752391b0ed3b4c9`, summary `Wrong Answer`, score `0`, vector `000`

```python
    new_list=[]
    if l==[]:
        return new_list
    else:
        for i in range(len(l)):
            l[-1]=l[-1]**2
            new_list=new_list
            return new_list
    """
    Takes a list of numbers and returns a new list containing the
    squares of the elements in reverse order.

    Args:
        l (list): A list of numbers.

    Returns:
        list: A new list with squares in reverse order.

# ...
```

### Incorrect reversed-squares logic (broad wrong-answer failure)

- Cluster frequency: `15/171` (`8.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `15/171` (`8.8%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `8c2fefabc4a14d879aa13981b3539ff8`, summary `Wrong Answer`, score `0`, vector `000`

```python
    for i in l:
        i**2
    x = []
    x = reversed(l)
    return list(x)
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
# ...
```

### Hard-codes public sample outputs/cases instead of computing reversed squares

- Cluster frequency: `14/171` (`8.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `14/171` (`8.2%`)
- Dominant private-case vectors: `000` x13, `010` x1
- Score distribution (top): `0.0` x13, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `29bf8572e50240f9b475efda03611852`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if l==[1,2,3,4,5]:
        return [25,16,9,4,1]
    elif l==[10,2]:
        return [4,100]
    elif l==[]:
     return []
    """
    Takes a list of numbers and returns a new list containing the
    squares of the elements in reverse order.

    Args:
        l (list): A list of numbers.

    Returns:
        list: A new list with squares in reverse order.

    Examples:
        >>> reversed_squares([1, 2, 3])
# ...
```

### Reverses the list but forgets to square the elements

- Cluster frequency: `13/171` (`7.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `13/171` (`7.6%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `0fdf6645bdc54e7da88566e0422fbda1`, summary `Wrong Answer`, score `0`, vector `000`

```python
x = str(l[1:-1])
nums = x.split(",")
n = len(nums)
numbers = []
for num in range(1, n + 3):
    m = num
    number = m * m
    numbers.append(number)
return numbers[::-1]
```

### No return / implicit `None`

- Cluster frequency: `11/171` (`6.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `11/171` (`6.4%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `26c2a640962c420d95e8eb421b888db5`, summary `Wrong Answer`, score `0`, vector `000`

```python
    for ele in l:
        ele=ele**2
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
# ...
```

### Sorts squared values descending instead of preserving reversed input order

- Cluster frequency: `8/171` (`4.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `8/171` (`4.7%`)
- Dominant private-case vectors: `010` x6, `001` x2
- Score distribution (top): `33.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `b7d6d40c20dd467a90278981d2302061`, summary `Wrong Answer`, score `33`, vector `010`

```python
...
new_l = []
if len(l) < 1:
    return []
elif len(l) < 3:
    new_l.append(l[1] ** 2)
    new_l.append(l[0] ** 2)
    return new_l
else:
    for num in l:
        if num is not None or str(num).isnumeric():
            sq = num**2
            # print(sq)
            new_l.append(sq)
new_l2 = sorted(new_l, reverse=True)
return new_l2
```

### Runtime NameError

- Cluster frequency: `6/171` (`3.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `6/171` (`3.5%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `bb87f81c00064cff915615a6233f0c06`, summary `Runtime Error`, score `0`, vector `000`

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

### Runtime AttributeError

- Cluster frequency: `4/171` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `4/171` (`2.3%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `ea4030d43fba4474a17569dd9cdd0b55`, summary `Runtime Error`, score `0`, vector `000`

```python
...
import math

i = 0
while i <= 0:
    l[i] = pow.l[i]
    print("l[i]", end=" ")
    i += 1
return l[i]
```

### Prints squared values instead of returning the transformed list

- Cluster frequency: `3/171` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `3/171` (`1.8%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `8c72b50b479647a1babde4c3e7d10bd8`, summary `Wrong Answer`, score `0`, vector `000`

```python
import math

l = int


def k_the(a):
    a == [l**2]
    return a

    def is_equal(S):
        S = (reversed_square(l), k_the(a))
        print(S)
```

### Runtime RecursionError

- Cluster frequency: `3/171` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `3/171` (`1.8%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `539ee244dbd241fdb69f4f375d982989`, summary `Runtime Error`, score `0`, vector `000`

```python
list = [2, 3, 4, 5, 6]
reversed_squares([2, 3, 4, 5, 6])
```

### Runtime IndexError

- Cluster frequency: `3/171` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `3/171` (`1.8%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `a2a4a9f57a654579bd01bd3f6584e955`, summary `Runtime Error`, score `0`, vector `000`

```python
m = []
a = l[0] ** 2
b = l[1] ** 2
c = l[2] ** 2
d = l[3] ** 2
e = l[4] ** 2
m.append(e)
m.append(d)
m.append(c)
m.append(b)
m.append(a)
return m
```

### Runtime TypeError from misusing `.reverse()` result / in-place reverse API

- Cluster frequency: `2/171` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `2/171` (`1.2%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `4fc370c459384de3ad74d7922d05cf43`, summary `Runtime Error`, score `0`, vector `000`

```python
if len(l) == 0:
    return l
new_list = [i * i for i in l.reverse()]
return new_list
```

### Returns from inside the build loop, producing only the first squared/reversed element

- Cluster frequency: `2/171` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `2/171` (`1.2%`)
- Dominant private-case vectors: `000` x1, `010` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `cd812a63afa54341aa24353f49023ffa`, summary `Wrong Answer`, score `33`, vector `010`

```python
    ...
    '''

    new_list=[]
    n = len(l)
    for i in range(-1,-n)

    new_list.append(l[-1]*l[-1])
    new_list.append(l[-2])

    '''
    new_list=[]
    n = len(l)
    if(n==5):
        for i in  [-1,-2,-3,-4,-5]:
             new_list.append(l[i]*l[i])
    if(n==2):
        for i in [-1,-2]:
# ...
```

### Runtime AttributeError from wrong list method/attribute usage

- Cluster frequency: `2/171` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `2/171` (`1.2%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `be916a0787be4d9d8d77d763e5649c40`, summary `Runtime Error`, score `0`, vector `000`

```python
new_list = []
for i in range(len(l)):
    new_list.appends(l[i] ** 2)
new_list = new_list[::-1]
return new_list
"""
new_list =[]
for i in l:
    new_list.appends(i**2)
new_list = new_list[::-1]
return new_list
"""
```

### Uses in-place `.reverse()` incorrectly (returns/mutates list without producing squared reversed result)

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `2d505127c8fe42bcbf73a114ba3d8ce2`, summary `Wrong Answer`, score `0`, vector `000`

```python
new_l = []
new_2 = []
l1 = []
for num in l:
    squares = num**2
    l1.append(squares)
    new_l = l1.reverse()
return l1
```

### Attempts to square values, but ultimately returns only the reversed list (squares are not stored)

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `335f83dfe0424e30b628dbe794172c01`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
new_list = l[::-1]
for i in new_list:
    new_list = i**2
return new_list
```

### Returns only one squared value wrapped in a list instead of the full reversed-squares list

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `3b858e1e349a4384ae896b3b68993ea8`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = len(l)
i = n
for i in range(n):
    new_list = l[i] * l[i]
    i -= 1
return [new_list]
```

### Partially correct list transformation (reverse-vs-sort order mistake on specific test groups)

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `43c601b8441f4feb88918267d1f17335`, summary `Wrong Answer`, score `33`, vector `001`

```python
for i in range(len(l)):
    l[i] *= l[i]
return l[: len(l) + 2]
```

### Runtime IndexError from invalid index while iterating transformed list

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `53ab1ed2ff82497197e849ebbe59ff59`, summary `Runtime Error`, score `0`, vector `000`

```python
list1 = l[-1]
list2 = l[-2]
list3 = l[-3]
list4 = l[-4]
list5 = l[-5]
return [list1**2, list2**2, list3**2, list4**2, list5**2]
```

### Squares only the first two elements (length-specific partial implementation)

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `b82e43893a9443ab814bc12dfc8ac620`, summary `Wrong Answer`, score `0`, vector `000`

```python
a = []
for i in range(0, 2):
    b = l[i] ** 2
    a.append(b)
a.reverse()
return a
```

### Squares index/range values instead of squaring the list elements

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `bd70f63de5fa463bbcbfe4b93d9f39aa`, summary `Wrong Answer`, score `0`, vector `000`

```python
squares = [x**2 for x in range(1, len(l) + 1)]
reversed_squares = squares[::-1]
return reversed_squares
...
```

### Sorts values instead of reversing the input order before squaring

- Cluster frequency: `1/171` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/17`: `1/171` (`0.6%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/17`, Student ID `fade59fa57ee40ad92e6204000f1b835`, summary `Wrong Answer`, score `33`, vector `100`

```python
new_list = []
for elem in l:
    sq = elem**2
    new_list.append(sq)
    new_list.sort()
return new_list
```
