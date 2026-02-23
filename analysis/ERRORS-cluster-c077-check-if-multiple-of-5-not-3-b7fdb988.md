# Error Patterns: Cluster C077 (`Check If Multiple of 5 Not 3`)

## Cluster Summary

- Cluster ID: `C077`
- Cluster title: `Check If Multiple of 5 Not 3`
- Cluster file (this file): `analysis/ERRORS-cluster-c077-check-if-multiple-of-5-not-3-b7fdb988.md`
- Variants in cluster: `1`
- Total final submitters across variants: `1011`
- Total non-full final submissions across variants: `121`
- Canonical variant (by submissions): `ns_25t2_py22_1/14`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py22_1/14` (canonical) | 1011 | 121 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py22_1/14.json`

## Cluster-Level Outcome Summary

- Final submitters: `1011`
- Full pass: `890`
- Non-full final submissions: `121`
- Parseable non-full (logic/runtime focus): `93`
- Non-parseable non-full: `28`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py22_1/14` | 1011 | 890 | 121 | 93 | 28 |

## Private Case Structure

- Private case 1: mixed positives/negatives around divisibility by 5 and 3 (incl 30)
- Private case 2: includes negative multiple of 5, zero, and non-multiple distractor
- Private case 3: larger positives/negatives incl multiple of 15 distractor (45)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py22_1/14` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 28 | 23.1% | 28 |
| Uses `num % 3 == 0` in the positive condition (accepts multiples of 15) | 18 | 14.9% | 18 |
| Handles only the `num % 5 == 0` branch and forgets the non-multiple fallback case | 8 | 6.6% | 8 |
| Incorrect divisibility logic (broad wrong-answer failure) | 8 | 6.6% | 8 |
| No return / implicit `None` | 8 | 6.6% | 8 |
| Runtime NameError | 8 | 6.6% | 8 |
| Checks only divisibility by 5 (omits the 'not multiple of 3' condition) | 8 | 6.6% | 8 |
| Uses `or` instead of `and` when combining divisibility conditions | 7 | 5.8% | 7 |
| Uses floor-division/digit heuristic instead of direct modulus divisibility checks | 5 | 4.1% | 5 |
| Always returns `True` (constant output) | 5 | 4.1% | 5 |
| Checks divisibility by 3 instead of 'multiple of 5 and not 3' | 3 | 2.5% | 3 |
| Uses bitwise `&` in divisibility condition (operator/precedence bug) | 2 | 1.7% | 2 |
| Boolean literal expression (`True or False`) used instead of real condition | 2 | 1.7% | 2 |
| Always returns `False` (constant output) | 2 | 1.7% | 2 |
| Uses arithmetic multiplication truthiness (`num*5`, `num*3`) instead of divisibility checks | 2 | 1.7% | 2 |
| Runtime error (parseable final submission) | 2 | 1.7% | 2 |
| Computes the `% 3 != 0` check but does not use it in a condition | 1 | 0.8% | 1 |
| Runtime RecursionError | 1 | 0.8% | 1 |
| Runtime TypeError | 1 | 0.8% | 1 |
| Returns a text message/string instead of boolean `True`/`False` | 1 | 0.8% | 1 |
| Other wrong-answer logic pattern (residual) | 1 | 0.8% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `1/121` (`0.8%`)

### Syntax / non-parseable final submission

- Cluster frequency: `28/121` (`23.1%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `28/121` (`23.1%`)
- Dominant private-case vectors: `000` x28
- Score distribution (top): `0.0` x28
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `3b46c3f98dd54ed299c2d21f7324e878`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_multiple_of_5_not_3(num):
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
        >>> is_multiple_of_5_not_3(9)
        False
        >>> is_multiple_of_5_not_3(-25)
# ...
```

### Uses `num % 3 == 0` in the positive condition (accepts multiples of 15)

- Cluster frequency: `18/121` (`14.9%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `18/121` (`14.9%`)
- Dominant private-case vectors: `001` x15, `000` x3
- Score distribution (top): `33.0` x15, `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `26c2a640962c420d95e8eb421b888db5`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if num%5==0 and num%3==0:
        return False
    else:
        return True
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
# ...
```

### Handles only the `num % 5 == 0` branch and forgets the non-multiple fallback case

- Cluster frequency: `8/121` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `8/121` (`6.6%`)
- Dominant private-case vectors: `001` x8
- Score distribution (top): `33.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `33fc4d07fe0c414198d94992fe5e25e7`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if num % 5 == 0:
        if num % 3 != 0:
            return True
        else:
            return False
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
# ...
```

### Incorrect divisibility logic (broad wrong-answer failure)

- Cluster frequency: `8/121` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `8/121` (`6.6%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `f22e58daffb64207bbd5ab3d0437f3bb`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return num & 5 == 0 and  num & 3 != 0 ;
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
        >>> is_multiple_of_5_not_3(9)
        False
        >>> is_multiple_of_5_not_3(-25)
# ...
```

### No return / implicit `None`

- Cluster frequency: `8/121` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `8/121` (`6.6%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `1722d022d9af4513a3f82d29424a57ff`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_multiple_of_5_not_3(num):
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
        >>> is_multiple_of_5_not_3(9)
        False
        >>> is_multiple_of_5_not_3(-25)
# ...
```

### Runtime NameError

- Cluster frequency: `8/121` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `8/121` (`6.6%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `679d790200f54bc79417acf791a81709`, summary `Runtime Error`, score `0`, vector `000`

```python
    def is_multiple_of_5_not_3(num):
        num=int(input())
    for i in range(num):
        if num % 3 ==o:
            print(False)
        if num % 5 == 0 and num % 3 != 0:
            print(True)
        else:
            return(num)
```

### Checks only divisibility by 5 (omits the 'not multiple of 3' condition)

- Cluster frequency: `8/121` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `8/121` (`6.6%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `44db886f898a499789806b5566fe0925`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if num % 5 == 0:
        return True
    else:
        return False
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
# ...
```

### Uses `or` instead of `and` when combining divisibility conditions

- Cluster frequency: `7/121` (`5.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `7/121` (`5.8%`)
- Dominant private-case vectors: `000` x6, `011` x1
- Score distribution (top): `0.0` x6, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `30189c78a18e445f92aa67b28342d78a`, summary `Wrong Answer`, score `67`, vector `011`

```python
    return(num < 0 > num and num % 5 == 0) or (num >0 and num % 3 ==1 )
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
        >>> is_multiple_of_5_not_3(9)
        False
        >>> is_multiple_of_5_not_3(-25)
# ...
```

### Uses floor-division/digit heuristic instead of direct modulus divisibility checks

- Cluster frequency: `5/121` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `5/121` (`4.1%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `c4561c654d2749a99ca73ac2825c3c7e`, summary `Wrong Answer`, score `0`, vector `000`

```python
    numb= abs(int(num))
    if (numb//5) != (numb //3):
        return True
    if (numb//5) == (numb//3):
        return False
    else:
        return False
```

### Always returns `True` (constant output)

- Cluster frequency: `5/121` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `5/121` (`4.1%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `f2d4b598bab14253b347148544457bbb`, summary `Wrong Answer`, score `0`, vector `000`

```python
    for i in range(abs(num)):
        if i%5==0 and i%3!=0:
            return True
    else:
        pass
```

### Checks divisibility by 3 instead of 'multiple of 5 and not 3'

- Cluster frequency: `3/121` (`2.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `3/121` (`2.5%`)
- Dominant private-case vectors: `110` x1, `000` x1, `010` x1
- Score distribution (top): `67.0` x1, `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `77e82ca1230647be951608b63795d672`, summary `Wrong Answer`, score `0`, vector `000`

```python
    divisible_by_5 = False
    divisible_by_3 = False
    last_digit = num % 10
    first_digit = num // 10
    sum_digits = first_digit+last_digit
    if last_digit == 0 or last_digit == 5:
        divisible_by_5 = True
    elif sum_digits % 3 == 0:
        divisible_by_3 = True
    if divisible_by_5 == True and divisible_by_3 == False:
        return True
    else:
        return False
    ...
```

### Uses bitwise `&` in divisibility condition (operator/precedence bug)

- Cluster frequency: `2/121` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `2/121` (`1.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `0360be91223b401d83220d914278edfe`, summary `Wrong Answer`, score `0`, vector `000`

```python
    num == ()
    if (num % 5 != 0 & num % 3 == num % 5 & num % 3 != num % 5):
        return False
    return True
```

### Boolean literal expression (`True or False`) used instead of real condition

- Cluster frequency: `2/121` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `2/121` (`1.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `ea4030d43fba4474a17569dd9cdd0b55`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if(num%3==0):
        print("False")
    if (num%5==0):
       if(num%3==0):
         print("True")
    return True or False
```

### Always returns `False` (constant output)

- Cluster frequency: `2/121` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `2/121` (`1.7%`)
- Dominant private-case vectors: `000` x1, `001` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `ab79b27f080745a4bed5b217d69cd6e4`, summary `Wrong Answer`, score `33`, vector `001`

```python
    ...
    abs_num=abs(num)
    if (abs_num%5 == 0):
        if(abs_num%3 != 0):
            return(bool(abs_num))
        elif(abs_num%3 == 0):
            return(False)
```

### Uses arithmetic multiplication truthiness (`num*5`, `num*3`) instead of divisibility checks

- Cluster frequency: `2/121` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `2/121` (`1.7%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `28598fabe12245e3bf668990e1a2c81f`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if  num*5 and num *3:
        return True
    else:
        return False
```

### Runtime error (parseable final submission)

- Cluster frequency: `2/121` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `2/121` (`1.7%`)
- Dominant private-case vectors: `001` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `98b1bf7841c046a699c63609430d34d5`, summary `Runtime Error`, score `33`, vector `001`

```python
    flag2 = False
    num = abs(num)
    if num%5==0:
        flag1 = True
    if num%3 !=0:
        flag2 = True
    if flag1 and flag2:
        return True
    else:
        return False
```

### Computes the `% 3 != 0` check but does not use it in a condition

- Cluster frequency: `1/121` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `1/121` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `07e35959e5444c60a5104720efd575d9`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if num % 5 == 0:
        num % 3 != 0
        return True
    elif num % 3 == 0:
         return False
    else:
        return True
```

### Runtime RecursionError

- Cluster frequency: `1/121` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `1/121` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `081970c94ee0475aaae93b6baa496c2a`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
```

### Runtime TypeError

- Cluster frequency: `1/121` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `1/121` (`0.8%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `4f6630f96c6e48e9b972756b6827904f`, summary `Runtime Error`, score `0`, vector `000`

```python
    if str(abs(num))%5==0:
        return True
    if num%3==0:
        return False
```

### Returns a text message/string instead of boolean `True`/`False`

- Cluster frequency: `1/121` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `1/121` (`0.8%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `e869d0352c314af5be0cca1a90528ec5`, summary `Wrong Answer`, score `33`, vector `001`

```python
    rem1 = num % 5
    rem2 = num % 3
    if (rem1 == 0 and rem2 > 0):
        return True
    elif rem1 > 0:
        return  "Num is not multiple of 5"
    else:
        return False
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
# ...
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `1/121` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/14`: `1/121` (`0.8%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/14`, Student ID `f86b980c7e2e410c94e8ada11ecc6a62`, summary `Wrong Answer`, score `33`, vector `010`

```python
    return num % 5 == 0 and num % 3 == 1
    """
    Checks if a number is a multiple of 5 but not a multiple of 3.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if `num` is a multiple of 5 but not 3, False otherwise.

    Examples:
        >>> is_multiple_of_5_not_3(10)
        True
        >>> is_multiple_of_5_not_3(15)
        False
        >>> is_multiple_of_5_not_3(9)
        False
        >>> is_multiple_of_5_not_3(-25)
# ...
```
