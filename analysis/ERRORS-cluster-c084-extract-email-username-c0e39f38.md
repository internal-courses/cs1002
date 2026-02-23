# Error Patterns: Cluster C084 (`Extract Email Username`)

## Cluster Summary

- Cluster ID: `C084`
- Cluster title: `Extract Email Username`
- Cluster file (this file): `analysis/ERRORS-cluster-c084-extract-email-username-c0e39f38.md`
- Variants in cluster: `1`
- Total final submitters across variants: `820`
- Total non-full final submissions across variants: `192`
- Canonical variant (by submissions): `ns_25t2_py13_2/6`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_2/6` (canonical) | 820 | 192 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/6.json`

## Cluster-Level Outcome Summary

- Final submitters: `820`
- Full pass: `628`
- Non-full final submissions: `192`
- Parseable non-full (logic/runtime focus): `116`
- Non-parseable non-full: `76`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_2/6` | 820 | 628 | 192 | 116 | 76 |

## Private Case Structure

- Private case 1: dotted username and short username across different domains (must return text before `@` only)
- Private case 2: more dotted usernames with varied domain lengths to catch fixed-slice/domain-length assumptions
- Private case 3: underscore username plus single-character username (`a@xyz.in`) edge case

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_2/6` |
| --- | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 76 | 39.6% | 76 |
| Incorrect email-username extraction logic (broad wrong-answer failure) | 26 | 13.5% | 26 |
| No return / implicit `None` | 22 | 11.5% | 22 |
| Hard-codes public sample usernames instead of extracting text before `@` | 11 | 5.7% | 11 |
| Runtime NameError | 10 | 5.2% | 10 |
| Returns the full email string instead of only the username | 10 | 5.2% | 10 |
| Runtime error (parseable final submission) | 6 | 3.1% | 6 |
| Uses fixed-length slicing (domain-length assumption) instead of splitting at `@` | 6 | 3.1% | 6 |
| Runtime TypeError from mixing string/list values in email-username extraction logic | 6 | 3.1% | 6 |
| Reads `input()` inside function (EOF under evaluator function-call tests) | 6 | 3.1% | 6 |
| Runtime AttributeError | 5 | 2.6% | 5 |
| Runtime RecursionError | 3 | 1.6% | 3 |
| Returns the first character encountered in a loop instead of accumulating characters before `@` | 2 | 1.0% | 2 |
| Extracts username then mutates it (`replace`/normalization), changing the required output | 1 | 0.5% | 1 |
| Runtime AttributeError from string/list API misuse while extracting username | 1 | 0.5% | 1 |
| Runtime TypeError | 1 | 0.5% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/192` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `76/192` (`39.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `76/192` (`39.6%`)
- Dominant private-case vectors: `000` x76
- Score distribution (top): `0.0` x76
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `37ed2d8f955c4f58baf8cefc3241dc20`, summary `Runtime Error`, score `0`, vector `000`

```python
def extract_email_username(email):
    '''
    Given an email address string of the form "username@domain.com",
    return just the username part (everything before the @ symbol).

    Examples:
    >>> extract_email_username("ananya.sharma@iitd.ac.in")
    "ananya.sharma"
    >>> extract_email_username("rahul123@gmail.com")
    "rahul123"
    >>> extract_email_username("priya_r@company.in")
    "priya_r"
    >>> extract_email_username("v.kumar@institute.edu")
    "v.kumar"

    Args:
        email (str): A valid email address

# ...
```

### Incorrect email-username extraction logic (broad wrong-answer failure)

- Cluster frequency: `26/192` (`13.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `26/192` (`13.5%`)
- Dominant private-case vectors: `000` x26
- Score distribution (top): `0.0` x26
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `9b6c4fdfc8ee45a1ad1c60aaccf00e93`, summary `Wrong Answer`, score `0`, vector `000`

```python
    n = len(email)
    remove = ''
    for char in range(n):
        if char == '@':
            remove += char
        else:
            None
        continue
    final_email = ''
    for char in email:
        if char in remove:
            continue
        else:
            final_email += char
    return final_email
```

### No return / implicit `None`

- Cluster frequency: `22/192` (`11.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `22/192` (`11.5%`)
- Dominant private-case vectors: `000` x22
- Score distribution (top): `0.0` x22
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `3eecee7cbc3e4c6c88fe4bfa5e110154`, summary `Wrong Answer`, score `0`, vector `000`

```python
def extract_email_username(email: str) -> str:
    '''
    Given an email address string of the form "username@domain.com",
    return just the username part (everything before the @ symbol).

    Examples:
    >>> extract_email_username("ananya.sharma@iitd.ac.in")
    "ananya.sharma"
    >>> extract_email_username("rahul123@gmail.com")
    "rahul123"
    >>> extract_email_username("priya_r@company.in")
    "priya_r"
    >>> extract_email_username("v.kumar@institute.edu")
    "v.kumar"

    Args:
        email (str): A valid email address

# ...
```

### Hard-codes public sample usernames instead of extracting text before `@`

- Cluster frequency: `11/192` (`5.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `11/192` (`5.7%`)
- Dominant private-case vectors: `000` x10, `110` x1
- Score distribution (top): `0.0` x10, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `f09b14135bf04899855d0912be420909`, summary `Wrong Answer`, score `0`, vector `000`

```python
    name = []
    username = []
    for i in range(len(email)):
        if(email[i]== '@'):
            break
        else:
            name.append(email[i])
    u = 0
    k = len(name)
    while u in range(1,k):
        if(u%2!=0):
            username = username.append()
    username = str(username)
    return username
    '''
    Given an email address string of the form "username@domain.com",
    return just the username part (everything before the @ symbol).

# ...
```

### Runtime NameError

- Cluster frequency: `10/192` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `10/192` (`5.2%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `a82a8fb5ec394dcf9e8a916d375095a7`, summary `Runtime Error`, score `0`, vector `000`

```python
    email = 'username@domain.com'
    symbol ='@'
    count = 0
    for symbol in email:
        count += 1

        if count == 1:
            for i in email:
                symbol[i] = int(a)
                if i < a:
                    return email[i]
```

### Returns the full email string instead of only the username

- Cluster frequency: `10/192` (`5.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `10/192` (`5.2%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `66be9395e3c843efb4ed33cc0bdcac15`, summary `Wrong Answer`, score `0`, vector `000`

```python
    ...
    """for i in range(len(email)):
        username = []
        while email[i] != "@" :
         username = email[i]
    return username"""
    return email[:11:]
```

### Runtime error (parseable final submission)

- Cluster frequency: `6/192` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `6/192` (`3.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `08d20a3c5e8341c6a2bcd16132a7401e`, summary `Runtime Error`, score `0`, vector `000`

```python
n=str(input('type your email id here:'))
if (n in 'n has only one @'):
    if(n in 'n is alpnum'):
        if(n in 'n has symbols'):
            print (n)
else:
    print('enter a valid email id')
```

### Uses fixed-length slicing (domain-length assumption) instead of splitting at `@`

- Cluster frequency: `6/192` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `6/192` (`3.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `1aa4af7b52b944b69ee5550bf9231cf1`, summary `Wrong Answer`, score `0`, vector `000`

```python
    return (f"{email[:11]}")
```

### Runtime TypeError from mixing string/list values in email-username extraction logic

- Cluster frequency: `6/192` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `6/192` (`3.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `54ac632c9a9a49e4bbb16d6cd80deed5`, summary `Runtime Error`, score `0`, vector `000`

```python
    username = email[1::"@"]
    extract_email_username = username
    return extract_email_username
    '''
    Given an email address string of the form "username@domain.com",
    return just the username part (everything before the @ symbol).

    Examples:
    >>> extract_email_username("ananya.sharma@iitd.ac.in")
    "ananya.sharma"
    >>> extract_email_username("rahul123@gmail.com")
    "rahul123"
    >>> extract_email_username("priya_r@company.in")
    "priya_r"
    >>> extract_email_username("v.kumar@institute.edu")
    "v.kumar"

    Args:
# ...
```

### Reads `input()` inside function (EOF under evaluator function-call tests)

- Cluster frequency: `6/192` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `6/192` (`3.1%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `752007b9b66a419abeb03dfa9345b8c5`, summary `Runtime Error`, score `0`, vector `000`

```python
    ...
    email = input('Enter the email ID: ')
    if c in email is '@':
        exact_email = email
        while c == '@':
            extract_email_username = c+c

    else:
        print('the email is not valid')
```

### Runtime AttributeError

- Cluster frequency: `5/192` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `5/192` (`2.6%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `3229b0f2292e4e0c91b1973ff048767a`, summary `Runtime Error`, score `0`, vector `000`

```python
    username = ""
    for char in email:
    #     username += email[i]
    #     if email[i] == '@:
    #         break
    #     username.del('@')
    # return str(username)
        username = username + char
        if char == "@":
            break
        username.remove("@")
    return username
```

### Runtime RecursionError

- Cluster frequency: `3/192` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `3/192` (`1.6%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `3d6127e9d7ba41ce9c385f920760654f`, summary `Runtime Error`, score `0`, vector `000`

```python
    email1: "sneha.verma@infosys.com"
    is_equal(extract_email_username("sneha.verma@infosys.com"),"sneha.verma")
    return(sneha.verma)
    email2: "arjun_k@tcs.co.in"
    is_equal(extract_email_username("arjun_k@tcs.co.in"),"arjun_k")
    return(arjun_k)
    email3: "neeraj.m@iitb.ac.in"
    is_equal(extract_email_username("neeraj.m@iitb.ac.in"),"neeraj.m")
    return(neeraj.m)
```

### Returns the first character encountered in a loop instead of accumulating characters before `@`

- Cluster frequency: `2/192` (`1.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `2/192` (`1.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `087db96b0d6d42ec976f8aef1d279861`, summary `Wrong Answer`, score `0`, vector `000`

```python
    username = str
    for i in email:
        if i == "@":
            break
        else:
            return i
```

### Extracts username then mutates it (`replace`/normalization), changing the required output

- Cluster frequency: `1/192` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `1/192` (`0.5%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `64ae9a7776ba4b7baf9422e816883bad`, summary `Wrong Answer`, score `67`, vector `110`

```python
    username = email.split('@')[0]
    return username.replace('_','')
```

### Runtime AttributeError from string/list API misuse while extracting username

- Cluster frequency: `1/192` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `1/192` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `8223a48491fc45eab57b0bcb2d624cc2`, summary `Runtime Error`, score `0`, vector `000`

```python
def extract_email_username (email: str) -> str:
    '''
    Given an email address string of the form "username@domain.com",
    return just the username part (everything before the @ symbol).

    Examples:
    >>> extract_email_username("ananya.sharma@iitd.ac.in")
    "ananya.sharma"
    >>> extract_email_username("rahul123@gmail.com")
    "rahul123"
    >>> extract_email_username("priya_r@company.in")
    "priya_r"
    >>> extract_email_username("v.kumar@institute.edu")
    "v.kumar"

    Args:
        email (str): A valid email address

# ...
```

### Runtime TypeError

- Cluster frequency: `1/192` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/6`: `1/192` (`0.5%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/6`, Student ID `a930f774eaca4c28b26700e87cc423b4`, summary `Runtime Error`, score `0`, vector `000`

```python
    username = ''
    n = email.index()
    username = email[0:(n-1)]
    return username
```
