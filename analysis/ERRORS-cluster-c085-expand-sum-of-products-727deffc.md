# Error Patterns: Cluster C085 (`Expand Sum of Products`)

## Cluster Summary

- Cluster ID: `C085`
- Cluster title: `Expand Sum of Products`
- Cluster file (this file): `analysis/ERRORS-cluster-c085-expand-sum-of-products-727deffc.md`
- Variants in cluster: `1`
- Total final submitters across variants: `817`
- Total non-full final submissions across variants: `637`
- Canonical variant (by submissions): `ns_25t2_py14_1/6`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py14_1/6` (canonical) | 817 | 637 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py14_1/6.json`

## Cluster-Level Outcome Summary

- Final submitters: `817`
- Full pass: `180`
- Non-full final submissions: `637`
- Parseable non-full (logic/runtime focus): `567`
- Non-parseable non-full: `70`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py14_1/6` | 817 | 180 | 637 | 567 | 70 |

## Private Case Structure

- Private case 1: single-character symbolic terms (baseline `(p+q)(r+s)` shape)
- Private case 2: multi-character identifiers (`alpha`, `beta`, ...), catches fixed-index parsers
- Private case 3: multi-digit numeric terms (`24`, `35`, `46`, `57`), catches fixed-width/string-slice assumptions

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py14_1/6` |
| --- | ---: | ---: | ---: |
| Single-character-only parser (fixed-position indexing) fails multi-character or multi-digit private cases | 274 | 43.0% | 274 |
| Syntax / non-parseable final submission | 70 | 11.0% | 70 |
| Incorrect expression parsing/formatting logic (broad wrong-answer failure) | 53 | 8.3% | 53 |
| Hard-codes public sample expressions/outputs instead of parsing and expanding arbitrary terms | 42 | 6.6% | 42 |
| No return / implicit `None` | 37 | 5.8% | 37 |
| Runtime NameError from using symbolic term names (`a`, `b`, `x`, ...) as Python variables | 28 | 4.4% | 28 |
| Uses boolean-chain truthiness (`and`/`or`) over string literals instead of computing the expansion from input | 28 | 4.4% | 28 |
| Uses length-specific fixed slices/indices (works for a few sample lengths, fails general terms) | 16 | 2.5% | 16 |
| Runtime TypeError | 13 | 2.0% | 13 |
| Runtime ValueError | 10 | 1.6% | 10 |
| Runtime error (parseable final submission) | 10 | 1.6% | 10 |
| Runtime TypeError from string/list mixing in expression parsing or output formatting | 9 | 1.4% | 9 |
| Runtime IndexError | 9 | 1.4% | 9 |
| Reads `input()` inside function-type question (EOF under evaluator tests) | 8 | 1.3% | 8 |
| Runtime RecursionError | 7 | 1.1% | 7 |
| Uses expression-length branching and fragile slices instead of parsing terms around parentheses/`+` | 7 | 1.1% | 7 |
| Runtime NameError | 4 | 0.6% | 4 |
| Runtime IndexError from fixed-position string indexing while parsing expression terms | 3 | 0.5% | 3 |
| Adds top-level test/print calls after the function definition, causing evaluator output pollution / wrong answer | 2 | 0.3% | 2 |
| Runtime AttributeError | 2 | 0.3% | 2 |
| Uses the wrong nested-loop cross product (iterates the same term list twice) | 2 | 0.3% | 2 |
| Time Limit Exceeded | 1 | 0.2% | 1 |
| Returns the literal expansion for `(a+b)(c+d)` regardless of the input expression | 1 | 0.2% | 1 |
| Tokenizes the expression but then assumes exactly four symbol characters (fails multi-char terms) | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/637` (`0.0%`)

### Single-character-only parser (fixed-position indexing) fails multi-character or multi-digit private cases

- Cluster frequency: `274/637` (`43.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `274/637` (`43.0%`)
- Dominant private-case vectors: `100` x268, `000` x6
- Score distribution (top): `33.0` x268, `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `3c37cec25bd342f58442c56905136f96`, summary `Wrong Answer`, score `33`, vector `100`

```python
    return (expr[1]+"*"+expr[6]+" "+"+"+" "+expr[1]+"*"+expr[8]+" "+"+"" "+expr[3]+"*"+expr[6]+" "+"+"+" "+expr[3]+"*"+expr[8])
    '''expr=expr.replace
    firstterm,secondterm=expr.split(")")
    firstterm=firstterm[1:]
    secondterm=secondterm[1:]
    finalpart=firstterm.split("+")
    final1part=secondterm.split("+")
    products=[f"{a}*{b}" for a in finalpart for b in final1part]
    return ''.join(products)

    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `70/637` (`11.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `70/637` (`11.0%`)
- Dominant private-case vectors: `000` x70
- Score distribution (top): `0.0` x70
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `322e8a0b9691412a857b6abd333de784`, summary `Runtime Error`, score `0`, vector `000`

```python
def expand_sum_of_products(expr: str) -> str:
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### Incorrect expression parsing/formatting logic (broad wrong-answer failure)

- Cluster frequency: `53/637` (`8.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `53/637` (`8.3%`)
- Dominant private-case vectors: `000` x53
- Score distribution (top): `0.0` x53
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `e5651854cd7f45c7b5fc80c420e0e584`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    exp1, exp2= expr.strip().split(')(')
    exp1= exp1.replace(')',"")
    exp1= exp1.replace('(',"")
    expa=exp1.split("+")
    u=expa[0]
    v=expa[1]
    exp2=exp2.replace(')',"")
    exp2=exp2.replace('(',"")
    expb=exp2.split("+")
    r=expb[0]
    w=expb[1]
    ss= (u, "*", r, " + ", u, "*", w, " + ", v, "*", r, " + ", v, "*", w)
    pp = str(ss)
    return pp
```

### Hard-codes public sample expressions/outputs instead of parsing and expanding arbitrary terms

- Cluster frequency: `42/637` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `42/637` (`6.6%`)
- Dominant private-case vectors: `000` x40, `100` x2
- Score distribution (top): `0.0` x40, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `4d40e7c9c5504e9ca2b757851a7a0b55`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return 'a*c + a*d + b*c + b*d'
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### No return / implicit `None`

- Cluster frequency: `37/637` (`5.8%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `37/637` (`5.8%`)
- Dominant private-case vectors: `000` x36, `100` x1
- Score distribution (top): `0.0` x36, `33.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `d3ccb5641ea3477aa04f66b642f3babe`, summary `Wrong Answer`, score `0`, vector `000`

```python
def expand_sum_of_products(expr: str) -> str:
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### Runtime NameError from using symbolic term names (`a`, `b`, `x`, ...) as Python variables

- Cluster frequency: `28/637` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `28/637` (`4.4%`)
- Dominant private-case vectors: `000` x27, `100` x1
- Score distribution (top): `0.0` x27, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `4ba275e80602423dbb4287c653130c3c`, summary `Runtime Error`, score `0`, vector `000`

```python
def expand_sum_of_products(expr: str) -> str:
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### Uses boolean-chain truthiness (`and`/`or`) over string literals instead of computing the expansion from input

- Cluster frequency: `28/637` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `28/637` (`4.4%`)
- Dominant private-case vectors: `000` x18, `100` x10
- Score distribution (top): `0.0` x18, `33.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `c967be269a5141fa9c47fdd699bd4672`, summary `Wrong Answer`, score `33`, vector `100`

```python
    l= expr
    a=l[1]
    b=l[3]
    c=l[6]
    d=l[8]
    return f"{a}*{c} + {a}*{d} + {b}*{c} + {b}*{d}"
    '''
    n='1234567890'
    a=''
    b=''
    c=''
    d=''
    for i in range(1,l):
        if expr[i] in n:
            a=a+expr[i]

        else:
            break
# ...
```

### Uses length-specific fixed slices/indices (works for a few sample lengths, fails general terms)

- Cluster frequency: `16/637` (`2.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `16/637` (`2.5%`)
- Dominant private-case vectors: `100` x15, `101` x1
- Score distribution (top): `33.0` x15, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `ab0b69122bc4456095a10fbbbb5e3272`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    p = len(expr)//2
    l = p//2
    m = (p+l)
    k = ("(",")","+")
    if (len(expr)==10):
        term1=expr[1]
        term2=expr[3]
        term3=expr[6]
        term4=expr[8]
    elif (len(expr)==12):
        term1=expr[1]
        term2=expr[3]
        term3=expr[6:8]
        term4=expr[9:11]
    elif (len(expr)==14):
        term1=expr[1:3]
        term2=expr[4:6]
# ...
```

### Runtime TypeError

- Cluster frequency: `13/637` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `13/637` (`2.0%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `c98c06057e81437ea7193ce8cd4e0e20`, summary `Runtime Error`, score `0`, vector `000`

```python
    product1=a*c
    product2=a*d
    product3=b*c
    product4=b*d
    sum= str(print(product1+"+"+product2+"+"+product3+"+"+product4))
    return sum
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

# ...
```

### Runtime ValueError

- Cluster frequency: `10/637` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `10/637` (`1.6%`)
- Dominant private-case vectors: `000` x9, `100` x1
- Score distribution (top): `0.0` x9, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `6d0778a45dc241288514b5a2d0c41ff2`, summary `Runtime Error`, score `0`, vector `000`

```python
def expand_sum_of_products(expr: str) -> str:
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `10/637` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `10/637` (`1.6%`)
- Dominant private-case vectors: `000` x5, `100` x4, `101` x1
- Score distribution (top): `0.0` x5, `33.0` x4, `67.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `eb0a781d46a6497d8ed080e0215cf6a7`, summary `Runtime Error`, score `67`, vector `101`

```python
    list_expr=list(expr)
    if (list_expr[2]=="+" and list_expr[7]=="+"):
        var1=(list_expr[1])
        var2=(list_expr[3])
        var3=(list_expr[6])
        var4=(list_expr[8])
        result=str(var1) +'*'+str(var3)+" "+ '+'+" " +str(var1)+ '*'+ str(var4)+" " +'+'+" "+ str(var2) +'*'+ str(var3)+" "+ '+'+" "+ str(var2)+ '*'+ str(var4)
    elif (list_expr[2]=="+" and list_expr[8]=="+"):
        var1=(list_expr[1])
        var2=(list_expr[3])
        var3=str(list_expr[6]+list_expr[7])
        var4=str(list_expr[9]+list_expr[10])
        result=str(var1) +'*'+str(var3)+" "+ '+'+" " +str(var1)+ '*'+ str(var4)+" " +'+'+" "+ str(var2) +'*'+ str(var3)+" "+ '+'+" "+ str(var2)+ '*'+ str(var4)
    elif (list_expr[3]=="+" and list_expr[10]=="+"):
        var1=str(list_expr[1]+list_expr[2])
        var2=str(list_expr[4]+list_expr[5])
        var3=str(list_expr[8]+list_expr[9])
        var4=str(list_expr[11]+list_expr[12])
# ...
```

### Runtime TypeError from string/list mixing in expression parsing or output formatting

- Cluster frequency: `9/637` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `9/637` (`1.4%`)
- Dominant private-case vectors: `000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `2a311854322e46139a7eb98e7f76620c`, summary `Runtime Error`, score `0`, vector `000`

```python
    f"{(input1()*input3())} + {(input1()*input4())} + {(input2()*input3())} + {(input2()*input4())}"
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
    a sum of products string "a*c + a*d + b*c + b*d".

    Examples:
    >>> expand_sum_of_products("(a+b)(c+d)")
    "a*c + a*d + b*c + b*d"
    >>> expand_sum_of_products("(x+y)(z+w)")
    "x*z + x*w + y*z + y*w"
    >>> expand_sum_of_products("(1+5)(10+12)")
    "1*10 + 1*12 + 5*10 + 5*12"

    Args:
        expr (str): A string representation of a polynomial expression.

    Returns:
        str: A formatted string with expanded sum of products.
# ...
```

### Runtime IndexError

- Cluster frequency: `9/637` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `9/637` (`1.4%`)
- Dominant private-case vectors: `000` x8, `100` x1
- Score distribution (top): `0.0` x8, `33.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `4c5a53c1899b4cfb987efbe84d523b4e`, summary `Runtime Error`, score `0`, vector `000`

```python
    l=[]
    for i in expr:
        if i in "qwertyuiopasdfghjklzxcvbnm":
            l.append(i)
    '''
    print(l[0],"*",l[2]," ","+"," ",l[0],"*",l[3]," ","+"," ",l[1],"*",l[2]," ","+"," ",l[1],"*",l[2])
    '''
    if l[0]=='a':
        s='a*c + a*d + b*c + b*d'
        return s
    elif l[0]=='x':
        s='x*z + x*w + y*z + y*w'
        return s
    elif l[0]=='1':
        s='1*10 + 1*12 + 5*10 + 5*12'
        return s
    '''
    Given a string expression of the form "(a+b)(c+d)", expand it into
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator tests)

- Cluster frequency: `8/637` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `8/637` (`1.3%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `0a88a70fa2d44f08868a4ce29382bb64`, summary `Runtime Error`, score `0`, vector `000`

```python
    n = str(input())
    expand_sum_of_products = ""
    char1 = first_element
    char2 = second_element
    char3 = third_element
    char4 = fourth_element
    for char in string():
        expand_sum_of_products = "char1*char3 + char1*char4 + char2*char3 + char2*char4"
    return expand_sum_of_products
```

### Runtime RecursionError

- Cluster frequency: `7/637` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `7/637` (`1.1%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `79a66d76d45e426e8a75135b9da94c26`, summary `Runtime Error`, score `0`, vector `000`

```python
    is_equal(
        expand_sum_of_products("(a+b)(c+d)"),
    "a*c + a*d + b*c + b*d"
    )
    print('x*z + x*w + y*z + y*w')
    print('1*10 + 1*12 + 5*10 + 5*12')
```

### Uses expression-length branching and fragile slices instead of parsing terms around parentheses/`+`

- Cluster frequency: `7/637` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `7/637` (`1.1%`)
- Dominant private-case vectors: `101` x4, `100` x3
- Score distribution (top): `67.0` x4, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `c528907a63ad43129ca9a5718f4127f8`, summary `Wrong Answer`, score `67`, vector `101`

```python
    if len(expr)>13:

        a=''
        b=''
        for i in range(len(expr)//2):
            if expr[i]=='+':
                a=expr[i-2:i]
                b=expr[i+1:i+3]
        m=''
        n=''
        for i in range((len(expr)//2),len(expr)):
            if expr[i]=='+':
                m=expr[i-2:i]
                n=expr[i+1:i+3]
        return(f'{a}*{m} + {a}*{n} + {b}*{m} + {b}*{n}')
    if len(expr)==10:

        a=''
# ...
```

### Runtime NameError

- Cluster frequency: `4/637` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `4/637` (`0.6%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `fce3dadb7bc34fe3b7d0569d31786724`, summary `Runtime Error`, score `0`, vector `000`

```python
    #expand_sum_of_products

    # sum = "(a+b) (c+d)"

    # sum = "(x+y) (z+w)"

    # sum = "(1+5) (10+12)"


    #Returns
     #sum_of_products_string
```

### Runtime IndexError from fixed-position string indexing while parsing expression terms

- Cluster frequency: `3/637` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `3/637` (`0.5%`)
- Dominant private-case vectors: `100` x3
- Score distribution (top): `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `f3fb4bd897eb463a8f52962f52088e65`, summary `Runtime Error`, score `33`, vector `100`

```python
    l = []
    for i in range(len(expr)):
        if(expr[i].isalpha()):
            l.append(expr[i])
        '''elif(expr[i].isdigit()):
            if(expr[i+1].isdigit()):
                num = expr[i]+expr[i+1]'''
    return str(l[0])+"*"+str(l[2])+" + "+str(l[0])+"*"+str(l[3])+" + "+str(l[1])+"*"+str(l[2])+" + "+str(l[1])+"*"+str(l[3])
```

### Adds top-level test/print calls after the function definition, causing evaluator output pollution / wrong answer

- Cluster frequency: `2/637` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `2/637` (`0.3%`)
- Dominant private-case vectors: `100` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `c07ffd33255a41df88511673bc1a4be1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    expr = expr.replace(" " , " ")
    if expr.count('(') != 2 or expr.count(')') != 2:
        raise ValueError("Invalid input format")
    first = expr[expr.find('(') + 1 : expr.find(')')]
    second = expr[expr.rfind('(') + 1 : expr.rfind(')')]
    a,b = first.split('+')
    c,d = second.split('+')
    result = f"{a}*{c} + {a}*{d} + {b}*{c} + {b}*{d}"
    return result
```

### Runtime AttributeError

- Cluster frequency: `2/637` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `2/637` (`0.3%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `0adec33d6006463d8e91551a9a3e0738`, summary `Runtime Error`, score `0`, vector `000`

```python
    words=expr.split()
    w=words.split('+')
    result=''
    for word in words:
        for i in range(len(words)):
            result+=w[word]*w[word+1]
    return result
```

### Uses the wrong nested-loop cross product (iterates the same term list twice)

- Cluster frequency: `2/637` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `2/637` (`0.3%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `0c48678766d943c7b034e5744d8576ba`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    expr = expr.replace(" ","")
    if expr.count('(') !=2 or expr.count(')') !=2 :
        print ("error")
    first_group = expr[expr.find('(')+1 : expr.find(')')]
    second_group = expr[expr.rfind('(')+1 : expr.rfind(')')]
    terms1 = first_group.split('+')
    terms2 = second_group.split ('+')
    products = [f"a*b" for a in terms1 for b in terms1]
    return str(' + '.join(products))
```

### Time Limit Exceeded

- Cluster frequency: `1/637` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `1/637` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `43bb1b6e2f4448a29964b3a7a773abca`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
    temp = expr[1:len(expr) - 1]
    i = 0
    while i < len(temp):
        if (temp[i] == ")"):
            first_eq = temp[:i]
            second_eq = temp[i + 2:]
            break
    j = 0
    while j < len(first_eq):
        if (first_eq[j] == "+"):
            var1 = first_eq[:j]
            var2 = first_eq[j + 1:]
            break
    k = 0
    while k < len(second_eq):
        if (second_eq[k] == "+"):
            var3 = second_eq[:k]
            var4 = second_eq[k + 1:]
# ...
```

### Returns the literal expansion for `(a+b)(c+d)` regardless of the input expression

- Cluster frequency: `1/637` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `1/637` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `acd83ce4921b40d7b0d34a4b5038ad28`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if ("(a+b) (c+d)"):
        return "a*c + a*d + b*c + b*d"
    elif ("(x+y) (z+w)"):
        return "x*z + x*w + y*z + y*w"
    elif ("(1+5) (10+12)"):
        return "1*10 + 1*12 + 5*10 + 5*12"
    else:
        return
```

### Tokenizes the expression but then assumes exactly four symbol characters (fails multi-char terms)

- Cluster frequency: `1/637` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/6`: `1/637` (`0.2%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/6`, Student ID `c2ed0e2a45a74c5789dadf1b1119a1d5`, summary `Wrong Answer`, score `33`, vector `100`

```python
    n = expr.split(")(")
    a=''
    for i in n:
        for j in i:
            if j.isalnum():
                a+=j
    return(a[0]+"*"+a[2]+" + "+a[0]+"*"+a[3]+" + "+a[1]+"*"+a[2]+" + "+a[1]+"*"+a[3])
```
