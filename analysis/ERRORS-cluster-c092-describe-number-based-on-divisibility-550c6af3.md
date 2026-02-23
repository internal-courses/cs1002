# Error Patterns: Cluster C092 (`Describe Number Based on Divisibility`)

## Cluster Summary

- Cluster ID: `C092`
- Cluster title: `Describe Number Based on Divisibility`
- Cluster file (this file): `analysis/ERRORS-cluster-c092-describe-number-based-on-divisibility-550c6af3.md`
- Variants in cluster: `1`
- Total final submitters across variants: `624`
- Total non-full final submissions across variants: `251`
- Canonical variant (by submissions): `ns_25t2_py11_1/5`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py11_1/5` (canonical) | 624 | 251 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py11_1/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `624`
- Full pass: `373`
- Non-full final submissions: `251`
- Parseable non-full (logic/runtime focus): `189`
- Non-parseable non-full: `62`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py11_1/5` | 624 | 373 | 251 | 189 | 62 |

## Private Case Structure

- Private case 1: numbers divisible by 3, 5, and neither (baseline label routing)
- Private case 2: includes multiples of 15 to ensure `FizzBuzz` branch is checked before `%3`/`%5` branches
- Private case 3: additional mixed cases to catch casing / boolean-return / missing-fallback bugs

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py11_1/5` |
| --- | ---: | ---: | ---: |
| Returns wrong casing for fallback label (`'normal'` instead of `'Normal'`) | 122 | 48.6% | 122 |
| Syntax / non-parseable final submission | 62 | 24.7% | 62 |
| No return / implicit `None` | 13 | 5.2% | 13 |
| Runtime NameError from returning bare labels (`Fizz`, `Buzz`, etc.) without quotes | 9 | 3.6% | 9 |
| Incorrect Fizz/Buzz/FizzBuzz labeling logic (broad wrong-answer failure) | 7 | 2.8% | 7 |
| Reads `input()` inside function-type question (EOF under evaluator tests) | 6 | 2.4% | 6 |
| Missing fallback `Normal` branch / incomplete case coverage | 6 | 2.4% | 6 |
| Checks `%3`/`%5` before `%15`, so `FizzBuzz` branch is unreachable for multiples of 15 | 5 | 2.0% | 5 |
| Runtime TypeError from invalid modulo/comparison operations in Fizz/Buzz logic | 5 | 2.0% | 5 |
| Runtime error (parseable final submission) | 3 | 1.2% | 3 |
| Runtime RecursionError | 3 | 1.2% | 3 |
| Runtime TypeError | 3 | 1.2% | 3 |
| Runtime NameError | 2 | 0.8% | 2 |
| Returns a boolean divisibility test instead of the required string label (`Fizz`/`Buzz`/`FizzBuzz`/`Normal`) | 1 | 0.4% | 1 |
| Uses always-truthy string boolean-chain logic (`'Fizz' or 'Buzz' ...`) instead of conditional labels | 1 | 0.4% | 1 |
| Uses bitwise `&` in divisibility conditions (operator/precedence bug) | 1 | 0.4% | 1 |
| Uses `% 10 == 0` for `Buzz` instead of `% 5 == 0` | 1 | 0.4% | 1 |
| Runtime ValueError | 1 | 0.4% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/251` (`0.0%`)

### Returns wrong casing for fallback label (`'normal'` instead of `'Normal'`)

- Cluster frequency: `122/251` (`48.6%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `122/251` (`48.6%`)
- Dominant private-case vectors: `110` x107, `000` x11, `100` x2, `101` x1
- Score distribution (top): `67.0` x108, `0.0` x11, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `4d02b19cf86448818f4d2863ee8576eb`, summary `Wrong Answer`, score `0`, vector `000`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `62/251` (`24.7%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `62/251` (`24.7%`)
- Dominant private-case vectors: `000` x62
- Score distribution (top): `0.0` x62
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `4b88f6d7f59e46e7a86a2d88e1af3a53`, summary `Runtime Error`, score `0`, vector `000`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### No return / implicit `None`

- Cluster frequency: `13/251` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `13/251` (`5.2%`)
- Dominant private-case vectors: `000` x12, `110` x1
- Score distribution (top): `0.0` x12, `67.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `1adae64996404462bc053aa2408cc692`, summary `Wrong Answer`, score `0`, vector `000`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### Runtime NameError from returning bare labels (`Fizz`, `Buzz`, etc.) without quotes

- Cluster frequency: `9/251` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `9/251` (`3.6%`)
- Dominant private-case vectors: `000` x8, `100` x1
- Score distribution (top): `0.0` x8, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `091c83759ba14da289eb6ada9f49b85b`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    pass
    if (num%3==0):
        print("\'Fizz\'")
        if(num % 5==0):
          print("\'Buzz\'")
        elif(num%3==0 and num%5==o):
            print("\'FizzBuzz\'")
    else:
        print("\'Normal\'")


        return(num(10),"Buzz")
        return(num(15),"FizzBuzz")
```

### Incorrect Fizz/Buzz/FizzBuzz labeling logic (broad wrong-answer failure)

- Cluster frequency: `7/251` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `7/251` (`2.8%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `f8f6336e1a0c47e7b3a39c9a6ddee9a4`, summary `Wrong Answer`, score `0`, vector `000`

```python
    a = divisible_by_3 = (9 % 3 == 0)
    b = divisible_by_5 = (10 % 5 == 0)
    c = divisible_by_3_and_5 = divisible_by_3 and divisible_by_5
    divisible_by_neither = ( 9 % 3 != 0 and 10 % 5 != 0)
    return a or b or c or divisible_by_neither
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `6/251` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `6/251` (`2.4%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `d94ebc77eb114acfbcdc4fbc85f0f99d`, summary `Runtime Error`, score `0`, vector `000`

```python
    describe_number = int(input())
    if  describe_number % 3 == 0 and describe_number % 5 != 0:
        print("\"Fizz\"")
    if  describe_number % 5 == 0 and describe_number%3 != 0:
        print("\"Buzz\"")
    if  describe_number % 3 == 0 and describe_number % 5 == 0:
        print("\"FizzBuzz\"")
    if  describe_number% 3 != 0 and  describe_number% 5 != 0:
        print("\"Normal\"")
```

### Missing fallback `Normal` branch / incomplete case coverage

- Cluster frequency: `6/251` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `6/251` (`2.4%`)
- Dominant private-case vectors: `000` x4, `100` x2
- Score distribution (top): `0.0` x4, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `8a51fee95a8a475b9380c0234c31fc24`, summary `Wrong Answer`, score `33`, vector `100`

```python
    if num % 3 ==0:
        return "Fizz"
    if num % 5 ==0:
        return "Buzz"
    if num % 3 == 0 and num % 5 == 0:
        return "FizzBuzz"
```

### Checks `%3`/`%5` before `%15`, so `FizzBuzz` branch is unreachable for multiples of 15

- Cluster frequency: `5/251` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `5/251` (`2.0%`)
- Dominant private-case vectors: `110` x5
- Score distribution (top): `67.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `a1b82274ca234177a0b52bd483698b2a`, summary `Wrong Answer`, score `67`, vector `110`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### Runtime TypeError from invalid modulo/comparison operations in Fizz/Buzz logic

- Cluster frequency: `5/251` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `5/251` (`2.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `34cb1a31b2984d98beb02dfd277965a9`, summary `Runtime Error`, score `0`, vector `000`

```python
    if num % 3 == 0:
       num = str("Fizz")
    if num % 5 == 0:
       num = str("Buzz")
    if num % 3 == 0 and num % 5 == 0:
       num = str("FizzBuzz")
    if num % 3 != 0 and num % 5 != 0:
       num=str("Normal")
    return(num)
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/251` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `3/251` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `746069c82f304844b44a016864bd963b`, summary `Runtime Error`, score `0`, vector `000`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### Runtime RecursionError

- Cluster frequency: `3/251` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `3/251` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `ebdadf37c91b450f8d49ed7b58b854a3`, summary `Runtime Error`, score `0`, vector `000`

```python
def describe_number(num: int) -> str:
    '''
    Given an integer, return the description based on divisibility:
    - "Fizz" if divisible by 3
    - "Buzz" if divisible by 5
    - "FizzBuzz" if divisible by both 3 and 5
    - "Normal" if divisible by neither

    Examples:
    describe_number(9) -> "Fizz"
    describe_number(10) -> "Buzz"
    describe_number(15) -> "FizzBuzz"
    describe_number(7) -> "Normal"

    Args:
        num (int): The number to be checked.

    Returns:
# ...
```

### Runtime TypeError

- Cluster frequency: `3/251` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `3/251` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `e199f37e2a5b4c3c8cc5916f95b9c18a`, summary `Runtime Error`, score `0`, vector `000`

```python
    str(9,10,15,7)//(3,5,3 or 5 , neither)
```

### Runtime NameError

- Cluster frequency: `2/251` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `2/251` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `9bd709c45e30423fb75f3ed93ae10d4e`, summary `Runtime Error`, score `0`, vector `000`

```python
    return (num1 % 3 == 0 and num2 % 5 ==0)
```

### Returns a boolean divisibility test instead of the required string label (`Fizz`/`Buzz`/`FizzBuzz`/`Normal`)

- Cluster frequency: `1/251` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `1/251` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `0d8c8285b536400d976110965afc435c`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return num % 3 == 0 or num % 5 == 0
```

### Uses always-truthy string boolean-chain logic (`'Fizz' or 'Buzz' ...`) instead of conditional labels

- Cluster frequency: `1/251` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `1/251` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `1022c5e6385c41d1aec6d665035b648b`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return str('Fizz' or 'Buzz' or 'FizzBuzz' or 'Normal')
```

### Uses bitwise `&` in divisibility conditions (operator/precedence bug)

- Cluster frequency: `1/251` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `1/251` (`0.4%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `3d9f954f5e024097b29b53f440205c56`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if n%3==0 & n%5==0:
        return "FizzBuzz"
    elif n%3==0:
        return "Fizz"
    elif n%5==0:
        return "Buzz"
    else:
        return "Normal"
```

### Uses `% 10 == 0` for `Buzz` instead of `% 5 == 0`

- Cluster frequency: `1/251` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `1/251` (`0.4%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `45c997f81ad44e9589169355aa075342`, summary `Wrong Answer`, score `67`, vector `101`

```python
    a = "Fizz"
    b = "Buzz"
    c = "FizzBuzz"
    d="Normal"
    if num%3==0 and num%5==0:
        return c

    elif num %3==0:
        return a
    elif num%10==0:
        return b
    else:
        return d
```

### Runtime ValueError

- Cluster frequency: `1/251` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py11_1/5`: `1/251` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py11_1/5`, Student ID `8b517dfd2f66418fbfbd3bf85caca79a`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
```
