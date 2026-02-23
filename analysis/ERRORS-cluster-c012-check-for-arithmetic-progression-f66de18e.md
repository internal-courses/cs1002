# Error Patterns: Cluster C012 (`Check for Arithmetic Progression`)

## Cluster Summary

- Cluster ID: `C012`
- Cluster title: `Check for Arithmetic Progression`
- Cluster file (this file): `analysis/ERRORS-cluster-c012-check-for-arithmetic-progression-f66de18e.md`
- Variants in cluster: `2`
- Total final submitters across variants: `1365`
- Total non-full final submissions across variants: `507`
- Canonical variant (by submissions): `ns_25t2_py21_2/20`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py21_1/17` | 677 | 264 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/20` (canonical) | 688 | 243 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/20.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/17.json`

## Cluster-Level Outcome Summary

- Final submitters: `1365`
- Full pass: `858`
- Non-full final submissions: `507`
- Parseable non-full (logic/runtime focus): `439`
- Non-parseable non-full: `68`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py21_1/17` | 677 | 413 | 264 | 232 | 32 |
| `ns_25t2_py21_2/20` | 688 | 445 | 243 | 207 | 36 |

## Private Case Structure

- Private case 1: non-AP + constant sequence + positive AP
- Private case 2: descending AP + nonlinear non-APs
- Private case 3: geometric/non-AP + zero-diff AP + mixed non-AP

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py21_1/17` | `ns_25t2_py21_2/20` |
| --- | ---: | ---: | ---: | ---: |
| Returns inside loop before completing full check/computation | 183 | 36.1% | 110 | 73 |
| Runtime IndexError | 98 | 19.3% | 48 | 50 |
| Syntax / non-parseable final submission | 68 | 13.4% | 32 | 36 |
| Incorrect AP logic (broad wrong-answer failure) | 23 | 4.5% | 6 | 17 |
| Partially correct AP check (fails specific edge-case groups) | 21 | 4.1% | 9 | 12 |
| Skeleton placeholder `...` left in function | 15 | 3.0% | 7 | 8 |
| Runtime NameError | 15 | 3.0% | 7 | 8 |
| Always returns `True` (constant output) | 14 | 2.8% | 7 | 7 |
| Uses `abs()` on differences (sign-insensitive AP check) | 13 | 2.6% | 8 | 5 |
| Checks only a few fixed positions, not the whole sequence | 12 | 2.4% | 8 | 4 |
| Runtime TypeError | 8 | 1.6% | 2 | 6 |
| Runtime error (parseable final submission) | 8 | 1.6% | 6 | 2 |
| Always returns `False` (constant output) | 7 | 1.4% | 2 | 5 |
| Other wrong-answer logic pattern (residual) | 7 | 1.4% | 3 | 4 |
| No return / implicit `None` | 5 | 1.0% | 3 | 2 |
| Runtime RecursionError | 3 | 0.6% | 2 | 1 |
| Runtime AttributeError | 2 | 0.4% | 1 | 1 |
| Runtime ValueError | 1 | 0.2% | 0 | 1 |
| Compares only initial/final differences, not all consecutive differences | 1 | 0.2% | 0 | 1 |
| Reconstructs expected sequence with wrong base term/indexing | 1 | 0.2% | 1 | 0 |
| Time Limit Exceeded | 1 | 0.2% | 1 | 0 |
| Prints output but does not return required value | 1 | 0.2% | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `7/507` (`1.4%`)

### Returns inside loop before completing full check/computation

- Cluster frequency: `183/507` (`36.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `110/264` (`41.7%`)
  - `ns_25t2_py21_2/20`: `73/243` (`30.0%`)
- Dominant private-case vectors: `100` x79, `000` x59, `110` x23, `001` x18
- Score distribution (top): `33.0` x98, `0.0` x59, `67.0` x26
- Interpretation: Control-flow bug: the function returns during iteration before processing all required items/conditions.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `d73393757a5b404cbd06feae2f5f9b6e`, summary `Wrong Answer`, score `0`, vector `000`

```python
prev = 0
after = 1
cons = sequence[1] - sequence[0]
n = len(sequence)
while after < n:
        if ((sequence[after]) - (sequence[prev])) == cons:
            return True
            prev += 1
            after += 1
        else:
            return False
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `300b0f417401414590a2ed5c84505b0f`, summary `Wrong Answer`, score `33`, vector `001`

```python
l1=[]
for i in range(0,len(sequence)):
        for j in range(i+1,len(sequence)):
            l1.append(sequence[j]- sequence[i])
for k in range(len(l1)):
        if(l1[k]==l1[k+1]):
            return True
        else:
            return False
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
# ...
```

### Runtime IndexError

- Cluster frequency: `98/507` (`19.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `48/264` (`18.2%`)
  - `ns_25t2_py21_2/20`: `50/243` (`20.6%`)
- Dominant private-case vectors: `110` x70, `100` x12, `000` x12, `001` x4
- Score distribution (top): `67.0` x70, `33.0` x16, `0.0` x12
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `139005fc975e48c9ae8439c4e5528b1a`, summary `Runtime Error`, score `67`, vector `110`

```python
for i in range(len(sequence)):
        if len(sequence)<=5:
            if sequence[i+1]-sequence[i] == sequence[i+2]-sequence[i+1] == sequence[i+3] - sequence[i+2]==sequence[i+4]-sequence[i+3]:
                return True
            else:
                return False
        elif len(sequence) <= 8:
            if sequence[i+1]-sequence[i]==sequence[i+2]-sequence[i+1]==sequence[i+3]-sequence[i+2]==sequence[i+4]-sequence[i+3]==sequence[i+5]-sequence[i+4]==sequence[i+6]-sequence[i+5]==sequence[i+7]-sequence[i+6]:
                return True
            else:
                return False
        elif len(sequence) > 8:
            if sequence[i+1]-sequence[i]==sequence[i+2]-sequence[i+1]==sequence[i+3]-sequence[i+2]==sequence[i+4]-sequence[i+3]==sequence[i+5]-sequence[i+4]==sequence[i+6]-sequence[i+5]==sequence[i+7]-sequence[i+6]==sequence[i+8]-sequence[i+7]==sequence[i+9]-sequence[i+8]==sequence[i+10]-sequence[i+9]==sequence[i+11]-sequence[i+10]:
                return True
            else:
                return False
```
  - Variant `ns_25t2_py21_2/20`, Student ID `fbbd37d093eb4b94b728959d2881a780`, summary `Runtime Error`, score `67`, vector `110`

```python
for i in range(len(sequence)):
        n1=(sequence[i+1]-sequence[i])
        n2=(sequence[i+2]-sequence[i+1])
        n3=(sequence[i+3]-sequence[i+2])
        n4=(sequence[i+4]-sequence[i+3])
        if n1==n2==n3==n4:
            return True
        else:
            return False
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `68/507` (`13.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `32/264` (`12.1%`)
  - `ns_25t2_py21_2/20`: `36/243` (`14.8%`)
- Dominant private-case vectors: `000` x68
- Score distribution (top): `0.0` x68
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `b05545d0b9964d1e850a1695206fbb20`, summary `Runtime Error`, score `0`, vector `000`

```python
diff=sequence[1]- sequence[0]
if sequence[1]- sequence[0]==diff:
    else:
        return False
        if sequence[2]- sequence[1]==diff:
        else:
            return False
            if sequence[3]- sequence[2]==diff:
            else:
                return False
                if sequence[4]- sequence[3]==diff:
                    return True
                else:
                    return False
                    if sequence[5]- sequence[4]==diff:
                        return True
                    else:
                        return False
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `32783e45160a476ab02847d2dbd387e5`, summary `Runtime Error`, score `0`, vector `000`

```python
if len(sequence)<2:
        return True
common_difference =sequence[1]- sequence[0]
for i in range(2,lem(sequence)):
        if sequence[i]-sequence[i-1]!=
common_difference:
        return False
return True
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
    >>> True
# ...
```

### Incorrect AP logic (broad wrong-answer failure)

- Cluster frequency: `23/507` (`4.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `6/264` (`2.3%`)
  - `ns_25t2_py21_2/20`: `17/243` (`7.0%`)
- Dominant private-case vectors: `000` x23
- Score distribution (top): `0.0` x23
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `fe04254019c34dfbad02c01cfc5f1da2`, summary `Wrong Answer`, score `0`, vector `000`

```python
a = len(sequence)
'''c1 = sequence[a:a-1]
    c2 = sequence[a-1:a-2]
    b = (c1 - c2)
    d1 = sequence[a-2:a-3]
    d2 = sequence[a-3:a-4]
    e = d1 - d2'''
if 2&10 in sequence:
        return False
    elif 2 in sequence:
        return True
    elif 1 or 32 in sequence:
        return True
    elif 22 in sequence:
        return False
'''else:
        return False'''
```
  - Variant `ns_25t2_py21_2/20`, Student ID `24fe2547249e44bf91cc4af2c7c2cdba`, summary `Wrong Answer`, score `0`, vector `000`

```python
a = sequence[1] - sequence[0]
c = []
for i in range(len(sequence)):
        if i>0:
            if sequence[i]- sequence[i-1] == a:
                c.append("1")
            else:
                c.append("0")
''' i in range(len(c)):
        if c[i] == "0":
            return False
        return True'''
minu = min(c)
if minu ==0:
        return True
    else:
        return False
'''
# ...
```

### Partially correct AP check (fails specific edge-case groups)

- Cluster frequency: `21/507` (`4.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `9/264` (`3.4%`)
  - `ns_25t2_py21_2/20`: `12/243` (`4.9%`)
- Dominant private-case vectors: `110` x14, `100` x7
- Score distribution (top): `67.0` x14, `33.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `5facc27e0c754129abbac1c610613d9e`, summary `Wrong Answer`, score `67`, vector `110`

```python
bool1=True
if len(sequence)>1:
        sub=sequence[1]-sequence[0]
if len(sequence)==3:
        num1=sequence[0]
        num2=sequence[1]
        num3=sequence[2]
        if (((num2-num1)==(num3-num2)) and ((num2-num1)==sub)):
            bool1=True
        else:
            bool1=False
if len(sequence)>3:
        for i in range(len(sequence)):
            if i == (len(sequence)-3):
                break
            num1=sequence[i]
            num2=sequence[i+1]
            num3=sequence[i+2]
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `e167e906fa4244918efe46144d1237f8`, summary `Wrong Answer`, score `67`, vector `110`

```python
...
n=len(sequence)-3
flag=False
for i in range (0,n):
        if sequence[i+1]- sequence[i]== sequence[i+2]- sequence[i+1]:
            flag=True
        else:
            flag=False
            break
if flag == True:
        return True
    else:
        return False
```

### Skeleton placeholder `...` left in function

- Cluster frequency: `15/507` (`3.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `7/264` (`2.7%`)
  - `ns_25t2_py21_2/20`: `8/243` (`3.3%`)
- Dominant private-case vectors: `000` x14, `110` x1
- Score distribution (top): `0.0` x14, `67.0` x1
- Interpretation: Template placeholder remains; Python treats `...` as valid syntax, often yielding a wrong-answer `None` path instead of syntax failure.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `683a174f345b43dca0e3b6af165a4eff`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `07a5cf895ccf4b1c97306f462f6aa45f`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
```

### Runtime NameError

- Cluster frequency: `15/507` (`3.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `7/264` (`2.7%`)
  - `ns_25t2_py21_2/20`: `8/243` (`3.3%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `7b426e25a8734e40bd73dd7bba0f4e64`, summary `Runtime Error`, score `0`, vector `000`

```python
print("True")
print("True")
is_equal(
    is_arithmetic_progression([10, 9, 6, 4, 2]),
    False
)
is_equal(
    is_arithmetic_progression([10, 8, 7, 4, 2]),
    False
)
is_equal(
    is_arithmetic_progression([10, 9, 6, 4, 2]),
    False
)
is_equal(
    is_arithmetic_progression([10, 8, 7, 4, 2]),
    False
)
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `8bc7d985cd314cee9c8c8d4a2df21a90`, summary `Runtime Error`, score `0`, vector `000`

```python
n=len(s)
if n<=1:
        return True
s.sort()
cd=sequence[1]-sequence[0]
for i in range(2,n):
        if s[i]-s[i-1] != cd:
            return False
for i in range(len(sequence)):
        if (sequence[i+1]-sequence[i]) == (sequence[i+2]-sequence[i+1]):
            return True
        else:
            return False
        '''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

# ...
```

### Always returns `True` (constant output)

- Cluster frequency: `14/507` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `7/264` (`2.7%`)
  - `ns_25t2_py21_2/20`: `7/243` (`2.9%`)
- Dominant private-case vectors: `000` x14
- Score distribution (top): `0.0` x14
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `bed97911eb304dbcaa618a55d613930b`, summary `Wrong Answer`, score `0`, vector `000`

```python
for i in range(4):
        if i+1 - i == i+2 - i+1:
            return True
        else:
            return True
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
    >>> True
    is_arithmetic_progression([9, 6, 3, 0, -3, -6])
    >>> True
    is_arithmetic_progression([1, 3, 5, 6, 11])
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `b2e2c48acdb14de9bced791a07a34694`, summary `Wrong Answer`, score `0`, vector `000`

```python
if len(sequence)>2:
       return True
       diff=sequence[1]-sequence[0]
       for i in range(2,len(sequence)):
           if sequence[i]-sequence[i-1]==diff:
               return True
           else:
               return True
           is_arithmetic_progression([1,3,5,7,9])
```

### Uses `abs()` on differences (sign-insensitive AP check)

- Cluster frequency: `13/507` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `8/264` (`3.0%`)
  - `ns_25t2_py21_2/20`: `5/243` (`2.1%`)
- Dominant private-case vectors: `000` x4, `110` x3, `101` x2, `100` x2
- Score distribution (top): `67.0` x6, `0.0` x4, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `fc0739882afb4c888047076d6f2d6c75`, summary `Wrong Answer`, score `0`, vector `000`

```python
diffValue = abs(sequence[1] - sequence[0])
for i in range(0, len(sequence)-1, 1) :
        #diffValue = abs(sequence[1] - sequence[0])
        #print("constant value:")
        #print(diffValue)

        nomatch = False
        #print(abs(sequence[i+1] - sequence[i]))
        if (abs(sequence[i+1] - sequence[i]) != diffValue) :
            nomatch = False
            #return False

        #if (sequence[i+1] - sequence[i]) != 2 :
         #   return False
if not nomatch :
        return True
    else :
        return nomatch
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `8d2c5337634240e29a28e245332e876c`, summary `Wrong Answer`, score `33`, vector `010`

```python
result= sequence[1]-sequence[0]
result=abs(result)
sum= result*(len(sequence)-1)-(2*len(sequence))
if result==abs(sum):
        return True
    else:
        return False
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
    >>> True
    is_arithmetic_progression([9, 6, 3, 0, -3, -6])
# ...
```

### Checks only a few fixed positions, not the whole sequence

- Cluster frequency: `12/507` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `8/264` (`3.0%`)
  - `ns_25t2_py21_2/20`: `4/243` (`1.6%`)
- Dominant private-case vectors: `110` x8, `100` x2, `101` x1, `001` x1
- Score distribution (top): `67.0` x9, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `7a1863dc1cf64832922d1f0d35fabbbe`, summary `Wrong Answer`, score `67`, vector `110`

```python
if len(sequence)<6:
        a=sequence[0]
        b=sequence[1]
        c=b-a
        d = sequence[2]
        e = sequence[3]
        f = e-d
        if c==f:
            return True
        else:
            return False
    else:
        a=sequence[0]
        b=sequence[1]
        c=b-a
        d=sequence[2]
        e=sequence[3]
        f=e-d
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `66a7b1afdbf345bdbe757e0385665e93`, summary `Wrong Answer`, score `67`, vector `110`

```python
if len(sequence) >= 4 and len(sequence) < 6:
        a = sequence[0]
        b = sequence[1]
        c = sequence[2]
        d = sequence[3]

        diff1 = a - b
        diff2 = c - d

        if diff1 == diff2:
            return True
        else:
            return False
if len(sequence) >= 8:
        a = sequence[0]
        b = sequence[1]
        c = sequence[2]
        d = sequence[3]
# ...
```

### Runtime TypeError

- Cluster frequency: `8/507` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `2/264` (`0.8%`)
  - `ns_25t2_py21_2/20`: `6/243` (`2.5%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `bee6eac0421a43c3bbad0423b13e6898`, summary `Runtime Error`, score `0`, vector `000`

```python
n= len (list)
for i in range (n):
        if list[i+1] - list[i] == list[i+2] - list[i+1]:
            return True
        else:
            return False
```
  - Variant `ns_25t2_py21_2/20`, Student ID `2a311854322e46139a7eb98e7f76620c`, summary `Runtime Error`, score `0`, vector `000`

```python
for i in list:
        i = 0
        is_arithmetic_progression = list[i+1] - list[i]
        i += 1
        difference = sum(is_arithmetic_progression)/ (i-1)
return difference
if difference == is_arithmetic_progression:
        print("True")
    else:
        print("False")
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `8/507` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `6/264` (`2.3%`)
  - `ns_25t2_py21_2/20`: `2/243` (`0.8%`)
- Dominant private-case vectors: `000` x7, `010` x1
- Score distribution (top): `0.0` x7, `33.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `1bd13e9ff636464b9f83a0f69c0f6fa3`, summary `Runtime Error`, score `33`, vector `010`

```python
count = 0
diff = 0
for i in sequence:
        count += 1
for j in range (count-1):
        diff_per_iter = sequence[j+1] - sequence[j]
        if diff == 0:
            diff = diff_per_iter
        else:
            if diff_per_iter == diff:
                is_arithmetic_progression = True
            else:
                is_arithmetic_progression = False
                break
return is_arithmetic_progression
```
  - Variant `ns_25t2_py21_2/20`, Student ID `4513408ff00d473ebafdbad27b173ddd`, summary `Runtime Error`, score `0`, vector `000`

```python
n=len(sequence)
d=sequence[1]-sequence[0]
while i<n-1:
        if s[i+1]-s[i]==d:
            continue
            i+=1
        else:
            return False
        return True
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
# ...
```

### Always returns `False` (constant output)

- Cluster frequency: `7/507` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `2/264` (`0.8%`)
  - `ns_25t2_py21_2/20`: `5/243` (`2.1%`)
- Dominant private-case vectors: `000` x4, `100` x2, `001` x1
- Score distribution (top): `0.0` x4, `33.0` x3
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `574006c958544a7095715299824dab97`, summary `Wrong Answer`, score `0`, vector `000`

```python
...
a=sequence[0]-sequence[1]
for i in range(len(sequence)):
        if i==len(sequence) and sequence[i]==sequence[i+1]+a:
            return(True)

        else:
            return(False)
```
  - Variant `ns_25t2_py21_2/20`, Student ID `5ae92d5eb96a4382be5e0a9242bb9276`, summary `Wrong Answer`, score `33`, vector `001`

```python
x = sequence[1] - sequence[0]
for i in range(len(sequence)):
        while i in range(len(sequence)):
            if sequence[i] - sequence[(i+1)] == x:
                return(True)
            else:
                return(False)
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `7/507` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `3/264` (`1.1%`)
  - `ns_25t2_py21_2/20`: `4/243` (`1.6%`)
- Dominant private-case vectors: `001` x5, `010` x1, `011` x1
- Score distribution (top): `33.0` x6, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `a169860299dd4cbd8cd4fbc7499e2baa`, summary `Wrong Answer`, score `33`, vector `001`

```python
n=len(sequence)
l=[]
for i in range(1,n):
        a=sequence[i]
        b=i-1
        q=sequence[b]
        l.append(q)
s=set(l)
if len(s)==1:
        return True
    else:
        return False
'''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `7e003dc9ec2149a68e438dca79b94c07`, summary `Wrong Answer`, score `33`, vector `001`

```python
first=sequence[0]
f1=0
s1=0
check=0
second=sequence[1]
difference=second-first
i=0
while (i<len(sequence)):
        f1=sequence[i]
        if((i+1)<len(sequence)):
            s1=sequence[i+1]
        else:
            break
        diff1=s1-f1
        i=i+1
if(check==(difference*(len(sequence)-1))):
        return True
    else:
# ...
```

### No return / implicit `None`

- Cluster frequency: `5/507` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `3/264` (`1.1%`)
  - `ns_25t2_py21_2/20`: `2/243` (`0.8%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `ebdadf37c91b450f8d49ed7b58b854a3`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_arithmetic_progression(sequence: list) -> bool:
    '''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
    >>> True
    is_arithmetic_progression([9, 6, 3, 0, -3, -6])
    >>> True
    is_arithmetic_progression([1, 3, 5, 6, 11])
    >>> False
    is_arithmetic_progression([0, 0, 0, 0, 0])
    >>> True
    is_arithmetic_progression([1, 2, 4, 8, 16])
# ...
```
  - Variant `ns_25t2_py21_2/20`, Student ID `510df751d0b34826849149c5caac5316`, summary `Wrong Answer`, score `0`, vector `000`

```python
def is_arithmetic_progression(sequence: list) -> bool:
    '''
    Given a sequence of numbers, determine if it is an arithmetic progression.

    An arithmetic progression is a sequence where the difference between consecutive terms is constant.

    Examples:
    is_arithmetic_progression([1, 3, 5, 7, 9])
    >>> True
    is_arithmetic_progression([2, 4, 6, 8, 10])
    >>> True
    is_arithmetic_progression([9, 6, 3, 0, -3, -6])
    >>> True
    is_arithmetic_progression([1, 3, 5, 6, 11])
    >>> False
    is_arithmetic_progression([0, 0, 0, 0, 0])
    >>> True
    is_arithmetic_progression([1, 2, 4, 8, 16])
# ...
```

### Runtime RecursionError

- Cluster frequency: `3/507` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `2/264` (`0.8%`)
  - `ns_25t2_py21_2/20`: `1/243` (`0.4%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `abd9675ec2e1419291b48fc1c1bd0b2a`, summary `Runtime Error`, score `0`, vector `000`

```python
is_equal(
    is_arithmetic_progression([2,4,6,8,10]),
    True
    )
is_equal(
        is_arithmetic_progression([-1,1,3,5,7]),
        True
        )
```
  - Variant `ns_25t2_py21_2/20`, Student ID `36f278254d9f42a5bfa8e20d0ab640e1`, summary `Runtime Error`, score `0`, vector `000`

```python
if is_arithmetic_progression([8,12,16,20,24,28,32,36]):
        print(True)
    elif is_arithmetic_progression([10, 9, 6, 4, 2]):
        print(False)
    elif is_arithmetic_progression([10, 8, 7, 4, 2,]):
        print(False)
    elif is_arithmetic_progression([-1, 1, 3, 5, 7]):
        print(True)
    elif is_arithmetic_progression([2, 4, 6, 8, 10]):
        print(True)
    elif is_arithmetic_progression([8,12,16,20,22,24,26,28]):
        print(False)
```

### Runtime AttributeError

- Cluster frequency: `2/507` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `1/264` (`0.4%`)
  - `ns_25t2_py21_2/20`: `1/243` (`0.4%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `1af8b8766aa7419eb29e044f215eceff`, summary `Runtime Error`, score `0`, vector `000`

```python
sequence = [1,3,5,7,9]
diff_1 = sequence.idx(1) - sequence.idx(0)
diff_2 = sequence.idx(2) - sequence.idx(1)
diff_3 = sequence.idx(3) - sequence.idx(2)
diff_4 = sequence.idx(4) - sequence.idx(3)
is_arithmetic_progression = (diff_1==diff_2==diff_3==diff_4)
return is_arithmetic_progression
```
  - Variant `ns_25t2_py21_2/20`, Student ID `5b124aa8e1074ca1af120f98e94636e3`, summary `Runtime Error`, score `0`, vector `000`

```python
for i in str(len(sequence)):
        i += i
if sequence.arithmetic:
        return true
    else:
        return False
```

### Runtime ValueError

- Cluster frequency: `1/507` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `0/264` (`0.0%`)
  - `ns_25t2_py21_2/20`: `1/243` (`0.4%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/20`, Student ID `96743b60b9ab45259fd283585746a3b5`, summary `Runtime Error`, score `33`, vector `010`

```python
a1=sequence[0]
a2=sequence[1]
d=a2-a1
length=len(sequence)
L1=[]
for i in range(a1,(a1+(length-1)*d)+d,d):
        L1.append(i)
for i in range(length):
        if L1[i]==sequence[i]:
            continue
        else :
            return False
            break
return True
```

### Compares only initial/final differences, not all consecutive differences

- Cluster frequency: `1/507` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `0/264` (`0.0%`)
  - `ns_25t2_py21_2/20`: `1/243` (`0.4%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/20`, Student ID `ef0942d05fe9437c9b8ff4b886241d95`, summary `Wrong Answer`, score `33`, vector `100`

```python
x = 0
y = 0
for j in range(len(sequence[1:])):
        m = sequence[j]
for i in range(len(sequence)):
        y = sequence[i]-m
if ((sequence[0]-sequence[1])==(sequence[1]-sequence[2])):
        return True
    else:
        return False
```

### Reconstructs expected sequence with wrong base term/indexing

- Cluster frequency: `1/507` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `1/264` (`0.4%`)
  - `ns_25t2_py21_2/20`: `0/243` (`0.0%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `435ae931a3ad45cd9abc141f1d3f4883`, summary `Wrong Answer`, score `33`, vector `001`

```python
com_diff = sequence[1] - sequence[0]
l = []
for i, x in enumerate(sequence):
        l.append((i+1) * com_diff)
if sequence == l:
        return True
    elif sequence != l:
        return False
```

### Time Limit Exceeded

- Cluster frequency: `1/507` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `1/264` (`0.4%`)
  - `ns_25t2_py21_2/20`: `0/243` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `787fdade9e7e4a809ce311b0e2363415`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
i = 0
length = len(sequence)
diff1 = sequence [1] - sequence [0]
while i < length:
        if (sequence [i+1] - sequence[i]) == diff1:
            diff2 = sequence[i+1] - sequence[i]
i = i+1
if diff2 == diff1:
        return True
    else:
        return False
```

### Prints output but does not return required value

- Cluster frequency: `1/507` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/17`: `1/264` (`0.4%`)
  - `ns_25t2_py21_2/20`: `0/243` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: In function-type questions, printing is not enough; tests compare the returned value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/17`, Student ID `f8c14b164b324e31b64642cfa166e6df`, summary `Wrong Answer`, score `0`, vector `000`

```python
if(is_arithmetic_progression == ([2, 4 ,6 ,8 ,10])):
        print("True")
if(is_arithmetic_progression == ([-1, 1, 3, 5, 7])):
        print("True")
if(is_arithmetic_progression == ([10, 9, 6, 4, 2])):
        print("False")
if(is_arithmetic_progression == ([10, 8, 7, 4, 2])):
        print("False")
if(is_arithmetic_progression == ([8, 12, 16, 20, 24, 28, 32, 36])):
        print("True")
if(is_arithmetic_progression == ([8, 12, 16, 20, 24, 28, 32, 36])):
        print("True")
if(is_arithmetic_progression == ([8, 12, 16, 20, 22, 24, 26, 28])):
        print("False")
```
