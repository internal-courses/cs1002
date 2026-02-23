# Error Patterns: Cluster C016 (`Check Divisibility by Last Two Digits`)

## Cluster Summary

- Cluster ID: `C016`
- Cluster title: `Check Divisibility by Last Two Digits`
- Cluster file (this file): `analysis/ERRORS-cluster-c016-check-divisibility-by-last-two-digits-24422e8a.md`
- Variants in cluster: `2`
- Total final submitters across variants: `683`
- Total non-full final submissions across variants: `277`
- Canonical variant (by submissions): `ns_25t3_py14_1/7`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py14_1/7` (canonical) | 683 | 277 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py14_1/7.json`
- Other variants in cluster:
  - `problems/ns_25t3_py14_2/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `683`
- Full pass: `406`
- Non-full final submissions: `277`
- Parseable non-full (logic/runtime focus): `217`
- Non-parseable non-full: `60`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py14_1/7` | 683 | 406 | 277 | 217 | 60 |
| `ns_25t3_py14_2/7` | 0 | 0 | 0 | 0 | 0 |

## Private Case Structure

- Private case 1: non-zero last-two digits with mixed True/False cases (core divisibility logic only)
- Private case 2: includes 2-digit case and a last-digit-zero case (`9870`) to test zero guard
- Private case 3: mixed lengths with repeated/non-repeated last digits (e.g., `7533`) to catch extraction mistakes

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py14_1/7` | `ns_25t3_py14_2/7` |
| --- | ---: | ---: | ---: | ---: |
| Incorrect divisibility-by-last-two-digits logic (broad wrong-answer failure) | 60 | 21.7% | 60 | 0 |
| Syntax / non-parseable final submission | 60 | 21.7% | 60 | 0 |
| Runtime ZeroDivisionError from checking divisibility before guarding against zero in the last two digits | 41 | 14.8% | 41 | 0 |
| Runtime TypeError | 16 | 5.8% | 16 | 0 |
| Runtime TypeError from treating `num` as a string/sequence (or mixing string and int arithmetic) | 15 | 5.4% | 15 | 0 |
| Always returns `False` (constant output) | 13 | 4.7% | 13 | 0 |
| No return / implicit `None` | 12 | 4.3% | 12 | 0 |
| Runtime NameError | 11 | 4.0% | 11 | 0 |
| Returns after checking only part of the digits/conditions (loop exits before completing the divisibility check) | 8 | 2.9% | 8 | 0 |
| Always returns `True` (constant output) | 6 | 2.2% | 6 | 0 |
| Runtime ValueError | 5 | 1.8% | 5 | 0 |
| Partially correct divisibility logic with operator/condition bug (`or` vs `and`, wrong digit, or quotient truthiness) | 4 | 1.4% | 4 | 0 |
| Last-digit extraction bug: one of the two divisibility checks uses the wrong digit/expression | 4 | 1.4% | 4 | 0 |
| Reads `input()` inside function-type question (EOF under evaluator tests) | 3 | 1.1% | 3 | 0 |
| Runtime error (parseable final submission) | 3 | 1.1% | 3 | 0 |
| Other wrong-answer logic pattern (residual) | 3 | 1.1% | 3 | 0 |
| Uses bitwise `&` in the divisibility condition (operator/precedence bug) | 3 | 1.1% | 3 | 0 |
| Checks the same digit twice instead of testing divisibility by both last digits | 2 | 0.7% | 2 | 0 |
| Extracts the wrong digits (`%1000`/`//100`) and uses the hundreds digit instead of the tens digit | 1 | 0.4% | 1 | 0 |
| Only checks whether the last two digits are non-zero, then returns `True` without testing actual divisibility | 1 | 0.4% | 1 | 0 |
| Uses the first two digits of the string instead of the last two digits | 1 | 0.4% | 1 | 0 |
| String extraction is correct, but divisibility is checked with quotient truthiness instead of `% ... == 0` | 1 | 0.4% | 1 | 0 |
| Runtime IndexError from invalid indexing while extracting the last two digits | 1 | 0.4% | 1 | 0 |
| Uses quotient truthiness (`num//a`, `num//b`) instead of remainder checks (`num % a == 0`) | 1 | 0.4% | 1 | 0 |
| Runtime AttributeError | 1 | 0.4% | 1 | 0 |
| Runtime IndexError | 1 | 0.4% | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `3/277` (`1.1%`)

### Incorrect divisibility-by-last-two-digits logic (broad wrong-answer failure)

- Cluster frequency: `60/277` (`21.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `60/277` (`21.7%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x60
- Score distribution (top): `0.0` x60
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `3c428e4aeb254f2d93ae4e649f7b7572`, summary `Wrong Answer`, score `0`, vector `000`

```python
    count = 1
    while num!=0:
        num /= 10
        count = count + 1
    if num%10 ==0 or num%100 ==0 or num %1000 ==0:
       return False
    if (count ==3):
        first_digit = num /100
        last_digit = num % 10
        second_last_digit = (num - (first_digit)*100 - last_digit)/10
        if num % last_digit ==0 and num % second_last_digit ==0:
            return True
    if (count ==4):
        first_and_second_digit = num / 100
        last_digit = num % 10
        second_last_digit = (num - (first_and_second_digit*100) - last_digit)/10
        if num % last_digit ==0 and num % second_last_digit==0:
            return True
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `60/277` (`21.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `60/277` (`21.7%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x60
- Score distribution (top): `0.0` x60
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `b29e3d9a083d4d48b7178eb15528643f`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """
    nums =
    n = len(nums)
    if nums >= 11:
        if n >= 2:
            for i in nums:
                last_digit = nums[-2:]
# ...
```

### Runtime ZeroDivisionError from checking divisibility before guarding against zero in the last two digits

- Cluster frequency: `41/277` (`14.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `41/277` (`14.8%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x32, `000` x3, `100` x3, `110` x2
- Score distribution (top): `67.0` x34, `33.0` x4, `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `a06d21a49cb54484919c05bad9e613a6`, summary `Runtime Error`, score `67`, vector `101`

```python
    num2 = str(num)
    if num2[-1] != '0' or num2[-2] != '0':

        if num % int(num2[-1]) == 0 and int(num) % int(num2[-2]) == 0:
            return True
        else:
            return False
    elif num2[-1] == '0' or num2[-2] == '0':
        return False
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
# ...
```

### Runtime TypeError

- Cluster frequency: `16/277` (`5.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `16/277` (`5.8%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `8f17b3e06d7b41d19b92275643dfaf2a`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """
is_divisible_by_last_two_digits=(1464)
last_2=is_divisible_by_last_two_digits%100
tens = last_2//10
ones = last_2%10
if tens == 0 or ones == 0:
    print (False)
# ...
```

### Runtime TypeError from treating `num` as a string/sequence (or mixing string and int arithmetic)

- Cluster frequency: `15/277` (`5.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `15/277` (`5.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `85b53b66d84f43e98ca036284fec3e38`, summary `Runtime Error`, score `0`, vector `000`

```python
    if num % num[:-1]==0 and num % num[:-2] ==0:
        return True
    else:
       False
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """
    ...
```

### Always returns `False` (constant output)

- Cluster frequency: `13/277` (`4.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `13/277` (`4.7%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `758419b4835d43fba0522fc5237c4f46`, summary `Wrong Answer`, score `0`, vector `000`

```python
    num = ("str")
    n = num.split()
    last = num[::-1]
    last2nd = num[::-2]
    if len(num) >= 2:
        if n[::-1] == 0:
            return False
        if n[::-2] == 0:
            return False
    return False
```

### No return / implicit `None`

- Cluster frequency: `12/277` (`4.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `12/277` (`4.3%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `e41cf92ad42c4af9ba64299423587809`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.
     num=x
     a=num//10
     b=num//100
     if (num%a==0 and nu%b==0):
        if (num//10==0 or num//100==0):
        print("GIven no. is valid")
     else:
        print("Given no. is not valid")






    Return False if any of the last two digits is 0.
# ...
```

### Runtime NameError

- Cluster frequency: `11/277` (`4.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `11/277` (`4.0%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x10, `001` x1
- Score distribution (top): `0.0` x10, `33.0` x1
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `bf5dbadf1c3a448da60ab08082506236`, summary `Runtime Error`, score `0`, vector `000`

```python
    num = str(num)
    if num[-1] == "0" or num[-2] == "0":
        return false
    elif num[-1] !="0" and num[-2]!="0":
        a = int(num[-1])
        b= int(num[-2])
        num = int(num)
        if num%a ==0 and num%b==0:
            return True

        if num%a !=0 or num%b !=0:
            return false
    else:
        return false
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.
# ...
```

### Returns after checking only part of the digits/conditions (loop exits before completing the divisibility check)

- Cluster frequency: `8/277` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `8/277` (`2.9%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5, `010` x2, `001` x1
- Score distribution (top): `0.0` x5, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `e1acedce135446d588a5c5c7a79eca5a`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """
def check_divisibility_by_last_two_digits(num):
    digits=[int(d) for d in str(num)[-2:]]
    d2=(num//10) % 10
    if d1 == 0 or d2 == 0:
        return False
    return num % d1 == 0 and num % d2 == 0
```

### Always returns `True` (constant output)

- Cluster frequency: `6/277` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `6/277` (`2.2%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `0fe1018ac97746cfae52a73a5c00a45d`, summary `Wrong Answer`, score `0`, vector `000`

```python
    a=num%10
    b=(num%100)-a
    if(a*b==0):
        return(False)
    elif(num%a!=0 or num%b!=0):
        return(False)
    else:
        return(True)
```

### Runtime ValueError

- Cluster frequency: `5/277` (`1.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `5/277` (`1.8%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `0a8abe6a996743a593d978082e6b190e`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """

num = input()
num1 = int(num) % 10
num2 = int(num) % 100
num3 = num2//10
if (num1 != 0 and num3 != 0):
# ...
```

### Partially correct divisibility logic with operator/condition bug (`or` vs `and`, wrong digit, or quotient truthiness)

- Cluster frequency: `4/277` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `4/277` (`1.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x4
- Score distribution (top): `33.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `e195b88c29214a53b0866870be98f49d`, summary `Wrong Answer`, score `33`, vector `001`

```python
    n= num % 10
    ln= n % 10
    if num !=0:
        if (n == 0) :
           return False
        if (ln == 0):
            return 0
        if num % n !=0:
            return False
        if num % ln != 0:
            return False
        elif(num %n ==0):
            return True
        elif(num % ln ==0):
            return True
```

### Last-digit extraction bug: one of the two divisibility checks uses the wrong digit/expression

- Cluster frequency: `4/277` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `4/277` (`1.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x4
- Score distribution (top): `67.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `f587b49a89a6436bb7540ac1905a3e47`, summary `Wrong Answer`, score `67`, vector `101`

```python
    a = str(num)
    b = int(a[-2:-1])
    c = int(a[-1])
    if num>0 and len(a)>2:
        # if b ==0 or c ==0:
        #     return False
        if b ==0 and c==0:
            return False
        elif b==0 and c!=0:
            return False
        elif b!=0 and c==0:
            return False
        elif num%b ==0 and num%c ==0:
            return True
        elif num%b ==0 and num%c !=0:
            return False
        elif num%b !=0 and num%c ==0:
            return False
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `3/277` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `3/277` (`1.1%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `f82977150c354d5387b7e84b97c7cdc7`, summary `Runtime Error`, score `0`, vector `000`

```python
    num = int(input("Enter a number(Atleast 2 digits):"))
    if(num % num[-1] == 0):
        if(num % num[-2] == 0):
            print("is_divisible_by_last_two_digits","True")
        else:
            print("False")
    else:
        print("False")
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/277` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `3/277` (`1.1%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2, `001` x1
- Score distribution (top): `0.0` x2, `33.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `a6718c5a28db4f748d23bcabb988e3f2`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_divisible_by_last_two_digits(num: int):
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if divisible by both last two digits, False otherwise.
    """


return
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `3/277` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `3/277` (`1.1%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x2, `011` x1
- Score distribution (top): `33.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `e6261cff35dc4a2685cb18b8e00540ac`, summary `Wrong Answer`, score `33`, vector `100`

```python
    num1 = str(num)
    if len(num1) == 3:
        return False
    a = int(num1[-1])
    b = int(num1[-2])
    if num%a == 0 and num%b == 0:
        return True
    elif a == 0 or b == 0:
        return False
    else:
        return False
    """
    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.
# ...
```

### Uses bitwise `&` in the divisibility condition (operator/precedence bug)

- Cluster frequency: `3/277` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `3/277` (`1.1%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x1, `000` x1, `001` x1
- Score distribution (top): `33.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `dbe6dc7d105e4b309398b99789333e4a`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if len(str(num))<2:
        return False
    else:
        k= num % 10
        num1= num & 10
        m= num1 % 10

        if k==0 or m==0:
            return False
        elif num%k==0 and num%m==0:
            return True
        else:
            return False
```

### Checks the same digit twice instead of testing divisibility by both last digits

- Cluster frequency: `2/277` (`0.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `2/277` (`0.7%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x1, `001` x1
- Score distribution (top): `67.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `4d51d1b34d304517aea154a4237dadd6`, summary `Wrong Answer`, score `67`, vector `101`

```python
    'eturn False if any of the last two digits is 0.'
    last_two=num%100
    last_digit=num%100
    second_last_digit=(num//10)%10
    if last_digit==0 or second_last_digit==0:
        return False
    return (num % second_last_digit==0) and (num%second_last_digit==0)
```

### Extracts the wrong digits (`%1000`/`//100`) and uses the hundreds digit instead of the tens digit

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `05917bc18ff94dd5a89c93ac33c01ca1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    last_two= num%1000
    tens= last_two//100
    ones= last_two % 10
    if tens == 0 or ones == 0 :
        return (False)
    return num % tens == 0 and num % ones == 0
```

### Only checks whether the last two digits are non-zero, then returns `True` without testing actual divisibility

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `0c8ee15a4aef41c081959ed7aa5c6e60`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if num%100==0 or num%10==0:
        return False
    else:
        return True
```

### Uses the first two digits of the string instead of the last two digits

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `1ee14c301c0f4071aefcec5372a320c3`, summary `Wrong Answer`, score `33`, vector `010`

```python
    p = str(num)
    rev = p[::-1]
    rev1 = p[0]
    rev2 = p[1]
    digit1 = int(rev1)
    digit2 = int(rev2)
    if (num % digit1 == 0 and num % digit2 == 0):
        return True
    else:
        return False
```

### String extraction is correct, but divisibility is checked with quotient truthiness instead of `% ... == 0`

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `2f1e798384bd478a93612af94225d4e0`, summary `Wrong Answer`, score `0`, vector `000`

```python
    strNum= str(num)
    n= len(strNum)
    last= int(strNum[-1])
    second_last = int(strNum[-2])
    if num//last==0 and num//second_last==0 or last ==0:
       return True
    else:
        return False
    """

    Checks if the given number is divisible by both of its last two digits.

    Return False if any of the last two digits is 0.

    Args:
        num (int): The number to check.

    Returns:
# ...
```

### Runtime IndexError from invalid indexing while extracting the last two digits

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `5e08a0dbd73e4dbaa3f458c17caa705b`, summary `Runtime Error`, score `0`, vector `000`

```python
    int = str(num)
    for i in int :
      if num % i[-2] and num % i[-1] :
        return True
      if i[-2]==0 or int[-1]==0 :
        return False
    return False
```

### Uses quotient truthiness (`num//a`, `num//b`) instead of remainder checks (`num % a == 0`)

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `a32e2403d9034cf8923d7737e7927592`, summary `Wrong Answer`, score `33`, vector `001`

```python
    num = str(num)
    a = num[-2]
    b = num[-1]
    a = int(a)
    b = int(b)
    num = int(num)
    if a == 0 or b == 0 :
        return False
    if num//a and num//b :
        return True




    else :
        return False
```

### Runtime AttributeError

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `f51d9adce3854d69a63b99458e2d8ba5`, summary `Runtime Error`, score `0`, vector `000`

```python
    return(num /num.digits(-1) and num /num.digits(-2))
```

### Runtime IndexError

- Cluster frequency: `1/277` (`0.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/7`: `1/277` (`0.4%`)
  - `ns_25t3_py14_2/7`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/7`, Student ID `fabc9f0d2eee4e629a3823c03acb908b`, summary `Runtime Error`, score `0`, vector `000`

```python
    num = [str(num)]
    n = len(num)
    for _ in range(len(num)):
        if (num % num[len(num)] == 0 and num % num[len(num)-1] == 0):
            return True
        if(num%num[n]==0 or num%num[n-1]==0):
            return False
        if (num[n]==0):
            return False
```
