# Error Patterns: Cluster C107 (`Print Pieces Moved from Chess Notation string.`)

## Cluster Summary

- Cluster ID: `C107`
- Cluster title: `Print Pieces Moved from Chess Notation string.`
- Cluster file (this file): `analysis/ERRORS-cluster-c107-print-pieces-moved-from-chess-notation-string-c8e0c643.md`
- Variants in cluster: `1`
- Total final submitters across variants: `376`
- Total non-full final submissions across variants: `257`
- Canonical variant (by submissions): `ns_25t2_py13_2/10`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_2/10` (canonical) | 376 | 257 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/10.json`

## Cluster-Level Outcome Summary

- Final submitters: `376`
- Full pass: `119`
- Non-full final submissions: `257`
- Parseable non-full (logic/runtime focus): `216`
- Non-parseable non-full: `41`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_2/10` | 376 | 119 | 257 | 216 | 41 |

## Private Case Structure

- Private case 1: long SAN string with move numbers, pawns/pieces, and kingside castling (`O-O`) token handling
- Private case 2: captures/check suffixes (e.g., `Qxe4+`, `Nxc7+`) to catch fragile `len==2` or digit-only pawn heuristics
- Private case 3: includes queenside castling (`O-O-O`) plus captures; catches castling mapping and token filtering bugs

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_2/10` |
| --- | ---: | ---: | ---: |
| Empty/comment-only final submission | 45 | 17.5% | 45 |
| Syntax / non-parseable final submission | 41 | 16.0% | 41 |
| Outputs lowercase piece names (`king`) instead of the required title-case labels (`King`, `Rook`, ...) | 34 | 13.2% | 34 |
| Tokenizes by spaces but does not robustly filter move-number tokens before indexing piece letters | 22 | 8.6% | 22 |
| Incorrect chess-notation token parsing and piece-name emission logic (broad wrong-answer failure) | 21 | 8.2% | 21 |
| Indexes `token[0]` without safely skipping move-number/empty tokens, causing `IndexError` | 19 | 7.4% | 19 |
| Runtime NameError from undefined piece maps/counters in notation parsing logic | 14 | 5.4% | 14 |
| Uses zeroes (`0-0`, `0-0-0`) instead of SAN castling tokens with letter O (`O-O`, `O-O-O`) | 10 | 3.9% | 10 |
| Runtime TypeError from invalid `input()/map()` or dictionary API usage while parsing tokens | 8 | 3.1% | 8 |
| Misclassifies queenside castling (`O-O-O`) as involving `Queen` instead of printing `King` and `Rook` | 7 | 2.7% | 7 |
| Handles castling by printing only `King` and forgets the required second line `Rook` | 6 | 2.3% | 6 |
| Uses square/file-prefix heuristics for specific sample moves (e.g., `startswith('e')`) instead of SAN piece parsing rules | 4 | 1.6% | 4 |
| Runtime IndexError | 4 | 1.6% | 4 |
| Reads multiple separate `input()` values (`move_number`, white move, black move) instead of one notation string line | 4 | 1.6% | 4 |
| Parses only the first move pair (or a fixed number of tokens) instead of scanning the entire notation string | 3 | 1.2% | 3 |
| Mutates the token list while iterating (`remove(...)`), which skips moves and loses output lines | 3 | 1.2% | 3 |
| Uses a brittle move-number state flag / hard-coded `1.`..`10.` list and skips many tokens in longer games | 2 | 0.8% | 2 |
| Prints a fixed piece-name sequence (sample output) instead of parsing the notation string | 2 | 0.8% | 2 |
| Tries to read an integer move count first (`int(input())`) even though input is a single notation string | 2 | 0.8% | 2 |
| Hard-codes public sample move-to-piece outputs instead of parsing arbitrary chess-notation tokens | 1 | 0.4% | 1 |
| Partial SAN token filtering logic: some games pass, but move-number/capture/castling token handling fails on hidden cases | 1 | 0.4% | 1 |
| Hard-codes exact public sample notation strings and corresponding outputs instead of parsing arbitrary games | 1 | 0.4% | 1 |
| Misspells `.startswith(...)` as `.startwith(...)` while decoding piece tokens | 1 | 0.4% | 1 |
| Runtime error (parseable final submission) | 1 | 0.4% | 1 |
| Near-correct token parsing, but castling output formatting/mapping is wrong on hidden cases | 1 | 0.4% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/257` (`0.0%`)

### Empty/comment-only final submission

- Cluster frequency: `45/257` (`17.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `45/257` (`17.5%`)
- Dominant private-case vectors: `000` x45
- Score distribution (top): `0.0` x45
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `0469715305644874a34c4591de87ada1`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here
```

### Syntax / non-parseable final submission

- Cluster frequency: `41/257` (`16.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `41/257` (`16.0%`)
- Dominant private-case vectors: `000` x41
- Score distribution (top): `0.0` x41
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `e22f93eb66374b19905b4035ccb2b47f`, summary `Runtime Error`, score `0`, vector `000`

```python
{move_number} {white_move} {black_move}
str e4,e5,Nf3,Nc6,Bb5,a6,O-O,Qc7
# Method 1
number = input()

mistakes = 0
incorrect_str = {'l': '1', 'o': '0'}
out = ''

for digit in number:
    if digit in incorrect_str:
        mistakes += 1
        digit = incorrect_str[digit]
    out += digit

if mistakes:
    print('No of mistakes:', mistakes)
    print('Corrected number', out)
# ...
```

### Outputs lowercase piece names (`king`) instead of the required title-case labels (`King`, `Rook`, ...)

- Cluster frequency: `34/257` (`13.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `34/257` (`13.2%`)
- Dominant private-case vectors: `000` x26, `100` x5, `101` x2, `011` x1
- Score distribution (top): `0.0` x26, `33.0` x5, `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `2b74e135eee14b9389752ca5a73d399d`, summary `Wrong Answer`, score `33`, vector `100`

```python
alpha='abcdefghijklmnopqrstuvwxyz'
# write your solution here
a=input()
moves=a.split(" ")
for i in range(len(moves)):
    move=moves[i]
    if move.startswith("N"):
        print("Knight")
    elif move.startswith("K"):
        print("King")
    elif move.startswith("Q"):
        print("Queen")
    elif move.startswith("B"):
        print("Bishop")
    elif move.startswith("R"):
        print("Rook")
    elif move.startswith("O-O"):
        print("King")
# ...
```

### Tokenizes by spaces but does not robustly filter move-number tokens before indexing piece letters

- Cluster frequency: `22/257` (`8.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `22/257` (`8.6%`)
- Dominant private-case vectors: `000` x10, `101` x6, `100` x6
- Score distribution (top): `0.0` x10, `67.0` x6, `33.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `1cd73ad8e27246ca8134cf05e9d30b53`, summary `Wrong Answer`, score `67`, vector `101`

```python
# so the string provided is in terms of chess notation
# the input seems to be a single string
# so the strategy seems to first split the string at the '.'
# so then each move decomposes to -> [1, e4, e5 ]
# the next move would be to strip the whitespaces, giving a cleaner list
# then we iterate through the list, ignoring every 3rd index which is the move number
# we can use a dict to store the chess pieces that the respective move starts with

moveSet = input()
moveList = moveSet.split(" ")
newList = []
for index in range(len(moveList)):
    if index == 0 or index % 3 == 0:
        continue
    if moveList[index][0] == "N":
        newList.append("Knight")
    elif moveList[index][0] == "Q":
        newList.append("Queen")
# ...
```

### Incorrect chess-notation token parsing and piece-name emission logic (broad wrong-answer failure)

- Cluster frequency: `21/257` (`8.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `21/257` (`8.2%`)
- Dominant private-case vectors: `000` x21
- Score distribution (top): `0.0` x21
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `f7ca456861874786ae331f934810dfe5`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here
moves="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. O-O Qc7"
result=[]
tokens=moves.split()
for token in tokens:
    if token.endswith('.'):
        continue
    if token in['O-O','0-0']:
        result.append('King')
        result.append("Rook")
    elif token in ['O-O-O','0-0-0']:
        result.append('King')
        result.append("Rook")
    else:
        f=token[0]
        if f=='K':
            result.append('King')
        elif f=='Q':
# ...
```

### Indexes `token[0]` without safely skipping move-number/empty tokens, causing `IndexError`

- Cluster frequency: `19/257` (`7.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `19/257` (`7.4%`)
- Dominant private-case vectors: `100` x11, `000` x5, `101` x2, `110` x1
- Score distribution (top): `33.0` x11, `0.0` x5, `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `9c923bc6ca754215bf512104dbc278b6`, summary `Runtime Error`, score `0`, vector `000`

```python
# write your solution here
n=input()
lst=n.split(" ")
for i in range(0,len(lst),3):
    if(len(lst[i+1])==2):
        print("Pawn")
    if(len(lst[i+1])==3):
        if(lst[i+1][0]=="N"):
            print("Knight")
        elif(lst[i+1][0]=="Q"):
            print("Queen")
        elif(lst[i+1][0]=="R"):
            print("Rook")
        elif(lst[i+1][0]=="B"):
            print("Bishop")
        elif(lst[i+1][0]=="K"):
            print("King")
        elif(lst[i+1]=="O-O"):
# ...
```

### Runtime NameError from undefined piece maps/counters in notation parsing logic

- Cluster frequency: `14/257` (`5.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `14/257` (`5.4%`)
- Dominant private-case vectors: `000` x14
- Score distribution (top): `0.0` x14
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `9292540bb7a0483b89c14d64f4ad50c1`, summary `Runtime Error`, score `0`, vector `000`

```python
# Write your solution here
notation = input().split()

#Define piece symbols
piece_map = {
    'K':"King",
    'Q':"Queen",
    'R':"Rook",
    'B':"Bishop",
    'N':"Knight"
}

for move in notation:
    #Check for castling
        if move in ["O-O","O-O-O"]:
            print("King")
        else:
            #If first letter indicates a piece
# ...
```

### Uses zeroes (`0-0`, `0-0-0`) instead of SAN castling tokens with letter O (`O-O`, `O-O-O`)

- Cluster frequency: `10/257` (`3.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `10/257` (`3.9%`)
- Dominant private-case vectors: `000` x7, `010` x3
- Score distribution (top): `0.0` x7, `33.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `c677ab3638bb4ffc8aedd80396f80d8d`, summary `Wrong Answer`, score `33`, vector `010`

```python
    tokens = chess_notation_string.split()
    piece_names = {
        'K':'King',
        'Q':'Queen',
        'R':'Rook',
        'B':'Bishop',
        'P':'Pawn',
        'N':'Knight'
    }
    for token in tokens:
        if token.endswith('.'):
            continue
        if token == "0-0" or token == "0-0-0":
            print("King")
            print("Rook")
        else:
            first_char = token[0]
            if first_char in piece_names:
# ...
```

### Runtime TypeError from invalid `input()/map()` or dictionary API usage while parsing tokens

- Cluster frequency: `8/257` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `8/257` (`3.1%`)
- Dominant private-case vectors: `000` x8
- Score distribution (top): `0.0` x8
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `8c9c1932b30a468bbf4658e922a7e0c9`, summary `Runtime Error`, score `0`, vector `000`

```python
move=input()
move_list=list(move)
a=''.join(move_list)


for i in move_list:
    if i=='e' or i=='a':
        print('Pawn')
    elif i=='N':
        print('Knight')
    elif i=='B':
        print('Bishop')
    elif i=='Q':
        print('Queen')
    elif i=='K':
        print('King')
    elif i=='O':
        a=move_list.index(i)
# ...
```

### Misclassifies queenside castling (`O-O-O`) as involving `Queen` instead of printing `King` and `Rook`

- Cluster frequency: `7/257` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `7/257` (`2.7%`)
- Dominant private-case vectors: `000` x4, `110` x1, `100` x1, `010` x1
- Score distribution (top): `0.0` x4, `33.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `54e4975eff7445fab0f7bd01cd4bfe0b`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here
a=input()
x=['K','Q','R','B','N']
if a[3]=="K":
     print("King")
elif a[3]=="Q":
     print("Queen")
elif a[3]=="R":
     print("Rook")
elif a[3]=="B":
     print("Bishop")
elif a[3]=="N":
     print("Knight")
elif a[3] not in x:
     print("Pawn")
elif a=="O-O":
     print("King")
     print("Rook")
# ...
```

### Handles castling by printing only `King` and forgets the required second line `Rook`

- Cluster frequency: `6/257` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `6/257` (`2.3%`)
- Dominant private-case vectors: `100` x3, `000` x2, `010` x1
- Score distribution (top): `33.0` x4, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `a38d6d49fff24ce09c328ccf0ea48607`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here

move=input()
k=list(move.split('.'))
for i in range(1,len(k)):

    if k[i][1] in 'abcdefghijklmnopqrstuvwxz':
        print('Pawn')
        if k[i][4] in 'abcdefghijklmnopqrstuvwxz':
            print('Pawn')
        elif k[i][4]=='K':
            print('King')
        elif k[i][4]=='Q':
            print('Queen')
        elif k[i][4]=='R':
            print('Rook')
        elif k[i][4]=='B':
            print('Bishop')
# ...
```

### Uses square/file-prefix heuristics for specific sample moves (e.g., `startswith('e')`) instead of SAN piece parsing rules

- Cluster frequency: `4/257` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `4/257` (`1.6%`)
- Dominant private-case vectors: `000` x3, `101` x1
- Score distribution (top): `0.0` x3, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `0bd8c7ea3fb147d18f5b6f70b3a95226`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here

s= str(input())
new_s = s.split()
for moves in new_s:
    if moves.startswith('1.'):
        continue
    if moves.startswith('2.'):
        continue
    if moves.startswith('3'):
        continue
    if moves.startswith('4'):
        continue
    if moves.startswith('5'):
        continue
    if moves.startswith('6'):
        continue
    if moves.startswith('7'):
# ...
```

### Runtime IndexError

- Cluster frequency: `4/257` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `4/257` (`1.6%`)
- Dominant private-case vectors: `000` x2, `101` x1, `100` x1
- Score distribution (top): `0.0` x2, `67.0` x1, `33.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `ce4de84afb3e4d219f3688124ec46b12`, summary `Runtime Error`, score `0`, vector `000`

```python
# write your solution here
chess = str(input())

for i in range(len(chess)):
    if chess[i]==' ':
        if chess[i+1]== 'K':
            print ('King')

        elif chess[i+1]=='Q':
            print ('Queen')

        elif chess[i+1]=='R':
            print ('Rook')

        elif chess[i+1]=='B':
            print ('Bishop')

        elif chess[i+1]=='N':
# ...
```

### Reads multiple separate `input()` values (`move_number`, white move, black move) instead of one notation string line

- Cluster frequency: `4/257` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `4/257` (`1.6%`)
- Dominant private-case vectors: `000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `2b0fc54023b54552909deaa698da1a8b`, summary `Runtime Error`, score `0`, vector `000`

```python
move_number = input()
white_move = input()
black_move = input()
if (white_move == "K"):
    print("King")
elif  (white_move == "Q"):
    print("Queen")
elif (white_move == "R"):
    print("Rook")
elif (white_move == "B"):
    print("Bishop")
elif (white_move == "N"):
    print("Knight")
elif (white_move == "O-O" or white_move == "O-O-O"):
    print ("King")
    print ("Rook")
else:
    print("Pawm")
# ...
```

### Parses only the first move pair (or a fixed number of tokens) instead of scanning the entire notation string

- Cluster frequency: `3/257` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `3/257` (`1.2%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `bde31e5c03024cdfb45c6fe47e049503`, summary `Wrong Answer`, score `0`, vector `000`

```python
    if move =='0-0':
        print("King")
        print("Rook")
    elif move== '0-0-0':
        print("King")
        print("Rook")
    elif move[0]=='K':
        print("King")
    elif move[0]=='Q':
        print("Queen")
    elif move[0]=='R':
        print("Rook")
    elif move[0]=='B':
        print("Bishop")
    elif move[0]=='N':
        print("Knight")
    else:
        print("Pawn")
# ...
```

### Mutates the token list while iterating (`remove(...)`), which skips moves and loses output lines

- Cluster frequency: `3/257` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `3/257` (`1.2%`)
- Dominant private-case vectors: `000` x1, `011` x1, `110` x1
- Score distribution (top): `67.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `cfbd1d079c0e490ba7f95c0be49821c3`, summary `Wrong Answer`, score `67`, vector `110`

```python
# write your solution here

s=input()
s=s.replace(".","")
lst=s.split()
for x in lst:
    if x.isdigit():
        lst.remove(x)
for i in range(len(lst)):
    if lst[i][0]=="B":
        print("Bishop")
    elif lst[i][0]=="N":
        print("Knight")
    elif lst[i][0]=="K":
        print("King")
    elif lst[i][0]=="Q":
        print("Queen")
    elif lst[i]=="O-O":
# ...
```

### Uses a brittle move-number state flag / hard-coded `1.`..`10.` list and skips many tokens in longer games

- Cluster frequency: `2/257` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `2/257` (`0.8%`)
- Dominant private-case vectors: `000` x1, `010` x1
- Score distribution (top): `0.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `02f1750139f8412097a3443bbec378ee`, summary `Wrong Answer`, score `0`, vector `000`

```python
n=input()
m=n.split(' ')
judge=0
for i in range(len(m)):
    if (m[i]=='1.' or m[i]=='2.' or m[i]=='3.' or m[i]=='4.' or m[i]=='5.' or m[i]=='6.' or m[i]=='7.' or m[i]=='8.' or m[i]=='9.' or m[i]=='10.') and judge==0:
       judge+=1
    elif judge==1:
        if m[i][0] not in 'KQRBNO':
            if m[i][1] in '12345678':
                print("Pawn")
        elif m[i][0]=='K':
            print("King")
        elif m[i][0]=='Q':
            print("Queen")
        elif m[i][0]=='R':
            print("Rook")
        elif m[i][0]=='B':
            print("Bishop")
# ...
```

### Prints a fixed piece-name sequence (sample output) instead of parsing the notation string

- Cluster frequency: `2/257` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `2/257` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `35b44eca461c4fb087bdd7d49f7ff41a`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here

print("Pawn\nPawn\nKnight\nKnight\nBishop\nPawn\nKing\nRook\nQueen\n")
```

### Tries to read an integer move count first (`int(input())`) even though input is a single notation string

- Cluster frequency: `2/257` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `2/257` (`0.8%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `b42e424cfdcd4c3e9db3acb7bed425e6`, summary `Runtime Error`, score `0`, vector `000`

```python
    if move in ['O-O','O-O-O']:
        return ["King","Rook"]
    elif move.startswith('K'):
        return ("King")
    elif move.startswith('Q'):
        return ("Queen")
    elif move.startswith('R'):
        return("Rook")
    elif move.startswith("B"):
        return("Bishop")
    elif move.startswith("N"):
        return("Knight")
    else:
        return ("Pawn")
```

### Hard-codes public sample move-to-piece outputs instead of parsing arbitrary chess-notation tokens

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `06630cacd1174b58b548e876b2276b88`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here
e4 = 'Pawn'
e5 = 'Knight'
Nf3 = 'Bishop'
Nc6 = 'King'
Bb5 = 'Rook'
a6 = 'Queen'

print(e4 )
print(e4 )
print(e5)
print(e5)
print(Nf3)
print(e4)
print(Nc6)
print(Bb5)
print(a6)
```

### Partial SAN token filtering logic: some games pass, but move-number/capture/castling token handling fails on hidden cases

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `348e61a26bc84a6f91628dbc5fdbe666`, summary `Wrong Answer`, score `33`, vector `100`

```python
# write your solution here

d = {'K':'King', 'Q':'Queen', 'R':'Rook', 'B':'Bishop', 'N':'Knight'}

s = input().split()
move = [i for i in s if not i[0].isdigit()]

for i in move:
    if i[-1]!='O' and 1<=int(i[-1])<=8 and move.count('O-O')<3 and move.count('O-O-O')<3:
        if len(i) == 2:
            print('Pawn')
        elif i[0] in d:
            print(d[i[0]])
    elif i[-1]=='O':
        print('King\nRook')
    else:
        break
```

### Hard-codes exact public sample notation strings and corresponding outputs instead of parsing arbitrary games

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `3e0afbf341da4056b3f6751e5c396404`, summary `Wrong Answer`, score `0`, vector `000`

```python
# write your solution here

inp = input()
if inp == "e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. O-O Qc7":
    print ('Pawn')
    print ('Pawn')
    print ('Knight')
    print ('Knight')
    print ('Bishop')
    print ('pawn')
    print ('King')
    print ('Rook')
    print ('Queen')
if inp == "e4 e5 2. O-O O-O-O":
    print ('Pawn')
    print ('Pawn')
    print ('King')
    print ("Rook")
# ...
```

### Misspells `.startswith(...)` as `.startwith(...)` while decoding piece tokens

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `77972e7e1f8b421aa818bd5f238a5088`, summary `Runtime Error`, score `0`, vector `000`

```python
    if move.startswith("0-0-0"):
        return["king","Rook"]
    elif move.startswith("0-0"):
        return["king","Rook"]
    elif move.startwith("K"):
        return ["king"]
    elif move.startwith("Q"):
        return ["Queen"]
    elif move.startwith("R"):
        return ["Rook"]
    elif move.startwith("B"):
        return ["Bishop"]
    elif move.startwith("N"):
        return["Knight"]
    else:
        return ["Pawn"]
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `a60e462e6e9d44f79573951e88968d6e`, summary `Runtime Error`, score `0`, vector `000`

```python
# write your solution here

k= input()
kn=input()
p = input()
h= input()
q=input()
s=input()

k- list.append(p,h,q,s)
n=list.split(0)
kn=split(q,p)
p=k.split()
k=split(l)

return k + kn
return kn
```

### Near-correct token parsing, but castling output formatting/mapping is wrong on hidden cases

- Cluster frequency: `1/257` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/10`: `1/257` (`0.4%`)
- Dominant private-case vectors: `011` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/10`, Student ID `bc9072598fc1486f983ff4b7d234a19e`, summary `Wrong Answer`, score `67`, vector `011`

```python
    move=move.upper()
    if move in ["0-0","0-0-0","O-O","O-O-O"]:
        return ["King","Rook"]
    elif move.startswith("K"):
        return ["King"]
    elif move.startswith("Q"):
        return ["Queen"]
    elif move.startswith("R"):
        return ["Rook"]
    elif move.startswith("N"):
        return ["Knight"]
    elif move.startswith("B"):
        return ['Bishop']

    else:
        return ["Pawn"]
```
