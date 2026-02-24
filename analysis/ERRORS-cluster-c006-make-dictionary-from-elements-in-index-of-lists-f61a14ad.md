# Error Patterns: Cluster C006 (`Make dictionary from elements in index of lists`)

## Cluster Summary

- Cluster ID: `C006`
- Cluster title: `Make dictionary from elements in index of lists`
- Cluster file (this file): `analysis/ERRORS-cluster-c006-make-dictionary-from-elements-in-index-of-lists-f61a14ad.md`
- Variants in cluster: `3`
- Total final submitters across variants: `474`
- Total non-full final submissions across variants: `124`
- Canonical variant (by submissions): `ns_25t2_py12_1/7`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py12_1/7` (canonical) |              474 |      124 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py12_1/7.json`
- Other variants in cluster:
  - `problems/ns_25t1_py11_1/4.json`
  - `problems/ns_25t1_py_15_exe/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `474`
- Full pass: `350`
- Non-full final submissions: `124`
- Parseable non-full (logic/runtime focus): `91`
- Non-parseable non-full: `33`

Variant-level comparison:

| Variant               | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t1_py11_1/4`    |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t1_py_15_exe/7` |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t2_py12_1/7`    |              474 |       350 |      124 |                 91 |                     33 |

## Private Case Structure

- Private case 1: positive indices with symbol/string keys and values (baseline single-pair extraction)
- Private case 2: includes integer keys and a valid negative index (must support Python negative indexing semantics)

Private-case vectors in this report are 2-character pass/fail strings over the private case groups (e.g., `11` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                        | Cluster count | % of cluster non-full | `ns_25t1_py11_1/4` | `ns_25t1_py_15_exe/7` | `ns_25t2_py12_1/7` |
| -------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: | --------------------: | -----------------: |
| Syntax / non-parseable final submission                                                                        |            33 |                 26.6% |                  0 |                     0 |                 33 |
| Incorrect dictionary construction (ignores `index`, returns wrong shape/type, or uses sample-specific values)  |            26 |                 21.0% |                  0 |                     0 |                 26 |
| No return / implicit `None`                                                                                    |            17 |                 13.7% |                  0 |                     0 |                 17 |
| Builds the dictionary with invalid syntax/types (tuple/set/string formatting instead of `{key: value}`)        |            16 |                 12.9% |                  0 |                     0 |                 16 |
| Negative-index handling bug: solution works for positive indices but treats valid negative indices incorrectly |             9 |                  7.3% |                  0 |                     0 |                  9 |
| Returns the full `dict(zip(keys, values))` instead of a single key-value pair at the given index               |             3 |                  2.4% |                  0 |                     0 |                  3 |
| Runtime RecursionError                                                                                         |             3 |                  2.4% |                  0 |                     0 |                  3 |
| Hard-codes public sample dictionaries instead of using the provided `keys`, `values`, and `index`              |             3 |                  2.4% |                  0 |                     0 |                  3 |
| Runtime NameError                                                                                              |             2 |                  1.6% |                  0 |                     0 |                  2 |
| Treats valid negative indices as out-of-bounds (`0 <= index < ...`) instead of using Python indexing semantics |             2 |                  1.6% |                  0 |                     0 |                  2 |
| Rejects negative indices with a non-negative bounds check (`0 <= index < ...`)                                 |             2 |                  1.6% |                  0 |                     0 |                  2 |
| Runtime ValueError                                                                                             |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Assumes `keys[index]` is always a string (`.strip(...)`), but hidden tests include integer keys                |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Copies evaluator-style self-tests into the function and triggers recursive/self-test failures                  |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Runtime error (parseable final submission)                                                                     |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Runtime KeyError                                                                                               |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Returns the first key-value pair from nested loops, ignoring the requested `index`                             |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Returns a formatted string (`"key, value"`) instead of a dictionary                                            |             1 |                  0.8% |                  0 |                     0 |                  1 |
| Builds a list of per-index dictionaries and returns `l[index]`, which fails hidden negative-index semantics    |             1 |                  0.8% |                  0 |                     0 |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/124` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `33/124` (`26.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `33/124` (`26.6%`)
- Dominant private-case vectors: `00` x33
- Score distribution (top): `0.0` x33
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `3f4c81f04e9844618a552f2131ef06df`, summary `Runtime Error`, score `0`, vector `00`

```python
def make_dict_from_elems_in_index(keys, values, index:int)-> dict:
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
        values (list): The list with the values.
        index (int): An integer

# ...
```

### Incorrect dictionary construction (ignores `index`, returns wrong shape/type, or uses sample-specific values)

- Cluster frequency: `26/124` (`21.0%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `26/124` (`21.0%`)
- Dominant private-case vectors: `00` x26
- Score distribution (top): `0.0` x26
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `8bc7d985cd314cee9c8c8d4a2df21a90`, summary `Wrong Answer`, score `0`, vector `00`

```python
    dict={}
    dict[list1[0]]=list2[0]
    return dict
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
        values (list): The list with the values.
# ...
```

### No return / implicit `None`

- Cluster frequency: `17/124` (`13.7%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `17/124` (`13.7%`)
- Dominant private-case vectors: `00` x17
- Score distribution (top): `0.0` x17
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `146f3dac6aed45458143f7526f807eca`, summary `Wrong Answer`, score `0`, vector `00`

```python
def make_dict_from_elems_in_index(keys, values, index:int)-> dict:
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
        values (list): The list with the values.
        index (int): An integer

# ...
```

### Builds the dictionary with invalid syntax/types (tuple/set/string formatting instead of `{key: value}`)

- Cluster frequency: `16/124` (`12.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `16/124` (`12.9%`)
- Dominant private-case vectors: `00` x16
- Score distribution (top): `0.0` x16
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `28c88101f6f24942abcc8b2b0b20c2a5`, summary `Runtime Error`, score `0`, vector `00`

```python
def make_dict_from_elems_in_index(keys, values, index:int)-> dict:
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
        values (list): The list with the values.
        index (int): An integer

# ...
```

### Negative-index handling bug: solution works for positive indices but treats valid negative indices incorrectly

- Cluster frequency: `9/124` (`7.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `9/124` (`7.3%`)
- Dominant private-case vectors: `10` x9
- Score distribution (top): `50.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `0e2e5f7cb7be4418baca296aa8b8975b`, summary `Wrong Answer`, score `50`, vector `10`

```python
d = dict()
if index >= 0:
    for i in range(len(keys)):
        if i == index:
            d[keys[i]] = values[i]
    return d
if index > 0:
    for i in range(len(keys), -1):
        if i == index:
            d[keys[i]] = vlues[i]
    return d
```

### Returns the full `dict(zip(keys, values))` instead of a single key-value pair at the given index

- Cluster frequency: `3/124` (`2.4%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `3/124` (`2.4%`)
- Dominant private-case vectors: `00` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `15a1c7848d404ce2bc7e9cca246335cc`, summary `Wrong Answer`, score `0`, vector `00`

```python
s = dict(zip(keys, values))
return s
```

### Runtime RecursionError

- Cluster frequency: `3/124` (`2.4%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `3/124` (`2.4%`)
- Dominant private-case vectors: `00` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `946dca1a03ba45acbbba4fee8538cc23`, summary `Runtime Error`, score `0`, vector `00`

```python
k = len(keys)
l = len(values)
i = 0
if k >= l:
    while i <= l:
        return make_dict_from_elems_in_index(keys, values, i)
        i += 1
else:
    while i <= k:
        return make_dict_from_elems_in_index(keys, values, i)
        i += 1
```

### Hard-codes public sample dictionaries instead of using the provided `keys`, `values`, and `index`

- Cluster frequency: `3/124` (`2.4%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `3/124` (`2.4%`)
- Dominant private-case vectors: `00` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `284559937f79444aa795af1e4d633de7`, summary `Wrong Answer`, score `0`, vector `00`

```python
if index == 1:
    return {"age": 25}
if index == 0:
    return {"Country": "India"}
if index == 2:
    return {"city": "New York"}
if index == -3:
    return {"apple": "yellow"}
```

### Runtime NameError

- Cluster frequency: `2/124` (`1.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `2/124` (`1.6%`)
- Dominant private-case vectors: `00` x2
- Score distribution (top): `0.0` x2
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `2b3b47f75c1a4f319f9a51964eebb2d2`, summary `Runtime Error`, score `0`, vector `00`

```python
list1 = ["name", "agecity"]
list2 = ["Alice", 25, "New York"]
is_eqaul(makke_dict_from_elems_in_index(list1, list2, 1), {"age": 25})
is_equal(make_dict_from_elems_in_index(list1, list2, 2), {"city": "New York"})
```

### Treats valid negative indices as out-of-bounds (`0 <= index < ...`) instead of using Python indexing semantics

- Cluster frequency: `2/124` (`1.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `2/124` (`1.6%`)
- Dominant private-case vectors: `10` x2
- Score distribution (top): `50.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `aa1f05d99ace440a958d2dbd6a405e69`, summary `Runtime Error`, score `50`, vector `10`

```python
    if not (0 <= index < len(keys) and 0 <= index < len(values)) :

        raise IndexError("index out of bounds for either keys or value list.")
    selected_key = keys[index]
    selected_value = values[index]
    return {selected_key : selected_value}
```

### Rejects negative indices with a non-negative bounds check (`0 <= index < ...`)

- Cluster frequency: `2/124` (`1.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `2/124` (`1.6%`)
- Dominant private-case vectors: `10` x2
- Score distribution (top): `50.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `a79de7cd3c6b48c986ddd587499cd87e`, summary `Wrong Answer`, score `50`, vector `10`

```python
    if 0 <= index < len(keys) and 0 <= index <len(values) :
        return {keys[index] : values[index]}
    else :
        return {}
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
# ...
```

### Runtime ValueError

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `10658a5ae5f24525b9b4c42425ab6174`, summary `Runtime Error`, score `0`, vector `00`

```python
i = index
ke = keys[i]
val = values[i]
dict1 = dict(f"{ke}")
dict2 = dict(f"{val}")
return f"{dict1, dict2}"
```

### Assumes `keys[index]` is always a string (`.strip(...)`), but hidden tests include integer keys

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `10` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `485dbb37223342cfa0932fd8f2715abc`, summary `Runtime Error`, score `50`, vector `10`

```python
a = keys[index].strip("")
if type(values) == "str":
    b = values[index].strip("")
else:
    b = values[index]
if type(b) == "int":
    return {f"{a}": b}
else:
    return {f"{a}": b}
```

### Copies evaluator-style self-tests into the function and triggers recursive/self-test failures

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `941f9c347bff4e8cb0c230dbd5aaa0b7`, summary `Runtime Error`, score `0`, vector `00`

```python
key = ["apple", "banana", "cherry"]
value = [10, 20, 30, 40]
is_equal(make_dict_from_elems_in_index(key, values, 1), {"banana: 20"})
is_equal(make_dict_from_elems_in_index(key, values, 1), {"cherry": 40})
return is_equal(_)
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `9facbfdac2c34774ab83d3f1fe012451`, summary `Runtime Error`, score `0`, vector `00`

```python
def make_dict_from_elems_in_index(keys, values,i )-> dict:
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
    {'cherry': 40}

    Args:
        keys (list): The list with the keys.
        values (list): The list with the values.
        index (int): An integer

# ...
```

### Runtime KeyError

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Interpretation: Dictionary lookup on uninitialized/unexpected key.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `a4193fbd439f43b2a470cc3be4d21851`, summary `Runtime Error`, score `0`, vector `00`

```python
keys = ["apple", "banana", "cherry"]
values = [10, 20, 30, 40]
if index == 1:
    dict = {"apple": 10, "banana": 20, "cherry": 30}
    return dict[index]
else:
    dict = {"apple": 20, "banana": 30, "cherry": 40}
    return dict[index]
```

### Returns the first key-value pair from nested loops, ignoring the requested `index`

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `b05561e9bfd148deb83b97040fd00dd7`, summary `Wrong Answer`, score `0`, vector `00`

```python
dict = {}
for i in range(len(keys)):
    for key in keys:
        for value in values:
            return {key: value}
```

### Returns a formatted string (`"key, value"`) instead of a dictionary

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `00` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `ea5e0b7e2c2240608421c3da13d359d1`, summary `Wrong Answer`, score `0`, vector `00`

```python
key = keys[index]
value = values[index]
return f"{key}, {value}"
```

### Builds a list of per-index dictionaries and returns `l[index]`, which fails hidden negative-index semantics

- Cluster frequency: `1/124` (`0.8%`)
- Variant frequencies:
  - `ns_25t1_py11_1/4`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/7`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/7`: `1/124` (`0.8%`)
- Dominant private-case vectors: `10` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/7`, Student ID `f8e82f0a292642a086bcd1f5175c4b6a`, summary `Wrong Answer`, score `50`, vector `10`

```python
    l = []
    for i in range(len(k)):
        for j in range(len(v)):
            if i == j:
                d = {}
                d[k[i]]=v[j]
                l.append(d)
    return l[index]
    '''
    Returns a dictionary with one key and value pair
    taken from the given index of keys and values list.

    Eg:
    >>> keys = ['apple', 'banana', 'cherry']
    >>> values = [10, 20, 30, 40]
    >>> make_dict_from_elems_in_index(keys, values, 1)
    {'banana': 20}
    >>> make_dict_from_elems_in_index(keys, values, -1)
# ...
```
