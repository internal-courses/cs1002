# OPPE Exam Administration Guide (Data-Informed)

This guide explains how OPPE exams appear to be created and administered, based on the 2025 dataset in this repo (`submissions/*.json`, `problems/*`, and derived `analysis/*.csv`).

It is written for a new exam administrator: what the naming means, how variants work, how students are distributed, what repeats across terms look like, and where the edge-cases are.

## 1) How to read the identifiers

The core exam key is `Namespace`.

Typical format:

- `ns_YYtT_pyXX[_V]`
- Example: `ns_25t3_py11` (Year 2025, Term 3, exam code `py11`)
- Example: `ns_25t3_py13_1` (same, with variant `_1`)

Interpretation:

- `YYtT` is academic window (`25t1`, `25t2`, `25t3`)
- `pyXX` is the base OPPE exam code in that term
- Optional suffix `_1`, `_2` indicates paper variant/set
- `ProblemID` is the question slot within that namespace

A student-question attempt is identified by:

- `(Namespace, ProblemID, StudentID)`

## 2) How many OPPE exams per term? Is it fixed?

From observed 2025 data (`final_scores.csv`):

| YearTerm | Base exams (dedup variants) | Namespaces (incl. variants) |
| -------- | --------------------------: | --------------------------: |
| 25t1     |                           8 |                          15 |
| 25t2     |                           7 |                          10 |
| 25t3     |                           8 |                          10 |

Observed exam sets:

- `25t1`: `py11, py12, py13, py14, py21, py22, py23, py_15_exe`
- `25t2`: `py11, py12, py13, py14, py21, py22, py23`
- `25t3`: `py11, py12, py13, py14, py21, py22, py23, py24`

Conclusion:

- Not a hard-and-fast fixed count in data.
- In 2025, terms had either 7 or 8 base exams.
- Exam codes can evolve (`py_15_exe` in 25t1, `py24` in 25t3).
- Practical rule of thumb: each term has a "first OPPE wave" (`py11`-`py14`) and a "second OPPE wave" (`py21`-`py23`, plus `py24` in 25t3).

### 2.1 Is "one from {py11..py14} + one from {py21..py23}" usually true?

Short answer: **common, but not universal**.

From student-term rows in `final_scores.csv`:

- `25t1`: 4,247 / 6,638 (63.98%) have exactly 1 `py1x` + 1 `py2x` (no extras)
- `25t2`: 2,932 / 5,197 (56.42%) have exactly 1 `py1x` + 1 `py2x`
- `25t3`: 1,584 / 5,055 (31.34%) have exactly 1 `py1x` + 1 `py2x`

Why lower in 25t3?

- `py24` exists in 25t3 and pulls part of the cohort into an additional `py2x`-family paper.
- Many students show only one side in `final_scores.csv`; this can be true non-assignment, but can also be missing private records for other assigned papers.

So for administration planning, model "1 from wave-1 + 1 from wave-2" as the dominant template for 25t1/25t2, and a weaker template in 25t3.

## 3) How many variants per exam?

Observed variant counts by term:

- `25t1`: 7 exams with 2 variants, 1 exam with 1 variant
- `25t2`: 3 exams with 2 variants, 4 exams with 1 variant
- `25t3`: 2 exams with 2 variants, 6 exams with 1 variant

So varianting is selective, not universal.

Examples:

- Two variants: `ns_25t3_py13_1`, `ns_25t3_py13_2`
- Single variant: `ns_25t3_py11` (no `_1/_2`)

## Timing and schedule intuition (from submission timestamps)

Using private-submission timestamps from `submissions/*.json` (`FileName` timestamp), the term structure looks like a two-wave schedule with a consistent gap:

- Wave 1: `py11`-`py14`
- Wave 2: `py21`-`py23` (and `py24` in 25t3)

Median first-touch gap between waves:

- `25t1`: 35.04 days
- `25t2`: 35.08 days
- `25t3`: 34.96 days

This ~35-day spacing is one of the clearest regularities in the dataset.

### Concrete calendar examples

Each term is split below into separate wave tables. Timing is formatted as `Fri 18 Jul 2025, 06:30` and all times are in **IST (UTC+05:30)**.
Wave-level and namespace-level timing uses **all activity rows** (`saved_code`, `test_run`, `submission`, etc.), not only final/private scores.
Namespace `start_time` and `end_time` come from a per-namespace 95% activity window (2.5% to 97.5%) rounded to 15-minute boundaries, generated in `analysis/schedule.csv`.

#### 25t1

Wave overlap summary:

| Wave | Namespaces | Namespace enrollments | Unique students in wave | Students in >1 namespace (same wave) | Overlap enrollments within wave | Students present in both Wave 1 and Wave 2 | 95% activity window (rounded to 15 min, IST) | Activity rows |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| Wave 1 (py11-py14) | 8 | 5565 | 5562 | 1 | 3 | 4290 | Wed 26 Feb 2025, 18:15 -> Sun 02 Mar 2025, 18:30 | 363045 |
| Wave 2 (py21+) | 6 | 5354 | 5354 | 0 | 0 | 4290 | Sun 06 Apr 2025, 09:30 -> Sun 06 Apr 2025, 18:30 | 363913 |
| Other | 1 | 110 | 110 | 0 | 0 | 4290 | Sat 08 Mar 2025, 18:45 -> Sat 08 Mar 2025, 21:15 | 6871 |

##### Wave 1 (py11-py14)

Total unique students in this wave: **5562**. Students overlapping across namespaces within this wave: **1** (overlap enrollments: **3**).
Students who appear in both Wave 1 and Wave 2 in 25t1: **4290**.
Rounded 95% activity window (all events, IST): **Wed 26 Feb 2025, 18:15 -> Sun 02 Mar 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t1_py11_1` | Wed 26 Feb 2025, 18:00 -> Wed 26 Feb 2025, 20:00 | 683 | Q2: Check is even or divisible by 5.<br>Q3: Deinterleave Even and Odd Indices in String.<br>Q4: Make dictionary from elements in index of lists.<br>Q6: Counts unique even and odd numbers.<br>Q7: Vowel count of words.<br>Q9: Student Score Filter.<br>Q10: Pattern Printing - W Pattern. |
| `ns_25t1_py11_2` | Thu 27 Feb 2025, 18:00 -> Thu 27 Feb 2025, 20:00 | 834 | Q2: Check If a number divides two other numbers.<br>Q3: Check String Rotation.<br>Q4: Find missing number in a range of numbers.<br>Q6: Merge two dictionaries and sum on conflicts.<br>Q7: Most Frequent Numbers form the input.<br>Q9: Employee Data Analysis.<br>Q10: Pattern Printing - Z Pattern. |
| `ns_25t1_py12_1` | Sun 02 Mar 2025, 09:30 -> Sun 02 Mar 2025, 11:45 | 677 | Q2: Check Even Number and Second Last Digit is Two.<br>Q3: Capitalize nth Character.<br>Q4: Merge and Remove Duplicates.<br>Q6: Replace Vowels with Next Alphabet.<br>Q7: Max Column sum and Max column sum index.<br>Q9: Analyze Sentences.<br>Q10: Pattern printing - Centered Triangle Of Zeroes. |
| `ns_25t1_py12_2` | Sun 02 Mar 2025, 09:30 -> Sun 02 Mar 2025, 11:45 | 555 | Q2: Check Even Number and Second Last Digit is Two.<br>Q3: Capitalize nth Character.<br>Q4: Merge and Remove Duplicates.<br>Q6: Replace Vowels with Next Alphabet.<br>Q7: Max Column sum and Max column sum index.<br>Q9: Analyze Sentences.<br>Q10: Pattern printing - Centered Triangle Of Zeroes. |
| `ns_25t1_py13_1` | Sun 02 Mar 2025, 13:30 -> Sun 02 Mar 2025, 15:30 | 506 | Q3: Check if a Triangle is Obtuse.<br>Q4: Markdown Image to HTML Image.<br>Q5: Remove n Elements from the Given Index.<br>Q7: First Non-Repeating Character in a String.<br>Q8: Compute Running Average Skipping NaN.<br>Q10: Time Series Analysis.<br>Q11: Pattern Printing - Diamond. |
| `ns_25t1_py13_2` | Sun 02 Mar 2025, 13:30 -> Sun 02 Mar 2025, 15:30 | 660 | Q3: Check if a Triangle is Obtuse.<br>Q4: Markdown Image to HTML Image.<br>Q5: Remove n Elements from the Given Index.<br>Q7: First Non-Repeating Character in a String.<br>Q8: Compute Running Average Skipping NaN.<br>Q10: Time Series Analysis.<br>Q11: Pattern Printing - Diamond. |
| `ns_25t1_py14_1` | Sun 02 Mar 2025, 16:30 -> Sun 02 Mar 2025, 18:30 | 905 | Q3: Check if 2D Vectors are Orthogonal.<br>Q4: Get Next Roll Number.<br>Q5: Check If a String has No Vowels in Even Indices.<br>Q7: Find Minimum Card of a Specific Suit in Hand.<br>Q8: Score Objective Questions.<br>Q10: Key Stroke Analysis.<br>Q11: Pattern Printing - Hexagon. |
| `ns_25t1_py14_2` | Sun 02 Mar 2025, 16:30 -> Sun 02 Mar 2025, 18:30 | 745 | Q3: Check if 2D Vectors are Orthogonal.<br>Q4: Get Next Roll Number.<br>Q5: Check If a String has No Vowels in Even Indices.<br>Q7: Find Minimum Card of a Specific Suit in Hand.<br>Q8: Score Objective Questions.<br>Q10: Key Stroke Analysis.<br>Q11: Pattern Printing - Hexagon. |

##### Wave 2 (py21+)

Total unique students in this wave: **5354**. Students overlapping across namespaces within this wave: **0** (overlap enrollments: **0**).
Students who appear in both Wave 1 and Wave 2 in 25t1: **4290**.
Rounded 95% activity window (all events, IST): **Sun 06 Apr 2025, 09:30 -> Sun 06 Apr 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t1_py21_1` | Sun 06 Apr 2025, 09:15 -> Sun 06 Apr 2025, 11:30 | 829 | Q5: Check if Either of Two Numbers is a Multiple of the Other.<br>Q6: Check if a String Starts and Ends with the Same Vowel (Case Insensitive).<br>Q7: Rearrange Even Length Tuple by Placing Middle Elements at Ends.<br>Q9: Count Strings with Length Divisible by Either 3 or 5.<br>Q10: Thresholding a 2D Array and Printing with * and @.<br>Q12: Railway Ticket Booking Analysis.<br>Q13: String Rearrangement. |
| `ns_25t1_py21_2` | Sun 06 Apr 2025, 09:15 -> Sun 06 Apr 2025, 11:30 | 955 | Q5: Check if Either of Two Numbers is a Multiple of the Other.<br>Q6: Check if a String Starts and Ends with the Same Vowel (Case Insensitive).<br>Q7: Rearrange Even Length Tuple by Placing Middle Elements at Ends.<br>Q9: Count Strings with Length Divisible by Either 3 or 5.<br>Q10: Thresholding a 2D Array and Printing with * and @.<br>Q12: Railway Ticket Booking Analysis.<br>Q13: String Rearrangement. |
| `ns_25t1_py22_1` | Sun 06 Apr 2025, 13:30 -> Sun 06 Apr 2025, 15:45 | 564 | Q5: Middle element from list.<br>Q6: Shuffle a Three Word Sentence.<br>Q7: Check if both numbers have the same sign.<br>Q9: Check Palindrome - Advanced.<br>Q10: Abbreviate Initials And Sort.<br>Q12: Employee Task Analysis.<br>Q13: Simple Stemmer. |
| `ns_25t1_py22_2` | Sun 06 Apr 2025, 13:30 -> Sun 06 Apr 2025, 15:45 | 1015 | Q5: Middle element from list.<br>Q6: Shuffle a Three Word Sentence.<br>Q7: Check if both numbers have the same sign.<br>Q9: Check Palindrome - Advanced.<br>Q10: Abbreviate Initials And Sort.<br>Q12: Employee Task Analysis.<br>Q13: Simple Stemmer. |
| `ns_25t1_py23_1` | Sun 06 Apr 2025, 16:15 -> Sun 06 Apr 2025, 18:30 | 860 | Q5: Extract Border Elements from a List.<br>Q6: Absolute Time Difference Between Two Times.<br>Q7: Transfer amount.<br>Q9: Words with Consecutive Identical Letters.<br>Q10: Hand Cricket Match Runs.<br>Q12: Polygon Analysis.<br>Q13: Total Size of Image Files. |
| `ns_25t1_py23_2` | Sun 06 Apr 2025, 16:15 -> Sun 06 Apr 2025, 18:30 | 1131 | Q5: Extract Border Elements from a List.<br>Q6: Absolute Time Difference Between Two Times.<br>Q7: Transfer amount.<br>Q9: Words with Consecutive Identical Letters.<br>Q10: Hand Cricket Match Runs.<br>Q12: Polygon Analysis.<br>Q13: Total Size of Image Files. |

##### Other

Total unique students in this wave: **110**. Students overlapping across namespaces within this wave: **0** (overlap enrollments: **0**).
Rounded 95% activity window (all events, IST): **Sat 08 Mar 2025, 18:45 -> Sat 08 Mar 2025, 21:15**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t1_py_15_exe` | Sat 08 Mar 2025, 18:45 -> Sat 08 Mar 2025, 21:15 | 110 | Q5: Check is even or divisible by 5.<br>Q6: Deinterleave Even and Odd Indices in String.<br>Q7: Make dictionary from elements in index of lists.<br>Q9: Counts unique even and odd numbers.<br>Q10: Vowel count of words.<br>Q12: Student Score Filter.<br>Q13: Pattern Printing - W Pattern.<br>Q18: Calculate Scholarship.<br>Q19: Find LCM of Two Positive Integers.<br>Q20: Fizz-Buzz.<br>Q22: Reverse the digits of a number.<br>Q23: Find the closest prime number.<br>Q24: Count the number of Leap years in a given range A leap year is a year that: ● is divi. |

#### 25t2

Wave overlap summary:

| Wave | Namespaces | Namespace enrollments | Unique students in wave | Students in >1 namespace (same wave) | Overlap enrollments within wave | Students present in both Wave 1 and Wave 2 | 95% activity window (rounded to 15 min, IST) | Activity rows |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| Wave 1 (py11-py14) | 5 | 4288 | 4286 | 1 | 2 | 2933 | Sat 19 Jul 2025, 10:15 -> Sun 20 Jul 2025, 18:30 | 338601 |
| Wave 2 (py21+) | 5 | 3847 | 3844 | 2 | 3 | 2933 | Sun 24 Aug 2025, 09:30 -> Sun 24 Aug 2025, 18:30 | 334539 |

##### Wave 1 (py11-py14)

Total unique students in this wave: **4286**. Students overlapping across namespaces within this wave: **1** (overlap enrollments: **2**).
Students who appear in both Wave 1 and Wave 2 in 25t2: **2933**.
Rounded 95% activity window (all events, IST): **Sat 19 Jul 2025, 10:15 -> Sun 20 Jul 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t2_py11_1` | Sat 19 Jul 2025, 10:00 -> Sat 19 Jul 2025, 12:00 | 653 | Q5: Describe Number Based on Divisibility.<br>Q6: Card to Value Tuple.<br>Q7: Rotate Even Indices.<br>Q9: Unique Sum Pairs.<br>Q10: Replace Consonants with Hash.<br>Q12: Text Frequency Analysis.<br>Q13: Draw Arrow Trail from Movement Deltas. |
| `ns_25t2_py12_1` | Sat 19 Jul 2025, 13:15 -> Sat 19 Jul 2025, 15:30 | 714 | Q5: Check is even or divisible by 5.<br>Q6: Deinterleave Even and Odd Indices in String.<br>Q7: Make dictionary from elements in index of lists.<br>Q9: Counts unique even and odd numbers.<br>Q10: Vowel count of words.<br>Q12: Student Score Filter.<br>Q13: Pattern Printing - W Pattern. |
| `ns_25t2_py13_1` | Sun 20 Jul 2025, 09:30 -> Sun 20 Jul 2025, 11:30 | 910 | Q5: Check If a Number is a Decreasing 4-Digit Number.<br>Q6: Parse Equation and Solve for x.<br>Q7: Divide Number Into Almost Equal Parts.<br>Q9: Compute Polynomial Value.<br>Q10: Update Todo List Based on Given Indices.<br>Q12: Batsman Performance Analysis.<br>Q13: Horizontal Bar Chart. |
| `ns_25t2_py13_2` | Sun 20 Jul 2025, 13:30 -> Sun 20 Jul 2025, 15:30 | 964 | Q5: Double First and Last Elements in a List.<br>Q6: Extract Email Username.<br>Q7: Four Digit Shuffle.<br>Q9: Upper Case Even Index Words.<br>Q10: Print Pieces Moved from Chess Notation string.<br>Q12: YouTube Video Engagement Analysis.<br>Q13: Format Tic-Tac-Toe Board. |
| `ns_25t2_py14_1` | Sun 20 Jul 2025, 16:30 -> Sun 20 Jul 2025, 19:00 | 1047 | Q5: Position of a Point Relative to a Line.<br>Q6: Expand Sum of Products.<br>Q7: Repeat Second Half of a Tuple.<br>Q9: Convert Excel Column Name to 1-Based Index.<br>Q10: Reverse Vowel Order in a String.<br>Q12: Chess Game Analysis.<br>Q13: Visualize Pattern Lock. |

##### Wave 2 (py21+)

Total unique students in this wave: **3844**. Students overlapping across namespaces within this wave: **2** (overlap enrollments: **3**).
Students who appear in both Wave 1 and Wave 2 in 25t2: **2933**.
Rounded 95% activity window (all events, IST): **Sun 24 Aug 2025, 09:30 -> Sun 24 Aug 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t2_py21_1` | Sun 24 Aug 2025, 09:15 -> Sun 24 Aug 2025, 11:30 | 783 | Q14: Compute Electricity Bill.<br>Q15: is_reverse_combined_palindrome.<br>Q16: Pangram Check.<br>Q17: Check for Arithmetic Progression.<br>Q18: Rotate Matrix Clockwise 90 degree.<br>Q19: Book Data Analysis.<br>Q20: File Content Zig-Zag Shift. |
| `ns_25t2_py21_2` | Sun 24 Aug 2025, 09:15 -> Sun 24 Aug 2025, 11:30 | 791 | Q14: Compute Electricity Bill.<br>Q16: is_reverse_combined_palindrome.<br>Q18: Pangram Check.<br>Q20: Check for Arithmetic Progression.<br>Q22: Rotate Matrix Clockwise 90 degree.<br>Q24: Book Data Analysis.<br>Q26: File Content Zig-Zag Shift. |
| `ns_25t2_py22_1` | Sun 24 Aug 2025, 13:15 -> Sun 24 Aug 2025, 15:30 | 1033 | Q14: Check If Multiple of 5 Not 3.<br>Q15: Check For Greeting Prefix.<br>Q16: Combine First and Last Two Chars of a string.<br>Q17: Reversed Squares of List Elements.<br>Q18: Make Word Using Last Characters of Words with Minimum Length and Starting Character.<br>Q19: Sales Data Analysis.<br>Q20: Uppercase Every k-th Vowel and lower case other vowels in a File. |
| `ns_25t2_py23_1` | Sun 24 Aug 2025, 16:15 -> Sun 24 Aug 2025, 18:30 | 645 | Q14: Three-Digit Number with Digit-Sum Divisible by k.<br>Q15: Remove Second and Second-Last Character from String.<br>Q16: Add average key with absolute difference value (in-place).<br>Q17: Count Words with Matching First/Last but Different Second/Second-Last Letters.<br>Q18: Remainder Grouping Dictionary.<br>Q19: Book Reading List Data Analysis.<br>Q20: Column Totals in a Markdown Table (Numeric Columns Only). |
| `ns_25t2_py23_2` | Sun 24 Aug 2025, 16:15 -> Sun 24 Aug 2025, 18:30 | 595 | Q14: Three-Digit Number with Digit-Sum Divisible by k.<br>Q15: Remove Second and Second-Last Character from String.<br>Q16: Add average key with absolute difference value (in-place).<br>Q17: Count Words with Matching First/Last but Different Second/Second-Last Letters.<br>Q18: Remainder Grouping Dictionary.<br>Q19: Book Reading List Data Analysis.<br>Q20: Column Totals in a Markdown Table (Numeric Columns Only). |

#### 25t3

Wave overlap summary:

| Wave | Namespaces | Namespace enrollments | Unique students in wave | Students in >1 namespace (same wave) | Overlap enrollments within wave | Students present in both Wave 1 and Wave 2 | 95% activity window (rounded to 15 min, IST) | Activity rows |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| Wave 1 (py11-py14) | 6 | 4127 | 4126 | 1 | 1 | 2682 | Sat 08 Nov 2025, 18:15 -> Sun 09 Nov 2025, 18:30 | 344856 |
| Wave 2 (py21+) | 4 | 3611 | 3611 | 0 | 0 | 2682 | Sat 13 Dec 2025, 14:45 -> Sun 14 Dec 2025, 18:30 | 305833 |

##### Wave 1 (py11-py14)

Total unique students in this wave: **4126**. Students overlapping across namespaces within this wave: **1** (overlap enrollments: **1**).
Students who appear in both Wave 1 and Wave 2 in 25t3: **2682**.
Rounded 95% activity window (all events, IST): **Sat 08 Nov 2025, 18:15 -> Sun 09 Nov 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t3_py11` | Sat 08 Nov 2025, 18:00 -> Sat 08 Nov 2025, 21:00 | 712 | Q7: Check if a String Starts and Ends with the Same Vowel (Case Insensitive).<br>Q8: Compare Last Digits.<br>Q9: Move Even Indices to End (Reversed).<br>Q10: Remove Duplicate Characters from String.<br>Q11: Print Average of Every Two Non-Empty Values Until Stop.<br>Q12: People Connection Analysis.<br>Q13: Create Slug from String. |
| `ns_25t3_py12` | Sun 09 Nov 2025, 09:30 -> Sun 09 Nov 2025, 11:30 | 387 | Q5: Middle element from list.<br>Q6: Get First and Last Characters Sorted.<br>Q7: Average of Negative Even Numbers.<br>Q8: Leaderboard List by Scores.<br>Q9: Word Sandwich.<br>Q10: Hospital Patient Analytics.<br>Q11: Number Line Marker. |
| `ns_25t3_py13_2` | Sun 09 Nov 2025, 13:15 -> Sun 09 Nov 2025, 15:30 | 765 | Q7: Shuffle a Three Word Sentence.<br>Q8: Number of Unique letters present in exactly one of the two strings.<br>Q9: Double if Even Else Square.<br>Q10: Find Characters Appearing More Than Once.<br>Q11: Word Filter by Criteria.<br>Q12: Count Word Types by Length and Palindrome Property.<br>Q13: Step Triangle Pattern. |
| `ns_25t3_py13_1` | Sun 09 Nov 2025, 13:30 -> Sun 09 Nov 2025, 15:30 | 780 | Q7: Shuffle a Three Word Sentence.<br>Q8: Number of Unique letters present in exactly one of the two strings.<br>Q9: Double if Even Else Square.<br>Q10: Find Characters Appearing More Than Once.<br>Q11: Count Word Types by Length and Palindrome Property.<br>Q12: Word Filter by Criteria.<br>Q13: Step Triangle Pattern. |
| `ns_25t3_py14_2` | Sun 09 Nov 2025, 16:15 -> Sun 09 Nov 2025, 18:30 | 757 | Q7: Check Divisibility by Last Two Digits.<br>Q8: Bold Nth Character.<br>Q9: Separate Outer Characters.<br>Q10: Replace Spaces with Index.<br>Q11: Add Pairs with Carry Over Above 100.<br>Q12: Sales Records Analysis.<br>Q13: Sum Numbers Inside Square Brackets. |
| `ns_25t3_py14_1` | Sun 09 Nov 2025, 16:30 -> Sun 09 Nov 2025, 18:30 | 726 | Q7: Check Divisibility by Last Two Digits.<br>Q8: Bold Nth Character.<br>Q9: Separate Outer Characters.<br>Q10: Replace Spaces with Index.<br>Q11: Sales Records Analysis.<br>Q12: Sum Numbers Inside Square Brackets.<br>Q13: Add Pairs with Carry Over Above 100. |

##### Wave 2 (py21+)

Total unique students in this wave: **3611**. Students overlapping across namespaces within this wave: **0** (overlap enrollments: **0**).
Students who appear in both Wave 1 and Wave 2 in 25t3: **2682**.
Rounded 95% activity window (all events, IST): **Sat 13 Dec 2025, 14:45 -> Sun 14 Dec 2025, 18:30**.

| Namespace | Activity timing window (all events, 95% rounded, IST) | Students | Questions included (concise cues) |
|---|---|---:|---|
| `ns_25t3_py21` | Sat 13 Dec 2025, 14:30 -> Sat 13 Dec 2025, 16:30 | 598 | Q5: Sum of Two Halves of an Even-Digit Number.<br>Q6: Reverse Directional Connection.<br>Q7: Deinterleave Even and Odd Indices in String.<br>Q9: Pairwise Average of Lists.<br>Q10: Average of Valid Positive Integers.<br>Q12: Department Project Analysis.<br>Q13: Format Pairs of Integers as Product of Fractions. |
| `ns_25t3_py22` | Sun 14 Dec 2025, 09:15 -> Sun 14 Dec 2025, 11:30 | 529 | Q5: Swap Diagonal Characters in a 2‑Line String.<br>Q6: Create Username from First Name and User ID.<br>Q7: Square the last three numbers in a list.<br>Q9: Mirror Merge - Advanced.<br>Q10: Bank Account Number Generator.<br>Q12: University Course Enrollment Analysis.<br>Q13: Tap Code Decoder. |
| `ns_25t3_py23` | Sun 14 Dec 2025, 12:45 -> Sun 14 Dec 2025, 15:00 | 999 | Q5: Swap Signs of Two Integers.<br>Q6: Check First and Last Element are Same Integer (Type-Insensitive).<br>Q7: Absolute difference between sum and sum of the squares.<br>Q9: Spy Number - Advanced.<br>Q10: Identify Eligible Voters.<br>Q12: Ride Booking Data Analysis.<br>Q13: Fill Blanks with Words from a List. |
| `ns_25t3_py24_1` | Sun 14 Dec 2025, 16:15 -> Sun 14 Dec 2025, 18:30 | 1485 | Q5: Mask all characters of a password except the first two and last two.<br>Q6: Find the length of concatenated dictionary values.<br>Q7: Middle element from list.<br>Q9: Count Strings With More Vowels Than Consonants.<br>Q10: Sum of Digit Sums from Words.<br>Q12: Job Scheduling Analysis.<br>Q13: Rotate a Stacked‑Item Matrix 90° Clockwise. |


Scheduling intuition:

- OPPEs are largely administered in weekend-centered blocks (Fri/Sat/Sun).
- Each base exam typically has a short active window (about 1-3 days of first-touch activity).
- Terms appear to run two exam cycles separated by ~5 weeks.

Counter-example/edge-case notes:

- Some exams open earlier than the main cluster (example: `25t1 py11` starts on Tue, Feb 25).
- Some exams are nearly single-day windows (`25t3 py11`, `25t1 py12`).
- Timestamp windows are behavior-derived (from submissions), not official published timetables; they reflect when students actually submitted private runs.

## 4) How questions are distributed

### 4.1 Per namespace question count

- Almost every namespace has **7 questions**.
- Strong outlier: `ns_25t1_py_15_exe` has **13 questions**.

### 4.2 ProblemID patterns

Problem IDs are not globally uniform across all exams.

Examples:

- `ns_25t1_py11_*`: `2,3,4,6,7,9,10`
- `ns_25t3_py13_*`: `7,8,9,10,11,12,13`
- `ns_25t2_py21_1`: `14,15,16,17,18,19,20`
- `ns_25t2_py21_2`: `14,16,18,20,22,24,26` (even-only pattern)

Edge case:

- `ns_25t2_py21` is the main mismatch between `_1` and `_2` ProblemID sets.
- Most other `_1/_2` pairs share the same 7 ProblemIDs.

### 4.3 Are `_1` and `_2` actually different questions?

Yes. Same base exam + same ProblemID can still be different content across variants.

Concrete example:

- `problems/ns_25t3_py13_1/11.json`: "Count Word Types by Length and Palindrome Property"
- `problems/ns_25t3_py13_2/11.json`: "Word Filter by Criteria"

So in operations, treat variant namespaces as separate papers, not cosmetic aliases.

## 5) How students are assigned to variants

Empirically, students are assigned to one variant per base exam, almost always exclusively.

Evidence:

- For each base exam with `_1/_2`, student split is usually near-balanced.
- Examples:
  - `ns_25t2_py21`: 783 (`_1`) vs 791 (`_2`) (~50/50)
  - `ns_25t3_py13`: 780 (`_1`) vs 765 (`_2`) (~50/50)
  - `ns_25t1_py22`: 564 (`_1`) vs 1015 (`_2`) (skewed, still exclusive)
- Only **2 student+base-exam cases** appear in both variants:
  - `77d4f519a8bf4073bb057499d465f629` in `ns_25t2_py23_1` and `_2`
  - `f14645d55837451d94a7afc5615ca1b7` in `ns_25t1_py14_1` and `_2`

Likely assignment mechanism (inference):

- Cohort or section-level sharding to variants
- Rare dual-variant rows likely retake/migration/admin/testing artifacts

## 6) How many students per term, and do students repeat?

Unique students observed in each term:

- `25t1`: 6,638
- `25t2`: 5,197
- `25t3`: 5,055
- Total unique across all terms: 13,299

Overlap (same student appearing in multiple terms):

- `t1 ∩ t2`: 2,010 (30.28% of t1; 38.68% of t2)
- `t2 ∩ t3`: 1,367 (26.30% of t2; 27.04% of t3)
- `t1 ∩ t3`: 717 (10.80% of t1; 14.18% of t3)
- All three terms: 503 students (3.78% of all students)

Composition of the full student population:

- Only t1: 4,414 (33.19%)
- Only t2: 2,323 (17.47%)
- Only t3: 3,474 (26.12%)
- t1+t2 only: 1,507 (11.33%)
- t1+t3 only: 214 (1.61%)
- t2+t3 only: 864 (6.50%)
- all three: 503 (3.78%)

Pattern intuition:

- Strong adjacent-term continuity (`t1->t2`, `t2->t3`)
- Much weaker `t1->t3` direct overlap (expected for cohort progression and churn)

## 7) Important caveat about what these rows mean

`analysis/final_scores.csv` includes **only latest private records that exist**.

So absence of `(student, namespace, problem)` can mean:

- student was not assigned that paper, or
- student was assigned but has no private submission for that question, or
- ingestion/administrative filtering omitted it

This is why some students have non-7 counts inside a namespace (example: student `f14645d...` has 5 or 6 rows in some namespaces). Do not equate row presence with formal assignment without enrollment/allocation data.

## 8) Practical administration model (recommended)

Treat this as the operational blueprint your data currently reflects.

### Step A: Create papers

- For each term, define base exam codes (`py11`, `py12`, etc.).
- Decide which need anti-collusion variants (`_1`, `_2`).
- Keep a strict namespace naming policy (`ns_YYtT_pyXX[_V]`).

### Step B: Build question banks

- Publish question JSONs under `problems/<namespace>/<ProblemID>.json`.
- Keep per-namespace question count consistent (usually 7).
- Avoid accidental ID drift across variants unless deliberate.

### Step C: Assign students

- Assign by cohort/section to variants.
- Aim balanced load per variant where possible.
- Track assignment table explicitly (not derivable perfectly from submissions).

### Step D: Capture attempts

- Multiple attempts happen (observed avg private attempts per student-question: 2.73; max 138).
- Persist raw attempts (`saved_code`, `test_run`, `submission`, public/private).

### Step E: Produce final marks

- Use latest private per `(Namespace, ProblemID, StudentID)` for final question score.
- Aggregate for term reports from that final table.

## 9) Edge-cases to monitor every term

- Namespace format exceptions (`ns_25t1_py_15_exe` style)
- Variant ProblemID mismatch (`ns_25t2_py21_1` vs `_2` pattern)
- Students appearing in both variants of same base exam
- Very high-activity IDs (possible admin/test accounts), e.g. `f14645d55837451d94a7afc5615ca1b7` appears in 13 namespaces and 77 final rows
- Terms with 7 vs 8 exams (not fixed policy in observed data)

## 10) Administrator checklist

Before releasing a term:

- Validate namespace grammar and uniqueness
- Validate question counts per namespace
- Validate intended variant count per base exam
- Validate ProblemID alignment policy across variants
- Freeze assignment roster (student -> namespace variant)

After exam closes:

- Generate latest-private final rows
- Audit dual-variant student anomalies
- Publish termwise score + theoretical max with clear caveats

---

## Data sources used for this guide

- `analysis/final_scores.csv`
- `analysis/final_scores_termwise.csv`
- `analysis/scores.csv`
- `problems/*/*.json`

All statistics in this guide are computed from those files in this repository snapshot.
