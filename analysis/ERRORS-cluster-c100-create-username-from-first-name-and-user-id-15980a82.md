# Error Patterns: Cluster C100 (`Create Username from First Name and User ID`)

## Cluster Summary

- Cluster ID: `C100`
- Cluster title: `Create Username from First Name and User ID`
- Cluster file (this file): `analysis/ERRORS-cluster-c100-create-username-from-first-name-and-user-id-15980a82.md`
- Variants in cluster: `1`
- Total final submitters across variants: `495`
- Total non-full final submissions across variants: `89`
- Canonical variant (by submissions): `ns_25t3_py22/6`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py22/6` (canonical) | 495 | 89 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py22/6.json`

## Cluster-Level Outcome Summary

- Final submitters: `495`
- Full pass: `406`
- Non-full final submissions: `89`
- Parseable non-full (logic/runtime focus): `70`
- Non-parseable non-full: `19`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py22/6` | 495 | 406 | 89 | 70 | 19 |

## Private Case Structure

- Private case 1: exactly-3-character mixed-case name (`Amy`) should produce lowercase prefix + ID
- Private case 2: another exactly-3-character mixed-case name (`Max`) to catch sample-initial-specific logic
- Private case 3: 2-character name (`Li`) must use full lowercase name (no indexing `name[2]`)
- Private case 4: longer name (`Franklin`) must truncate to first 3 lowercase letters before concatenating ID
- Private case 5: single-character name (`a`) edge case (no indexing past length 1)

Private-case vectors in this report are 5-character pass/fail strings over the private case groups (e.g., `10001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py22/6` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 19 | 21.3% | 19 |
| No return / implicit `None` | 7 | 7.9% | 7 |
| Hard-codes public sample usernames/names instead of generating the username from arbitrary inputs | 7 | 7.9% | 7 |
| Uses the first 3 characters but forgets to lowercase the name prefix | 7 | 7.9% | 7 |
| Username construction logic is broadly incorrect (lowercasing, prefix length, or input usage) | 6 | 6.7% | 6 |
| Reads `input()` in a function-type question instead of using `first_name, user_id` parameters | 5 | 5.6% | 5 |
| Runtime TypeError | 5 | 5.6% | 5 |
| Runtime error (parseable final submission) | 4 | 4.5% | 4 |
| Runtime NameError | 4 | 4.5% | 4 |
| Calls `create_username(...)` inside itself using sample examples (recursive/self-test code in function) | 4 | 4.5% | 4 |
| Uses undefined lowercasing helper/identifier (`lower`, `lowercase`) instead of `.lower()` | 4 | 4.5% | 4 |
| Misuses string APIs (`tolower`, `.append`, or `.lower` without proper call/usage) while building username | 3 | 3.4% | 3 |
| Short-name edge-case bug: indexes `[0],[1],[2]` in a branch that still runs for names shorter than 3 | 3 | 3.4% | 3 |
| Lowercases only specific sample initials (A/B/J) instead of calling `.lower()` on the whole name | 2 | 2.2% | 2 |
| Lowercases the full name but forgets to truncate to the first 3 characters for long names | 2 | 2.2% | 2 |
| Branch initialization bug: `id_str` is defined only in one branch and used in both | 1 | 1.1% | 1 |
| References `.lower` but does not call it (`.lower()` missing) | 1 | 1.1% | 1 |
| Runtime ValueError | 1 | 1.1% | 1 |
| Indexes the first three characters without a safe short-name guard (`len(name) < 3`) | 1 | 1.1% | 1 |
| Sample-specific/manual case handling (initial-letter-specific logic) instead of general lowercase+prefix logic | 1 | 1.1% | 1 |
| Length-branch bug: long names return the full name instead of a 3-letter prefix | 1 | 1.1% | 1 |
| Single hidden-case miss: truncation/length-branch logic is wrong for one name-length scenario | 1 | 1.1% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/89` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `19/89` (`21.3%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `19/89` (`21.3%`)
- Dominant private-case vectors: `00000` x19
- Score distribution (top): `0.0` x19
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `a41b220edd2841edbcb120e05d05cadb`, summary `Runtime Error`, score `0`, vector `00000`

```python
def create_username(first_name: str, user_id: int) -> str:
    """
    Create a username from the first name and user ID.

    The username is formed by taking the first three letters of the first name
    in lowercase and concatenating it with the user ID. If the first name has
    fewer than three letters, the entire name in lowercase is used.

    Parameters:
    first_name (str): The first name of the user.
    user_id (int): The user ID.

    Returns:
    str: The generated username.
    """



# ...
```

### No return / implicit `None`

- Cluster frequency: `7/89` (`7.9%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `7/89` (`7.9%`)
- Dominant private-case vectors: `00000` x7
- Score distribution (top): `0.0` x7
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `9aad4589179f4aa19c8334a34ef68664`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def create_username(first_name: str, user_id: int) -> str:
    """
    Create a username from the first name and user ID.

    The username is formed by taking the first three letters of the first name
    in lowercase and concatenating it with the user ID. If the first name has
    fewer than three letters, the entire name in lowercase is used.

    Parameters:
    first_name (str): The first name of the user.
    user_id (int): The user ID.

    Returns:
    str: The generated username.
    """
```

### Hard-codes public sample usernames/names instead of generating the username from arbitrary inputs

- Cluster frequency: `7/89` (`7.9%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `7/89` (`7.9%`)
- Dominant private-case vectors: `00000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `47a311a308e745228f5d3b9cda3048a9`, summary `Wrong Answer`, score `0`, vector `00000`

```python
    s='ali123'
    return(s)
    """
    Create a username from the first name and user ID.

    The username is formed by taking the first three letters of the first name
    in lowercase and concatenating it with the user ID. If the first name has
    fewer than three letters, the entire name in lowercase is used.

    Parameters:
    first_name (str): The first name of the user.
    user_id (int): The user ID.

    Returns:
    str: The generated username.
    """
    ...
```

### Uses the first 3 characters but forgets to lowercase the name prefix

- Cluster frequency: `7/89` (`7.9%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `7/89` (`7.9%`)
- Dominant private-case vectors: `00000` x7
- Score distribution (top): `20.0` x5, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `ea309c5e01454a809cfafdd268e91219`, summary `Wrong Answer`, score `20`, vector `00000`

```python
    user_id_str = str(user_id)
    Name_id = first_name[:3]
    Digit_id = user_id_str[:-3]
    X = Name_id + user_id_str
    Upper_case = ("A", "B","C","D","I","J")
    Lower_case = ("a","b","c","d","i","j")
    if "A" in X:
        X= list(X)
        X[0] = "a"
    if "B" in X:
        X[0] = "b"
    if "C" in X:
        X[0] = "c"
    if "D" in X:
        X[0] = "d"
    if "I" in X:
        X[0] = "i"
    if "J" in X:
# ...
```

### Username construction logic is broadly incorrect (lowercasing, prefix length, or input usage)

- Cluster frequency: `6/89` (`6.7%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `6/89` (`6.7%`)
- Dominant private-case vectors: `00000` x6
- Score distribution (top): `0.0` x5, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `754bdc34424d45fd88bd49fbb8cf5e34`, summary `Wrong Answer`, score `0`, vector `00000`

```python
   name_lower=first_name.lower()
   if len(name_lower)>=3:
       name_part=name_lower[:3]
   else:
        name_part=name_lower
   return f"{name_part}-{user_id}"
```

### Reads `input()` in a function-type question instead of using `first_name, user_id` parameters

- Cluster frequency: `5/89` (`5.6%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `5/89` (`5.6%`)
- Dominant private-case vectors: `00000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `cd2735a1e75240fbac10b254388ac951`, summary `Runtime Error`, score `0`, vector `00000`

```python
'''
    Create a username from the first name and user ID.

    The username is formed by taking the first three letters of the first name
    in lowercase and concatenating it with the user ID. If the first name has
    fewer than three letters, the entire name in lowercase is used.

    Parameters:
    first_name (str): The first name of the user.
    user_id (int): The user ID.

    Returns:
    '''
first_name = str(input())
user_id = int(input())

a = (first_name[0:4])
b =( user_id[0:4])
# ...
```

### Runtime TypeError

- Cluster frequency: `5/89` (`5.6%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `5/89` (`5.6%`)
- Dominant private-case vectors: `00000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `f6c4043e0ba14603afcda2ccd4186ae2`, summary `Runtime Error`, score `0`, vector `00000`

```python
    '''ffname=first_name.islower()
    fname=ffname.split()

    fname=first_name.split()
    if len(fname)<3:
        str=fname+user_id
    else:
        str=fname[0:3]+user_id

    return str'''
    str=first_name[:3].islower()
    return str+str(user_id)
```

### Runtime error (parseable final submission)

- Cluster frequency: `4/89` (`4.5%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `4/89` (`4.5%`)
- Dominant private-case vectors: `00000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `d86ff343593a4b19ba87300797f6c684`, summary `Runtime Error`, score `0`, vector `00000`

```python
def create_username(first_name: str, user_id: int) -> str:
    """
    Create a username from the first name and user ID.

    The username is formed by taking the first three letters of the first name
    in lowercase and concatenating it with the user ID. If the first name has
    fewer than three letters, the entire name in lowercase is used.

    Parameters:
    first_name (str): The first name of the user.
    user_id (int): The user ID.

    Returns:
    str: The generated username.
    """
if len(first_name)<2 :
    return first_name.lower() + str(user_id)
else:
# ...
```

### Runtime NameError

- Cluster frequency: `4/89` (`4.5%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `4/89` (`4.5%`)
- Dominant private-case vectors: `00000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `eb5f9f921c2b4592ac6359e22592491e`, summary `Runtime Error`, score `0`, vector `00000`

```python
'''def create_username(first_name: str, user_id: int) -> str:
first_name = str(input('enter the first name: '))
user_id = int(input('enter the user id: '))
 a = first_name
 b = user_id
 username = (a.list[2]) + (b.list[2])
 print (username)
'''
print ("'ali123'")
```

### Calls `create_username(...)` inside itself using sample examples (recursive/self-test code in function)

- Cluster frequency: `4/89` (`4.5%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `4/89` (`4.5%`)
- Dominant private-case vectors: `00000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `93a166dcb2594bb58c52afb865e68937`, summary `Runtime Error`, score `0`, vector `00000`

```python
    create_username("Alice",123)
    create_username("Bob",456)
    create_username("Jo",789)
    first_name=lower(first_name)
```

### Uses undefined lowercasing helper/identifier (`lower`, `lowercase`) instead of `.lower()`

- Cluster frequency: `4/89` (`4.5%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `4/89` (`4.5%`)
- Dominant private-case vectors: `00000` x3, `00100` x1
- Score distribution (top): `0.0` x3, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `9e7799fd5704490d91f7a12b88ffef49`, summary `Runtime Error`, score `20`, vector `00100`

```python
    if (first_name[0]=="A"):
       l=list(first_name)
       l[0]="a"
       first_name1=str(l[0]+l[1]+l[2])
       return first_name1+str(user_id)
    elif (first_name[0]=="B"):
        l=list(first_name)
        l[0]="b"
        first_name1=str(l[0]+l[1]+l[2])
        return first_name1+str(user_id)
    elif (first_name[0]=="J"):
        l=list(first_name)
        l[0]="j"
        first_name1=str(l[0]+l[1])
        return first_name1+str(user_id)
    else:
        first_name2=lower(first_name)
        l=list(first_name2)
# ...
```

### Misuses string APIs (`tolower`, `.append`, or `.lower` without proper call/usage) while building username

- Cluster frequency: `3/89` (`3.4%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `3/89` (`3.4%`)
- Dominant private-case vectors: `00000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `20d7219dccd8427ca1eb239f3f8d5dc9`, summary `Runtime Error`, score `0`, vector `00000`

```python
    '''name2 = tolower(first_name)
    name1 = name2.split("")
    name = name1[:3]
    name= "".join(name)
    username = name + user_id
    return username'''
    name = list(first_name)
    name1 = name[:3]
    name2 = str(name)
    name_made = name2.tolower()
    username = name_made + user_id
    print(username)
```

### Short-name edge-case bug: indexes `[0],[1],[2]` in a branch that still runs for names shorter than 3

- Cluster frequency: `3/89` (`3.4%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `3/89` (`3.4%`)
- Dominant private-case vectors: `00111` x3
- Score distribution (top): `80.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `5b5aa1138e494ddbbd21e8204bc65149`, summary `Runtime Error`, score `80`, vector `00111`

```python
    if len(first_name)>=3:
        username = first_name[0] + first_name[1] + first_name[2]
        new = username.lower() + str(user_id)
    else:
         username = first_name[0] + first_name[1]
         new = username.lower() + str(user_id)
    return new
```

### Lowercases only specific sample initials (A/B/J) instead of calling `.lower()` on the whole name

- Cluster frequency: `2/89` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `2/89` (`2.2%`)
- Dominant private-case vectors: `00100` x2
- Score distribution (top): `40.0` x1, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `aa1711c3f28f4377b046245af20cca2a`, summary `Wrong Answer`, score `20`, vector `00100`

```python
    if len(first_name)>2:
        u1=first_name[0]
        u2=first_name[1]
        u3=first_name[2]
        ID=int(user_id)
        if u1=="A":
            u1='a'
        else:
            u1='b'
        return str(u1+u2+u3+str(ID))

    else:
        u1="j"
        u2="o"
        ID=int(user_id)
        return str(u1+u2+str(ID))
    """
    Create a username from the first name and user ID.
# ...
```

### Lowercases the full name but forgets to truncate to the first 3 characters for long names

- Cluster frequency: `2/89` (`2.2%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `2/89` (`2.2%`)
- Dominant private-case vectors: `00111` x2
- Score distribution (top): `80.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `1a9f1dbd648949719d08a622569a4181`, summary `Wrong Answer`, score `80`, vector `00111`

```python
    firstnl = first_name.lower()
    num = str(user_id)
    name = list(firstnl)
    uid = []
    x = 0
    for i in range(len(name)):
        if i < 3:
            uid.insert(i,name[i])
            x = x+1
    x = x+1
    for y in range(len(num)):

        if y < 3:
            uid.insert(x+i,num[y])
    '''if len(uidn) >= 3:

        uid.insert(0,uidn[0])
        uid.insert(1,uidn[1])
# ...
```

### Branch initialization bug: `id_str` is defined only in one branch and used in both

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00110` x1
- Score distribution (top): `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `22657508945141ee8b9ea86ea444fd71`, summary `Runtime Error`, score `60`, vector `00110`

```python
    lower_name = first_name.lower()
    if len(lower_name)<3:
        prefix = lower_name

    else:
        prefix = lower_name [:3]
        id_str = str(user_id)
    return prefix + id_str
```

### References `.lower` but does not call it (`.lower()` missing)

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00111` x1
- Score distribution (top): `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `2a4504f6e5e54c5380b4d921c35a26a1`, summary `Wrong Answer`, score `80`, vector `00111`

```python
    username=str.lower(first_name)
    id=str(user_id)
    return username+id
```

### Runtime ValueError

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `3c148ff7692f4e409fa15d83d2a61227`, summary `Runtime Error`, score `0`, vector `00000`

```python
    if len(int(first_name)<=3):
        return f"({first_name.lower()}{user_id})"
```

### Indexes the first three characters without a safe short-name guard (`len(name) < 3`)

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00110` x1
- Score distribution (top): `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `49c4a4ec711e4a1485a1bef3f6f0fb4e`, summary `Runtime Error`, score `60`, vector `00110`

```python
    lowered_first_name = first_name.lower()
    str_user_id = str(user_id)
    return(lowered_first_name[0] + lowered_first_name[1] +lowered_first_name[2] +str_user_id)
```

### Sample-specific/manual case handling (initial-letter-specific logic) instead of general lowercase+prefix logic

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00100` x1
- Score distribution (top): `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `5bb283b71c664564aae8172a8eff39a7`, summary `Wrong Answer`, score `20`, vector `00100`

```python
    if c==0:
        return '0'
    elif c==1:
        return '1'
    elif c==2:
        return '2'
    elif c==3:
        return '3'
    elif c==4:
        return '4'
    elif c==5:
        return '5'
    elif c==6:
        return '6'
    elif c==7:
        return '7'
    elif c==8:
        return '8'
# ...
```

### Length-branch bug: long names return the full name instead of a 3-letter prefix

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00111` x1
- Score distribution (top): `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `676b6777bdaf45c090e9351a216f5d7d`, summary `Wrong Answer`, score `80`, vector `00111`

```python
    first_name = first_name.lower()
    if len(first_name)<=3:
        username = first_name[:3] + str(user_id)
    else:
        username = first_name + str(user_id)
    return username
```

### Single hidden-case miss: truncation/length-branch logic is wrong for one name-length scenario

- Cluster frequency: `1/89` (`1.1%`)
- Variant frequencies:
  - `ns_25t3_py22/6`: `1/89` (`1.1%`)
- Dominant private-case vectors: `00111` x1
- Score distribution (top): `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py22/6`, Student ID `b265e26a24de49ab82a47006247b717a`, summary `Wrong Answer`, score `80`, vector `00111`

```python
    username=''
    swap_first=first_name.swapcase()
    username+=swap_first[0]
    if len(first_name)>3:
        for i in (1,2):
            username+=first_name[i]

    else:
        for i in range(1,len(first_name)):
            username+=first_name[i]
    ID=str(user_id)
    for x in range(len(ID)):
        username+=  ID[x]
    return username
```
