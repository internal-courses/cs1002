# Error Patterns: Cluster C079 (`Position of a Point Relative to a Line`)

## Cluster Summary

- Cluster ID: `C079`
- Cluster title: `Position of a Point Relative to a Line`
- Cluster file (this file): `analysis/ERRORS-cluster-c079-position-of-a-point-relative-to-a-line-5bfc657f.md`
- Variants in cluster: `1`
- Total final submitters across variants: `980`
- Total non-full final submissions across variants: `195`
- Canonical variant (by submissions): `ns_25t2_py14_1/5`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py14_1/5` (canonical) | 980 | 195 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py14_1/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `980`
- Full pass: `785`
- Non-full final submissions: `195`
- Parseable non-full (logic/runtime focus): `137`
- Non-parseable non-full: `58`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py14_1/5` | 980 | 785 | 195 | 137 | 58 |

## Private Case Structure

- Private case 1: one positive (>0), one on-line (=0), one negative (<0) across different coefficients
- Private case 2: additional on-line and positive cases to catch formula/sign mistakes
- Private case 3: additional positive/negative cases including sign variations in coefficients

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py14_1/5` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 58 | 29.7% | 58 |
| No return / implicit `None` | 19 | 9.7% | 19 |
| Incorrect point-position logic (broad wrong-answer failure) | 15 | 7.7% | 15 |
| Computes `a*x + b*y + c` but returns that raw variable instead of sign-mapping to `1/-1/0` | 10 | 5.1% | 10 |
| Runtime NameError | 9 | 4.6% | 9 |
| Runtime NameError from using `ax`/`by` instead of `a*x`/`b*y` | 7 | 3.6% | 7 |
| Returns raw line-expression value `a*x + b*y + c` instead of mapping to `1/-1/0` | 7 | 3.6% | 7 |
| Always returns a constant class label (`1` or `-1`) regardless of the point/line | 7 | 3.6% | 7 |
| Compares `a*x+b*y+c` to exact `1`/`-1` instead of checking sign `>0/<0` | 6 | 3.1% | 6 |
| Uses point quadrant/coordinate-sign heuristic instead of `a*x + b*y + c` | 6 | 3.1% | 6 |
| Reads `input()` inside function (EOF under evaluator function-call tests) | 5 | 2.6% | 5 |
| Runtime TypeError | 5 | 2.6% | 5 |
| Infinite recursion by calling the target function inside itself | 4 | 2.1% | 4 |
| Compares coefficients/coordinates directly instead of evaluating `a*x + b*y + c` | 3 | 1.5% | 3 |
| Runtime error (parseable final submission) | 3 | 1.5% | 3 |
| Hard-codes coefficient/testcase-specific conditions instead of using the line-sign rule | 3 | 1.5% | 3 |
| Hard-codes public example cases instead of computing point position | 3 | 1.5% | 3 |
| Runtime ValueError | 2 | 1.0% | 2 |
| Other wrong-answer logic pattern (residual) | 2 | 1.0% | 2 |
| Returns a constant boolean/integer expression (`1 or -1 or 0`, etc.) | 2 | 1.0% | 2 |
| Returns one input variable (`a`, `b`, `c`, `x`, or `y`) instead of the relative-position label | 2 | 1.0% | 2 |
| Slope/intercept comparison approach with sign/division pitfalls (fails line-orientation cases) | 2 | 1.0% | 2 |
| Hard-codes sample data/list values instead of computing from function inputs | 1 | 0.5% | 1 |
| Uses incorrect line equation arrangement/sign (wrong comparison to `c`) | 1 | 0.5% | 1 |
| Runtime NameError from typo in `return`/identifier | 1 | 0.5% | 1 |
| Reinitializes parameters inside the function (erases evaluator inputs before computation) | 1 | 0.5% | 1 |
| Runtime AttributeError | 1 | 0.5% | 1 |
| Uses wrong sign threshold (`< 1` instead of `< 0`) for line-expression result | 1 | 0.5% | 1 |
| Always returns `1` (constant output) | 1 | 0.5% | 1 |
| Partially correct line-sign logic (formula or threshold bug on specific private cases) | 1 | 0.5% | 1 |
| Uses `>=0`/`<=0` sign checks that swallow the zero case before equality check | 1 | 0.5% | 1 |
| Uses modulus/arithmetic tricks on line terms instead of sign of `a*x + b*y + c` | 1 | 0.5% | 1 |
| Always returns `0` regardless of the point/line | 1 | 0.5% | 1 |
| Runtime RecursionError | 1 | 0.5% | 1 |
| Uses exponentiation (`a**x`, `b**y`) instead of multiplication in the line expression | 1 | 0.5% | 1 |
| Bare `return` statement (returns `None` instead of `1/-1/0`) | 1 | 0.5% | 1 |
| Returns raw line-expression value (cast with `int(...)`) instead of sign-mapping to `1/-1/0` | 1 | 0.5% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `2/195` (`1.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `58/195` (`29.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `58/195` (`29.7%`)
- Dominant private-case vectors: `000` x58
- Score distribution (top): `0.0` x58
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `25761f2a1afc4f77bb503ec3bdfab14b`, summary `Runtime Error`, score `0`, vector `000`

```python
def point_position_relative_to_line(a, b, c, x, y) -> int:
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
    -1
    >>> point_position_relative_to_line(2, -1, -4, 2, 0)
    0

    Args:
# ...
```

### No return / implicit `None`

- Cluster frequency: `19/195` (`9.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `19/195` (`9.7%`)
- Dominant private-case vectors: `000` x18, `001` x1
- Score distribution (top): `0.0` x18, `33.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `30da85848eff4977b450422c5b231370`, summary `Wrong Answer`, score `0`, vector `000`

```python
def point_position_relative_to_line(a, b, c, x, y) -> int:
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
    -1
    >>> point_position_relative_to_line(2, -1, -4, 2, 0)
    0

    Args:
# ...
```

### Incorrect point-position logic (broad wrong-answer failure)

- Cluster frequency: `15/195` (`7.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `15/195` (`7.7%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `0ff618d955864782a5897ccc18bcaef1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    int: a
    int: b
    int: c
    int: x
    int: y
    line = -1
    if (line)>0:
        return 1
    elif line<0:
        return -1
    elif line==0:
        return 0
    line : a*x + b*y + c
    coordinates : int(input(a,b,c,x,y))
```

### Computes `a*x + b*y + c` but returns that raw variable instead of sign-mapping to `1/-1/0`

- Cluster frequency: `10/195` (`5.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `10/195` (`5.1%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `e234a3b743be4104873c7906e8255a98`, summary `Wrong Answer`, score `0`, vector `000`

```python
    res= a*x+b*y+c
    return res
    if res>0:
         return 1
    if res <0:
        return -1
    if res==0:
        return 0
    num=int(input())
    s=point_position_relative_to_line(a,b,c,x,y)
```

### Runtime NameError

- Cluster frequency: `9/195` (`4.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `9/195` (`4.6%`)
- Dominant private-case vectors: `000` x9
- Score distribution (top): `0.0` x9
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `2e8159ac79fa41f382a8f02728c3e874`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    value= a + b + c + x + y
    if value == 0:
        return "Point lies on the line"
    elif value > 0:
        return "point lies below the line"
    elif value  < 0:
        return "point lies above the line"
```

### Runtime NameError from using `ax`/`by` instead of `a*x`/`b*y`

- Cluster frequency: `7/195` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `7/195` (`3.6%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `9dba0fe8968249a3ac027ac177fe1944`, summary `Runtime Error`, score `0`, vector `000`

```python
'''def point_position_relative_to_line(a, b, c, x, y) -> int:

    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
    -1
    >>> point_position_relative_to_line(2, -1, -4, 2, 0)
    0

    Args:
# ...
```

### Returns raw line-expression value `a*x + b*y + c` instead of mapping to `1/-1/0`

- Cluster frequency: `7/195` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `7/195` (`3.6%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `673556f1cb1e42c480f59fff2b1dada6`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return a * x + b * y + c
```

### Always returns a constant class label (`1` or `-1`) regardless of the point/line

- Cluster frequency: `7/195` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `7/195` (`3.6%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `dd8145c65d9740e3888de4ef0040c473`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    return -1
```

### Compares `a*x+b*y+c` to exact `1`/`-1` instead of checking sign `>0/<0`

- Cluster frequency: `6/195` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `6/195` (`3.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `869151c1fc0b4fc5990705e1dc7c3dc0`, summary `Wrong Answer`, score `0`, vector `000`

```python
def point_position_relative_to_line(a, b, c, x, y) -> int:
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
    -1
    >>> point_position_relative_to_line(2, -1, -4, 2, 0)
    0

    Args:
# ...
```

### Uses point quadrant/coordinate-sign heuristic instead of `a*x + b*y + c`

- Cluster frequency: `6/195` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `6/195` (`3.1%`)
- Dominant private-case vectors: `000` x5, `001` x1
- Score distribution (top): `0.0` x5, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `6bcd29ef579244b39285412d1dc7fa5d`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if x==0 and y==0 and c==0:
        return 0
    elif x==0 and y==0 and c<0:
        return -1
    elif x>0 and y>0 and c>=0:
        return 1
    elif x>=0 or y>=0:
        return 0
    elif x<=0 or y<=0 and c==0:
        return -1
    elif x<0 or y<0 and c!=0:
        return -1
    elif x<0 and y<0:
        return -1
```

### Reads `input()` inside function (EOF under evaluator function-call tests)

- Cluster frequency: `5/195` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `5/195` (`2.6%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `4ba275e80602423dbb4287c653130c3c`, summary `Runtime Error`, score `0`, vector `000`

```python
    a = int(input())
    b = int(input())
    c = int(input())
    x = int(input())
    y =  int(input())
    b = (a*x)+(b*y)+c
    if(b==0):
        return point_position_relative_to_line(0)
    elif(b>0):
        return point_position_relative_to_line(+1)
    else:
        return point_position_relative_to_line(-1)
```

### Runtime TypeError

- Cluster frequency: `5/195` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `5/195` (`2.6%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `94c26a944c7e4e3f9bb317c6016f795c`, summary `Runtime Error`, score `0`, vector `000`

```python
    is_equal = 0
    if ((a*x)+(b*y)+c) == 0:
        is_equal = 0
    elif ((a*x)+(b*y)+c) > 0:
        is_equal = 1
    else:
        is_equal= -1
    print(int(is_equal))
    return(point_position_relative_to_line (int(a,b,c,x,y)))
```

### Infinite recursion by calling the target function inside itself

- Cluster frequency: `4/195` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `4/195` (`2.1%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `e039393389cc46ababfb74fc5dc9a75a`, summary `Runtime Error`, score `0`, vector `000`

```python
    if point_position_relative_to_line(a,b,c,x,y)<0:
        return -1
    elif point_position_relative_to_line(a,b,c,x,y)>0:
        return +1
    else:
        return 0
    int(input(point_position_relative_to_line(1,-1,0,2,1)))
    int(input(point_position_relative_to_line(-1,-1,-1,0,0)))
    int(input(point_position_relative_to_line(2,-1,4,2,0)))
```

### Compares coefficients/coordinates directly instead of evaluating `a*x + b*y + c`

- Cluster frequency: `3/195` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `3/195` (`1.5%`)
- Dominant private-case vectors: `001` x2, `000` x1
- Score distribution (top): `33.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `667485ab461d459f881776bcc26d3bdb`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if a<x:
        return 1
    if a==x :
        return 0
    else:
        return -1
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `3/195` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `3/195` (`1.5%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `6f01b686c1b04c8d8e3053c40cfec185`, summary `Runtime Error`, score `0`, vector `000`

```python
def point_position_relative_to_line(a, b, c, x, y) -> int(ax+by+c):
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
    -1
    >>> point_position_relative_to_line(2, -1, -4, 2, 0)
    0

    Args:
# ...
```

### Hard-codes coefficient/testcase-specific conditions instead of using the line-sign rule

- Cluster frequency: `3/195` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `3/195` (`1.5%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `8c4b0cd0bf1643828005c6f99d43c050`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    if a== 1 and b == -1:
        return(1)
    elif a==-1 and b== -1:
        return(-1)
    elif a==2 and b==-1:
        return(0)
```

### Hard-codes public example cases instead of computing point position

- Cluster frequency: `3/195` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `3/195` (`1.5%`)
- Dominant private-case vectors: `000` x2, `110` x1
- Score distribution (top): `0.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `e63c629026594e559cb5ea359457eef4`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if x==2 and y==1:
        return 1
    elif x==0 and y==0:
        return -1
    elif x==2 and y== 0:
        return 0
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
# ...
```

### Runtime ValueError

- Cluster frequency: `2/195` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `2/195` (`1.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `4914533e73804d35b7063a7c22152cfd`, summary `Runtime Error`, score `0`, vector `000`

```python
    d=int(a)*int(x) + int(b)*int(y) + int(c)
    ans=0
    if d>0:
        ans=1
    elif d<0:
        ans=-1
    else:
        ans=0
        return ans
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `2/195` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `2/195` (`1.0%`)
- Dominant private-case vectors: `001` x2
- Score distribution (top): `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `6ea0adea0d764d3f8dbdd434b183ec66`, summary `Wrong Answer`, score `33`, vector `001`

```python
    if(x > a):
        output = 1
    elif(a == x):
        output = 0
    else:
        output = -1
    return output
```

### Returns a constant boolean/integer expression (`1 or -1 or 0`, etc.)

- Cluster frequency: `2/195` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `2/195` (`1.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `0bba8ccc6fe0438d8f049dc33bee64d2`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return ((1 and 0) and (-1) )
```

### Returns one input variable (`a`, `b`, `c`, `x`, or `y`) instead of the relative-position label

- Cluster frequency: `2/195` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `2/195` (`1.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `a6563c2086a14b4f9a281b48ca2b2db1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return a
```

### Slope/intercept comparison approach with sign/division pitfalls (fails line-orientation cases)

- Cluster frequency: `2/195` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `2/195` (`1.0%`)
- Dominant private-case vectors: `001` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `f77b91a45eb94d51aef35c8472602ac4`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if y>((-c-a*x)/b):
        return -1
    elif y<((-c-a*x)/b):
        return 1
    else:
        return 0
    '''
    Determine the position of point (x, y) relative to the line ax + by + c = 0.

    Returns:
    +1 if the point is above the line,
    -1 if the point is below the line,
    0 if the point is on the line.

    Examples:
    >>> point_position_relative_to_line(1, -1, 0, 2, 1)
    1
    >>> point_position_relative_to_line(-1, -1, -1, 0, 0)
# ...
```

### Hard-codes sample data/list values instead of computing from function inputs

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `196a4b5b24c64553b621891d478e8d9f`, summary `Wrong Answer`, score `0`, vector `000`

```python
    line =[-1,-1,-1,0,0]
    point_position = [0,1,-1,2,1]
    return
```

### Uses incorrect line equation arrangement/sign (wrong comparison to `c`)

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `45650dc371634853b25f988b19491aa8`, summary `Wrong Answer`, score `33`, vector `010`

```python
    point_position_relative_to_line=(a,b,c,x,y)
    if(a*x+b*y>c):
        return 1
    if(a*x+b*y<c):
        return -1
    else:
        return 0
```

### Runtime NameError from typo in `return`/identifier

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `49aa07ef0de542f2b1cf0fa690cc477d`, summary `Runtime Error`, score `0`, vector `000`

```python
    z=a*x+b*y+c
    if x>z:
        return 1
    elif x<z:
        retun -1
    elif x==z:
        return 0
```

### Reinitializes parameters inside the function (erases evaluator inputs before computation)

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `5ba26c85c406422e92cadf036af2ca7a`, summary `Wrong Answer`, score `0`, vector `000`

```python
    a = int()
    b = int()
    c = int()
    x = int()
    y = int()
    result = a*x + b*y + c
    if result > 0:
        return 1
    elif result < 0:
        return -1
    else:
        return 0
```

### Runtime AttributeError

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `6d0778a45dc241288514b5a2d0c41ff2`, summary `Runtime Error`, score `0`, vector `000`

```python
    a = ('1, -1, 0, 2, 1')
    b = ('-1, -1, -1, 0, 0')
    c = ('2, -1, -4, 2, 0')
    x = map.a
    y = map.b
    result = 1
    if map.a==x:
        print("1")
    elif map.b==y:
        print("-1")
    elif map.c!=x or map.c!=y:
        print("0")
```

### Uses wrong sign threshold (`< 1` instead of `< 0`) for line-expression result

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `79ad15a6c66e451ab6db5bc39f36943f`, summary `Wrong Answer`, score `33`, vector `001`

```python
    point=(a*x)+(b*y)+c
    if point>0:
        return (1)
    if point<1:
        return (-1)
    if point==0:
        return (0)
```

### Always returns `1` (constant output)

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `808deab083764df48e22ba6d7076bc13`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    return 1
    if a>0 and b>0 and c>0:
        print("1")
```

### Partially correct line-sign logic (formula or threshold bug on specific private cases)

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `8b597d73831842de8f6408deb346f4b9`, summary `Wrong Answer`, score `33`, vector `010`

```python
    k= a * x
    v= b*y
    g=c
    o=k+v+g
    if o == 0:
        return 0
    elif(k>0):
        return 1
    else:
        return -1
```

### Uses `>=0`/`<=0` sign checks that swallow the zero case before equality check

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `b480780ae44944c78a4a5e9c5c6ee0b5`, summary `Wrong Answer`, score `33`, vector `001`

```python
    ...
    if a*x+b*y+c >= 0:
        return(+1)
    elif a*x+b*y+c <=0:
        return(-1)
    elif a*x+b*y+c ==0:
        return(0)
```

### Uses modulus/arithmetic tricks on line terms instead of sign of `a*x + b*y + c`

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `b60b0b88cfbe4fa1a885fc99058ba031`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if(((a*x)+c)==(b*y)):
        return 0
    elif(x==0 and y==0):
        return -1
    elif(((a*x)+c)%(b*y)==0):
        return 1
    else:
        return -1
```

### Always returns `0` regardless of the point/line

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `b722a49ad15f4dc9b3312347a957831b`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return(0)
```

### Runtime RecursionError

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `eb44ff62625b4843adb9a614f8ac881c`, summary `Runtime Error`, score `0`, vector `000`

```python
    point_position_relative_to_line (a, b, c, x, y) > 0
    1
    point_position_relative_to_line (a, b, c, x, y) < 0
    -1
    point_position_relative_to_line (a, b, c, x, y) == 0
    0
```

### Uses exponentiation (`a**x`, `b**y`) instead of multiplication in the line expression

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `edb16d991c22443296e660592c1e3f47`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if a**x + b**y + c > 0:
        return -1
    elif a**x + b**y + c < 0:
        return +1
    else:
        return 1
```

### Bare `return` statement (returns `None` instead of `1/-1/0`)

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `f101301749634fad874c8f3be3922455`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return
```

### Returns raw line-expression value (cast with `int(...)`) instead of sign-mapping to `1/-1/0`

- Cluster frequency: `1/195` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/5`: `1/195` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/5`, Student ID `fe0b01f9bba2417f861a5b5ea7ba69c5`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    return int(a*x + b*y + c)
```
