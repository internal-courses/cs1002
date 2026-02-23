# Error Patterns: Cluster C078 (`Check For Greeting Prefix`)

## Cluster Summary

- Cluster ID: `C078`
- Cluster title: `Check For Greeting Prefix`
- Cluster file (this file): `analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md`
- Variants in cluster: `1`
- Total final submitters across variants: `982`
- Total non-full final submissions across variants: `405`
- Canonical variant (by submissions): `ns_25t2_py22_1/15`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py22_1/15` (canonical) | 982 | 405 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py22_1/15.json`

## Cluster-Level Outcome Summary

- Final submitters: `982`
- Full pass: `577`
- Non-full final submissions: `405`
- Parseable non-full (logic/runtime focus): `381`
- Non-parseable non-full: `24`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py22_1/15` | 982 | 577 | 405 | 381 | 24 |

## Private Case Structure

- Private case 1: `Hello`/`Hi` without trailing space should be False; `Hi Bob` True; lowercase `hello` False
- Private case 2: positive `Hello universe`, leading-space negative (`' hi there'`), unrelated string negative
- Private case 3: empty string negative; `'Hi '` and `'Hello '` positives (trailing-space edge cases)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py22_1/15` |
| --- | ---: | ---: | ---: |
| Checks `Hello`/`Hi` without requiring the trailing space | 92 | 22.7% | 92 |
| Runtime IndexError from direct indexing on short/empty strings | 79 | 19.5% | 79 |
| Checks first token via `split()` (accepts `Hello`/`Hi` without required trailing space) | 47 | 11.6% | 47 |
| Syntax / non-parseable final submission | 24 | 5.9% | 24 |
| Partially correct greeting-prefix logic (fails edge cases like no-space/leading-space/empty input) | 23 | 5.7% | 23 |
| Strips whitespace before checking prefix (wrongly accepts leading-space inputs / changes semantics) | 19 | 4.7% | 19 |
| Boolean-chain literal bug (`... or 'Hi'`) creates an always-truthy greeting condition | 18 | 4.4% | 18 |
| Incorrect greeting-prefix logic (broad wrong-answer failure) | 16 | 4.0% | 16 |
| No return / implicit `None` | 15 | 3.7% | 15 |
| Makes the check case-insensitive (`hello`/`hi` become accepted) | 12 | 3.0% | 12 |
| Always returns `True` (constant output) | 12 | 3.0% | 12 |
| Extracts the first word manually (or via `split`) and compares to `Hello`/`Hi`, ignoring required trailing-space semantics | 10 | 2.5% | 10 |
| Runtime NameError | 5 | 1.2% | 5 |
| Uses `and` between `Hello` and `Hi` prefix checks (impossible conjunction) | 5 | 1.2% | 5 |
| Always returns `False` (constant output) | 4 | 1.0% | 4 |
| Other wrong-answer logic pattern (residual) | 4 | 1.0% | 4 |
| Hard-codes public sample strings/examples instead of the general prefix rule | 4 | 1.0% | 4 |
| Checks `Hello`/`Hi` prefixes without trailing space using `startswith((...))` | 4 | 1.0% | 4 |
| Uses substring containment (`in`) instead of checking the prefix | 4 | 1.0% | 4 |
| Runtime TypeError | 3 | 0.7% | 3 |
| Uses `startswith("Hello" or "Hi")` (Python `or` collapses to one prefix) | 2 | 0.5% | 2 |
| Runtime AttributeError | 1 | 0.2% | 1 |
| Runtime error (parseable final submission) | 1 | 0.2% | 1 |
| Runtime RecursionError | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `4/405` (`1.0%`)

### Checks `Hello`/`Hi` without requiring the trailing space

- Cluster frequency: `92/405` (`22.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `92/405` (`22.7%`)
- Dominant private-case vectors: `011` x81, `000` x5, `010` x5, `110` x1
- Score distribution (top): `67.0` x82, `0.0` x5, `33.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `afea0a243a5642679780d8b464c84eed`, summary `Wrong Answer`, score `67`, vector `011`

```python
    if ((s.startswith('hi')) or (s.startswith('hello'))):
        return True
    if ((s.startswith('Hi')) or (s.startswith('Hello'))):
        return True
    return False
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
# ...
```

### Runtime IndexError from direct indexing on short/empty strings

- Cluster frequency: `79/405` (`19.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `79/405` (`19.5%`)
- Dominant private-case vectors: `010` x56, `000` x13, `011` x6, `110` x4
- Score distribution (top): `33.0` x56, `0.0` x13, `67.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `6119ae15706c4340a349ce254c3058fc`, summary `Runtime Error`, score `33`, vector `010`

```python
    words=s.split()
    if words[0]=="Hi":
        return bool(1)
    elif words[0]=="Hello":
        return bool(1)
    else:
        return bool(0)
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
# ...
```

### Checks first token via `split()` (accepts `Hello`/`Hi` without required trailing space)

- Cluster frequency: `47/405` (`11.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `47/405` (`11.6%`)
- Dominant private-case vectors: `011` x38, `010` x5, `110` x2, `000` x1
- Score distribution (top): `67.0` x40, `33.0` x6, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `26c2a640962c420d95e8eb421b888db5`, summary `Wrong Answer`, score `33`, vector `010`

```python
    s=s.split()
    for char in s:
        if s[0]=="Hello":
            return True
        elif s[0]=="Hi":
            return True
        else:
            return False
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `24/405` (`5.9%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `24/405` (`5.9%`)
- Dominant private-case vectors: `000` x24
- Score distribution (top): `0.0` x24
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `698c28cd9f984314be266e185b1a988d`, summary `Runtime Error`, score `0`, vector `000`

```python
def starts_with_greeting(s):
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
        True
        >>> starts_with_greeting('Good morning')
        False
        >>> starts_with_greeting('HiThere')
# ...
```

### Partially correct greeting-prefix logic (fails edge cases like no-space/leading-space/empty input)

- Cluster frequency: `23/405` (`5.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `23/405` (`5.7%`)
- Dominant private-case vectors: `011` x16, `010` x4, `110` x3
- Score distribution (top): `67.0` x19, `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `0da654ac991d4aa1a2dd5b41b7efd4b9`, summary `Wrong Answer`, score `67`, vector `011`

```python
   x= s[0:6]
   y= s[0:3]
   if (x=="Hello " or x=="hello " or x=="HELLO " or x=="heLLo " or x=="hELLO " or x=="HeLlO " or x=="hElLo " or x=="HELLo " ):
       return True
   elif (y=="Hi " or y=="hi " or y=="HI " or y=="hI" ):
       return True
   else:
       return False
```

### Strips whitespace before checking prefix (wrongly accepts leading-space inputs / changes semantics)

- Cluster frequency: `19/405` (`4.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `19/405` (`4.7%`)
- Dominant private-case vectors: `011` x11, `001` x4, `110` x3, `000` x1
- Score distribution (top): `67.0` x14, `33.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `bf97192352334345b5d727113b541709`, summary `Wrong Answer`, score `67`, vector `011`

```python
    s.strip()
    l=s.split(" ")
    if l[0]=="Hi" or l[0]=="Hello":
        return True
    else:
        return False
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
# ...
```

### Boolean-chain literal bug (`... or 'Hi'`) creates an always-truthy greeting condition

- Cluster frequency: `18/405` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `18/405` (`4.4%`)
- Dominant private-case vectors: `000` x14, `010` x2, `011` x1, `101` x1
- Score distribution (top): `0.0` x14, `67.0` x2, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `8081d5521dcb4ba7ae8d2fd07f9282a4`, summary `Wrong Answer`, score `0`, vector `000`

```python
def starts_with_greeting(s):
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
        True
        >>> starts_with_greeting('Hithere')
        False
        >>> starts_with_greeting('Welcome')
# ...
```

### Incorrect greeting-prefix logic (broad wrong-answer failure)

- Cluster frequency: `16/405` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `16/405` (`4.0%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `8c72b50b479647a1babde4c3e7d10bd8`, summary `Wrong Answer`, score `0`, vector `000`

```python
    bool=(True, False)
    if(s):
        s=("Hello", "Hi")
        return(True)
    elif(s):
        s=("Hithere", "Welcome")
        return(False)
    else:
        return("OK")
    def is_equal(A):
        A=(starts_with_greeting(s), "bool")
        print(A)
```

### No return / implicit `None`

- Cluster frequency: `15/405` (`3.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `15/405` (`3.7%`)
- Dominant private-case vectors: `000` x11, `011` x3, `010` x1
- Score distribution (top): `0.0` x11, `67.0` x3, `33.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `3b46c3f98dd54ed299c2d21f7324e878`, summary `Wrong Answer`, score `0`, vector `000`

```python
def starts_with_greeting(s):
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
        True
        >>> starts_with_greeting('Good morning')
        False
        >>> starts_with_greeting('HiThere')
# ...
```

### Makes the check case-insensitive (`hello`/`hi` become accepted)

- Cluster frequency: `12/405` (`3.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `12/405` (`3.0%`)
- Dominant private-case vectors: `011` x11, `000` x1
- Score distribution (top): `67.0` x11, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `a846a94be87a4ad49d6f652d8980a90b`, summary `Wrong Answer`, score `0`, vector `000`

```python
    s = s.lower().lstrip()
    return s.startswith("Hello") or s.startswith("Hi")
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
        True
        >>> starts_with_greeting('Good morning')
        False
# ...
```

### Always returns `True` (constant output)

- Cluster frequency: `12/405` (`3.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `12/405` (`3.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `cc61ea411a4f4cff9c125cccd3f78729`, summary `Wrong Answer`, score `0`, vector `000`

```python
    s = {"hello ","Hi "}
    for i in s:
        if i == "Hello ":
            return True
        elif i == "Hi ":
            return True
```

### Extracts the first word manually (or via `split`) and compares to `Hello`/`Hi`, ignoring required trailing-space semantics

- Cluster frequency: `10/405` (`2.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `10/405` (`2.5%`)
- Dominant private-case vectors: `011` x6, `000` x2, `010` x2
- Score distribution (top): `67.0` x6, `0.0` x2, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `340fce4c21fb4eaea58e137862867e2b`, summary `Wrong Answer`, score `67`, vector `011`

```python
    word = ""
    s = s.lower()
    for i in s:
        if i == ' ':
            break
        else:
            word += i
    if word == "hello":
        return True
    elif word == "hi":
        return True
    else:
        return False
```

### Runtime NameError

- Cluster frequency: `5/405` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `5/405` (`1.2%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `d6ad28442e9e434db73567370b038861`, summary `Runtime Error`, score `0`, vector `000`

```python
    if iStreamAs.startwith ("Hello"):
        return True
    elif iStreamAs.startwith ("Hi"):
        return True
    else:
        return False
```

### Uses `and` between `Hello` and `Hi` prefix checks (impossible conjunction)

- Cluster frequency: `5/405` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `5/405` (`1.2%`)
- Dominant private-case vectors: `000` x4, `011` x1
- Score distribution (top): `0.0` x4, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `3598ccbe31ff449bae4dd781dd30dd7d`, summary `Wrong Answer`, score `67`, vector `011`

```python
    if s[0:5]=="Hello" or s[0:2]=="Hi":
        return True
    else:
        return False
    '''
    if (s[0:5]=="Hello" and s[6]==" ") or (s[0:2] and s[3]==" "):
        return True
    else:
        return False'''
```

### Always returns `False` (constant output)

- Cluster frequency: `4/405` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `4/405` (`1.0%`)
- Dominant private-case vectors: `000` x2, `110` x1, `011` x1
- Score distribution (top): `67.0` x2, `0.0` x2
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `aabbd7568c7e4f33aa4c6788f664086d`, summary `Wrong Answer`, score `67`, vector `011`

```python
    s_str=s.split(' ')
    greet_word=['Hello','Hi']
    for char in s_str:
        if greet_word[0]==s_str[0] or greet_word[1]==s_str[0]:
            return(True)
        else:
            return(False)
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `4/405` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `4/405` (`1.0%`)
- Dominant private-case vectors: `001` x3, `100` x1
- Score distribution (top): `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `e499194e5cc04cff9ec5484545eefb54`, summary `Wrong Answer`, score `33`, vector `100`

```python
    H="Hello "
    h="Hi "
    for i in range(len(s)):
        if (s[0:5]==H):
            return True
        elif(s[0:3]==h):
            return True
        else:
            return False
```

### Hard-codes public sample strings/examples instead of the general prefix rule

- Cluster frequency: `4/405` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `4/405` (`1.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `e5c98dbe050d4d2c816344b402a17bc7`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    for i in s:
        if i[0] == ("Hello there ") or i[0] == ("Hi friend ") :
            return False
        else:
            return True
```

### Checks `Hello`/`Hi` prefixes without trailing space using `startswith((...))`

- Cluster frequency: `4/405` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `4/405` (`1.0%`)
- Dominant private-case vectors: `011` x3, `000` x1
- Score distribution (top): `67.0` x3, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `f22e58daffb64207bbd5ab3d0437f3bb`, summary `Wrong Answer`, score `67`, vector `011`

```python
    return s.startswith(("Hello", "Hi"))
    """
    Checks whether a given string starts with 'Hello ' or 'Hi '.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string starts with 'Hello ' or 'Hi ', False otherwise.

    Examples:
        >>> starts_with_greeting('Hello there')
        True
        >>> starts_with_greeting('Hi friend')
        True
        >>> starts_with_greeting('Good morning')
        False
        >>> starts_with_greeting('HiThere')
# ...
```

### Uses substring containment (`in`) instead of checking the prefix

- Cluster frequency: `4/405` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `4/405` (`1.0%`)
- Dominant private-case vectors: `011` x2, `010` x1, `000` x1
- Score distribution (top): `67.0` x2, `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `b5774add0243429e87bf974726f72d76`, summary `Wrong Answer`, score `33`, vector `010`

```python
    for i in s:
        if "Hello" in s:
             return True
        elif 'Hi'in s:
            return True
        else:
            return False
```

### Runtime TypeError

- Cluster frequency: `3/405` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `3/405` (`0.7%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `b7d58357b99047b090f5abae237464d0`, summary `Runtime Error`, score `0`, vector `000`

```python
    s = str('Hello there', 'Hi friend', 'Good morning', ' HiThere')
    for i in s:
        s_w_t = split.s
        s_w_w = append.s
        return True
    else:
        return False
```

### Uses `startswith("Hello" or "Hi")` (Python `or` collapses to one prefix)

- Cluster frequency: `2/405` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `2/405` (`0.5%`)
- Dominant private-case vectors: `010` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `0d0b149e4e1d41d2bb6a0929a0905d08`, summary `Wrong Answer`, score `33`, vector `010`

```python
    if s.startswith(("Hello" or "Hi")):
        return True
    else:
        return False
```

### Runtime AttributeError

- Cluster frequency: `1/405` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `1/405` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `8b19220c23c0436bbebff9e2bcb05d05`, summary `Runtime Error`, score `0`, vector `000`

```python
    if s.start("Hello" or "Hi"):
       return True
    else:
       return False
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/405` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `1/405` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `c7218380af4d460b8e03a2bfe33094cf`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
```

### Runtime RecursionError

- Cluster frequency: `1/405` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/15`: `1/405` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/15`, Student ID `f92c1eaf820e46679028a3a6d529ee4f`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    return starts_with_greeting('Hello') or starts_with_greeting('Hi')
```
