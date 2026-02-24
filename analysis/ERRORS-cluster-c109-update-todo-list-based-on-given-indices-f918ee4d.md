# Error Patterns: Cluster C109 (`Update Todo List Based on Given Indices`)

## Cluster Summary

- Cluster ID: `C109`
- Cluster title: `Update Todo List Based on Given Indices`
- Cluster file (this file): `analysis/ERRORS-cluster-c109-update-todo-list-based-on-given-indices-f918ee4d.md`
- Variants in cluster: `1`
- Total final submitters across variants: `362`
- Total non-full final submissions across variants: `248`
- Canonical variant (by submissions): `ns_25t2_py13_1/10`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py13_1/10` (canonical) |              362 |      248 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `362`
- Full pass: `114`
- Non-full final submissions: `248`
- Parseable non-full (logic/runtime focus): `201`
- Non-parseable non-full: `47`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py13_1/10` |              362 |       114 |      248 |                201 |                     47 |

## Private Case Structure

- Private case 1: baseline todo updates with out-of-range indices mixed in (must ignore invalid indices while updating valid ones)
- Private case 2: multi-digit indices and repeated indices (catches substring/character parsing like `'1' in '10 12'`)
- Private case 3: extra trailing todo lines beyond the first input `n` (must process only `n` lines, not all remaining stdin)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                               | Cluster count | % of cluster non-full | `ns_25t2_py13_1/10` |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: |
| Incorrect todo-list update logic (index parsing, checkbox replacement, or item-loop handling is broadly wrong)                        |            61 |                 24.6% |                  61 |
| Syntax / non-parseable final submission                                                                                               |            47 |                 19.0% |                  47 |
| Empty/comment-only final submission                                                                                                   |            27 |                 10.9% |                  27 |
| Runtime ValueError while parsing the completed-index line (variable-length index list handling bug)                                   |            20 |                  8.1% |                  20 |
| Parses indices as raw text/characters and uses substring membership, so multi-digit hidden indices are misread                        |            12 |                  4.8% |                  12 |
| Runtime NameError from undefined variables in todo-list update logic                                                                  |            11 |                  4.4% |                  11 |
| Runtime TypeError from string/list API misuse while updating todo rows                                                                |            10 |                  4.0% |                  10 |
| Runtime IndexError from using out-of-range completed indices (hidden cases require ignoring invalid indices)                          |             9 |                  3.6% |                   9 |
| Parses completed indices character-by-character / fixed positions, so multi-digit indices are split incorrectly                       |             8 |                  3.2% |                   8 |
| Prints hard-coded public sample todo output instead of updating the provided input list                                               |             8 |                  3.2% |                   8 |
| Checks index membership with substring search (`if str(i) in indices_line`), so `1` matches `10`/`12`                                 |             8 |                  3.2% |                   8 |
| Runtime error (parseable final submission)                                                                                            |             7 |                  2.8% |                   7 |
| Assumes exactly two completed indices (`a, b = map(int, input().split())`), so variable-length index lists crash                      |             4 |                  1.6% |                   4 |
| Defines a helper and returns updated todos but never prints the required line-by-line output                                          |             3 |                  1.2% |                   3 |
| Reads until EOF / blank line instead of processing exactly the first `n` todo items                                                   |             3 |                  1.2% |                   3 |
| Runtime AttributeError from invalid string/list APIs (e.g., `.range`, wrong `.replace` usage)                                         |             2 |                  0.8% |                   2 |
| Generates `Task {i}` labels instead of using the actual todo item text from input                                                     |             2 |                  0.8% |                   2 |
| Parses the index line as a single integer / fixed character slices, causing crashes on spaced or multi-digit indices                  |             1 |                  0.4% |                   1 |
| Near-correct todo update logic, but output formatting/checkbox mutation is wrong (commonly space-replacement instead of `[ ] -> [x]`) |             1 |                  0.4% |                   1 |
| Reverses checkbox replacement (turns `[x]` into `[]`) instead of marking `[ ]` as completed                                           |             1 |                  0.4% |                   1 |
| Reads all remaining stdin lines as todo items instead of processing only the first `n` items (fails extra-line hidden case)           |             1 |                  0.4% |                   1 |
| Off-by-one loop over todo items (`range(n+1)`) reads/prints one extra line                                                            |             1 |                  0.4% |                   1 |
| Prints inside a nested `for item` / `for index` loop, causing duplicate/missing output lines                                          |             1 |                  0.4% |                   1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/248` (`0.0%`)

### Incorrect todo-list update logic (index parsing, checkbox replacement, or item-loop handling is broadly wrong)

- Cluster frequency: `61/248` (`24.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `61/248` (`24.6%`)
- Dominant private-case vectors: `000` x61
- Score distribution (top): `0.0` x61
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `523212fb43d34083ab49e8a09c81f2de`, summary `Wrong Answer`, score `0`, vector `000`

```python
lines = input_text.strip().splitlines()
if not lines:
    return ""
indices = {int(i.strip()) for i in lines[0].split(",") if i.strip().isdigit()}
output = [lines[0]]
task_line_index = 0
for line in lines[1:]:
    stripped = line.lstrip()
    if stripped.startwith("- [ ]"):
        task_line_index += 1
        prefix = line[: len(line) - len(stripped)]
        if task_line_index in indices:
            output.append(f"{prices}- [x]{strripped[5:]}")
        else:
            output.append(line)
    else:
        output.append(line)
return "\n".join(output)
```

### Syntax / non-parseable final submission

- Cluster frequency: `47/248` (`19.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `47/248` (`19.0%`)
- Dominant private-case vectors: `000` x47
- Score distribution (top): `0.0` x47
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `adaf37b10b9948609d93e5ea3e1c7e15`, summary `Not able to run`, score `0`, vector `000`

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
# ...
```

### Empty/comment-only final submission

- Cluster frequency: `27/248` (`10.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `27/248` (`10.9%`)
- Dominant private-case vectors: `000` x27
- Score distribution (top): `0.0` x27
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `05037d9569a945b8b2d5a1b7330c6d62`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your code here.
```

### Runtime ValueError while parsing the completed-index line (variable-length index list handling bug)

- Cluster frequency: `20/248` (`8.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `20/248` (`8.1%`)
- Dominant private-case vectors: `000` x19, `101` x1
- Score distribution (top): `0.0` x19, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `d9139631243c4abe9ed3716dbc15d953`, summary `Runtime Error`, score `0`, vector `000`

```python
    n = int(input())
    data = input()
    val1, val2 = data.split(' ')
    a1 = int(val1)
    a2 = int(val2)
    for i in range(n):
        #value = input()

        #value = value.remove('-')
        #str = '- ' + '['

        if (i == a1) or (i == a2):
            str += 'x'
        else:
            str += ' '
        str += '] Task '

        if i == 0:
# ...
```

### Parses indices as raw text/characters and uses substring membership, so multi-digit hidden indices are misread

- Cluster frequency: `12/248` (`4.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `12/248` (`4.8%`)
- Dominant private-case vectors: `101` x12
- Score distribution (top): `75.0` x7, `50.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `76b14b9137fa4d5098f92ddef73ff1d9`, summary `Wrong Answer`, score `75`, vector `101`

```python
li = ["","","","","","","","","","","","","","","","","","","",""]
number = [100,100,-100,100,100,100,100,100,100,100]
t = 0
temp = 0
pr = ""
stop = 0
n = int(input())
s = input()
for i in range(n):
    li[i] = input()
for ch in s:
    if ch != " " :
        number[t] = int(ch)
        t += 1
for i in range(n):
    if i in number:
        for j in li[i]:
            if j != "]" and stop == 0:
# ...
```

### Runtime NameError from undefined variables in todo-list update logic

- Cluster frequency: `11/248` (`4.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `11/248` (`4.4%`)
- Dominant private-case vectors: `000` x10, `101` x1
- Score distribution (top): `0.0` x10, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `f7747d665d754450bbd1816fcd2f8ea5`, summary `Runtime Error`, score `50`, vector `101`

```python
# write your code here.
todo_list=[]
a = int(input())
b= list(input().split())
if a==3:
    str1=input()
    str2=input()
    str3=input()
    string=[str1,str2,str3]
if a==4:
    str1=input()
    str2=input()
    str3=input()
    str4=input()
    string=[str1,str2,str3,str4]

for x in b:
    if int(x)>=a:
# ...
```

### Runtime TypeError from string/list API misuse while updating todo rows

- Cluster frequency: `10/248` (`4.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `10/248` (`4.0%`)
- Dominant private-case vectors: `000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `3389a750605b4d12bf5f26177a0b5fb9`, summary `Runtime Error`, score `0`, vector `000`

```python
# input

n = int(input())
completed_index = input()
to_do = []
for i in range(n):
    list = str(input())
    to_do.append(list)

# updating completed task_name

for char in completed_index:
    index = int(char)
    string = list(to_do[index])
    string[3] = x

# print output
for i in range(len(to_do)):
# ...
```

### Runtime IndexError from using out-of-range completed indices (hidden cases require ignoring invalid indices)

- Cluster frequency: `9/248` (`3.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `9/248` (`3.6%`)
- Dominant private-case vectors: `001` x5, `000` x4
- Score distribution (top): `25.0` x5, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `5130326ff1f74e9c9e41711de53d2561`, summary `Runtime Error`, score `25`, vector `001`

```python
# write your code here.

n = int(input())
ndx_str = str(input())
ndx = sorted(ndx_str.split(" "), reverse = True)
lst = []
for i in range(n):
    lst.append(input())
for i in range(len(ndx)):
    y = ""
    if int(ndx[i]) <= len(lst):
        x = list(lst[int(ndx[i])])
        x[3:4] = "x"
        for i in range(len(x)):
            y+=x[i]
            for i in range(len(ndx)):
                lst[int(ndx[i])] = y
for i in range(len(lst)):
# ...
```

### Parses completed indices character-by-character / fixed positions, so multi-digit indices are split incorrectly

- Cluster frequency: `8/248` (`3.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `8/248` (`3.2%`)
- Dominant private-case vectors: `100` x3, `101` x2, `001` x2, `000` x1
- Score distribution (top): `25.0` x5, `75.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `076533440ea64c5e94b06abafb0f8545`, summary `Wrong Answer`, score `25`, vector `100`

```python
# write your code here.

n=int(input(""))
s=input()
l=[]
l2=s.split(" ")
try:
    for i in range(n):
        s1=input()
        l=l+[s1]
    for i in range(n):
        if int(l2[0])==i:
            b=l[i]
            l3=b.split("[")
            print(l3[0]+"["+"x"+l3[1].strip(" "))
        elif int(l2[1])==i:
            b=l[i]
            l3=b.split("[")
# ...
```

### Prints hard-coded public sample todo output instead of updating the provided input list

- Cluster frequency: `8/248` (`3.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `8/248` (`3.2%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `b02211e1e90145bfa41981d85efd3c3a`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = [0, 1, 2, 3]
k = [4, 5, 6]
z = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
a = "- [x] Task 1"
b = "- [x] Task 2"
c = "- [ ] Task 3"
d = "- [ ] Task 4"
e = "- [ ] Finish homework"
f = "- [ ] Prepare presentation"
g = "- [x] Submit report"
h = "- [ ] Attend meeting"

if (k == 4 and z, y == 2, 4):
    print(e)
    print(f)
    print(g)
    print(h)
```

### Checks index membership with substring search (`if str(i) in indices_line`), so `1` matches `10`/`12`

- Cluster frequency: `8/248` (`3.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `8/248` (`3.2%`)
- Dominant private-case vectors: `101` x8
- Score distribution (top): `75.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `9094a487eb554821b41f648acb539057`, summary `Wrong Answer`, score `75`, vector `101`

```python
n = int(input())
lst = input()
lst = str(lst)
for i in range(n):
    if str(i) in lst:
        task = input()
        print(task[:3] + "x" + task[4:])
        # print("- [x] Task",i+1)
    else:
        task = input()
        print(task[:3] + " " + task[4:])
```

### Runtime error (parseable final submission)

- Cluster frequency: `7/248` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `7/248` (`2.8%`)
- Dominant private-case vectors: `000` x7
- Score distribution (top): `0.0` x7
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `a705010c8d384fc5a35836c85a78876a`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input)
todo_list = [map(input) for _ in range(n)]

n_completed = int(input)
completed_task = []
remaining_task = []

for s in todo_list:
    if n_completed == s.index():
        completed_task += s
    else:
        remaining_task += s

return completed_task
```

### Assumes exactly two completed indices (`a, b = map(int, input().split())`), so variable-length index lists crash

- Cluster frequency: `4/248` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `4/248` (`1.6%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `180623169e3f44eb93bbffe5b1892884`, summary `Runtime Error`, score `0`, vector `000`

```python
# write your code here.

n = int(input())
a, b = map(int, input().split())
task = list()
for i in range(n):
    c = input()
    task.append(c)
index = 0
for i in task:
    check = i.split()
    output = ""
    if index == a or index == b:
        for k in check:
            if k == "]":
                output = output.rstrip(" ") + "x" + k + " "
            else:
                output += k + " "
# ...
```

### Defines a helper and returns updated todos but never prints the required line-by-line output

- Cluster frequency: `3/248` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `3/248` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `5facc27e0c754129abbac1c610613d9e`, summary `Wrong Answer`, score `0`, vector `000`

```python
s1 = ""
l2 = l1.copy()
l3 = []
for i in range(0, len(l1)):
    try:
        x = l2[i].split("[")
        x.insert(1, "[ x")
        for i in x:
            s1 += i
        l3.append(s1)
    except IndexError:
        l3 = l1.copy()
return l3
```

### Reads until EOF / blank line instead of processing exactly the first `n` todo items

- Cluster frequency: `3/248` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `3/248` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `880eadde20ff4a03a476a5d5781db66e`, summary `Runtime Error`, score `0`, vector `000`

```python
n = int(input())

l = []
d = []


for i in range(0, n - 1):
    m = input()
    l.append(m)

for i in range(0, n):
    item = input()
    d.append(item)


# ...
```

### Runtime AttributeError from invalid string/list APIs (e.g., `.range`, wrong `.replace` usage)

- Cluster frequency: `2/248` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `2/248` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `2a626329194c41ebb8d71de367d54180`, summary `Runtime Error`, score `0`, vector `000`

```python
# write your code here.
task = ""
n = int(input())
indices = input()
l = indices.split()

for i in range(n):
    task += input()
    task += "\n"

l1 = task.split()
for i in range(n):
    l1[i].pop(3)
l2 = []
for i in l1:
    for j in range(len(i)):
        if i[j] == "[":
            l2.append(i[j])
# ...
```

### Generates `Task {i}` labels instead of using the actual todo item text from input

- Cluster frequency: `2/248` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `2/248` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `304bd925911248d99744cb5a6b9b5b1c`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your code here.

n = int(input())
index = input().split()
a = "- [ ] Task 1"
b = "- [ ] Task 2"
c = "- [ ] Task 3"
for i in range(1, n):
    if i in index:
        print(f"- [x] Task i")
```

### Parses the index line as a single integer / fixed character slices, causing crashes on spaced or multi-digit indices

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `0be95b2a0ecb411d8f81880b5a1edc67`, summary `Runtime Error`, score `0`, vector `000`

```python
n1 = int(input())

n2 = int(input()).split()

l = []
for i in range(n1):
    x = input(
        "-[]",
    )
    l.append(x)

for i in range(len(l)):
    if n2 == l[i]:
        l.replace("-[]", "-[X]")
        print(l)
```

### Near-correct todo update logic, but output formatting/checkbox mutation is wrong (commonly space-replacement instead of `[ ] -> [x]`)

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `209e1e2f89534881a5b4ddaa8cefcc3c`, summary `Wrong Answer`, score `75`, vector `111`

```python
data01 = int(input())
data02 = input()

done_list = data02.split()
todo = []

for i in range(data01):
    todo.append(input())

for i in done_list:
    if int(i) >= data01:
        continue
    todo[int(i)] = todo[int(i)].replace(" ", "x", 2)
    todo[int(i)] = todo[int(i)].replace("x", " ", 1)
for i in range(data01):
    print(todo[i])
```

### Reverses checkbox replacement (turns `[x]` into `[]`) instead of marking `[ ]` as completed

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `31c2cccb6dbe44fdb893e0e8dd197fef`, summary `Wrong Answer`, score `0`, vector `000`

```python
n = int(input())
try:
    completed_indices = set(map(int, input().split()))
except:
    completed_indices = set()
toods = [input() for _ in range(n)]

for i in range(n):
    line = toods[i]
    if i in completed_indices:
        line = line.replace("[x]", "[]", 1)
        print(line)
```

### Reads all remaining stdin lines as todo items instead of processing only the first `n` items (fails extra-line hidden case)

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `52ec4829bcc74644a5afe67e87e9c600`, summary `Wrong Answer`, score `75`, vector `111`

```python
import sys

lst = sys.stdin.read().strip().split("\n")
n = int(lst[0])
hello = lst[1].split(" ")
taskstodo = lst[2:]
# print(taskstodo)
for i in range(len(taskstodo)):
    if str(i) in hello:
        taskstodo[i] = taskstodo[i].replace(" ", "x", 2)
        taskstodo[i] = taskstodo[i].replace("x", " ", 1)
for i in taskstodo:
    print(i)
```

### Off-by-one loop over todo items (`range(n+1)`) reads/prints one extra line

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `72629bcf67754068b450f6c5054f33a6`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your code here.
n = int(input())
s = list()
tasks = str(input())

for i in range(n + 1):
    if i in s:
        print(f"-[x] {tasks}")

    else:
        print(f"-[ ] {tasks}")
```

### Prints inside a nested `for item` / `for index` loop, causing duplicate/missing output lines

- Cluster frequency: `1/248` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/10`: `1/248` (`0.4%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/10`, Student ID `b63ee13d84e0473a8225d182619bb010`, summary `Wrong Answer`, score `25`, vector `001`

```python
# write your code here.
n = int(input())
comp = input().split(" ")
comp2 = []
tasks = []
for i in range(n):
    task = input()
    tasks.append(task)
for i in comp:
    comp2.append(int(i))
for i in range(0, n):
    for j in comp2:
        if j <= n:
            if i == j:
                x = tasks[i]
                y = x[:3] + "x" + x[4:]
                print(y)
                break
# ...
```
