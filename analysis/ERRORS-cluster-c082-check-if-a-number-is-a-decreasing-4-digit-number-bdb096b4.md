# Error Patterns: Cluster C082 (`Check If a Number is a Decreasing 4-Digit Number`)

## Cluster Summary

- Cluster ID: `C082`
- Cluster title: `Check If a Number is a Decreasing 4-Digit Number`
- Cluster file (this file): `analysis/ERRORS-cluster-c082-check-if-a-number-is-a-decreasing-4-digit-number-bdb096b4.md`
- Variants in cluster: `1`
- Total final submitters across variants: `851`
- Total non-full final submissions across variants: `420`
- Canonical variant (by submissions): `ns_25t2_py13_1/5`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_1/5` (canonical) | 851 | 420 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/5.json`

## Cluster-Level Outcome Summary

- Final submitters: `851`
- Full pass: `431`
- Non-full final submissions: `420`
- Parseable non-full (logic/runtime focus): `345`
- Non-parseable non-full: `75`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_1/5` | 851 | 431 | 420 | 345 | 75 |

## Private Case Structure

- Private case 1: clear decreasing 4-digit positives (`9876`, `8765`)
- Private case 2: positive and duplicate-digit negative (`5432` vs `5433`) to test strictness
- Private case 3: non-consecutive but strictly decreasing positive (`5431`) plus non-decreasing negative (`2001`)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_1/5` |
| --- | ---: | ---: | ---: |
| Returns after checking only the first digit comparison (loop exits before all 4 digits are checked) | 82 | 19.5% | 82 |
| Syntax / non-parseable final submission | 75 | 17.9% | 75 |
| Partially correct decreasing-digit logic (fails one private test group due loop/index/strictness bug) | 56 | 13.3% | 56 |
| Always returns `True` (constant output) | 25 | 6.0% | 25 |
| Incorrect decreasing-number logic (broad wrong-answer failure) | 17 | 4.0% | 17 |
| No return / implicit `None` | 15 | 3.6% | 15 |
| Uses sorting-based digit check instead of pairwise strict comparison | 15 | 3.6% | 15 |
| Runtime TypeError | 15 | 3.6% | 15 |
| Hard-codes sample numbers/examples instead of checking digit order generically | 14 | 3.3% | 14 |
| Extracts digits using `/` (float division) instead of integer division `//` | 14 | 3.3% | 14 |
| Runtime TypeError from mixed string/int digit operations or invalid sorted/index logic | 13 | 3.1% | 13 |
| Uses sorted-descending digit check (accepts duplicates; not strict decreasing) | 11 | 2.6% | 11 |
| Sorted/non-strict decreasing check bug (duplicates like `5433` slip through) | 10 | 2.4% | 10 |
| Uses non-strict comparisons (`>=`/`<=`), so equal adjacent digits can be accepted | 10 | 2.4% | 10 |
| Runtime NameError | 8 | 1.9% | 8 |
| Reads `input()` inside function (EOF under evaluator function-call tests) | 6 | 1.4% | 6 |
| Requires consecutive step of exactly 1 between digits (rejects valid decreasing numbers like `5431`) | 5 | 1.2% | 5 |
| Always returns `False` (constant output) | 5 | 1.2% | 5 |
| Runtime AttributeError | 4 | 1.0% | 4 |
| Runtime error (parseable final submission) | 4 | 1.0% | 4 |
| Runtime NameError from lowercase `true`/`false` or typoed identifier | 3 | 0.7% | 3 |
| Consecutive-step (`-1`) check bug (requires 1-step decreases, rejects valid cases like `5431`) | 3 | 0.7% | 3 |
| Runtime IndexError from out-of-range digit indexing in comparison loop | 2 | 0.5% | 2 |
| Runtime ValueError | 2 | 0.5% | 2 |
| Runtime RecursionError | 1 | 0.2% | 1 |
| Returns a string/non-boolean representation instead of a boolean result | 1 | 0.2% | 1 |
| Time Limit Exceeded | 1 | 0.2% | 1 |
| Uses an incorrect 4-digit range check (`1000 <= n >= 9999` / wrong bounds) | 1 | 0.2% | 1 |
| Runtime IndexError | 1 | 0.2% | 1 |
| Always returns `True` due always-truthy condition / misplaced logic | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/420` (`0.0%`)

### Returns after checking only the first digit comparison (loop exits before all 4 digits are checked)

- Cluster frequency: `82/420` (`19.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `82/420` (`19.5%`)
- Dominant private-case vectors: `100` x67, `101` x10, `110` x3, `011` x1
- Score distribution (top): `33.0` x67, `67.0` x14, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `1d9bb3c6b861457483696cf2357bf930`, summary `Wrong Answer`, score `67`, vector `011`

```python
    '''
    d = []
    a = n
    while a>0:
        d.append(a%10)
        a = n//10
    max = 9
    flag = True
    for i in d:
        if i<=max:
            max = i
        else:
            flag = False
    if flag:
        return True
    else:
        return False

# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `75/420` (`17.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `75/420` (`17.9%`)
- Dominant private-case vectors: `000` x75
- Score distribution (top): `0.0` x75
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `b139c4e883774e60a46980b150709089`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_decreasing_number(n: int) -> bool:
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
    >>> is_decreasing_number(4321)
    True
    >>> is_decreasing_number(4312)
    False
    >>> is_decreasing_number(9876)
    True
    >>> is_decreasing_number(1111)
    False
    >>> is_decreasing_number(3210)
    True

    Args:
# ...
```

### Partially correct decreasing-digit logic (fails one private test group due loop/index/strictness bug)

- Cluster frequency: `56/420` (`13.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `56/420` (`13.3%`)
- Dominant private-case vectors: `100` x55, `010` x1
- Score distribution (top): `33.0` x56
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `0def2b2e03ab47f3a3edda09ea264d7e`, summary `Wrong Answer`, score `33`, vector `100`

```python
    a=str(n)
    if a[0]>a[1]:
        if a[1]>a[2]:
            if a[2]>a[3]:
                return True
    else:
        return False
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
    >>> is_decreasing_number(4321)
    True
    >>> is_decreasing_number(4312)
    False
    >>> is_decreasing_number(9876)
    True
# ...
```

### Always returns `True` (constant output)

- Cluster frequency: `25/420` (`6.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `25/420` (`6.0%`)
- Dominant private-case vectors: `100` x23, `000` x2
- Score distribution (top): `33.0` x23, `0.0` x2
- Interpretation: Constant-output bug or always-truthy condition causes the function to ignore the actual input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `0cac401c3afd4f599534362b0d8e1bf5`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    for i in range(10, 0, -1):
        for j in range(9, 0, -1):
            if j > i & j != i:
                return True
    n = int(input("Enter a four digit number:"))
    print("It is a decreasing number", is_decreasing_number)
```

### Incorrect decreasing-number logic (broad wrong-answer failure)

- Cluster frequency: `17/420` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `17/420` (`4.0%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `d282de2807ad4c8380e0a570512bb723`, summary `Wrong Answer`, score `0`, vector `000`

```python
    n = str(n)
    if n[0] > n[1]:
        s = True
    else:
        s = False
    if n[1] > n[2]:
        t = True
    else:
        t  = False
    if n[2] > n [3]:
        u = True
    else:
        u = False
    if s==t and u==t:
        is_decreasing_number =True
    else:
        is_decreasing_number =False
    return(is_decreasing_number)
```

### No return / implicit `None`

- Cluster frequency: `15/420` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `15/420` (`3.6%`)
- Dominant private-case vectors: `000` x14, `100` x1
- Score distribution (top): `0.0` x14, `33.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `fd642f4f9f9e4f38a86912f5a97a0b99`, summary `Wrong Answer`, score `0`, vector `000`

```python
    for i in range(1,5):
        x=n%10
        y=n%100
        if y>x:
            print("True")
        else:
            print("False")
            continue
        n=n/10
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
    >>> is_decreasing_number(4321)
    True
    >>> is_decreasing_number(4312)
    False
# ...
```

### Uses sorting-based digit check instead of pairwise strict comparison

- Cluster frequency: `15/420` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `15/420` (`3.6%`)
- Dominant private-case vectors: `100` x10, `101` x4, `000` x1
- Score distribution (top): `33.0` x10, `67.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `0ad1c427973645aba18902d9ebab84a5`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    l = []
    l1 = []
    n1 = n
    ''' while(n1!=0):
        rem1 = n1 % 10
        n1 = n1//10
        rem2 = n1 % 10
        if(rem1 >= rem2):
            return True
        else :
            continue
    return False'''
    n1 = n
    for i in range(4):
        rem = n%10
        l.append(rem)
    l1 = l
# ...
```

### Runtime TypeError

- Cluster frequency: `15/420` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `15/420` (`3.6%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `def7eb8218924db6b8e4b14740110883`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_decreasing_number(n: int) -> bool:
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
    >>> is_decreasing_number(4321)
    True
    >>> is_decreasing_number(4312)
    False
    >>> is_decreasing_number(9876)
    True
    >>> is_decreasing_number(1111)
    False
    >>> is_decreasing_number(3210)
    True

    Args:
# ...
```

### Hard-codes sample numbers/examples instead of checking digit order generically

- Cluster frequency: `14/420` (`3.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `14/420` (`3.3%`)
- Dominant private-case vectors: `100` x7, `000` x6, `101` x1
- Score distribution (top): `33.0` x7, `0.0` x6, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `f65250d0ba134eeaac83cfe3f2e4a5a0`, summary `Wrong Answer`, score `0`, vector `000`

```python
    num=len(str(n))
    if num!=4:
        print("Enter a 4 digit number")
        return False
    rem1=n%10
    while n!=0:
        n=n//10
        rem2=n%10
        if(rem1<rem2):
            rem1=rem2
        else:
            return False
    return True
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
# ...
```

### Extracts digits using `/` (float division) instead of integer division `//`

- Cluster frequency: `14/420` (`3.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `14/420` (`3.3%`)
- Dominant private-case vectors: `101` x11, `100` x2, `000` x1
- Score distribution (top): `67.0` x11, `33.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `cd455bd6c66f44908ddaa2fb58e70b0e`, summary `Wrong Answer`, score `67`, vector `101`

```python
    l=[0,1,2,3]
    count =0
    for i in range(len(l)):
        #while n/10!=0:
        rem=n%10
        l[i]=rem
        n=n/10
    for i in range(len(l)-1):
        if(l[i]==l[i+1]):
            count=0
            break
        elif(l[i]<l[i+1]):
            count=count+1
        """elif(l[i]==l[i+1]):
            count=0"""
    if count==3:
        return True
    else:
# ...
```

### Runtime TypeError from mixed string/int digit operations or invalid sorted/index logic

- Cluster frequency: `13/420` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `13/420` (`3.1%`)
- Dominant private-case vectors: `000` x12, `100` x1
- Score distribution (top): `0.0` x12, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `02d8318114704f26aff53b4e426fcde7`, summary `Runtime Error`, score `0`, vector `000`

```python
#def is_decreasing_number(n: int) -> bool:
n = int()
#is_decreasing_number(n)
while(n >= 0):
    num = False
    i = 0
    for i in range(i,3):
        if(n[i] < n[i+1]):
            num = False
            break
        else:
            num = True

if(num == True):
    print("True")
else:
    print
```

### Uses sorted-descending digit check (accepts duplicates; not strict decreasing)

- Cluster frequency: `11/420` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `11/420` (`2.6%`)
- Dominant private-case vectors: `101` x6, `100` x4, `000` x1
- Score distribution (top): `67.0` x6, `33.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `086ecfde88dd41aeb5c759aecb385433`, summary `Wrong Answer`, score `67`, vector `101`

```python
    n_str = str(n)
    strlen = len(n_str)
    n_str_r = n_str[::-1]
    l= []
    count = 0
    p = int(n_str[1])
    if n_str == n_str_r:
        return False
    else:
        for i in range(strlen):
            num = int(n_str[i])
            l.append(num)
        l_rev = sorted(l, reverse = True)
        if l == l_rev:
            return True
        else:
            return False
```

### Sorted/non-strict decreasing check bug (duplicates like `5433` slip through)

- Cluster frequency: `10/420` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `10/420` (`2.4%`)
- Dominant private-case vectors: `101` x10
- Score distribution (top): `67.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `45f70339477144b68a58f71aa08e8a2c`, summary `Wrong Answer`, score `67`, vector `101`

```python
    p = n % 10
    q= n % 100
    r= n% 1000
    s = n % 10000
    if s >r and r>q and q>p:
        return True
    elif s==r and r==q and q==p:
        return False
    else:
        return False
```

### Uses non-strict comparisons (`>=`/`<=`), so equal adjacent digits can be accepted

- Cluster frequency: `10/420` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `10/420` (`2.4%`)
- Dominant private-case vectors: `100` x6, `000` x3, `101` x1
- Score distribution (top): `33.0` x6, `0.0` x3, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `98fa4e48f12e4559804968079534f2f3`, summary `Wrong Answer`, score `33`, vector `100`

```python
    temp = n
    L=[]
    k = True
    for i in range(0,4):
        t = temp%10
        L.append(t)
    k = True
    for i in range(0,3):
        if(L[i]<=L[i+1]):
            continue
        else:
            k = False
    return k
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
# ...
```

### Runtime NameError

- Cluster frequency: `8/420` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `8/420` (`1.9%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `7a58abeeabab4720a439fd991ac91331`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    b=[]
    a=(n//k)
    c=0
    for i in range(k):
        c=n-a
        g=(a-i)
        if g==0:
            div=c//(g+1)
        else:
            div=c//g
        b.append(div)
    return b
```

### Reads `input()` inside function (EOF under evaluator function-call tests)

- Cluster frequency: `6/420` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `6/420` (`1.4%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `8e64567aa0914ad09221d0884e102fbf`, summary `Runtime Error`, score `0`, vector `000`

```python
    n=int(input())
    for i in range:
        if n is decreasing:
            return true
    '''
    Given a 4-digit number, check if its digits are strictly decreasing
    from left to right.

    Examples:
    >>> is_decreasing_number(4321)
    True
    >>> is_decreasing_number(4312)
    False
    >>> is_decreasing_number(9876)
    True
    >>> is_decreasing_number(1111)
    False
    >>> is_decreasing_number(3210)
# ...
```

### Requires consecutive step of exactly 1 between digits (rejects valid decreasing numbers like `5431`)

- Cluster frequency: `5/420` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `5/420` (`1.2%`)
- Dominant private-case vectors: `110` x4, `101` x1
- Score distribution (top): `67.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `30c8b3477738484296171f6a2d6655fd`, summary `Wrong Answer`, score `67`, vector `110`

```python
    ...
    '''lst=[]
    while n>0:
        x=int(n%10)
        n=int(n//(10))
        lst.append(x)
    flag=False
    for i in range(3):
        if (lst[i]<lst[i+1]):
            flag=True
        else:
            flag=False
    return flag'''
    s1="9876543210"
    s2=str(n)
    if s2 in s1:
        return True
    else:
# ...
```

### Always returns `False` (constant output)

- Cluster frequency: `5/420` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `5/420` (`1.2%`)
- Dominant private-case vectors: `100` x4, `101` x1
- Score distribution (top): `33.0` x4, `67.0` x1
- Interpretation: Constant-output bug: function returns `False` regardless of input.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `528f1f727103421e9338fe6ff46da584`, summary `Wrong Answer`, score `33`, vector `100`

```python
    ...
    num = str(n)
    nums = num.split()
    for i in range(len(nums)):
        if i < len(nums)-1:
            if nums[i] > nums[i + 1]:
                return True
            else:
                return False
            break
    if False:
        return False
    else:
        return True
```

### Runtime AttributeError

- Cluster frequency: `4/420` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `4/420` (`1.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `f9495838528e4f98ae84d89d38e3dfd9`, summary `Runtime Error`, score `0`, vector `000`

```python
    check = True
    t = n.list
    if t[0] < t[1]:
        check = False
        if t[1] < t[2]:
            check = False
            if t[2] < t[3]:
                check = False
    else :
        check = True
    return check
```

### Runtime error (parseable final submission)

- Cluster frequency: `4/420` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `4/420` (`1.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `8fba234557d94057ae3d7f589c52756e`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    if n < 1000 or n > 9999:
    # print("value must be a 4 digit number")

        digits = (int (d) for d in str (n))
    return digits(0) > digits (1) > digits(2) > digits (3)
```

### Runtime NameError from lowercase `true`/`false` or typoed identifier

- Cluster frequency: `3/420` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `3/420` (`0.7%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `edb1300740f946009f4fe4eb0cf73ed4`, summary `Runtime Error`, score `0`, vector `000`

```python
    for i in range(1000<n<9999):
            if (n(i1>i2>i3)):
                return True
            else:
                return False
```

### Consecutive-step (`-1`) check bug (requires 1-step decreases, rejects valid cases like `5431`)

- Cluster frequency: `3/420` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `3/420` (`0.7%`)
- Dominant private-case vectors: `110` x3
- Score distribution (top): `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `1bd13e9ff636464b9f83a0f69c0f6fa3`, summary `Wrong Answer`, score `67`, vector `110`

```python
    n = abs(n)
    n_str = str(n)
    a = 0
    is_decending = True
    if len(n_str) == 1:
        return False
    for i in n_str:
        if a == 0:
            a = int(i)
        else:
            if int(i)<a:
                a = int(i)
                is_decending = True
            else:
                is_decending = False
    return is_decending
```

### Runtime IndexError from out-of-range digit indexing in comparison loop

- Cluster frequency: `2/420` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `2/420` (`0.5%`)
- Dominant private-case vectors: `001` x1, `000` x1
- Score distribution (top): `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `2640e9a942fe466486dc03ad6dbbb030`, summary `Runtime Error`, score `33`, vector `001`

```python
    num_list = []
    while n!=0:
        num = n % 10
        num_list.append(num)
        n //= 10
    for i in num_list:
        if num_list[i] < num_list[i+1]:
            return True
        elif num_list[i] == num_list[i+1]:
            return False
        else:
            return False
```

### Runtime ValueError

- Cluster frequency: `2/420` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `2/420` (`0.5%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `a3438897912e4de38a5ce49eaefa4ce4`, summary `Runtime Error`, score `0`, vector `000`

```python
    if n<=9999 and n>=1000:
        n=str(n)
        i=0
        for x in n:
            if (x[int(i)]<x[int(i+1)] and x[int(i+1)]<x[int(i+2)] and x[int(i+2)]< x[int(i+3)]):
                return True
                print("True")
            else:
                return False
                print("False")
    else:
        print("Enter only 4 digit number")
```

### Runtime RecursionError

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `0b4cc28f35474b64adb6fa769c896595`, summary `Runtime Error`, score `0`, vector `000`

```python
    is_decreasing_number(4321)
    list=[]
    a =is_decreasing_number/1000
    print(list.append(a))
    b = a/100
    print(list.append(b))
    c =b/10
    print(list.append(c))
    d= 1
    print(list.append(d))
    print(list)
    if(a>b and b>c and c>d):
        print(True)
    else:
        print(False)
```

### Returns a string/non-boolean representation instead of a boolean result

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `16d61530ea3d4d1693aa106f749ee8c0`, summary `Wrong Answer`, score `67`, vector `101`

```python
     return str(n)[0] > str(n)[1]> str(n)[3]
```

### Time Limit Exceeded

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `1a8b179f605f4c638d6193310eba7a99`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
    sum = ""
    n1 = str(n)
    while (n>=0):
        rem = n%10
        sum = sum+str(rem)
        n = n//10
    rev = sum[::-1]
    if rev == n1:
        return True
    else:
        return False
```

### Uses an incorrect 4-digit range check (`1000 <= n >= 9999` / wrong bounds)

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `1ad898f315fb4f3d9245f7326ce96aec`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if n<1000 or n>999:
        return False
        digits=int(n)
        return digits[0]>digits[1]>digits[2]>digits[3]
```

### Runtime IndexError

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `42938c8096a643a3a5ad6440b33075e5`, summary `Runtime Error`, score `0`, vector `000`

```python
    c = []
    while(n == 0):
        n %=10
        c.append(n)
    if(c[0] > c[1] > c[2] > c[3] == True):
        return True
```

### Always returns `True` due always-truthy condition / misplaced logic

- Cluster frequency: `1/420` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/5`: `1/420` (`0.2%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/5`, Student ID `d6517bdce12e49df817aa195d6da1fd6`, summary `Wrong Answer`, score `33`, vector `100`

```python
    i = 0
    while i<4:
        digit = (n) % 10
        n = n//10
        i+=1
    return True if digit > n//10 else False
```
