# Error Patterns: Cluster C014 (`Book Data Analysis`)

## Cluster Summary

- Cluster ID: `C014`
- Cluster title: `Book Data Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c014-book-data-analysis-6446788a.md`
- Variants in cluster: `2`
- Total final submitters across variants: `803`
- Total non-full final submissions across variants: `447`
- Canonical variant (by submissions): `ns_25t2_py21_2/24`

Cluster membership (zero-submitter variants omitted):

| Variant                         | final_submitters | non_full | Relationship                 |
| ------------------------------- | ---------------: | -------: | ---------------------------- |
| `ns_25t2_py21_1/19`             |              383 |      212 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/24` (canonical) |              420 |      235 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/24.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/19.json`

## Cluster-Level Outcome Summary

- Final submitters: `803`
- Full pass: `356`
- Non-full final submissions: `447`
- Parseable non-full (logic/runtime focus): `374`
- Non-parseable non-full: `73`

Variant-level comparison:

| Variant             | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| ------------------- | ---------------: | --------: | -------: | -----------------: | ---------------------: |
| `ns_25t2_py21_1/19` |              383 |       171 |      212 |                181 |                     31 |
| `ns_25t2_py21_2/24` |              420 |       185 |      235 |                193 |                     42 |

## Private Case Structure

- Private case 1: `get_short_books` correctness on varied pages/ISBNs
- Private case 2: `get_medium_books` boundary handling (200 and 500 inclusive)
- Private case 3: `get_pages_by_isbn` lookup (found cases in varied positions)
- Private case 4: `count_by_language` aggregation into exact language-count dict
- Private case 5: `total_pages_in_genre_lang` filtered page summation across multiple matches

Private-case vectors in this report are 5-character pass/fail strings over the private case groups (e.g., `10001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern                                                                                                                                                    | Cluster count | % of cluster non-full | `ns_25t2_py21_1/19` | `ns_25t2_py21_2/24` |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------: | --------------------: | ------------------: | ------------------: |
| Broad multi-function failure (multiple required helpers incomplete, placeholder, hard-coded, or semantically incorrect)                                    |            95 |                 21.3% |                  49 |                  46 |
| Syntax / non-parseable final submission                                                                                                                    |            73 |                 16.3% |                  31 |                  42 |
| In `count_by_language`, returns from inside the loop, so only the first/partial language counts are produced                                               |            45 |                 10.1% |                  21 |                  24 |
| Implements earlier helper functions but leaves `count_by_language` / `total_pages_in_genre_lang` incomplete (`...` / placeholder logic)                    |            36 |                  8.1% |                  20 |                  16 |
| Early helper functions are mostly correct, but aggregation helpers (`count_by_language` and/or `total_pages_in_genre_lang`) are wrong or incomplete        |            27 |                  6.0% |                  16 |                  11 |
| Runtime NameError from variable-name mismatch (`data` vs `book_data`) across helper functions                                                              |            25 |                  5.6% |                  14 |                  11 |
| In `get_medium_books`, uses `< 500` instead of inclusive `<= 500`, so 500-page books are wrongly excluded                                                  |            19 |                  4.3% |                   4 |                  15 |
| In `get_pages_by_isbn`, returns `None` inside the search loop (prematurely exits after the first non-match)                                                |            17 |                  3.8% |                   6 |                  11 |
| Runtime TypeError from collection-building misuse across the required book-data helper functions                                                           |            15 |                  3.4% |                   5 |                  10 |
| Partial multi-function solution with `get_pages_by_isbn` lookup/control-flow bug (often premature `return None`) and another helper issue                  |            14 |                  3.1% |                   6 |                   8 |
| Hard-codes sample ISBN sets/dicts or outputs instead of computing from the provided book list                                                              |            13 |                  2.9% |                   4 |                   9 |
| Usually `get_medium_books` boundary bug (`<500`) plus additional later-helper mistakes (common multi-function partial pass)                                |             9 |                  2.0% |                   5 |                   4 |
| Only one helper function appears correct; others are missing, type-mismatched (list vs set), or placeholder/hard-coded                                     |             9 |                  2.0% |                   5 |                   4 |
| Returns lists from `get_short_books`/`get_medium_books` instead of the required ISBN sets                                                                  |             8 |                  1.8% |                   4 |                   4 |
| Partial multi-function solution: `get_short_books` mostly works, but several other helpers are missing/incomplete or contain control-flow/indexing bugs    |             6 |                  1.3% |                   4 |                   2 |
| Runtime KeyError from direct dictionary counting/lookup without initializing language keys                                                                 |             6 |                  1.3% |                   3 |                   3 |
| Runtime NameError                                                                                                                                          |             5 |                  1.1% |                   2 |                   3 |
| Runtime ValueError                                                                                                                                         |             5 |                  1.1% |                   3 |                   2 |
| Uses membership (`if isbn in book`) instead of exact ISBN equality in `get_pages_by_isbn`                                                                  |             4 |                  0.9% |                   2 |                   2 |
| Uses `range(len(book_data)-1)`, skipping the last book and causing off-by-one errors in one or more helpers                                                |             3 |                  0.7% |                   1 |                   2 |
| Does not define all five required functions (`get_short_books`, `get_medium_books`, `get_pages_by_isbn`, `count_by_language`, `total_pages_in_genre_lang`) |             3 |                  0.7% |                   1 |                   2 |
| Runtime AttributeError                                                                                                                                     |             3 |                  0.7% |                   2 |                   1 |
| Runtime IndexError                                                                                                                                         |             2 |                  0.4% |                   1 |                   1 |
| Uses external file I/O (`open`/`read_csv`) instead of operating on the provided `book_data` list parameter                                                 |             1 |                  0.2% |                   0 |                   1 |
| Other wrong-answer logic pattern (residual)                                                                                                                |             1 |                  0.2% |                   0 |                   1 |
| Runtime error (parseable final submission)                                                                                                                 |             1 |                  0.2% |                   1 |                   0 |
| Runtime RecursionError                                                                                                                                     |             1 |                  0.2% |                   1 |                   0 |
| Uses unsupported imports/dependencies in the evaluator environment                                                                                         |             1 |                  0.2% |                   1 |                   0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `1/447` (`0.2%`)

### Broad multi-function failure (multiple required helpers incomplete, placeholder, hard-coded, or semantically incorrect)

- Cluster frequency: `95/447` (`21.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `49/212` (`23.1%`)
  - `ns_25t2_py21_2/24`: `46/235` (`19.6%`)
- Dominant private-case vectors: `00000` x95
- Score distribution (top): `0.0` x94, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `fabc9f0d2eee4e629a3823c03acb908b`, summary `Wrong Answer`, score `0`, vector `00000`

```python
data = [("978-3-16-148410-0", 150, "English", "Thriller"),
        ("978-0-14-103620-2", 450, "Tamil", "Fantasy"),
        ("978-1-4028-9467-2", 200, "English", "Fiction"),
        ("978-0-393-04002-2", 350, "Hindi", "History"),
        ("978-0-06-112008-4", 300, "English", "Fiction"),
        ("978-1-60413-970-0", 175, "Bengali", "Mystery"),
        ("978-0-7432-7356-5", 420, "English", "Science Fiction"),
        ("978-1-56619-909-4", 100, "Tamil", "Romance"),
        ("978-1-4088-4994-7", 270, "Telugu", "Biography"),
        ("978-0-374-53243-2", 540, "English", "Thriller")]

def get_short_books(book_data:list, pages: int) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    if (data(pages) > 200):
        return book_data ['978-3-16-148410-0', '978-1-60413-970-0', '978-1-56619-909-4']

def get_medium_books(book_data:list) -> set:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `81e1870f567245aead6842e348a6a37e`, summary `Wrong Answer`, score `40`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    x = len(book_data)
    short_books = []
    for i in range(0, x):
        if book_data[i][1] < 200:
            short_books += book_data[i][0]
    return set(short_books)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    x = len(book_data)
    medium_books = []
    for i in range(0, x):
        if book_data[i][1] > 200 and book_data[i][1] < 500:
            medium_books += book_data[i][0]


# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `73/447` (`16.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `31/212` (`14.6%`)
  - `ns_25t2_py21_2/24`: `42/235` (`17.9%`)
- Dominant private-case vectors: `00000` x73
- Score distribution (top): `0.0` x73
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `cbdf04d513764e2ca266c39fcc22147f`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...


def count_by_language(book_data: list) -> dict:
    """Returns a dict with the languages as keys and the number of books of that language as values."""
    ...


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `a6885569e50c488ab296c012bfeae270`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    return [book_data[0] for book in book_data if book_data[1] < 200]


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...


def count_by_language(book_data: list) -> dict:
    """Returns a dict with the languages as keys and the number of books of that language as values."""
    ...


# ...
```

### In `count_by_language`, returns from inside the loop, so only the first/partial language counts are produced

- Cluster frequency: `45/447` (`10.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `21/212` (`9.9%`)
  - `ns_25t2_py21_2/24`: `24/235` (`10.2%`)
- Dominant private-case vectors: `00111` x26, `00101` x9, `00110` x5, `00100` x2
- Score distribution (top): `80.0` x30, `60.0` x7, `40.0` x5, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `fd0ad5cbfbca46e58742fd79632a9f30`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    list1 = []
    for i, x in enumerate(book_data):
        list2 = book_data[i]
        isbn = list2[0]
        pages = list2[1]
        if pages < 200:
            list1.append(isbn)
    return set(list1)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    list1 = []
    for i, x in enumerate(book_data):
        list2 = book_data[i]
        isbn = list2[0]
        pages = list2[1]


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `c8da9d2b51e24e129a3bda84dac73e7c`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    shortbook = []
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            shortbook.append(book_data[i][0])
    shortbook_set = set(shortbook)
    return shortbook_set


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    mediumbook = []
    for i in range(len(book_data)):
        if 200 <= book_data[i][1] <= 500:
            mediumbook.append(book_data[i][0])
    mediumbook_set = set(mediumbook)


# ...
```

### Implements earlier helper functions but leaves `count_by_language` / `total_pages_in_genre_lang` incomplete (`...` / placeholder logic)

- Cluster frequency: `36/447` (`8.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `20/212` (`9.4%`)
  - `ns_25t2_py21_2/24`: `16/235` (`6.8%`)
- Dominant private-case vectors: `00111` x36
- Score distribution (top): `60.0` x18, `80.0` x18
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `f53ac78539ca47a1887a752393568fc5`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ISBNs = []
    i = 0
    while i in range(0, len(data)):
        if data[i][1] < 200:
            ISBNs.append(data[i][0])
        i += 1
    return set(ISBNs)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    isbn = []
    i = 0
    while i in range(0, len(data)):
        if data[i][1] >= 200 and data[i][1] <= 500:
            isbn.append(data[i][0])
        i += 1


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `038a9af131044e13bf444cdf0dfdf8d3`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    book_set = set()
    for i in range(len(book_data)):
        t = tuple()
        t = tuple(book_data[i])
        if t[1] < 200:
            book_set.add(t[0])
    return book_set


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    book_set = set()
    for i in range(len(book_data)):
        t = tuple()
        t = tuple(book_data[i])
        if 200 <= t[1] <= 500:
            book_set.add(t[0])


# ...
```

### Early helper functions are mostly correct, but aggregation helpers (`count_by_language` and/or `total_pages_in_genre_lang`) are wrong or incomplete

- Cluster frequency: `27/447` (`6.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `16/212` (`7.5%`)
  - `ns_25t2_py21_2/24`: `11/235` (`4.7%`)
- Dominant private-case vectors: `00111` x27
- Score distribution (top): `80.0` x22, `60.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `139005fc975e48c9ae8439c4e5528b1a`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    sett = set()
    for pages in data:
        if pages[1]<200:
            sett.add(pages[0])
    return sett

def get_medium_books(book_data:list) -> set:
    sett = set()
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    for pages in data:
        if 200 <=pages[1]<=500:
            sett.add(pages[0])
    return sett


def get_pages_by_isbn(book_data:list, isbn: str) -> int:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `bdd5a27e9ce849f58f07715a93c2b470`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    l = []
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            l.append(book_data[i][0])
    l_s = set(l)
    return l_s


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    l1 = []
    for i in range(len(book_data)):
        if 200 <= book_data[i][1] <= 500:
            l1.append(book_data[i][0])
    l1_s = set(l1)
    return l1_s


# ...
```

### Runtime NameError from variable-name mismatch (`data` vs `book_data`) across helper functions

- Cluster frequency: `25/447` (`5.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `14/212` (`6.6%`)
  - `ns_25t2_py21_2/24`: `11/235` (`4.7%`)
- Dominant private-case vectors: `00111` x11, `00000` x10, `00100` x1, `00101` x1
- Score distribution (top): `0.0` x9, `80.0` x9, `60.0` x3, `20.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `20b6b50e3f6844208ea38c726911ab15`, summary `Runtime Error`, score `0`, vector `00000`

```python
from typing import List, Tuple, Dict, Set
import ast
import sys


def get_short_books(book_data: List[Tuple[str, int, str, str]]) -> List[str]:
    return [isbn for isbn, pages, _, _, _ in book_data if pages < 200]


def get_medium_books(book_data: List[Tuple[str, int, str, str]]) -> List[str]:
    return [isbn for isbn, pages, _, _, _ in book_data if 200 <= pages < 500]


def get_pages(book_data: List[Tuple[str, int, str, str]], isbn: str) -> int:
    for isbn, pages, _, _, _ in book_data:
        if b_isbn == isbn:
            return pages
    return -1


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `32783e45160a476ab02847d2dbd387e5`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    return [book for book in books_data if book[1] < 200]
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...


def get_medium_books(book_data: list) -> set:
    return [book for book in books_data if 200 <= book[1] <= 300]
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    for book in books_data:
        if book[0] == isbn:
            return book[1]


# ...
```

### In `get_medium_books`, uses `< 500` instead of inclusive `<= 500`, so 500-page books are wrongly excluded

- Cluster frequency: `19/447` (`4.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `4/212` (`1.9%`)
  - `ns_25t2_py21_2/24`: `15/235` (`6.4%`)
- Dominant private-case vectors: `00101` x16, `00100` x2, `00000` x1
- Score distribution (top): `80.0` x7, `60.0` x5, `40.0` x4, `20.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `ef550493a2bb4b8da430e4412063cb4d`, summary `Wrong Answer`, score `20`, vector `00100`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    s = set()
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            s.add(book_data[i][0])

    return s


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""

    s = set()
    for i in range(len(book_data)):
        if 200 <= book_data[i][1] < 500:
            s.add(book_data[i][0])
    return s


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `a527b932ceb143b7bd4a4a05256bf432`, summary `Wrong Answer`, score `60`, vector `00101`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    short_books = []
    for i in range(len(book_data)):
        if int(book_data[i][1]) < 200:
            short_books.append(book_data[i][0])
            # print(short_books)
    return set(short_books)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...
    medium_books = []
    for i in range(len(book_data)):
        if 200 <= int(book_data[i][1]) < 500:
            medium_books.append(book_data[i][0])
            # print(medium_books)


# ...
```

### In `get_pages_by_isbn`, returns `None` inside the search loop (prematurely exits after the first non-match)

- Cluster frequency: `17/447` (`3.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `6/212` (`2.8%`)
  - `ns_25t2_py21_2/24`: `11/235` (`4.7%`)
- Dominant private-case vectors: `00111` x6, `00110` x4, `00101` x3, `00001` x2
- Score distribution (top): `80.0` x7, `40.0` x6, `60.0` x3, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `04e3c983d8084c44a5e1375a32b85416`, summary `Wrong Answer`, score `40`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    new = []
    for item in book_data:
        pages = item[1]
        if pages < 200:
            new.append(pages)
    my_set = new
    return my_set


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    new = []
    for item in book_data:
        pages = item[1]
        if 200 <= pages <= 500:
            new.append(pages)


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `0c48678766d943c7b034e5744d8576ba`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    #return [book_data for book_data in book_data if book_data[1]<200]
    return set([isbns for isbns,pages , _, _ in book_data if pages < 200])

def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...
    return set([isbns for isbns,pages , _, _ in book_data if 200<= pages <= 500])

def get_pages_by_isbn(book_data:list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...
    for b_isbn , pages, _, _ in book_data:
        if b_isbn == isbn:
            return pages
    return None
    for _, _, lang, _ in book_data:
# ...
```

### Runtime TypeError from collection-building misuse across the required book-data helper functions

- Cluster frequency: `15/447` (`3.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `5/212` (`2.4%`)
  - `ns_25t2_py21_2/24`: `10/235` (`4.3%`)
- Dominant private-case vectors: `00000` x6, `00111` x4, `00100` x2, `00011` x1
- Score distribution (top): `0.0` x5, `80.0` x4, `60.0` x3, `20.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `e64568ac03a94b088c948d74f330af54`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    output_short = set()
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            output_short.add(book_data[i][0])
    return output_short


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    output_medium = set()
    for i in range(len(book_data)):
        if book_data[i][1] >= 200 and book_data[i][1] <= 500:
            output_medium.add(book_data[i][0])
    return output_medium


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `2c41356dd8b947058b05e123dfc72faf`, summary `Runtime Error`, score `60`, vector `00010`

```python
def get_short_books(book_data: list, genre: str, lang: str) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    return sum(pages for _, pages, lang, gen in book_data if lang == language and gen == genre)

    def get_short_books(book_data):
        return {isbn for isbn, pages, _, _ in book_data if pages < 200}


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    return {isbn for isbn, pages, _, _ in book_data if 200 <= pages <= 500}


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    for isbn, pages, _, _ in book_data:
        if target_isbn == isbn:
            return pages
    return None


# ...
```

### Partial multi-function solution with `get_pages_by_isbn` lookup/control-flow bug (often premature `return None`) and another helper issue

- Cluster frequency: `14/447` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `6/212` (`2.8%`)
  - `ns_25t2_py21_2/24`: `8/235` (`3.4%`)
- Dominant private-case vectors: `00110` x14
- Score distribution (top): `40.0` x11, `60.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `dad513095ce04cd1b893335e57f55826`, summary `Wrong Answer`, score `60`, vector `00110`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    short_book = set()
    for ele in book_data:
        if ele[1] < 200:
            short_book.add(ele[0])
    return short_book


def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    medium_book = set()
    for ele in book_data:
        if 200 <= ele[1] <= 500:
            medium_book.add(ele[0])
    return medium_book

def get_pages_by_isbn(book_data:list, isbn: str) -> int:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `6ccec9f68114454c99fcf26c569d3d23`, summary `Wrong Answer`, score `40`, vector `00110`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    all_isbn = []
    all_pages = []
    all_languages = []
    all_genre = []
    set_isbn = []
    for i in book_data:
        isbn, pages, language, genre = i
        all_isbn.append(isbn)
        all_pages.append(pages)

    for i in range(len(all_pages)):
        if all_pages[i] < 200:
            set_isbn.append(all_isbn[i])

    return set(set_isbn)


# ...
```

### Hard-codes sample ISBN sets/dicts or outputs instead of computing from the provided book list

- Cluster frequency: `13/447` (`2.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `4/212` (`1.9%`)
  - `ns_25t2_py21_2/24`: `9/235` (`3.8%`)
- Dominant private-case vectors: `00000` x8, `00101` x3, `00001` x1, `00111` x1
- Score distribution (top): `0.0` x8, `80.0` x3, `40.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `cd2ac6c187b04a0f8170b59e30290341`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    short_books=[]
    for book in book_data:
        isbn=book[0]
        pages=0
        if pages < 200:
            short_books.append(isbn)
    return short_books


def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    short_books=[]
    for book in book_data:
        isbn=book[0]
        pages=0
        if 200< pages< 500:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `d3d8e14efc344d5ba5b136ef97552739`, summary `Wrong Answer`, score `80`, vector `00101`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    """page=[]
    for s in book_data:
        for i in range(len(s)):
            page.append(s[i])
        print(page)
    return {s[0] for each in page if int(each) < 200}"""
    page = []
    result = []
    for i in range(len(book_data)):
        page.append(book_data[i][1])
    # print(page)
    # for p in page:
    #   if int(p) < 200:
    # for j in range(len(book_data)):
    #   if int(book_data[j][1]) < 200:


# ...
```

### Usually `get_medium_books` boundary bug (`<500`) plus additional later-helper mistakes (common multi-function partial pass)

- Cluster frequency: `9/447` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `5/212` (`2.4%`)
  - `ns_25t2_py21_2/24`: `4/235` (`1.7%`)
- Dominant private-case vectors: `00101` x9
- Score distribution (top): `40.0` x4, `80.0` x3, `60.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `e07935bb1e8f47938664011475e24509`, summary `Wrong Answer`, score `80`, vector `00101`

```python
def get_short_books(book_data:list) -> set:
    l = []
    for book in book_data:
        if(book[1]<200):
            l.append(book[0])
    s = set(l)
    return s

def get_medium_books(book_data:list) -> set:
    l = []
    for book in book_data:
        if(book[1]>=200 and book[1]<500):
            l.append(book[0])
    s = set(l)
    return s


def get_pages_by_isbn(book_data:list, isbn: str) -> int:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `39e4e21f1cc4477097f66cc9be27d9f5`, summary `Wrong Answer`, score `60`, vector `00101`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    l = []
    for item in book_data:
        if item[1] < 200:
            l.append(item[0])
    return set(l)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    l = []
    for item in book_data:
        if item[1] >= 200 and item[1] < 500:
            l.append(item[0])
    return set(l)


# ...
```

### Only one helper function appears correct; others are missing, type-mismatched (list vs set), or placeholder/hard-coded

- Cluster frequency: `9/447` (`2.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `5/212` (`2.4%`)
  - `ns_25t2_py21_2/24`: `4/235` (`1.7%`)
- Dominant private-case vectors: `00001` x9
- Score distribution (top): `40.0` x7, `20.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `47ce364bbf42408d94994eab9d21d1c7`, summary `Wrong Answer`, score `40`, vector `00001`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    l1 = []
    for i in range(len(book_data)):
        if (int(book_data[i][1])) < 200:
            l1.append(book_data[i][0])
    return l1


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...
    l2 = []
    for i in range(len(book_data)):
        if 200 <= (int(book_data[i][1])) <= 500:
            l2.append(book_data[i][0])
    return l2


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `c2a41f082c29407e86697c29b44d3981`, summary `Wrong Answer`, score `40`, vector `00001`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    page = 0
    check = False
    for book in book_data:
        if isbn == book[0]:
            page = int(book[1])
            check = True


# ...
```

### Returns lists from `get_short_books`/`get_medium_books` instead of the required ISBN sets

- Cluster frequency: `8/447` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `4/212` (`1.9%`)
  - `ns_25t2_py21_2/24`: `4/235` (`1.7%`)
- Dominant private-case vectors: `00000` x5, `00001` x3
- Score distribution (top): `0.0` x4, `60.0` x3, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `6c35790bfb504db496f63a6ae44891aa`, summary `Wrong Answer`, score `20`, vector `00000`

```python
def get_short_books(books):
    """return a list of books fewer than 200 pages."""
    return [book for book in books if book[1] < 200]


def get_medium_books(books):
    """return a list of books with pages between 200 and 500 inclusive."""
    return [book for book in books if 200 <= book[1] <= 500]


def get_pages_by_isbn(books, isbn):
    """return the no of books with the given isbn. return none if not found."""
    for books in books:
        if book[0] == isbn:
            return book[1]
    return none


def count_by_language(books):
    """return a dictionary with the count of books per language."""
    language_count = {}


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `398dd876a2924d419615dbcefb2492a0`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    return [isbn for isbn, pages in book_data if pages < 200]


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    return [isbn for isbn, marks in book_data if 200 < pages <= 500]


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...


def count_by_language(book_data: list) -> dict:
    """Returns a dict with the languages as keys and the number of books of that language as values."""


# ...
```

### Partial multi-function solution: `get_short_books` mostly works, but several other helpers are missing/incomplete or contain control-flow/indexing bugs

- Cluster frequency: `6/447` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `4/212` (`1.9%`)
  - `ns_25t2_py21_2/24`: `2/235` (`0.9%`)
- Dominant private-case vectors: `00100` x6
- Score distribution (top): `20.0` x5, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `d3074cc4c591441e85a3cb0f11e79032`, summary `Wrong Answer`, score `40`, vector `00100`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""

    Set = set()

    for i in book_data:
        if i[1] < 200:
            Set.add(i[0])

    return Set


def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""

    Set = set()

    for i in book_data:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `0a1a982c6438406bb5ccd2f9f87a2a9f`, summary `Wrong Answer`, score `20`, vector `00100`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""

    list = []
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            list.append(book_data[i][0])
    return set(list)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    list = []
    for i in range(len(book_data)):
        if 200 <= book - data[i][1] <= 500:
            list.append(book_data[i][0])
    return set(list)


# ...
```

### Runtime KeyError from direct dictionary counting/lookup without initializing language keys

- Cluster frequency: `6/447` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `3/212` (`1.4%`)
  - `ns_25t2_py21_2/24`: `3/235` (`1.3%`)
- Dominant private-case vectors: `00111` x6
- Score distribution (top): `80.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `9f07720ac9a2468bbabd9f45c1568640`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    a = len(book_data)
    x = []
    for i in range(a):
        b = book_data[i][1]
        c = book_data[i][0]
        if b < 200:
            x.append(c)
    return set(x)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    a = len(book_data)
    x = []
    for i in range(a):
        b = book_data[i][1]


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `3d07f55e5b1846b6b7b9f22c4fa656e3`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    isbn = []
    for book in book_data:
        if book[1] < 200:
            isbn.append(book[0])
    return set(sorted(isbn))


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    isbn = set()
    for book in book_data:
        if book[1] >= 200 and book[1] <= 500:
            isbn.add(book[0])
    return set(sorted(isbn))


# ...
```

### Runtime NameError

- Cluster frequency: `5/447` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `2/212` (`0.9%`)
  - `ns_25t2_py21_2/24`: `3/235` (`1.3%`)
- Dominant private-case vectors: `00000` x4, `00001` x1
- Score distribution (top): `0.0` x4, `40.0` x1
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `7b426e25a8734e40bd73dd7bba0f4e64`, summary `Runtime Error`, score `0`, vector `00000`

```python
print("{'978-1-56619-909-4', '978-1-60413-970-0', '978-3-16-148410-0'}")
data = [
    ("978-3-16-148410-0", 150, "English", "Thriller"),
    ("978-0-14-103620-2", 450, "Tamil", "Fantasy"),
    ("978-1-4028-9467-2", 200, "English", "Fiction"),
    ("978-0-393-04002-2", 350, "Hindi", "History"),
    ("978-0-06-112008-4", 300, "English", "Fiction"),
    ("978-1-60413-970-0", 175, "Bengali", "Mystery"),
    ("978-0-7432-7356-5", 420, "English", "Science Fiction"),
    ("978-1-56619-909-4", 100, "Tamil", "Romance"),
    ("978-1-4088-4994-7", 270, "Telugu", "Biography"),
    ("978-0-374-53243-2", 540, "English", "Thriller")
]
is_equal(
    get_medium_books(data),
    {
        '978-0-14-103620-2', '978-1-4028-9467-2', '978-0-393-04002-2', '978-0-06-112008-4', '978-1-4088-4994-7', '978-0-7432-7356-5'
    }
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `0ea006a053f44339ab969e531fc584fb`, summary `Runtime Error`, score `40`, vector `00001`

```python
from typing import List, Tuple, Optional, Dict

Book = Tuple[str, int, str, str]


def get_short_books(books):
    return (book for book in books if book[1] < 200)


def get_medium_books(books):
    return (book for book in books if 200 <= book[1] <= 500)


def get_pages_by_isbn(books, target_isbn):
    for book in books:
        if book[0] == target_isbn:
            return book[1]
    return None


# ...
```

### Runtime ValueError

- Cluster frequency: `5/447` (`1.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `3/212` (`1.4%`)
  - `ns_25t2_py21_2/24`: `2/235` (`0.9%`)
- Dominant private-case vectors: `00111` x4, `00000` x1
- Score distribution (top): `80.0` x4, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `4928a08cfb214ef59088b95e5b7869b7`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    return {b[0] for b in book_data if int(b[2]) < 200}


def get_medium_books(book_data: list) -> set:
    return {b[0] for b in book_data if 200 <= int(b[2]) < 500}


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    for b in book_data:
        if isinstance(b, dict):
            if b.get("isbn") == isbn:
                return int(b.get("pages", 0))
        else:
            if b[0] == isbn:
                return int(b[2])
    return 0


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `acbf01e71a6c41c49c22e08e11b62e98`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    """a=['isbn','pages','lang','genre']
    x=dict(zip(a,book_data))
    k=[]
    for item in x:
        if((item['pages'])<'200'):
            k.append(item)
            return k"""
    k = []
    for i in book_data:
        if (i[1]) < 200:
            k.append(i[0])
            k.sort()
            s = set(k)
    return s


# ...
```

### Uses membership (`if isbn in book`) instead of exact ISBN equality in `get_pages_by_isbn`

- Cluster frequency: `4/447` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `2/212` (`0.9%`)
  - `ns_25t2_py21_2/24`: `2/235` (`0.9%`)
- Dominant private-case vectors: `00111` x2, `00101` x1, `00110` x1
- Score distribution (top): `40.0` x2, `60.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `5a585ff3fa9e4f7b9beb2b3916084234`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    l = []
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            l.append(book_data[i][0])
    return set(l)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    l = []
    for i in range(len(book_data)):
        if 200 <= book_data[i][1] <= 500:
            l.append(book_data[i][0])
    return set(l)


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `4186797e5b6240bcbb3963a4a3444cec`, summary `Wrong Answer`, score `40`, vector `00101`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    c = len(book_data)
    d = []
    e = set(d)

    for i in range(c):
        if int(book_data[i][1]) < 200:
            d.append(book_data[i][0])
    return set(d)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


# ...
```

### Uses `range(len(book_data)-1)`, skipping the last book and causing off-by-one errors in one or more helpers

- Cluster frequency: `3/447` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `2/235` (`0.9%`)
- Dominant private-case vectors: `00100` x1, `00110` x1, `00111` x1
- Score distribution (top): `60.0` x2, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `86f36954c92a48209348faa5efae5864`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    book=[]
    for i in range(len(book_data)):
        if book_data[i][1]<200:
            book.append(book_data[i][0])
    return set(book)
def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    bookn=[]
    for i in range(len(book_data)):
        if 200<=book_data[i][1]<=500:
            bookn.append(book_data[i][0])

    return set(bookn)


def get_pages_by_isbn(book_data:list, isbn: str) -> int:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `a8e35142f3e748fc928548ba41f1b918`, summary `Wrong Answer`, score `60`, vector `00110`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    shorts = []
    for i in range(len(book_data)):
        if book_data[i][1] < 200:
            shorts.append(book_data[i][0])
    return set(shorts)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    medium = []
    for i in range(len(book_data)):
        if 200 <= book_data[i][1] and book_data[i][1] <= 500:
            medium.append(book_data[i][0])
    return set(medium)


# ...
```

### Does not define all five required functions (`get_short_books`, `get_medium_books`, `get_pages_by_isbn`, `count_by_language`, `total_pages_in_genre_lang`)

- Cluster frequency: `3/447` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `2/235` (`0.9%`)
- Dominant private-case vectors: `00000` x2, `00001` x1
- Score distribution (top): `0.0` x2, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `de5d5fee15ff43a58a12f2149cd4d58e`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def get_short_books(books):
    return[b for b in books if b[1] < 200]
def get_medium_books(books):
    return[b for b in books if 200 <= b[1] < 500]
def get_pages_by_isbn(books,isbn):
    for b in books:
        if b[0] == isbn:
            return b[1]
        return None
def count_by_lang(books):
    counts ={}
    for _, _, lang, _, in books:
        counts[lang] = counts.get(lang,0) +1
    return counts
def total_pages_in_genre_lang(books,genre,lang):
    return sum(p for _, p, l, g in books if g == genre and l == lang)
books_data =[
    ("ISBN001", 150, "english", "fiction"),
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `d38c7f0fae804038a643fceb4020f3e9`, summary `Wrong Answer`, score `60`, vector `00001`

```python
def get_short_short_books(books_data):
    return [book for book in books_data if book[1] < 200]


def get_medium_books(books_data):
    return [book for book in books_data if 200 <= book[1] <= 500]


def get_pages_by_isbn(books_data, isbn):
    for book in books_data:
        if book[0] == isbn:
            return book[1]
    return None


def count_by_language(books_data):
    lang_count = {}
    for book in books_data:
        lang = book[2]
        lang_count[lang] = lang_count.get(lang, 0) + 1
    return lang_count


def total_pages_in_genre_lang(books_data, genre, language):
    return sum(book[1] for book in books_data if book[3] == genre and book[2] == language)
```

### Runtime AttributeError

- Cluster frequency: `3/447` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `2/212` (`0.9%`)
  - `ns_25t2_py21_2/24`: `1/235` (`0.4%`)
- Dominant private-case vectors: `00111` x2, `00001` x1
- Score distribution (top): `80.0` x2, `20.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `2d1bef7d8cfb4c36b15e45b8846955c7`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    lst=[]
    for i in range(len(data)):
        if data[i][1]<200:
            lst.append(data[i][0])
    return set(lst)

def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    lst=[]
    for i in range(len(data)):
        if data[i][1]>=200 and data[i][1]<=500:
            lst.append(data[i][0])
    return set(lst)


def get_pages_by_isbn(book_data:list, isbn: str) -> int:
# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `da1961c8210b44a285673c7fec93aa96`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    leng = len(book_data)
    result = []
    for i in range(leng):
        a = int(book_data[i][1])
        if a < 200:
            result.append(book_data[i][0])
    result = set(result)
    return result


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    leng = len(book_data)
    result = []
    for i in range(leng):
        a = int(book_data[i][1])


# ...
```

### Runtime IndexError

- Cluster frequency: `2/447` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `1/235` (`0.4%`)
- Dominant private-case vectors: `00000` x1, `00111` x1
- Score distribution (top): `20.0` x1, `80.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `d579c4279c044410a18084421506e1c0`, summary `Runtime Error`, score `80`, vector `00111`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ISBN = set()
    for book in book_data:
        if book[1] < 200:
            ISBN.add(book[0])
    return ISBN


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ISBN = set()
    for book in book_data:
        if 200 <= book[1] <= 500:
            ISBN.add(book[0])
    return ISBN


# ...
```

- Variant `ns_25t2_py21_2/24`, Student ID `11e8f0621d3247f59b6b7ffebcb58280`, summary `Runtime Error`, score `20`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    return [book for book in data if book[4] < 200]


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    return [book for book in data if 200 < book[4] <= 500]


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    for book in data:
        if book[0] == isbn:
            return book[4]
        return None


# ...
```

### Uses external file I/O (`open`/`read_csv`) instead of operating on the provided `book_data` list parameter

- Cluster frequency: `1/447` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `0/212` (`0.0%`)
  - `ns_25t2_py21_2/24`: `1/235` (`0.4%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/24`, Student ID `3a799689719645f0b83b1137ec7f70d9`, summary `Runtime Error`, score `0`, vector `00000`

```python
with open("book_data", "r") as f:
    d = f.read()


def get_short_books(book_data: list) -> set:
    for i in range(d[1]):
        if i < 200:
            return book_data[0]
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...


# ...
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `1/447` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `0/212` (`0.0%`)
  - `ns_25t2_py21_2/24`: `1/235` (`0.4%`)
- Dominant private-case vectors: `00010` x1
- Score distribution (top): `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/24`, Student ID `66a7b1afdbf345bdbe757e0385665e93`, summary `Wrong Answer`, score `20`, vector `00010`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    short_books = []
    for each in book_data:
        if each[1] < 200:
            short_books.append(each[0])
    return short_books


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    medium_books = []
    for each in book_data:
        if 200 <= each[1] <= 500:
            medium_books.append(each[0])

    return set(medium_books)


# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/447` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `0/235` (`0.0%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `1691a5c1e7444db5b54c803439538174`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...


def count_by_language(book_data: list) -> dict:
    """Returns a dict with the languages as keys and the number of books of that language as values."""
    ...


# ...
```

### Runtime RecursionError

- Cluster frequency: `1/447` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `0/235` (`0.0%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `4094b15d683b4746ba4537a31a48e2e2`, summary `Runtime Error`, score `0`, vector `00000`

```python
def get_short_books(book_data: list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    return get_short_books(book_data)


def get_medium_books(book_data: list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    return get_medium_books(book_data)


def get_pages_by_isbn(book_data: list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    return get_pages_by_isbn(book_data)


def count_by_language(book_data: list) -> dict:
    """Returns a dict with the languages as keys and the number of books of that language as values."""
    return count_by_language(book_data)


# ...
```

### Uses unsupported imports/dependencies in the evaluator environment

- Cluster frequency: `1/447` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/19`: `1/212` (`0.5%`)
  - `ns_25t2_py21_2/24`: `0/235` (`0.0%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/19`, Student ID `ce3d3eecd6da491986999cc1ae5be46a`, summary `Runtime Error`, score `0`, vector `00000`

```python
from typing import List,Tupple,Dict,Optional,Set
Book=Tupple[str,int,str,str]
def get_short_books(book_data:list) -> set:
    """Returns the list of ISBNs of the books with pages less than 200."""
    ...
    return {isbn for isbn,pages,lang,genre in book_data if pages < 200}


def get_medium_books(book_data:list) -> set:
    """Returns the list of isbns of the books with pages Between 200 and 500(inclusive)."""
    ...
    return {isbn for isbn,pages,lang,genre in book_data if 200<= pages <=500}


def get_pages_by_isbn(book_data:list, isbn: str) -> int:
    """Returns the number of pages in the book given the ISBN."""
    ...
    for book_isbn,pages,lang,genre,in book_data:
# ...
```
