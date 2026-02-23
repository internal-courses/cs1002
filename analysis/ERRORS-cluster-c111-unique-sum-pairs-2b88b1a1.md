# Error Patterns: Cluster C111 (`Unique Sum Pairs`)

## Cluster Summary

- Cluster ID: `C111`
- Cluster title: `Unique Sum Pairs`
- Cluster file (this file): `analysis/ERRORS-cluster-c111-unique-sum-pairs-2b88b1a1.md`
- Variants in cluster: `1`
- Total final submitters across variants: `336`
- Total non-full final submissions across variants: `262`
- Canonical variant (by submissions): `ns_25t2_py11_1/9`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py11_1/9` (canonical) | 336 | 262 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py11_1/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `336`
- Full pass: `74`
- Non-full final submissions: `262`
- Parseable non-full (logic/runtime focus): `205`
- Non-parseable non-full: `57`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py11_1/9` | 336 | 74 | 262 | 205 | 57 |

## Private Case Structure

- Private case 1: duplicate-value pairs and repeated-number cases (e.g., `(10,10)` only when the value appears at least twice)
- Private case 2: `(x, x)` duplicate-count edge cases (`[2,0,-1], k=0` should not return `(0,0)`) plus no-solution cases
- Private case 3: negative-number pairs and unique tuple ordering (`(-5,5)`, `(-3,3)`) without reversed duplicates

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py11_1/9` |
| --- | ---: | ---: | ---: |
| Hard-codes the public sample pair set (`{(1,3), (2,2)}`) / sample inputs instead of general pair generation | 78 | 29.8% | 78 |
| Syntax / non-parseable final submission | 57 | 21.8% | 57 |
| Runtime TypeError | 25 | 9.5% | 25 |
| Skeleton placeholder `...` left in function | 19 | 7.3% | 19 |
| Returns inside loop before completing full check/computation | 19 | 7.3% | 19 |
| Runtime NameError | 14 | 5.3% | 14 |
| No return / implicit `None` | 11 | 4.2% | 11 |
| Runtime IndexError | 10 | 3.8% | 10 |
| Runtime error (parseable final submission) | 7 | 2.7% | 7 |
| Runtime AttributeError | 7 | 2.7% | 7 |
| Incorrect unique-sum-pair logic (returns too early, wrong return type, or non-general pair construction) | 5 | 1.9% | 5 |
| Nested-loop pair generation does not correctly enforce unique-pair semantics / duplicate handling | 3 | 1.1% | 3 |
| Runtime ValueError | 2 | 0.8% | 2 |
| Returns a single tuple pair (`a, b`) instead of the required set of all unique pairs | 1 | 0.4% | 1 |
| Builds all pair tuples and removes reversed duplicates while iterating the same list (mutation skips cases) | 1 | 0.4% | 1 |
| Accumulates pairs in a list then converts to `set`, but duplicate/order logic is still incorrect | 1 | 0.4% | 1 |
| Single-pass complement logic stores `target` instead of `num` (`seen.add(target)`), so valid pairs are missed | 1 | 0.4% | 1 |
| Counter-based solution nests the `num < complement` branch under `num == complement`, so distinct-value pairs are skipped | 1 | 0.4% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/262` (`0.0%`)

### Hard-codes the public sample pair set (`{(1,3), (2,2)}`) / sample inputs instead of general pair generation

- Cluster frequency: `78/262` (`29.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `78/262` (`29.8%`)
- Dominant private-case vectors: `000` x48, `100` x13, `010` x11, `001` x4
- Score distribution (top): `0.0` x48, `33.0` x28, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `a35cffa6d9f9451ca9f70db8b73aa790`, summary `Wrong Answer`, score `33`, vector `010`

```python
sum_pairs=set()
for each in nums:
        for i in nums:
            if ((each)+(i))==k:
                if ((each)+(i))==k and nums.count(each)>=2:
                    tuplez=(each,i)
                    sum_pairs.add(tuplez)
                else:
                    non_tuple=(each,i)
return sum_pairs
'''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `57/262` (`21.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `57/262` (`21.8%`)
- Dominant private-case vectors: `000` x57
- Score distribution (top): `0.0` x57
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `1ea14054eb8b4454a52888be1261d68b`, summary `Runtime Error`, score `0`, vector `000`

```python
def card_to_value_tuple(card: str) -> tuple:
    '''Converts the card of format "{rank}{suit}" to value tuple.

    The suit values from low to high:

    - `S` (Spades) - 1
    - `H` (Hearts) - 2
    - `D` (Diamonds) - 3
    - `C` (Clubs) - 4

    The rank values from low to high:

    - `A` (Ace) - 1
    - `2` through `10` - same as the number
    - `J` (Jack) - 11
    - `Q` (Queen) - 12
    - `K` (King) - 13

# ...
```

### Runtime TypeError

- Cluster frequency: `25/262` (`9.5%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `25/262` (`9.5%`)
- Dominant private-case vectors: `000` x24, `010` x1
- Score distribution (top): `0.0` x24, `33.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `3852cae4f6294032b38049f382c7af98`, summary `Runtime Error`, score `33`, vector `010`

```python
def unique_sum_pairs(nums: list, k: int) -> set:
    '''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    {(1, 3), (2, 2)}
    >>> unique_sum_pairs([1, 5, 7, -1, 5], 6)
    {(1, 5), (-1, 7)}

    Args:
        nums (list): A list of integers
        k (int): The target sum to be achieved by pairs

    Returns:
# ...
```

### Skeleton placeholder `...` left in function

- Cluster frequency: `19/262` (`7.3%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `19/262` (`7.3%`)
- Dominant private-case vectors: `000` x19
- Score distribution (top): `0.0` x19
- Interpretation: Template placeholder remains; Python treats `...` as valid syntax, often yielding a wrong-answer `None` path instead of syntax failure.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `0548593c26af4f65a3fcda53cc146987`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

### Returns inside loop before completing full check/computation

- Cluster frequency: `19/262` (`7.3%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `19/262` (`7.3%`)
- Dominant private-case vectors: `000` x19
- Score distribution (top): `0.0` x19
- Interpretation: Control-flow bug: the function returns during iteration before processing all required items/conditions.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `9377390f0c1f4c3597b71a9341d5b8fb`, summary `Wrong Answer`, score `0`, vector `000`

```python
setn = set(nums)
numss = list(setn)
t = ()
setr = set()
for i in range(len(numss)):
        for j in numss:
            sum = int(numss[i]) + int(j)
            if sum == k:
                t = (nums[i],j,)
                if t[::-1] not in setr:
                    setr.add(t)
        return (setr)
return(setr)
'''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.
# ...
```

### Runtime NameError

- Cluster frequency: `14/262` (`5.3%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `14/262` (`5.3%`)
- Dominant private-case vectors: `000` x14
- Score distribution (top): `0.0` x14
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `44b94f124c7d4c119ef86a91ded05c43`, summary `Runtime Error`, score `0`, vector `000`

```python
def unique_sum_pairs(nums: list, k: int) -> set:
    '''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    {(1, 3), (2, 2)}
    >>> unique_sum_pairs([1, 5, 7, -1, 5], 6)
    {(1, 5), (-1, 7)}

    Args:
        nums (list): A list of integers
        k (int): The target sum to be achieved by pairs

    Returns:
# ...
```

### No return / implicit `None`

- Cluster frequency: `11/262` (`4.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `11/262` (`4.2%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `561d7d7092be4d4b8b57bd9d0dbe4320`, summary `Wrong Answer`, score `0`, vector `000`

```python
'''

def unique_sum_pairs(nums: list, k: int) -> set:
    ...
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([3,-6,8,-4,-8], -48)
    {(3,-6), (-4, 48)}
    >>> unique_sum_pairs([2,-4,8,-6,8], 8)
    {(2, 8), (-4,-6)}

    Args:
        nums (list): A list of integers
        k (int): The target sum to be achieved by pairs
# ...
```

### Runtime IndexError

- Cluster frequency: `10/262` (`3.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `10/262` (`3.8%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `5fef6857a2bd4c63905245c165fd266a`, summary `Runtime Error`, score `0`, vector `000`

```python
...
s=set()
eq=0
for i in nums:
        for j in nums:
            if i==j and  nums[i]+nums[j]==k:

                for m in nums:
                    if m==nums[i]:
                        eq+=1
                    if eq >=2:
                        s.add((nums[i],nums[i]))


            elif nums[i]+nums[j]==k:
                s.add((nums[i],nums[j]))
return sorted(s)
```

### Runtime error (parseable final submission)

- Cluster frequency: `7/262` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `7/262` (`2.7%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `38b49e7eeb094babb8d09e0cc823de59`, summary `Runtime Error`, score `0`, vector `000`

```python
for a in nums:
        for b in nums:
            if(a<=b):
                if(a+b==k):
                    m=a,b
            return(tuple(m))
'''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    {(1, 3), (2, 2)}
    >>> unique_sum_pairs([1, 5, 7, -1, 5], 6)
    {(1, 5), (-1, 7)}

# ...
```

### Runtime AttributeError

- Cluster frequency: `7/262` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `7/262` (`2.7%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `12dae22fcc254856ad46ef0042be6366`, summary `Runtime Error`, score `0`, vector `000`

```python
elements= nums.slice(',')
print('elements')
'''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    {(1, 3), (2, 2)}
    >>> unique_sum_pairs([1, 5, 7, -1, 5], 6)
    {(1, 5), (-1, 7)}

    Args:
        nums (list): A list of integers
        k (int): The target sum to be achieved by pairs

# ...
```

### Incorrect unique-sum-pair logic (returns too early, wrong return type, or non-general pair construction)

- Cluster frequency: `5/262` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `5/262` (`1.9%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `ee888736ced84c81aedf64c579c4e99b`, summary `Wrong Answer`, score `0`, vector `000`

```python
count = {}
for num in nums:
        if num in count:
            count[num] += 1
        else:
            count[num] = 1
pair = set()
for num in count:
        if k - num in count and (num != k - num and count [num] > 1):
           pair = set(sorted((num, k - num)))
return pair
```

### Nested-loop pair generation does not correctly enforce unique-pair semantics / duplicate handling

- Cluster frequency: `3/262` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `3/262` (`1.1%`)
- Dominant private-case vectors: `000` x2, `100` x1
- Score distribution (top): `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `b782e810dd3c49eba1e479e9eb5c168b`, summary `Wrong Answer`, score `33`, vector `100`

```python
newlist = []
for i in nums:
        for j in nums:
            if i+j==k and i<j:
                newlist.append((i,j))
            elif i+j==k and i==j:
                newlist.append((i,j))
                break
            else:
                pass
return set(newlist)
...
```

### Runtime ValueError

- Cluster frequency: `2/262` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `2/262` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `781607694e0542eb9a642978f9061315`, summary `Runtime Error`, score `0`, vector `000`

```python
tu1=set()
for i in nums:
        for j in nums:
            if i+j== k:
                tu1.add((i,j))
                nums.remove(i)
                nums.remove(j)
                break
return tu1
'''
    Given a list of integers and an integer k, return a set of unique tuples
    where each tuple contains two different elements that sum up to k.

    Same number can only be used as a pair if it appears atleast twice in the list.

    Examples:
    >>> unique_sum_pairs([1, 2, 3, 2, 1], 4)
    {(1, 3), (2, 2)}
# ...
```

### Returns a single tuple pair (`a, b`) instead of the required set of all unique pairs

- Cluster frequency: `1/262` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `1/262` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `094b5e3b86fd4c2c92fab53a448ce05c`, summary `Wrong Answer`, score `0`, vector `000`

```python
b = nums.copy()
c = 0
d=0
for i in nums:
        for j in b:
            if i + j == k:
                c= i
                d= j
return c,d
```

### Builds all pair tuples and removes reversed duplicates while iterating the same list (mutation skips cases)

- Cluster frequency: `1/262` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `1/262` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `24da594976024ad68e3659fe8169bc11`, summary `Wrong Answer`, score `0`, vector `000`

```python
l=[]
z=list(set(nums))
for i in z:
        for j in z:
            if(i+j==k):
                u=[]
                u.append(i)
                u.append(j)
                l.append(tuple(u))
d=list(set(l))
for i in d:
        for j in d:
            if(i[0]==j[1] and i[1]==j[0]):
                if(i[0]!=j[0] and i[1]!=j[1]):
                    d.remove(j)
return set(d)
```

### Accumulates pairs in a list then converts to `set`, but duplicate/order logic is still incorrect

- Cluster frequency: `1/262` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `1/262` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `257da0e7aa144a7bb18ea6edbe5e05d3`, summary `Wrong Answer`, score `0`, vector `000`

```python
complement = {}
answers = []
for num in nums:
        if num not in complement.values():
            complement[num] = k - num
        # print(num, k-num)
        answers.append(tuple(sorted([num, k - num])))
return set(answers)
```

### Single-pass complement logic stores `target` instead of `num` (`seen.add(target)`), so valid pairs are missed

- Cluster frequency: `1/262` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `1/262` (`0.4%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `2fc907d81fda439886322c108fa5f4e5`, summary `Wrong Answer`, score `33`, vector `010`

```python
seen = set()
used = set()
result = set()
for num in nums:
        target = k - num
        if target in seen and (target not in used and  num not in used):
            result.add(tuple(sorted((num , target))))
            used.add(num)
            used.add(target)
        seen.add(target)
return result
```

### Counter-based solution nests the `num < complement` branch under `num == complement`, so distinct-value pairs are skipped

- Cluster frequency: `1/262` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/9`: `1/262` (`0.4%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/9`, Student ID `3d9f954f5e024097b29b53f440205c56`, summary `Wrong Answer`, score `33`, vector `010`

```python
count=Counter(nums)
result=set()
for num in count:
     complement = k-num
     if complement in count:
         if num==complement:
             if count[num]>=2:
                 result.add((num,num))
             elif num<complement:
                 result.add((num,complement))
return result
```
