# Error Patterns: Cluster C090 (`Compute Polynomial Value`)

## Cluster Summary

- Cluster ID: `C090`
- Cluster title: `Compute Polynomial Value`
- Cluster file (this file): `analysis/ERRORS-cluster-c090-compute-polynomial-value-a73aab7f.md`
- Variants in cluster: `1`
- Total final submitters across variants: `634`
- Total non-full final submissions across variants: `249`
- Canonical variant (by submissions): `ns_25t2_py13_1/9`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_1/9` (canonical) |              634 |      249 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/9.json`

## Cluster-Level Outcome Summary

- Final submitters: `634`
- Full pass: `385`
- Non-full final submissions: `249`
- Parseable non-full (logic/runtime focus): `197`
- Non-parseable non-full: `52`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_1/9` |              634 |       385 |      249 |                197 |                     52 |

## Private Case Structure

- Private case 1: baseline polynomial evaluations on hidden coefficient lists (descending powers)
- Private case 2: cases with repeated coefficients/values to catch `coef.index(...)` exponent bugs
- Private case 3: additional lengths/degrees to catch fixed-length formulas and premature loop returns

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                | Cluster count | % of cluster non-full | `ns_25t2_py13_1/9` |
| ------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | -----------------: |
| Syntax / non-parseable final submission                                                                |            52 |                 20.9% |                 52 |
| Returns from inside the coefficient loop, so only part of the polynomial is evaluated                  |            43 |                 17.3% |                 43 |
| No return / implicit `None`                                                                            |            43 |                 17.3% |                 43 |
| Incorrect polynomial evaluation logic (broad wrong-answer failure)                                     |            30 |                 12.0% |                 30 |
| Runtime TypeError from mixing coefficient list and scalar operations in polynomial evaluation          |            15 |                  6.0% |                 15 |
| Runtime IndexError from fixed-position coefficient indexing on varying polynomial lengths              |            13 |                  5.2% |                 13 |
| Hard-codes public sample polynomial values instead of evaluating arbitrary coefficients                |            12 |                  4.8% |                 12 |
| Runtime NameError from variable-name mismatch in coefficient/exponent computation                      |            11 |                  4.4% |                 11 |
| Partially correct polynomial evaluation with exponent-order / premature-return bug                     |             8 |                  3.2% |                  8 |
| Runtime NameError                                                                                      |             6 |                  2.4% |                  6 |
| Reads `input()` inside function-type question (EOF under evaluator tests)                              |             3 |                  1.2% |                  3 |
| Uses fixed-degree formula (length-specific polynomial) instead of handling arbitrary coefficient lists |             3 |                  1.2% |                  3 |
| Uses `^` (bitwise XOR) instead of exponentiation `**` for powers of `x`                                |             2 |                  0.8% |                  2 |
| Runtime IndexError                                                                                     |             1 |                  0.4% |                  1 |
| Runtime RecursionError                                                                                 |             1 |                  0.4% |                  1 |
| Runtime error (parseable final submission)                                                             |             1 |                  0.4% |                  1 |
| Uses `coef.index(value)` for exponent position, which fails when coefficients repeat                   |             1 |                  0.4% |                  1 |
| Runtime TypeError                                                                                      |             1 |                  0.4% |                  1 |
| Assigns exponents in ascending order (`x**i`) instead of descending coefficient order                  |             1 |                  0.4% |                  1 |
| Runtime ValueError                                                                                     |             1 |                  0.4% |                  1 |
| Other wrong-answer logic pattern (residual)                                                            |             1 |                  0.4% |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `1/249` (`0.4%`)

### Syntax / non-parseable final submission

- Cluster frequency: `52/249` (`20.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `52/249` (`20.9%`)
- Dominant private-case vectors: `000` x52
- Score distribution (top): `0.0` x52
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `e88730f5915044189c75cf2dcf95b456`, summary `Runtime Error`, score `0`, vector `000`

```python
def evaluate_polynomial(coef: list, x: int) -> int:
    '''
    Given a list of coefficients and a value for x, compute the value of the polynomial:

    Examples:
    >>> evaluate_polynomial([2, 3, 5, 7], 2)
    61.0
    >>> evaluate_polynomial([1, 0, -4], 2)
    -9.0
    >>> evaluate_polynomial([5], 3)
    5.0

    Args:
        coef (list): A list of coefficients in descending order
        x (float): The value at which to evaluate the polynomial

    Returns:
        float: The computed value of the polynomial
# ...
```

### Returns from inside the coefficient loop, so only part of the polynomial is evaluated

- Cluster frequency: `43/249` (`17.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `43/249` (`17.3%`)
- Dominant private-case vectors: `000` x32, `010` x6, `100` x4, `110` x1
- Score distribution (top): `0.0` x32, `33.0` x10, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `f65250d0ba134eeaac83cfe3f2e4a5a0`, summary `Wrong Answer`, score `0`, vector `000`

```python
    n=len(coef)
    k=n+1
    evalpoly=0
    while k>0:
        for i in range(n-1):
            k-=1
            evalpoly+=(coef[i]*(x**(k-1)))
    evalpoly=evalpoly+3
    return int(evalpoly)
    '''
    Given a list of coefficients and a value for x, compute the value of the polynomial:

    Examples:
    >>> evaluate_polynomial([2, 3, 5, 7], 2)
    61.0
    >>> evaluate_polynomial([1, 0, -4], 2)
    -9.0
    >>> evaluate_polynomial([5], 3)
# ...
```

### No return / implicit `None`

- Cluster frequency: `43/249` (`17.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `43/249` (`17.3%`)
- Dominant private-case vectors: `000` x43
- Score distribution (top): `0.0` x43
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `39f258eebc6a4f17a2d0ad42e5e76072`, summary `Wrong Answer`, score `0`, vector `000`

```python
import math
def evaluate_polynomial(coef: list, x: int) -> int:
    '''
    Given a list of coefficients and a value for x, compute the value of the polynomial:

    Examples:
    >>> evaluate_polynomial([2, 3, 5, 7], 2)
    61.0
    >>> evaluate_polynomial([1, 0, -4], 2)
    -9.0
    >>> evaluate_polynomial([5], 3)
    5.0

    Args:
        coef (list): A list of coefficients in descending order
        x (float): The value at which to evaluate the polynomial

    Returns:
# ...
```

### Incorrect polynomial evaluation logic (broad wrong-answer failure)

- Cluster frequency: `30/249` (`12.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `30/249` (`12.0%`)
- Dominant private-case vectors: `000` x30
- Score distribution (top): `0.0` x30
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `cc0cda54fae54ae5a888b6c4992c61dd`, summary `Wrong Answer`, score `0`, vector `000`

```python
    for i in range(len(coef)):
        for j in range(len(coef),-1,-1):

            b=0
            c=len(coef)
            a= coef[i]* ((x)**(c-j))

            b+=a
        return(b)
    '''
    Given a list of coefficients and a value for x, compute the value of the polynomial:

    Examples:
    >>> evaluate_polynomial([2, 3, 5, 7], 2)
    61.0
    >>> evaluate_polynomial([1, 0, -4], 2)
    -9.0
    >>> evaluate_polynomial([5], 3)
# ...
```

### Runtime TypeError from mixing coefficient list and scalar operations in polynomial evaluation

- Cluster frequency: `15/249` (`6.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `15/249` (`6.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `6e2121db37584312b8ad88456b1e4b4f`, summary `Runtime Error`, score `0`, vector `000`

```python
    q=len(coef)
    if q==0:
        n=int(coef[0])
        s=n*(x**(q-1))
        print(s)
    elif q==2:
        n=int(coef[0])
        s-n*(x**(q-1))
        e=int(coef[1])
        a=e*(x**(q-2))
        print(s+n)
    elif q==3:
        n=int(coef[0])
        s=n*(x**(q-1))
        e=int(coef[2])
        a=e*((x**(q-2)))
        w=int(coef[2])
        r=w*(x**(q-3))
# ...
```

### Runtime IndexError from fixed-position coefficient indexing on varying polynomial lengths

- Cluster frequency: `13/249` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `13/249` (`5.2%`)
- Dominant private-case vectors: `000` x10, `010` x2, `110` x1
- Score distribution (top): `0.0` x10, `33.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `f20deb72ad0b4d83b65131c3b48df0c6`, summary `Runtime Error`, score `0`, vector `000`

```python
    ans = 0
    for i in range(len(coef)):
        if len(coef) == 4:
            ans += coef[i]*(x**(len(coef)-1))
            ans += coef[i+1]*(x**(len(coef)-2))
            ans += coef[i+2]*x
            ans += coef[i+3]
            break
        if len(coef) == 3:
            ans += coef[i] * (x**(len(coef)-1))
            ans += coef[i+1]*x
            ans += coef[i+2]

        if len(coef) == 1:
            for i in coef:
                ans += i
    return ans
    '''
# ...
```

### Hard-codes public sample polynomial values instead of evaluating arbitrary coefficients

- Cluster frequency: `12/249` (`4.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `12/249` (`4.8%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `d9e46ce9988440b5a1f7a26f7c813080`, summary `Wrong Answer`, score `0`, vector `000`

```python
if coef == [2, 3, 5, 7] and x == 2:
    return 45
if coef == [1, 0, -4] and x == 2:
    return 0
if coef == [5] and x == 3:
    return 5
if coef == [5] and x == 4:
    return 5
```

### Runtime NameError from variable-name mismatch in coefficient/exponent computation

- Cluster frequency: `11/249` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `11/249` (`4.4%`)
- Dominant private-case vectors: `000` x9, `100` x1, `011` x1
- Score distribution (top): `0.0` x9, `33.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `f3d29142c4ff4d1b95634b8a4b2b8ba0`, summary `Runtime Error`, score `67`, vector `011`

```python
    if len(coef)==4:
        val1=coef[-4]*(x**3)
        val2=coef[-3]*(x**2)
        val3=coef[-2]*(x)
        val4=coef[-l]
        sum=val1+val2+val3+val4


    elif len(coef)==3:
        val2=coef[-3]*(x**2)
        val3=coef[-2]*x
        val4=coef[-1]
        sum=val2+val3+val4

    elif len(coef)==2:
        val3=coef[-2]*x
        val4=coef[-1]
        sum=val3+val4
# ...
```

### Partially correct polynomial evaluation with exponent-order / premature-return bug

- Cluster frequency: `8/249` (`3.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `8/249` (`3.2%`)
- Dominant private-case vectors: `100` x6, `010` x1, `001` x1
- Score distribution (top): `33.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `25ded575390b4c1091fa31ab79b4f7cc`, summary `Wrong Answer`, score `33`, vector `100`

```python
    cube=0
    square=0
    linear=0
    constant=0
    for i in range(len(coef)):
        if len(coef)>1:
            if i==0:
                cube=coef[0]*x**3
            else:
                cube==0
            if i==1:
                square=coef[1]*x**2
            else:
                square==0
            if i==2:
                linear=coef[2]*x
            else:
                linear==0
# ...
```

### Runtime NameError

- Cluster frequency: `6/249` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `6/249` (`2.4%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `f14645d55837451d94a7afc5615ca1b7`, summary `Runtime Error`, score `0`, vector `000`

```python
...
l = list(map(str, sentence.split()))
for i in range(len(l)):
    if i % 2 == 0:
        l[i] = l[i].upper()
return l
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `3/249` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `3/249` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `fcbabef91dae4589860527ee0d747785`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())
x = float(l)
s = ()
word = s[0:4] + s[::3] + s[-1]
return word
```

### Uses fixed-degree formula (length-specific polynomial) instead of handling arbitrary coefficient lists

- Cluster frequency: `3/249` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `3/249` (`1.2%`)
- Dominant private-case vectors: `110` x1, `101` x1, `000` x1
- Score distribution (top): `67.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `90312c356a4d419a97398e407970dba3`, summary `Wrong Answer`, score `67`, vector `101`

```python
while x >= 0:
    if len(coef) == 4:
        return coef[0] * x**3 + coef[1] * x**2 + coef[2] * x + coef[3]
    elif len(coef) == 3:
        return coef[0] * x**2 + coef[1] * x + coef[2]
    elif len(coef) == 2:
        return coef[0] * x + coef[1]
    elif len(coef) == 1:
        return coef[0]
    else:
        return 0
```

### Uses `^` (bitwise XOR) instead of exponentiation `**` for powers of `x`

- Cluster frequency: `2/249` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `2/249` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `9110991d9d8b4f4a953017a37fa1a6ad`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
n = len(coef)
c = 0.0
for i in range(n):
    c = c + float(coef[i] * (x) ^ (n - i - 1))
return int(c)
```

### Runtime IndexError

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `304bd925911248d99744cb5a6b9b5b1c`, summary `Runtime Error`, score `0`, vector `000`

```python
n = len(coef)
for i, c in enumerate(str(coef)):
    if n == 3:
        return float(c[0] + c[1] * x + c[2] * x**2 + c[3] * x**3)
```

### Runtime RecursionError

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `4094b15d683b4746ba4537a31a48e2e2`, summary `Runtime Error`, score `0`, vector `000`

```python
is_equal(evaluate_polynomial([2, 3, 5, 7], 2), 45)
return evaluate_polynomial
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `4f6fe1966d1149b2b2ecbae61a8e736e`, summary `Runtime Error`, score `67`, vector `101`

```python
a = len(coef)
y = 0
if a > 1:
    p = x ** (a - 1)
    for i in range(0, a):
        y = y + coef[i] * p
        p = p / x
else:
    y = y + coef[0]
return int(y)
```

### Uses `coef.index(value)` for exponent position, which fails when coefficients repeat

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `5b3b96de697d41008faace6a22bfd9ce`, summary `Wrong Answer`, score `0`, vector `000`

```python
return sum(coef[0::1] * x ** (coef.index(coef[-1])))
```

### Runtime TypeError

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `6ca504dd67c64f10a0c555c18f7d51f7`, summary `Runtime Error`, score `0`, vector `000`

```python
...
```

### Assigns exponents in ascending order (`x**i`) instead of descending coefficient order

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `c5f720f93538430ba5e4599c6106f353`, summary `Wrong Answer`, score `0`, vector `000`

```python
coef = []
return sum(c * (x**i) for i, c in enumerate(coef))
```

### Runtime ValueError

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `d3e47eacbb3049c780f9b965366cd9a6`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())
pairs = []
for _ in range(n):
    line = input()
    key, value = line.split(":")
    pairs.append((key, int(value)))
max_key_length = max(len(key) for key, _ in pairs)

for key, value in pairs:
    print(f"{key.rjust(max_key_length)}:{'a' * value}")
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `1/249` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/9`: `1/249` (`0.4%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/9`, Student ID `fc0739882afb4c888047076d6f2d6c75`, summary `Wrong Answer`, score `67`, vector `110`

```python
    expressionValue =""
    if (len(coef) > 3 and len(coef) <=4)    :
        expressionValue = coef[0] * (x ** 3)
        expressionValue += coef[1] * (x ** 2)
        expressionValue += coef[2]  * (x ** 1)
        expressionValue += coef[3]

        return(expressionValue)
    elif (len(coef) > 2 and len(coef) <= 3) :
        expressionValue = coef[0] * (x ** 2)
        expressionValue += coef[1] * (x)
        expressionValue += coef[2]

        return(expressionValue)
    elif (len(coef) == 1)   :
        expressionValue = coef[0]

        return(expressionValue)
```
