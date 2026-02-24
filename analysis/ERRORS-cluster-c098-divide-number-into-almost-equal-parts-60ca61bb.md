# Error Patterns: Cluster C098 (`Divide Number Into Almost Equal Parts`)

## Cluster Summary

- Cluster ID: `C098`
- Cluster title: `Divide Number Into Almost Equal Parts`
- Cluster file (this file): `analysis/ERRORS-cluster-c098-divide-number-into-almost-equal-parts-60ca61bb.md`
- Variants in cluster: `1`
- Total final submitters across variants: `525`
- Total non-full final submissions across variants: `368`
- Canonical variant (by submissions): `ns_25t2_py13_1/7`

Cluster membership (zero-submitter variants omitted):

| Variant                        | final_submitters | non_full | Relationship                 |
| ------------------------------ | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_1/7` (canonical) |              525 |      368 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/7.json`

## Cluster-Level Outcome Summary

- Final submitters: `525`
- Full pass: `157`
- Non-full final submissions: `368`
- Parseable non-full (logic/runtime focus): `302`
- Non-parseable non-full: `66`

Variant-level comparison:

| Variant            | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------ | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_1/7` |              525 |       157 |      368 |                302 |                     66 |

## Private Case Structure

- Private case 1: baseline/easy cases incl exact division and simple remainder distribution
- Private case 2: larger non-divisible cases (must distribute `+1` across the earliest parts)
- Private case 3: additional exact + non-exact cases to verify length, sum, and larger-first ordering

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                               | Cluster count | % of cluster non-full | `ns_25t2_py13_1/7` |
| ----------------------------------------------------------------------------------------------------- | ------------: | --------------------: | -----------------: |
| Hard-codes public sample outputs or `(n, k)` cases instead of computing a general partition           |           106 |                 28.8% |                106 |
| Incorrect partition construction (wrong length/sum/order or non-general logic)                        |            77 |                 20.9% |                 77 |
| Syntax / non-parseable final submission                                                               |            66 |                 17.9% |                 66 |
| No return / implicit `None`                                                                           |            42 |                 11.4% |                 42 |
| Runtime TypeError                                                                                     |            14 |                  3.8% |                 14 |
| Runtime NameError from undefined counters/helpers while constructing the partition list               |            10 |                  2.7% |                 10 |
| Runtime IndexError                                                                                    |             7 |                  1.9% |                  7 |
| Runtime error (parseable final submission)                                                            |             7 |                  1.9% |                  7 |
| Sorts/reorders the result after construction, which breaks the required stable larger-first ordering  |             6 |                  1.6% |                  6 |
| Passes simpler/equal-split cases but distributes the remainder incorrectly on non-divisible inputs    |             6 |                  1.6% |                  6 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests)               |             5 |                  1.4% |                  5 |
| Time Limit Exceeded                                                                                   |             4 |                  1.1% |                  4 |
| Runtime ValueError                                                                                    |             4 |                  1.1% |                  4 |
| Runtime AttributeError                                                                                |             4 |                  1.1% |                  4 |
| Computes quotient/remainder but sorts the result, breaking the required larger-first order            |             3 |                  0.8% |                  3 |
| Mixes numeric and list accumulators while building the output parts (list/int type error)             |             2 |                  0.5% |                  2 |
| Handles only exact-division cases (`n % k == 0`) and omits the non-divisible remainder case           |             2 |                  0.5% |                  2 |
| Uses `k`-specific branches / length-specific outputs instead of a general quotient-remainder solution |             1 |                  0.3% |                  1 |
| Assumes a fixed 3-element output list (e.g., `[0,0,0]`) instead of length `k`                         |             1 |                  0.3% |                  1 |
| Runtime RecursionError                                                                                |             1 |                  0.3% |                  1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/368` (`0.0%`)

### Hard-codes public sample outputs or `(n, k)` cases instead of computing a general partition

- Cluster frequency: `106/368` (`28.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `106/368` (`28.8%`)
- Dominant private-case vectors: `000` x56, `100` x50
- Score distribution (top): `0.0` x56, `33.0` x50
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `068a9cfeff804057a789cf340725189b`, summary `Wrong Answer`, score `0`, vector `000`

```python
    '''
    Help on class list in module builtins:\n
\n
class list(object)\n
 |  list() -> new empty list\n
 |  list(iterable) -> new list initialized from iterable's items\n
 |  \n
 |  Methods defined here:\n
 |  \n
 |  __add__(self, value, /)\n
 |      Return self+value.\n
 |  \n
 |  __contains__(self, key, /)\n
 |      Return key in self.\n
 |  \n
 |  __delitem__(self, key, /)\n
 |      Delete self[key].\n
 |  \n
# ...
```

### Incorrect partition construction (wrong length/sum/order or non-general logic)

- Cluster frequency: `77/368` (`20.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `77/368` (`20.9%`)
- Dominant private-case vectors: `000` x77
- Score distribution (top): `0.0` x77
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `80a338ddd27b418f8c71bba5b90a7182`, summary `Wrong Answer`, score `0`, vector `000`

```python
    g=n//k
    return[4,3,3]
    '''
    Given two integers n and k, return a list of size k
    such that the values are almost equal and their sum is n.
    Larger numbers should appear earlier in the list.

    Examples:
    >>> divide_into_almost_equal_parts(5, 3)
    [2, 2, 1]
    >>> divide_into_almost_equal_parts(16, 3)
    [6, 5, 5]
    >>> divide_into_almost_equal_parts(12, 4)
    [3, 3, 3, 3]
    >>> divide_into_almost_equal_parts(10, 3)
    [4, 3, 3]

    Args:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `66/368` (`17.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `66/368` (`17.9%`)
- Dominant private-case vectors: `000` x66
- Score distribution (top): `0.0` x66
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `a718ee744e1049649315ced45408a906`, summary `Runtime Error`, score `0`, vector `000`

```python
def divide_into_almost_equal_parts(n: int, k: int) -> list:
    '''
    Given two integers n and k, return a list of size k
    such that the values are almost equal and their sum is n.
    Larger numbers should appear earlier in the list.

    Examples:
    >>> divide_into_almost_equal_parts(5, 3)
    [2, 2, 1]
    >>> divide_into_almost_equal_parts(16, 3)
    [6, 5, 5]
    >>> divide_into_almost_equal_parts(12, 4)
    [3, 3, 3, 3]
    >>> divide_into_almost_equal_parts(10, 3)
    [4, 3, 3]

    Args:
        n (int): Total number to be divided
# ...
```

### No return / implicit `None`

- Cluster frequency: `42/368` (`11.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `42/368` (`11.4%`)
- Dominant private-case vectors: `000` x42
- Score distribution (top): `0.0` x42
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `94bb2e5ac1dd4423bb0788eb73c5fd2a`, summary `Wrong Answer`, score `0`, vector `000`

```python
def divide_into_almost_equal_parts(n: int, k: int) -> list:
    '''
    Given two integers n and k, return a list of size k
    such that the values are almost equal and their sum is n.
    Larger numbers should appear earlier in the list.

    Examples:
    >>> divide_into_almost_equal_parts(5, 3)
    [2, 2, 1]
    >>> divide_into_almost_equal_parts(16, 3)
    [6, 5, 5]
    >>> divide_into_almost_equal_parts(12, 4)
    [3, 3, 3, 3]
    >>> divide_into_almost_equal_parts(10, 3)
    [4, 3, 3]

    Args:
        n (int): Total number to be divided
# ...
```

### Runtime TypeError

- Cluster frequency: `14/368` (`3.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `14/368` (`3.8%`)
- Dominant private-case vectors: `000` x14
- Score distribution (top): `0.0` x14
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `ff23805daf6344998ef8bc2238138833`, summary `Runtime Error`, score `0`, vector `000`

```python
...
avg = (k) // n
rem = (k) % n
result = []
start = 0
for i in range(n):
    end = start + avg + (1 if i < rem else 0)
    result.append(list[start:end])
    start = end
return result
```

### Runtime NameError from undefined counters/helpers while constructing the partition list

- Cluster frequency: `10/368` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `10/368` (`2.7%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `3b26534dff4843bd817619c7df7a5951`, summary `Runtime Error`, score `0`, vector `000`

```python
sum1 = 0
while sum1 != n:
    i = 0
    while i < k:
        temp = random(int)
        sum += temp
        l.insert(0, temp)
        i += 1
if sum1 == n:
    list.sort(key=None, reverse=True)
    return list
```

### Runtime IndexError

- Cluster frequency: `7/368` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `7/368` (`1.9%`)
- Dominant private-case vectors: `000` x6, `100` x1
- Score distribution (top): `0.0` x6, `33.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `fa7fb11db3234e0ebc924b9eb7e8636e`, summary `Runtime Error`, score `33`, vector `100`

```python
l = []
for i in range(k):
    if n % k == 1:
        l.append(int(n / k))
    elif n % k == 0:
        l.append(int(n / k))
    elif n % k == 2:
        l.append(int(n / k))
length = len(l)
for j in range(k):
    if sum(l) != n:
        l[(length - 1)] += 1
    length = length - 1
l.sort()
l.reverse()
return l
```

### Runtime error (parseable final submission)

- Cluster frequency: `7/368` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `7/368` (`1.9%`)
- Dominant private-case vectors: `000` x6, `100` x1
- Score distribution (top): `0.0` x6, `33.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `1b78ba5a5c6c41ee9bc5f26aa52b6bf4`, summary `Runtime Error`, score `0`, vector `000`

```python
...
lst = []
mst = []
sum = 0
for i in range(k):
    noof += 1
    i += 1
    for j in range(noof):
        if m < n:
            sum += m
            mst.append(sum)
            if sum == n:
                lst.append(mst)
return lst
```

### Sorts/reorders the result after construction, which breaks the required stable larger-first ordering

- Cluster frequency: `6/368` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `6/368` (`1.6%`)
- Dominant private-case vectors: `100` x5, `000` x1
- Score distribution (top): `33.0` x5, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `80639f4eaa364e7fa816d5672ebf5892`, summary `Wrong Answer`, score `33`, vector `100`

```python
p = n / k
o = p - (n // k)
if o >= 0.5:
    t = math.ceil(p)
else:
    t = math.floor(p)
lis = []
suma = 0
for i in range(k - 1):
    lis.append(t)
    suma += t
x = n - suma
lis.append(x)
lis.sort()
sol = []
for j in range(len(lis) - 1, -1, -1):
    sol.append(lis[j])
return sol
```

### Passes simpler/equal-split cases but distributes the remainder incorrectly on non-divisible inputs

- Cluster frequency: `6/368` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `6/368` (`1.6%`)
- Dominant private-case vectors: `100` x6
- Score distribution (top): `33.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `5eeb3c8a85a54c0eba20741e2fb1d6e9`, summary `Wrong Answer`, score `33`, vector `100`

```python
    l=[]
    if n%k==0:
        for i in range(1,k+1):
            l.append(n//k)
        return l
    elif n>2*k:
        remainder=n%k
        for i in range(1,k+1):
            l.append(n//k)
        l[0]+=remainder
        return l
        '''
    else:
        remainder=n%k
        for i in range(1,k+1):
            l.append(n//k)
        l[-1]+=remainder
        return l
# ...
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `5/368` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `5/368` (`1.4%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `0b4cc28f35474b64adb6fa769c896595`, summary `Runtime Error`, score `0`, vector `000`

```python
list = []
a = int(input("enter order1"))
b = int(input("enter order2"))
c = int(input("enter order3"))
n = int(input("enter the number"))
k = int(input("enter the number1"))
k = len(list)
n = a + b + c
list = list.append(a)
list = list.append(b)
list = list.append(c)
print(list)
print(list)
```

### Time Limit Exceeded

- Cluster frequency: `4/368` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `4/368` (`1.1%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `0824f51aa9364f11b942c5beef49ea10`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
l1 = []
if n % k == 0:
    for i in range(k):
        l1.append(n // k)
else:
    if (k * 2 > n) and (n != 0):
        l1.append(k - 1)
        k = k - 1
        n = n - (k - 1)
    else:
        while n != 0:
            l1.append(k * 2)
return l1
```

### Runtime ValueError

- Cluster frequency: `4/368` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `4/368` (`1.1%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `def7eb8218924db6b8e4b14740110883`, summary `Runtime Error`, score `0`, vector `000`

```python
def divide_into_almost_equal_parts(n: int, k: int) -> list:
    '''
    Given two integers n and k, return a list of size k
    such that the values are almost equal and their sum is n.
    Larger numbers should appear earlier in the list.

    Examples:
    >>> divide_into_almost_equal_parts(5, 3)
    [2, 2, 1]
    >>> divide_into_almost_equal_parts(16, 3)
    [6, 5, 5]
    >>> divide_into_almost_equal_parts(12, 4)
    [3, 3, 3, 3]
    >>> divide_into_almost_equal_parts(10, 3)
    [4, 3, 3]

    Args:
        n (int): Total number to be divided
# ...
```

### Runtime AttributeError

- Cluster frequency: `4/368` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `4/368` (`1.1%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `b40432590f9a4aac83d1706195930428`, summary `Runtime Error`, score `0`, vector `000`

```python
l = []
summation = n
total = 0
for i in range(k - 1):
    a = n // k
    l.append(a)
    total += a
b = summation - total
l.append(b)
x = l.reverse().sort()
return l
```

### Computes quotient/remainder but sorts the result, breaking the required larger-first order

- Cluster frequency: `3/368` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `3/368` (`0.8%`)
- Dominant private-case vectors: `100` x2, `000` x1
- Score distribution (top): `33.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `453d4d987e7d402db64a97d214925398`, summary `Wrong Answer`, score `33`, vector `100`

```python
    equalparts=[]
    if n>k and n>0 and k>0:
        for i in range(k):
            if (n%k<2):
                if i==(k-1):
                    equalparts.append(n%k+n//k)
                else:
                    #print(i)
                    equalparts.append(round(n/k))
            elif (n%k==2):
                if i==(k-1):
                    equalparts.append(n//k)
                else:
                    equalparts.append(round(n/k))
    sum=0
    for i in range(len(equalparts)):
        sum+=equalparts[i]
    if sum==n:
# ...
```

### Mixes numeric and list accumulators while building the output parts (list/int type error)

- Cluster frequency: `2/368` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `2/368` (`0.5%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `0def2b2e03ab47f3a3edda09ea264d7e`, summary `Runtime Error`, score `0`, vector `000`

```python
    sum=0
    if n%k==0:
        while k>=0:
            sum=[n//3]+sum
    return sum
    '''
    Given two integers n and k, return a list of size k
    such that the values are almost equal and their sum is n.
    Larger numbers should appear earlier in the list.

    Examples:
    >>> divide_into_almost_equal_parts(5, 3)
    [2, 2, 1]
    >>> divide_into_almost_equal_parts(16, 3)
    [6, 5, 5]
    >>> divide_into_almost_equal_parts(12, 4)
    [3, 3, 3, 3]
    >>> divide_into_almost_equal_parts(10, 3)
# ...
```

### Handles only exact-division cases (`n % k == 0`) and omits the non-divisible remainder case

- Cluster frequency: `2/368` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `2/368` (`0.5%`)
- Dominant private-case vectors: `000` x1, `100` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `cee10ddf88e940e485cd4b1da6f14c77`, summary `Wrong Answer`, score `33`, vector `100`

```python
if n % k == 0:
    x = []
    for i in range(k):
        x.append(n // k)
    return x
if n % k == 1:
    y = []
    for i in range(k):
        y.append(n // k + (n % k))
        n = n - (n % k)
    return y
if n % k == 2:
    z = []
    for i in range(k - 1):
        z.append(n % k)
    z.append(1)
    return z
```

### Uses `k`-specific branches / length-specific outputs instead of a general quotient-remainder solution

- Cluster frequency: `1/368` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `1/368` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `5570b72887ef4e2e9ae30b0c4e3eda67`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if k==3:
        for i in range(0,n):
            for j in range(0,n):
                for l in range(0,n):
                    if (i>=j and j>=l) or (i==j==l):
                        if i+j+l==n:
                            return [i,j,l]

    else:
        return [3,3,3,3]
```

### Assumes a fixed 3-element output list (e.g., `[0,0,0]`) instead of length `k`

- Cluster frequency: `1/368` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `1/368` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `6bad5c9cb51b41e59f96f24491402fff`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    x=n//k
    list=[0,0,0]
    if((k%2==0) and (n%2==0)):
        for i in range(k):
            list[i]=x
    elif((k%2==1) and (n%2==0)):
        for i in range(k):
            list[i]=x
        list[0]=x+1
    elif((k%2==0) and (n%2==1)):
        for i in range(k):
            list[i]=x
        list[0]=x+1
    else:
        for i in range(k):
            list[i]=x
        list[0]=x+1
# ...
```

### Runtime RecursionError

- Cluster frequency: `1/368` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/7`: `1/368` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/7`, Student ID `e0e08ab2fd9b4654b2ec7d7dcddc0aea`, summary `Runtime Error`, score `0`, vector `000`

```python
if n > 0 and k > 0:
    is_equal(divide_into_almost_equal_parts(5, 3), [2, 2, 1])
    return [2, 2, 1]
if n > 0 and k > 0:
    is_equal(divide_into_almost_equal_parts(16, 3), [6, 5, 5])
    return [6, 5, 5]
if n > 0 and k > 0:
    is_equal(divide_into_almost_equal_parts(12, 4), [3, 3, 3, 3])
    return [3, 3, 3, 3]
```
