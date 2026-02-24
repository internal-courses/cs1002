# Error Patterns: Cluster C008 (`Pattern Printing - W Pattern`)

## Cluster Summary

- Cluster ID: `C008`
- Cluster title: `Pattern Printing - W Pattern`
- Cluster file (this file): `analysis/ERRORS-cluster-c008-pattern-printing-w-pattern-35071c74.md`
- Variants in cluster: `3`
- Total final submitters across variants: `367`
- Total non-full final submissions across variants: `180`
- Canonical variant (by submissions): `ns_25t2_py12_1/13`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py12_1/13` (canonical) |              367 |      180 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py12_1/13.json`
- Other variants in cluster:
  - `problems/ns_25t1_py11_1/10.json`
  - `problems/ns_25t1_py_15_exe/13.json`

## Cluster-Level Outcome Summary

- Final submitters: `367`
- Full pass: `187`
- Non-full final submissions: `180`
- Parseable non-full (logic/runtime focus): `141`
- Non-parseable non-full: `39`

Variant-level comparison:

| Variant                | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ---------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t1_py11_1/10`    |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t1_py_15_exe/13` |                0 |         0 |        0 |                  0 |                      0 |
| `ns_25t2_py12_1/13`    |              367 |       187 |      180 |                141 |                     39 |

## Private Case Structure

- Private case 1: large `n=16` formatting case (spacing and exact character placement must scale)
- Private case 2: large `n=18` formatting case to catch sample-size hard-coding and spacing formulas
- Private case 3: large `n=20` formatting case; stresses generalized row construction and no extra spaces/newlines

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                    |                                                              Cluster count | % of cluster non-full | `ns_25t1_py11_1/10` | `ns_25t1_py_15_exe/13` | `ns_25t2_py12_1/13` |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------: | --------------------: | ------------------: | ---------------------: | ------------------: |
| Incorrect W-pattern printing logic (missing output, wrong row formula, or formatting mismatch)             |                                                                         54 |                 30.0% |                   0 |                      0 |                  54 |
| Syntax / non-parseable final submission                                                                    |                                                                         39 |                 21.7% |                   0 |                      0 |                  39 |
| Empty/comment-only final submission                                                                        |                                                                         24 |                 13.3% |                   0 |                      0 |                  24 |
| Row-spacing arithmetic is incorrect (bars/slashes are printed, but the W geometry/spacing is wrong)        |                                                                         22 |                 12.2% |                   0 |                      0 |                  22 |
| Hard-codes small sample sizes (`n=1/2/3/...`) with `if/elif` branches instead of a general pattern loop    |                                                                         16 |                  8.9% |                   0 |                      0 |                  16 |
| Runtime NameError                                                                                          |                                                                          4 |                  2.2% |                   0 |                      0 |                   4 |
| Hard-codes the public sample sizes (`n=1/2/5`, etc.) instead of generating the W pattern for arbitrary `n` |                                                                          4 |                  2.2% |                   0 |                      0 |                   4 |
| Uses a grid/nested-loop character plot that prints extra spaces/separators and fails exact row formatting  |                                                                          2 |                  1.1% |                   0 |                      0 |                   2 |
| Builds row strings by adding integers to strings (string-multiplication/concatenation arithmetic bug)      |                                                                          2 |                  1.1% |                   0 |                      0 |                   2 |
| Prints the same row (`                                                                                     |        /\\|`) repeatedly instead of widening the interior spacing each row |                     2 |                1.1% |                      0 |                   0 |
| Repeats bars/slashes/backslashes `n` times (`'                                                             | '*n`,`'/'*n`) instead of printing single boundary/slash characters per row |                     1 |                0.6% |                      0 |                   0 |
| Center-spacing off-by-two bug (`2*i-2`) breaks the first rows of the W pattern                             |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Submits a helper/function-style return value instead of reading `n` and printing the W pattern rows        |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Uses loop/size variables (`n`, `w`, etc.) without reading the input size first                             |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Reuses `n` as the loop variable (`for n in range(...)`), corrupting the intended pattern size              |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Uses invalid input conversion (`input(int())`) instead of reading the integer with `int(input())`          |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Builds placeholder row arrays (e.g., `['1 ']*...`) instead of constructing exact W rows with `             |                                                             `,`/`, and`\\` |                     1 |                0.6% |                      0 |                   0 |
| Unrelated pasted function/problem solution instead of W-pattern generation                                 |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Infinite loop in pattern generation (e.g., `while` loop that never updates the loop variable)              |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Hard-codes a specific W output (fixed rows) instead of generating the pattern from the input `n`           |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |
| Runtime error (parseable final submission)                                                                 |                                                                          1 |                  0.6% |                   0 |                      0 |                   1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/180` (`0.0%`)

### Incorrect W-pattern printing logic (missing output, wrong row formula, or formatting mismatch)

- Cluster frequency: `54/180` (`30.0%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `54/180` (`30.0%`)
- Dominant private-case vectors: `000` x54
- Score distribution (top): `0.0` x54
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `d759b7e50c9846ccae379b600b9a19b4`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

# |/\|
# | /\ |
# |/  \|

#|  /\  |
#| /  \ |
#|/    \|

n= int(input())

if (n==1):
    print('|/\\|')
elif(n==2):
    print('| /\\ |')
    print('|/  \\|')
elif(n==3):
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `39/180` (`21.7%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `39/180` (`21.7%`)
- Dominant private-case vectors: `000` x39
- Score distribution (top): `0.0` x39
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `611c2b762e9543909e7a29bee416438f`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

hi guys my name is mayank and i wanted to tell you
something that i won't repeat again in my life
my biggest problem of life is procrastination and inconsistency
and its been with me since I was born.
I only able to stay consistent with things that gives me pleasure like
mobile games, gym and going outside for a walk to shoot videos for instagram
and my youtube channel.
Now these things become part of my daily routine and I feel ashamed of myself
sometimes.
I was born as a performer in almost everything like sports, academics and some
extra-curriculum activities in school competiting with my friends of my childhood
. Now,they are also engaged in sorting their lives and playing with their  careers
but still some of them like and post on instagram which are relatable to them.
I generally make content regarding  fitness and sharing my personal opinion towards
the life I am living in a sarcastic way.
Sometimes I feel that I lost a lot in my life just because of my own pleasure and
# ...
```

### Empty/comment-only final submission

- Cluster frequency: `24/180` (`13.3%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `24/180` (`13.3%`)
- Dominant private-case vectors: `000` x24
- Score distribution (top): `0.0` x24
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `018d12e10e374ebe97a30f0112e0b52d`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output
```

### Row-spacing arithmetic is incorrect (bars/slashes are printed, but the W geometry/spacing is wrong)

- Cluster frequency: `22/180` (`12.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `22/180` (`12.2%`)
- Dominant private-case vectors: `000` x22
- Score distribution (top): `0.0` x22
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `80df44524a174abca411c774ea3b1aaa`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())

for i in range(n):
    # Left side of the pattern
    print("|", end="")

    # Forward slash and space pattern for the first diagonal
    for j in range(i):
        print(" ", end="")
    print("/", end="")

    # Space in between diagonals
    for j in range(2 * (n - i - 1) - 1):
        print(" ", end="")

    # Backslash and space pattern for the second diagonal
    if i < n - 1:
        print("\\", end="")
# ...
```

### Hard-codes small sample sizes (`n=1/2/3/...`) with `if/elif` branches instead of a general pattern loop

- Cluster frequency: `16/180` (`8.9%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `16/180` (`8.9%`)
- Dominant private-case vectors: `000` x16
- Score distribution (top): `0.0` x16
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `6d3d1b01e07b4b01947d39c60df5bdb3`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output


n = int(input())
if n == 1:
    print("|/\|")
elif n == 2:
    print("| /\ |")
    print("|/  \|")
elif n == 3:
    print("|  /\  |")
    print("| /  \ |")
    print("|/    \|")
elif n == 4:
    print("|   /\   |")
    print("|  /  \  |")
    print("| /    \ |")
    print("|/      \|")
# ...
```

### Runtime NameError

- Cluster frequency: `4/180` (`2.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `4/180` (`2.2%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `25076140f9894caea85ee99321c08a06`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = int(input())

right_row = n - 1 - i
left_row = 2 * i
middle_row = "|" + " " * left_spaces + "/" + " " * middle_spaces + "\\" + "" * left_spaces + "|"
print(line)
```

### Hard-codes the public sample sizes (`n=1/2/5`, etc.) instead of generating the W pattern for arbitrary `n`

- Cluster frequency: `4/180` (`2.2%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `4/180` (`2.2%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `371a71c461334a50a0c9263314abc5c8`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output
n = int(input())
if n == 1:
    print("|/\|")
if n == 2:
    print("| /\ |")
    print("|/  \|")
if n == 3:
    print("|  /\  |")
    print("| /  \ |")
    print("|/    \|")
if n == 4:
    print("|   /\   |")
    print("|  /  \  |")
    print("| /    \ |")
    print("|/      \|")
if n == 5:
    print("|    /\    |")
# ...
```

### Uses a grid/nested-loop character plot that prints extra spaces/separators and fails exact row formatting

- Cluster frequency: `2/180` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `2/180` (`1.1%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `f79c296ab84440c29b435b67baddd7b1`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())

for i in range(n):
    for j in range(n):
        if j == 0:
            print("|", end = "")
        else:
            print(" " , end = "")
    for j in range(n):
        if j == i and i != n-1:
            print("/", end = "")
        elif j == n-1-i and i != n-1:
            print("\\" , end = "")
        elif i == n-1 and j == i:
            print("/",end = "")
        elif i == n-1 and j == n-1-i:
            print("\\",end = "")
        else:
# ...
```

### Builds row strings by adding integers to strings (string-multiplication/concatenation arithmetic bug)

- Cluster frequency: `2/180` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `2/180` (`1.1%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `80314f2d6ba54da7bac24b6de5129417`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = int(input())
for i in range(n):
    left = "|" + " " * i
    spaces_between = max(0, 2 * i - 1)
    mid = " " * (2 * (n - 1 - i)) + "/" + " " * spaces_between + (2 * i - 1) + "\\"
    right = " " * (2 * (n - 1 - i) + "|")
    print(left + mid + right)
```

### Prints the same row (`|/\\|`) repeatedly instead of widening the interior spacing each row

- Cluster frequency: `2/180` (`1.1%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `2/180` (`1.1%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `39eb23633fb042c8a4afc1c60a769aec`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = int(input())
for i in range(n):
    print("|" + "/\\" + "|")
```

### Repeats bars/slashes/backslashes `n` times (`'|'*n`, `'/'*n`) instead of printing single boundary/slash characters per row

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `056b57703e4546d8999704d7f01d7357`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = int(input())
for i in range(n):
    print(
        (
            "|" * (n) + " " * (n - 1) + "/" * n + " " * 2 * i + "\\" * n + " " * (n - 1) + "|" * (n)
        ).rstrip()
    )
```

### Center-spacing off-by-two bug (`2*i-2`) breaks the first rows of the W pattern

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `0b013f1120914ba39ea3be673a30a963`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = int(input())
for i in range(n):
    print("|", end="")
    print(" " * (n - i - 1), end="")
    print("/", end="")
    print(" " * (2 * i - 2), end="")
    print("\\", end="")
    print(" " * (n - i - 1), end="")
    print("|")
```

### Submits a helper/function-style return value instead of reading `n` and printing the W pattern rows

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `0bf880516c12486d8fb3f137ec413a4d`, summary `Wrong Answer`, score `0`, vector `000`

```python
if size < 2:
    print("the size should be above 3")
size = 2 * (n - 2)
leading_spaces = 2 * n - 1
centre_spacing = "" * 2 * (n - i - 1)
print("f|{leading_spaces}/{centre_spacing}\\{leading_spaces}|")
return print_w_pattern
```

### Uses loop/size variables (`n`, `w`, etc.) without reading the input size first

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `10584803759840c49a135e6464e508b9`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output
# | /\ |
# |/  \|
for i in range(n):
    str_line = "|" * i
```

### Reuses `n` as the loop variable (`for n in range(...)`), corrupting the intended pattern size

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `1c7611a77674468b818ef1a95c98518c`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output
n = int(input())
for n in range(0, n):
    print("|/\|")
```

### Uses invalid input conversion (`input(int())`) instead of reading the integer with `int(input())`

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `27de57db72234103a6b0213ed264ca53`, summary `Wrong Answer`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

n = input(int())
print(n)
```

### Builds placeholder row arrays (e.g., `['1 ']*...`) instead of constructing exact W rows with `|`, `/`, and `\\`

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `3d384b252ae64c7b8dbb1c721fdd612c`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())

for i in range(n):
    row = ["1 "] * (2 * n)  # total width = 2n
    row[0] = "|"  # Left border
    row[-1] = "|"  # Right border
    row[n - 1 + i] = "//"  # Left diagonal moves left
    row[n - 1 + i] = "/"
```

### Unrelated pasted function/problem solution instead of W-pattern generation

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `4c54d9d33dda498fa3ebc5d2805e557a`, summary `Wrong Answer`, score `0`, vector `000`

```python
def filter_students(data: dict, criteria: str) -> set:
    '''
    Takes a dictionary where keys are student names and values are lists of scores, filters names based on the given criteria
     - "excellent" - average score >= 85.
     - "good" - average score >= 50 and < 85.
     - "all_pass" - all scores >= 50.
     - "balanced" - difference between min and max is <= 10.

    Args:
        scores(dict)  : keys are student names and values are lists of scores

    Returns:
        set: Set of roll numbers matching the criteria
    '''
values=int(input())
if(values>=85):
    print("good")
elif(values>=50 and values<85):
# ...
```

### Infinite loop in pattern generation (e.g., `while` loop that never updates the loop variable)

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `84001511ac004996bfb9a6b47ab85ba9`, summary `Time Limit Exceeded`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

w = int(input())
while w >= 1:
    w1 = "|''*(w-1)/''*(w-1)/"
print("w1")
print(w1)
```

### Hard-codes a specific W output (fixed rows) instead of generating the pattern from the input `n`

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `d0d3a3bef55848f8b13f91cfa4e26ecd`, summary `Wrong Answer`, score `33`, vector `100`

```python
print("|               /\               |")
print("|              /  \              |")
print("|             /    \             |")
print("|            /      \            |")
print("|           /        \           |")
print("|          /          \          |")
print("|         /            \         |")
print("|        /              \        |")
print("|       /                \       |")
print("|      /                  \      |")
print("|     /                    \     |")
print("|    /                      \    |")
print("|   /                        \   |")
print("|  /                          \  |")
print("| /                            \ |")
print("|/                              \|")
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/180` (`0.6%`)
- Variant frequencies:
  - `ns_25t1_py11_1/10`: `0/0` (`0.0%`)
  - `ns_25t1_py_15_exe/13`: `0/0` (`0.0%`)
  - `ns_25t2_py12_1/13`: `1/180` (`0.6%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py12_1/13`, Student ID `fb486158876b40e1a3c52ef986f732c1`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your code here to read the input and print the output

return
```
