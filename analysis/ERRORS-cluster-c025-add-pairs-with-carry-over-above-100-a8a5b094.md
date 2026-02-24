# Error Patterns: Cluster C025 (`Add Pairs with Carry Over Above 100`)

## Cluster Summary

- Cluster ID: `C025`
- Cluster title: `Add Pairs with Carry Over Above 100`
- Cluster file (this file): `analysis/ERRORS-cluster-c025-add-pairs-with-carry-over-above-100-a8a5b094.md`
- Variants in cluster: `2`
- Total final submitters across variants: `395`
- Total non-full final submissions across variants: `214`
- Canonical variant (by submissions): `ns_25t3_py14_1/13`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t3_py14_1/13` (canonical) |              395 |      214 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py14_1/13.json`
- Other variants in cluster:
  - `problems/ns_25t3_py14_2/11.json`

## Cluster-Level Outcome Summary

- Final submitters: `395`
- Full pass: `181`
- Non-full final submissions: `214`
- Parseable non-full (logic/runtime focus): `175`
- Non-parseable non-full: `39`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t3_py14_1/13` |              395 |       181 |      214 |                175 |                     39 |
| `ns_25t3_py14_2/11` |                0 |         0 |        0 |                  0 |                      0 |

## Private Case Structure

- Private case 1: carry propagation across multiple pairs (must reuse carry every step)
- Private case 2: includes exact-100 resets and a `200 0` pair (carry can be `100` and then reset later)
- Private case 3: repeated large sums causing carry to grow beyond two digits (tests correct `sum-100` recurrence)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                      | Cluster count | % of cluster non-full | `ns_25t3_py14_1/13` | `ns_25t3_py14_2/11` |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Syntax / non-parseable final submission                                                                                      |            39 |                 18.2% |                  39 |                   0 |
| Empty/comment-only final submission                                                                                          |            21 |                  9.8% |                  21 |                   0 |
| Incorrect carry-simulation program logic (input parsing, carry update, or output printing is broadly wrong)                  |            20 |                  9.3% |                  20 |                   0 |
| Reads each pair value on separate lines (`a=int(input()); b=int(input())`), causing input parsing failure on `a b` lines     |            17 |                  7.9% |                  17 |                   0 |
| Prints constant sample output lines instead of reading input pairs and simulating carry                                      |            13 |                  6.1% |                  13 |                   0 |
| Runtime TypeError from treating input strings/lists as numbers while computing carry                                         |            12 |                  5.6% |                  12 |                   0 |
| Reinitializes carry inside the loop, so carry does not persist across pairs                                                  |            12 |                  5.6% |                  12 |                   0 |
| Processes each pair independently without maintaining a carry state across iterations                                        |            11 |                  5.1% |                  11 |                   0 |
| Runtime ValueError from malformed pair parsing (`a b`) or incorrect integer conversion                                       |            11 |                  5.1% |                  11 |                   0 |
| Runtime NameError from undefined variables (`pairs`, `a`, `b`, `carry`) in carry-update logic                                |             9 |                  4.2% |                   9 |                   0 |
| Accumulates carry with `carry += ...` instead of assigning the new carry (`carry = sum - 100`)                               |             7 |                  3.3% |                   7 |                   0 |
| Reads only `n` (or an incomplete prefix) and never processes the required `n` pairs                                          |             6 |                  2.8% |                   6 |                   0 |
| Carry propagation/update bug: solution works on simpler steps but hidden multi-step carry behavior is wrong                  |             6 |                  2.8% |                   6 |                   0 |
| Runtime EOFError from wrong input protocol (extra `input()` calls or incorrect pair parsing)                                 |             5 |                  2.3% |                   5 |                   0 |
| Ignores the previous carry when computing the next sum (`sum = a + b` instead of `a + b + carry`)                            |             5 |                  2.3% |                   5 |                   0 |
| Runtime error (parseable final submission)                                                                                   |             4 |                  1.9% |                   4 |                   0 |
| Computes carry as a digit/flag (`0/1`, `//10`, `%10`) instead of the required overflow amount `sum - 100`                    |             3 |                  1.4% |                   3 |                   0 |
| Writes a helper/function-style solution (expects `pairs` or returns a list) instead of the required input/output program     |             3 |                  1.4% |                   3 |                   0 |
| Hard-codes the public sample carry outputs instead of simulating carry updates for arbitrary input pairs                     |             2 |                  0.9% |                   2 |                   0 |
| Parses `a b` using fixed string positions/line length instead of robust `split()` parsing (fails hidden widths like `200 0`) |             2 |                  0.9% |                   2 |                   0 |
| Prints the input pair values (`ai, bi`) instead of computing and printing carry outputs                                      |             1 |                  0.5% |                   1 |                   0 |
| Processes each pair independently and never feeds the previous carry into the next step                                      |             1 |                  0.5% |                   1 |                   0 |
| Stores all pairs and reprocesses them in a second loop, causing carry-order/reset mistakes                                   |             1 |                  0.5% |                   1 |                   0 |
| Runtime AttributeError from string/list method misuse while parsing pairs                                                    |             1 |                  0.5% |                   1 |                   0 |
| Partial carry simulation bug on hidden edge cases (exact-100/reset or carry reuse ordering)                                  |             1 |                  0.5% |                   1 |                   0 |
| Misses the exact-100 edge case (checks only `<100` and `>100` branches)                                                      |             1 |                  0.5% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/214` (`0.0%`)

### Syntax / non-parseable final submission

- Cluster frequency: `39/214` (`18.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `39/214` (`18.2%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x39
- Score distribution (top): `0.0` x39
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `4de7339f7cf64cc3b7330500858b953b`, summary `Runtime Error`, score `0`, vector `000`

```python
def add_pairs_with_carry_over():

   data = "5,30,40,80,30,10,90,90,15,5,5"
   nums = list(map(int, data.replace(","," ").split()))

   N = nums[0]
   values = nums[1:]

   current_carry=0
   result = []
   idx = 0

   for_ in range(N):
       A = values[idx]
       B = values[idx +1 ]
       idx += 2

       total_sum = A + B + current_carry
# ...
```

### Empty/comment-only final submission

- Cluster frequency: `21/214` (`9.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `21/214` (`9.8%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x21
- Score distribution (top): `0.0` x21
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `684a20602d664930ba2b14fce523a712`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

# sum = 0
# n = int(input())


# # a,b = int(input())
# sum += a
# sum += b
# if sum > 100:
#     sum -= 100
# else:
#     sum = 0
# print(sum)
```

### Incorrect carry-simulation program logic (input parsing, carry update, or output printing is broadly wrong)

- Cluster frequency: `20/214` (`9.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `20/214` (`9.3%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x20
- Score distribution (top): `0.0` x20
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `dbad691e4ce24e20a9bb20785182dab9`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here
n = 1
carry = 0
a1 = 90
b1 = 10
sum = a1 + b1 + carry
sum == carry
if sum > 100:
    carry = sum - 100
else:
    carry = 0
print(carry)

n = 2
carry = 0
a2 = 80
b2 = 30
sum = a2 + b2 + carry
# ...
```

### Reads each pair value on separate lines (`a=int(input()); b=int(input())`), causing input parsing failure on `a b` lines

- Cluster frequency: `17/214` (`7.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `17/214` (`7.9%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x17
- Score distribution (top): `0.0` x17
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `0d6d0d7e18e8435e8bdebac817580eba`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())
carry = 0
sum = 0
for _ in range(n):
    a, b = int(input()), int(input())
    print(a)
    if (int(a) + int(b)) <= 100:
        carry = 0
        sum = a + b
        print(carry)
    else:
        carry += 100 - (a + b)
        sum = a + b + carry
        print(carry)
```

### Prints constant sample output lines instead of reading input pairs and simulating carry

- Cluster frequency: `13/214` (`6.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `13/214` (`6.1%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x13
- Score distribution (top): `0.0` x13
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `5fef0945b0c84516907b91ce2a5ecb42`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

n=5
a1, b1 = 30, 40
a2, b2 = 80, 30
a3,b3 =  10, 90
a4,b4 =  90,15
a5, b5 = 5,5
sum1 = a1+b1
if sum1 >=100 :
    print(sum1 - 100 )
sum2 = a2+b2
if sum2 >=100 :
    print(sum2 -100)
sum3 = a3+b3
print(10)
sum3= a3+b3
if sum3>=100 :
# ...
```

### Runtime TypeError from treating input strings/lists as numbers while computing carry

- Cluster frequency: `12/214` (`5.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `12/214` (`5.6%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x12
- Score distribution (top): `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `02513462bc7544fbab76018300ebd9b3`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())
carry = 0
p = 0
while n != 0:
    k = input()
    j = list(k.split())
    if int(j[0]) + int(j[1]) + carry < 100:
        print(0)

    elif int(j[0]) + int(j[1]) >= 100:
        l = 100 - int(j[0]) - int(j[1])
        print(abs(l) + l)
        carry = abs(100 - int(j[0]) - int(j[1]))

    l = abs((j[0] + int(j[1] + carry - 100)))
# ...
```

### Reinitializes carry inside the loop, so carry does not persist across pairs

- Cluster frequency: `12/214` (`5.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `12/214` (`5.6%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `011` x5, `000` x4, `101` x2, `001` x1
- Score distribution (top): `67.0` x7, `0.0` x4, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `ec7f09358e9641d5ba12e643d5423190`, summary `Wrong Answer`, score `67`, vector `101`

```python
# Write your solution here

n = int(input())
carry = 0
for i in range(n):
    x = input()
    a, b = map(int, x.split(" "))
    if a + b + carry < 100:
        carry = 0
        print(carry)
    elif a + b + carry > 100:
        carry = (a + b + carry) - 100
        print(carry)
    elif a + b + carry <= 100:
        carry = 0
    else:
        None
```

### Processes each pair independently without maintaining a carry state across iterations

- Cluster frequency: `11/214` (`5.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `11/214` (`5.1%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x8, `101` x2, `001` x1
- Score distribution (top): `0.0` x8, `67.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `67217175654b46238df8e89497739220`, summary `Wrong Answer`, score `67`, vector `101`

```python
n = int(input())
l = []
for i in range(n):
    s = input()
    l.append(s)
count = 0
m = 0
for str in l:
    if len(str) <= 3:
        a = int(str[0])
        b = int(str[2])

    else:
        a = int(str[0:2])
        b = int(str[3:5])


# ...
```

### Runtime ValueError from malformed pair parsing (`a b`) or incorrect integer conversion

- Cluster frequency: `11/214` (`5.1%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `11/214` (`5.1%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x9, `011` x1, `001` x1
- Score distribution (top): `0.0` x9, `67.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `8062d3541f7c4b6a9dc03531b6f3c95d`, summary `Runtime Error`, score `33`, vector `001`

```python
n = int(input(""))
a = []
b = 0
c = 0
while n > 0:
    n1 = input("")
    x = [n1]
    a.append(x)
    n -= 1
for i in a:
    for j in i:
        if len(j) == 5:
            if int(j[:3]) == 100:
                print(1)
            elif len(j) == 5:
                b = int(j[:2]) + int(j[2:]) + c
                if b <= 100:
                    print(0)
# ...
```

### Runtime NameError from undefined variables (`pairs`, `a`, `b`, `carry`) in carry-update logic

- Cluster frequency: `9/214` (`4.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `9/214` (`4.2%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `f7f6eafcceab429ca88e5642658b1aff`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
l = []
carry = 0
n = int(input())
for i in range(n):
    ad = input().split(" ")
    l.append(ad)
for j in range(len(l)):
    sec = int(l[j][1])
    first = int(l[j][0])
    thie = sec + first
    ooh = thie - 100
    carry += ohh
    print(carry)

# l.strip().split
# print(l[1])
#     # for j in ad:
# ...
```

### Accumulates carry with `carry += ...` instead of assigning the new carry (`carry = sum - 100`)

- Cluster frequency: `7/214` (`3.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `7/214` (`3.3%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x5, `000` x2
- Score distribution (top): `33.0` x5, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `fc0c929d63144a97b8ef83ae22339e4a`, summary `Wrong Answer`, score `33`, vector `001`

```python
# Write your solution here
a = int(input())
lines = []
jj = "jwfnbdvew. "

for i in range(0, a):
    b = input()
    b += "            "
    lines.append(b)
carry = 0
r = 0
for i in lines:
    a = 0
    b = 0
    if i[0] != " " and i[1] != " " and i[2] != " ":
        a = int(str(i[0]) + str(i[1]) + str(i[2]))
    elif i[0] != " " and i[1] != " ":
        a = int(str(i[0]) + str(i[1]))
# ...
```

### Reads only `n` (or an incomplete prefix) and never processes the required `n` pairs

- Cluster frequency: `6/214` (`2.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `6/214` (`2.8%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `c208bfb67d3142779f9a58f3b9b3a060`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())
if n == 5:
    print("0")
    print("10")
    print("10")
    print("15")
    print("0")
if n == 3:
    print("10")
    print("20")
    print("20")
if n == 4:
    print("1")
    print("0")
    print("1")
    print("0")
```

### Carry propagation/update bug: solution works on simpler steps but hidden multi-step carry behavior is wrong

- Cluster frequency: `6/214` (`2.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `6/214` (`2.8%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `001` x5, `011` x1
- Score distribution (top): `33.0` x5, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `0bf505f40ebd407280d0bd14f70557e3`, summary `Wrong Answer`, score `33`, vector `001`

```python
# Write your solution here

n = int(input())
carry = 0
naw = n
new_a = ""
new_b = ""
while n > 0:
    a = input()

    i = 0
    q = len(a) - 1
    while a[i] != " ":
        new_a = new_a + a[i]
        i = i + 1

    while a[q] != " ":
        new_b = a[q] + new_b
# ...
```

### Runtime EOFError from wrong input protocol (extra `input()` calls or incorrect pair parsing)

- Cluster frequency: `5/214` (`2.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `5/214` (`2.3%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x5
- Score distribution (top): `0.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `16b60c17a91046a9a655943e3a2fb4a4`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

text1 = input()
text2 = input()
text3 = input()
text4 = input()
text5 = input()
text6 = input()

list = []
list.append(text2)
list.append(text3)
list.append(text4)
list.append(text5)
list.append(text6)

# print(list)

# ...
```

### Ignores the previous carry when computing the next sum (`sum = a + b` instead of `a + b + carry`)

- Cluster frequency: `5/214` (`2.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `5/214` (`2.3%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2, `001` x1, `101` x1, `011` x1
- Score distribution (top): `0.0` x2, `67.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `e7c8e4e301074b2e8f0cc39e1fe12d0e`, summary `Wrong Answer`, score `67`, vector `011`

```python
n = int(input())
carry = 0
diff = 0
for i in range(n):
    stg = str(input())
    a, b = map(int, stg.split(" "))
    sum = a + b
    if sum > 100:
        diff = sum - 100
        carry = carry + diff
        print(carry)
    else:
        if (sum + carry) > 100:
            print((sum + carry) - 100)
        else:
            print(0)
            carry = 0
```

### Runtime error (parseable final submission)

- Cluster frequency: `4/214` (`1.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `4/214` (`1.9%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `3e3d0f09ac434ed8ade5bb5aaa3870e1`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
n = int(input())
sum = 0
for i in (0, n):
    en = input(a, b)
    if a + b > 100:
        sum = sum - 100
        return sum
    else:
        sum = 0
        return sum
```

### Computes carry as a digit/flag (`0/1`, `//10`, `%10`) instead of the required overflow amount `sum - 100`

- Cluster frequency: `3/214` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `3/214` (`1.4%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `1a5d249d0db94993a497f65faf0da585`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here
n = int(input())
for k in range(n):
    c = input()
    l = c.split()
    d = (int(l[0])) + int(l[1])
    if d >= 100:
        if d % 10 != 0 and d > 104:
            f = 10 + d % 10
            print(f)

        else:
            print(10)
    else:
        print(0)
```

### Writes a helper/function-style solution (expects `pairs` or returns a list) instead of the required input/output program

- Cluster frequency: `3/214` (`1.4%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `3/214` (`1.4%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `3b2e576888344b8d9cf12ed523bdf17b`, summary `Wrong Answer`, score `0`, vector `000`

```python
    carry = 0
    c = []
    for a, b in pairs:
        total_sum = a + b + carry
        if total_sum<100:
            carry = 0

        else:
            carry = total_sum//10
            c.append(carry)
    return c
```

### Hard-codes the public sample carry outputs instead of simulating carry updates for arbitrary input pairs

- Cluster frequency: `2/214` (`0.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `2/214` (`0.9%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `cefbd2b624284ed2952b3d21e8b1c8b7`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())

i = 0

if n == 5:
    print(0)
    print(10)
    print(10)
    print(15)
    print(0)

elif n == 3:
    print(10)
    print(20)
    print(20)

# ...
```

### Parses `a b` using fixed string positions/line length instead of robust `split()` parsing (fails hidden widths like `200 0`)

- Cluster frequency: `2/214` (`0.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `2/214` (`0.9%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `8067e5d3fe4a4b68b94dcede8f3fde99`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())

for i in range(n):
    str1 = input()

    a = int(str1[0])
    b = int(str1[-1])

    carry_val = 0

    sum1 = a + b + carry_val
    if sum1 > 100:
        carry_val = sum1 - 100
        print(carry_val)
    else:
        carry_val = 0
# ...
```

### Prints the input pair values (`ai, bi`) instead of computing and printing carry outputs

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `0be95b2a0ecb411d8f81880b5a1edc67`, summary `Wrong Answer`, score `0`, vector `000`

```python
for i in range(n):
    print(ai, bi)
```

### Processes each pair independently and never feeds the previous carry into the next step

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `1008115a775d4077b77796f19977fd0d`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())
l = []
m = []
carry = 0
sum_1 = 0
for i in range(n):
    t = tuple(input())
    l1 = list(t)
    l.append(l1)

for i in range(n):
    sum_1 = int(l[i][0] + l[i][1])
    if sum_1 <= 100:
        m.append(0)
    if sum_1 > 100:
        carry = carry + (sum_1 - 100)
# ...
```

### Stores all pairs and reprocesses them in a second loop, causing carry-order/reset mistakes

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `69d20a8399374c8abd2d92b331bcf249`, summary `Wrong Answer`, score `67`, vector `101`

```python
n = int(input())

lines = []
carry = 0

for i in range(n):
    line = input()
    lines.append(line)

for line in lines:
    w = line.split(" ")
    sum = int(w[0]) + int(w[1]) + carry
    if sum > 100:
        carry = sum - 100
    if sum < 100:
        carry = 0
    print(carry)
```

### Runtime AttributeError from string/list method misuse while parsing pairs

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `b358e2a6027646f3b3f2058dd42b7097`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here

n = int(input())
lst = []
for i in range(n):
    lst.append(input)

car = 0
car = int(car)

for i in range(n):
    addn = 0
    addn += lst[i].append([car])
    if addn > 100:
        car = addn - 100
        print(car)
```

### Partial carry simulation bug on hidden edge cases (exact-100/reset or carry reuse ordering)

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `101` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `c99486767b1f4379a051f0eecc02da20`, summary `Wrong Answer`, score `67`, vector `101`

```python
carry = 0

n = int(input(""))
i = 1

while i <= n:
    Given = input("")
    a = int(Given[0:2])
    b = int(Given[-2:])
    if (a + b + (carry)) >= 100:
        carry = a + b + (carry) - 100

    else:
        carry = 0
    print(carry)
    i = i + 1
```

### Misses the exact-100 edge case (checks only `<100` and `>100` branches)

- Cluster frequency: `1/214` (`0.5%`)
- Variant frequencies:
  - `ns_25t3_py14_1/13`: `1/214` (`0.5%`)
  - `ns_25t3_py14_2/11`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/13`, Student ID `d0bdd7c331534291a148e6e63778b17d`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())
for i in range(0, n):
    s = input()
    a = s.split()
    a1 = int(a[0])
    b1 = int(a[1])
    carry = 0
    sum = a1 + b1 + carry
    if sum < 100:
        print(carry)
    elif sum > 100:
        c = sum - 100
        sum = a1 + b1 + carry + c
        print(c)
```
