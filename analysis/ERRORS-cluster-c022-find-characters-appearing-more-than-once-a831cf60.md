# Error Patterns: Cluster C022 (`Find Characters Appearing More Than Once`)

## Cluster Summary

- Cluster ID: `C022`
- Cluster title: `Find Characters Appearing More Than Once`
- Cluster file (this file): `analysis/ERRORS-cluster-c022-find-characters-appearing-more-than-once-a831cf60.md`
- Variants in cluster: `2`
- Total final submitters across variants: `564`
- Total non-full final submissions across variants: `317`
- Canonical variant (by submissions): `ns_25t3_py13_1/10`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py13_1/10` (canonical) | 564 | 317 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py13_1/10.json`
- Other variants in cluster:
  - `problems/ns_25t3_py13_2/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `564`
- Full pass: `247`
- Non-full final submissions: `317`
- Parseable non-full (logic/runtime focus): `263`
- Non-parseable non-full: `54`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py13_1/10` | 564 | 247 | 317 | 263 | 54 |
| `ns_25t3_py13_2/10` | 0 | 0 | 0 | 0 | 0 |

## Private Case Structure

- Private case 1: repeated characters where first-appearance order matters (`['l', 'e']` style output)
- Private case 2: another repeated-character case to distinguish dedupe/order logic from raw occurrence counting
- Private case 3: `mississippi`-style case where second-appearance order differs from first-appearance order

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py13_1/10` | `ns_25t3_py13_2/10` |
| --- | ---: | ---: | ---: | ---: |
| Incorrect repeated-character detection logic (returns wrong type/order/content) | 118 | 37.2% | 118 | 0 |
| Syntax / non-parseable final submission | 54 | 17.0% | 54 | 0 |
| Runtime TypeError from invalid indexing/loop variables while scanning repeated characters | 15 | 4.7% | 15 | 0 |
| Uses `split()`/word-based logic, but the task is about repeated characters within a single string | 15 | 4.7% | 15 | 0 |
| No return / implicit `None` | 15 | 4.7% | 15 | 0 |
| Appends a character every time `count(ch) > 1`, so repeated characters appear multiple times in the output list | 12 | 3.8% | 12 | 0 |
| Builds repeated characters and then converts to `set`, which destroys the required first-appearance order | 11 | 3.5% | 11 | 0 |
| Hard-codes sample outputs/examples instead of detecting repeated characters from arbitrary input | 11 | 3.5% | 11 | 0 |
| Runtime NameError from undefined lists/counters in repeated-character tracking | 11 | 3.5% | 11 | 0 |
| Tracks repeats in the order of second appearance (`seen`/`repeated` sets), not the required first appearance order | 10 | 3.2% | 10 | 0 |
| Second-appearance order bug (`seen`/`repeated` approach): output order is wrong on cases like `mississippi` | 9 | 2.8% | 9 | 0 |
| Uses `set(s)` in the main scan, which loses first-appearance order of repeated characters | 7 | 2.2% | 7 | 0 |
| Order-loss bug from using `set(...)`/`list(set(...))` (repeated characters found, but output order is unstable/incorrect) | 7 | 2.2% | 7 | 0 |
| Lowercases the string, changing case-sensitive character identity and output order/values | 4 | 1.3% | 4 | 0 |
| Runtime error (parseable final submission) | 4 | 1.3% | 4 | 0 |
| Runtime IndexError from manual nested-index scans over the string | 3 | 0.9% | 3 | 0 |
| Runtime AttributeError from string/list API misuse in repeated-character logic | 3 | 0.9% | 3 | 0 |
| Reads `input()` inside function-type question (EOF under evaluator function-call tests) | 3 | 0.9% | 3 | 0 |
| Runtime RecursionError from accidental recursive `repeated_characters(...)` call | 2 | 0.6% | 2 | 0 |
| Time Limit Exceeded | 1 | 0.3% | 1 | 0 |
| Runtime ValueError | 1 | 0.3% | 1 | 0 |
| Converts the input to a set first, losing duplicate counts before checking which characters repeat | 1 | 0.3% | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/317` (`0.0%`)

### Incorrect repeated-character detection logic (returns wrong type/order/content)

- Cluster frequency: `118/317` (`37.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `118/317` (`37.2%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x118
- Score distribution (top): `0.0` x118
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `d7bdb014157343948d282f6009b7d1e3`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    for char in s:
        empty_list=[]
        empty_set=set(empty_list)
        repeated_char=[]
        repeated_count=False
        if char in empty_set:
            repeated_count=True
                #repeated_char.append(char)
            repeated_char.append(char)
        empty_set.add(char)
        repeated_count=False
    return repeated_char
    '''set1=set(s)
    update_list=int(list(set1))
    list1=list(s)
    l3=[]
    for i in list1:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `54/317` (`17.0%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `54/317` (`17.0%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x54
- Score distribution (top): `0.0` x54
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `012d1734e4f64314a776db3db2036f10`, summary `Runtime Error`, score `0`, vector `000`

```python
def repeated_characters(s: str) -> list:
    """Finds characters that appear more than once."""
    djbdkdnfngj rjjqr4rbjkn(for)
    jfjfjfffsfrrnfigbngeiuajalangn nnnnn
    github basestring memoryview flka;fjvirjgifjaj
    ajhngr fjvirjgifjaj
mc bdi ndfh print command idihiai dijngjgjgnritur;aa;;ajffgulskshghtgughggh
hsugutnufjsbvgbbre485eeeee54444444444444444THTHGHHH
 nmnnnnnndn
 ncn ixdin void type tuple print functions fijfiirn sir rj
 all el-oeooele.lkr fs getattr compile more than gm
 nkjnijokp-o0eifijfjgijrjgjnnfvm,wwssecbscwqcuw;gbg49vib
```

### Runtime TypeError from invalid indexing/loop variables while scanning repeated characters

- Cluster frequency: `15/317` (`4.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `15/317` (`4.7%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `9ab159d3418c45bca39a7ff27e3d4f6a`, summary `Runtime Error`, score `0`, vector `000`

```python
    l= list[s]
    count=0
    lst=[]
    for i in range(0,len(s)):
        if i not in lst :
            count = +1

        else :
            count = +2
            lst = +i
    return set(lst)
```

### Uses `split()`/word-based logic, but the task is about repeated characters within a single string

- Cluster frequency: `15/317` (`4.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `15/317` (`4.7%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `85f4806a7c544f4a9b5e25068665aaa7`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    p=0
    t = []
    word =""
    r = s[0]
    for char in range(len(s)) :

        if s[char] == r:
            p +=1
            if p>1:
                word +=s[char]
                word =word.split(",")
                return word
            r =s[char]
    return t
```

### No return / implicit `None`

- Cluster frequency: `15/317` (`4.7%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `15/317` (`4.7%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x15
- Score distribution (top): `0.0` x15
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `4f0915dbe2c8446bac7dd9cc9e4ae024`, summary `Wrong Answer`, score `0`, vector `000`

```python
def repeated_characters(s: str) -> list:
    """Finds characters that appear more than once."""
```

### Appends a character every time `count(ch) > 1`, so repeated characters appear multiple times in the output list

- Cluster frequency: `12/317` (`3.8%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `12/317` (`3.8%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `2553699800c043c0bf3ca3dbe8e8860c`, summary `Wrong Answer`, score `0`, vector `000`

```python
    repeat = []
    new_list = []
    for char in s:
        repeat.append(char)
    for char in repeat:
        if repeat.count(char) > 1:
            new_list.append(char)
    for char in new_list:
        if new_list.count(char) > 1:
            new_list.remove(char)
    return new_list
    """Finds characters that appear more than once."""
    ...
```

### Builds repeated characters and then converts to `set`, which destroys the required first-appearance order

- Cluster frequency: `11/317` (`3.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `11/317` (`3.5%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5, `001` x2, `100` x2, `101` x1
- Score distribution (top): `0.0` x5, `33.0` x4, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `559e4d91521e484faf2fb6b7bf816c4f`, summary `Wrong Answer`, score `67`, vector `101`

```python
     l=list(s)
     st=[]
     for i in range(len(l)):
         for j in range(len(l)):
             if i!=j:
                 if l[i]==l[j]:
                     st.append(l[i])
     str=list(set(st))
     return str
```

### Hard-codes sample outputs/examples instead of detecting repeated characters from arbitrary input

- Cluster frequency: `11/317` (`3.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `11/317` (`3.5%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `eeef87b3e12f4e26bba31f790ad923df`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if s == "programming":
        x = list(s)
        return [x[1],x[3],x[6]]

    else:
        a = list(s)
        l = []
        b = []
        for i in a:
            if i not in l:
                l.append(i)
            else:
                b.append(i)
        return b
```

### Runtime NameError from undefined lists/counters in repeated-character tracking

- Cluster frequency: `11/317` (`3.5%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `11/317` (`3.5%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x11
- Score distribution (top): `0.0` x11
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `6853ee16e23647bb924e2144676f2fd1`, summary `Runtime Error`, score `0`, vector `000`

```python
    char_count={}
    repeated_chars=[]
    seen_repeated=set()
    for char in s:
        charcounts[char]=charcounts.get(char,0)+1
        if char_counts[char]>1 and char not in seen_repeated:
            repeated_chars.append(char)
            seen_repeated.add(char)
    return repeated_chars
```

### Tracks repeats in the order of second appearance (`seen`/`repeated` sets), not the required first appearance order

- Cluster frequency: `10/317` (`3.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `10/317` (`3.2%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x6, `000` x4
- Score distribution (top): `33.0` x6, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `893505d5e44746be87b9a83d00ff6476`, summary `Wrong Answer`, score `0`, vector `000`

```python
    result=[]
    seen=set()
    repeated=set()
    for ch in s:
        if ch is seen:
            repeated.add(ch)
        else:
              seen.add(ch)
    for ch in s:
        if ch in repeated and ch not in resut:
           result.append(ch)
    return result
```

### Second-appearance order bug (`seen`/`repeated` approach): output order is wrong on cases like `mississippi`

- Cluster frequency: `9/317` (`2.8%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `9/317` (`2.8%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x9
- Score distribution (top): `33.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `babb0948afa54a87af52040f5f9e111d`, summary `Wrong Answer`, score `33`, vector `010`

```python
    acount = 0
    bcount = 0
    ccount = 0
    dcount = 0
    ecount = 0
    fcount = 0
    gcount = 0
    hcount = 0
    icount = 0
    jcount = 0
    kcount = 0
    lcount = 0
    mcount = 0
    ncount = 0
    ocount = 0
    pcount = 0
    qcount = 0
    rcount = 0
# ...
```

### Uses `set(s)` in the main scan, which loses first-appearance order of repeated characters

- Cluster frequency: `7/317` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `7/317` (`2.2%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3, `101` x2, `100` x2
- Score distribution (top): `0.0` x3, `67.0` x2, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `ccbb63e610d94a89921140103d9a0894`, summary `Wrong Answer`, score `0`, vector `000`

```python
    repeated = []
    for char in set(s):
        if s.count(char)>1:
            repeated.append(char)
        return repeated
    s = input()
    print(repeated_characters(s))
```

### Order-loss bug from using `set(...)`/`list(set(...))` (repeated characters found, but output order is unstable/incorrect)

- Cluster frequency: `7/317` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `7/317` (`2.2%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x4, `101` x2, `001` x1
- Score distribution (top): `33.0` x5, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `fe97ceea338c4b18bc9ad815c23c8244`, summary `Wrong Answer`, score `67`, vector `101`

```python
    list_s=list(s)
    set_s=set(list_s)
    mod_list=list(sorted(set_s))
    output=[]
    for x in list_s:
        if x in list_s[list_s.index(x)+1:]:
            output.append(x)
            for y in list_s:
                if y==x:
                    list_s.remove(y)
    return output
```

### Lowercases the string, changing case-sensitive character identity and output order/values

- Cluster frequency: `4/317` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `4/317` (`1.3%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2, `101` x1, `100` x1
- Score distribution (top): `0.0` x2, `67.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `ff687f6257d34c749fc7c3c42d22ac41`, summary `Wrong Answer`, score `33`, vector `100`

```python
    s=s.lower()
    s=list(s)
    s2=s.copy()
    l=[]
    for i in s:
        count=0
        for j in s:
            if i == j:
                count+=1
        if count>=2:
            l.append(i)
    l2=l[::-1]
    for i in l2:
        count=0
        for j in l2:
            if i == j:
                count+=1
        if count>=2:
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `4/317` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `4/317` (`1.3%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `11abcb87e1b7490bbd0d25ebcd6b86f4`, summary `Runtime Error`, score `0`, vector `000`

```python
def repeated_characters(s: str) -> list:
   """Finds characters that appear more than once."""
s=""
s1=[]
l=len(s)
i=0
for i in range(0,l):
    if s[i]==s[i+1]:
        s1.append(s[i])
        i=i+1
return (s1)
```

### Runtime IndexError from manual nested-index scans over the string

- Cluster frequency: `3/317` (`0.9%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `3/317` (`0.9%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `a1f2931aacb74a7eae4e46be573f8e0a`, summary `Runtime Error`, score `0`, vector `000`

```python
    l=[]
    for i in s:
        if s.count(i) > 1:

            l.append(i)
    x=len(l)
    y=[]
    for i in range(x-1) :
        for j in range(x-1):
            if l[i] == l[j] :
                l.remove(l[j])
                y.append(l[i])
    return y
```

### Runtime AttributeError from string/list API misuse in repeated-character logic

- Cluster frequency: `3/317` (`0.9%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `3/317` (`0.9%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `ad2a9dd19d934d9fb3d48032b92e2ca8`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    list = []
    new_list = []
    for i in range(0,len(s)):
        if s[i] in list:
            new_list.append(s[i])
        else :
            list.append(s[i])
    sorted.new_list
    return new_list
```

### Reads `input()` inside function-type question (EOF under evaluator function-call tests)

- Cluster frequency: `3/317` (`0.9%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `3/317` (`0.9%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `f8c2b831bcea4c23b8427cdfbe255e7f`, summary `Runtime Error`, score `0`, vector `000`

```python
    s= input()
    for i in range(1,n+1):
        repeated_characters=0
        for j in range(1,n+1):
            repeated_characters= (repeated_characters)+j
    print(repeated_characters)
```

### Runtime RecursionError from accidental recursive `repeated_characters(...)` call

- Cluster frequency: `2/317` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `2/317` (`0.6%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `28ddf89babfa4007889128d678232b5d`, summary `Runtime Error`, score `0`, vector `000`

```python
    count=0
    for i in s:
        if (i==s):
            count+=1
            list_of_character
            return count
    print(repeated_characters("programming"))
```

### Time Limit Exceeded

- Cluster frequency: `1/317` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `1/317` (`0.3%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `798fd6a07b5e405588a481ed1ec4785e`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
    L=[]
    t=s
    i=0
    while i<len(s):
        j=i+1
        while j<len(t):
            if s[i]==t[j]:
               L=L+s[i]
            j+=1
    return(L)
    """Finds characters that appear more than once."""
    ...
```

### Runtime ValueError

- Cluster frequency: `1/317` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `1/317` (`0.3%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `b4c1823ac2ac4b08921d4e99eb28931d`, summary `Runtime Error`, score `0`, vector `000`

```python
    l=[]
    i=0
    a=s.split('')
    for i in a:
        if i>=2:
            l.append[i]
            return l
```

### Converts the input to a set first, losing duplicate counts before checking which characters repeat

- Cluster frequency: `1/317` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py13_1/10`: `1/317` (`0.3%`)
  - `ns_25t3_py13_2/10`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py13_1/10`, Student ID `cfc82ecc4ec541b68afa05fe091c2d6c`, summary `Wrong Answer`, score `33`, vector `010`

```python
    unique_chars = set(s)
    result_list = [
        (char)
        for char in unique_chars
        if s.count(char)>1
        ]
    return result_list
```
