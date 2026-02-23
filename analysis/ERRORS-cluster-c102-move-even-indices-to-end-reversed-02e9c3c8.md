# Error Patterns: Cluster C102 (`Move Even Indices to End (Reversed)`)

## Cluster Summary

- Cluster ID: `C102`
- Cluster title: `Move Even Indices to End (Reversed)`
- Cluster file (this file): `analysis/ERRORS-cluster-c102-move-even-indices-to-end-reversed-02e9c3c8.md`
- Variants in cluster: `1`
- Total final submitters across variants: `464`
- Total non-full final submissions across variants: `189`
- Canonical variant (by submissions): `ns_25t3_py11/9`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py11/9` (canonical) | 464 | 189 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py11/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `464`
- Full pass: `275`
- Non-full final submissions: `189`
- Parseable non-full (logic/runtime focus): `137`
- Non-parseable non-full: `52`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py11/9` | 464 | 275 | 189 | 137 | 52 |

## Private Case Structure

- Private case 1: small tuple edge cases (`len=1`, `len=2`) to verify exact slicing/concatenation semantics
- Private case 2: repeated-value tuple (`('x','y','z')*3`) to catch value-based `.index(...)` / duplicate-removal bugs
- Private case 3: long repeated pattern tuple (`tuple('qwerty')*5`) to catch off-by-one slice and ordering mistakes

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py11/9` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 52 | 27.5% | 52 |
| Hard-codes the public example tuple/output shape instead of processing arbitrary tuples | 50 | 26.5% | 50 |
| No return / implicit `None` | 29 | 15.3% | 29 |
| Runtime TypeError from mixing tuple/list/scalar operations while rebuilding the tuple | 24 | 12.7% | 24 |
| Runtime NameError from undefined temporary lists/indices in even/odd split logic | 13 | 6.9% | 13 |
| Runtime AttributeError | 6 | 3.2% | 6 |
| Fixed-position indexing assumes longer tuples and fails on hidden small-tuple or slice-edge cases | 5 | 2.6% | 5 |
| Incorrect tuple slicing/reconstruction logic for moving even indices to the end in reversed order | 4 | 2.1% | 4 |
| Runtime error (parseable final submission) | 2 | 1.1% | 2 |
| Runtime RecursionError | 2 | 1.1% | 2 |
| Uses non-existent tuple/string reverse APIs (`t.reversed()`) or wrong reverse method semantics | 1 | 0.5% | 1 |
| Runtime ValueError | 1 | 0.5% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/189` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `52/189` (`27.5%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `52/189` (`27.5%`)
- Dominant private-case vectors: `000` x52
- Score distribution (top): `0.0` x52
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `65128236fe924d7e9e1ad940be203f6d`, summary `Runtime Error`, score `0`, vector `000`

```python
def move_even_indices_to_end_reversed(t):
    '''
    Given a tuple `t`, move all elements at even indices to the end
    in reversed order, while keeping odd-indexed elements as they are.

    Example:
    >>> t = (10, 20, 30, 40, 50)
    >>> move_even_indices_to_end_reversed(t)
    (20, 40, 50, 30, 10)

    Args:
        t (tuple): The input tuple.

    Returns:
        tuple: A new tuple with odd-indexed elements followed by reversed even-indexed elements.
    '''
   odd_indexed_elements = ' '
   even_indexed_elements = ' '
# ...
```

### Hard-codes the public example tuple/output shape instead of processing arbitrary tuples

- Cluster frequency: `50/189` (`26.5%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `50/189` (`26.5%`)
- Dominant private-case vectors: `000` x27, `100` x9, `010` x8, `101` x5
- Score distribution (top): `0.0` x27, `33.0` x17, `67.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `fd04d04076164d0e9e60afc5d098ecd3`, summary `Wrong Answer`, score `0`, vector `000`

```python
    u=()
    index=0
    for each in t:
        if index%2==0:
            u+=t
        index+=1
    index =0
    for each in t:
        if index%2!=0:
            u+=t
        index+=1
    return (20,40,50,30,10)
    '''
    Given a tuple `t`, move all elements at even indices to the end
    in reversed order, while keeping odd-indexed elements as they are.

    Example:
    >>> t = (10, 20, 30, 40, 50)
# ...
```

### No return / implicit `None`

- Cluster frequency: `29/189` (`15.3%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `29/189` (`15.3%`)
- Dominant private-case vectors: `000` x29
- Score distribution (top): `0.0` x29
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `ff340ce3ad0547758ce90f2f2c1bcf20`, summary `Wrong Answer`, score `0`, vector `000`

```python
def move_even_indices_to_end_reversed(t):
    '''
    Given a tuple `t`, move all elements at even indices to the end
    in reversed order, while keeping odd-indexed elements as they are.

    Example:
    >>> t = (10, 20, 30, 40, 50)
    >>> move_even_indices_to_end_reversed(t)
    (20, 40, 50, 30, 10)

    Args:
        t (tuple): The input tuple.

    Returns:
        tuple: A new tuple with odd-indexed elements followed by reversed even-indexed elements.
    '''

print("('b','d','f','e','c','a')")
```

### Runtime TypeError from mixing tuple/list/scalar operations while rebuilding the tuple

- Cluster frequency: `24/189` (`12.7%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `24/189` (`12.7%`)
- Dominant private-case vectors: `000` x22, `011` x2
- Score distribution (top): `0.0` x22, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `0a106e4bebfd4c13a901cfac5ebc6336`, summary `Runtime Error`, score `0`, vector `000`

```python
    '''even_index = (t[0],t[2],t[4])
    re_even_index = (even_index.reversed)
    odd_index = (t[1],t[3])
    final_output = f"{odd_index} +{re_even_index} "
    return final_output'''
    for n in t.index:
        if n%2 == 0:
            even_index += n
            even_index = even_index.reversed
        else:
            odd_index += n
    return (f"{odd_index} + {even_index}")
```

### Runtime NameError from undefined temporary lists/indices in even/odd split logic

- Cluster frequency: `13/189` (`6.9%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `13/189` (`6.9%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `e9b8132b4db646f9bc4f88d5e385752a`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    arr=list(t)
    odd_indexed = [arr[i] for i in range (len(arr)) if i % 2 !=0]
    even_indexed = [arr[i] for i in range (len(arr)) if i % 2 == 0]
    result = odd_indexed +list(reversed(even-indexed))
    return tuple(result)
```

### Runtime AttributeError

- Cluster frequency: `6/189` (`3.2%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `6/189` (`3.2%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `cdfa1171a8f4417c9f7f0497bb97ce38`, summary `Runtime Error`, score `0`, vector `000`

```python
    t2=()
    for j in range(len(t)-1):

        for i in range(len(t)-1):
            if i//2 != 0:
                t2.append(t[i])
        for i in range(len(t)-1):
            if i//2 == 0:
                t2.append(t[i])
    return t2
```

### Fixed-position indexing assumes longer tuples and fails on hidden small-tuple or slice-edge cases

- Cluster frequency: `5/189` (`2.6%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `5/189` (`2.6%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `8cfe5b38ff4b403491556f70518474a7`, summary `Runtime Error`, score `0`, vector `000`

```python
    l = list(t)
    length = len(l)
    l1 = []
    l2 = []
    for i in range(length):
        if(i%2 == 0):
            l1.append(l[i])
        else:
            l2.append(l[i])
    lth = len(l1)
    l3 = []
    l4 = []
    for j in range(lth):
        l3[j] = l1[(lth-1)-j]
    l4 = l2 + l3
    t1 = tuple(l4)
    return t1
```

### Incorrect tuple slicing/reconstruction logic for moving even indices to the end in reversed order

- Cluster frequency: `4/189` (`2.1%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `4/189` (`2.1%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `242f6a6bda8d40adb0a6324bf648b44e`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if len(t) == 2:
        return (t[-1], t[0])
    elif len(t) == 3:
        return (t[1], t[2], t[0])
    elif len(t) == 4:
        return (t[1], t[3], t[2], t[0])
    elif len(t) == 5:
        return (t[1], t[3], t[4], t[2], t[0])
    elif len(t) == 6:
        return (t[1], t[3], t[5], t[4], t[2], t[0])
    elif len(t) == 7:
        return (t[1], t[3], t[5], t[6], t[4], t[2], t[0])
    elif len(t) == 8:
        return (t[1], t[3], t[5], t[7], t[6], t[4], t[2], t[0])
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/189` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `2/189` (`1.1%`)
- Dominant private-case vectors: `011` x1, `000` x1
- Score distribution (top): `67.0` x1, `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `172355adc4da493bb9a384955f8221ae`, summary `Runtime Error`, score `67`, vector `011`

```python
    l=list(t)
    l1=[]
    l2=[]
    if l!=[]:
        for i in range(len(l)):
            if i%2!=0:
                l1=l1+[l[i]]
            else:
                l2=l2+[l[i]]
        for j in range(len(l1)):
            l3=l2[::-1]
        l4=l1+l3
        t=tuple(l4)
        return t
    else:
        t=()
        return t
```

### Runtime RecursionError

- Cluster frequency: `2/189` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `2/189` (`1.1%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `36b06d193e214495ac347cdcdd86fb20`, summary `Runtime Error`, score `0`, vector `000`

```python
    t = (10, 20, 30, 40, 50)
    move_even_indices_to_end_reversed(t)
```

### Uses non-existent tuple/string reverse APIs (`t.reversed()`) or wrong reverse method semantics

- Cluster frequency: `1/189` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `1/189` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `008f24528b0a4f4cb589dc4838be9a08`, summary `Runtime Error`, score `0`, vector `000`

```python
    t.reversed()
```

### Runtime ValueError

- Cluster frequency: `1/189` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py11/9`: `1/189` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py11/9`, Student ID `bcdce38be417426d8c7e7d9cf15136af`, summary `Runtime Error`, score `0`, vector `000`

```python
    z = list(t)
    b = []
    for i in range(len(z)):
        if i%2==0:
            b.remove(z[i])
    return b
```
