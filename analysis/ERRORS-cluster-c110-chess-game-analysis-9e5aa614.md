# Error Patterns: Cluster C110 (`Chess Game Analysis`)

## Cluster Summary

- Cluster ID: `C110`
- Cluster title: `Chess Game Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c110-chess-game-analysis-9e5aa614.md`
- Variants in cluster: `1`
- Total final submitters across variants: `354`
- Total non-full final submissions across variants: `334`
- Canonical variant (by submissions): `ns_25t2_py14_1/12`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py14_1/12` (canonical) |              354 |      334 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py14_1/12.json`

## Cluster-Level Outcome Summary

- Final submitters: `354`
- Full pass: `20`
- Non-full final submissions: `334`
- Parseable non-full (logic/runtime focus): `285`
- Non-parseable non-full: `49`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py14_1/12` |              354 |        20 |      334 |                285 |                     49 |

## Private Case Structure

- Private case 1: `parse_moves`, `get_n_moves`, and `count_piece_moves` on SAN strings with move numbers/results/castling
- Private case 2: `most_used_piece` and `remaining_pieces` (player parity + capture counting + tie-break semantics)
- Private case 3: `n_checks` and integrated SAN edge cases (checks/checkmates, castling, result-token filtering consistency)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                                                      | Cluster count | % of cluster non-full | `ns_25t2_py14_1/12` |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------: | --------------------: | ------------------: |
| Leaves template placeholders (`...`) in multiple required chess-analysis helper functions                                                                    |           221 |                 66.2% |                 221 |
| Syntax / non-parseable final submission                                                                                                                      |            49 |                 14.7% |                  49 |
| In `count_piece_moves(...)`, misclassifies queenside castling (`O-O-O`) as a `Queen` move                                                                    |             9 |                  2.7% |                   9 |
| Leaves the template placeholder `...` in `remaining_pieces(...)` (partial multi-function implementation)                                                     |             8 |                  2.4% |                   8 |
| Runtime NameError from undefined helpers/maps/counters in chess-analysis functions                                                                           |             8 |                  2.4% |                   8 |
| Leaves the template placeholder `...` in `n_checks(...)` (partial multi-function implementation)                                                             |             5 |                  1.5% |                   5 |
| Leaves the template placeholder `...` in `most_used_piece(...)` (partial multi-function implementation)                                                      |             5 |                  1.5% |                   5 |
| Uses undefined globals like `piece_map` / `piece_values` in chess-analysis helpers                                                                           |             3 |                  0.9% |                   3 |
| Uses undefined move variables (`moves`, `move`) inside helper functions                                                                                      |             3 |                  0.9% |                   3 |
| Partial chess-analysis implementation: `parse_moves`/basic helpers work, but later helper semantics fail on hidden SAN cases                                 |             3 |                  0.9% |                   3 |
| Runtime TypeError from wrong container/value types in chess helper computations                                                                              |             3 |                  0.9% |                   3 |
| In `parse_moves(...)`, strips move numbers but forgets to remove the trailing game result token (`1-0`/`0-1`/`1/2-1/2`)                                      |             2 |                  0.6% |                   2 |
| Recursive/self-calling helper (`get_n_moves`, etc.) without a terminating base case                                                                          |             2 |                  0.6% |                   2 |
| Chess-analysis helper logic is broadly incorrect across the required functions                                                                               |             2 |                  0.6% |                   2 |
| In `parse_moves(...)`, removes tokens while iterating, which skips SAN tokens and leaves move numbers/results behind                                         |             2 |                  0.6% |                   2 |
| Near-complete chess-analysis helpers, but hidden SAN edge cases fail (commonly result-token filtering, castling semantics, or tie-break/player-parity logic) |             2 |                  0.6% |                   2 |
| Parses SAN by searching for `#`/`+` positions (`.index(...)`) and crashes when the symbol is absent                                                          |             1 |                  0.3% |                   1 |
| Implements only a subset of the required chess-analysis helper functions                                                                                     |             1 |                  0.3% |                   1 |
| In `remaining_pieces(...)`, counts captures without separating white/black moves by parity                                                                   |             1 |                  0.3% |                   1 |
| In `parse_moves(...)`, returns an undefined `moves` variable instead of parsed SAN tokens                                                                    |             1 |                  0.3% |                   1 |
| In `n_checks(...)`, counts checks across all moves instead of only the specified player's moves                                                              |             1 |                  0.3% |                   1 |
| Runtime AttributeError from string/list/dict API misuse in chess helper logic                                                                                |             1 |                  0.3% |                   1 |
| Copies evaluator/sample games and checks into the submission instead of implementing general chess-analysis helpers                                          |             1 |                  0.3% |                   1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/334` (`0.0%`)

### Leaves template placeholders (`...`) in multiple required chess-analysis helper functions

- Cluster frequency: `221/334` (`66.2%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `221/334` (`66.2%`)
- Dominant private-case vectors: `000` x138, `110` x37, `111` x18, `100` x13
- Score distribution (top): `0.0` x138, `33.0` x35, `17.0` x26, `50.0` x15
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `5f9297993822468abfc4c4d8d97ba86e`, summary `Wrong Answer`, score `83`, vector `111`

```python
alphabets = ["a", "b", "c", "d", "e", "f", "g", "h", "o", "i", "j", "k", "n", "r", "q", "x"]


def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    movess = game.split(" ")
    finalmove = []
    for move in movess:
        for char in move:
            if char.lower() in alphabets:
                finalmove.append(move)
                break
    return list(finalmove)
    ...


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    movess = game.split(" ")
    finalmove = []


# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `49/334` (`14.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `49/334` (`14.7%`)
- Dominant private-case vectors: `000` x49
- Score distribution (top): `0.0` x49
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `98aded93f75049e5bcf0d1775a698fcc`, summary `Runtime Error`, score `0`, vector `000`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    tokens=games.split()
    moves=[token for token in tokens if'.' not in token]
    return moves

def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


def count_piece_moves(moves: list) -> dict:
    """Returns a dictionary with piece names and the number of moves made by that piece.

    During castling a move is counted for both king and rook.
    """
    count={"Pawn":0,"Knight":0,"Bishop":0,"Rook":0,"Queen":0,"King":0}
    for move in moves:
# ...
```

### In `count_piece_moves(...)`, misclassifies queenside castling (`O-O-O`) as a `Queen` move

- Cluster frequency: `9/334` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `9/334` (`2.7%`)
- Dominant private-case vectors: `111` x7, `001` x1, `110` x1
- Score distribution (top): `83.0` x5, `50.0` x2, `33.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `5444d029e9de4d2e92f100ba9b946c0e`, summary `Wrong Answer`, score `33`, vector `001`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    # Split the game string by spaces
    moves = game.split()

    # We will ignore move numbers (e.g., "1.", "2."), and just return the moves
    parsed_moves = [move for move in moves if not move.endswith(".")]

    return parsed_moves


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    # Split the game string by spaces
    moves = game.split()

    # Filter out the move numbers and just count the actual moves (excluding periods)
    total_moves = len([move for move in moves if not move.endswith(".")])


# ...
```

### Leaves the template placeholder `...` in `remaining_pieces(...)` (partial multi-function implementation)

- Cluster frequency: `8/334` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `8/334` (`2.4%`)
- Dominant private-case vectors: `111` x6, `001` x1, `000` x1
- Score distribution (top): `67.0` x4, `50.0` x2, `17.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `1660fe89726b4cbeb901eaec49b8331f`, summary `Wrong Answer`, score `50`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    l = game.split(" ")
    for i in range(1, (len(l) // 3) + 1):
        l.remove(f"{i}.")
    l.pop(-1)
    return l


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    l = game.split(" ")
    for i in range(1, (len(l) // 3) + 1):
        l.remove(f"{i}.")

    return len(l) - 1


# ...
```

### Runtime NameError from undefined helpers/maps/counters in chess-analysis functions

- Cluster frequency: `8/334` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `8/334` (`2.4%`)
- Dominant private-case vectors: `000` x6, `111` x2
- Score distribution (top): `0.0` x6, `50.0` x1, `83.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `9dba0fe8968249a3ac027ac177fe1944`, summary `Runtime Error`, score `0`, vector `000`

```python
'''def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    game = "1. d4 d5 2. c4 Nf6 3. cxd5 Nxd5 4. Nf3 Be6 5. e4 Nb6 6. Nc3 f5 7. Ng5 Qd7 8. Nb5 c6 9. Nxe6 Qxe6 10. Nc7+ Kd8 11. Nxe6+ Ke8 12. Nc7+ Kd8 13. Bf4 N8d7 14. d5 e6 15. dxe6 Bb4+ 16. Ke2 Rc8 17. exd7 Nxd7 18. Ne6+ Ke7 19. Nxg7 Rcg8 20. Bd6+ Bxd6 21. Nxf5+ Ke6 22. Qxd6+ Kf7 23. Qxd7+ Kf8 24. Qe7# 1-0"
moves = [
    'd4', 'd5', 'c4', 'Nf6', 'cxd5', 'Nxd5', 'Nf3', 'Be6', 'e4', 'Nb6',
    'Nc3', 'f5', 'Ng5', 'Qd7', 'Nb5', 'c6', 'Nxe6', 'Qxe6', 'Nc7+', 'Kd8',
    'Nxe6+', 'Ke8', 'Nc7+', 'Kd8', 'Bf4', 'N8d7', 'd5', 'e6', 'dxe6', 'Bb4+',
    'Ke2', 'Rc8', 'exd7', 'Nxd7', 'Ne6+', 'Ke7', 'Nxg7', 'Rcg8', 'Bd6+',
    'Bxd6', 'Nxf5+', 'Ke6', 'Qxd6+', 'Kf7', 'Qxd7+', 'Kf8', 'Qe7#'
]
is_equal(
    parse_moves(game),
    moves
)
game = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 b5 5. Bb3 Nd4 6. Nxd4 exd4 7. O-O Bb7 8. Qf3 Bc5 9. Qxf7# 1-0"
moves = [
    'e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5', 'Bb3',
    'Nd4', 'Nxd4', 'exd4', 'O-O', 'Bb7', 'Qf3', 'Bc5', 'Qxf7#'
# ...
```

### Leaves the template placeholder `...` in `n_checks(...)` (partial multi-function implementation)

- Cluster frequency: `5/334` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `5/334` (`1.5%`)
- Dominant private-case vectors: `000` x3, `111` x1, `110` x1
- Score distribution (top): `0.0` x3, `50.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `50e597edeaae4352b1be8dbd81bd1dd1`, summary `Wrong Answer`, score `50`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    lst = game.split(' ')

    for i in lst[::3]:
        lst.remove(i)

    return lst[:len(lst)-1]


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    res = parse_moves(game)

    return len(res)


def count_piece_moves(moves: list) -> dict:
# ...
```

### Leaves the template placeholder `...` in `most_used_piece(...)` (partial multi-function implementation)

- Cluster frequency: `5/334` (`1.5%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `5/334` (`1.5%`)
- Dominant private-case vectors: `110` x3, `111` x1, `100` x1
- Score distribution (top): `50.0` x2, `83.0` x1, `17.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `fd5f43e7105e455d8ef369243b04eca5`, summary `Wrong Answer`, score `50`, vector `110`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    moves_list = game.split(" ")
    for i in moves_list:
        if i.endswith("."):
            moves_list.remove(i)
        if i == "1-0":
            moves_list.remove(i)

    return moves_list


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    moves_list = game.split(" ")
    for i in moves_list:
        if i.endswith("."):
            moves_list.remove(i)


# ...
```

### Uses undefined globals like `piece_map` / `piece_values` in chess-analysis helpers

- Cluster frequency: `3/334` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `3/334` (`0.9%`)
- Dominant private-case vectors: `000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `49bcf9351b99495eaa6ec1b8afc6be69`, summary `Runtime Error`, score `0`, vector `000`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    game = re.sub(r"\d+\.", "", game).strip()
    moves = game.split()
    if moves[-1] in {"1-0", "0-1", "1/2-1/2"}:
        moves.pop()
    return moves


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


def count_piece_moves(moves: list) -> dict:
    """Returns a dictionary with piece names and the number of moves made by that piece.

    During castling a move is counted for both king and rook.
    """


# ...
```

### Uses undefined move variables (`moves`, `move`) inside helper functions

- Cluster frequency: `3/334` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `3/334` (`0.9%`)
- Dominant private-case vectors: `100` x1, `110` x1, `010` x1
- Score distribution (top): `17.0` x2, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `6d4faa3732e540cb988919e43edaf11f`, summary `Runtime Error`, score `67`, vector `110`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    moves = []
    for i , n in enumerate(game.split(" ")):
        if i % 3 == 0:
            continue
        moves.append(n)
    moves.pop()
    return moves



def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


def count_piece_moves(moves: list) -> dict:
# ...
```

### Partial chess-analysis implementation: `parse_moves`/basic helpers work, but later helper semantics fail on hidden SAN cases

- Cluster frequency: `3/334` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `3/334` (`0.9%`)
- Dominant private-case vectors: `001` x2, `110` x1
- Score distribution (top): `33.0` x2, `17.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `1ca936b5714844d5b66c045c739e5bc5`, summary `Wrong Answer`, score `33`, vector `001`

```python
import re
from collections import defaultdict

# SAN to full piece names
PIECE_NAMES = {
    'K': 'King',
    'Q': 'Queen',
    'R': 'Rook',
    'B': 'Bishop',
    'N': 'Knight'
}

# For tie-breaking by value
PIECE_VALUES = {
    'Pawn': 1,
    'Bishop': 2,
    'Knight': 3,
    'Rook': 4,
# ...
```

### Runtime TypeError from wrong container/value types in chess helper computations

- Cluster frequency: `3/334` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `3/334` (`0.9%`)
- Dominant private-case vectors: `111` x1, `000` x1, `100` x1
- Score distribution (top): `83.0` x1, `0.0` x1, `17.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `3c98d6eb29f94b96bbfc64c542dab5f0`, summary `Runtime Error`, score `83`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    l = []
    game2 = ""
    for i in range(len(game) - 3):
        if (game[i] in "1234567890" and game[i + 1] == ".") or game[i] == ".":
            continue
        else:
            game2 += game[i]
    l = game2.split(" ")
    l2 = []
    for ele in l:
        if ele == "" or ele == " " or ele in "123456789":
            continue
        else:
            l2.append(ele)
    return l2


# ...
```

### In `parse_moves(...)`, strips move numbers but forgets to remove the trailing game result token (`1-0`/`0-1`/`1/2-1/2`)

- Cluster frequency: `2/334` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `2/334` (`0.6%`)
- Dominant private-case vectors: `111` x1, `001` x1
- Score distribution (top): `67.0` x1, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `04d59247b8724fc69b2ddcd5563c4935`, summary `Wrong Answer`, score `67`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    s = game
    l = s.split(" ")
    l2 = []
    for x in l:
        if not ("." in x):
            l2.append(x)

    return l2[: len(l2) - 1 :]


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    s = game
    l = s.split(" ")


# ...
```

### Recursive/self-calling helper (`get_n_moves`, etc.) without a terminating base case

- Cluster frequency: `2/334` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `2/334` (`0.6%`)
- Dominant private-case vectors: `000` x1, `100` x1
- Score distribution (top): `0.0` x1, `17.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `4f6630f96c6e48e9b972756b6827904f`, summary `Runtime Error`, score `0`, vector `000`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    return [
        "d4",
        "d5",
        "c4",
        "Nf6",
        "cxd5",
        "Nxd5",
        "Nf3",
        "Be6",
        "e4",
        "Nb6",
        "Nc3",
        "f5",
        "Ng5",
        "Qd7",
        "Nb5",
        "c6",
        "Nxe6",
        "Qxe6",
        "Nc7+",
        "Kd8",
        "Nxe6+",
        "Ke8",
        "Nc7+",
        "Kd8",
        "Bf4",
        "N8d7",
        "d5",
        "e6",
        "dxe6",
        "Bb4+",
        "Ke2",
        "Rc8",
        "exd7",
        "Nxd7",
        "Ne6+",
        "Ke7",
        "Nxg7",
        "Rcg8",
        "Bd6+",
        "Bxd6",
        "Nxf5+",
        "Ke6",
        "Qxd6+",
        "Kf7",
        "Qxd7+",
        "Kf8",
        "Qe7#",
    ]


[
    "e4",
    "e5",
    "Nf3",
    "Nc6",
    "Bb5",
    "a6",
    "Ba4",
    "b5",
    "Bb3",
    "Nd4",
    "Nxd4",
    "exd4",
    "O-O",
    "Bb7",
    "Qf3",
    "Bc5",
    "Qxf7#",
]


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return 47 and 17


def count_piece_moves(moves: list) -> dict:
    """Returns a dictionary with piece names and the number of moves made by that piece.

    During castling a move is counted for both king and rook.
    """


# ...
```

### Chess-analysis helper logic is broadly incorrect across the required functions

- Cluster frequency: `2/334` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `2/334` (`0.6%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `6cbbbb139ee843adbba237d338e11c4c`, summary `Wrong Answer`, score `0`, vector `000`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    parse_moves = list(game)
    white_count = 0
    black_count = 0

    for _ in parse_moves:
        if game == 'white':
            white_count += 1
            white_count.append()
        elif game == 'black':
            black_count += 1
            black_count.append()

    return [game + ',']


def get_n_moves(game: str) -> int:
# ...
```

### In `parse_moves(...)`, removes tokens while iterating, which skips SAN tokens and leaves move numbers/results behind

- Cluster frequency: `2/334` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `2/334` (`0.6%`)
- Dominant private-case vectors: `110` x1, `111` x1
- Score distribution (top): `67.0` x1, `83.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `dd4664dcaa1e4c6e9071c33c0d82c603`, summary `Wrong Answer`, score `83`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    movesinit = game.split(" ")
    for i in movesinit:
        if i[0] in "1234567890":
            movesinit.remove(i)
    return movesinit


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    turns = 0
    lists = game.split(" ")
    movesy = len(lists) // 3
    if len(lists) % 3 == 0:
        return movesy * 2 - 1
    else:
        return movesy * 2


# ...
```

### Near-complete chess-analysis helpers, but hidden SAN edge cases fail (commonly result-token filtering, castling semantics, or tie-break/player-parity logic)

- Cluster frequency: `2/334` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `2/334` (`0.6%`)
- Dominant private-case vectors: `111` x2
- Score distribution (top): `83.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `87d281ba22934c659393ac35607606bd`, summary `Wrong Answer`, score `83`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    indexes = [str(i) + "." for i in range(100)]
    move = game.split()
    ans = []
    for s in move:
        if s in indexes:
            pass
        else:
            ans.append(s)

    return ans[:-1]


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


# ...
```

### Parses SAN by searching for `#`/`+` positions (`.index(...)`) and crashes when the symbol is absent

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `011` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `2b8696e4bab9419085d14bdf4243042c`, summary `Runtime Error`, score `33`, vector `011`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    last = game.index("#")
    first = game.index(".")
    s = game[first + 1 : last + 1]
    s = s.strip()
    lst = s.split(".")

    new_list = []
    for move in lst:
        m = move.strip().split(" ")
        new_list.append(m[0].strip())
        if len(m) > 2:
            new_list.append(m[1].strip())

    return new_list


# ...
```

### Implements only a subset of the required chess-analysis helper functions

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `2d6eae9751474b3493cddde65ef6d1df`, summary `Wrong Answer`, score `50`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    a = game.split()
    b = []
    for i in range(0, len(a) - 2, 3):
        b = b + [a[i + 1]] + [a[i + 2]]
    b.reverse()
    b = b[1:]
    b.reverse()
    return b


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


def count_piece_moves(moves: list) -> dict:
    piece_counts = {"King": 0, "Queen": 0, "Rook": 0, "Bishop": 0, "Knight": 0, "Pawn": 0}


# ...
```

### In `remaining_pieces(...)`, counts captures without separating white/black moves by parity

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `83.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `343aff2ac9b74e4a98754c43ca509738`, summary `Wrong Answer`, score `83`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    l=game.split()
    ans=[]
    for i in range(len(l)-1):
        if i%3!=0:
            ans.append(l[i])
    return ans

def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    return len(parse_moves(game))


def count_piece_moves(moves: list) -> dict:
    """Returns a dictionary with piece names and the number of moves made by that piece.

    During castling a move is counted for both king and rook.
# ...
```

### In `parse_moves(...)`, returns an undefined `moves` variable instead of parsed SAN tokens

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `46fd0fc905114057b1bdf7f63c4c49e4`, summary `Wrong Answer`, score `50`, vector `110`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    game = game.replace("\n", "").replace("\r", "")
    tokens = game.split()
    moves = []
    for token in tokens:
        if token[0].isdigit() and token[-1] == ".":
            continue
        if token[0].isdigit() and token.endswith("."):
            continue
        if token in ["1-0", "0-1", "1/2-1/2"]:
            continue
        moves.append(token)
    return moves


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""


# ...
```

### In `n_checks(...)`, counts checks across all moves instead of only the specified player's moves

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `83.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `4b19c30764a741dc98d9e81f0e377cbf`, summary `Wrong Answer`, score `83`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    result = []
    moves = game.split()
    for i in range(len(moves)):
        if i == len(moves) - 1:
            return result
        if moves[i].endswith("."):
            continue
        else:
            result.append(moves[i])
    return result


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    result1 = parse_moves(game)
    return len(result1)


# ...
```

### Runtime AttributeError from string/list/dict API misuse in chess helper logic

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `111` x1
- Score distribution (top): `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `63b548403f0546bea64ece3388c1bb92`, summary `Runtime Error`, score `50`, vector `111`

```python
def parse_moves(game: str) -> list:
    """Returns a list with alternate white and black moves."""
    tokens = game.strip().split()
    moves = []
    for token in tokens:
        if "." in token:
            continue
        if token in {"1-0", "0-1", "1/2-1/2"}:
            continue
        moves.append(token)
    return moves


def get_n_moves(game: str) -> int:
    """Returns the total number of moves played in the game."""
    moves = parse_moves(game)
    return len(moves)


# ...
```

### Copies evaluator/sample games and checks into the submission instead of implementing general chess-analysis helpers

- Cluster frequency: `1/334` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py14_1/12`: `1/334` (`0.3%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py14_1/12`, Student ID `a9d78bf76ef54f1a8c61bd43fed65a88`, summary `Wrong Answer`, score `0`, vector `000`

```python
def parse_moves(game: str) -> list:
 game = "1. d4 d5 2. c4 Nf6 3. cxd5 Nxd5 4. Nf3 Be6 5. e4 Nb6 6. Nc3 f5 7. Ng5 Qd7 8. Nb5 c6 9. Nxe6 Qxe6 10. Nc7+ Kd8 11. Nxe6+ Ke8 12. Nc7+ Kd8 13. Bf4 N8d7 14. d5 e6 15. dxe6 Bb4+ 16. Ke2 Rc8 17. exd7 Nxd7 18. Ne6+ Ke7 19. Nxg7 Rcg8 20. Bd6+ Bxd6 21. Nxf5+ Ke6 22. Qxd6+ Kf7 23. Qxd7+ Kf8 24. Qe7# 1-0"
moves = ['d4', 'd5', 'c4', 'Nf6', 'cxd5', 'Nxd5', 'Nf3', 'Be6', 'e4', 'Nb6',
    'Nc3', 'f5', 'Ng5', 'Qd7', 'Nb5', 'c6', 'Nxe6', 'Qxe6', 'Nc7+', 'Kd8',
    'Nxe6+', 'Ke8', 'Nc7+', 'Kd8', 'Bf4', 'N8d7', 'd5', 'e6', 'dxe6', 'Bb4+',
    'Ke2', 'Rc8', 'exd7', 'Nxd7', 'Ne6+', 'Ke7', 'Nxg7', 'Rcg8', 'Bd6+',
    'Bxd6', 'Nxf5+', 'Ke6', 'Qxd6+', 'Kf7', 'Qxd7+', 'Kf8', 'Qe7#']
(parse_moves,
    moves)
game = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 b5 5. Bb3 Nd4 6. Nxd4 exd4 7. O-O Bb7 8. Qf3 Bc5 9. Qxf7# 1-0"
moves = ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5', 'Bb3',
    'Nd4', 'Nxd4', 'exd4', 'O-O', 'Bb7', 'Qf3', 'Bc5', 'Qxf7#']


def get_n_moves(game: str) -> int:
    game = "1. d4 d5 2. c4 Nf6 3. cxd5 Nxd5 4. Nf3 Be6 5. e4 Nb6 6. Nc3 f5 7. Ng5 Qd7 8. Nb5 c6 9. Nxe6 Qxe6 10. Nc7+ Kd8 11. Nxe6+ Ke8 12. Nc7+ Kd8 13. Bf4 N8d7 14. d5 e6 15. dxe6 Bb4+ 16. Ke2 Rc8 17. exd7 Nxd7 18. Ne6+ Ke7 19. Nxg7 Rcg8 20. Bd6+ Bxd6 21. Nxf5+ Ke6 22. Qxd6+ Kf7 23. Qxd7+ Kf8 24. Qe7# 1-0"

(get_n_moves(game),
# ...
```
