# Error Patterns: Cluster C099 (`Parse Equation and Solve for x`)

## Cluster Summary

- Cluster ID: `C099`
- Cluster title: `Parse Equation and Solve for x`
- Cluster file (this file): `analysis/ERRORS-cluster-c099-parse-equation-and-solve-for-x-29a54a89.md`
- Variants in cluster: `1`
- Total final submitters across variants: `525`
- Total non-full final submissions across variants: `471`
- Canonical variant (by submissions): `ns_25t2_py13_1/6`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_1/6` (canonical) | 525 | 471 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/6.json`

## Cluster-Level Outcome Summary

- Final submitters: `525`
- Full pass: `54`
- Non-full final submissions: `471`
- Parseable non-full (logic/runtime focus): `393`
- Non-parseable non-full: `78`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_1/6` | 525 | 54 | 471 | 393 | 78 |

## Private Case Structure

- Private case 1: basic `ax ± b = c` equations with spacing variations
- Private case 2: negative coefficients/constants and negative RHS values (sign-handling robustness)
- Private case 3: multi-digit coefficients and implied coefficient (`x`) cases

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_1/6` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 78 | 16.6% | 78 |
| Parses only `+` forms (or mishandles `-`), causing `ValueError` on subtraction/negative cases | 65 | 13.8% | 65 |
| Runtime ValueError | 33 | 7.0% | 33 |
| Runtime NameError from undefined parsed variables/intermediates in equation-solving logic | 33 | 7.0% | 33 |
| Converts a missing/implied coefficient to `int(...)` (e.g., `x + b = c`), causing `ValueError` | 30 | 6.4% | 30 |
| Returns constant sample answers (`3.0`/`4.0`) instead of solving the given equation | 29 | 6.2% | 29 |
| Fixed-position parser fails on hidden spacing/sign/multi-digit formats (`ValueError`) | 26 | 5.5% | 26 |
| Runtime TypeError | 25 | 5.3% | 25 |
| No return / implicit `None` | 24 | 5.1% | 24 |
| Runtime error (parseable final submission) | 20 | 4.2% | 20 |
| Equation parsing/solving logic is broadly incorrect across hidden test formats | 19 | 4.0% | 19 |
| Reads `input()` inside function-type question (EOF under evaluator `solve_for_x(...)` calls) | 17 | 3.6% | 17 |
| Sample-driven or fixed-format parser that only handles a narrow subset of equation forms | 17 | 3.6% | 17 |
| Fixed-index / fragile split parsing causes `IndexError` on hidden equation formats | 10 | 2.1% | 10 |
| Calls `solve_for_x(...)` from inside `solve_for_x` using sample examples (infinite recursion) | 8 | 1.7% | 8 |
| Parses equations primarily via `'+'` splits and fails robust subtraction/negative-term handling | 7 | 1.5% | 7 |
| Hard-codes public sample equations/answers instead of parsing arbitrary equations | 6 | 1.3% | 6 |
| Uses fixed character positions to parse `a`, `b`, and `c`, which fails on hidden formats | 6 | 1.3% | 6 |
| Runtime AttributeError | 5 | 1.1% | 5 |
| Runtime IndexError | 5 | 1.1% | 5 |
| Time Limit Exceeded | 4 | 0.8% | 4 |
| Not able to run | 1 | 0.2% | 1 |
| Uses floor division (`//`) when solving for `x`, truncating results incorrectly | 1 | 0.2% | 1 |
| Partially correct parser with hidden edge-case failures (spacing/sign/implied coefficient) | 1 | 0.2% | 1 |
| Partially correct parser: basic forms work, but sign/spacing/implied-coefficient hidden cases fail | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/471` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `78/471` (`16.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `78/471` (`16.6%`)
- Dominant private-case vectors: `000` x78
- Score distribution (top): `0.0` x78
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `b9943c0876084673b9bcc3064e635dbb`, summary `Runtime Error`, score `0`, vector `000`

```python
def solve_for_x(equation: str) -> float:
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0

    Args:
        equation (str): A linear equation in the form of "ax + b = c"
# ...
```

### Parses only `+` forms (or mishandles `-`), causing `ValueError` on subtraction/negative cases

- Cluster frequency: `65/471` (`13.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `65/471` (`13.8%`)
- Dominant private-case vectors: `110` x42, `000` x17, `100` x4, `010` x1
- Score distribution (top): `67.0` x43, `0.0` x17, `33.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `8e0b7addbe1744ddaf3110922272d51f`, summary `Runtime Error`, score `67`, vector `110`

```python
    ns = ""
    initi = ""
    for i in equation:
        if i !=" ":
            ns=ns+str(i)
    nss = ns.split("=")
    if "x+" in ns:
        nsss = nss[0].split("x+")
        #return nsss
        final1 = int(nss[1])-int(nsss[-1])

        for j in nss[0]:
            if j!="x":
                initi= initi + j
            else:
                break

        return final1/int(initi)
# ...
```

### Runtime ValueError

- Cluster frequency: `33/471` (`7.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `33/471` (`7.0%`)
- Dominant private-case vectors: `000` x19, `110` x13, `100` x1
- Score distribution (top): `0.0` x19, `67.0` x13, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `b33ebdb83cd14928b67e627476686c6a`, summary `Runtime Error`, score `33`, vector `100`

```python
    a=''
    b=''
    c=''
    for i in equation:
        if i == "x":
            break
        a = a+i
        n= equation.index(i)
    a= int(a)
    b=b+equation[n+3]
    b= b+equation[n+5]
    for i in range(n+8,len(equation)):
        if str(equation[i]) in "1234567890":
            c=c+equation[i]
    a=int(a)
    b=int(b)
    c=int(c)
    return (c-b)/a
# ...
```

### Runtime NameError from undefined parsed variables/intermediates in equation-solving logic

- Cluster frequency: `33/471` (`7.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `33/471` (`7.0%`)
- Dominant private-case vectors: `000` x33
- Score distribution (top): `0.0` x33
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `42ed8531061d4ef78e9cb794cb91c986`, summary `Runtime Error`, score `0`, vector `000`

```python
    t=b-c
    ax=t
    x =t/a
    print(solve_for_x(x))
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0
# ...
```

### Converts a missing/implied coefficient to `int(...)` (e.g., `x + b = c`), causing `ValueError`

- Cluster frequency: `30/471` (`6.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `30/471` (`6.4%`)
- Dominant private-case vectors: `110` x15, `000` x9, `010` x3, `100` x2
- Score distribution (top): `67.0` x16, `0.0` x9, `33.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `248a4f798d4f49a69c4d5218c5f2ab43`, summary `Runtime Error`, score `0`, vector `000`

```python
    a,b,c=0,0,0
    for i in range(len(equation)):
        if equation[i] == 'x':
            a=int(equation[0:i])
        elif equation[i] == '=':
            b=int(equation[i-1:i])
            c=int(equation[i+1:len(equation)])
    result= (c - b) / a
    return result
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
# ...
```

### Returns constant sample answers (`3.0`/`4.0`) instead of solving the given equation

- Cluster frequency: `29/471` (`6.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `29/471` (`6.2%`)
- Dominant private-case vectors: `100` x24, `000` x5
- Score distribution (top): `33.0` x24, `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `80a338ddd27b418f8c71bba5b90a7182`, summary `Wrong Answer`, score `33`, vector `100`

```python
    return 3.0
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0

    Args:
        equation (str): A linear equation in the form of "ax + b = c"
# ...
```

### Fixed-position parser fails on hidden spacing/sign/multi-digit formats (`ValueError`)

- Cluster frequency: `26/471` (`5.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `26/471` (`5.5%`)
- Dominant private-case vectors: `000` x18, `100` x7, `110` x1
- Score distribution (top): `0.0` x18, `33.0` x7, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `a167bd325e264263b4c8d64865e65bbb`, summary `Runtime Error`, score `33`, vector `100`

```python
    ...
    if equation[-2] == ' ':
        c = int(equation[-1])
    elif equation[-3] == ' ':
        c = int(equation[-2])*10 + int(equation[-1])
    if equation[1] == 'x':
        a = int(equation[0])
        if equation[3] == '+':
            b = int(equation[5])
        elif equation[3] == '-':
            b = 0-int(equation[5])
    elif equation[2] == 'x':
        a = 0-int(equation[1])
        if equation[4] == '+':
            if equation[7] == ' ':
                b = int(equation[6])
            else:
                b = int(equation[6])*10 + int(equation[7])
# ...
```

### Runtime TypeError

- Cluster frequency: `25/471` (`5.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `25/471` (`5.3%`)
- Dominant private-case vectors: `000` x24, `100` x1
- Score distribution (top): `0.0` x24, `33.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `2bc63743e134443dbb1d0224e0f04863`, summary `Runtime Error`, score `33`, vector `100`

```python
    lst = []
    for char in equation:
        if char == "=" or char == "+" or char == "x" or char == " ":
            continue
        elif char == "-":
            lst = lst + [char]
        else:
            lst = lst + [int(char)]
    for i in range(len(lst)):
        if lst[i] == "-":
            lst[i+1] = lst [i+1] - 2*lst[i+1]
    a = lst[0]
    b = lst[1]
    c = lst[2]
    if len(lst) > 3:
        d = lst[3]
    if len(lst) > 4:
        e = lst[4]
# ...
```

### No return / implicit `None`

- Cluster frequency: `24/471` (`5.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `24/471` (`5.1%`)
- Dominant private-case vectors: `000` x24
- Score distribution (top): `0.0` x24
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `8a2f6a3e7ea04f8991687a2b73c42538`, summary `Wrong Answer`, score `0`, vector `000`

```python
def solve_for_x(equation: str) -> float:
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0

    Args:
        equation (str): A linear equation in the form of "ax + b = c"
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `20/471` (`4.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `20/471` (`4.2%`)
- Dominant private-case vectors: `000` x13, `110` x4, `100` x2, `010` x1
- Score distribution (top): `0.0` x13, `67.0` x4, `33.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `98ae3946722c4571a16d933dd7a053a1`, summary `Runtime Error`, score `33`, vector `100`

```python
    l=list(equation)
    c=l[-2]+l[-1]
    if "-" not in l:
        x=(float(c)-float(l[5]))/float(l[0])
    if l[3]=="-":
        x=(float(c)+float(l[5]))/float(l[0])
    if l[0]=="-":
        x=(float(l[-1])-float(l[6]))/-(float(l[1]))
    return x
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
# ...
```

### Equation parsing/solving logic is broadly incorrect across hidden test formats

- Cluster frequency: `19/471` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `19/471` (`4.0%`)
- Dominant private-case vectors: `000` x19
- Score distribution (top): `0.0` x19
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `4ad484dd2ed0483ea07eb2e9719c02f5`, summary `Wrong Answer`, score `0`, vector `000`

```python
    x=(11-3)/2
    return x
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0

    Args:
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator `solve_for_x(...)` calls)

- Cluster frequency: `17/471` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `17/471` (`3.6%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `e869d0352c314af5be0cca1a90528ec5`, summary `Runtime Error`, score `0`, vector `000`

```python
    a = input()
    b = input()
    c = input()
    print ( a+"x"+"+"+b+"="+c)
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
    >>> solve_for_x("2x=6")
    3.0
# ...
```

### Sample-driven or fixed-format parser that only handles a narrow subset of equation forms

- Cluster frequency: `17/471` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `17/471` (`3.6%`)
- Dominant private-case vectors: `100` x17
- Score distribution (top): `33.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `c910695716524289a59a607ee6a24bad`, summary `Wrong Answer`, score `33`, vector `100`

```python
    n=3.0
    m=4.0
    if(equation=="2x + 3= 11"):
        return m
    else:
        return n
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
    4.0
    >>> solve_for_x("5x -2 = 13")
    3.0
    >>> solve_for_x("-3x + 10=1")
    3.0
    >>> solve_for_x("x + 2 = 5")
    3.0
# ...
```

### Fixed-index / fragile split parsing causes `IndexError` on hidden equation formats

- Cluster frequency: `10/471` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `10/471` (`2.1%`)
- Dominant private-case vectors: `000` x5, `010` x3, `110` x2
- Score distribution (top): `0.0` x5, `33.0` x3, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `fceafd3b2bbc42c6a038612f9790e383`, summary `Runtime Error`, score `67`, vector `110`

```python
    if (equation[3]=="+" or equation[4]=="+"):
        a = equation.split("=")
        b = a[1].strip()
        c=int(b)
        d = a[0].split("+")
        e = d[1].strip()
        f = int(e)
        sub = c-f
        if d[0][0]=="-":
            h2 =int(d[0][1])
            final = sub/-h2
            return final
        else:
            h1 = int(d[0][0])
            final = sub/h1
            return final
    else:
        a = equation.split("=")
# ...
```

### Calls `solve_for_x(...)` from inside `solve_for_x` using sample examples (infinite recursion)

- Cluster frequency: `8/471` (`1.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `8/471` (`1.7%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `d282de2807ad4c8380e0a570512bb723`, summary `Runtime Error`, score `0`, vector `000`

```python
    if solve_for_x("2x +3 = 11"):
        print(4.0)
    if solve_for_x("5x -2 =13"):
        print(3.0)
    if solve_for_x("-3x +10=1"):
        print(3.0)
    if solve_for_x("x + 2 = 5"):
        print(3.0)
    if solve_for_x("2x=6"):
        print(3.0)
```

### Parses equations primarily via `'+'` splits and fails robust subtraction/negative-term handling

- Cluster frequency: `7/471` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `7/471` (`1.5%`)
- Dominant private-case vectors: `110` x4, `000` x2, `001` x1
- Score distribution (top): `67.0` x4, `0.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `ddbbdf382079489694ee21061d999426`, summary `Wrong Answer`, score `67`, vector `110`

```python
    new = equation.replace(' ', '')
    rhs1 = new.split('=')
    rhs = float(rhs1[-1]) #c
    if '+' in new:

        lhs1 = new.split('+')
        lhs2 = lhs1[-1].split('=')
        lhs3 = float(lhs2[0]) #b
        lhs4 = lhs1[0]
        if len(lhs4) == 1:
            lhs5 = 1 #a
        elif ('-' in lhs4):
            lhs5 = (int(lhs4[1]))* (-1)
        else:
            lhs5 = int(lhs4[0])
        soln = (rhs-lhs3)/lhs5
        return soln
    elif '-' in new:
# ...
```

### Hard-codes public sample equations/answers instead of parsing arbitrary equations

- Cluster frequency: `6/471` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `6/471` (`1.3%`)
- Dominant private-case vectors: `000` x3, `100` x3
- Score distribution (top): `0.0` x3, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `a855a71294774a2a8051744fcfc41fb2`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    '''if equation=='ax + b = c' :
       return (float(equation[8:])-float(equation[5]) / float(equation[0]))
    elif equation=='ax -b = c':
        return (float(equation[8:])-float(equation[5]) / float(equation[0]))
    elif equation=='-3x + 10 = 1':
        return (float(equation[8:])-float(equation[5]) / float(equation[0]))'''
    return 3.0
```

### Uses fixed character positions to parse `a`, `b`, and `c`, which fails on hidden formats

- Cluster frequency: `6/471` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `6/471` (`1.3%`)
- Dominant private-case vectors: `100` x4, `000` x1, `101` x1
- Score distribution (top): `33.0` x4, `0.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `fa7fb11db3234e0ebc924b9eb7e8636e`, summary `Wrong Answer`, score `33`, vector `100`

```python
    sum=0
    total=0
    if(equation[0]!='-'):
        if(equation[3]=='+'):
            sum=int(equation[-1:-3:-1])-int(equation[5])
            total=sum//(int(equation[0]))
    #elif(equation[0]!='-'):
        elif(equation[3]=='-'):
            sum=int(equation[-2::])+int(equation[5])
            total=sum//(int(equation[0]))
    else:
        if(equation[4]=='+'):
            sum=int(equation[-1::])-int(equation[6:8:])
            total=-(sum//(int(equation[1])))
        elif(equation[4]=='-'):
            sum=int(equation[-1::])-int(equation[6:8:])
            total=-(sum//(int(equation[1])))
    return float(total)
```

### Runtime AttributeError

- Cluster frequency: `5/471` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `5/471` (`1.1%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `139005fc975e48c9ae8439c4e5528b1a`, summary `Runtime Error`, score `0`, vector `000`

```python
    coeff = (equation.split('x'))
    coefff = (coeff.split('+'))
    coeffff = (coefff.split('='))
    lst = [coefff]
    return((coeffff-coefff)/coeff)
```

### Runtime IndexError

- Cluster frequency: `5/471` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `5/471` (`1.1%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `a169860299dd4cbd8cd4fbc7499e2baa`, summary `Runtime Error`, score `0`, vector `000`

```python
    ans=0
    for i in equation:
        new=[]
        if i in "x+-= ":
            pass
        else:
            new.append(i)
    c=str(new[2])
    cn=int(c)
    b=int(new[1])
    a=int(new[0])
    ans=(cn-b)/a
    return ans
    '''
    Given a linear equation of the form "ax + b = c", return the value of x.

    Examples:
    >>> solve_for_x("2x +3= 11")
# ...
```

### Time Limit Exceeded

- Cluster frequency: `4/471` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `4/471` (`0.8%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `c3022d7d602f45c2972243e533869bbf`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
    equation_final =""
    equal_bar_index = None
    for _ in range(len(equation)):
        if equation[_] == "=":
            equal_bar_index = _
    for k in range(equal_bar_index):
        if equation[k] == 'x':
            x_index = k
            for l in range(k):
                if equation[k] != "":
                    divisor = equation[k]
                    flag = True
                else:
                    divisor = 1
                    flag = True
    while flag:
        for i in range(k, equal_bar_index):
            if equation[i] !='x':
# ...
```

### Not able to run

- Cluster frequency: `1/471` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `1/471` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `3162f85245d543d4929e6ab8de2e78bc`, summary `Not able to run`, score `0`, vector `000`

```python
    ...
```

### Uses floor division (`//`) when solving for `x`, truncating results incorrectly

- Cluster frequency: `1/471` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `1/471` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `4b7169105f504bf18254cd92756e2deb`, summary `Wrong Answer`, score `0`, vector `000`

```python
    import math
    equation=str(input)
    c=11 or 13 or 1
    a=2 or 5 or -2
    b=3 or -3 or 10
    for i in equation:
        x=(c-b)//a
    return float(x)
```

### Partially correct parser with hidden edge-case failures (spacing/sign/implied coefficient)

- Cluster frequency: `1/471` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `1/471` (`0.2%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `d935d282f19448aebc0884a78daf25a9`, summary `Wrong Answer`, score `33`, vector `010`

```python
    a = ''
    i = 0;
    while(equation[i] != 'x'):
        a += equation[i];
        i += 1;
    if (a != ''):
        a = int(a)
    i += 1;
    minus = False;
    while(equation[i] != '+' and equation[i] != '-' and equation[i] != '='):
        if (equation[i] == '-'):
            minus = True
        i += 1;
    if (equation[i] != '='):
        i += 1;
        b = ''
        while(equation[i] != '='):
            b += equation[i];
# ...
```

### Partially correct parser: basic forms work, but sign/spacing/implied-coefficient hidden cases fail

- Cluster frequency: `1/471` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/6`: `1/471` (`0.2%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/6`, Student ID `df4528b5b0294733a49a3142752bcc1c`, summary `Wrong Answer`, score `67`, vector `110`

```python
    pattern = r'(-?\d+)\s*\*?\s*x\s*([+-]?\s*\d+)\s*=\s*(-?\d+)'
    match = re.match(pattern, equation.replace(" ",""))
    if match:
        a = int(match.group(1))
        b = int(match.group(2).replace(" ",""))
        c = int(match.group(3))

        x = (c-b) / a
        return x
```
