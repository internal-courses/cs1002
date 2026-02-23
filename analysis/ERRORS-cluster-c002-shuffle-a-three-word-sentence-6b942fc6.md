# Error Patterns: Cluster C002 (`Shuffle a Three Word Sentence`)

## Cluster Summary

- Cluster ID: `C002`
- Cluster title: `Shuffle a Three Word Sentence`
- Cluster file (this file): `analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md`
- Variants in cluster: `4`
- Total final submitters across variants: `518`
- Total non-full final submissions across variants: `212`
- Canonical variant (by submissions): `ns_25t3_py13_1/7`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py13_1/7` (canonical) | 518 | 212 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py13_1/7.json`
- Other variants in cluster:
  - `problems/ns_25t1_py22_1/6.json`
  - `problems/ns_25t1_py22_2/6.json`
  - `problems/ns_25t3_py13_2/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `518`
- Full pass: `306`
- Non-full final submissions: `212`
- Parseable non-full (logic/runtime focus): `169`
- Non-parseable non-full: `43`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t1_py22_1/6` | 0 | 0 | 0 | 0 | 0 |
| `ns_25t1_py22_2/6` | 0 | 0 | 0 | 0 | 0 |
| `ns_25t3_py13_1/7` | 518 | 306 | 212 | 169 | 43 |
| `ns_25t3_py13_2/7` | 0 | 0 | 0 | 0 | 0 |

## Private Case Structure

- Private case 1: three unseen sentences using the same three permutation orders as public examples (`(0,2,1)`, `(2,1,0)`, `(1,0,2)`)
- Private case 2: introduces cyclic permutations (`(2,0,1)`, `(1,2,0)`) to catch inverse-permutation and public-order-only logic
- Private case 3: includes identity order `(0,1,2)` plus repeated unseen/public permutations to verify general tuple-driven shuffling

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t1_py22_1/6` | `ns_25t1_py22_2/6` | `ns_25t3_py13_1/7` | `ns_25t3_py13_2/7` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Hard-codes public sample outputs/sentences instead of using the provided `order` tuple generically | 72 | 34.0% | 0 | 0 | 72 | 0 |
| Syntax / non-parseable final submission | 43 | 20.3% | 0 | 0 | 43 | 0 |
| No return / implicit `None` | 22 | 10.4% | 0 | 0 | 22 | 0 |
| Runtime TypeError | 20 | 9.4% | 0 | 0 | 20 | 0 |
| Runtime NameError | 13 | 6.1% | 0 | 0 | 13 | 0 |
| Joins shuffled words without spaces (`''.join(...)`) instead of returning a space-separated sentence | 11 | 5.2% | 0 | 0 | 11 | 0 |
| Incorrect word-order reconstruction or output formatting in the 3-word shuffle task | 5 | 2.4% | 0 | 0 | 5 | 0 |
| Runtime IndexError | 5 | 2.4% | 0 | 0 | 5 | 0 |
| TypeError while assembling output string (mixes tuple indices/ints with string concatenation) | 3 | 1.4% | 0 | 0 | 3 | 0 |
| Returns the original sentence unchanged (ignores the `order` tuple) | 3 | 1.4% | 0 | 0 | 3 | 0 |
| Runtime RecursionError | 3 | 1.4% | 0 | 0 | 3 | 0 |
| Runtime ValueError | 2 | 0.9% | 0 | 0 | 2 | 0 |
| Runtime error (parseable final submission) | 2 | 0.9% | 0 | 0 | 2 | 0 |
| Runtime AttributeError | 2 | 0.9% | 0 | 0 | 2 | 0 |
| Permutation-order bug: code works for self-inverse/public orders but fails unseen cyclic permutations | 1 | 0.5% | 0 | 0 | 1 | 0 |
| Defines the wrong function name (`shuffle_sentence_order`), so evaluator cannot call `shuffle_sentence` | 1 | 0.5% | 0 | 0 | 1 | 0 |
| Applies the permutation in reverse (`out[order[i]] = words[i]`) instead of selecting `words[order[i]]` | 1 | 0.5% | 0 | 0 | 1 | 0 |
| Reads `input()` inside function-type question (EOF under evaluator `shuffle_sentence(...)` calls) | 1 | 0.5% | 0 | 0 | 1 | 0 |
| Copies `is_equal(shuffle_sentence(...))` tests into the function and triggers recursive self-calls | 1 | 0.5% | 0 | 0 | 1 | 0 |
| Handles only the public permutation tuples and misses unseen orders like `(2,0,1)` / `(1,2,0)` | 1 | 0.5% | 0 | 0 | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/212` (`0.0%`)

### Hard-codes public sample outputs/sentences instead of using the provided `order` tuple generically

- Cluster frequency: `72/212` (`34.0%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `72/212` (`34.0%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x60, `100` x12
- Score distribution (top): `0.0` x60, `33.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `78befc829f0e4b6880a8b58d86be50db`, summary `Wrong Answer`, score `33`, vector `100`

```python
    l=sentence.split()
    x=[]
    for z in order:
        x.append(z)
    k=[0,0,0]
    for a in range(len(x)):
        k[x[a]]=l[a]
    return(f"{k[0]} {k[1]} {k[2]}")
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `43/212` (`20.3%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `43/212` (`20.3%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x43
- Score distribution (top): `0.0` x43
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `8b4f46826d8b4044851a22200d86bd66`, summary `Runtime Error`, score `0`, vector `000`

```python
def shuffle_sentence(sentence, order):
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
        'apple orange banana'
        >>> shuffle_sentence('cat dog mouse', (2, 1, 0))
        'mouse dog cat'
    """

# ...
```

### No return / implicit `None`

- Cluster frequency: `22/212` (`10.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `22/212` (`10.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x22
- Score distribution (top): `0.0` x22
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `c9a40172eb7044729314735706b98251`, summary `Wrong Answer`, score `0`, vector `000`

```python
def shuffle_sentence(sentence, order):
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
        'apple orange banana'
        >>> shuffle_sentence('cat dog mouse', (2, 1, 0))
        'mouse dog cat'
    """
print("mouse dog cat")
```

### Runtime TypeError

- Cluster frequency: `20/212` (`9.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `20/212` (`9.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x20
- Score distribution (top): `0.0` x20
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `f4c32610a43446eca3b1ca46db4d5e1f`, summary `Runtime Error`, score `0`, vector `000`

```python
def shuffle_sentence(sentence, order):
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
        'apple orange banana'
        >>> shuffle_sentence('cat dog mouse', (2, 1, 0))
        'mouse dog cat'
    """
import random
# ...
```

### Runtime NameError

- Cluster frequency: `13/212` (`6.1%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `13/212` (`6.1%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `a718ee744e1049649315ced45408a906`, summary `Runtime Error`, score `0`, vector `000`

```python
    before_shuffle(sentence, order)
    return first
    shuffle_sentence.sorted(sentence, order)
    return (shuffle_sentence)
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
        'apple orange banana'
        >>> shuffle_sentence('cat dog mouse', (2, 1, 0))
# ...
```

### Joins shuffled words without spaces (`''.join(...)`) instead of returning a space-separated sentence

- Cluster frequency: `11/212` (`5.2%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `11/212` (`5.2%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x7, `000` x4
- Score distribution (top): `33.0` x7, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `f44308675c054bc498eaf1a66cd5a948`, summary `Wrong Answer`, score `33`, vector `100`

```python
    map = {}
    words = sentence.split(' ')
    for i in range(len(words)):
        word = words[i]
        new_idx = order[i]
        map[new_idx] = word
    suffled_lst = []
    output = []
    for key, val in map.items():
        output.append([key, val])
    output.sort()
    return ' '.join([val for key, val in output])
```

### Incorrect word-order reconstruction or output formatting in the 3-word shuffle task

- Cluster frequency: `5/212` (`2.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `5/212` (`2.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `04eeb78d433849308f2bd7c40ea46f13`, summary `Wrong Answer`, score `0`, vector `000`

```python
    L=sentence.split()
    N=""
    for i in (order):
        if order[int(i)]==0:
            N+L[0]
        if order[int(i)]==1:
            N+L[1]
        if order[int(i)]==2:
            N+L[2]
    return N
```

### Runtime IndexError

- Cluster frequency: `5/212` (`2.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `5/212` (`2.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `44d49526562943c9a1dcbc2279fc4a2d`, summary `Runtime Error`, score `0`, vector `000`

```python
    ord=" "
    for i in range(0,len(sentence)):
        for j in range(0,len(sentence)):
            for k in range(0,len(sentence)):
                if((i,j,k)==order):
                    print(ord[i],"",ord[j],"",ord[k])
    return ord
```

### TypeError while assembling output string (mixes tuple indices/ints with string concatenation)

- Cluster frequency: `3/212` (`1.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `3/212` (`1.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `0af4af464b3345bc80496b47bb14e7f2`, summary `Runtime Error`, score `0`, vector `000`

```python
    words = sentence.split()
    new = ""
    if len(words) != len(order):
        return False
    else:
        words[0],words[1],words[2] = order[0],order[1],order[2]
        new+= words
    return new
```

### Returns the original sentence unchanged (ignores the `order` tuple)

- Cluster frequency: `3/212` (`1.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `3/212` (`1.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `b1765dfcdb194e0fb4b5856f46a7ba8e`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    for i in sentence:
        if order == (0,2,1):
            sentence = 'apple orange banana'
        elif order == (2, 1, 0):
            sentence = 'mouse dog cat'
        else:
            sentence = 'yellow red green'
    return sentence
```

### Runtime RecursionError

- Cluster frequency: `3/212` (`1.4%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `3/212` (`1.4%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `652d5f13745a4ca8bc6475925d42f7d8`, summary `Runtime Error`, score `0`, vector `000`

```python
    sentence = "papaya orange banana"
    order = (2, 1, 0)
    suffle = shuffle_sentence("papaya orange banana", (2, 1, 0))
    return (shuffle)
```

### Runtime ValueError

- Cluster frequency: `2/212` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `2/212` (`0.9%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `893505d5e44746be87b9a83d00ff6476`, summary `Runtime Error`, score `0`, vector `000`

```python
    words = sentence.split("")
    shuffled = [words[i]for i in order]
    return"".join(shuffled)
    ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/212` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `2/212` (`0.9%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `8237423b47124c07b3fb32cd970cf424`, summary `Runtime Error`, score `0`, vector `000`

```python
    sentence = ['first word', 'second word', 'third word']
    a,b,c = 0,0,0
    tuple_order = i(a,b,c)
    for i in range (0,2):
        sentence[i] = sentence [a]
    return (sentence)
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
# ...
```

### Runtime AttributeError

- Cluster frequency: `2/212` (`0.9%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `2/212` (`0.9%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `9dce5080b1744dee840e28f4b3df698c`, summary `Runtime Error`, score `0`, vector `000`

```python
    index[i] = order.sorted()
    sentence = index[i]
```

### Permutation-order bug: code works for self-inverse/public orders but fails unseen cyclic permutations

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `10b0cb7c7197450487ca739e953d0986`, summary `Wrong Answer`, score `33`, vector `100`

```python
    sentence = sentence.split(' ')
    x,y,z = sentence[0],sentence[1],sentence[2]
    if order == (0,2,1):
        s = str(x)+' '+str(z)+' '+str(y)
    elif order == (2,1,0):
        s = str(z)+' '+str(y)+' '+str(x)
    else:
        s = str(y)+' '+str(x)+' '+str(z)
    return (s)
```

### Defines the wrong function name (`shuffle_sentence_order`), so evaluator cannot call `shuffle_sentence`

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `13eae9bca8504c51a2a6e7b4b0e3c619`, summary `Runtime Error`, score `0`, vector `000`

```python
   words = sentence.split()
   if len(words)!=3:
       raise ValueError("the sentence must contain exactly three wors.")
   if sorted(list(order))!=[0,1,2]:
       raise ValueError("the order tuple must be purmutation of (0,1,2)")
   shuffled_words=[words[order[0]],words[order[1]],words[2]]
   shuffled_sentence=" ".join(shuffled_words)
   return shuffled_sentence
```

### Applies the permutation in reverse (`out[order[i]] = words[i]`) instead of selecting `words[order[i]]`

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `76be1a416db8429ab3b7cb5d19b21ec7`, summary `Wrong Answer`, score `33`, vector `100`

```python
    words=sentence
    words=words.split()
    relist=["mouse","orange","green"]
    restr=""
    relist[order[0]]=words[0]
    relist[order[1]]=words[1]
    relist[order[2]]=words[2]
    restr=relist[0]+" "+relist[1]+" "+relist[2]
    return restr
```

### Reads `input()` inside function-type question (EOF under evaluator `shuffle_sentence(...)` calls)

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `770bd13a062b4077bfd3d06261339bd4`, summary `Runtime Error`, score `0`, vector `000`

```python
    sentence = str()
    order = input()
    return(sentence)
```

### Copies `is_equal(shuffle_sentence(...))` tests into the function and triggers recursive self-calls

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `983c56a73fa247f4a0b243721735a13a`, summary `Runtime Error`, score `0`, vector `000`

```python
    is_equal(shuffle_sentence('apple banana orange',(0,2,1)),'apple orange banana')
    print("shuffled sentence",shuffle_sentence)
    is_equal(shuffle_sentence('cat dog mouse',(2,1,0)), 'mouse dog cat')
    print("shuffled sentence",shuffle_sentence)
    """
    Shuffles the words of a three-word sentence according to the specified order.

    Args:
        sentence (str): The three-word sentence.
        order (tuple): The shuffling order.

    Returns:
        str: The shuffled sentence.

    Examples:
        >>> shuffle_sentence('apple banana orange', (0, 2, 1))
        'apple orange banana'
        >>> shuffle_sentence('cat dog mouse', (2, 1, 0))
# ...
```

### Handles only the public permutation tuples and misses unseen orders like `(2,0,1)` / `(1,2,0)`

- Cluster frequency: `1/212` (`0.5%`)
- Variant frequencies:
  - `ns_25t1_py22_1/6`: `0/0` (`0.0%`)
  - `ns_25t1_py22_2/6`: `0/0` (`0.0%`)
  - `ns_25t3_py13_1/7`: `1/212` (`0.5%`)
  - `ns_25t3_py13_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/7`, Student ID `ee4efeca14164d62a39ccf53915a749d`, summary `Wrong Answer`, score `33`, vector `100`

```python
    words=sentence.split()
    for word in words:
        if order==(0,2,1):
            return words[0]+" "+words[2]+" "+words[1]
        elif order==(2,1,0):
            return words[2]+" "+words[1]+" "+words[0]
        elif order==(1,0,2):
            return words[1]+" "+words[0]+" "+words[2]
```
