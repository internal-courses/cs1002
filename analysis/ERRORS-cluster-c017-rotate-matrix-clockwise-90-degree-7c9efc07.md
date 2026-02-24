# Error Patterns: Cluster C017 (`Rotate Matrix Clockwise 90 degree`)

## Cluster Summary

- Cluster ID: `C017`
- Cluster title: `Rotate Matrix Clockwise 90 degree`
- Cluster file (this file): `analysis/ERRORS-cluster-c017-rotate-matrix-clockwise-90-degree-7c9efc07.md`
- Variants in cluster: `2`
- Total final submitters across variants: `593`
- Total non-full final submissions across variants: `454`
- Canonical variant (by submissions): `ns_25t2_py21_2/22`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py21_1/18`             |              276 |      213 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/22` (canonical) |              317 |      241 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/22.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/18.json`

## Cluster-Level Outcome Summary

- Final submitters: `593`
- Full pass: `139`
- Non-full final submissions: `454`
- Parseable non-full (logic/runtime focus): `374`
- Non-parseable non-full: `80`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py21_1/18` |              276 |        63 |      213 |                172 |                     41 |
| `ns_25t2_py21_2/22` |              317 |        76 |      241 |                202 |                     39 |

## Private Case Structure

- Private case 1: rectangular-matrix rotation case (catches square-only indexing / row-count confusion)
- Private case 2: another non-square rotation case with negatives/varied values (input parsing + index-order robustness)
- Private case 3: additional rotation case emphasizing exact output formatting expectations
- Private case 4: private case group 4

Private-case vectors in this report are 4-character pass/fail strings over the private case groups (e.g., `1001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                                     | Cluster count | % of cluster non-full | `ns_25t2_py21_1/18` | `ns_25t2_py21_2/22` |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Residual promoted: hard-coded/fixed-size sample-matrix output instead of general `m x n` rotation                                           |           103 |                 22.7% |                  48 |                  55 |
| Likely correct rotation logic, but prints rows with `print(*row)` (evaluator appears to expect different spacing/trailing-space formatting) |            86 |                 18.9% |                  38 |                  48 |
| Syntax / non-parseable final submission                                                                                                     |            80 |                 17.6% |                  41 |                  39 |
| Runtime ValueError from parsing matrix dimensions/elements with the wrong input format                                                      |            36 |                  7.9% |                  18 |                  18 |
| Empty final submission                                                                                                                      |            33 |                  7.3% |                  14 |                  19 |
| Other wrong-answer logic pattern (residual)                                                                                                 |            21 |                  4.6% |                  11 |                  10 |
| Runtime IndexError from square-matrix assumptions or swapped row/column indexing on rectangular matrices                                    |            21 |                  4.6% |                   9 |                  12 |
| Runtime NameError from undefined matrix/dimension variables (`m`, `n`, `a`, etc.)                                                           |            16 |                  3.5% |                   8 |                   8 |
| Implements a function-only solution (or helper) without producing the required printed output                                               |            10 |                  2.2% |                   5 |                   5 |
| Runtime TypeError from treating dimensions/data as the wrong type while building/rotating the matrix                                        |            10 |                  2.2% |                   8 |                   2 |
| Runtime error (parseable final submission)                                                                                                  |             9 |                  2.0% |                   2 |                   7 |
| Runtime EOFError from fixed-size input assumptions (e.g., hard-coded 3x3 reads) or wrong input format parsing                               |             8 |                  1.8% |                   4 |                   4 |
| Hard-codes the public sample rotated matrix output instead of rotating arbitrary input matrices                                             |             8 |                  1.8% |                   1 |                   7 |
| Runtime AttributeError from list/string API misuse while reading or rotating the matrix                                                     |             4 |                  0.9% |                   2 |                   2 |
| Adds debug prints (`print(order)` / dimension prints), causing output-format mismatch                                                       |             2 |                  0.4% |                   0 |                   2 |
| Not able to run                                                                                                                             |             2 |                  0.4% |                   1 |                   1 |
| Hard-codes sample rotated-matrix lines instead of computing the rotation from input                                                         |             2 |                  0.4% |                   1 |                   1 |
| Runtime KeyError                                                                                                                            |             1 |                  0.2% |                   0 |                   1 |
| Assumes a fixed-size sample matrix (e.g., hard-coded 3x3 input) instead of handling general `m x n` matrices                                |             1 |                  0.2% |                   1 |                   0 |
| Returns a rotated matrix from a helper function but does not print it (I/O question requires explicit output)                               |             1 |                  0.2% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `21/454` (`4.6%`)

### Residual promoted: hard-coded/fixed-size sample-matrix output instead of general `m x n` rotation

- Cluster frequency: `103/454` (`22.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `48/213` (`22.5%`)
  - `ns_25t2_py21_2/22`: `55/241` (`22.8%`)
- Dominant private-case vectors: `0000` x103
- Score distribution (top): `0.0` x102, `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `752792aa9bf54b308e48a5b3cdc982db`, summary `Wrong Answer`, score `0`, vector `0000`

```python
a = input().split(" ")
arr = []
for _ in range(int(a[0])):
    arr.append(input())
arr = arr[::-1]
qwer = ""
for i in range(len(arr)):
    for j in range(len(arr[i])):
        if j % 2 == 0:
            qwer = qwer + arr[i][j]
asd = ""
zxc = ""
mnb = ""
fgh = ""
for i in range(len(qwer)):
    if i % int(a[1]) == 0:
        if asd != "":
            asd = asd + " " + qwer[i]
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `784db00abffd4a6b9bd6de8febb9409c`, summary `Wrong Answer`, score `0`, vector `0000`

```python
size = input()
size_int = list(map(int, list(size.split(' '))))
m = size_int[0]
n = size_int[1]
matrix = []
rotated_matrix = []
for i in range(n):
    rotated_matrix.append([])
for i in range(m):
    row = input()
    row_lst = row.split(' ')
    matrix.append(row_lst)
for i in range(n):
    for j in range(m):
        rotated_matrix[i].insert(0, matrix[j][i])

for i in range(len(rotated_matrix)):
    for j in range(len(rotated_matrix[i])):
# ...
```

### Likely correct rotation logic, but prints rows with `print(*row)` (evaluator appears to expect different spacing/trailing-space formatting)

- Cluster frequency: `86/454` (`18.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `38/213` (`17.8%`)
  - `ns_25t2_py21_2/22`: `48/241` (`19.9%`)
- Dominant private-case vectors: `0000` x86
- Score distribution (top): `0.0` x86
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `76d58a6358a448cc9a0c6d0ee8f377a7`, summary `Wrong Answer`, score `0`, vector `0000`

```python
m,n = map(int, input().split())
matrix = [list(map(int, input().split())) for _ in range(m)]
rotated_matrix = zip(*matrix[::-1])
for row in rotated_matrix:
    print(*row)


'''
MY CODE IS CORRECT BUT IN SECTION-2 QS-2 HAVE BUG ,
MY CODE OUTPUT AS EXPECTED IN ALL THREE TEST CASES BUT IT SILL NOT PASS
AND I ALSO TRIED OTHER CODE BUT SAME BUG !!


I TAKE ALL SCREEE-SHOT WITH THE PERMISSION OF INSTRUCTOR
AND IF THIS BUG IS NOT SOLVED THEN I WILL MAIL TO IITM WITH PROOF !!

MY DETAILS :
Username: SHRESTH KASERA
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `1250d50bbd384f0da4b2a2ae2313142b`, summary `Wrong Answer`, score `0`, vector `0000`

```python
# # def rotate_matrix(matrix,m,n):
# #     rotated=[]
# #     for col in range(n):
# #         new_row=[]
# #         for row in range(m-1,-1,-1):
# #             new_row.append(matrix[row][col])
# #         rotated.append(new_row)
# #     return rotated

# m,n=map(int,input().split())
# matrix=[list(map(int,input().split())) for _ in range(m)]

# transpose=[[matrix[r][c] for r in range(m)] for c in range(n)]

# for row in transpose:
#     row.reverse()

# for row in transpose:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `80/454` (`17.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `41/213` (`19.2%`)
  - `ns_25t2_py21_2/22`: `39/241` (`16.2%`)
- Dominant private-case vectors: `0000` x80
- Score distribution (top): `0.0` x80
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `116d112cb9ab47dfb79fa8cc77752330`, summary `Runtime Error`, score `0`, vector `0000`

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

- Variant `ns_25t2_py21_2/22`, Student ID `76d78eedef7d4c6ebd8989c4e981fdc9`, summary `Runtime Error`, score `0`, vector `0000`

```python
def rotate_matrix_clockwise(matrix):
    if not matrix:
        return[]
    m = len(matrix)
    n = len(matrix[0])

    transposed_matrix = [[0] for m in range(n)]
    for i in range(m):
        for j in range(n):
            transposed_matrix[j][i] = matrix[i][j]

    rotated_matrix = [row[::-1] for row in transposed_matrix]

    return rotated_matrix

    original_matrix = []

def main():
# ...
```

### Runtime ValueError from parsing matrix dimensions/elements with the wrong input format

- Cluster frequency: `36/454` (`7.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `18/213` (`8.5%`)
  - `ns_25t2_py21_2/22`: `18/241` (`7.5%`)
- Dominant private-case vectors: `0000` x36
- Score distribution (top): `0.0` x36
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `4f48bdf894fc455291000ac4c07c34ea`, summary `Runtime Error`, score `0`, vector `0000`

```python
m, n = str(input()).split()

M = []
for i in range(int(m)):
    row = []
    for j in range(int(n)):
        x, y, z = str(input()).split()
        row.append(int(x))
        row.append(int(y))
        row.append(int(z))
    M.append(row)
R = []
for i in range(int(n)):
    row = []
    for j in range(int(m)):
        R[i][j] = M[m - j - 1][i]
        row.append(R[i][j])
    R.append(row)
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `d7c2a7d1d3d14616b921bd1f494035c5`, summary `Runtime Error`, score `0`, vector `0000`

```python
m = int(input())
n = int(input())
print("m,n, end=''")
# to rotate a matrix to 90 degrees we have to change the positions of its digits.
# a31 will be a11, a21 will be a12, a11 will be a 13 and so on.

print('pos"a31" at "a11"')
print('pos"a21" at "a12"')
print('pos"a11" at "a13"')
print('pos"a32" at "a21"')
print('pos "a22" at "a22"')
print('pos "a12" at "a23"')
print('pos "a33" at "a31"')
print('pos "a23" at "a32"')
print('pos "a13" at "a33"')
```

### Empty final submission

- Cluster frequency: `33/454` (`7.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `14/213` (`6.6%`)
  - `ns_25t2_py21_2/22`: `19/241` (`7.9%`)
- Dominant private-case vectors: `0000` x33
- Score distribution (top): `0.0` x33
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `117ecf9bb7804b1b9fb5f84311eeb917`, summary `Wrong Answer`, score `0`, vector `0000`

```python
```

- Variant `ns_25t2_py21_2/22`, Student ID `224f568bdc8140bd9ac55e1c97146e79`, summary `Wrong Answer`, score `0`, vector `0000`

```python
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `21/454` (`4.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `11/213` (`5.2%`)
  - `ns_25t2_py21_2/22`: `10/241` (`4.1%`)
- Dominant private-case vectors: `0000` x18, `0100` x2, `0010` x1
- Score distribution (top): `0.0` x18, `25.0` x2, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `10c07f92045949e5b4c57eb63126ec61`, summary `Wrong Answer`, score `50`, vector `0100`

```python
l = list()
matrix_list = list()
matrix_str_list = list()
rmatrx = list()
line = input()
s1,s2=line.split(" ")
n = int(s1)
m = int(s2)
#print(n,m)
for i in range(n):
    il = input()
    matrix_str_list.append(il)
for item in matrix_str_list:
    ll = list(map(int,list(item.split(" "))))
    matrix_list.append(ll)
rmatrx = matrix_list[::-1]
lt = list()
for i in range(len(rmatrx)):
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `15673188f9e1405eb03f1c85350b0795`, summary `Wrong Answer`, score `0`, vector `0000`

```python
'''M,N=map(int, input().split() )
matrix=[]
for _ in range(M):
    matrix.append(list(map(int, input().split())))
rotated=[]
for c in range(N):
    new_row=[]
    for r in range(M-1, -1, -1):
        new_row.append(matrix[r] [c])'''
'''m,n = map(int, input().split())
matrix=[]
#print(f"enter {m} rows with {n} elements each:")
for _ in range(m):
    row = list(map(int, input().split()))
    matrix.append(row)
rotated_matrix = []
for j in range(n):
    new_row = []
# ...
```

### Runtime IndexError from square-matrix assumptions or swapped row/column indexing on rectangular matrices

- Cluster frequency: `21/454` (`4.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `9/213` (`4.2%`)
  - `ns_25t2_py21_2/22`: `12/241` (`5.0%`)
- Dominant private-case vectors: `0000` x17, `0100` x4
- Score distribution (top): `0.0` x17, `25.0` x3, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `cfc5cc937b0f4ae9b12ee229634f2a4d`, summary `Runtime Error`, score `0`, vector `0000`

```python
a,b= input().split(' ')
m,n=int(a),int(b)
l=[]
mat=[]
for i in range(m):
    if n==2:
        c,d= input().split(' ')
        mat.append([int(c),int(d)])
    if n==3:
        c,d,e=input().split(' ')
        mat.append([int(c),int(d),int(e)])
mati=mat.copy()

for i in range(m):
    for j in range(n):
        if j==1:
            mati[i][j]= mat[j][i]
        elif j==0:
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `c6121db846024850ac5bd52aab0ee0a9`, summary `Runtime Error`, score `0`, vector `0000`

```python
# In this program we'll convert matrices to 90 degrees,
# which is basically taking transpose of the matrix
# and then interchanging the first and last columns
import numpy as np

orde = input()
order = orde.split(" ")

i = 0
matrix = []
while i < int(order[0]):
    row = input()
    rowl = row.split(" ")
    # rowl.reverse()
    matrix.append(rowl)
    # matrix.reverse()
    i += 1


# ...
```

### Runtime NameError from undefined matrix/dimension variables (`m`, `n`, `a`, etc.)

- Cluster frequency: `16/454` (`3.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `8/213` (`3.8%`)
  - `ns_25t2_py21_2/22`: `8/241` (`3.3%`)
- Dominant private-case vectors: `0000` x15, `0100` x1
- Score distribution (top): `0.0` x15, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `8410b925e86f4ceb9d5f49bd09b8fea5`, summary `Runtime Error`, score `50`, vector `0100`

```python
n = input()
m=int(n[2])
n=int(n[0])
if(n>=m):
    temp = n-m
    mat = []
    for i in range(n):
        t = input()
        t = t.split()
        mat.append([int(a) for a in t])
        for j in range(temp):
            mat[i].append(0)

    for i in range(n):
        for j in range(i):
            mat[i][j],mat[j][i] = mat[j][i],mat[i][j]

    for i in range(n):
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `2d6a399f03ad4ffb93b8bd766502ce42`, summary `Runtime Error`, score `0`, vector `0000`

```python
x,y=map(int,input().split())
if x==3:
    l=input()
    m=input()
    n=input()
elif x==2:
    l=input()
    m=input()
u=[]
if y==3:
    t=2
elif y==2:
    t=1
for i in range(y+t):
    for j in range(x+1):
        if x==3:
           r=n[i]+' '+m[i]+' '+l[i]
        elif x==2:
# ...
```

### Implements a function-only solution (or helper) without producing the required printed output

- Cluster frequency: `10/454` (`2.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `5/213` (`2.3%`)
  - `ns_25t2_py21_2/22`: `5/241` (`2.1%`)
- Dominant private-case vectors: `0000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `29fabe2017354e42896d76d503bbb88d`, summary `Wrong Answer`, score `0`, vector `0000`

```python
if not matrix or not matrix[0]:
    return []
rows = len(matrix)
column = len(matrix[0])
rotated_matrix = [[0 for _ in range(rows)] for _ in range(column)]
for i in range(rows):
    for j in range(column):
        rotated_matrix[j][rows - 1 - i] = mat[i][j]
return rotated_matrix
```

- Variant `ns_25t2_py21_2/22`, Student ID `1535d22d1cb147ebbdf929be44d7ca75`, summary `Wrong Answer`, score `0`, vector `0000`

```python
if not matrix:
    return []
rows = len(matrix)
cols = len(matrix[0])
rorated_matrix = [[0 for _ in range(rows)] for _ in range(cols)]
for i in range(rows):
    for j in rows(cols):
        rotate_matrix[j][rows - 1 - i] = matrix[i][j]
    return rotated_matrix
return rotate_matrix_cloclwise(rotated_matrix(matrix))
```

### Runtime TypeError from treating dimensions/data as the wrong type while building/rotating the matrix

- Cluster frequency: `10/454` (`2.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `8/213` (`3.8%`)
  - `ns_25t2_py21_2/22`: `2/241` (`0.8%`)
- Dominant private-case vectors: `0000` x10
- Score distribution (top): `0.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `c5860bb5bf784caca9dece6dedbf6c66`, summary `Runtime Error`, score `0`, vector `0000`

```python
num = input().split()

m = int(num[0])
n = int(num[1])
matrix = []
reversed_mat = []
word = []

for i in range(m):
    rows = input().split()
    matrix.append(rows)

matrix = matrix[::-1]

for i in range(n):
    for j in range(m):
        x = matrix[j]
        y = x[i]
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `ae46d18eb74e4a7fa14ade7c82ce2009`, summary `Runtime Error`, score `0`, vector `0000`

```python
rotated_matrix = [[0] * m for i in range(n)]
for i in range(m):
    for j in range(n - 1, -1, -1):
        rotated_matrix[i][j] = m[i][n - 1 - j]
return rotated_matrix
```

### Runtime error (parseable final submission)

- Cluster frequency: `9/454` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `2/213` (`0.9%`)
  - `ns_25t2_py21_2/22`: `7/241` (`2.9%`)
- Dominant private-case vectors: `0000` x9
- Score distribution (top): `0.0` x9
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `8512d5e49f034370b62ed3054a73bc13`, summary `Runtime Error`, score `0`, vector `0000`

```python
n = int(input())
m = int(input())
for i in range(0, n):
    for j in range(0, m):
        a[i, j] = input()
for j in range(0, n):
    for i in range(0, m):
        b[j, i] = a[i, j]
result = b[n, m]
return result
```

- Variant `ns_25t2_py21_2/22`, Student ID `b0602c705d4d4150a3bacec5f72fd3f5`, summary `Runtime Error`, score `0`, vector `0000`

```python
m, n = len(matrix), len(matrix[0])
rotated = [[0] * m for _ in range(n)]
for i in range(m):
    for j in range(n):
        rotated[j][m - 1 - i] = matrix[i][j]
return rotated
```

### Runtime EOFError from fixed-size input assumptions (e.g., hard-coded 3x3 reads) or wrong input format parsing

- Cluster frequency: `8/454` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `4/213` (`1.9%`)
  - `ns_25t2_py21_2/22`: `4/241` (`1.7%`)
- Dominant private-case vectors: `0000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `1bd13e9ff636464b9f83a0f69c0f6fa3`, summary `Runtime Error`, score `0`, vector `0000`

```python
size = input()
matrix1 = input()
matrix2 = input()
matrix3 = input()
length_of_each, total_lists = size.split()
length_of_each, total_lists = int(length_of_each), int(total_lists)
print(matrix3[0], matrix2[0], matrix1[0] + " ")
print(matrix3[2], matrix2[2], matrix1[2] + " ")
print(matrix3[4], matrix2[4], matrix1[4] + " ")
```

- Variant `ns_25t2_py21_2/22`, Student ID `6d3d1b01e07b4b01947d39c60df5bdb3`, summary `Runtime Error`, score `0`, vector `0000`

```python
nm=input()
l=nm.split()

new=""
for i in range(int(l[0])):
    for j in range(int(l[1])):
        mat=input()
        r_split=mat.split()
        print(r_split[i]+new)

#    for j in range(int(l[1])):
#        mat=input()



'''
col=int(input())
for i in range (row):
# ...
```

### Hard-codes the public sample rotated matrix output instead of rotating arbitrary input matrices

- Cluster frequency: `8/454` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `1/213` (`0.5%`)
  - `ns_25t2_py21_2/22`: `7/241` (`2.9%`)
- Dominant private-case vectors: `0000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `997950a3c2f648b99fb96fa09570725a`, summary `Wrong Answer`, score `0`, vector `0000`

```python
print(7, 4, 1)
print(8, 5, 2)
print(9, 6, 3)
```

- Variant `ns_25t2_py21_2/22`, Student ID `84cadb6a693241bf89a658609b9f7229`, summary `Wrong Answer`, score `0`, vector `0000`

```python
in_put = input().split()
m,n = int(in_put[0]),int(in_put[1])

matrix = []
for _ in range(m):
    row = input().split()
    row = [int(__) for __ in row]
    matrix.append(row)

new_matrix = []
for j in range(n):
    new_row = []
    for i in range(m):
        new_elem = matrix[m-1-i][j]
        new_row.append(new_elem)
    new_matrix.append(new_row)

for i in range(len(new_matrix)):
# ...
```

### Runtime AttributeError from list/string API misuse while reading or rotating the matrix

- Cluster frequency: `4/454` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `2/213` (`0.9%`)
  - `ns_25t2_py21_2/22`: `2/241` (`0.8%`)
- Dominant private-case vectors: `0000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `ccd7ec367e81430b8d02a57b08082f12`, summary `Runtime Error`, score `0`, vector `0000`

```python
m, n = map(int, input().split())
matrix = []
for i in range(m):
    row = list(map(int, input.split()))
    matrix.append(row)
rotated = []
for j in range(n):
    new_row = []
    for i in range(m - 1, -1, -1):
        new_row.append(matrix[i][j])
    rotated.append(new_row)
for row in rotated:
    for val in rotated:
        print(val, row)
```

- Variant `ns_25t2_py21_2/22`, Student ID `c8472f5d0cb44df3b2ed8d33f0cd5cbe`, summary `Runtime Error`, score `0`, vector `0000`

```python
m, n = map(input.split())

matrix = []
print("Enter matrix elements")
for _ in range(m):
    row = list(map(int, input().split()))
    matrix.append(row)
rotated = [[0] * m for _ in range(n)]
for i in range(m):
    for j in range(n):
        rotated[j][m - 1 - i] = matrix[i][j]
for tow in rotated:
    print(*row)
```

### Adds debug prints (`print(order)` / dimension prints), causing output-format mismatch

- Cluster frequency: `2/454` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `0/213` (`0.0%`)
  - `ns_25t2_py21_2/22`: `2/241` (`0.8%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/22`, Student ID `d3d8e14efc344d5ba5b136ef97552739`, summary `Wrong Answer`, score `0`, vector `0000`

```python
line = []
result = []
m, n = map(int, (input().split()))
# print(m,n)
# print(type(m),type(n))
for row in range(m):
    line.append([input().strip()])
print(line)
result = line[::-1]
print(result)
for i in range(m - 1):
    result.append(result[i][0])
print(result)


# for i in line:
#   print(line)
```

### Not able to run

- Cluster frequency: `2/454` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `1/213` (`0.5%`)
  - `ns_25t2_py21_2/22`: `1/241` (`0.4%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `c7c0672e66204c2a96b5660b708f3025`, summary `Not able to run`, score `0`, vector `0000`

```python
m, n = map(int, input().split())

# Step 2: Read the matrix
matrix = []
for _ in range(m):
    row = list(map(int, input().split()))
    matrix.append(row)

# Step 3: Rotate matrix 90° clockwise
rotated = []
for col in range(n):
    new_row = []
    for row in range(m - 1, -1, -1):  # take from bottom to top
        new_row.append(matrix[row][col])
    rotated.append(new_row)

# Step 4: Print rotated matrix
for row in rotated:
# ...
```

- Variant `ns_25t2_py21_2/22`, Student ID `7a213b2882464ba680ddbbcf140e9041`, summary `Not able to run`, score `0`, vector `0000`

```python
if not matrix or not matrix[0]:
    return []
rows, cols = len(matrix), len(matrix[0])
rotated = [[0] * rows for _ in range(cols)]
for i in range(rows):
    for j in range(cols):
        rotated[j][rows - 1 - i] = matrix[i][j]
return rotated
```

### Hard-codes sample rotated-matrix lines instead of computing the rotation from input

- Cluster frequency: `2/454` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `1/213` (`0.5%`)
  - `ns_25t2_py21_2/22`: `1/241` (`0.4%`)
- Dominant private-case vectors: `0000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `a01d72884f4e43fc9c7519ec8abddf17`, summary `Wrong Answer`, score `0`, vector `0000`

```python
print("5 3 1")
print("6 4 2")
```

- Variant `ns_25t2_py21_2/22`, Student ID `8050e0f59a44408eb909701d7cdde1a6`, summary `Wrong Answer`, score `0`, vector `0000`

```python
print("5 3 1\n6 4 2")
```

### Runtime KeyError

- Cluster frequency: `1/454` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `0/213` (`0.0%`)
  - `ns_25t2_py21_2/22`: `1/241` (`0.4%`)
- Dominant private-case vectors: `0000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Dictionary lookup on uninitialized/unexpected key.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/22`, Student ID `3d07f55e5b1846b6b7b9f22c4fa656e3`, summary `Runtime Error`, score `0`, vector `0000`

```python
rc = input()
m = int(rc.split()[0])
n = int(rc.split()[-1])
matrix = []
for i in range(m):
    matrix.append(input().split())
n_m = matrix
mdict = {0: [], 1: [], 2: []}
for i in matrix[::-1]:
    for j in range(m):
        mdict[j].append(i[j])
for key in mdict:
    print(" ".join(mdict[key]))
```

### Assumes a fixed-size sample matrix (e.g., hard-coded 3x3 input) instead of handling general `m x n` matrices

- Cluster frequency: `1/454` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `1/213` (`0.5%`)
  - `ns_25t2_py21_2/22`: `0/241` (`0.0%`)
- Dominant private-case vectors: `0000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `0ad1c427973645aba18902d9ebab84a5`, summary `Wrong Answer`, score `0`, vector `0000`

```python
m , n = map(int , input().split())
mat = []
for i in range(m):
    l = list(map(int , input().split()))
    mat.append(l)
m1 = []
for i in range(n):
    l1 = []
    for j in range(m):
        l1.append(0)
    m1.append(l1)
for i in range(n):
    for j in range(m):
        m1[i][j] = mat[j][i]
a = []
for i in m1:
    a.append(i[::-1])
for i in range(len(a)):
# ...
```

### Returns a rotated matrix from a helper function but does not print it (I/O question requires explicit output)

- Cluster frequency: `1/454` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/18`: `1/213` (`0.5%`)
  - `ns_25t2_py21_2/22`: `0/241` (`0.0%`)
- Dominant private-case vectors: `0000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/18`, Student ID `25eefece568d403baeebe051f2f00e1b`, summary `Wrong Answer`, score `0`, vector `0000`

```python
return [list(row) for row in zip(*matrix)[::-1]]
```
