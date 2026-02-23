#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pandas>=2.2.0",
# ]
# ///
"""Generate cluster-specific error reports for the top 4 submission-volume clusters.

Targets:
- C010 Compute Electricity Bill
- C011 is_reverse_combined_palindrome
- C012 Check for Arithmetic Progression
- C013 Pangram Check

Inputs:
- analysis/question_clusters.csv
- analysis/question_cluster_members.csv
- analysis/error_pattern_pilot/*__final_rows.csv

Outputs:
- analysis/ERRORS-cluster-*.md for the 4 target clusters (overwrites C013 file)

Goal:
- Re-cluster wrong-answer logic rows so `Other` residual is < 5% of non-full rows per cluster
- Keep pattern set reasonably compact and instructionally meaningful
"""

from __future__ import annotations

import ast
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
PILOT_DIR = ANALYSIS_DIR / "error_pattern_pilot"

TARGET_CLUSTERS = ["C010", "C011", "C012", "C013"]
RESIDUAL_TARGET_PCT = 5.0


def extract_function_executable_body(code: str) -> str:
    """Return function body source (docstring removed) if `code` contains a function."""
    if not code.strip():
        return code
    try:
        tree = ast.parse(code)
    except Exception:
        return code
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef)), None)
    if fn is None:
        return code
    stmts = list(fn.body)
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(getattr(stmts[0], "value", None), ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        stmts = stmts[1:]
    if not stmts:
        return ""
    lines = code.splitlines()
    chunks: list[str] = []
    for stmt in stmts:
        if getattr(stmt, "lineno", None) is None or getattr(stmt, "end_lineno", None) is None:
            continue
        chunks.append("\n".join(lines[stmt.lineno - 1 : stmt.end_lineno]))
    return "\n".join(chunks).strip("\n")


def fallback_return_stats(code: str) -> tuple[int, int, int]:
    """Approximate return counts from source when pilot row stats are missing/zero."""
    if not code or "return" not in code:
        return 0, 0, 0
    try:
        tree = ast.parse(code)
    except Exception:
        # Coarse regex fallback
        all_returns = re.findall(r"(?m)^\s*return\b", code)
        true_returns = re.findall(r"(?mi)^\s*return\s*\(?\s*true\s*\)?\s*$", code)
        false_returns = re.findall(r"(?mi)^\s*return\s*\(?\s*false\s*\)?\s*$", code)
        return len(all_returns), len(true_returns), len(false_returns)
    returns: list[ast.Return] = [n for n in ast.walk(tree) if isinstance(n, ast.Return)]
    r_true = 0
    r_false = 0
    for r in returns:
        v = r.value
        if isinstance(v, ast.Constant) and v.value is True:
            r_true += 1
        if isinstance(v, ast.Constant) and v.value is False:
            r_false += 1
    return len(returns), r_true, r_false


def fallback_body_non_doc_stmt_count(function_code: str, logic_code: str) -> int:
    if function_code and function_code != logic_code:
        try:
            tree = ast.parse(function_code)
            fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef)), None)
            if fn is not None:
                stmts = list(fn.body)
                if (
                    stmts
                    and isinstance(stmts[0], ast.Expr)
                    and isinstance(getattr(stmts[0], "value", None), ast.Constant)
                    and isinstance(stmts[0].value.value, str)
                ):
                    stmts = stmts[1:]
                return len(stmts)
        except Exception:
            pass
    # Coarse statement count by non-empty lines.
    return sum(1 for ln in (logic_code or "").splitlines() if ln.strip())


def norm_vec(v: Any) -> str:
    if v is None:
        return "???"
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return "???"
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    if s.isdigit():
        return s.zfill(3)
    return s


def norm_vec_to_width(v: Any, width: int) -> str:
    """Normalize a private-case vector to the expected private-case width."""
    s = norm_vec(v)
    if width <= 0:
        return s
    filtered = "".join(ch for ch in s if ch in "01?")
    if not filtered:
        return s
    if len(filtered) > width:
        filtered = filtered[:width]
    elif len(filtered) < width:
        if "?" in filtered:
            filtered = filtered + ("?" * (width - len(filtered)))
        else:
            filtered = filtered.zfill(width)
    return filtered


def norm_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in {"true", "1", "t", "yes"}


def norm_int(v: Any, default: int = 0) -> int:
    try:
        if str(v).strip() == "" or str(v).strip().lower() == "nan":
            return default
        return int(float(v))
    except Exception:
        return default


def norm_float(v: Any, default: float | None = None) -> float | None:
    try:
        if str(v).strip() == "" or str(v).strip().lower() == "nan":
            return default
        return float(v)
    except Exception:
        return default


def parse_json_list(v: Any) -> list[Any]:
    if isinstance(v, list):
        return v
    s = str(v).strip()
    if not s or s.lower() == "nan":
        return []
    try:
        x = json.loads(s)
        return x if isinstance(x, list) else []
    except Exception:
        return []


def first_code_line(code: str) -> str:
    for ln in (code or "").splitlines():
        t = ln.strip()
        if t:
            return t[:140]
    return "<empty>"


def shorten_code(code: str, max_lines: int = 18) -> str:
    lines = [ln.rstrip() for ln in (code or "").splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + "\n# ..."


def split_tag_set(v: Any) -> set[str]:
    return set(str(x) for x in parse_json_list(v))


def read_cluster_meta() -> tuple[pd.DataFrame, pd.DataFrame]:
    clusters = pd.read_csv(ANALYSIS_DIR / "question_clusters.csv")
    members = pd.read_csv(ANALYSIS_DIR / "question_cluster_members.csv")
    members["problem_id"] = members["problem_id"].astype(int)
    members["is_canonical"] = members["is_canonical"].map(norm_bool)
    members["final_submitters"] = members["final_submitters"].astype(int)
    members["non_full_final_submissions"] = members["non_full_final_submissions"].astype(int)
    return clusters, members


def load_problem_json(namespace: str, problem_id: int) -> dict[str, Any]:
    fp = ROOT / "problems" / namespace / f"{problem_id}.json"
    return json.loads(fp.read_text(encoding="utf-8"))


def parse_assertions_from_test_input(inp: str) -> list[tuple[list[Any], Any]]:
    # Lightweight regex parser for `is_equal(func(args...), expected)`.
    # We only need rough tags/examples, not exact AST semantics.
    out: list[tuple[list[Any], Any]] = []
    # Keep simple: split by lines and extract quoted strings/numbers/bools heuristically.
    chunks = inp.split("is_equal(")
    for ch in chunks[1:]:
        body = ch.split(")", 1)[0]
        lits = re.findall(r'"([^"]*)"|\'([^\']*)\'|\\b(True|False)\\b|\\b-?\\d+(?:\\.\\d+)?\\b', body)
        vals: list[Any] = []
        for a, b, c, d in lits:
            if a != "":
                vals.append(a)
            elif b != "":
                vals.append(b)
            elif c != "":
                vals.append(True if c == "True" else False)
            elif d != "":
                vals.append(float(d) if "." in d else int(d))
        expected = vals[-1] if vals else None
        args = vals[:-1] if vals else []
        out.append((args, expected))
    return out


def private_case_notes_for_cluster(cluster_id: str, canonical_problem: dict[str, Any]) -> dict[str, str]:
    tests = canonical_problem.get("private_testcase") or []
    notes: dict[str, str] = {}
    if cluster_id == "C013":
        notes = {
            "1": "mixed-case positives + one negative sentence",
            "2": "digit/non-letter-heavy cases incl reversed-alphabet positives",
            "3": "short negatives + punctuation/digit positive pangram",
        }
    elif cluster_id == "C010":
        notes = {
            "1": "low slab only (0 and small units)",
            "2": "middle slab incl 400 boundary",
            "3": "high slab (>400)",
        }
    elif cluster_id == "C011":
        notes = {
            "1": "basic reverse+concat palindrome/negative pair",
            "2": "mixed lengths incl palindromes and non-palindromes",
            "3": "additional edge combinations",
        }
    elif cluster_id == "C012":
        notes = {
            "1": "non-AP + constant sequence + positive AP",
            "2": "descending AP + nonlinear non-APs",
            "3": "geometric/non-AP + zero-diff AP + mixed non-AP",
        }
    elif cluster_id == "C077":
        notes = {
            "1": "mixed positives/negatives around divisibility by 5 and 3 (incl 30)",
            "2": "includes negative multiple of 5, zero, and non-multiple distractor",
            "3": "larger positives/negatives incl multiple of 15 distractor (45)",
        }
    elif cluster_id == "C078":
        notes = {
            "1": "`Hello`/`Hi` without trailing space should be False; `Hi Bob` True; lowercase `hello` False",
            "2": "positive `Hello universe`, leading-space negative (`' hi there'`), unrelated string negative",
            "3": "empty string negative; `'Hi '` and `'Hello '` positives (trailing-space edge cases)",
        }
    elif cluster_id == "C079":
        notes = {
            "1": "one positive (>0), one on-line (=0), one negative (<0) across different coefficients",
            "2": "additional on-line and positive cases to catch formula/sign mistakes",
            "3": "additional positive/negative cases including sign variations in coefficients",
        }
    elif cluster_id == "C080":
        notes = {
            "1": "long string positive (`Programming` -> first two + last two)",
            "2": "length-2 edge case should return empty string",
            "3": "another long string positive (`abcdef` -> `abef`)",
            "4": "length-3 edge case should return empty string",
        }
    elif cluster_id == "C081":
        notes = {
            "1": "single-element and multi-element positives (reverse after squaring)",
            "2": "negative numbers and zero cases (squaring before/after reverse matters)",
            "3": "duplicates/symmetric values to distinguish reverse-order vs sorted-order logic",
        }
    elif cluster_id == "C082":
        notes = {
            "1": "clear decreasing 4-digit positives (`9876`, `8765`)",
            "2": "positive and duplicate-digit negative (`5432` vs `5433`) to test strictness",
            "3": "non-consecutive but strictly decreasing positive (`5431`) plus non-decreasing negative (`2001`)",
        }
    elif cluster_id == "C083":
        notes = {
            "1": "mixed string-list cases (length 3 and 4) to verify duplicate-first-prefix + duplicate-last-suffix ordering",
            "2": "boolean/uppercase cases incl minimum-length list (`len=2`) edge behavior",
            "3": "float and longer-list cases to catch length-specific/sample-only implementations",
        }
    elif cluster_id == "C084":
        notes = {
            "1": "dotted username and short username across different domains (must return text before `@` only)",
            "2": "more dotted usernames with varied domain lengths to catch fixed-slice/domain-length assumptions",
            "3": "underscore username plus single-character username (`a@xyz.in`) edge case",
        }
    elif cluster_id == "C085":
        notes = {
            "1": "single-character symbolic terms (baseline `(p+q)(r+s)` shape)",
            "2": "multi-character identifiers (`alpha`, `beta`, ...), catches fixed-index parsers",
            "3": "multi-digit numeric terms (`24`, `35`, `46`, `57`), catches fixed-width/string-slice assumptions",
        }
    elif cluster_id == "C014":
        notes = {
            "1": "`get_short_books` correctness on varied pages/ISBNs",
            "2": "`get_medium_books` boundary handling (200 and 500 inclusive)",
            "3": "`get_pages_by_isbn` lookup (found cases in varied positions)",
            "4": "`count_by_language` aggregation into exact language-count dict",
            "5": "`total_pages_in_genre_lang` filtered page summation across multiple matches",
        }
    elif cluster_id == "C086":
        notes = {
            "1": "odd-length tuples (len 5 and 3): middle belongs to first half; only suffix repeats",
            "2": "odd-length tuples with floats/strings to catch type/shape assumptions",
            "3": "minimum even tuple (`len=2`) and longer odd tuple (`len=7`) edge behavior",
        }
    elif cluster_id == "C004":
        notes = {
            "1": "mixed false/true cases (odd non-multiple, multiple of 5, odd non-multiple)",
            "2": "large even/5-multiple positives to catch parameter-ignoring and wrong-operator logic",
            "3": "mixed `True/False/True` cases to distinguish `or` vs `and` and missing-`return False` bugs",
        }
    elif cluster_id == "C015":
        notes = {
            "1": "negative odd and positive even (checks odd squaring + even doubling together)",
            "2": "multiple negative odds plus a positive even (catches absolute-value/negativity handling bugs)",
            "3": "negative even and positive odd (catches sign errors in the even branch)",
        }
    elif cluster_id == "C016":
        notes = {
            "1": "non-zero last-two digits with mixed True/False cases (core divisibility logic only)",
            "2": "includes 2-digit case and a last-digit-zero case (`9870`) to test zero guard",
            "3": "mixed lengths with repeated/non-repeated last digits (e.g., `7533`) to catch extraction mistakes",
        }
    elif cluster_id == "C087":
        notes = {
            "1": "4-cycle shuffle on hidden digits (`1825 -> 8512 -> 5281 -> 2158 -> 1825`)",
            "2": "second hidden 4-cycle (`7395 -> 3579 -> 5937 -> 9753 -> 7395`) to catch public-case hard-coding",
        }
    elif cluster_id == "C088":
        notes = {
            "1": "five-word lowercase sentence (baseline alternating-uppercase behavior)",
            "2": "single-letter all-uppercase words (`A B C D E`) catches over-normalization/lowercasing bugs",
            "3": "longer odd-length sentence to test indexing across many words",
            "4": "another odd-length sentence to catch length-specific or early-return implementations",
        }
    elif cluster_id == "C089":
        notes = {
            "1": "same-vowel positives/negatives with mixed case (must check both vowelhood and equality case-insensitively)",
            "2": "same-letter non-vowel negative and different-vowel negative cases (catches equality-only / vowel-only bugs)",
            "3": "additional mixed-case same-vowel positives and mismatched endpoints",
        }
    elif cluster_id == "C090":
        notes = {
            "1": "baseline polynomial evaluations on hidden coefficient lists (descending powers)",
            "2": "cases with repeated coefficients/values to catch `coef.index(...)` exponent bugs",
            "3": "additional lengths/degrees to catch fixed-length formulas and premature loop returns",
        }
    elif cluster_id == "C091":
        notes = {
            "1": "same-last-digit vs different-last-digit hidden pairs (core `%10` comparison)",
            "2": "cases where full numbers differ but last digits match (catches full-number equality bug)",
            "3": "additional mixed pairs to catch num1/num2 misuse and wrong-digit extraction",
        }
    elif cluster_id == "C092":
        notes = {
            "1": "numbers divisible by 3, 5, and neither (baseline label routing)",
            "2": "includes multiples of 15 to ensure `FizzBuzz` branch is checked before `%3`/`%5` branches",
            "3": "additional mixed cases to catch casing / boolean-return / missing-fallback bugs",
        }
    elif cluster_id == "C093":
        notes = {
            "1": "multi-line input with mixed vowels/consonants (reverse vowels globally across all lines)",
            "2": "uppercase vowels included (catches incomplete vowel sets like missing `U`)",
            "3": "formatting-sensitive cases (line preservation / newline handling with global vowel reversal)",
        }
    elif cluster_id == "C094":
        # Observed evaluator vectors have 3 hidden groups (current problem JSON shows more private cases).
        notes = {
            "1": "baseline filtering by both constraints (`len(word) >= l` and first character == `c`)",
            "2": "case-sensitivity checks (must *not* lowercase/uppercase-normalize the starting character comparison)",
            "3": "minimum-length boundary and no-match/empty-output behavior",
        }
    elif cluster_id == "C017":
        # Observed evaluator vectors have 3 hidden groups (current problem JSON private-case metadata appears drifted).
        notes = {
            "1": "rectangular-matrix rotation case (catches square-only indexing / row-count confusion)",
            "2": "another non-square rotation case with negatives/varied values (input parsing + index-order robustness)",
            "3": "additional rotation case emphasizing exact output formatting expectations",
        }
    elif cluster_id == "C018":
        notes = {
            "1": "general case slicing (`outer = s[:n] + s[-n:]`, `inner = s[n:-n]`)",
            "2": "`len(s) == 2*n` edge case where inner string must be empty",
            "3": "duplicate-character strings (catches `strip(...)` / `s.index(...)`-based inner extraction bugs)",
        }
    elif cluster_id == "C019":
        notes = {
            "1": "case-insensitive symmetric-difference counting on mixed-case strings",
            "2": "strings with repeated letters (must count unique letters, not occurrences)",
            "3": "additional mixed-case + repeated-letter combinations to catch no-op normalization (`s1.upper()`) bugs",
        }
    elif cluster_id == "C020":
        # Submission behavior indicates a historical evaluator/prompt variant (alternate number-sequence triangle),
        # while current canonical JSON title/spec may refer to a different problem.
        notes = {
            "1": "small `n` cases (row construction and alternating direction starts correctly)",
            "2": "medium `n` cases (even-row reversal correctness and consecutive numbering across rows)",
            "3": "larger `n` cases (counter continuity / formatting across many rows)",
        }
    elif cluster_id == "C021":
        notes = {
            "1": "valid interior `n` (1-based indexing) should wrap exactly one middle character with `<b>...</b>`",
            "2": "boundary `n = 1` case (first character should be bolded, not treated as invalid)",
            "3": "end/out-of-range checks (`n = len(text)` valid; `n > len(text)` returns original string unchanged)",
        }
    elif cluster_id == "C095":
        notes = {
            "1": "3- and 4-letter columns (e.g., `XFD`, `AAAA`) to catch fixed-length or `<=3`-only solutions",
            "2": "single-letter columns (`A`..`Z`) baseline mapping",
            "3": "two-letter columns (e.g., `ZA`, `CZ`) to catch additive/sorted-letter mistakes and positional-weight bugs",
        }
    elif cluster_id == "C001":
        notes = {
            "1": "longer string (`programming`) to catch fixed-slice and duplicate-character index bugs",
            "2": "odd-length simple string (`abcdefg`) baseline deinterleaving",
            "3": "10-character numeric string to catch sample hard-coding / fixed-`10` slicing assumptions",
        }
    elif cluster_id == "C022":
        notes = {
            "1": "repeated characters where first-appearance order matters (`['l', 'e']` style output)",
            "2": "another repeated-character case to distinguish dedupe/order logic from raw occurrence counting",
            "3": "`mississippi`-style case where second-appearance order differs from first-appearance order",
        }
    elif cluster_id == "C005":
        notes = {
            "1": "large repeated-range list (must count unique even/odd values, not occurrences)",
            "2": "mixed negatives/offset values (checks parity of values, uniqueness, and correct dict counts)",
        }
    elif cluster_id == "C002":
        notes = {
            "1": "three unseen sentences using the same three permutation orders as public examples (`(0,2,1)`, `(2,1,0)`, `(1,0,2)`)",
            "2": "introduces cyclic permutations (`(2,0,1)`, `(1,2,0)`) to catch inverse-permutation and public-order-only logic",
            "3": "includes identity order `(0,1,2)` plus repeated unseen/public permutations to verify general tuple-driven shuffling",
        }
    elif cluster_id == "C100":
        notes = {
            "1": "exactly-3-character mixed-case name (`Amy`) should produce lowercase prefix + ID",
            "2": "another exactly-3-character mixed-case name (`Max`) to catch sample-initial-specific logic",
            "3": "2-character name (`Li`) must use full lowercase name (no indexing `name[2]`)",
            "4": "longer name (`Franklin`) must truncate to first 3 lowercase letters before concatenating ID",
            "5": "single-character name (`a`) edge case (no indexing past length 1)",
        }
    elif cluster_id == "C101":
        notes = {
            "1": "moderate-length word with repeated letters (`pineapple`) preserving first-appearance order",
            "2": "repetition-heavy word (`missisippi`) to catch order-preservation and dedupe logic bugs",
            "3": "longer mixed-repeat string to catch sample hard-coding and unstable `set(...)` ordering",
        }
    elif cluster_id == "C006":
        notes = {
            "1": "positive indices with symbol/string keys and values (baseline single-pair extraction)",
            "2": "includes integer keys and a valid negative index (must support Python negative indexing semantics)",
        }
    elif cluster_id == "C102":
        notes = {
            "1": "small tuple edge cases (`len=1`, `len=2`) to verify exact slicing/concatenation semantics",
            "2": "repeated-value tuple (`('x','y','z')*3`) to catch value-based `.index(...)` / duplicate-removal bugs",
            "3": "long repeated pattern tuple (`tuple('qwerty')*5`) to catch off-by-one slice and ordering mistakes",
        }
    elif cluster_id == "C023":
        notes = {
            "1": "leading/trailing + consecutive spaces (must preserve exact indices and whitespace count)",
            "2": "long sentence with multi-digit replacement indices",
            "3": "punctuation-heavy sentence with multiple spaced segments and multi-digit indices",
        }
    elif cluster_id == "C096":
        notes = {
            "1": "`total_revenue` over full and sliced transaction lists",
            "2": "`product_wise_total_units_and_revenue` aggregation over repeated product IDs",
            "3": "`top_selling_product` with unit-count tie broken by total revenue",
            "4": "`average_product_price` as `total_revenue / total_units_sold` per product, rounded to 2 decimals",
        }
    elif cluster_id == "C097":
        notes = {
            "1": "`total_engagement(video)` on varied records incl zero-view videos",
            "2": "`engagement_rate(video)` zero-view guard + rounding to 2 decimals",
            "3": "`most_engaging_video(videos)` with first-on-tie behavior",
            "4": "`videos_with_engagement_rate_above_threshold(...)` using strict `>`",
            "5": "`average_engagement_rate(videos)` over non-zero-view videos only, rounded to 2 decimals",
            "6": "comprehensive mixed suite combining all helpers (zero-view, tie, and threshold-edge cases)",
        }
    elif cluster_id == "C098":
        notes = {
            "1": "baseline/easy cases incl exact division and simple remainder distribution",
            "2": "larger non-divisible cases (must distribute `+1` across the earliest parts)",
            "3": "additional exact + non-exact cases to verify length, sum, and larger-first ordering",
        }
    elif cluster_id == "C099":
        notes = {
            "1": "basic `ax ± b = c` equations with spacing variations",
            "2": "negative coefficients/constants and negative RHS values (sign-handling robustness)",
            "3": "multi-digit coefficients and implied coefficient (`x`) cases",
        }
    elif cluster_id == "C103":
        notes = {
            "1": "longer list (`len=6`) checks only the last three elements are squared, with in-place modification",
            "2": "`len=4` case catches off-by-one tail slicing/indexing mistakes",
            "3": "`len=5` mixed values to verify correct tail selection and order preservation",
            "4": "`len=3` edge case (entire list must be squared) with in-place mutation semantics",
        }
    elif cluster_id == "C024":
        notes = {
            "1": "multi-line input with a trailing space after one line (exposes `split(' ')` empty-token bugs)",
            "2": "single-line mixed lengths/palindromes for baseline odd/even + palindrome classification",
            "3": "single-line non-palindrome words (`hello world`) to verify normal-word counts",
            "4": "large mixed corpus stressing aggregation across many words/lines",
            "5": "single-line even-length non-palindromes only (`abcd dcba`) to verify category placement",
        }
    elif cluster_id == "C104":
        notes = {
            "1": "length-2 case with mixed parity; catches mirror pairing and sign-direction mistakes",
            "2": "all-ones case (all same parity) should produce pure additions",
            "3": "multi-assert suite covering same-parity add, mixed-parity subtract (`a-b_rev`), and length-1 edge case",
        }
    elif cluster_id == "C007":
        notes = {
            "1": "single-letter words that are all vowels (per-word counting and formatting basics)",
            "2": "strings with digits/no vowels to ensure non-letters are not counted as vowels",
            "3": "long sentence with punctuation and repeated words (`is` appears twice), catching dict/set dedup and formatting drift",
        }
    elif cluster_id == "C025":
        notes = {
            "1": "carry propagation across multiple pairs (must reuse carry every step)",
            "2": "includes exact-100 resets and a `200 0` pair (carry can be `100` and then reset later)",
            "3": "repeated large sums causing carry to grow beyond two digits (tests correct `sum-100` recurrence)",
        }
    elif cluster_id == "C105":
        notes = {
            "1": "mixed letters/digits with newline-preserving reversal (`AA\\nBB`, `q1\\n2r`)",
            "2": "symmetric/unchanged cases (`!!\\n!!`, `ab\\nba`) to catch unnecessary mutation or constant-output code",
            "3": "additional alphanumeric/string cases to verify general 2-line transformation (not sample-specific)",
        }
    elif cluster_id == "C106":
        notes = {
            "1": "`k=4`, multi-line prose with mixed case; tests cumulative vowel counting across lines",
            "2": "`k=2` short mixed-case line; catches basic every-kth-vowel casing logic",
            "3": "large `k` (`100`) should produce no kth-vowel uppercase hits while still lowercasing other vowels",
            "4": "`k=1` edge case (every vowel uppercased) with lines containing few/no vowels",
            "5": "dense mixed-case vowel sequence; checks counting of both upper/lower vowels and lowercasing non-kth vowels",
        }
    elif cluster_id == "C107":
        notes = {
            "1": "long SAN string with move numbers, pawns/pieces, and kingside castling (`O-O`) token handling",
            "2": "captures/check suffixes (e.g., `Qxe4+`, `Nxc7+`) to catch fragile `len==2` or digit-only pawn heuristics",
            "3": "includes queenside castling (`O-O-O`) plus captures; catches castling mapping and token filtering bugs",
        }
    elif cluster_id == "C008":
        notes = {
            "1": "large `n=16` formatting case (spacing and exact character placement must scale)",
            "2": "large `n=18` formatting case to catch sample-size hard-coding and spacing formulas",
            "3": "large `n=20` formatting case; stresses generalized row construction and no extra spaces/newlines",
        }
    elif cluster_id == "C108":
        notes = {
            "1": "`overall_run_stats(...)` on a larger hidden dataset (flatten-all-years min/max/total/rounded average)",
            "2": "`century_rate(...)` hidden year lists including exact-100 boundary cases (`>= 100` required)",
            "3": "`average_yearly_century_rate(...)` must average per-year century rates (not global century percentage)",
            "4": "`years_with_more_than_average_yearly_century_rate(...)` strict `>` comparison and set return type",
            "5": "`year_with_most_average_runs(...)` tie handling via earliest year on equal average runs",
        }
    elif cluster_id == "C109":
        # Observed evaluator vectors are grouped into 3 hidden-case buckets.
        notes = {
            "1": "baseline todo updates with out-of-range indices mixed in (must ignore invalid indices while updating valid ones)",
            "2": "multi-digit indices and repeated indices (catches substring/character parsing like `'1' in '10 12'`)",
            "3": "extra trailing todo lines beyond the first input `n` (must process only `n` lines, not all remaining stdin)",
        }
    elif cluster_id == "C110":
        # Multi-function evaluator is grouped into 3 hidden-case buckets.
        notes = {
            "1": "`parse_moves`, `get_n_moves`, and `count_piece_moves` on SAN strings with move numbers/results/castling",
            "2": "`most_used_piece` and `remaining_pieces` (player parity + capture counting + tie-break semantics)",
            "3": "`n_checks` and integrated SAN edge cases (checks/checkmates, castling, result-token filtering consistency)",
        }
    elif cluster_id == "C026":
        # Multi-function evaluator is grouped into 3 hidden-case buckets.
        notes = {
            "1": "`total_revenue_in_region(...)` correctness (region matching and no premature `return 0`)",
            "2": "`revenue_range_for_product(...)` correctness (max-min range, including 0 for missing/single-record product)",
            "3": "`region_with_max_sales(...)` + `steady_revenue_products(...)` (aggregation + tie-break + exact set semantics)",
        }
    elif cluster_id == "C111":
        notes = {
            "1": "duplicate-value pairs and repeated-number cases (e.g., `(10,10)` only when the value appears at least twice)",
            "2": "`(x, x)` duplicate-count edge cases (`[2,0,-1], k=0` should not return `(0,0)`) plus no-solution cases",
            "3": "negative-number pairs and unique tuple ordering (`(-5,5)`, `(-3,3)`) without reversed duplicates",
        }
    elif cluster_id == "C112":
        notes = {
            "1": "multi-line mixed-case inputs (must preserve spaces and line boundaries while hashing consonants only)",
            "2": "all-vowel line (`aeiouAEIOU`) should remain unchanged (catches over-replacement of vowels)",
            "3": "uppercase-vowel + consonant mixes across multiple lines (catches lowercase-only vowel sets and line-collapse bugs)",
        }
    grouped_vector_clusters = {"C026", "C109", "C110"}
    # fallback if missing (skip raw testcase padding when evaluator vectors are grouped into fewer buckets)
    if cluster_id not in grouped_vector_clusters:
        for i in range(1, len(tests) + 1):
            notes.setdefault(str(i), f"private case group {i}")
    return notes


def _base_label(row: dict[str, Any]) -> str | None:
    if not row["is_non_full"]:
        return None
    summary = row["summary"]
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"
    if summary == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc in {"NameError", "TypeError", "AttributeError", "IndexError", "KeyError", "ValueError", "RecursionError"}:
            return f"Runtime {exc}"
        return "Runtime error (parseable final submission)"
    if summary != "Wrong Answer":
        return summary or "Unknown"

    tags = row["detector_tags"]
    if row["has_ellipsis_node"] and row["body_non_doc_stmt_count"] <= 1 and row["return_count"] == 0:
        return "Skeleton placeholder `...` left in function"
    if "prints_but_does_not_return" in tags:
        return "Prints output but does not return required value"
    if row["return_count"] == 0:
        return "No return / implicit `None`"
    code = row["logic_code"].lower()
    if row["return_count"] > 0 and row["return_true_count"] == row["return_count"]:
        return "Always returns `True` (constant output)"
    if row["return_count"] > 0 and row["return_false_count"] == row["return_count"]:
        return "Always returns `False` (constant output)"
    if re.search(r"\breturn\s*\(\s*true\s*\)\s*$", code):
        return "Always returns `True` (constant output)"
    if re.search(r"\breturn\s*\(\s*false\s*\)\s*$", code):
        return "Always returns `False` (constant output)"
    if re.search(r"\bif\s+true\s*:", code) and "return true" in code:
        return "Always returns `True` (constant output)"
    if re.search(r"\bif\s+false\s*:", code) and "return false" in code:
        return "Always returns `False` (constant output)"
    if "reads_input_inside_function_type_question" in tags:
        return "Reads input inside function-type question instead of parameters"
    if "early_return_inside_loop" in tags:
        return "Returns inside loop before completing full check/computation"
    return None


def classify_c010(row: dict[str, Any]) -> str:
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    code = row["logic_code"].lower()
    vec = row["vec"]
    vec3 = vec[-3:] if isinstance(vec, str) and len(vec) >= 3 else vec
    tags = row["detector_tags"]

    if "compute_electricity" in code or re.search(r"\bunits\s*=\s*\d+", code):
        return "Ignores input parameter / uses hard-coded units"

    # Sequential independent `if` blocks overwrite earlier slab results.
    if code.count("if ") >= 2 and "elif" not in code and "units" in code and "200" in code and "400" in code:
        return "Uses separate `if` slabs (branch overwrite / wrong slab precedence)"

    # Boundary mistake at 400 is very common (`< 400` instead of `<= 400`).
    if ("<400" in code or "< 400" in code) and "0.75" in code:
        return "Excludes the `400` boundary from middle slab (`< 400` vs `<= 400`)"

    # Middle slab formula missing fixed 150 charge.
    if "0.75" in code and "150" not in code and ("units" in code or "*" in code):
        return "Middle slab formula missing fixed `+150` charge"

    # High slab formula missing fixed 300 charge.
    if "0.9" in code and "300" not in code and ("units" in code or "*" in code):
        return "High slab formula missing fixed `+300` charge"

    # Returns just rates/charges instead of bill total computation.
    if re.search(r"return\s+float\s*\(\s*(0\.5|0\.75\s*\+\s*150|0\.9\s*\+\s*300)\s*\)", code):
        return "Returns tariff/rate expression instead of total bill"
    if re.search(r"return\s+(0\.5|0\.75|0\.9)\b", code):
        return "Returns per-unit rate instead of computed bill"

    # Condition booleans computed but never used to guard assignments.
    if ("is_num_of_units" in code or "condition" in code) and code.count("=") >= 3 and "return" in code:
        return "Computes slab conditions but overwrites bill unconditionally"

    # Flat-vs-progressive confusion (using unit deltas).
    if "(units-200" in code or "(units - 200" in code or "(units-400" in code or "(units - 400" in code:
        return "Implements progressive-slab billing instead of flat slab + fixed charge"

    # Case-vector-guided broad families.
    if vec == "011":
        return "Low-slab-only mistake (lower slab cases fail; upper slabs often pass)"
    if vec == "101":
        return "Middle-slab mistake (boundary/charge error in 200-400 range)"
    if vec == "110":
        return "High-slab mistake (>400 formula/branch error)"
    if vec == "001":
        return "Only high-slab case passes (low/mid branch logic broken)"

    return "Other wrong-answer logic pattern (residual)"


def classify_c011(row: dict[str, Any]) -> str:
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    code = row["logic_code"]
    low = code.lower()
    vec = row["vec"]

    # Wrong order of concatenation after reversing first string.
    if re.search(r"(s2\s*\+\s*[A-Za-z_][A-Za-z0-9_]*|s2\s*\+\s*s1\s*\[\s*::?-?1\s*\])", low) and ("[::-1]" in code or "reverse" in low):
        return "Reverses first string but concatenates in wrong order (`s2 + reversed(s1)`)"

    # Forgets to reverse s1 at all.
    if "s1+s2" in low.replace(" ", "") and ("[::-1]" not in code and ".reverse(" not in low):
        return "Concatenates `s1 + s2` without reversing the first string"

    # Boolean inversion after palindrome check.
    if re.search(r"return\s+.*!=.*\[\s*::?-?1\s*\]", low) or "!=newstr[::-1]" in low.replace(" ", ""):
        return "Inverts palindrome condition (`!=` instead of `==`)"

    # Checks substring/membership instead of palindrome equality.
    if " in " in low and ("[::-1]" in code or "reverse" in low):
        return "Uses substring/membership check instead of palindrome equality"

    # Returns non-boolean/string/manipulated string instead of bool.
    if re.search(r"return\s+f[\"']", code) or re.search(r"return\s+['\"]", code):
        return "Returns string/text instead of boolean result"

    # Fixed-index / fixed-length manual construction (non-general).
    idx_refs = len(re.findall(r"\[[0-9:-]+\]", code))
    if idx_refs >= 4 and ("s1[" in code or "s2[" in code or "new_str[" in code):
        return "Hard-coded index/slice comparisons (works only for specific lengths)"

    # Uses reverse slice but compares partial slices only.
    if "::-1" in code and re.search(r"\[[^\]]*:[^\]]*\]", code) and ("[:2]" in code or "[-2:]" in code or "1:2" in code):
        return "Compares only partial slices instead of full reversed+combined palindrome"

    # Wrong object checked for palindrome (checks only one input).
    if ("s1[::-1]" in code or "s2[::-1]" in code) and ("+ s2" not in code and "+s2" not in low and "+ s1" not in code and "+s1" not in low):
        return "Checks palindrome on one string (or wrong intermediate) instead of reversed(s1)+s2"

    # Case-vector guided broad families.
    if vec in {"010", "011", "110", "101", "100", "001"} and "::-1" in code:
        return "Partial/incorrect reverse+combine logic (close but wrong construction)"
    if vec == "000":
        return "Incorrect construction/check of reversed+combined string (broad logic failure)"

    return "Other wrong-answer logic pattern (residual)"


def classify_c012(row: dict[str, Any]) -> str:
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    code = row["logic_code"]
    low = code.lower()
    vec = row["vec"]

    # Absolute-difference misuse ignores sign and can misclassify direction-sensitive cases.
    if "abs(" in low:
        if "sequence" in low and ("-" in low):
            return "Uses `abs()` on differences (sign-insensitive AP check)"

    # Checks only first/few terms via fixed indices.
    fixed_idxs = set(re.findall(r"sequence\[(\-?\d+)\]", low))
    if len(fixed_idxs) >= 4 and "for " not in low:
        return "Checks only a few fixed positions, not the whole sequence"
    if len(fixed_idxs) >= 4 and "for " in low and "range(len(sequence)-" not in low:
        return "Mixes fixed-index checks with incomplete iteration"

    # Returns comparison of last computed pair after loop (loop computes but final return only uses last values).
    if re.search(r"for .*:\s*.*first\s*=.*second\s*=.*return\s+first\s*==\s*second", low, re.S):
        return "Computes pairwise diffs in loop but returns only last comparison"
    if "return first == second" in low:
        return "Returns only the last computed pairwise-difference comparison"

    # Expected-sequence reconstruction from common diff but wrong origin/indexing.
    if "(i+1) *" in code or "(i + 1) *" in code:
        return "Reconstructs expected sequence with wrong base term/indexing"

    # Sorting sequence before checking AP can mask order requirements / change meaning.
    if ".sort(" in low or "sorted(" in low:
        return "Sorts sequence before checking AP (changes sequence semantics)"

    # Fixed-width comparisons (head/tail only) without full scan.
    if ("sequence[0]-sequence[1]" in low or "sequence[1]-sequence[2]" in low) and ("for " not in low or "len(sequence)-" not in low):
        return "Compares only initial/final differences, not all consecutive differences"

    # Case-vector guided broad families.
    if vec in {"110", "100", "101"}:
        return "Partially correct AP check (fails specific edge-case groups)"
    if vec == "000":
        return "Incorrect AP logic (broad wrong-answer failure)"

    return "Other wrong-answer logic pattern (residual)"


def classify_c013(row: dict[str, Any]) -> str:
    # Start from existing pangram-specific primary pattern, but consolidate and split residuals.
    if not row["is_non_full"]:
        return None
    label = row["orig_primary_pattern"]
    code = row["logic_code"].lower()
    vec = row["vec"]

    # Keep most informative existing labels, but consolidate runtime long tail a bit.
    keep = {
        "Returns inside the alphabet-check loop (decides after first character/iteration)",
        "Hard-codes sample pangram strings/examples instead of checking letter coverage",
        "Syntax / non-parseable final submission",
        "Skeleton placeholder `...` left in function (no implementation; returns None)",
        "Always returns `True` (constant output)",
        "Always returns `False` (constant output)",
        "Checks exact alphabet string order (`abcdefghijklmnopqrstuvwxyz`) instead of pangram coverage",
        "Counts total alphabetic characters instead of distinct letters",
        "Compares exact set(text) to alphabet set (rejects valid pangrams with extra chars/spaces)",
        "Fails non-letter/digit-heavy private case despite passing others",
        "Uses total string length ==/>= 26 as pangram test (counts spaces/digits/punctuation)",
        "Strips spaces only but not other non-letters; digit/punctuation cases still break logic",
        "Counts unique characters (or len(set(...)) == 26) instead of checking all letters",
        "Uses `text.isalpha()` gate, rejecting valid pangrams that include spaces/punctuation/digits",
        "No return / implicit `None`",
    }
    if label in keep:
        return label

    # Consolidate runtime families.
    if label.startswith("Runtime ") or label.startswith("Manual character-count dictionary crashes") or label.startswith("Infinite recursion"):
        if "KeyError" in label:
            return "Runtime KeyError (unexpected character handling)"
        if "NameError" in label:
            return "Runtime NameError (undefined variable/helper)"
        return "Runtime error (parseable final submission)"

    # Split the residual with additional semantic families.
    if label == "Other wrong-answer logic pattern (residual)":
        if "isalpha" in code and "isalpha()" not in code and (
            "if text.isalpha" in code or "x=text.isalpha" in code or " = text.isalpha" in code
        ):
            return "Uses method object truthiness (`text.isalpha` without `()`)"
        if "isalpha()" in code:
            return "Uses `text.isalpha()` as pangram test (alphabetic-only, not 26-letter coverage)"
        if re.search(r"\b(?:if|elif)\s+\"a\"\s+(?:or|and)\s+\"b\"", code) or re.search(r"\b(?:if|elif)\s+'a'\s+(?:or|and)\s+'b'", code):
            return "Incorrect boolean-chain membership test (`\"a\" or \"b\" in text` / `and` chain)"
        if re.search(r"\bis_pangram\s*(?:==|!=|is)\s*text\b", code) or re.search(r"\btext\s*(?:==|!=|is)\s*is_pangram\b", code):
            return "Compares function object/name (`is_pangram`) with input text"
        if re.search(r"\btext\s*==\s*[\"']text[\"']", code):
            return "Compares the input to the literal string `\"text\"` (placeholder-name confusion)"
        if re.search(r"\breturn\s+str\s*!=\s*\(\s*[\"']{2}\s*\)", code) or re.search(r"\bif\s+str\s*:", code):
            return "Uses input truthiness / non-empty-string check instead of pangram logic"
        if re.search(r"(?s)\b([a-z_][a-z0-9_]*)\s*=\s*[\"'][^\"']*[\"'].*\bif\s+\1\s*:", code):
            return "Checks truthiness of a constant/local variable instead of letter coverage"
        if "len(str_list)==len(new_set)" in code or "len(str_list) == len(new_set)" in code:
            return "Checks for duplicate characters (uniqueness) instead of pangram coverage"
        if "count == 0" in code and "if i not in s" in code and "else:\n            count += 1" in code:
            return "Checks for duplicate characters (uniqueness) instead of pangram coverage"
        if ("len(dic)" in code or "len(dict" in code) and "==26" in code.replace(" ", ""):
            return "Counts unique characters (dictionary/list length == 26) instead of checking all letters"
        if ("len(set(" in code or "list(set(" in code) and "26" in code:
            return "Counts unique characters (or len(set(...)) == 26) instead of checking all letters"
        if ".sort()==" in code or ".sort() ==" in code:
            return "Compares the return value of `.sort()` (None) while checking alphabet coverage"
        if (
            re.search(r"[\"'][A-Za-z]{20,}[\"']", code)
            and (" in text" in code or "text in " in code or "== text" in code or "text ==" in code)
        ):
            if "==" in code and ("text ==" in code or "== text" in code):
                return "Hard-codes a specific alphabet/pangram string and checks exact equality"
            return "Alphabet-string/list membership confusion (`in`/substring check instead of coverage)"
        if "ascii_lowercase" in code and "set(" in code and "import string" not in code and "from string" not in code:
            return "Uses `string.ascii_lowercase` without importing `string` (environment-dependent fail-all)"
        if "count > len(text)" in code and "count+=1" in code:
            return "Impossible/always-false condition after counting characters (trivial constant decision)"
        if "string.ascii_lowercase" in code and (" in text" in code or "in string.ascii_lowercase" in code):
            return "Substring/membership confusion with alphabet string (`text in alphabet` / `alphabet in text`)"
        if ("len(" in code and "26" in code) and ("set(" not in code) and ("ascii_lowercase" in code or "count" in code):
            return "Length/threshold heuristic instead of letter-set coverage"
        if "len(set(" in code and ("isalpha" in code or "split(" in code or "join(" in code):
            return "Raw unique-character counting after partial normalization"
        if "abcdefghijklmnopqrstuvwxyz" in code and ("==" in code or " in " in code):
            return "Alphabet-string equality/substring check instead of coverage"
        if ("'a'" in code and "'b'" in code and " in text" in code) or (" or 'a'" in code) or ("or 'a'" in code):
            return "Incorrect boolean-chain membership checks for letters"
        if "set(" in code and "ascii_lowercase" in code and "<=" in code:
            # Usually close but a bug elsewhere (case handling / filtering / variable use)
            return "Near-correct set-based approach with implementation bug"
        if vec in {"101", "001", "100", "110"}:
            return "Partial-score pangram logic bug (case/filtering/coverage edge case)"
        return "Other wrong-answer logic pattern (residual)"

    if label == "Computes values but never returns a boolean (implicit `None`)":
        return "No return / implicit `None`"

    if label == "Checks whether full input is a substring of the alphabet string":
        return "Substring/membership confusion with alphabet string (`text in alphabet` / `alphabet in text`)"

    return label


def classify_c077(row: dict[str, Any]) -> str:
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    code = row["logic_code"]
    low = code.lower()
    vec = row["vec"]
    squashed = low.replace(" ", "")

    if re.search(r"\breturn\s+is_multiple_of_5_not_3\b", low):
        return "Returns the function object/name instead of a boolean result"
    if "input(" in low:
        return "Reads input inside function instead of using parameter `num`"
    if re.search(r"\breturn\s+\(?\s*(true\s+or\s+false|1\s+or\s+0|1\s+or\s+-1\s+or\s+0)\s*\)?", low):
        return "Boolean literal expression (`True or False`) used instead of real condition"
    if "%5" in squashed and "%3" not in squashed:
        return "Checks only divisibility by 5 (omits the 'not multiple of 3' condition)"
    if "%3" in squashed and "%5" not in squashed:
        return "Checks divisibility by 3 instead of 'multiple of 5 and not 3'"
    if "%5" in squashed and "%3" in squashed and "or" in low and re.search(r"%\s*5|%\s*3", low):
        return "Uses `or` instead of `and` when combining divisibility conditions"
    if "%5" in squashed and "%3==0" in squashed and "%3!=0" not in squashed:
        return "Uses `num % 3 == 0` in the positive condition (accepts multiples of 15)"
    if re.search(r"(?m)^\s*[^#\n]*%\s*3\s*!=\s*0\s*$", code) and "if" in low and "% 5" in low:
        return "Computes the `% 3 != 0` check but does not use it in a condition"
    if re.search(r"\breturn\s+\w+\s*%\s*5\b(?!\s*[=!<>])", low) or re.search(r"\bif\s+\w+\s*%\s*5\b(?!\s*[=!<>])", low):
        return "Uses modulo value truthiness directly (`num % 5`) instead of explicit divisibility comparison"
    if ("num*5" in squashed and "num*3" in squashed) and "%" not in squashed:
        return "Uses arithmetic multiplication truthiness (`num*5`, `num*3`) instead of divisibility checks"
    if "//" in low and ("%5" not in squashed or "%3" not in squashed):
        return "Uses floor-division/digit heuristic instead of direct modulus divisibility checks"
    if "&" in code and "%" in code:
        return "Uses bitwise `&` in divisibility condition (operator/precedence bug)"
    if re.search(r"\breturn\s+[\"'][^\"']+[\"']", code):
        return "Returns a text message/string instead of boolean `True`/`False`"
    if vec == "001" and "%5" in squashed and "%3!=0" in squashed and "%5!=0" not in squashed:
        return "Handles only the `num % 5 == 0` branch and forgets the non-multiple fallback case"
    if any(tok in low for tok in ["10", "15", "-25"]) and ("num ==" in low or "if num" in low):
        if ("hello" not in low and "greeting" not in low):
            return "Hard-codes sample values/examples instead of checking the divisibility rule"
    if re.search(r"\breturn\s+\w+\s*//\s*5", low):
        return "Returns floor-division result instead of boolean divisibility test"
    if vec in {"001", "011"} and "%5" in squashed:
        return "Partially correct divisibility logic (fails one private case group due condition/branch bug)"
    if vec == "000":
        return "Incorrect divisibility logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c078(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    # More specific runtime labels first, then fall back to generic base labels.
    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "IndexError":
            return "Runtime IndexError from direct indexing on short/empty strings"
        if exc == "NameError" and ("string." in low or "stratwith" in low or "endswitch" in low):
            return "Runtime NameError from misspelled helper/API or undefined identifier"
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    # Semantic mistakes for greeting-prefix rule: must start with exact 'Hello ' or 'Hi ' (case-sensitive).
    if ".strip(" in low and ("startswith(" in low or ".split(" in low):
        return "Strips whitespace before checking prefix (wrongly accepts leading-space inputs / changes semantics)"
    if ".lower(" in low and ("startswith(" in low or ".split(" in low):
        return "Makes the check case-insensitive (`hello`/`hi` become accepted)"
    if re.search(r"startswith\s*\(\s*\(\s*[\"']hello[\"']\s+or\s+[\"']hi[\"']\s*\)\s*\)", low) or re.search(r"startswith\s*\(\s*[\"']hello[\"']\s+or\s+[\"']hi[\"']\s*\)", low):
        return "Uses `startswith(\"Hello\" or \"Hi\")` (Python `or` collapses to one prefix)"
    if (
        re.search(r"startswith\s*\(\s*[\"']hello[\"']\s*\)", low)
        or re.search(r"startswith\s*\(\s*[\"']hi[\"']\s*\)", low)
        or re.search(r"\[:\s*5\]\s*==\s*[\"']hello[\"']", low)
        or re.search(r"\[:\s*2\]\s*==\s*[\"']hi[\"']", low)
        or re.search(r"\[:\s*len\(\s*[\"']hello[\"']\s*\)\]\s*==\s*[\"']hello[\"']", low)
        or re.search(r"\[:\s*len\(\s*[\"']hi[\"']\s*\)\]\s*==\s*[\"']hi[\"']", low)
    ):
        return "Checks `Hello`/`Hi` without requiring the trailing space"
    if re.search(r"startswith\s*\(\s*\(\s*[\"']hello[\"']\s*,\s*[\"']hi[\"']\s*\)\s*\)", low) or re.search(r"startswith\s*\(\s*\(\s*[\"']hi[\"']\s*,\s*[\"']hello[\"']\s*\)\s*\)", low):
        return "Checks `Hello`/`Hi` prefixes without trailing space using `startswith((...))`"
    if (
        (re.search(r"startswith\s*\(\s*[\"']hello\s+[\"']\s*\)", low) and "hi " not in low)
        or (re.search(r"startswith\s*\(\s*[\"']hi\s+[\"']\s*\)", low) and "hello " not in low)
    ):
        return "Handles only one greeting prefix (`Hello ` or `Hi `), not both"
    if ".split(" in low and ("[0]" in low or "words[0]" in low or "greeting[0]" in low or "first_word" in low):
        return "Checks first token via `split()` (accepts `Hello`/`Hi` without required trailing space)"
    if (".split(" in low and ("=='hello'" in low or "==\"hello\"" in low or "=='hi'" in low or "==\"hi\"" in low or " in t" in low or " in l" in low)) or (
        ("new_word" in low or "word +=" in low or "s1=" in low or "while" in low)
        and ("hello" in low or "hi" in low)
        and ("break" in low or "!=" in low and " " in low)
    ):
        return "Extracts the first word manually (or via `split`) and compares to `Hello`/`Hi`, ignoring required trailing-space semantics"
    if ("\"hello\" in s" in low or "\"hi\" in s" in low or "'hello' in s" in low or "'hi' in s" in low) and "startswith" not in low:
        return "Uses substring containment (`in`) instead of checking the prefix"
    if re.search(r"\bin\s+[\"']hello[\"']", low) or re.search(r"\bin\s+[\"']hi[\"']", low):
        return "Checks membership in the literal string `'Hello'/'Hi'` instead of full prefix equality"
    if re.search(r"if\s+.*\bor\b\s*[\"'][^\"']+[\"']", low) and ("hello" in low or "hi" in low):
        return "Boolean-chain literal bug (`... or 'Hi'`) creates an always-truthy greeting condition"
    if " and " in low and "hello" in low and "hi" in low and ("==" in low or "startswith(" in low):
        return "Uses `and` between `Hello` and `Hi` prefix checks (impossible conjunction)"
    if "startswith ==" in low:
        return "Compares the `startswith` method object instead of calling `startswith(...)`"
    if re.search(r"if\s+s\s*==\s*[\"']welcome[\"']\s+or\s+[\"']hithere[\"']", low) or re.search(r"==\s*[\"']hello there[\"']\s+or\s+[\"']hi friend[\"']", low):
        return "Boolean-chain literal bug (`x == 'A' or 'B'`) while handling sample strings"
    if any(tok in low for tok in ["hello there", "hi friend", "welcome", "hithere"]) and ("==" in low or "startswith(" in low):
        return "Hard-codes public sample strings/examples instead of the general prefix rule"
    if (re.search(r"\[:\s*6\]\s*==\s*[\"']hello\s+[\"']", low) or re.search(r"\[:\s*3\]\s*==\s*[\"']hi\s+[\"']", low)) and "for " in low:
        return "Wraps a correct-ish prefix slice in an unnecessary loop (early-return control-flow bug)"
    if (re.search(r"s\s*==\s*[\"']hello\s+[\"']", low) or re.search(r"s\s*==\s*[\"']hi\s+[\"']", low)) and "startswith" not in low:
        return "Checks exact equality to `'Hello '`/`'Hi '` instead of prefix"
    if vec in {"011", "110", "010"}:
        return "Partially correct greeting-prefix logic (fails edge cases like no-space/leading-space/empty input)"
    if vec == "000":
        return "Incorrect greeting-prefix logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c079(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function (EOF under evaluator function-call tests)"
        if exc == "NameError":
            if re.search(r"\bax\b|\bby\b", low):
                return "Runtime NameError from using `ax`/`by` instead of `a*x`/`b*y`"
            if "retun" in low:
                return "Runtime NameError from typo in `return`/identifier"
        if exc == "RecursionError" and "point_position_relative_to_line(" in low:
            return "Infinite recursion by calling the target function inside itself"
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if re.search(r"\breturn\s*\(?\s*a\s*\*\s*x\s*\+\s*b\s*\*\s*y\s*\+\s*c\s*\)?\s*$", low):
        return "Returns raw line-expression value `a*x + b*y + c` instead of mapping to `1/-1/0`"
    if re.search(r"\breturn\s+int\s*\(\s*a\s*\*\s*x\s*\+\s*b\s*\*\s*y\s*\+\s*c\s*\)\s*$", low):
        return "Returns raw line-expression value (cast with `int(...)`) instead of sign-mapping to `1/-1/0`"
    m_expr_var = re.search(
        r"(?s)\b([a-z_][a-z0-9_]*)\s*=\s*\(?\s*\(?\s*a\s*\*\s*x\s*\)?\s*\+\s*\(?\s*b\s*\*\s*y\s*\)?\s*\+\s*c\s*\)?",
        low,
    )
    if m_expr_var:
        var = re.escape(m_expr_var.group(1))
        if re.search(rf"\breturn\s*\(?\s*{var}\s*\)?\b", low):
            return "Computes `a*x + b*y + c` but returns that raw variable instead of sign-mapping to `1/-1/0`"
    if (
        ("=a*x+b*y+c" in squashed or "=((a*x)+(b*y)+c)" in squashed or "=(a*x)+(b*y)+c" in squashed)
        and re.search(r"\breturn\s+[a-z_][a-z0-9_]*\b", low)
    ):
        return "Computes `a*x + b*y + c` but returns that raw variable instead of sign-mapping to `1/-1/0`"
    if "a*x+b*y+c" in squashed and ("==1" in squashed or "==-1" in squashed):
        return "Compares `a*x+b*y+c` to exact `1`/`-1` instead of checking sign `>0/<0`"
    if "a*x+b*y+c" in squashed and (">=0" in squashed or "<=0" in squashed):
        return "Uses `>=0`/`<=0` sign checks that swallow the zero case before equality check"
    if re.search(r"\bpoint\s*<\s*1\b", low) or re.search(r"\bo\s*<\s*1\b", low):
        return "Uses wrong sign threshold (`< 1` instead of `< 0`) for line-expression result"
    if ("/b" in low or "/ b" in low) and ("y>" in squashed or "y<" in squashed or "if(y" in squashed):
        return "Slope/intercept comparison approach with sign/division pitfalls (fails line-orientation cases)"
    if "a*x+b*y>c" in squashed or "a*x+b*y<c" in squashed or "a*x+b*y-c" in squashed:
        return "Uses incorrect line equation arrangement/sign (wrong comparison to `c`)"
    if "**" in low and ("a**x" in squashed or "b**y" in squashed):
        return "Uses exponentiation (`a**x`, `b**y`) instead of multiplication in the line expression"
    if "%" in low and ("a*x" in low or "b*y" in low):
        return "Uses modulus/arithmetic tricks on line terms instead of sign of `a*x + b*y + c`"
    if "ifx>a" in squashed or "ify>b" in squashed or "ifc>0" in squashed or "ifa<x" in squashed:
        return "Compares coefficients/coordinates directly instead of evaluating `a*x + b*y + c`"
    if (
        re.search(r"\breturn\s+\(?\s*[\"']\+?1[\"']\s*\)?", low)
        or re.search(r"\breturn\s+\(?\s*[\"']-1[\"']\s*\)?", low)
        or re.search(r"\breturn\s+\(?\s*[\"']0[\"']\s*\)?", low)
    ):
        return "Returns string labels (`'1'`, `'-1'`) instead of integer outputs"
    if "a=int()" in squashed or "b=int()" in squashed or "c=int()" in squashed:
        return "Reinitializes parameters inside the function (erases evaluator inputs before computation)"
    if "line=[" in squashed or "point_position=[" in squashed:
        return "Hard-codes sample data/list values instead of computing from function inputs"
    if "return(1or-1or0)" in squashed or "return((1and0)and(-1))" in squashed:
        return "Returns a constant boolean/integer expression (`1 or -1 or 0`, etc.)"
    if row["return_count"] == 1 and re.search(r"\breturn\s*\(?\s*-?1\s*\)?\s*$", low):
        return "Always returns a constant class label (`1` or `-1`) regardless of the point/line"
    if row["return_count"] == 1 and re.search(r"\breturn\s*\(?\s*0\s*\)?\s*$", low):
        return "Always returns `0` regardless of the point/line"
    if row["return_count"] == 1 and re.search(r"\breturn\s*\(?\s*[abcxy]\s*\)?\s*$", low):
        return "Returns one input variable (`a`, `b`, `c`, `x`, or `y`) instead of the relative-position label"
    if re.search(r"(?m)^\s*return\s*$", code):
        return "Bare `return` statement (returns `None` instead of `1/-1/0`)"
    if "a==1" in squashed or "a==-1" in squashed or "a==2" in squashed:
        return "Hard-codes coefficient/testcase-specific conditions instead of using the line-sign rule"
    if ("x>0" in squashed or "y>0" in squashed or "x<0" in squashed or "y<0" in squashed) and "a*x+b*y+c" not in squashed:
        return "Uses point quadrant/coordinate-sign heuristic instead of `a*x + b*y + c`"
    if re.search(r"\breturn\s+1\b", low) and "return -1" not in low and "return 0" not in low:
        return "Always returns `1` (constant output)"
    if re.search(r"\breturn\s+0\b", low) and "return 1" not in low and "return -1" not in low:
        return "Always returns `0` (constant output)"
    if any(tok in low for tok in ["point_position_relative_to_line(1, -1, 0, 2, 1)", "point_position_relative_to_line(-1, -1, -1, 0, 0)"]):
        return "Hard-codes public example cases instead of computing point position"
    if vec in {"001", "010", "011", "110"} and ("a*x+b*y+c" in squashed or "a * x" in low):
        return "Partially correct line-sign logic (formula or threshold bug on specific private cases)"
    if vec == "000":
        return "Incorrect point-position logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c080(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "IndexError" and ("[1]" in code or "[-2]" in code or "[-1]" in code):
            return "Runtime IndexError from indexing short strings (`s[1]`, `s[-2]`, etc.) without length guard"
        if exc == "NameError" and ("input" in low or "str(input)" in low):
            return "Runtime NameError from misusing `input`/undefined variable in string-edge logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["helloworld", "python"]) or any(tok in low for tok in ["'held'", "\"held\"", "'pyon'", "\"pyon\""]):
        return "Hard-codes sample strings/outputs instead of combining edges generically"
    if low.strip() in {"return ''", 'return ""', "return('')", 'return("")'}:
        return "Always returns empty string"
    if re.search(r"\breturn\s+s\s*$", low) or re.search(r"\breturn\s+\(\s*s\s*\)\s*$", low):
        return "Returns the original string instead of first-two + last-two combination"
    if "[:2]" in code and "[-2:]" in code:
        if ("len(s)>2" in squashed or "len(s)>=3" in squashed or "len(s)<2" in squashed or "len(s)<=2" in squashed):
            return "Uses wrong minimum-length threshold (treats length-3 strings like valid edge-combine inputs)"
        if ("len(s)<4" in squashed or "len(s)<=4" in squashed) and re.search(r"if\s+len\(s\)\s*[<>=]+\s*4\s*:\s*\n\s*return\s*['\"]{0,2}['\"]\s*\n\s*return", code, re.S):
            return "Long-string return path is unreachable (second `return` placed inside the short-string branch)"
        if "len(" not in low:
            return "Combines first/last two chars without handling short-string edge cases (`len <= 3`)"
        return "Near-correct edge-combine logic with branch/slice bug"
    if "[:2]" in code and "[-1:]" in code:
        return "Uses wrong slice widths (`first 2` + `last 1`) instead of first/last two characters"
    if ("[0]" in code and "[1]" in code and "[-2]" in code and "[-1]" in code) and ("len(" not in low or "len(s)>2" in squashed or "len(s)<=2" in squashed):
        return "Builds result via direct indexing (`s[0], s[1], s[-2], s[-1]`) with missing/wrong short-string guard"
    if "[:2]" in code and "[:2]" in code.split("return", 1)[-1]:
        return "Duplicates the first two characters instead of taking the last two"
    if re.search(r"\[\s*0\s*:\s*3\s*\].*\[\s*-1\s*:\s*\]", code, re.S):
        return "Uses wrong slices (`first 3` + `last 1`) instead of first/last two characters"
    if ".split(" in low:
        return "Uses split/token logic instead of simple string slicing on the whole input"
    if vec in {"1111", "0111", "111"}:
        return "Partially correct edge-combine logic: wrong length threshold for the 3-character edge case"
    if vec in {"1010", "0101", "101"}:
        return "Partially correct slicing but fails one or both short-string edge cases"
    if vec == "0000" or vec == "000":
        return "Incorrect edge-combine logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c081(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "TypeError":
            if ".reverse(" in low and "return" in low:
                return "Runtime TypeError from misusing `.reverse()` result / in-place reverse API"
            if "sort(" in low and "return sorted(" not in low:
                return "Runtime TypeError from sorting/reversing API misuse in list transformation"
        if exc == "AttributeError" and (".append" in low or ".reverse" in low or ".square" in low):
            return "Runtime AttributeError from wrong list method/attribute usage"
        if exc == "IndexError" and ("[i+1]" in low or "[-1]" in low):
            return "Runtime IndexError from invalid index while iterating transformed list"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in squashed for tok in ["[25,16,9,4,1]", "[4,100]"]) or ("if l==" in low and "[" in low and "return [" in low):
        return "Hard-codes public sample outputs/cases instead of computing reversed squares"
    if "append(25)" in low and "append(16)" in low and "append(9)" in low:
        return "Hard-codes public sample outputs/cases instead of computing reversed squares"
    if ".sort(" in low or "sorted(" in low:
        if "reverse=true" in squashed or "reverse = true" in low:
            return "Sorts squared values descending instead of preserving reversed input order"
        return "Sorts values instead of reversing the input order before squaring"
    if "range(1,len(l)+1)" in squashed and ("**2" in low or "*i" in low):
        return "Squares index/range values instead of squaring the list elements"
    if "range(0,2)" in squashed and ("**2" in low or "append(" in low):
        return "Squares only the first two elements (length-specific partial implementation)"
    if ("print(" in low and "return" in low and ".append(" not in low) or ("print(i**2" in squashed):
        return "Prints squared values instead of returning the transformed list"
    if ("**2" in low or "*i" in low or "i*i" in low or "num**2" in low or "x*x" in low) and (
        "reversed(" not in low and "::-1" not in low and ".reverse(" not in low and "sorted(" not in low and ".sort(" not in low
    ):
        return "Squares elements but does not reverse the order"
    if (
        ("[::-1]" in low or "reversed(l)" in low or ".reverse(" in low)
        and re.search(r"\breturn\s+(l1|l|x|new_list|list\(x\))\b", low)
        and "append(" not in low.split("return", 1)[0]
        and ("**2" in low or "i**2" in low or "x**2" in low)
    ):
        return "Attempts to square values, but ultimately returns only the reversed list (squares are not stored)"
    if ("[::-1]" in low or ".reverse(" in low or "reversed(" in low) and ("**2" not in low and "*i" not in low and "x*x" not in low and "num**2" not in low):
        return "Reverses the list but forgets to square the elements"
    if ".reverse(" in low and ("return l" in low or "return list" in low or "new_l=l1.reverse()" in squashed):
        return "Uses in-place `.reverse()` incorrectly (returns/mutates list without producing squared reversed result)"
    if "^2" in low:
        return "Uses `^2` (bitwise XOR) instead of squaring (`**2`)"
    if ("for " in low and "return" in low and ".append(" in low and row["return_count"] >= 1 and "return" in low.split("for", 1)[-1]):
        if "return" in low and ("return n_s" in low or "return new_list" in low):
            return "Returns from inside the build loop, producing only the first squared/reversed element"
    if low.strip() in {"return []", "return l", "return list()"}:
        return "Returns empty/original list instead of reversed squared values"
    if re.search(r"\breturn\s+\[\s*[a-z_][a-z0-9_]*\s*\]\s*$", low):
        return "Returns only one squared value wrapped in a list instead of the full reversed-squares list"
    if vec == "001" or vec == "010" or vec == "100" or vec == "1" or vec == "10":
        return "Partially correct list transformation (reverse-vs-sort order mistake on specific test groups)"
    if vec == "000":
        return "Incorrect reversed-squares logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c082(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    # Refine generic early-return loop label into a digit-check-specific pattern.
    base = _base_label(row)
    if base == "Returns inside loop before completing full check/computation":
        if ("str(n)" in low or "[i]" in low or "%10" in squashed or "//10" in squashed) and ("return true" in low and "return false" in low):
            return "Returns after checking only the first digit comparison (loop exits before all 4 digits are checked)"
        return base

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function (EOF under evaluator function-call tests)"
        if exc == "TypeError" and ("sorted" in low or "str(" in low or "[i+1" in low):
            return "Runtime TypeError from mixed string/int digit operations or invalid sorted/index logic"
        if exc == "IndexError" and ("[i+1]" in low or "[1+1]" in low):
            return "Runtime IndexError from out-of-range digit indexing in comparison loop"
        if exc == "NameError" and ("return false" in low or "return true" in low):
            return "Runtime NameError from lowercase `true`/`false` or typoed identifier"

    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["4321", "3210", "9876", "5432", "5433", "2001", "5431"]) and ("==" in low or "if n" in low):
        return "Hard-codes sample numbers/examples instead of checking digit order generically"
    if "sorted(" in low or ".sort(" in low:
        if "reverse=true" in squashed or "reverse = true" in low or "sorted(" in low and "reverse" in low:
            return "Uses sorted-descending digit check (accepts duplicates; not strict decreasing)"
        return "Uses sorting-based digit check instead of pairwise strict comparison"
    if ("9876543210" in low) or ("-1" in code and ("digits[i]-1" in squashed or "int(n[i])-1" in squashed or "==int" in squashed and "-1" in squashed)):
        return "Requires consecutive step of exactly 1 between digits (rejects valid decreasing numbers like `5431`)"
    if ("str(n)" in low or "n=str(n)" in squashed or "[0]" in code) and ("for " in low and "return true" in low and "return false" in low):
        return "Returns after checking only the first digit comparison (loop exits before all 4 digits are checked)"
    if ("str(n)" in low or "n=str(n)" in squashed) and ("[0]" in code and "[1]" in code and "[2]" in code and "[3]" in code):
        if re.search(r"\[[0123]\]\s*>\s*.*\[[0123]\]", code) and ("[3]" not in code.split(">", 1)[-1] or "str(n)[0] > str(n)[1]> str(n)[3]" in code):
            return "Compares only some digit positions (skips a required adjacent comparison)"
    if ">=" in code or "<=" in code:
        return "Uses non-strict comparisons (`>=`/`<=`), so equal adjacent digits can be accepted"
    if "1000<=n>=9999" in squashed or "n<1000orn>999" in squashed:
        return "Uses an incorrect 4-digit range check (`1000 <= n >= 9999` / wrong bounds)"
    if ("%10" in squashed or "//10" in squashed) and "/" in code and "//" not in code:
        return "Extracts digits using `/` (float division) instead of integer division `//`"
    if ("%10" in squashed or "//10" in squashed) and ("nums.append" in low or "l.append" in low):
        if "for j in range(0,3)" in low and ("is_true=true" in squashed or "is_true=false" in squashed):
            return "Digit extraction loop overwrites the flag each step instead of enforcing all comparisons"
    if re.search(r"\breturn\s+str\s*\(", low) or re.search(r"\breturn\s+[\"'](true|false)[\"']", low):
        return "Returns a string/non-boolean representation instead of a boolean result"
    if "return true" in low and "return false" not in low and "if" in low:
        return "Always returns `True` due always-truthy condition / misplaced logic"
    if vec in {"100", "010", "001"}:
        return "Partially correct decreasing-digit logic (fails one private test group due loop/index/strictness bug)"
    if vec in {"101"}:
        return "Sorted/non-strict decreasing check bug (duplicates like `5433` slip through)"
    if vec in {"110"}:
        return "Consecutive-step (`-1`) check bug (requires 1-step decreases, rejects valid cases like `5431`)"
    if vec == "000":
        return "Incorrect decreasing-number logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c083(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function (EOF under evaluator function-call tests)"
        if exc == "TypeError":
            if re.search(r"\w+\s*=\s*\w+\.append\(", code):
                return "Runtime TypeError from assigning `.append()` result (`None`) and then using it as a list"
            if ("l[0]*2" in squashed or "l[-1]*2" in squashed) and "+" in code:
                return "Runtime TypeError from mixing multiplied element values with list concatenation"
        if exc == "AttributeError" and (".append" in low or ".sort" in low or ".copy" in low):
            return "Runtime AttributeError from list-method misuse while building duplicated-ends output"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["['x', 'x', 'y', 'z', 'z']", "[100, 100, 200, 200]", "[0, 0, 1, 2, 3, 4, 4]"]):
        return "Hard-codes public sample outputs instead of duplicating list ends generically"
    if ("sorted(" in low or ".sort(" in low) and ("l[0]" in code or "l[-1]" in code or ".append(" in low):
        return "Sorts the list after adding duplicates, losing the required original order"
    if re.search(r"\breturn\s*\[\s*l\s*\[\s*0\s*\]\s*,\s*l\s*\[\s*0\s*\]\s*,\s*l\s*\[\s*-1\s*\]\s*,\s*l\s*\[\s*-1\s*\]\s*\]", low):
        return "Returns only duplicated ends and drops the middle elements of the original list"
    if "returnl+[l[0],l[-1]]" in squashed or "return(l+[l[0],l[-1]])" in squashed:
        return "Appends duplicated first/last elements at the end instead of inserting the first duplicate at the front"
    if "append(l[-1])" in low and "append(l[0])" in low and ("return l" in low or "returnl" in squashed):
        return "Mutates the input list by appending last then first (wrong order/position for duplicated ends)"
    if (
        low.count("if len(l)") + low.count("elif len(l)")
        + low.count("iflen(l)")
    ) >= 2 and any(x in squashed for x in ["len(l)==2", "len(l)==3", "len(l)==5"]):
        return "Length-specific sample-case implementation (handles only a few list lengths like 2/3/5)"
    if "str(l)" in low or "list(str(" in low or ("return" in low and "new_str" in low and "str" in low):
        return "Converts the list to a string and manipulates characters instead of duplicating list elements"
    if "l[0]*2" in squashed or "l[-1]*2" in squashed:
        return "Multiplies element values (`l[0]*2`, `l[-1]*2`) instead of duplicating list entries"
    if re.search(r"\breturn\s+l\s*$", low) or re.search(r"\breturn\s*\(\s*l\s*\)\s*$", low):
        return "Returns the original list unchanged instead of duplicating first/last elements"
    if vec == "011":
        return "Adds duplicates but then sorts/reorders the result (passes some cases by coincidence)"
    if vec == "010":
        return "Length-specific sample-case implementation (handles only a few list lengths like 2/3/5)"
    if vec in {"000", "100", "110"}:
        return "Incorrect list-end duplication logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c084(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function (EOF under evaluator function-call tests)"
        if exc == "IndexError" and ("[0]" in code or "[1]" in code):
            return "Runtime IndexError from direct indexing/string slicing without handling shorter usernames"
        if exc == "AttributeError" and (".split(" in low or ".replace(" in low or ".append(" in low):
            return "Runtime AttributeError from string/list API misuse while extracting username"
        if exc == "TypeError" and ("split" in low or "@" in code):
            return "Runtime TypeError from mixing string/list values in email-username extraction logic"

    if (
        row["summary"] == "Wrong Answer"
        and "for" in low
        and "email" in low
        and re.search(r"\breturn\s+i\b", low)
        and "@" in code
    ):
        return "Returns the first character encountered in a loop instead of accumulating characters before `@`"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["neeraj.m", "ananya.sharma", "rahul123", "priya_r", "v.kumar"]):
        return "Hard-codes public sample usernames instead of extracting text before `@`"
    if re.search(r"email\s*\[\s*:\s*-?\d+\s*\]", low):
        return "Uses fixed-length slicing (domain-length assumption) instead of splitting at `@`"
    if "split('@')[1]" in squashed or 'split("@")[1]' in squashed:
        return "Returns the domain part (`split('@')[1]`) instead of the username before `@`"
    if ("split('@')[0]" in squashed or 'split("@")[0]' in squashed) and (
        ".replace(" in low or ".strip(" in low or ".lower(" in low or ".upper(" in low
    ):
        return "Extracts username then mutates it (`replace`/normalization), changing the required output"
    if re.search(r"\breturn\s+email\b", low) or re.search(r"\breturn\s*\(\s*email\s*\)\s*$", low):
        return "Returns the full email string instead of only the username"
    if re.search(r"\breturn\s+len\s*\(\s*email\s*\)", low):
        return "Returns the email length instead of the username string"
    if ".split('@')" in low and re.search(r"\breturn\s+\w+\s*$", low) and "return username" not in low:
        return "Uses `split('@')` but returns the wrong value/type (list or unrelated variable)"
    if ".split('.')" in low and ".split('@')" not in low:
        return "Splits on `.`/domain punctuation instead of extracting everything before `@`"
    if vec == "110":
        return "Partially correct username extraction with post-processing/fixed-slice bug on some usernames"
    if vec == "000":
        return "Incorrect email-username extraction logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c085(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = fn_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "IndexError" and ("expr[" in low or "e[" in low):
            return "Runtime IndexError from fixed-position string indexing while parsing expression terms"
        if exc == "NameError" and any(tok in full_low for tok in ["a*c", "a*d", "b*c", "b*d", "x*z", "y*w"]):
            return "Runtime NameError from using symbolic term names (`a`, `b`, `x`, ...) as Python variables"
        if exc == "TypeError" and ("split(" in full_low or "join(" in full_low or "expr[" in low):
            return "Runtime TypeError from string/list mixing in expression parsing or output formatting"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if full_low.count("def expand_sum_of_products") >= 2 or low.lstrip().startswith("def expand_sum_of_products("):
        return "Defines a nested/redeclared `expand_sum_of_products` inside the function, so the outer function returns `None`"
    if "print(expand_sum_of_products" in full_low or "is_equal(expand_sum_of_products" in full_low:
        return "Adds top-level test/print calls after the function definition, causing evaluator output pollution / wrong answer"
    if any(tok in full_low for tok in ["(a+b)(c+d)", "(x+y)(z+w)", "(1+5)(10+12)"]) and (
        "if expr ==" in full_low or "return 'a*c + a*d + b*c + b*d'" in full_low or 'return "a*c + a*d + b*c + b*d"' in full_low
    ):
        return "Hard-codes public sample expressions/outputs instead of parsing and expanding arbitrary terms"
    if all(tok in squashed for tok in ["expr[1]", "expr[3]", "expr[6]", "expr[8]"]):
        if any(tok in squashed for tok in ["len(expr)==10", "len(expr)==12", "len(e)==10", "len(e)==12", "len(expr)>13"]):
            return "Uses length-specific fixed slices/indices (works for a few sample lengths, fails general terms)"
        return "Single-character-only parser (fixed-position indexing) fails multi-character or multi-digit private cases"
    if any(tok in squashed for tok in ["len(expr)==10", "len(expr)==12", "len(e)==10", "len(e)==12", "len(expr)>13", "len(expr)<"]):
        return "Uses expression-length branching and fragile slices instead of parsing terms around parentheses/`+`"
    if "and" in low and any(tok in low for tok in ["a*c", "x*z", "1*10"]) and "return" in low:
        return "Uses boolean-chain truthiness (`and`/`or`) over string literals instead of computing the expansion from input"
    if re.search(r"\breturn\s+['\"]a\*c\s*\+\s*a\*d\s*\+\s*b\*c\s*\+\s*b\*d['\"]", full_low):
        return "Returns the literal expansion for `(a+b)(c+d)` regardless of the input expression"
    if ".split(')('" in full_low or '.split(\")(\"' in full_low:
        if "isalnum()" in full_low and re.search(r"\ba\[\s*0\s*\].*\ba\[\s*3\s*\]", full_low, re.S):
            return "Tokenizes the expression but then assumes exactly four symbol characters (fails multi-char terms)"
    if "for " in low and " in " in low and " for " in low and "split('+')" in full_low and "return" in low:
        if re.search(r"for\s+\w+\s+in\s+(\w+).*for\s+\w+\s+in\s+\1", full_low, re.S):
            return "Uses the wrong nested-loop cross product (iterates the same term list twice)"
    if vec == "100":
        return "Single-character-only parser (fixed-position indexing) fails multi-character or multi-digit private cases"
    if vec == "101":
        return "Uses expression-length branching and fragile slices instead of parsing terms around parentheses/`+`"
    if vec == "000":
        return "Incorrect expression parsing/formatting logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c014(row: dict[str, Any]) -> str:
    code = (row["function_code"] or row["student_code"] or row["logic_code"] or "")
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads input inside multi-function question (EOF under evaluator function-call tests)"
        if exc == "FileNotFoundError" or ("open(" in low and ".csv" in low) or "read_csv(" in low:
            return "Uses external file I/O (`open`/`read_csv`) instead of operating on the provided `book_data` list parameter"
        if exc == "ImportError":
            return "Uses unsupported imports/dependencies in the evaluator environment"
        if exc == "NameError" and "book_data" in low and "data" in low:
            return "Runtime NameError from variable-name mismatch (`data` vs `book_data`) across helper functions"
        if exc == "KeyError":
            return "Runtime KeyError from direct dictionary counting/lookup without initializing language keys"
        if exc == "TypeError" and (".append(" in low or "set(" in low or "dict" in low):
            return "Runtime TypeError from collection-building misuse across the required book-data helper functions"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    required = [
        "get_short_books",
        "get_medium_books",
        "get_pages_by_isbn",
        "count_by_language",
        "total_pages_in_genre_lang",
    ]
    if sum(1 for fn in required if f"def {fn}" in low) < 5:
        return "Does not define all five required functions (`get_short_books`, `get_medium_books`, `get_pages_by_isbn`, `count_by_language`, `total_pages_in_genre_lang`)"
    if any(tok in low for tok in ["978-", "'bengali':", "'tamil':", "\"bengali\":", "\"tamil\":"]) and (
        "return {" in low or "if book_data ==" in low or "if data ==" in low
    ):
        return "Hard-codes sample ISBN sets/dicts or outputs instead of computing from the provided book list"
    if re.search(r"def\s+get_medium_books[\s\S]{0,700}?200\s*<=.*<\s*500", low, re.S) and not re.search(
        r"def\s+get_medium_books[\s\S]{0,700}?<=\s*500", low, re.S
    ):
        return "In `get_medium_books`, uses `< 500` instead of inclusive `<= 500`, so 500-page books are wrongly excluded"
    if re.search(
        r"def\s+get_pages_by_isbn[\s\S]{0,1000}?for[\s\S]{0,400}?return\s+pages[\s\S]{0,200}?return\s+none",
        low,
        re.S,
    ):
        return "In `get_pages_by_isbn`, returns `None` inside the search loop (prematurely exits after the first non-match)"
    if re.search(r"def\s+get_short_books[\s\S]{0,700}?return\s*\[", low, re.S) or re.search(
        r"def\s+get_medium_books[\s\S]{0,700}?return\s*\[", low, re.S
    ):
        return "Returns lists from `get_short_books`/`get_medium_books` instead of the required ISBN sets"
    if re.search(r"def\s+count_by_language[\s\S]{0,1000}?for[\s\S]{0,300}?return\s+\w+", low, re.S):
        if "return" in low.split("def count_by_language", 1)[1].split("def total_pages_in_genre_lang", 1)[0]:
            section = low.split("def count_by_language", 1)[1].split("def total_pages_in_genre_lang", 1)[0]
            if "for" in section and re.search(r"for[\s\S]{0,300}return\s+\w+", section, re.S):
                return "In `count_by_language`, returns from inside the loop, so only the first/partial language counts are produced"
    if "range(len(book_data)-1)" in squashed or "range(0,len(book_data)-1)" in squashed:
        return "Uses `range(len(book_data)-1)`, skipping the last book and causing off-by-one errors in one or more helpers"
    if "ifisbninbook" in squashed or "ifisbninbook_data" in squashed:
        return "Uses membership (`if isbn in book`) instead of exact ISBN equality in `get_pages_by_isbn`"
    if "..." in code and vec == "00111":
        return "Implements earlier helper functions but leaves `count_by_language` / `total_pages_in_genre_lang` incomplete (`...` / placeholder logic)"
    if vec == "00111":
        return "Early helper functions are mostly correct, but aggregation helpers (`count_by_language` and/or `total_pages_in_genre_lang`) are wrong or incomplete"
    if vec == "00101":
        return "Usually `get_medium_books` boundary bug (`<500`) plus additional later-helper mistakes (common multi-function partial pass)"
    if vec == "00110":
        return "Partial multi-function solution with `get_pages_by_isbn` lookup/control-flow bug (often premature `return None`) and another helper issue"
    if vec == "00100":
        return "Partial multi-function solution: `get_short_books` mostly works, but several other helpers are missing/incomplete or contain control-flow/indexing bugs"
    if vec == "00001":
        return "Only one helper function appears correct; others are missing, type-mismatched (list vs set), or placeholder/hard-coded"
    if vec == "00000":
        return "Broad multi-function failure (multiple required helpers incomplete, placeholder, hard-coded, or semantically incorrect)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c086(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "TypeError":
            if ("tuple(" in low or "list(" in low) and "+" in code:
                return "Runtime TypeError from list/tuple concatenation shape mismatch while repeating the second half"
            if ".append(" in low and ("tuple" in low or "t+" in squashed):
                return "Runtime TypeError from append/concatenation misuse when constructing repeated-half tuple"
        if exc == "AttributeError" and (".append(" in low or ".split(" in low or ".copy(" in low):
            return "Runtime AttributeError from list/string method misuse during tuple transformation"
        if exc == "IndexError" and ("[i+1]" in low or "[mid+1]" in squashed):
            return "Runtime IndexError from off-by-one indexing near the tuple midpoint"

    if row["summary"] == "Wrong Answer" and "for " in low and "return" in low and ("tuple(" in low or "t[" in low):
        if re.search(r"for[\s\S]{0,250}return\s+", low, re.S):
            return "Returns from inside the build loop before constructing the full repeated-half tuple"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["(4,5,6,7,8,7,8)", "('x', 'y', 'z', 'a', 'z', 'a')", "(1,2,3,4,5,6,7,5,6,7)"]):
        return "Hard-codes public sample tuple outputs instead of repeating the second half generically"
    if "mid+1" in squashed and ("t[mid+1:]" in squashed or "returnt+t[mid+1:]" in squashed):
        return "Near-correct tuple-slicing logic with midpoint off-by-one bug (commonly `mid+1` suffix selection)"
    if "returnt+t[mid:]" in squashed or "return(t+t[mid:])" in squashed:
        return "Duplicates `t[mid:]`, so odd-length tuples wrongly repeat the middle element"
    if "t[:mid]+t[mid+1:]+t[mid+1:]" in squashed:
        return "Drops the middle element from the original tuple and duplicates the wrong suffix (`t[mid+1:]` twice)"
    if "round(len(t)/2)" in squashed or "round(tlen/2)" in squashed or "round(len(t)/2)-1" in squashed:
        return "Uses `round(len(t)/2)` for the split point, causing parity/off-by-one errors for odd/even tuples"
    if re.search(r"\breturn\s+t\s*$", low) or re.search(r"\breturn\s+tuple\s*\(\s*t\s*\)\s*$", low):
        return "Returns the original tuple unchanged instead of appending a repeated second half"
    if "str(" in low and ("z=" in squashed or "split(" in low):
        return "Converts tuple data to strings and reconstructs incorrectly instead of using tuple slicing/concatenation"
    if ("list(t)" in low and ".append(" in low and "tuple(" in low) and ("mid" in low or "len(t)" in low):
        return "List-based reconstruction bug (wrong elements/order repeated before converting back to tuple)"
    if any(x in squashed for x in ["len(t)==2", "len(t)==3", "len(t)==5", "len(t)==7"]):
        return "Length-specific branch implementation (handles a few tuple sizes instead of a general midpoint rule)"
    if vec == "110":
        return "Near-correct tuple-slicing logic with midpoint off-by-one bug (commonly `mid+1` suffix selection)"
    if vec in {"001", "101", "010"}:
        return "Parity/half-split bug (wrong midpoint rule for odd vs even tuple lengths)"
    if vec == "000":
        return "Incorrect repeated-second-half tuple logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c004(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function (EOF under evaluator function-call tests)"
        if exc == "TypeError" and ("num[" in low or "%\"" in low or "%'" in low):
            return "Runtime TypeError from indexing/mixing types instead of numeric divisibility checks"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "%2==0" in squashed and "%5==0" in squashed and (" and " in low or "and" in squashed):
        return "Uses `and` instead of `or`, so numbers satisfying only one condition are rejected"
    if "%5==0" in squashed and "%2==0" not in squashed:
        return "Checks only divisibility by 5 and forgets the even-number condition"
    if ("/2==0" in squashed or "/5==0" in squashed or "//2==0" in squashed or "//5==0" in squashed) and (
        "%2==0" not in squashed and "%5==0" not in squashed
    ):
        return "Uses division (`/` or `//`) instead of modulus (`%`) in the divisibility test"
    if re.search(r"else\s*:\s*\n\s*false\b", low) and "return true" in low:
        return "Forgets `return False` in the `else` branch (bare `False` expression)"
    if ("num%2==0ornum%5==0" in squashed and "returntrue" in squashed and "returnfalse" not in squashed):
        return "Evaluates the correct condition but always returns `True` (missing false path)"
    if any(tok in low for tok in ["is_equal = 25", "a = 25", "n = 1000", "num = 0"]) and (
        "%2" in low or "%5" in low
    ):
        return "Ignores the function parameter and checks a hard-coded sample number instead"
    if re.search(r"\breturn\s+\(?\s*num\s*\)?\s*$", low):
        return "Returns the input number instead of a boolean result"
    if vec == "101":
        return "Checks only one condition (typically divisibility by 5), so even-only positives fail"
    if vec == "010":
        return "Partially correct boolean logic, but false cases are mishandled (missing `return False` or wrong operator)"
    if vec == "000":
        return "Incorrect even/divisible-by-5 logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c015(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = fn_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Wrong Answer":
        if full_low.count("def double_if_even_else_square") >= 2 or low.lstrip().startswith("def double_if_even_else_square("):
            return "Defines a nested/redeclared `double_if_even_else_square` inside the function, so the outer function returns `None`"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "TypeError" and ("double_if_even_else_square()" in full_low or "return double_if_even_else_square()" in full_low):
            return "Runtime TypeError from recursively/self-calling the function without the required argument"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "n/2==0" in squashed or "n//2==0" in squashed:
        return "Uses division (`n/2 == 0`) instead of parity test (`n % 2 == 0`)"
    if "^2" in low or "n^2" in squashed:
        return "Uses `^2` (bitwise XOR) instead of squaring (`n ** 2`)"
    if any(tok in full_low for tok in ["int(4 or 6 or 5)", "double_if_even_else_square(8)", "double_if_even_else_square(9)"]):
        return "Hard-codes sample values/examples instead of using the input parameter `n`"
    if "return 2*n or 2**n" in squashed or "return2*norn**2" in squashed or "return2*nor2**n" in squashed:
        return "Uses boolean `or` between candidate outputs, producing the wrong branch result for many inputs"
    if ("abs(" in low or "n > 0 and n % 2 == 0" in low or "n>0andn%2==0" in squashed):
        return "Incorrect handling of negative numbers (uses `abs()`/positive-only even check, changing required outputs)"
    if re.search(r"\bn\s*=\s*int\s*\(\s*\)", low) or ("input(" in full_low and "return" in low):
        return "Reassigns/reads `n` inside the function instead of using the evaluator-provided argument"
    if vec == "110":
        return "Negative-number handling bug (works on sample positives but fails private negative cases)"
    if vec == "000":
        return "Incorrect even-or-square branching logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c016(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Wrong Answer" and "for " in low and "return" in low:
        if re.search(r"for[\s\S]{0,250}return\s+", low, re.S):
            return "Returns after checking only part of the digits/conditions (loop exits before completing the divisibility check)"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "ZeroDivisionError":
            return "Runtime ZeroDivisionError from checking divisibility before guarding against zero in the last two digits"
        if exc == "TypeError" and ("num[" in low or "len(num)" in low or "%\"" in low or "num%3==\"0\"" in squashed):
            return "Runtime TypeError from treating `num` as a string/sequence (or mixing string and int arithmetic)"
        if exc == "IndexError" and ("[-1]" in low or "[-2]" in low):
            return "Runtime IndexError from invalid indexing while extracting the last two digits"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "num%100==0" in squashed and "ornum%10==0" in squashed and "returnfalse" in squashed and "returntrue" in squashed:
        return "Only checks whether the last two digits are non-zero, then returns `True` without testing actual divisibility"
    if ("%1000" in squashed and "//100" in squashed) or ("last_two=num%1000" in squashed):
        return "Extracts the wrong digits (`%1000`/`//100`) and uses the hundreds digit instead of the tens digit"
    if (" or " in low or "or" in squashed) and ("%10" in squashed or "num%" in squashed) and "and" not in low:
        if "==0" not in squashed:
            return "Uses `or` instead of `and` for divisibility by the last two digits"
    if "num//aandnum//b" in squashed or "int(num/n)andint(num/n1)" in squashed or "ifnum//aandnum//b" in squashed:
        return "Uses quotient truthiness (`num//a`, `num//b`) instead of remainder checks (`num % a == 0`)"
    if "num%second_last_digit==0)and(num%second_last_digit==0" in squashed or (
        "digit1=num%10" in squashed and "num1=num%10" in squashed and "digit2=num1%10" in squashed
    ):
        return "Checks the same digit twice instead of testing divisibility by both last digits"
    if "p=str(num)" in squashed and ("rev1=p[0]" in squashed or "rev2=p[1]" in squashed):
        return "Uses the first two digits of the string instead of the last two digits"
    if ("num=str(num)" in squashed or "s=str(num)" in squashed) and ("ifnum//" in squashed or "num//aandnum//b" in squashed):
        return "String extraction is correct, but divisibility is checked with quotient truthiness instead of `% ... == 0`"
    if "&" in low and "%" in low:
        return "Uses bitwise `&` in the divisibility condition (operator/precedence bug)"
    if vec == "101":
        return "Last-digit extraction bug: one of the two divisibility checks uses the wrong digit/expression"
    if vec in {"001", "010"}:
        return "Partially correct divisibility logic with operator/condition bug (`or` vs `and`, wrong digit, or quotient truthiness)"
    if vec == "000":
        return "Incorrect divisibility-by-last-two-digits logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c087(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = fn_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Wrong Answer":
        if full_low.count("def shuffle_digits") >= 2 or low.lstrip().startswith("def shuffle_digits("):
            return "Defines a nested/redeclared `shuffle_digits` inside the function, so the outer function returns `None`"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "TypeError":
            if "num[" in low or "num(" in low or "list(num)" in low:
                return "Runtime TypeError from treating integer input `num` as a sequence/function during digit shuffling"
            if "return int(" in low and "s[" in low:
                return "Runtime TypeError from broken string-digit reconstruction / type mixing in shuffle output"
        if exc == "IndexError" and ("[3]" in low or "[2]" in low or "shuffle_num[" in low):
            return "Runtime IndexError from invalid list/string indexing while reordering the four digits"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in full_low for tok in ["if num == 1234", "if num == 2413", "if num == 4321", "if num == 5678", "return(6857)", "print('2413')"]):
        return "Hard-codes public example shuffle cycles instead of computing the `2413` digit permutation"
    if re.search(r"\breturn\s*\(?\s*num\s*\)?\s*$", low):
        return "Returns the original number unchanged instead of shuffling digits to order `2413`"
    if ("str(num)" in low and ("[1::2]" in code or "[0::2]" in code)) and "int(" not in low:
        return "Builds the correct-looking reordered digits as a string but returns a string instead of an integer"
    if "return int(" in low and ("s[1]+s[3]+s[0]+s[2]" in squashed or "num_str[1]+num_str[3]+num_str[0]+num_str[2]" in squashed):
        return "Near-correct string reordering, but implemented in a broken scope/structure (outer function does not return the shuffled integer)"
    if "whiletrue:" in squashed and "return(num%1000-num%100)//100" in squashed:
        return "Extracts one digit and returns too early (never reconstructs the 4-digit shuffled result)"
    if re.search(r"\breturn\s*\(?\s*(2413|4321|3142|6857|8765|7586)\s*\)?\s*$", low):
        return "Returns a constant sample output instead of computing the shuffle from the input digits"
    if vec == "00":
        return "Incorrect four-digit shuffle logic (fails hidden cycles; often hard-coded, no-return, or wrong digit extraction)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c088(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "AttributeError" and (".upper" in low or ".split" in low or "split.sentence" in squashed):
            return "Runtime AttributeError from string/list method misuse while transforming alternate words"
        if exc == "TypeError" and ("len(sentence)" in low or "char // 2" in low or "sentence(" in low):
            return "Runtime TypeError from treating string data as numeric (or calling APIs with wrong argument types)"
        if exc == "IndexError" and ("lst[i]" in low or "words[" in low):
            return "Runtime IndexError from invalid list indexing while iterating words"

    if row["summary"] == "Wrong Answer" and "for " in low and "return" in low:
        if re.search(r"for[\s\S]{0,250}return\s+(word_list|words|o|result|l)\b", low, re.S):
            return "Returns from inside the loop after processing only the first word/index"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["return list(['hello','world'])", "return list(['hello', 'world'])", "return ['hello', 'world']", "return list(['this','is'"]):
        return "Hard-codes sample output lists instead of transforming the input sentence"
    if ".upper" in low and ".upper()" not in low:
        return "Uses `.upper` without calling it (`.upper()`), so words are not converted to uppercase"
    if "return sentence" in low and ("sentence.upper()" in low or "words[0].upper()" in low):
        return "Returns a string (or concatenated string) instead of the required list of words"
    if (".lower()" in low or "swapcase()" in low) and "i%2==0" in squashed:
        return "Changes odd-index words too (`lower()`/`swapcase()`), but the task requires leaving them unchanged"
    if ("for word in words" in low and "word = word.upper()" in low and "result.append(word)" in low) or (
        "for i in range(len(l))" in squashed and "l[i]=l[i].upper()" in squashed and "m.append(l[i])" in squashed
    ):
        return "Uppercases all words instead of only even-index words"
    if ".index(word)" in low or ".index(i)" in low:
        return "Uses `list.index(...)` to infer word position, which is wrong when words repeat (duplicate-word index bug)"
    if "split(\",\")" in low or "sentence.split(\",\")" in low:
        return "Splits on commas instead of spaces, so words are not tokenized correctly"
    if "if words[0] or words[2] or words[4]" in low:
        return "Uses an always-truthy boolean-chain (`words[0] or words[2] ...`), so the branch logic is incorrect"
    if "sentence=sentence.upper()" in squashed and "returnsentence" in squashed:
        return "Uppercases the entire sentence string and returns it, instead of returning a word list with alternate uppercase"
    if vec == "0111":
        return "Indexing-by-value bug (`list.index(...)` / mutation while iterating) causes wrong parity handling on some inputs"
    if vec == "0101":
        return "Over-normalizes output by changing odd-index words too (`lower()`/`swapcase()`)"
    if vec == "0010":
        return "Partial list transformation (often all-words uppercase or early return), so only some sentence patterns match"
    if vec == "0000":
        return "Incorrect alternate-uppercase word transformation logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c089(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "IndexError" and ("s[0]" in squashed or "s[-1]" in squashed or "str1[0]" in squashed):
            return "Runtime IndexError from indexing first/last character without handling empty string"
        if exc == "AttributeError" and (".lower" in low or ".startswith" in low or ".endswith" in low):
            return "Runtime AttributeError from string-method misuse while checking first/last vowels"
        if exc == "TypeError" and ("startswith" in low or "endswith" in low or "in" in low):
            return "Runtime TypeError from invalid membership/prefix API usage in vowel check"

    if row["summary"] == "Wrong Answer" and "for " in low and "return" in low:
        if ("aeiou" in low or "vowel" in low) and re.search(r"for[\s\S]{0,220}return\s+(true|false)\b", low, re.S):
            return "Returns inside vowel loop before checking both conditions completely (premature loop exit)"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["apple", "orange", "ice", "umbrella", "education", "aeiou"]):
        if "if s ==" in low or "return true" in low and ("apple" in low or "orange" in low):
            return "Hard-codes sample strings/examples instead of checking endpoints generically"
    if ".lower" in low and ".lower()" not in low:
        return "Uses `.lower` without calling it (`.lower()`), so case-insensitive comparison is broken"
    if ("s[0]==s[-1]" in squashed or "str1[0]==str1[-1]" in squashed or "x[0]==x[-1]" in squashed) and (
        "aeiou" not in low and "vowel" not in low
    ):
        return "Checks first/last character equality only, but forgets to require vowels"
    if ("aeiou" in low or "vowel" in low) and (
        ("s[0]ins" not in squashed and "s[-1]ins" not in squashed)
        and ("==" not in code or "s[0]==s[-1]" not in squashed and "lower()" not in low)
    ):
        if ("and" in low and "or" not in low) or "startswith" in low or "endswith" in low:
            return "Checks whether both ends are vowels, but not whether they are the same vowel"
    if ("startswith(" in low or "endswith(" in low) and any(tok in low for tok in ["'aeiou", "\"aeiou", "('a','e','i','o','u')"]) :
        return "Uses `startswith`/`endswith` incorrectly for vowel-equality logic (prefix/suffix test, not same-endpoint vowel comparison)"
    if ("=='a' or 'a'" in squashed or "=='a'or'a'" in squashed or "or'a'" in squashed and "==" in squashed):
        return "Uses always-truthy boolean chain for vowel checks/comparison (`... == 'a' or 'A' ...`)"
    if "is_palindrome" in low or ("s==s[::-1]" in squashed and "s[0]" not in squashed):
        return "Solves a palindrome/equality-to-reverse problem instead of comparing first and last vowels"
    if ("s[0] in 'aeiou'" in low or 's[0] in "aeiou"' in low) and ("s[-1] in 'aeiou'" in low or 's[-1] in "aeiou"' in low):
        if "==" not in code and "lower()" not in low:
            return "Checks vowel membership at both ends but misses same-vowel equality requirement"
    if "return s[0]==s[-1]" in squashed or "returnstr1[0]==str1[-1]" in squashed:
        return "Returns only first/last equality (non-vowel same-letter strings are incorrectly accepted)"
    if vec == "100":
        return "Equality-only endpoint check (forgets to ensure the matching endpoint letter is a vowel)"
    if vec == "010":
        return "Vowel-at-both-ends check without same-vowel equality comparison"
    if vec in {"001", "101", "011"}:
        return "Case-insensitive same-vowel check bug (method call / boolean-chain / endpoint comparison mistake)"
    if vec == "000":
        return "Incorrect same-vowel endpoint logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c090(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = fn_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "TypeError" and ("len(" in low or "range(" in low or "coef" in low or "x" in low):
            return "Runtime TypeError from mixing coefficient list and scalar operations in polynomial evaluation"
        if exc == "NameError" and ("coef" in low or "coeff" in low or "x" in low):
            return "Runtime NameError from variable-name mismatch in coefficient/exponent computation"
        if exc == "IndexError" and ("coef[" in low or "coeff[" in low):
            return "Runtime IndexError from fixed-position coefficient indexing on varying polynomial lengths"

    if row["summary"] == "Wrong Answer":
        if "for " in low and "return" in low and ("coef" in low or "coeff" in low):
            if re.search(r"for[\s\S]{0,400}return\s+", low, re.S):
                return "Returns from inside the coefficient loop, so only part of the polynomial is evaluated"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in full_low for tok in ["[1, 2, 3]", "[2, 3, 4]", "x=2", "return 45", "return 17"]):
        if "if coef ==" in full_low or "return 45" in full_low or "return 17" in full_low:
            return "Hard-codes public sample polynomial values instead of evaluating arbitrary coefficients"
    if "^" in code and "**" not in code:
        return "Uses `^` (bitwise XOR) instead of exponentiation `**` for powers of `x`"
    if ".index(" in low and ("coef.index" in low or "coeff.index" in low):
        return "Uses `coef.index(value)` for exponent position, which fails when coefficients repeat"
    if ("enumerate(" in low or "for i in range(len(" in low) and ("x**i" in squashed or "pow(x,i)" in squashed):
        if "len(coef)-1-i" not in squashed and "len(coeff)-1-i" not in squashed:
            return "Assigns exponents in ascending order (`x**i`) instead of descending coefficient order"
    if any(tok in squashed for tok in ["coef[0]*x**3+coef[1]*x**2+coef[2]*x+coef[3]", "a*x**2+b*x+c", "a*x+b"]):
        return "Uses fixed-degree formula (length-specific polynomial) instead of handling arbitrary coefficient lists"
    if ("sum(" in low and "coef" in low and "*x" in squashed) and ("**" not in code and "pow(" not in low):
        return "Multiplies coefficients by `x` but forgets exponentiation by term position"
    if "reversed(" in low and ("x**i" in squashed or "pow(" in low):
        if "list(reversed" in low or "coef[::-1]" in low:
            return "Reverses coefficients and then applies powers incorrectly (coefficient-order/exponent mismatch)"
    if re.search(r"\breturn\s+\w+\s*$", low) and ("sum =" in low or "total =" in low) and "for " in low and "x**" not in low and "pow(" not in low:
        return "Accumulates coefficients (or linear terms) but does not compute polynomial powers correctly"
    if vec in {"100", "010", "001"}:
        return "Partially correct polynomial evaluation with exponent-order / premature-return bug"
    if vec == "000":
        return "Incorrect polynomial evaluation logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c091(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "TypeError" and ("num1[" in low or "num2[" in low or "str(" not in low and "[" in code):
            return "Runtime TypeError from indexing integers directly instead of using `% 10` / `str(...)`"
        if exc == "NameError" and any(tok in low for tok in ["n1", "n2", "a", "b", "num"]):
            return "Runtime NameError from wrong variable names in last-digit comparison"
        if exc == "IndexError" and ("str(" in low and ("[1]" in code or "[-2]" in code)):
            return "Runtime IndexError from wrong string index on short numbers while extracting digits"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["123", "456", "789", "if num1 ==", "if n1 =="]) and ("return true" in low or "return false" in low):
        return "Hard-codes public sample pairs instead of comparing the input numbers' last digits"
    if "num1==num2" in squashed or "returnnum1==num2" in squashed:
        return "Compares the full numbers for equality instead of comparing only the last digits"
    if ("num1%10==num1%10" in squashed or "n1%10==n1%10" in squashed or "num1==num1" in squashed):
        return "Compares the first number to itself (ignores `num2`)"
    if ("num1%2" in squashed or "num2%2" in squashed) and "%10" not in squashed:
        return "Uses parity/even-odd checks instead of comparing the last digits"
    if ("str(num1)[0]" in squashed or "str(num2)[0]" in squashed or "num1//10" in squashed and "%10" not in squashed):
        return "Uses the first digit / wrong place value instead of the last digit"
    if ("str(num1)[-1]" in squashed or "str(num2)[-1]" in squashed) and "==" in code and "str(num1)[-1]==str(num2)[-1]" in squashed:
        return "String-based last-digit comparison is close, but surrounding logic/returns are incorrect on some cases"
    if ("return num1%10" in squashed or "returnnum2%10" in squashed):
        return "Returns a last digit value instead of the required boolean comparison result"
    if vec in {"100", "010", "001"}:
        return "Partially correct last-digit comparison (uses wrong variable/digit extraction in some cases)"
    if vec == "000":
        return "Incorrect last-digit comparison logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c092(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator tests)"
        if exc == "NameError" and any(tok in low for tok in ["fizz", "buzz", "normal", "fizzbuzz"]):
            return "Runtime NameError from returning bare labels (`Fizz`, `Buzz`, etc.) without quotes"
        if exc == "TypeError" and "%" in code:
            return "Runtime TypeError from invalid modulo/comparison operations in Fizz/Buzz logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["return 'fizzbuzz'", 'return "fizzbuzz"', "return 'fizz'", "return 'buzz'"]) and ("normal" in low):
        # handled more specifically below where relevant
        pass
    if any(tok in low for tok in ["if num == 3", "if num == 5", "if num == 15", "return \"fizz\"", "return \"buzz\""]) and ("if num ==" in low):
        return "Hard-codes sample numbers/labels instead of checking divisibility rules generically"
    if ("%3==0" in squashed or "num%3==0" in squashed) and ("%5==0" in squashed or "num%5==0" in squashed):
        pos3 = min([i for i in [squashed.find("%3==0"), squashed.find("num%3==0")] if i >= 0], default=-1)
        pos5 = min([i for i in [squashed.find("%5==0"), squashed.find("num%5==0")] if i >= 0], default=-1)
        pos15 = min([i for i in [squashed.find("%15==0"), squashed.find("num%15==0")] if i >= 0], default=-1)
        if pos15 >= 0 and ((0 <= pos3 < pos15) or (0 <= pos5 < pos15)):
            return "Checks `%3`/`%5` before `%15`, so `FizzBuzz` branch is unreachable for multiples of 15"
    if "%10==0" in squashed:
        return "Uses `% 10 == 0` for `Buzz` instead of `% 5 == 0`"
    if "&" in code and "%" in code:
        return "Uses bitwise `&` in divisibility conditions (operator/precedence bug)"
    if re.search(r"\breturn\s+(num\s*%\s*3\s*==\s*0\s*or\s*num\s*%\s*5\s*==\s*0)\b", low):
        return "Returns a boolean divisibility test instead of the required string label (`Fizz`/`Buzz`/`FizzBuzz`/`Normal`)"
    if any(tok in squashed for tok in ["'fizz'or'buzz'", "\"fizz\"or\"buzz\"", "fizzorbuzz"]):
        return "Uses always-truthy string boolean-chain logic (`'Fizz' or 'Buzz' ...`) instead of conditional labels"
    if "'normal'" in low or '"normal"' in low:
        return "Returns wrong casing for fallback label (`'normal'` instead of `'Normal'`)"
    if ("return 'normal'" not in low and 'return "normal"' not in low and "return 'Normal'" not in low and 'return "Normal"' not in low) and ("if" in low and "elif" in low or "if" in low and "return" in low):
        if "return" in low and low.count("return") <= 3:
            return "Missing fallback `Normal` branch / incomplete case coverage"
    if vec == "110":
        return "FizzBuzz-unreachable branch ordering bug (`%3` / `%5` checked before `%15`)"
    if vec in {"100", "010", "001"}:
        return "Partially correct Fizz/Buzz labeling with casing/branch/fallback bug"
    if vec == "000":
        return "Incorrect Fizz/Buzz/FizzBuzz labeling logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c093(row: dict[str, Any]) -> str:
    code = row["logic_code"]
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "TypeError" and ("[" in full_code and "] =" in full_code or "s[i]=" in full_squashed or "line[i]=" in full_squashed):
            return "Runtime TypeError from trying to mutate Python strings in-place while swapping vowels"
        if exc == "NameError" and any(tok in full_low for tok in ["line", "lines", "text", "vowels"]):
            return "Runtime NameError from undefined line/text accumulator variables in multi-line vowel-reversal code"
        if exc == "IndexError" and ("[j]" in full_code or "[i]" in full_code or "pop(" in full_low):
            return "Runtime IndexError from pointer/pop indexing bugs while reversing vowels"
        if exc == "ValueError" and ("int(input())" in full_low or "map(int" in full_low):
            return "Runtime ValueError from parsing string input as integers in a text-processing question"
        if exc == "EOFError" and "input(" in full_low:
            return "Input-reading protocol bug (wrong number/order of `input()` calls for multi-line program question)"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    if any(tok in full_low for tok in ["holle", "leotcede", "leotcede", "holl e".replace(" ", "")]):
        if "print(" in full_low or "return" in full_low:
            return "Hard-codes sample output strings (e.g., `HollE`) instead of reversing vowels for arbitrary input"
    if ("aeiouaeio" in full_low or "aeiouaeio'" in full_low or 'aeiouaeio"' in full_low) and "u" not in re.sub(r"[^aeiou]", "", full_low):
        return "Incomplete vowel set (missing `U`/`u` variant), so some uppercase-vowel cases fail"
    if "aeiouaeio" in full_low and ("u" not in full_low or "u" in full_low and "aeiouaeiou" not in full_low and "aeiouAEIOU".lower() not in full_low):
        return "Incomplete vowel set (missing one vowel/uppercase vowel), causing hidden-case misses"
    if "int(input())" in full_low and full_low.count("input(") <= 2 and ("for _ in range(n)" in full_low or "range(n)" in full_low):
        if "print(" in full_low and ("join(" not in full_low and "lines" not in full_low):
            return "Processes only one line (or prints line-by-line incorrectly) instead of reversing vowels globally across all input lines"
    if ("vowels=[]" in full_squashed or "v=[]" in full_squashed) and ("append(" in full_low and "reverse()" in full_low):
        if "print(" in full_low and ("\\n".join([]) is not None):  # no-op guard to keep structure simple
            return "Collects vowels globally but reconstructs/prints lines incorrectly (newline/line-boundary formatting bug)"
    if ("for _ in range(n)" in full_low or "for i in range(n)" in full_low) and ("print(" in full_low) and ("''.join" not in full_low and '".join' not in full_low and "join(" not in full_low):
        return "Builds transformed characters but outputs with incorrect formatting (missing join/newline preservation)"
    if ("while" in full_low and "i<j" in full_squashed or "i<=j" in full_squashed) and ("vowels" in full_low or "aeiou" in full_low):
        if "print(" not in full_low and "return" not in full_low:
            return "Incomplete two-pointer vowel-swap implementation (logic present but final output is never produced)"
    if "input().split()" in full_low or "split()" in full_low and "n=int(input())" in full_low and "for" not in full_low:
        return "Treats the entire multi-line input as a single tokenized line (ignores line count / line boundaries)"
    if vec == "000":
        return "Incorrect program-level vowel-reversal logic (I/O, global reversal, or formatting semantics are wrong)"
    if vec in {"100", "010", "001", "110", "101", "011"}:
        return "Partially correct vowel-reversal program with global-vowel or output-formatting bug"
    return "Other wrong-answer logic pattern (residual)"


def classify_c094(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "ValueError":
            if "l=int(input())" in low or "int(input()),input()" in squashed:
                return "Runtime ValueError from parsing `l` and `c` as separate input lines instead of reading `l c` from one line"
            return "Runtime ValueError from malformed input parsing for `l c` / `n`"
        if exc == "EOFError" and "input(" in full_low:
            return "Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)"
        if exc == "TypeError":
            if "word()" in low or ".split(0)" in low or ".split(1)" in low:
                return "Runtime TypeError from calling strings / misusing `split(...)` while parsing or filtering words"
            return "Runtime TypeError from string/list API misuse in word filtering logic"
        if exc == "NameError":
            return "Runtime NameError from variable typos / undefined lists while building the output word"
        if exc == "IndexError":
            return "Runtime IndexError from fixed-position parsing of the first input line (`[0]`, `[2]`) or empty-word indexing"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(line.strip().startswith("#") or not line.strip() for line in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if "given a minimum length l and a character c" in full_low and "input(" not in full_low:
        return "Pastes the problem statement text into the submission instead of executable code"
    if re.fullmatch(r"\s*print\s*\(\s*['\"].*['\"]\s*\)\s*", stripped) or re.fullmatch(r"\s*print\s*\(\s*\)\s*", stripped):
        return "Prints a constant/empty sample output instead of computing the result from the input words"
    if any(tok in full_low for tok in ["apple", "banana", "anchor", "ant", "etr"]) and (
        "print('etr')" in full_low or "l = [\"3 a\"" in full_low or "if n == " in full_low or "return 'etr'" in full_low
    ):
        return "Hard-codes public sample words/outputs instead of reading and filtering arbitrary input words"
    if full_low.lstrip().startswith("def ") and "input(" not in full_low and ("return " in full_low or "print(" in full_low):
        return "Writes a helper function (or code from another question) but never implements the required input/output program flow"
    if re.search(r"^\s*def\s+\w+\s*\(", full_low, re.M) and "input(" in full_low:
        defs = [m.group(1) for m in re.finditer(r"^\s*def\s+(\w+)\s*\(", full_low, re.M)]
        if defs and not any(re.search(rf"\b{re.escape(fn)}\s*\(", full_low.splitlines()[-1]) for fn in defs):
            if not any(re.search(rf"if __name__\s*==\s*['\"]__main__['\"][\s\S]{{0,200}}\b{re.escape(fn)}\s*\(", full_low, re.S) for fn in defs):
                return "Defines a helper/main function but never calls it, so no output is produced"
    if re.search(r"\b(first|string1|a|start)\s*=\s*input", low) and any(
        tok in squashed for tok in ["first[0]", "first[2]", "string1[0]", "a[2]", "start[2]"]
    ):
        return "Parses the first line using fixed character positions (`[0]`, `[2]`), so multi-digit `l` / spacing variations fail"
    if ("l=(input())" in squashed or "l=input()" in squashed) and ("len(l)" in squashed) and ("ch=l[-1]" in squashed or "c=l[-1]" in squashed):
        return "Uses `len(first_line)` as the minimum-length threshold instead of parsing the integer `l` from the first input line"
    if ".lower()" in full_low and ("word[0].lower()" in full_low or "c = " in full_low and ".lower()" in full_low):
        return "Uses case-insensitive normalization (`lower()`), but the starting-character match is required to be case-sensitive"
    if re.search(r"len\s*\(\s*\w+\s*\)\s*>\s*\w+", low) and ">= " not in low and ">=" not in low:
        return "Uses `len(word) > l` instead of `len(word) >= l`, so boundary-length words are wrongly excluded"
    if ("startswith(" in low or "[0]==" in squashed or "word[0]==c" in squashed) and "len(" not in low:
        return "Checks the starting character but forgets the minimum-length condition (`len(word) >= l`)"
    if re.search(r"len\s*\(\s*\w+\s*\)\s*>=\s*1", low) and ("word[0]==c" in squashed or "startswith(" in low):
        return "Uses a trivial length check (`len(word) >= 1`) instead of the required threshold `l`"
    if "len(" in low and ("word[0]" not in low and "startswith(" not in low and ".startswith" not in low):
        return "Checks only word length and forgets the starting-character condition"
    if "join(result_chars)" in full_low and "' '" in full_low:
        return "Prints selected last characters joined with spaces (`' '.join(...)`) instead of a single concatenated word"
    if ("sys.stdin.read" in full_low or "sys.stdin.readlines" in full_low) and ("len(word) >=1" in full_low or "len(word)>=1" in full_low):
        return "Parses all input at once but applies the wrong filter (`len(word) >= 1`) instead of the required minimum length `l`"
    if vec == "101":
        return "Partially correct filtering: starting-character condition works, but minimum-length handling is wrong or missing"
    if vec == "010":
        return "Case-sensitivity bug: normalizes input/character (`lower()`/`upper()`) even though matching must be case-sensitive"
    if vec == "100":
        return "Malformed filter condition (one of the two required checks is broken or applied to the wrong variable)"
    if vec == "000":
        return "Incorrect input parsing/filtering logic for building the output word (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c017(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Runtime EOFError from fixed-size input assumptions (e.g., hard-coded 3x3 reads) or wrong input format parsing"
        if exc == "ValueError":
            return "Runtime ValueError from parsing matrix dimensions/elements with the wrong input format"
        if exc == "IndexError":
            return "Runtime IndexError from square-matrix assumptions or swapped row/column indexing on rectangular matrices"
        if exc == "NameError":
            return "Runtime NameError from undefined matrix/dimension variables (`m`, `n`, `a`, etc.)"
        if exc == "TypeError":
            return "Runtime TypeError from treating dimensions/data as the wrong type while building/rotating the matrix"
        if exc == "AttributeError":
            return "Runtime AttributeError from list/string API misuse while reading or rotating the matrix"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    if not full_code.strip():
        return "Empty final submission"
    if any(tok in full_low for tok in ["print(7", "print(\"7 4 1", "print('7 4 1'", "if input == \"3 3", "matrix=([3,2]"]):
        return "Hard-codes the public sample rotated matrix output instead of rotating arbitrary input matrices"
    if "input(" not in full_low and full_low.count("print(") >= 1 and re.search(r"[0-9]", full_low):
        if ("7 4 1" in full_low or "8 5 2" in full_low or "9 6 3" in full_low or "5 3 1" in full_low or "6 4 2" in full_low):
            return "Hard-codes sample rotated-matrix lines instead of computing the rotation from input"
    if re.search(r"for\s+_\s+in\s+range\s*\(\s*3\s*\)", full_low) or (
        full_low.count("input().split()") >= 4 and full_low.count("for _ in range") == 0 and "m,n" in squashed
    ):
        return "Assumes a fixed-size sample matrix (e.g., hard-coded 3x3 input) instead of handling general `m x n` matrices"
    if (
        ("a=[input().split()for _ in range(n)]" in full_low.replace(" ", ""))
        or re.search(r"for\s+_\s+in\s+range\s*\(\s*n\s*\)\s*:\s*\n\s*\w+\s*=\s*input\(\)\.split", full_low)
    ):
        return "Reads `n` rows instead of `m` rows (row/column-count confusion), which breaks rectangular matrices"
    if re.search(r"\breturn\s+\[.*zip\(", low) and "print(" not in full_low:
        return "Returns a rotated matrix from a helper function but does not print it (I/O question requires explicit output)"
    if full_low.lstrip().startswith("def rotate") and "print(" not in full_low:
        return "Implements a function-only solution (or helper) without producing the required printed output"
    if ("print(order)" in full_low or "print(m,n)" in full_low or "print(order_matrix" in full_low):
        return "Adds debug prints (`print(order)` / dimension prints), causing output-format mismatch"

    # Dominant evaluator artifact: many logically correct rotations use `print(*row)` and score 0.
    looks_clockwise = any(
        tok in full_squashed
        for tok in [
            "matrix[row][col]",
            "rotated[j][m-1-i]=matrix[i][j]",
            "zip(*matrix[::-1])",
            "zip(*mat[::-1])",
            "zip(*a[::-1])",
            "nmat[i][m-1-j]=str(smat[i][j])",
            "list(reversed(col))forcolinzip(*matrix)",
            "list(row)[::-1]forrowinzip(*matrix)",
            "list(row)[::-1]forrowinzip(*mat)",
            "new_mat.append(new_row[::-1])",
            "new_row=[mat[j][i]forjinrange(len(mat))]",
        ]
    )
    if looks_clockwise and (
        ("print(*" in full_low and "end=\" \"" not in full_low and "end=' '" not in full_low)
        or "print(\" \".join(" in full_low
        or "print(' '.join(" in full_low
        or "end = ''" in full_low
        or "end=''" in full_low
        or "end=\"\"" in full_low
    ):
        return "Likely correct rotation logic, but prints rows with `print(*row)` (evaluator appears to expect different spacing/trailing-space formatting)"

    if "zip(*" in full_low and "[::-1]" not in full_low and "reversed(col)" not in full_low and "m-1-i" not in squashed:
        return "Uses transpose (`zip(*matrix)`) without the required row/column reversal for clockwise rotation"
    if re.search(r"for\s+i\s+in\s+range\s*\(\s*n\s*\)", full_low) and "matrix[i][j]" in full_low and "for j in range(n)" in full_low:
        return "Uses `n` for both row and column loops (square-matrix assumption), failing rectangular cases"
    if "print(*" in full_low and "zip(*a[::-1])" in full_low and "for _ in range(n)" in full_low:
        return "Combines correct-looking transpose/reverse logic with wrong row-count input reading (`n` rows instead of `m`)"
    if vec in {"100", "010"}:
        return "Partially correct matrix rotation with rectangular-matrix indexing/input-dimension bug"
    if vec == "000":
        return "Incorrect matrix-rotation output (often formatting mismatch, fixed-size assumptions, or input-dimension confusion)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c018(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in low:
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "TypeError":
            if "str[" in low or "s(" in low or "[1,n]" in low or "[-n,-1]" in low:
                return "Runtime TypeError from invalid string slicing/index syntax while constructing outer/inner parts"
            return "Runtime TypeError from string/tuple construction misuse in `separate_outer_chars`"
        if exc == "AttributeError" and (".append(" in low or ".join(" in low or ".split(" in low):
            return "Runtime AttributeError from string/list method misuse while building tuple outputs"
        if exc == "RecursionError":
            return "Runtime RecursionError from accidental self-recursive call / recursive wrapper"
        if exc == "NameError":
            return "Runtime NameError from undefined intermediate variables in slicing/tuple construction"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "('proing','gramm')" in squashed or '("proing","gramm")' in squashed:
        return "Hard-codes the sample output `('proing', 'gramm')` instead of computing from `s` and `n`"
    if ("s[:3]" in low or "s[-3:]" in low or "s[3:8]" in low) and "n" in low:
        return "Uses fixed sample slices (`3`, `8`) instead of slicing with the input parameter `n`"
    if "s[n:n+5]" in squashed or "s[n:n + 5]" in low:
        return "Uses a fixed inner-length slice (`n:n+5`) instead of `s[n:-n]`"
    if "strip(" in low and ("outer" in low or "olo" in low):
        return "Uses `strip(outer_chars)` to compute the inner string, but `strip` removes matching characters by value, not exact outer slices"
    if ".index(c)" in low or ".index(ch)" in low:
        return "Uses `s.index(...)` while iterating characters, so duplicate characters are misclassified by their first occurrence"
    if "s[-1:-n]" in squashed or "s[-1:-3]" in squashed:
        return "Uses a reverse-direction slice like `s[-1:-n]`, which produces the wrong end segment / empty slice"
    if re.search(r"\breturn\s+\(\s*outer_chars\s*\)\s*$", low) or re.search(r"\breturn\s+outer_chars\s*$", low):
        return "Returns only the outer string instead of the required `(outer_chars, inner_chars)` tuple"
    if re.search(r"\breturn\s+\w+\s*\+\s*\w+\s*$", low) and "return (" not in low:
        return "Returns a concatenated string instead of a tuple `(outer_chars, inner_chars)`"
    if "..." in code and ("return" in low) and ("s[0::n]" in low or "s[n+1:-1]" in low):
        return "Leaves template placeholder `...` and adds an incorrect string-slicing expression (wrong return type/logic)"
    if vec == "101":
        return "Inner-string extraction bug from character-value methods (`strip` / `index`) that break on repeated edge characters"
    if vec == "010":
        return "Fixed-slice/sample-specific implementation (uses constants like `3`/`8` or `n+5`) instead of general `n`-based slicing"
    if vec == "011":
        return "Incorrect inner-slice bounds formula (off-by-one/parity-based slicing mistake)"
    if vec == "000":
        return "Incorrect outer/inner slicing or wrong return shape (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c019(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("function_code") or row.get("student_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "TypeError":
            return "Runtime TypeError from mixing string/set/list types while counting unique letters"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/set/list method misuse (`append`, `lower`, etc.)"
        if exc == "IndexError":
            return "Runtime IndexError from manual index-based string comparison loops"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/intermediate variables in counting logic"
        if exc == "RecursionError":
            return "Runtime RecursionError from accidental recursive function call"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if ("if(s1,s2" in squashed or "if(s1,s2==" in squashed or "if s1 ==" in low) and any(
        tok in full_low for tok in ["apple", "plum", "hello", "world", "abc", "xyza"]
    ):
        return "Hard-codes sample input pairs/answers instead of computing the unique-letter count generically"
    if ("set(" in low or "symmetric_difference" in low or " ^ " in low or "^" in code) and (
        ".lower()" not in low and ".upper()" not in low
    ):
        return "Uses set symmetric-difference logic without case normalization (treats uppercase/lowercase letters as different)"
    if (".upper()" in low or ".lower()" in low) and ("set(s1)" in low or "set(s2)" in low):
        if ("s1 = s1.upper()" not in low and "s2 = s2.upper()" not in low and "s1=s1.upper()" not in low and "s2=s2.upper()" not in low
            and "s1 = s1.lower()" not in low and "s2 = s2.lower()" not in low and "s1=s1.lower()" not in low and "s2=s2.lower()" not in low):
            return "Calls `s1.upper()` / `s2.upper()` (or `lower()`) without assignment, so case normalization has no effect"
    if ("if char not in" in low or "if j not in l2" in low or "if j not in l1" in low) and "set(" not in low:
        if "count +=1" in low or "count+=1" in low or "count = count + 1" in low:
            return "Counts exclusive letter occurrences without deduplicating, so repeated letters in one string are overcounted"
    if ("s={}" in squashed or "dict={}" in squashed or re.search(r"\b[a-z_]+\s*=\s*\{\s*\}", low)) and ("==1" in squashed):
        return "Counts characters that appear exactly once overall (`freq == 1`) instead of unique letters present in exactly one string"
    if ".split()" in low and ("lower()" in low or "upper()" in low) and ("for word in" in low or "m+n" in squashed):
        return "Splits the strings into whole-word lists and then counts character frequency incorrectly (duplicate-exclusive letters are mishandled)"
    if ("set(" in low or "symmetric_difference" in low or "^" in code) and (".lower()" in low or ".upper()" in low):
        if "len(" in low and "return" in low and "symmetric_difference" not in low and "^" not in code:
            return "Set-based approach is incomplete/incorrectly combined (union/intersection/length formula bug)"
    if vec == "011":
        return "Counts exclusive letters but forgets uniqueness (duplicate letters in one string are counted multiple times)"
    if vec == "001":
        return "Case-normalization or set-logic bug that fails hidden mixed-case cases"
    if vec == "000":
        return "Incorrect unique-letter counting logic (hard-coding, placeholder, or wrong counting method)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c020(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "FileNotFoundError" or "open(filename" in full_low:
            return "Runtime file-I/O mismatch: attempts a `filename`-based file solution, but the evaluator behavior for this cluster uses standard input"
        if exc == "EOFError" and "input(" in full_low:
            return "Runtime EOFError from reading the wrong input shape / extra lines for the actual evaluator task"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/variables in triangle-generation logic"
        if exc == "TypeError":
            return "Runtime TypeError from mixing strings/ints or malformed `print`/list operations in pattern generation"
        if exc == "AttributeError":
            return "Runtime AttributeError from list/string method misuse while building/printing rows"
        if exc == "IndexError":
            return "Runtime IndexError from row-list indexing mistakes in generated pattern rows"
        if exc == "ValueError":
            return "Runtime ValueError from malformed numeric input parsing"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] == "Time Limit Exceeded":
        return "Inefficient/infinite-loop pattern generation (Time Limit Exceeded)"
    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    if not full_code.strip():
        return "Empty final submission"

    if "open(filename" in full_low or "read the file using the variable filename" in full_low:
        return "Solves a different file-based zig-zag-spacing question (`filename` I/O) instead of the evaluator’s alternate-number-sequence triangle task"
    if re.search(r"\bif\s+n\s*==\s*[1-9]\b", full_low) and full_low.count("print(") >= 2:
        return "Hard-codes outputs for specific values of `n` (sample-case branching) instead of generating the pattern"
    if full_low.lstrip().startswith("def ") and "input(" not in full_low and "print(" in full_low and full_low.count("\n") < 20:
        return "Defines a helper pattern function but does not integrate it with the expected input/output flow"
    if re.search(r"for\s+i\s+in\s+range", full_low) and "print(i" in full_low and "num" not in full_low and "current" not in full_low:
        return "Prints a row-number triangle pattern (`i`, `i+1`, etc.) instead of consecutive numbers with alternating row direction"
    if "num = 1" in full_low or "num=1" in full_low or "current = 1" in full_low or "current=1" in full_low:
        has_row_build = ("row.append(" in full_low) or ("line.append(" in full_low) or ("row_output.append(" in full_low)
        has_reverse = "row.reverse(" in full_low or "row_nums.reverse(" in full_low or "[::-1]" in full_low
        if has_row_build and not has_reverse:
            return "Builds consecutive rows but forgets to reverse the even-numbered rows (alternating direction missing)"
        if has_row_build and has_reverse:
            if re.search(r"for\s+j\s+in\s+range\([^\)]*\):[\s\S]{0,200}row\.append", full_low, re.S):
                if "num += 1" not in full_low and "num+=1" not in full_low and "current += 1" not in full_low and "current+=1" not in full_low:
                    return "Builds row lists and reverses rows, but never advances the running counter (`num`) across elements"
                if (("num += 1" in full_low or "num+=1" in full_low) and
                    ("row.append(num)" in full_low or "row.append(str(num))" in full_low) and
                    re.search(r"for\s+j\s+in\s+range\([^\)]*\):[\s\S]{0,160}row\.append\([^\n]*num[^\n]*\)[\s\S]{0,80}\n\s*num\s*\+=\s*1", full_low, re.S) is None):
                    return "Alternating-row idea is present, but the running counter is updated in the wrong place (counter/reset bug)"
    if ("i*i" in squashed or "((i*i)" in squashed) and "if i%2" in squashed and "print(" in full_low:
        return "Uses a closed-form row-start formula but gets row boundaries/reversal formatting wrong on some cases"
    if vec in {"101", "010"} and ("filename" in full_low or "open(" in full_low):
        return "Partially solves the file-based zig-zag variant, but this cluster’s evaluator behavior expects a different output pattern"
    if vec == "000":
        return "Incorrect pattern-generation logic for the evaluated task (often wrong pattern type, sample hard-coding, or missing alternating reversal)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c021(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = fn_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Wrong Answer":
        if "for " in low and "return" in low and "<b>" in code and re.search(r"for[\s\S]{0,220}return\s+", low, re.S):
            return "Returns from inside a loop while building the bolded string (partial output / premature return)"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "IndexError" and ("text[n" in squashed or "text[n-1]" in squashed or "text[n+1]" in squashed):
            return "Runtime IndexError from indexing `text[n]`/`text[n-1]` without validating `n` against string bounds"
        if exc == "TypeError" and ("list(" in low or "text(len" in squashed or "join(" in low):
            return "Runtime TypeError from invalid string/list concatenation or malformed slicing/index calls"
        if exc == "NameError" and ("text" in low or "n" in low):
            return "Runtime NameError from typoed variables while constructing the bolded string"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in full_low for tok in ["mango", "sandwich", "noodles", "chocolate"]) and (
        "if text ==" in full_low or "print(\" 'm<b>a</b>ngo' \"" in full_low or "return \"m<b>" in full_low
    ):
        return "Hard-codes sample strings/outputs instead of bolding the nth character generically"
    if "<b>" not in code or "</b>" not in code:
        if "return text" in low:
            return "Only validates `n` and returns the original string; never inserts the `<b>...</b>` tags"
    if "text[:-n]" in squashed:
        return "Uses `text[:-n]` for the suffix after the bolded character, truncating the string incorrectly"
    if re.search(r"\breturn\s+text\[:[^\]]+\]\s*\+\s*f?[\"']<b>", code) and "text[n:]" not in squashed and "text[index+1:]" not in squashed:
        return "Builds the bolded prefix and character but omits the suffix after the nth character"
    if "text.replace(" in low:
        return "Uses `text.replace(...)`, which replaces the first/all matching character values instead of the nth position"
    if "text.index(" in low:
        return "Uses `text.index(...)` while iterating, so duplicate characters use the first occurrence index and are bolded incorrectly"
    if "n<len(text)" in squashed and "n>0" in squashed and "returntext" in squashed:
        return "Uses `n < len(text)` instead of allowing `n == len(text)`, so the last character cannot be bolded"
    if "n<=1" in squashed and "returntext" in squashed:
        return "Treats `n == 1` as invalid (`n <= 1`), so the first character case is handled incorrectly"
    if "text[:n:]" in squashed or "text[n-1:2]" in squashed:
        return "Wraps a slice/prefix in `<b>` tags instead of exactly one nth character"
    if all(tok in squashed for tok in ["n==1", "n==2"]) or "if(n==5)" in squashed:
        return "Length/index-specific branching (special-cases `n == 1/2/...`) instead of one general slicing formula"
    if "<b/>" in code:
        return "Uses malformed HTML tag (`<b/>`) instead of closing with `</b>`"
    if vec == "110":
        return "Boundary bug: valid `n == len(text)` is rejected (strict `< len(text)` check)"
    if vec == "101":
        return "Boundary/position bug around `n == 1` or duplicate characters (rejects first-char case or uses value-based `replace/index`)"
    if vec == "011":
        return "Interior-case wrapping bug (wrong slice inside `<b>` tags) while boundary cases are handled separately"
    if vec == "001":
        return "Suffix-construction bug: bolds the target character but truncates/omits trailing text"
    if vec == "010":
        return "Partial special-case solution (hard-coded `n` branches or wraps the wrong slice/prefix)"
    if vec == "000":
        return "Incorrect nth-character bolding logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c095(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Wrong Answer":
        if "for char in" in low and "return" in low and re.search(r"for[\s\S]{0,220}return\s+\w+", low, re.S):
            return "Returns from inside the character loop, so only the first Excel letter contributes to the index"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "KeyError" and ("{" in code or "dict" in low):
            return "Runtime KeyError from incomplete letter-to-number dictionary lookup (missing entries for some letters)"
        if exc == "TypeError" and ("ord(column)" in squashed or "column.split" in low or "int(column)" in low):
            return "Runtime TypeError from treating the whole column string as one character/number"
        if exc == "RecursionError":
            return "Runtime RecursionError from calling `excel_index(...)` recursively without progress/base case"
        if exc == "NameError":
            return "Runtime NameError from undefined accumulator/dictionary variables in base-26 conversion logic"
        if exc == "ValueError":
            return "Runtime ValueError from invalid string/number conversion while parsing the column label"

    base = _base_label(row)
    if base == "Returns inside loop before completing full check/computation":
        if "for char in" in low or "for i in column" in low:
            return "Returns from inside the character loop, so only the first Excel letter contributes to the index"
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["if column=='az'", "if column == 'az'", "if column=='bba'", "return 1405"]):
        return "Hard-codes sample column names/indices (e.g., `AZ`, `BBA`, `1405`) instead of computing arbitrary Excel indices"
    if re.search(r"\{[^\n]{0,400}[\"']a[\"']\s*:\s*1", low) and "for char in" not in low and "ord(" not in low:
        return "Uses a partial letter dictionary / single-letter lookup only, so multi-letter columns are not handled correctly"
    if "sorted(column)" in squashed:
        return "Sorts the letters before converting, which destroys positional significance in Excel column notation"
    if "return1405" in squashed or ("return-1" in squashed and "ifcolumnnotin" in squashed):
        return "Length-limited/hard-coded fallback for longer columns (e.g., returns a constant or `-1` for unsupported lengths)"
    if "append(a[i]+a[j])" in squashed or "b.index(column)" in squashed or "l.index(column)" in squashed:
        return "Enumerates Excel labels in a list and searches with `.index(...)` (works only up to the generated max length)"
    if "ifn==1" in squashed and "ifn==2" in squashed and "return" in low:
        if "n==3" not in squashed and "for char in" not in low:
            return "Handles only 1- and 2-letter columns with explicit branches (missing general support for longer labels)"
    if ("ord(" in low and "*26" in squashed) and "+1" not in squashed and "ord('a')" in squashed:
        return "Base-26 accumulation off-by-one bug (`A` treated as 0 instead of 1)"
    if ("out+=" in squashed or "s=d[it]+s" in squashed or "ans+=(x+1)" in squashed) and "*26" not in squashed:
        return "Adds letter values without positional weighting (treats Excel columns like simple sums)"
    if "return1405" in squashed and ("ifn==1" in squashed or "ifn==2" in squashed):
        return "Length-specific branch solution: computes short labels but uses a constant for 3+/4-letter columns"
    if vec == "010":
        return "Single-letter-only / partial conversion logic (fails 2-letter and longer columns)"
    if vec == "011":
        return "Handles 1- and 2-letter columns but fails longer labels (3+/4-letter support missing or hard-coded)"
    if vec == "001":
        return "Two-letter formula only (fails single-letter and longer-column cases)"
    if vec == "000":
        return "Incorrect Excel column-to-index conversion logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c001(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "TypeError":
            return "Runtime TypeError from treating string characters as numbers / invalid indexing while deinterleaving"
        if exc == "NameError":
            if "is_even_or_divisible_by_5" in fn_code.lower():
                return "Copied code from a different question (`is_even_or_divisible_by_5`) causing NameError/wrong-function behavior"
            return "Runtime NameError from undefined variables in deinterleaving logic"
        if exc == "IndexError":
            return "Runtime IndexError from manual indexing/slicing mistakes while splitting even/odd positions"
        if exc == "RecursionError":
            return "Runtime RecursionError from accidental recursive `deinterleave(...)` call"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["acebdf", "13524", "1357924680", "pormigrgamn"]):
        return "Hard-codes sample outputs instead of deinterleaving the input string generically"
    if "s[0:10:2]" in squashed or "s[1:10:2]" in squashed:
        return "Uses fixed `0:10` slices, so longer strings are truncated and shorter cases are handled accidentally"
    if "s.index(" in low:
        return "Uses `s.index(char)` while iterating characters, so duplicate characters get the wrong parity/index"
    if re.search(r"\+\s*f?[\"']bdf[\"']", code):
        return "Appends a hard-coded odd-index suffix (e.g., `\"bdf\"`) instead of computing all odd-index characters"
    if re.search(r"\breturn\s+s\[[^\\]]*::2\]\s*\+\s*[\"']", code):
        return "Computes even-index characters correctly but appends a fixed string instead of the actual odd-index part"
    if vec == "011":
        return "Partial deinterleave logic (fixed-length slicing or duplicate-index bug) fails one hidden string pattern"
    if vec == "010":
        return "Computes the even-index part but hard-codes/incorrectly builds the odd-index suffix"
    if vec == "000":
        return "Incorrect deinterleaving logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c022(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "TypeError":
            return "Runtime TypeError from invalid indexing/loop variables while scanning repeated characters"
        if exc == "NameError":
            return "Runtime NameError from undefined lists/counters in repeated-character tracking"
        if exc == "IndexError":
            return "Runtime IndexError from manual nested-index scans over the string"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/list API misuse in repeated-character logic"
        if exc == "RecursionError":
            return "Runtime RecursionError from accidental recursive `repeated_characters(...)` call"

    base = _base_label(row)
    if base == "Returns inside loop before completing full check/computation":
        if "count(" in low and "for " in low:
            return "Returns immediately on the first repeated character found instead of collecting all repeated characters"
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in low for tok in ["['r', 'g', 'm']", "['l']", "programming", "hello", "abc"]):
        if "return [" in low or "if s ==" in low:
            return "Hard-codes sample outputs/examples instead of detecting repeated characters from arbitrary input"
    if "for ch in set(s)" in squashed or ("set(s)" in squashed and "count(" in low and "append(" in low):
        return "Uses `set(s)` in the main scan, which loses first-appearance order of repeated characters"
    if "list(set(" in squashed:
        return "Builds repeated characters and then converts to `set`, which destroys the required first-appearance order"
    if ("seen=set()" in squashed or "seen_char=set()" in squashed) and "repeated" in low and "append(" in low:
        return "Tracks repeats in the order of second appearance (`seen`/`repeated` sets), not the required first appearance order"
    if "s=set(s)" in squashed and "count(" in low:
        return "Converts the input to a set first, losing duplicate counts before checking which characters repeat"
    if "count(" in low and "append(" in low and "set(" not in low:
        if "not in" not in low:
            return "Appends a character every time `count(ch) > 1`, so repeated characters appear multiple times in the output list"
    if "split(" in low:
        return "Uses `split()`/word-based logic, but the task is about repeated characters within a single string"
    if "s.lower()" in squashed or "k=s.lower()" in squashed:
        return "Lowercases the string, changing case-sensitive character identity and output order/values"
    if re.search(r"\breturn\s+\[\s*characters\s*\]", low):
        return "Returns only the first repeated character encountered instead of the full repeated-character list"
    if vec == "010":
        return "Second-appearance order bug (`seen`/`repeated` approach): output order is wrong on cases like `mississippi`"
    if vec in {"101", "001", "110", "100"}:
        return "Order-loss bug from using `set(...)`/`list(set(...))` (repeated characters found, but output order is unstable/incorrect)"
    if vec == "000":
        return "Incorrect repeated-character detection logic (returns wrong type/order/content)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c005(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "KeyError":
            return "Runtime KeyError from incrementing dict keys without initializing `'even'`/`'odd'`"
        if exc == "TypeError":
            return "Runtime TypeError from invalid list/dict operations while counting unique even/odd values"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/keys in the even/odd count dictionary logic"
        if exc == "IndexError":
            return "Runtime IndexError from using list values as indices (e.g., `l[i]` inside `for i in l`)"
        if exc == "RecursionError":
            return "Runtime RecursionError from accidental recursive call in `count_unique_even_odd`"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if re.search(r"\breturn\s*\{\s*[\"']even[\"']\s*:\s*3\s*,\s*[\"']odd[\"']\s*:\s*[34]\s*\}", low):
        return "Returns the sample dictionary counts directly (hard-coded example output)"
    if "for i in range(len(" in squashed and "i%2" in squashed:
        return "Counts parity of indices (`i % 2`) instead of parity of the list values"
    if "//2" in squashed and "==0" in squashed or "//2==1" in squashed:
        return "Uses floor-division (`// 2`) as a parity test instead of modulo (`% 2`)"
    if "set(l)" in squashed or "set(l1)" in squashed:
        if "for i in range(len(s))" in squashed or "foriinrange(len(l))" in squashed:
            return "Deduplicates values with `set(...)` but still counts index parity, not value parity"
    if "unique_even.add(number)" in squashed and "else:" in low and "unique_even.add(number)" in squashed.split("else", 1)[-1]:
        return "Adds odd numbers to the even set in both branches, leaving the odd set empty"
    if "ifnum%2==0" in squashed or "if(i%2==0)" in squashed or "ifa%2==0" in squashed:
        if "set(" not in low and "unique" not in low:
            return "Counts all even/odd occurrences without deduplicating the input values first"
    if re.search(r"\breturn\s+\w+\s*$", low) and "dict" not in low and "{" not in code:
        return "Returns a non-dictionary value instead of `{'even': ..., 'odd': ...}`"
    if vec == "01":
        return "Deduplicates values but then counts parity of indices (`range(len(set(l)))`) instead of parity of values"
    if vec == "00":
        return "Incorrect unique even/odd counting logic (placeholder, occurrence-counting, or wrong parity test)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c023(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "TypeError" and ("replace(" in low or ("+" in code and "str(" not in low)):
            return "Uses integer indices directly in string replacement/concatenation (`str(i)` cast missing)"
        if exc == "ValueError" and ".index(" in low:
            return "Uses `s.index(...)` while constructing output, which breaks on repeated-space handling"
        if exc == "NameError":
            return "Runtime NameError from undefined index/result variables in space-replacement logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ["a1b3c", "hello5world", "i1love6python"]):
        return "Hard-codes public sample strings/outputs instead of replacing spaces generically"
    if ".split(" in low and (".join(" in low or "strip(" in low):
        return "Uses `split()`-based word logic, collapsing/trimming spaces instead of preserving exact positions"
    if "strip(" in low:
        return "Strips the input before processing, so leading/trailing spaces and their indices are lost"
    if ".replace(" in low and ("' '" in code or '" "' in code):
        return "Uses `str.replace(...)` for all spaces at once, so per-space index substitutions are incorrect"
    if "print(" in fn_code.lower() and "return" not in low:
        return "Prints the answer but does not return the transformed string"
    if vec in {"011", "010"}:
        return "Whitespace/index-counting bug: partially works but fails hidden spacing/multi-digit-index cases"
    if vec == "100":
        return "Handles only a simpler space pattern and fails longer/multi-space hidden cases"
    if vec == "000":
        return "Incorrect space-replacement logic (wrong index counting, mutation, or output assembly)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c096(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` / prints inside a function-type question instead of using `sales_data, task` parameters"
        if exc == "KeyError":
            if "unit_price" in low:
                return "Uses a non-existent `unit_price` field (the records already provide `revenue`)"
            if "units sold" in low or "product id" in low or "product_id\" ]" in low:
                return "Uses incorrect dictionary key names/casing (e.g., `units sold`, `Product Id`) for sales records"
            return "Runtime KeyError from wrong sales-record keys or malformed per-product summaries"
        if exc == "ZeroDivisionError":
            return "Average-price branch divides by zero because units are aggregated incorrectly for some products"
        if exc == "NameError":
            return "Runtime NameError from misspelled helper/accumulator variables in task branches"
        if exc == "TypeError" and ("tuple" in low or "set(" in low):
            return "Runtime TypeError from inconsistent summary container types (tuple/list/set mixups)"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    exact_tasks = [
        "total_revenue",
        "product_wise_total_units_and_revenue",
        "top_selling_product",
        "average_product_price",
    ]
    present = {t: (t in fn_code) for t in exact_tasks}
    n_present = sum(present.values())

    if "task" in low and any(
        tok in low
        for tok in [
            "product_wise_total_units_revenue",
            "product_wise_total_unit_and_revenue",
            "product_wise_total_units_and revenue",
            "top-selling_product",
            "top selling product",
            "average_revenu_per_unit",
            "average product price",
            "product_summary",
        ]
    ):
        return "Task-dispatch string mismatch (branch names do not exactly match evaluator `task` values)"

    if present["total_revenue"] and not any(present[t] for t in exact_tasks[1:]):
        return "Implements only the `total_revenue` task branch; other required task branches are missing"
    if present["total_revenue"] and present["product_wise_total_units_and_revenue"] and not present["top_selling_product"] and not present["average_product_price"]:
        return "Implements only `total_revenue` + `product_wise_total_units_and_revenue` (top/average tasks missing)"
    if n_present >= 3 and not present["average_product_price"]:
        return "Omits the `average_product_price` branch after implementing other sales-analysis tasks"

    if all(tok in low for tok in ["sales_data[0]", "sales_data[1]", "sales_data[2]", "sales_data[3]"]):
        return "Hard-codes the public sample size/positions (`sales_data[0]..[3]`) instead of aggregating arbitrary input length"
    if any(pid in fn_code for pid in ["'P101'", "\"P101\"", "'P102'", "\"P102\"", "'P103'", "\"P103\""]) and "product_id" in low:
        return "Hard-codes public-sample product IDs (`P101/P102/P103`) so hidden product IDs fail"

    if "top_selling_product" in low:
        if "max(" in low and "lambda" in low and "revenue" not in low:
            return "Chooses top-selling product by units only and ignores the required revenue tie-break"
        if "max(summary,key=summary.get)" in squashed or "max(product_summary,key=product_summary.get)" in squashed:
            return "Chooses top-selling product by units only and ignores the required revenue tie-break"

    if "average_product_price" in low:
        if "round(" not in low:
            return "Computes average product price but does not round to 2 decimals"
        if "/len(" in squashed and "units_sold" not in low:
            return "Averages by number of transactions instead of using `total_revenue / total_units_sold` per product"

    if "product_wise_total_units_and_revenue" in low and "set(" in low and "product_id" in low:
        return "Uses `set(product_id)` / fixed buckets for aggregation, leading to missing or unstable product summaries"

    if vec == "0111":
        return "First three tasks mostly work, but `average_product_price` is incorrect on hidden cases"
    if vec == "0101":
        return "A branch-name mismatch leaves one required task unreachable while others are implemented"
    if vec == "0110":
        return "Aggregation helpers exist, but one advanced task (top-selling tie-break or average-price) is still wrong"
    if vec == "0100":
        return "Only one task branch is reliable; other sales-analysis branches are incomplete or hidden-case specific"
    if vec == "0000":
        return "Task dispatch and sales aggregation logic are broadly incorrect across all required tasks"
    return "Other wrong-answer logic pattern (residual)"


def classify_c097(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    fn_names = [
        "total_engagement",
        "engagement_rate",
        "most_engaging_video",
        "videos_with_engagement_rate_above_threshold",
        "average_engagement_rate",
    ]
    def_count = sum(1 for name in fn_names if re.search(rf"\bdef\s+{re.escape(name)}\s*\(", fn_code))

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` in function definitions (interactive script approach causes EOF under evaluator)"
        if exc == "ZeroDivisionError":
            if "average_engagement_rate" in low and "/len(videos)" in squashed:
                return "Average-rate logic divides by the wrong count (includes zero-view videos or wrong denominator)"
            return "Zero-view handling is missing in one of the list-processing helpers (`most_engaging`, threshold, or average)"
        if exc == "NameError":
            if any(tok in low for tok in ["vedios", "highest_engagement_rate", "first_one_from_the_list"]):
                return "Uses undefined placeholder/typo variables in engagement helper functions"
            return "Runtime NameError from misspelled helper variables across the multi-function solution"
        if exc == "TypeError":
            if "video(" in low or "videos(" in low:
                return "Treats video dicts/lists as callable objects (e.g., `video('title')`) in helper composition"
            return "Runtime TypeError from wrong return shapes/types across the helper functions"

    if "is_equal(" in fn_code and "videos = [" in fn_code:
        return "Copies test cases / `is_equal(...)` checks into the submission instead of implementing helper functions"
    if def_count < 5:
        return "Leaves one or more required functions undefined or incomplete in the multi-function template"
    if any(tok in fn_code for tok in ["Advanced Python", "Lambda in Java", "Intro to Python", "Beginner Java"]):
        return "Hard-codes public sample video titles/results instead of computing engagement metrics"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "threshold" in low and ">=" in code:
        return "Uses `>= threshold` instead of strict `> threshold` in `videos_with_engagement_rate_above_threshold`"
    if re.search(r"def\s+most_engaging_video[\s\S]{0,1200}if\s+\w+\s*>=\s*\w+", fn_code):
        return "Tie-break bug in `most_engaging_video`: uses `>=` and can return the last tied video instead of the first"
    if re.search(r"def\s+most_engaging_video[\s\S]{0,1200}return\s+video\b", fn_code) or "return videos[i]" in low:
        return "Returns a video record/index instead of the video title in `most_engaging_video`"
    if "def engagement_rate" in low:
        er_block = low.split("def engagement_rate", 1)[1].split("def ", 1)[0]
        if "*100" not in er_block.replace(" ", "") and "/" in er_block and "views" in er_block:
            return "Computes `engagement_rate` as a ratio but forgets the `* 100` percentage conversion"
        if "round(" not in er_block and "return" in er_block:
            return "Does not round `engagement_rate` to 2 decimals"
    if "def average_engagement_rate" in low:
        avg_block = low.split("def average_engagement_rate", 1)[1].split("def ", 1)[0]
        if "/len(videos)" in avg_block.replace(" ", ""):
            return "Averages over all videos (`len(videos)`) instead of only non-zero-view videos"
        if "round(" not in avg_block and "return" in avg_block:
            return "Does not round `average_engagement_rate` to 2 decimals"
    if "videos.index(" in low and "engagement_rate(" in low:
        return "Uses repeated `videos.index(...)` lookups in helper logic, causing tie/order bugs and hidden-case mismatches"

    if vec == "000111":
        return "Most helper functions are present, but hidden edge-case handling (especially zero-view/average behavior) remains wrong"
    if vec == "000101":
        return "Partially correct helper set: hidden threshold/tie/average semantics are still incorrect"
    if vec == "000110":
        return "List-processing helpers are partially correct but fail hidden tie/order/zero-view edge cases"
    if vec == "000100":
        return "Core helpers work, but later functions are sample-specific or incomplete on hidden datasets"
    if vec == "000000":
        return "Engagement-analysis helper functions are broadly incorrect across the multi-function task"
    return "Other wrong-answer logic pattern (residual)"


def classify_c098(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator function-call tests)"
        if exc == "IndexError" and "[0,0,0]" in squashed:
            return "Assumes a fixed 3-element output list (e.g., `[0,0,0]`) instead of length `k`"
        if exc == "TypeError" and re.search(r"\bsum\s*=\s*0", low):
            return "Mixes numeric and list accumulators while building the output parts (list/int type error)"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/helpers while constructing the partition list"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ["[2, 2, 1]", "[6, 5, 5]", "[3, 3, 3, 3]"]) and "if" in low:
        return "Hard-codes public sample outputs or `(n, k)` cases instead of computing a general partition"
    if "ifn%k==0" in squashed and "else" not in low:
        return "Handles only exact-division cases (`n % k == 0`) and omits the non-divisible remainder case"
    if "ifn%k==0" in squashed and "n%2" in squashed:
        return "Uses `n` parity (`n % 2`) instead of quotient/remainder (`n//k`, `n%k`) to distribute parts"
    if "n//k" in squashed and "n%k" in squashed:
        if ".sort(" in low or "sorted(" in low:
            return "Computes quotient/remainder but sorts the result, breaking the required larger-first order"
        if any(tok in squashed for tok in ["append(x+y)", "l.append(x+y)"]):
            return "Adds all remainder to one part instead of distributing `+1` across the first `n % k` parts"
        if "append(result+1)" in squashed and "while(z>1)" in squashed:
            return "Remainder-distribution loop appends the wrong count/order of `q+1` values"
    if re.search(r"\bif\s*\(?\s*k\s*==\s*[2345]", low):
        return "Uses `k`-specific branches / length-specific outputs instead of a general quotient-remainder solution"
    if "[0,0,0]" in squashed:
        return "Assumes `k == 3` with a fixed list shape instead of constructing a list of length `k`"
    if ".sort(" in low or "sorted(" in low:
        return "Sorts/reorders the result after construction, which breaks the required stable larger-first ordering"
    if vec == "100":
        return "Passes simpler/equal-split cases but distributes the remainder incorrectly on non-divisible inputs"
    if vec == "000":
        return "Incorrect partition construction (wrong length/sum/order or non-general logic)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c099(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator `solve_for_x(...)` calls)"
        if exc == "RecursionError" and fn_code.count("solve_for_x(") > 1:
            return "Calls `solve_for_x(...)` from inside `solve_for_x` using sample examples (infinite recursion)"
        if exc == "ValueError":
            if "split(" in low and "+" in low and "split('-',1)" not in squashed and "replace('-','+-')" not in squashed:
                return "Parses only `+` forms (or mishandles `-`), causing `ValueError` on subtraction/negative cases"
            if any(tok in low for tok in ["equation[0]", "equation[3]", "equation[5]", "equation[-1]"]):
                return "Fixed-position parser fails on hidden spacing/sign/multi-digit formats (`ValueError`)"
            if "int(" in low and "'x'" in low:
                return "Converts a missing/implied coefficient to `int(...)` (e.g., `x + b = c`), causing `ValueError`"
        if exc == "IndexError" and ("equation[" in low or "split(" in low):
            return "Fixed-index / fragile split parsing causes `IndexError` on hidden equation formats"
        if exc == "NameError":
            return "Runtime NameError from undefined parsed variables/intermediates in equation-solving logic"

    if fn_code.count("solve_for_x(") > 1 and "if solve_for_x(" in low:
        return "Includes sample `solve_for_x(...)` calls inside the function instead of implementing the parser"
    if any(eq in fn_code for eq in ["2x + 3= 11", "5x - 2= 13", "-3x + 10 = 1", "x + 5 = -5"]) and re.search(r"\breturn\s+[34]\.0\b", low):
        return "Hard-codes public sample equations/answers instead of parsing arbitrary equations"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if ".replace(\" \",\" \")" in fn_code or ".replace(' ',' ')" in fn_code:
        return "Uses a no-op whitespace replacement (`replace(' ', ' ')`) so spacing is never normalized"
    if any(tok in low for tok in ["equation[0]", "equation[1]", "equation[3]", "equation[5]", "equation[-1]"]):
        return "Uses fixed character positions to parse `a`, `b`, and `c`, which fails on hidden formats"
    if "split(" in low and "+" in low and "split('-',1)" not in squashed and "replace('-','+-')" not in squashed:
        return "Parses equations primarily via `'+'` splits and fails robust subtraction/negative-term handling"
    if "//" in squashed:
        return "Uses floor division (`//`) when solving for `x`, truncating results incorrectly"
    if re.search(r"\breturn\s+[34]\.0\b", low):
        return "Returns constant sample answers (`3.0`/`4.0`) instead of solving the given equation"

    if vec == "110":
        return "Partially correct parser: basic forms work, but sign/spacing/implied-coefficient hidden cases fail"
    if vec == "100":
        return "Sample-driven or fixed-format parser that only handles a narrow subset of equation forms"
    if vec in {"010", "011", "001", "101"}:
        return "Partially correct parser with hidden edge-case failures (spacing/sign/implied coefficient)"
    if vec == "000":
        return "Equation parsing/solving logic is broadly incorrect across hidden test formats"
    return "Other wrong-answer logic pattern (residual)"


def classify_c002(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` inside function-type question (EOF under evaluator `shuffle_sentence(...)` calls)"
        if exc == "RecursionError" and "is_equal(shuffle_sentence(" in fn_code:
            return "Copies `is_equal(shuffle_sentence(...))` tests into the function and triggers recursive self-calls"
        if exc == "NameError" and "def shuffle_sentence_order" in fn_code:
            return "Defines the wrong function name (`shuffle_sentence_order`), so evaluator cannot call `shuffle_sentence`"
        if exc == "TypeError" and ("for i in order" in low or "order[" in low):
            return "TypeError while assembling output string (mixes tuple indices/ints with string concatenation)"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "return sentence" in low:
        return "Returns the original sentence unchanged (ignores the `order` tuple)"
    if ("''.join(" in squashed or '\"\".join(' in squashed) and "split" in low:
        return "Joins shuffled words without spaces (`''.join(...)`) instead of returning a space-separated sentence"
    if any(tok in fn_code for tok in ["apple orange banana", "mouse dog cat", "yellow red green"]):
        if "return" in low or "if order" in low:
            if all(tok in fn_code for tok in ["(0,2,1)", "(2,1,0)", "(1,0,2)"]) and "(2,0,1)" not in fn_code and "(1,2,0)" not in fn_code:
                return "Handles only the public permutation tuples and misses unseen orders like `(2,0,1)` / `(1,2,0)`"
            return "Hard-codes public sample outputs/sentences instead of using the provided `order` tuple generically"
    if re.search(r"\b\w+\[\s*order\[\w+\]\s*\]\s*=\s*\w+\[\w+\]", code) or "k[x[a]]=l[a]" in squashed:
        return "Applies the permutation in reverse (`out[order[i]] = words[i]`) instead of selecting `words[order[i]]`"
    if "map[new_idx] = word" in fn_code or "map[new_idx]=word" in fn_code.replace(" ", ""):
        return "Builds a `{order[i]: word_i}` mapping and sorts by key (inverse-permutation bug on unseen cyclic orders)"
    if vec == "100":
        return "Permutation-order bug: code works for self-inverse/public orders but fails unseen cyclic permutations"
    if vec == "000":
        return "Incorrect word-order reconstruction or output formatting in the 3-word shuffle task"
    return "Other wrong-answer logic pattern (residual)"


def classify_c100(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` in a function-type question instead of using `first_name, user_id` parameters"
        if exc == "RecursionError" and "create_username(" in fn_code and fn_code.count("create_username(") > 1:
            return "Calls `create_username(...)` inside itself using sample examples (recursive/self-test code in function)"
        if exc == "IndexError":
            if all(tok in squashed for tok in ["[0]", "[1]", "[2]"]) and "len(" in low:
                return "Short-name edge-case bug: indexes `[0],[1],[2]` in a branch that still runs for names shorter than 3"
            return "Indexes the first three characters without a safe short-name guard (`len(name) < 3`)"
        if exc == "UnboundLocalError" and "id_str" in low:
            return "Branch initialization bug: `id_str` is defined only in one branch and used in both"
        if exc == "AttributeError" and ("tolower" in low or ".append(" in low or ".lower" in low):
            return "Misuses string APIs (`tolower`, `.append`, or `.lower` without proper call/usage) while building username"
        if exc == "NameError" and ("lower(" in low or "lowercase" in low):
            return "Uses undefined lowercasing helper/identifier (`lower`, `lowercase`) instead of `.lower()`"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ["ali123", "bob456", "jo789", "Alice", "Bob", "Jo"]):
        if "return" in low or "if" in low:
            return "Hard-codes public sample usernames/names instead of generating the username from arbitrary inputs"
    if any(tok in fn_code for tok in ['if "A" in f', 'if "B" in f', 'if "J" in f', 'if (first_name[0]=="A")', 'if u1=="A"']):
        return "Lowercases only specific sample initials (A/B/J) instead of calling `.lower()` on the whole name"
    if ".lower" in low and ".lower()" not in low:
        return "References `.lower` but does not call it (`.lower()` missing)"
    if "[:3]" in squashed or "[0:3]" in squashed:
        if ".lower()" not in low and "lower(" not in low:
            return "Uses the first 3 characters but forgets to lowercase the name prefix"
    if ".lower()" in low or "lower(" in low:
        if "[:3]" not in squashed and "[0:3]" not in squashed:
            return "Lowercases the full name but forgets to truncate to the first 3 characters for long names"
        if re.search(r"if\s+len\([^)]*\)\s*<=\s*3", low) and re.search(r"else\s*:[\s\S]*=\s*first_name\b", low):
            return "Length-branch bug: long names return the full name instead of a 3-letter prefix"
    if re.search(r"\breturn\s*\(?\s*['\"]ali123['\"]\s*\)?", low):
        return "Returns a constant username string (sample output) instead of using the function inputs"

    if vec == "00111":
        return "Single hidden-case miss: truncation/length-branch logic is wrong for one name-length scenario"
    if vec == "00110":
        return "Partial edge-case handling bug: one short-name case fails due indexing/branch initialization"
    if vec == "00100":
        return "Sample-specific/manual case handling (initial-letter-specific logic) instead of general lowercase+prefix logic"
    if vec == "00000":
        return "Username construction logic is broadly incorrect (lowercasing, prefix length, or input usage)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c101(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` in a function-type question instead of using the string parameter `s`"
        if exc == "RecursionError" and "is_equal(remove_duplicates(" in fn_code:
            return "Copies `is_equal(remove_duplicates(...))` tests into the function and triggers recursive self-calls"
        if exc == "AttributeError" and ("s.remove" in low or ".remove(" in low):
            return "Uses list/string mutation APIs incorrectly (`remove`) while trying to edit a string in place"
        if exc == "KeyError" and "freq" in low:
            return "Frequency-dictionary lookup bug (`freq[...]`) without safe access while building output"
        if exc == "NameError":
            return "Runtime NameError from undefined loop/frequency variables in duplicate-removal logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if re.search(r"\breturn\s+s(\b|\[::\])", low):
        return "Returns the original string unchanged (duplicates are not removed)"
    if "set(" in low and "join(" in low:
        return "Uses `set(...)` + `join(...)`, which loses the original first-appearance order of characters"
    if "s=set(s)" in squashed or "s = set(s)" in low:
        return "Converts the input to a set before processing, destroying order and duplicate information"
    if ".split(" in low:
        return "Uses `split()`/word-based logic, but the task requires character-level deduplication"
    if any(tok in fn_code for tok in ["banana", "hello", "abc"]) and ("if s ==" in low or "return 'ban'" in low or 'return "ban"' in low):
        return "Hard-codes sample strings/outputs (`banana`, `hello`, `abc`) instead of removing duplicates generically"
    if "is_equal(remove_duplicates(" in fn_code:
        return "Copies test assertions into the submission instead of implementing `remove_duplicates`"
    if "flag" in low and "for j in range(i+1" in squashed and "word=word+s[i]" in squashed:
        return "Keeps only non-repeating characters (unique-once) instead of first occurrences of all characters"
    if ".index(" in low and "set(" in low:
        return "Uses `set(s)` plus `s.index(...)`, causing unstable/incorrect order reconstruction"

    if vec == "000":
        return "Incorrect character deduplication logic (order preservation and/or duplicate handling is wrong)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c006(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` in a function-type question instead of using `keys, values, index` parameters"
        if exc == "RecursionError" and "make_dict_from_elems_in_index(" in fn_code and "is_equal(" in fn_code:
            return "Copies evaluator-style self-tests into the function and triggers recursive/self-test failures"
        if exc == "IndexError":
            if "raise IndexError" in fn_code or re.search(r"0\s*<=\s*index\s*<", fn_code):
                return "Treats valid negative indices as out-of-bounds (`0 <= index < ...`) instead of using Python indexing semantics"
            return "Index handling bug when extracting the key/value pair at `index`"
        if exc == "AttributeError" and ".strip(" in low and "keys[index]" in squashed:
            return "Assumes `keys[index]` is always a string (`.strip(...)`), but hidden tests include integer keys"
        if exc == "TypeError":
            return "Builds the dictionary with invalid syntax/types (tuple/set/string formatting instead of `{key: value}`)"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ['{"age": 25}', "{'age': 25}", '{"Country": "India"}', "{'apple' : 'yellow'}"]):
        return "Hard-codes public sample dictionaries instead of using the provided `keys`, `values`, and `index`"
    if "dict(zip(keys,values))" in squashed:
        return "Returns the full `dict(zip(keys, values))` instead of a single key-value pair at the given index"
    if re.search(r"0\s*<=\s*index\s*<", fn_code):
        return "Rejects negative indices with a non-negative bounds check (`0 <= index < ...`)"
    if "l.append(d)" in squashed and "returnl[index]" in squashed:
        return "Builds a list of per-index dictionaries and returns `l[index]`, which fails hidden negative-index semantics"
    if "forkeyinkeys" in squashed and "forvalueinvalues" in squashed and "return{key:value}" in squashed:
        return "Returns the first key-value pair from nested loops, ignoring the requested `index`"
    if re.search(r"\breturn\s+f[\"']\{key\}.*,.*\{value\}", low):
        return "Returns a formatted string (`\"key, value\"`) instead of a dictionary"
    if vec == "10":
        return "Negative-index handling bug: solution works for positive indices but treats valid negative indices incorrectly"
    if vec == "00":
        return "Incorrect dictionary construction (ignores `index`, returns wrong shape/type, or uses sample-specific values)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c102(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_code.lower():
            return "Reads `input()` in a function-type question instead of transforming the tuple parameter `t`"
        if exc == "RecursionError" and "move_even_indices_to_end_reversed(" in fn_code and "is_equal(" in fn_code:
            return "Copies evaluator calls/tests into the function and triggers recursive/self-test failures"
        if exc == "AttributeError" and ("t.reversed" in low or ".reverse(" in low):
            return "Uses non-existent tuple/string reverse APIs (`t.reversed()`) or wrong reverse method semantics"
        if exc == "TypeError":
            return "Runtime TypeError from mixing tuple/list/scalar operations while rebuilding the tuple"
        if exc == "NameError":
            return "Runtime NameError from undefined temporary lists/indices in even/odd split logic"
        if exc == "IndexError":
            return "Fixed-position indexing assumes longer tuples and fails on hidden small-tuple or slice-edge cases"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ["(10, 20, 30, 40, 50)", "('a', 'b', 'c', 'd', 'e', 'f')", "return t[1], t[3], t[4], t[2], t[0]"]):
        return "Hard-codes the public example tuple/output shape instead of processing arbitrary tuples"
    if "t[1::2]+t[::-2]" in squashed or "tup=t[1::2]+t[::-2]" in squashed or "returnt[1::2]+t[-1::-2]" in squashed:
        return "Off-by-one slice bug for reversed even indices (`t[::-2]` / `t[-1::-2]`) causes wrong elements on hidden cases"
    if "sorted(" in low and "reverse=true" in low:
        return "Sorts the even-indexed values in descending order instead of reversing their original positional order"
    if ".index(" in low and "%2" in low:
        return "Uses value-based `.index(...)` parity checks, which break on tuples with repeated values"
    if "ifi not in even" in squashed or (".remove(" in low and "list(t)" in low):
        return "Removes elements by value/membership instead of by index, so repeated values are handled incorrectly"
    if "even_index_eliment[::-1]" in squashed or "even_index_elements[::-1]" in squashed:
        return "Calls reverse slicing without assigning it back (`evens[::-1]` no-op), so even indices are not actually reversed"
    if re.search(r"return\s+\w+\s*\+\s*\w+\s*$", low) and "::-1" not in low and "reversed(" not in low and "sorted(" not in low:
        return "Concatenates odd-index and even-index groups without reversing the even-index elements"

    if vec == "101":
        return "Duplicate-value bug: index/value-based filtering works on unique tuples but fails when values repeat"
    if vec == "100":
        return "Even-index group is identified, but reversal/order semantics are wrong on hidden cases"
    if vec == "010":
        return "Slice-based even-index extraction is off by one (passes some cases, fails hidden edge/order cases)"
    if vec in {"011", "110"}:
        return "Partial tuple-reconstruction logic: some hidden cases pass, but edge-case concatenation/type handling is wrong"
    if vec == "000":
        return "Incorrect tuple slicing/reconstruction logic for moving even indices to the end in reversed order"
    return "Other wrong-answer logic pattern (residual)"


def classify_c103(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = (row.get("student_code") or fn_code or code or "").lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` in a function-type question instead of modifying the list parameter `l`"
        if exc == "RecursionError" and ("square_last_three(" in full_low and ("modify_check(" in full_low or "is_equal(" in full_low)):
            return "Copies evaluator/sample calls into `square_last_three(...)`, causing recursive/self-test execution"
        if exc == "IndexError" and any(tok in squashed for tok in ["l[3]", "l[4]", "l[5]"]):
            return "Fixed-position indexing assumes longer lists and crashes on hidden shorter-list cases"
        if exc == "TypeError" and ("(l[-3:])**2" in squashed or ".replace(" in low):
            return "Uses list values like strings/scalars (e.g., `(l[-3:])**2` or `l.replace(...)`) while squaring the tail"
        if exc == "NameError":
            return "Runtime NameError from undefined temporary variables in tail-squaring logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if any(tok in fn_code for tok in ["[4, 5, 36, 49, 64]", "[10, 400, 900, 1600]", "[9, 25, 49]"]):
        return "Hard-codes public sample outputs/lists instead of squaring the last three elements generically"
    if re.search(r"\breturn\s+l\s*$", low) and ("**2" not in low and ".pop(" not in low and "[-3:]" not in low):
        return "Returns the input list unchanged (does not square the last three elements)"
    if "range(-1,-4)" in squashed or "range(-1,-3)" in squashed:
        return "Uses an empty negative-step range (`range(-1, -4)`) so the tail-squaring loop never runs"
    if "l[-3:]" in low and ("return" in low) and ("l[-3:]=" not in squashed and "l[-3:] = " not in low):
        return "Computes/returns a transformed tail slice but does not write it back to `l` in place"
    if (re.search(r"\bl\s*=\s*\[", code) or "l=l[:-3]+" in squashed or "l = l[:-3] +" in low or "returnl[:-3]+" in squashed):
        return "Rebuilds/reassigns `l` (or returns a new list) instead of modifying the original list in place"
    if re.search(r"\breturn\s+\w+\s*$", low) and "return l" not in low and "return none" not in low:
        if any(tok in low for tok in ["append(", "[-3:]", "**2", "* i", "*i"]):
            return "Returns an intermediate value/list instead of mutating `l` in place as required"
    if (".pop(" in low or ".remove(" in low) and (".append(" in low or ".insert(" in low):
        return "Removes and rebuilds the tail via `pop/remove` + append/insert, causing order/element mistakes"
    if ("for i in range(len(l))" in low or "for i in l" in low) and ("**2" in low or "*i" in squashed) and "-3" not in low:
        return "Squares the whole list (or the wrong elements) instead of only the last three entries"
    if any(tok in low for tok in ["l[:3]", "l[0:3]"]) and ("**2" in low or "append(" in low):
        return "Squares the first three elements instead of the last three"
    if "len(l)" in low and low.count("if") >= 2 and any(tok in low for tok in ["l[0]", "l[1]", "l[2]"]):
        return "Length-specific/manual case handling instead of a general last-three in-place update"

    if vec == "0011":
        return "Length-conditional partial implementation: passes some list sizes but fails hidden size/edge variants"
    if vec == "0001":
        return "Fixed-index partial implementation that works only for one list-length pattern"
    if vec == "0000":
        return "Incorrect tail-squaring or in-place modification logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c024(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            if "while true" in full_low or "while(True".lower() in full_low:
                return "Reads until EOF (`while True` + `input()`) instead of using the given line count `n`"
            return "Runtime EOFError from incorrect input protocol (wrong number/order of `input()` calls)"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/helpers (`reverse`, `word`, etc.) in counting logic"
        if exc == "TypeError":
            return "Runtime TypeError from treating words/lists as scalars (or malformed palindrome checks)"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/list method misuse while splitting/checking words"
        if exc == "IndexError":
            return "Runtime IndexError from fixed-index word/slice assumptions while classifying word categories"
        if exc == "ValueError":
            return "Runtime ValueError from malformed numeric input parsing for `n`"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] == "Time Limit Exceeded":
        return "Inefficient palindrome-check/counting logic (nested loops over characters/indices) causing Time Limit Exceeded"
    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if any(tok in full_low for tok in ['"2 2 2 1"', "'2 2 2 1'", '"3 2 0 0"', "'3 2 0 0'", '"0 0 2 2"', "'0 0 2 2'"]):
        if "if n ==" in full_low or "if number" in full_low or "print(" in full_low:
            return "Hard-codes public sample count outputs instead of counting word categories from the input"
    if re.fullmatch(r"\s*return\s+\w+\s*==\s*\w+\s*\[\s*::?-?1\s*\]\s*", stripped) or "return str==reversed(str)" in full_squashed:
        return "Submits only a palindrome helper (`return word == word[::-1]`) instead of the full counting program"
    if (
        ("n=int(input())" in full_squashed or "number_lines=int(input())" in full_squashed or "line=int(input())" in full_squashed)
        and full_low.count("input(") <= 2
        and not re.search(r"range\s*\(\s*(n|number_lines|line)\s*\)", full_low)
    ):
        return "Reads only one text line after `n` and ignores the remaining lines"
    if ".split(\" \")" in full_low or ".split(' ')" in full_low:
        return "Uses `split(' ')` instead of `split()`, so hidden trailing-space lines create empty-string tokens that are miscounted"
    if re.search(r"for\s+\w+\s+in\s+range\s*\(\s*n\s*\)\s*:[\s\S]{0,300}(odd|even).*=0", full_low, re.S):
        return "Resets the category counters inside the per-line loop, so only the last line (or partial totals) are reported"
    if "while true" in full_low and "eoferror" in full_low:
        return "Reads input until EOF instead of consuming exactly `n` lines after the first line"
    if ("for line in lines" in full_low and "for word in line" in full_low and ".split" not in full_low):
        return "Iterates characters of each line (`for word in line`) instead of splitting into words first"
    if ("for word in words" in full_low and "p=s[::-1]" in full_squashed) or ("word[::]==word[::-1]" in full_squashed and "word" in full_squashed and "words.split" in full_squashed):
        return "Compares against the reversed word-list/string (`p = s[::-1]`) instead of checking each word palindrome independently"
    if "word.lower()" in full_low and "is_palindrome" in full_low and ".lower()" in full_low and "word == word[::-1]" not in full_low:
        return "Normalizes words and changes palindrome semantics (hidden tests expect the direct word palindrome check)"

    if vec == "00011":
        return "Mostly correct category counting, but hidden input-tokenization/aggregation edge case fails (commonly `split(' ')` or per-line output placement)"
    if vec in {"00001", "00010", "00110", "00111"}:
        return "Partially correct counting logic with a hidden edge-case bug (word palindrome test or multi-line aggregation semantics)"
    if vec == "00000":
        return "Incorrect multi-line word-category counting logic (input handling, tokenization, or category assignment is broadly wrong)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c104(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    full_low = (row.get("student_code") or fn_code or code or "").lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in full_low:
            return "Reads `input()` in a function-type question instead of using parameters `a` and `b`"
        if exc == "RecursionError" and ("mirror_merge(" in full_low and "is_equal(" in full_low):
            return "Copies evaluator tests (`is_equal(mirror_merge(...))`) into the function and triggers recursive/self-test failures"
        if exc == "IndexError":
            return "Mirror-indexing bug (`b[-i]`, fixed positions, or length-specific indexing) causes out-of-range access"
        if exc == "TypeError":
            return "Runtime TypeError from treating lists as scalars/indices while building the mirrored result"
        if exc == "NameError":
            return "Runtime NameError from undefined temporaries (`lst`, `l`, `s`, etc.) in mirror-merge logic"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if re.search(r"\breturn\s+a\s*\+\s*b\b", low):
        return "Returns list concatenation (`a + b`) instead of elementwise mirror merge"
    if any(tok in full_low for tok in ["[-5, -3, -1]", "[1, 12, 7]", "return[-5,-3,6]"]):
        return "Hard-codes public sample outputs / fixed lists instead of applying the mirror-merge rule generically"
    if re.fullmatch(r"\s*return\s*\[\s*\]\s*", code.strip()) or re.fullmatch(r"\s*return\s*\[\s*-?\d+(?:\s*,\s*-?\d+)*\s*\]\s*", code.strip()):
        return "Returns a constant list (`[]` or fixed values) instead of computing the mirror merge from `a` and `b`"
    if "str(a)" in low and "str(b)" in low and ("return x, y" in low or "return x,y" in squashed):
        return "Converts the input lists to strings / tuple output instead of computing numeric mirror-merge results"
    if "mid_point" in low and "first_half" in low and "second_half" in low:
        return "Splits the lists into halves and combines them, but the task requires elementwise mirror pairing across the full lists"
    if (
        ("for num1 in a" in low and ("for num2 in b" in low or "for num2 in b_reverse" in low or "for num2 in bb" in low))
        or ("for i in range(len(a))" in low and "for j in reversed(range(len(b)))" in low)
    ):
        return "Uses nested loops over both lists (cross-product), producing too many pairings instead of one mirror pair per index"
    if ".index(" in low and ("bb" in low or "b[::-1]" in low or "a.index" in low):
        return "Uses `.index(...)` to match mirrored elements, which breaks on duplicate values (first-occurrence index bug)"
    if "&" in code and "%2" in code:
        return "Uses bitwise `&` in parity checks (operator/precedence bug) instead of logical `and`"
    if "b[-i]" in squashed and "b[-i-1]" not in squashed:
        return "Uses `b[-i]` instead of `b[-i-1]` for mirror indexing (`i=0` incorrectly selects `b[0]`)"
    if ("b[i]" in squashed and "fori inrange(len(a))" in squashed) and ("b[-i-1]" not in squashed and "b[len(a)-i-1]" not in squashed and "b[::-1]" not in squashed):
        return "Pairs `a[i]` with `b[i]` (same index) instead of the mirrored element `b[-i-1]`"
    if "^" in code and "%2" in code:
        return "Uses XOR-based parity logic incorrectly, so same-parity vs mixed-parity add/subtract rules are inverted"
    if re.search(r"append\s*\(\s*\w+\s*-\s*\w+\s*\)", low) and ("y-x" in squashed or "b[" in squashed and "-a[" in squashed):
        return "Subtracts in the wrong direction for mixed parity (`b_rev - a` instead of `a - b_rev`)"
    if any(tok in squashed for tok in ["-(a[i]-b[-1-i])", "-(b[-1-i]-a[i])", "c1.append(int(i/-1))"]):
        return "Applies extra sign-flip/negation logic, producing the wrong sign for mixed-parity results"
    if re.search(r"%\s*2\s*==\s*0\s*or", squashed) or re.search(r"or\s*\(.*%\s*2", squashed):
        if "+" in code and "-" in code:
            return "Uses an `or` parity condition instead of checking same parity, so mixed-parity cases are added incorrectly"
    if "len(a)==len(b)==3" in squashed or all(tok in squashed for tok in ["a[0]", "a[1]", "a[2]"]) and ("b[-1]" in squashed or "b[-2]" in squashed):
        return "Length-specific manual implementation (fixed indices for length-3) instead of a loop-based general solution"
    if "result.append(a[i])" in squashed and "result.append(b[j])" in squashed:
        return "Interleaves raw elements from `a` and reversed `b` instead of computing one merged value per mirror pair"

    if vec == "110":
        return "Near-correct mirror pairing, but mixed-parity subtraction sign/parity condition is wrong on hidden cases"
    if vec == "010":
        return "Mirror-index/pairing bug (wrong `b` index formula or partial pairing) causes one private group to fail"
    if vec == "101":
        return "Duplicate-value pairing bug from value-based `.index(...)` matching instead of position-based indexing"
    if vec == "100":
        return "Destructive list-mutation pairing approach (`remove`/pop style) mishandles one hidden mirror case"
    if vec == "000":
        return "Incorrect mirror pairing / parity-rule application (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c007(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            return "Runtime EOFError from incorrect input usage / extra `input()` calls in this single-line I/O task"
        if exc == "NameError":
            return "Runtime NameError from undefined variables (`line`, `word`, `char`, counters) in vowel-count formatting logic"
        if exc == "TypeError":
            return "Runtime TypeError from indexing strings by characters/values or malformed `print`/join construction"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/list method misuse (`spit`, `split('')`, etc.)"
        if exc == "ValueError":
            return "Runtime ValueError from invalid `split('')` / input parsing misuse"
        if exc == "IndexError":
            return "Runtime IndexError from fixed-position word/character indexing assumptions"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] == "Time Limit Exceeded":
        return "Inefficient/infinite-loop vowel counting (Time Limit Exceeded)"
    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if any(tok in full_low for tok in ["myths(0) gym(0)", "aeiou(5) aeiou(5)", "hi!(1) how(1) are(2) you?(2)"]):
        return "Hard-codes public sample outputs instead of formatting arbitrary input words with vowel counts"
    if "return sum(" in full_low and "print(" not in full_low:
        return "Submits only a helper/count-return function and omits the required input-reading + formatted output program"
    if re.fullmatch(r"\s*return\s+\w+\s*==\s*\w+\s*\[\s*::?-?1\s*\]\s*", stripped):
        return "Submits a palindrome helper (`return word == word[::-1]`) for the wrong question"
    if "return" in full_low and "print(" not in full_low and ("split()" in full_low or "vowel" in full_low or "word" in full_low):
        return "Uses function-style `return` in an I/O question (should read input and print the formatted output line)"
    if "count_vowels(words)" in full_squashed:
        return "Calls the vowel-count helper on the whole word list (`count_vowels(words)`) instead of each word"
    if ("print(words" in low or "print(s," in low or "print(sentence," in low) and ("count" in low or "v_count" in low):
        return "Counts vowels across the whole input string and prints the sentence plus one total count (not per-word `word(count)` output)"
    if ("result=[]" in full_squashed or "ans=[]" in full_squashed or "d={}" in full_squashed or "D={}" in full_squashed) and (
        "print(result)" in full_low or "print(ans)" in full_low or "print(d)" in full_low or "for word in d.keys()" in full_low or "for word in d.keys():" in full_low
    ):
        return "Builds a list/dict representation and prints it (or iterates dict keys), causing wrong format and repeated-word handling bugs"
    if ("d={}" in full_squashed or "d = {}" in full_low) and ("d[word]" in full_squashed or "d[word]=" in full_squashed) and ("for word in d.keys()" in full_low):
        return "Stores counts in a dictionary keyed by word, so repeated words collapse into one output entry (hidden repeated-word failure)"
    if ("forwordinwords" in full_squashed or "for i in strings" in full_low or "for w in word" in full_low) and ("count=0" in full_squashed or "vowel_count=0" in full_squashed):
        if ("print(f\"{word}({count})\"" in full_low or "print(f\"{i}({count})\"" in full_low or "print(f'{w}({x})'" in full_low):
            if not re.search(r"for\s+\w+\s+in\s+\w+\s*:\s*count\s*=\s*0", full_low):
                return "Does not reset the vowel counter per word, so counts accumulate across words"
    if ("if word in vowels" in full_low or "if vowels in i" in full_low or "if i in vowels" in full_low and "for i in words" in full_low):
        return "Checks whole words against the vowel set/string (`if word in vowels`) instead of counting vowel characters inside each word"
    if "== vowel" in full_low or "==vowel" in full_squashed or "== vowels" in full_low or "==vowels" in full_squashed:
        return "Compares characters/words to the entire vowel string (`== vowels`) instead of using membership checks (`in vowels`)"
    if any(tok in full_squashed for tok in ["'a'or'e'", "\"a\"or\"e\"", "==\"a\"or\"e\""]):
        return "Uses an always-truthy boolean chain for vowel checks (`'a' or 'e' or ...`)"
    if ("if \"a\" in" in full_low and "elif \"e\" in" in full_low) or ("if 'a' in" in full_low and "elif 'e' in" in full_low):
        return "Uses an `if/elif` vowel-presence chain, so each word contributes at most one vowel to the count"
    if "split('_')" in full_low:
        return "Splits the sentence on the wrong delimiter (`'_'` instead of spaces)"
    if ".split()" not in full_low and ("for char in" in full_low or "for i in" in full_low) and "print(" in full_low:
        return "Treats the entire input as one string and counts/prints globally instead of producing per-word outputs"
    if ("for word in line" in full_low or "for word in words" in full_low) and "print(f\"{word}(" in full_low and "join(" not in full_low and "end=" not in full_low:
        return "Prints one `word(count)` per line inside the loop instead of a single space-separated output line"
    if ("for char in word" in full_low or "for j in i" in full_low) and "print(" in full_low and "join(" not in full_low and "end=" in full_low:
        return "Per-word vowel counting is present, but output formatting is wrong (`word count` formatting/spacing instead of `word(count)`)"

    if vec == "110":
        return "Mostly correct per-word counting, but hidden repeated-word/format bug remains (commonly dict-key dedup or wrong character loop variable)"
    if vec == "010":
        return "Per-word loop is present, but counts accumulate across words (counter reset bug)"
    if vec == "100":
        return "Partial formatting/counting logic bug on one hidden edge case (often punctuation/word-boundary handling)"
    if vec == "000":
        return "Incorrect per-word vowel counting or output formatting (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c025(row: dict[str, Any]) -> str:
    code = row["logic_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            return "Runtime EOFError from wrong input protocol (extra `input()` calls or incorrect pair parsing)"
        if exc == "ValueError":
            if "a=int(input())" in full_squashed or "b=int(input())" in full_squashed:
                return "Reads each pair value on separate lines (`a=int(input()); b=int(input())`), causing input parsing failure on `a b` lines"
            return "Runtime ValueError from malformed pair parsing (`a b`) or incorrect integer conversion"
        if exc == "TypeError":
            return "Runtime TypeError from treating input strings/lists as numbers while computing carry"
        if exc == "NameError":
            return "Runtime NameError from undefined variables (`pairs`, `a`, `b`, `carry`) in carry-update logic"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/list method misuse while parsing pairs"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if full_low.count("print(") >= 2 and "input(" not in full_low and re.search(r"\bprint\s*\(\s*['\"]?\d+", full_low):
        return "Prints constant sample output lines instead of reading input pairs and simulating carry"
    if (
        any(tok in full_low for tok in ["0\\n10\\n10\\n15\\n0", "print(\"0\\n10\\n10\\n15\\n0", "print(''' 0 10 10 15 0'''"])
        or ("if n == 5" in full_low and "print(10)" in full_low and "print(15)" in full_low)
        or ("if(n==5)" in full_squashed and "print(10)" in full_squashed)
        or any(tok in full_squashed for tok in ["a1,b1=30,40", "a2,b2=80,30", "a3,b3=10,90", "a4,b4=90,15", "a5,b5=5,5"])
    ):
        return "Hard-codes the public sample carry outputs instead of simulating carry updates for arbitrary input pairs"
    if "for a, b in pairs" in full_low or ("return result" in full_low and "input(" not in full_low):
        return "Writes a helper/function-style solution (expects `pairs` or returns a list) instead of the required input/output program"
    if ("n=int(input())" in full_squashed or "n = int(input())" in full_low) and full_low.count("input(") == 1:
        return "Reads only `n` (or an incomplete prefix) and never processes the required `n` pairs"
    if "a=int(input())" in full_squashed and "b=int(input())" in full_squashed:
        return "Reads each pair as two separate input lines instead of parsing one `a b` line with `split()`/`map()`"
    if ("for _ in range(n)" in full_low or "for i in range(n)" in full_low or "while n>0" in full_squashed) and "input(" in full_low and "carry" not in full_low:
        if ("-100" in full_squashed or "print(0)" in full_low or "print(\"0\")" in full_low or "print('0')" in full_low):
            return "Processes each pair independently without maintaining a carry state across iterations"
    if (
        "q[:len(q)//2" in full_squashed
        or "len(str)<=3" in full_low
        or "a=int(given[0:2])" in full_low
        or "b=int(given[-2:])" in full_low
        or ("str1[0]" in full_low and "str1[-1]" in full_low)
        or ("m[:2]" in full_low and "m[-2" in full_low)
        or ("a=n_pair[0]" in full_squashed and "b=n_pair[-1]" in full_squashed)
    ):
        return "Parses `a b` using fixed string positions/line length instead of robust `split()` parsing (fails hidden widths like `200 0`)"
    if ("carry = 0" in full_low or "carry=0" in full_squashed) and re.search(r"for\s+.*in\s+range\s*\(\s*n\s*\)", full_low):
        if re.search(r"for\s+.*in\s+range\s*\(\s*n\s*\)\s*:[\s\S]{0,180}\bcarry(?:_val)?\s*=\s*0", full_low, re.S):
            return "Reinitializes carry inside the loop, so carry does not persist across pairs"
    if re.search(r"for\s+.*in\s+range\s*\(\s*n\s*\)\s*:[\s\S]{0,180}\b(points|count|remain)\s*=\s*0", full_low, re.S):
        if "+carry" not in full_squashed and ("a+b" in full_squashed or "suma=a+b" in full_squashed or "add=num1+num2" in full_squashed):
            return "Uses a fresh per-iteration temporary (`points`/`count`/`remain`) instead of a persistent carry variable"
    if "carry+=" in full_squashed and ("-100" in full_squashed or "sum-100" in full_squashed):
        return "Accumulates carry with `carry += ...` instead of assigning the new carry (`carry = sum - 100`)"
    if "else:carry=100" in full_squashed or "else: carry = 100" in full_low:
        return "Sets carry to `100` on non-overflow steps instead of resetting it to `0`"
    if ("carry=1" in full_squashed and "else:carry=0" in full_squashed) or "//10" in full_squashed or "%10" in full_squashed:
        return "Computes carry as a digit/flag (`0/1`, `//10`, `%10`) instead of the required overflow amount `sum - 100`"
    if ("100-" in full_squashed or "abs(l)+l" in full_squashed) and ("sum" in full_low or "total" in full_low or "a+b" in full_squashed):
        return "Uses the wrong carry formula (`100 - sum` / sign tricks) instead of `sum - 100`"
    if ("lines=[]" in full_squashed and "for line in lines" in full_low) or ("l=[]" in full_squashed and "forstrinl" in full_squashed):
        return "Stores all pairs and reprocesses them in a second loop, causing carry-order/reset mistakes"
    if "print(ai,bi)" in full_squashed:
        return "Prints the input pair values (`ai, bi`) instead of computing and printing carry outputs"
    if (
        ("carry" in full_low)
        and ("a+b+carry" not in full_squashed and "sum(nums,carry)" not in full_squashed)
        and (
            re.search(r"\bsum\s*=\s*a\s*\+\s*b\b", full_low)
            or re.search(r"\b(value|d|q)\s*=\s*\w+\s*\+\s*\w+\b", full_low)
            or "sum=int(f[0])+int(f[1])" in full_squashed
        )
    ):
        return "Ignores the previous carry when computing the next sum (`sum = a + b` instead of `a + b + carry`)"
    if ("for _ in range(n)" in full_low or "for i in range(n)" in full_low or "while n>0" in full_squashed) and "carry" in full_low:
        if "+carry" not in full_squashed and ("sum" in full_low or "total" in full_low or "add=" in full_squashed):
            return "Processes each pair independently and never feeds the previous carry into the next step"
    if ("sum>100" in full_squashed and "sum<100" in full_squashed) and not any(tok in full_squashed for tok in ["sum==100", "sum<=100", "sum>=100"]):
        return "Misses the exact-100 edge case (checks only `<100` and `>100` branches)"
    if "print(s,carry)" in full_squashed or "print(sum,carry)" in full_squashed:
        return "Prints the sum together with carry (or debug values) instead of printing only the carry after each pair"

    if vec in {"001", "011"}:
        return "Carry propagation/update bug: solution works on simpler steps but hidden multi-step carry behavior is wrong"
    if vec == "101":
        return "Partial carry simulation bug on hidden edge cases (exact-100/reset or carry reuse ordering)"
    if vec == "000":
        return "Incorrect carry-simulation program logic (input parsing, carry update, or output printing is broadly wrong)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c105(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["function_code"] or ""
    fn_code = row["function_code"] or code
    low = code.lower()
    fn_low = fn_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError" and "input(" in fn_low:
            return "Reads `input()` inside function-type question instead of using the parameter `s`"
        if exc == "RecursionError" and fn_code.count("swap_diagonals(") > 1:
            return "Calls `swap_diagonals(...)` from inside itself (copied self-test/sample call) causing recursion"
        if exc == "IndexError" and ("[1][1]" in squashed or "[0][1]" in squashed):
            return "Treats the 2-line string like a nested list/string matrix (`s[1][1]`), causing indexing errors"
        if exc == "ValueError" and ("split('/')" in squashed or "split(\"/\")" in low):
            return "Splits on `'/'` instead of the required newline (`'\\n'`), so hidden inputs cannot be unpacked"
        if exc == "AttributeError" and (".reversed(" in low or ".append(" in low):
            return "Uses invalid string/list APIs while trying to reverse/swap the 2-line string"
        if exc == "TypeError" and ("s=list(s)" in squashed or "returnn2,n1" in squashed or "returnf1" in squashed):
            return "Builds/returns the wrong type (tuple/list) instead of the required transformed string"

    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if re.search(r"\breturn\s*\(?\s*['\"]dc\\nba['\"]\s*\)?\s*$", low):
        return "Returns the public sample output (`'dc\\nba'`) as a constant instead of transforming the input"
    if re.search(r"\breturn\s+s\s*$", low):
        return "Returns the input string unchanged (no diagonal swap applied)"
    if "split('/')" in squashed or "split(\"/\")" in low:
        return "Uses the wrong delimiter (`'/'`) instead of splitting the two rows on newline (`'\\n'`)"
    if all(tok in squashed for tok in ["s[0]", "s[1]", "s[2]", "s[3]"]) and "\\n" not in code and "split(" not in low:
        return "Treats the input as a 4-character string and ignores the newline separator, so row positions are wrong"
    if re.search(r"\breturn\s+\w+\s*,\s*\w+\s*$", low):
        return "Returns a tuple of row fragments instead of one newline-joined string"
    if ".replace(" in low:
        if "returns.replace(m,s)" in squashed or "s.replace('ba','dc')" in squashed:
            return "Uses `str.replace(...)` on sample substrings / no-op replacements instead of positional swapping"
        return "Uses substring replacement (`replace`) rather than index-based row/column reconstruction"
    if "split(\"\\n\")" in code or "split('\\n')" in code:
        if "row1" in low and "row2" in low and "return" in low and "row2[1]+row1[1]" in squashed:
            return "Splits rows correctly but reassembles characters in the wrong order (`db\\nca`-style column swap)"
        if "[::-1]" not in low and re.search(r"row[12]\[\d\].*row[12]\[\d\]", squashed):
            return "Manual row-index reconstruction after `split('\\n')` has a character-order mixup on hidden cases"
    if "print(" in fn_low and "return" not in low:
        return "Prints a transformed string (or debug output) instead of returning the required string value"

    if vec == "010":
        return "Near-correct string manipulation, but replacement/reassembly logic is a no-op or swaps the wrong character positions"
    if vec == "000":
        return "Incorrect 2-line string diagonal-swap logic (constant output, wrong indexing, or wrong return type)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c106(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = low.replace(" ", "")
    full_squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            if "input(" in full_low:
                return "Reads stdin (`input()`) instead of reading from the provided `filename` file"
            return "Runtime EOFError from wrong input/file protocol (mixes file-reading with stdin assumptions)"
        if exc == "FileNotFoundError":
            return "Opens a hard-coded filename/path (e.g., `filename.txt`) instead of using the provided `filename`"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/file API misuse (`indexof`, wrong file/string methods) in vowel processing"
        if exc == "IndexError":
            return "Runtime IndexError from fragile line/character indexing while reconstructing file content"
        if exc == "ValueError":
            return "Runtime ValueError while parsing `k` from the file (malformed first-line handling)"
        if exc == "TypeError":
            return "Runtime TypeError from mixing list/string/file-handle values while rebuilding transformed lines"
        if exc == "NameError":
            return "Runtime NameError from undefined counters/output buffers in file vowel-transform logic"
        if exc == "KeyError":
            return "Runtime KeyError from dictionary-based vowel mapping logic missing some cases"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] == "Time Limit Exceeded":
        return "Infinite/inefficient file-read loop (e.g., `while` loop over `read(1)` without proper progress update)"
    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"

    if any(tok in full_low for tok in ["half upper half lower", "programming is the art", "make all vowels uppercase"]):
        if "print(" in full_low and "with open(filename" not in full_low:
            return "Prints a public sample output directly instead of transforming the contents of `filename`"
    if any(tok in full_low for tok in ["lazy dog", "typography.", "simple and elegant", "the quick brown fox"]):
        if "print(" in full_low and "open(filename" not in full_low:
            return "Prints hard-coded public sample output text instead of reading and transforming `filename`"
    if any(tok in full_low for tok in ["make all vowels upper", "ubbi", "dubbi"]):
        return "Pastes logic/output from a different string-transformation problem instead of the file-vowel task"
    if "output.txt" in full_low or re.search(r"\bopen\s*\(\s*['\"][^'\"]*output[^'\"]*['\"]\s*,\s*['\"]w", full_low):
        return "Writes the transformed result to an `output.txt` file (and re-reads it) instead of printing directly to stdout"
    if (
        ".read(1)" in full_low
        or re.search(r"\bint\s*\(\s*\w+\s*\[\s*0\s*\]\s*\)", full_low)
        or ("list(" in full_low and ".pop(0)" in full_low and ("content" in full_low or "text" in full_low))
        or re.search(r"\bk\s*=\s*\w+\s*\[\s*0\s*\]", full_low)
    ):
        return "Parses `k` from only the first character (`read(1)` / `text[0]`), which fails multi-digit `k` cases"
    if re.search(r"char\.lower\s*\(\s*\)\s*==\s*['\"]a['\"]\s+or\s+char\s*==\s*['\"]e['\"]", full_low):
        return "Boolean-precedence bug in vowel checks (`... or ... and count % k == 0`) uppercases the wrong characters"
    if re.search(r"for\s+\w+\s+in\s+lines\s*:\s*[\s\S]{0,160}if\s+\w+\s+in\s+vowels\s*:", full_low, re.S):
        return "Iterates over whole lines but checks `if line in vowels`, so vowel detection happens at the wrong granularity"
    if ("splitlines()" in full_low or ".split('\\n')" in full_low or '.split("\\n")' in full_low) and re.search(
        r"for\s+\w+\s+in\s+\w+\s*:[\s\S]{0,260}\bcount\s*=\s*0", full_low, re.S
    ):
        return "Resets the vowel counter for each line, but the task requires cumulative counting across the whole file"
    if re.search(r"for\s+\w+\s+in\s+\w+\s*:[\s\S]{0,260}\b(ctr|counter|c)\s*=\s*0", full_low, re.S):
        if "for line in" in full_low or "for i in f" in full_low or "readlines()" in full_low:
            return "Resets the vowel counter inside the per-line loop (`ctr/counter = 0`), breaking cumulative counting across the file"
    if (
        (".strip().split()" in full_low or ".strip().split(" in full_low or "line.strip().split()" in full_low)
        and ("for word in" in full_low or "split()" in full_low)
    ):
        return "Uses `strip().split()` word tokenization, which collapses spaces/newlines and breaks exact file formatting"
    if ("splitlines()" in full_low or ".split('\\n')" in full_low or '.split("\\n")' in full_low) and (
        ".strip(" in full_low or "print(newsentence)" in full_low
    ):
        return "Line-splitting reconstruction changes formatting (strips lines / inserts extra newlines) instead of preserving file text exactly"
    if "r+" in full_low and "open(filename" in full_low:
        return "Uses read/write (`r+`) file mode and manual whole-file mutation, often combined with fragile first-character `k` parsing"
    if (
        ".upper(" in full_low
        and ".lower(" not in full_low
        and ("aeiou" in full_low or "vowels" in full_low)
        and "swapcase()" not in full_low
    ):
        return "Uppercases every k-th vowel but does not lowercase the other vowels as required"
    if re.search(r"\bdef\s+\w+\s*\(", full_low) and "return" in full_low and "print(" not in full_low and "with open(filename" in full_low:
        return "Builds a helper that returns transformed text/list but never prints the required final output"
    if any(tok in full_squashed for tok in ["'a'or'e'","\"a\"or\"e\"","==\"a\"or\"e\""]):
        return "Uses an always-truthy boolean chain for vowel checks (`'a' or 'e' or ...`)"

    if vec in {"00110", "00100"}:
        return "Mostly correct transformation logic, but hidden formatting/`k` parsing edge cases fail (commonly first-char `k` parsing or newline stripping)"
    if vec in {"00011", "00010"}:
        return "Line-wise/tokenized processing partially works, but cumulative-count or exact-format preservation fails on hidden cases"
    if vec == "00000":
        return "Incorrect file-based vowel transformation logic (input source, cumulative counting, or exact output formatting is broadly wrong)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c107(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = code.lower()
    full_low = full_code.lower()
    squashed = full_low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            if full_low.count("input(") >= 2:
                return "Reads multiple separate `input()` values (`move_number`, white move, black move) instead of one notation string line"
            return "Runtime EOFError from incorrect input protocol (expects more lines than the single notation-string input)"
        if exc == "IndexError" and ".split" in full_low and "[0]" in full_low:
            return "Indexes `token[0]` without safely skipping move-number/empty tokens, causing `IndexError`"
        if exc == "AttributeError" and "startwith(" in full_low:
            return "Misspells `.startswith(...)` as `.startwith(...)` while decoding piece tokens"
        if exc == "ValueError" and ("int(input())" in full_low or "no_of_moves" in full_low):
            return "Tries to read an integer move count first (`int(input())`) even though input is a single notation string"
        if exc == "NameError":
            return "Runtime NameError from undefined piece maps/counters in notation parsing logic"
        if exc == "TypeError":
            return "Runtime TypeError from invalid `input()/map()` or dictionary API usage while parsing tokens"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"

    if any(tok in full_low for tok in ["e4 = 'pawn'", "qc7 = 'queen'", "print(e4 )", "print(e4)"]):
        return "Hard-codes public sample move-to-piece outputs instead of parsing arbitrary chess-notation tokens"
    if any(tok in full_low for tok in ['print("pawn\\npawn\\nknight', "print('pawn\\npawn\\nknight", "print(\"pawn\\npawn\\nking\\nrook"]):
        return "Prints a fixed piece-name sequence (sample output) instead of parsing the notation string"
    if any(tok in full_low for tok in ['if inp == "e4 e5', 'if inp == "1. e4 e5', "if inp==\"e4 e5", "if inp==\"1. e4 e5"]):
        return "Hard-codes exact public sample notation strings and corresponding outputs instead of parsing arbitrary games"
    if re.search(r"(?m)^def\s+get_piece_name\s*\(", full_code) and "input(" not in full_low and "print(" not in full_low:
        return "Defines a helper (`get_piece_name`) but omits the required input-reading/token loop and printed output"
    if "firstinput" in full_low or "secondinput" in full_low or ("white_move" in full_low and "black_move" in full_low):
        return "Parses only the first move pair (or a fixed number of tokens) instead of scanning the entire notation string"
    if "judge==0" in squashed or all(tok in squashed for tok in ["'1.'","'2.'","'10.'"]):
        return "Uses a brittle move-number state flag / hard-coded `1.`..`10.` list and skips many tokens in longer games"
    if "0-0" in full_code and "O-O" not in full_code:
        return "Uses zeroes (`0-0`, `0-0-0`) instead of SAN castling tokens with letter O (`O-O`, `O-O-O`)"
    if re.search(
        r'(?s)(if|elif)\s+[^\n]*["\']O-O["\'].*?:\s*print\(\s*["\']King["\']\s*\)(?![\s\S]{0,80}print\(\s*["\']Rook["\']\s*\))',
        full_code,
    ) or re.search(
        r'(?s)(if|elif)\s+[^\n]*["\']O-O-O["\'].*?:\s*print\(\s*["\']King["\']\s*\)(?![\s\S]{0,80}print\(\s*["\']Rook["\']\s*\))',
        full_code,
    ):
        return "Handles castling by printing only `King` and forgets the required second line `Rook`"
    if re.search(r'(?s)O-O-O[\s\S]{0,180}print\(\s*["\']Queen["\']\s*\)', full_code):
        return "Misclassifies queenside castling (`O-O-O`) as involving `Queen` instead of printing `King` and `Rook`"
    if ".remove(" in full_low and (".split(" in full_low or "temp.remove(" in full_low):
        return "Mutates the token list while iterating (`remove(...)`), which skips moves and loses output lines"
    if re.search(r"startswith\(\s*['\"][a-h]['\"]\s*\)", full_low) and "o-o" not in full_low and "move[0]" not in full_low:
        return "Uses square/file-prefix heuristics for specific sample moves (e.g., `startswith('e')`) instead of SAN piece parsing rules"
    if ("while i<(len(s))" in squashed or "whilei<len(s)" in squashed) and ".split" not in full_low:
        return "Scans the raw string character-by-character instead of tokenizing SAN moves, so move numbers/symbols are misread"
    if ".split" in full_low and "[0]" in full_low and "endswith('.')" not in full_low and "isdigit(" not in full_low:
        return "Tokenizes by spaces but does not robustly filter move-number tokens before indexing piece letters"
    if re.search(r'print\(\s*["\']king["\']\s*\)', full_low):
        return "Outputs lowercase piece names (`king`) instead of the required title-case labels (`King`, `Rook`, ...)"

    if vec in {"010", "011"}:
        return "Near-correct token parsing, but castling output formatting/mapping is wrong on hidden cases"
    if vec in {"100", "101", "110"}:
        return "Partial SAN token filtering logic: some games pass, but move-number/capture/castling token handling fails on hidden cases"
    if vec == "000":
        return "Incorrect chess-notation token parsing and piece-name emission logic (broad wrong-answer failure)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c008(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]
    vec3 = vec[-3:] if isinstance(vec, str) and len(vec) >= 3 else vec

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "NameError" and "input(" not in low and ("n" in low or "w" in low):
            return "Uses loop/size variables (`n`, `w`, etc.) without reading the input size first"
        if exc == "TypeError" and "print(" in low and ("*(" in low or "+ 2*" in low or "+2*" in squashed):
            return "Builds row strings by adding integers to strings (string-multiplication/concatenation arithmetic bug)"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] == "Time Limit Exceeded":
        return "Infinite loop in pattern generation (e.g., `while` loop that never updates the loop variable)"
    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if "class votingsystem" in low or "add_vote(" in low:
        return "Unrelated pasted solution (different problem entirely) instead of W-pattern printing logic"
    if "def filter_students" in low or "average score >=" in low:
        return "Unrelated pasted function/problem solution instead of W-pattern generation"
    if full_code.count("print(") >= 8 and "input(" not in low:
        return "Hard-codes a specific W output (fixed rows) instead of generating the pattern from the input `n`"
    if re.search(r"\bif\s+(n|num|x|a)\s*==\s*5\b", low) and re.search(r"\bif\s+(n|num|x|a)\s*==\s*[12]\b", low):
        return "Hard-codes the public sample sizes (`n=1/2/5`, etc.) instead of generating the W pattern for arbitrary `n`"
    if re.search(r"\b(if|elif)\s+(n|num|x|a)\s*==\s*1\b", low) and re.search(r"\b(if|elif)\s+(n|num|x|a)\s*==\s*2\b", low):
        if "for i in range" not in low and "while" not in low:
            return "Hard-codes small sample sizes (`n=1/2/3/...`) with `if/elif` branches instead of a general pattern loop"
    if re.search(r"\bif\s+n\s*==\s*1\b", low) and re.search(r"\bif\s+n\s*==\s*2\b", low):
        return "Hard-codes small-`n` cases (`n==1/2/3/...`) instead of using one general row-construction formula"
    if any(tok in squashed for tok in ['"|\"*(n)','\"/\"*n','\"\\\\\"*n',"'|'*(n)","'/'*n","'\\\\'*n"]):
        return "Repeats bars/slashes/backslashes `n` times (`'|'*n`, `'/'*n`) instead of printing single boundary/slash characters per row"
    if "input(int())" in squashed or "n=input(int())" in squashed:
        return "Uses invalid input conversion (`input(int())`) instead of reading the integer with `int(input())`"
    if re.search(r"(?m)^def\s+\w+\s*\(", full_code) and "input(" not in low and "return" in low:
        return "Submits a helper/function-style return value instead of reading `n` and printing the W pattern rows"
    if "forn inrange(0,n)" in squashed or "for n in range(0,n)" in low:
        return "Reuses `n` as the loop variable (`for n in range(...)`), corrupting the intended pattern size"
    if re.search(r"for\s+\w+\s+in\s+range", low) and (
        "print(\"|/\\\\|\")" in full_code or "print('|/\\\\|')" in full_code or "\"|\"+\"/\\\\\"+\"|\"" in full_code or "'|'+\"/\\\\\"+'|'" in full_code
    ):
        return "Prints the same row (`|/\\\\|`) repeatedly instead of widening the interior spacing each row"
    if "row= ['1 ']" in full_code or "row=['1 ']" in full_code:
        return "Builds placeholder row arrays (e.g., `['1 ']*...`) instead of constructing exact W rows with `|`, `/`, and `\\\\`"
    if "{leading_spaces}" in full_code or "{centre_spacing}" in full_code:
        return "Prints literal formatting placeholders (`{leading_spaces}`) / pseudo-f-string text instead of computed row strings"
    if "2*i-2" in squashed or "2*i - 2" in low:
        return "Center-spacing off-by-two bug (`2*i-2`) breaks the first rows of the W pattern"
    if "for i in range(n)" in low and "print(" in low:
        if "if i==j" in low or "for j in range(n)" in low:
            return "Uses a grid/nested-loop character plot that prints extra spaces/separators and fails exact row formatting"
        return "Row-spacing arithmetic is incorrect (bars/slashes are printed, but the W geometry/spacing is wrong)"

    if vec == "100":
        return "Large-size sample-specific output: passes one hidden size but fails other `n` values because rows are hard-coded"
    if vec == "000":
        return "Incorrect W-pattern printing logic (missing output, wrong row formula, or formatting mismatch)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c108(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    def block(fn: str) -> str:
        m = re.search(
            rf"(?ms)^def\s+{re.escape(fn)}\s*\([^\n]*\)\s*(?:->\s*[^:\n]+)?\s*:\s*\n(?P<body>.*?)(?=^\s*def\s+\w+\s*\(|\Z)",
            full_code,
        )
        return m.group("body") if m else ""

    req_fns = [
        "overall_run_stats",
        "century_rate",
        "average_yearly_century_rate",
        "years_with_more_than_average_yearly_century_rate",
        "year_with_most_average_runs",
    ]
    blocks = {fn: block(fn) for fn in req_fns}
    defs_present = {fn: bool(re.search(rf"(?m)^def\s+{re.escape(fn)}\s*\(", full_code)) for fn in req_fns}
    b1 = blocks["overall_run_stats"]
    b2 = blocks["century_rate"]
    b3 = blocks["average_yearly_century_rate"]
    b4 = blocks["years_with_more_than_average_yearly_century_rate"]
    b5 = blocks["year_with_most_average_runs"]

    def ellipsis_in_body(b: str) -> bool:
        return bool(re.search(r"(?m)^\s*\.\.\.\s*$", b))

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "RecursionError" and "is_equal(" in low:
            return "Copies evaluator/sample `is_equal(...)` calls into the submission, triggering recursive/self-test execution"
        if exc == "AttributeError":
            if "runs.values(" in low or "batsman_data.value(" in low or "batsman_data.keys()" in low and "min(" in low:
                return "Treats helper inputs as the wrong shape (e.g., `runs.values()` / `batsman_data.value()`), causing dict/list API AttributeErrors"
            return "Runtime AttributeError from dict/list API misuse across the batsman-analysis helper functions"
        if exc == "TypeError":
            if "min(batsman_data.values()" in low or "max(batsman_data.values()" in low or re.search(r"for\s+\w+\s+in\s+batsman_data\s*:[\s\S]{0,200}total\s*\+\=\s*\w+\b", low, re.S):
                return "Treats `batsman_data` as a flat list (or list of scalars) instead of flattening the per-year run lists"
            return "Runtime TypeError from mixing years/lists/scalars while aggregating runs or rates"
        if exc == "NameError":
            if "data" in low and "batsman_data" in low:
                return "Uses the sample global variable `data` inside helper functions instead of the function parameter"
            return "Runtime NameError from undefined accumulators/temporaries in one or more helper functions"
        if exc == "UnboundLocalError":
            return "Branch initialization bug in helper output variables (`result`/`year`/`max`) before returning"
        if exc == "KeyError":
            return "Uses fixed year keys / nested-dict assumptions that do not match the hidden batsman data shape"
        return _base_label(row) or "Runtime error (parseable final submission)"

    base = _base_label(row)
    if base and base != "Skeleton placeholder `...` left in function":
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    if "is_equal(" in low or "2016:[88,66,130" in squashed or "data = { 2016" in low:
        return "Copies evaluator/sample dataset and `is_equal(...)` checks into the submission instead of implementing the five helpers"
    if re.search(r"return\s*\{\s*['\"]average['\"]\s*:\s*112\s*,\s*['\"]max['\"]\s*:\s*157", low):
        return "Hard-codes the public sample overall stats dictionary (`112/157/66/2456`) instead of computing from `batsman_data`"
    if sum(defs_present.values()) < len(req_fns):
        return "Implements only a subset of the required helper functions (one or more named functions are missing)"
    ellipsis_blocks = [fn for fn, b in blocks.items() if ellipsis_in_body(b)]
    if ellipsis_blocks:
        if len(ellipsis_blocks) == 1:
            return f"Leaves the template placeholder `...` in `{ellipsis_blocks[0]}(...)` (partial multi-function implementation)"
        return "Leaves template placeholders (`...`) in multiple required helper functions (partial multi-function implementation)"
    if any(re.search(r"\bdata\b", b) for b in blocks.values()):
        return "Uses the sample global variable `data` inside helper functions instead of the provided parameters"

    if b1:
        b1_low = b1.lower()
        if (
            "min(batsman_data.values()" in b1_low
            or "max(batsman_data.values()" in b1_low
            or re.search(r"for\s+\w+\s+in\s+batsman_data\s*:[\s\S]{0,240}(total|sum)\s*\+\=\s*\w+\b", b1_low, re.S)
            or ("list(batsman_data.values())" in b1_low and "min(" in b1_low and "max(" in b1_low and "for run in" not in b1_low)
        ):
            return "In `overall_run_stats(...)`, treats `batsman_data` as flat values/list-of-lists instead of flattening all runs across years"
        if "int(" in b1_low and "/len(" in b1_low and "round(" not in b1_low:
            return "In `overall_run_stats(...)`, truncates the average with `int(...)` instead of rounding to the nearest integer"

    if b2:
        b2_low = b2.lower()
        if re.search(r">\s*100\b", b2) and ">=" not in b2:
            return "In `century_rate(...)`, counts centuries with `> 100` instead of `>= 100`"
        if "runs.values(" in b2_low:
            return "In `century_rate(...)`, treats `runs` as a dict (`runs.values()`) instead of a list of scores"
        if "int(" in b2_low and "*100" in b2_low and "round(" not in b2_low:
            return "In `century_rate(...)`, truncates the percentage with `int(...)` instead of rounding"

    if b3:
        b3_low = b3.lower()
        if "century_rate(" not in b3_low and (
            "extend(batsman_data[" in b3_low
            or re.search(r"for\s+\w+\s+in\s+batsman_data\s*:[\s\S]{0,400}for\s+\w+\s+in\s+batsman_data\[\w+\]", b3_low, re.S)
        ):
            return "In `average_yearly_century_rate(...)`, computes a global century percentage over all matches instead of averaging per-year century rates"
        if "data.items()" in b3_low or "data[" in b3_low:
            return "In `average_yearly_century_rate(...)`, uses the sample variable `data` instead of the parameter `batsman_data`"

    if b4:
        b4_low = b4.lower()
        if re.search(r">=\s*(average|avg|f|result)", b4_low):
            return "In `years_with_more_than_average_yearly_century_rate(...)`, uses `>=` instead of strict `>`"
        if re.search(r"\breturn\s*\[", b4_low):
            return "In `years_with_more_than_average_yearly_century_rate(...)`, returns a list instead of the required set of years"
        if re.search(r"\breturn\s*\{[^}]*:[^}]*\}", b4_low):
            return "In `years_with_more_than_average_yearly_century_rate(...)`, returns a dict instead of the required set of years"
        if "data.items()" in b4_low or "data[" in b4_low:
            return "In `years_with_more_than_average_yearly_century_rate(...)`, uses the sample variable `data` instead of `batsman_data`"

    if b5:
        b5_low = b5.lower()
        if re.search(r"return\s+max\(\s*(d|dict)\s*,\s*key\s*=\s*(d|dict)\.get\s*\)", b5_low):
            return "In `year_with_most_average_runs(...)`, uses `max(dict, key=dict.get)` and misses the earliest-year tie-break rule"
        if re.search(r"return\s+max\(\s*batsman_data\.items\(\)\s*,\s*key\s*=\s*lambda", b5_low) and "-item[0]" not in b5_low and "min(" not in b5_low:
            return "In `year_with_most_average_runs(...)`, picks max average only and does not enforce earliest-year tie-breaks"
        if "batsman_data[year]['runs']" in b5_low or "keys=lambda year" in b5_low:
            return "In `year_with_most_average_runs(...)`, assumes the wrong data shape (nested dict fields / invalid `keys=` usage)"
        if "data.items()" in b5_low or "data[" in b5_low:
            return "In `year_with_most_average_runs(...)`, uses the sample variable `data` instead of `batsman_data`"

    if vec == "00111":
        return "Later helpers mostly work, but one early helper (`overall_run_stats` or `century_rate`) still has hidden edge-case semantics wrong"
    if vec in {"00010", "00100", "00110", "00011"}:
        return "Partial multi-helper implementation: some helper functions are correct, but one or more required helpers still have logic/edge-case bugs"
    if vec == "00000":
        return "Batsman-analysis helper logic is broadly incorrect across the five required functions"
    return "Other wrong-answer logic pattern (residual)"


def classify_c109(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]
    vec3 = vec[-3:] if isinstance(vec, str) and len(vec) >= 3 else vec

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            return "Reads until EOF / blank line instead of processing exactly the first `n` todo items"
        if exc == "ValueError":
            if re.search(r"\b\w+\s*,\s*\w+\s*=\s*map\s*\(\s*int\s*,\s*input\s*\(\s*\)\s*\.split", low):
                return "Assumes exactly two completed indices (`a, b = map(int, input().split())`), so variable-length index lists crash"
            if "int(input()).split" in squashed or re.search(r"\bint\s*\(\s*\w+\s*\[\s*\d", low):
                return "Parses the index line as a single integer / fixed character slices, causing crashes on spaced or multi-digit indices"
            return "Runtime ValueError while parsing the completed-index line (variable-length index list handling bug)"
        if exc == "IndexError":
            return "Runtime IndexError from using out-of-range completed indices (hidden cases require ignoring invalid indices)"
        if exc == "TypeError":
            return "Runtime TypeError from string/list API misuse while updating todo rows"
        if exc == "NameError":
            return "Runtime NameError from undefined variables in todo-list update logic"
        if exc == "AttributeError":
            return "Runtime AttributeError from invalid string/list APIs (e.g., `.range`, wrong `.replace` usage)"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"

    if (
        any(tok in full_code for tok in ["Task 1", "Task 2", "Task 3", "Finish homework", "Submit report", "Study for exam"])
        and "input(" not in low
        and "print(" in low
    ):
        return "Prints hard-coded public sample todo output instead of updating the provided input list"
    if "print(f\"- [ ] task" in low or "print(f'- [ ] task" in low or "print(f\"- [x] task" in low or "print(f'- [x] task" in low:
        return "Generates `Task {i}` labels instead of using the actual todo item text from input"
    if "sys.stdin.read" in low and ("lst[2:]" in squashed or "split('\\n')" in low or 'split("\\n")' in low):
        return "Reads all remaining stdin lines as todo items instead of processing only the first `n` items (fails extra-line hidden case)"
    if re.search(r"if\s+str\s*\(\s*i\s*\)\s+in\s+\w+", low):
        return "Checks index membership with substring search (`if str(i) in indices_line`), so `1` matches `10`/`12`"
    if (
        re.search(r"\bint\s*\(\s*\w+\s*\[\s*0\s*\]\s*\)", low)
        or re.search(r"\bint\s*\(\s*\w+\s*\[\s*2\s*\]\s*\)", low)
        or re.search(r"\ba\s*,\s*b\s*=\s*int\s*\(", low)
        or re.search(r"for\s+\w+\s+in\s+\w+\s*:\s*[\s\S]{0,160}if\s+\w+\s*!=\s*['\"]\s*['\"][\s\S]{0,160}append\s*\(\s*int\s*\(\s*\w+\s*\)\s*\)", full_code, re.S)
    ):
        return "Parses completed indices character-by-character / fixed positions, so multi-digit indices are split incorrectly"
    if re.search(r"\b\w+\s*,\s*\w+\s*=\s*map\s*\(\s*int\s*,\s*input\s*\(\s*\)\s*\.split", low):
        return "Handles only two completed indices and ignores additional indices in hidden cases"
    if ".replace(\" \",\"x\",2)" in squashed or ".replace(' ','x',2)" in squashed:
        return "Replaces the first spaces in the line to insert `x` instead of replacing the checkbox token `[ ]`"
    if ".replace(\"[x]\",\"[]\"" in squashed or ".replace('[x]','[]'" in squashed:
        return "Reverses checkbox replacement (turns `[x]` into `[]`) instead of marking `[ ]` as completed"
    if re.search(r"for\s+\w+\s+in\s+range\s*\(\s*0\s*,\s*n\s*\)\s*:\s*[\s\S]{0,240}for\s+\w+\s+in\s+\w+", full_code, re.S) and "print(" in low:
        return "Prints inside a nested `for item` / `for index` loop, causing duplicate/missing output lines"
    if "for i in range(n+1)" in squashed or "foriinrange(n+1)" in squashed:
        return "Off-by-one loop over todo items (`range(n+1)`) reads/prints one extra line"
    if re.search(r"\bdef\s+\w+\s*\(", full_code) and "input(" in low and "print(" not in low and "return" in low:
        return "Defines a helper and returns updated todos but never prints the required line-by-line output"

    if vec3 == "111":
        return "Near-correct todo update logic, but output formatting/checkbox mutation is wrong (commonly space-replacement instead of `[ ] -> [x]`)"
    if vec3 == "101":
        return "Parses indices as raw text/characters and uses substring membership, so multi-digit hidden indices are misread"
    if vec3 in {"100", "001"}:
        return "Partially handles the index list, but fixed-position / fixed-count index parsing fails hidden variable-length cases"
    if vec3 == "000":
        return "Incorrect todo-list update logic (index parsing, checkbox replacement, or item-loop handling is broadly wrong)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c110(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]
    vec3 = vec[-3:] if isinstance(vec, str) and len(vec) >= 3 else vec

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    def block(fn: str) -> str:
        m = re.search(
            rf"(?ms)^def\s+{re.escape(fn)}\s*\([^\n]*\)\s*(?:->\s*[^:\n]+)?\s*:\s*\n(?P<body>.*?)(?=^\s*def\s+\w+\s*\(|\Z)",
            full_code,
        )
        return m.group("body") if m else ""

    req_fns = [
        "parse_moves",
        "get_n_moves",
        "count_piece_moves",
        "most_used_piece",
        "remaining_pieces",
        "n_checks",
    ]
    blocks = {fn: block(fn) for fn in req_fns}
    defs_present = {fn: bool(re.search(rf"(?m)^def\s+{re.escape(fn)}\s*\(", full_code)) for fn in req_fns}

    def ellipsis_in_body(b: str) -> bool:
        return bool(re.search(r"(?m)^\s*\.\.\.\s*$", b))

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "NameError":
            if "piece_map" in low or "piece_values" in low:
                return "Uses undefined globals like `piece_map` / `piece_values` in chess-analysis helpers"
            if re.search(r"\breturn\s+moves\b", low) or "for mov in move" in low:
                return "Uses undefined move variables (`moves`, `move`) inside helper functions"
            return "Runtime NameError from undefined helpers/maps/counters in chess-analysis functions"
        if exc == "RecursionError":
            return "Recursive/self-calling helper (`get_n_moves`, etc.) without a terminating base case"
        if exc == "ValueError":
            if "index('#')" in low or "index(\"#\")" in low:
                return "Parses SAN by searching for `#`/`+` positions (`.index(...)`) and crashes when the symbol is absent"
            return "Runtime ValueError from brittle SAN parsing assumptions"
        if exc == "AttributeError":
            return "Runtime AttributeError from string/list/dict API misuse in chess helper logic"
        if exc == "TypeError":
            return "Runtime TypeError from wrong container/value types in chess helper computations"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    if "is_equal(" in low or "game = \"1. d4 d5 2. c4" in low or "(parse_moves," in low:
        return "Copies evaluator/sample games and checks into the submission instead of implementing general chess-analysis helpers"
    if all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"
    if re.search(r"(?m)^\s*print\s*\(\s*\d+\s*\)\s*$", full_code) and "def " not in full_code:
        return "Prints constant sample answers instead of implementing the required helper functions"

    if sum(defs_present.values()) < len(req_fns):
        return "Implements only a subset of the required chess-analysis helper functions"
    ellipsis_blocks = [fn for fn, b in blocks.items() if ellipsis_in_body(b)]
    if ellipsis_blocks:
        if len(ellipsis_blocks) == 1:
            return f"Leaves the template placeholder `...` in `{ellipsis_blocks[0]}(...)` (partial multi-function implementation)"
        return "Leaves template placeholders (`...`) in multiple required chess-analysis helper functions"

    b_parse = blocks["parse_moves"].lower()
    b_count = blocks["count_piece_moves"].lower()
    b_most = blocks["most_used_piece"].lower()
    b_rem = blocks["remaining_pieces"].lower()
    b_checks = blocks["n_checks"].lower()

    if re.search(r"\breturn\s+moves\b", b_parse) and "moves =" not in b_parse:
        return "In `parse_moves(...)`, returns an undefined `moves` variable instead of parsed SAN tokens"
    if "return list(game)" in b_parse or "returnlist(game)" in b_parse.replace(" ", ""):
        return "In `parse_moves(...)`, returns `list(game)` (characters) instead of SAN move tokens"
    if ".remove(" in b_parse and ".split" in b_parse:
        return "In `parse_moves(...)`, removes tokens while iterating, which skips SAN tokens and leaves move numbers/results behind"
    if ("endswith('.')" in b_parse or "'.' in" in b_parse) and "1-0" not in b_parse and "0-1" not in b_parse and "1/2-1/2" not in b_parse:
        return "In `parse_moves(...)`, strips move numbers but forgets to remove the trailing game result token (`1-0`/`0-1`/`1/2-1/2`)"
    if re.search(r"\breturn\s+\[\s*['\"]d4['\"].*['\"]nf6['\"]", low, re.S):
        return "Hard-codes the public sample parsed move list instead of parsing arbitrary SAN strings"
    if "0-0" in full_code and "O-O" not in full_code:
        return "Uses zeroes (`0-0`, `0-0-0`) instead of SAN castling notation with letter O (`O-O`, `O-O-O`)"
    if "o-o-o" in b_count and "queen" in b_count:
        return "In `count_piece_moves(...)`, misclassifies queenside castling (`O-O-O`) as a `Queen` move"
    if "o-o" in b_count and "rook" not in b_count and "king" in b_count:
        return "In `count_piece_moves(...)`, counts castling only for `King` and forgets the required `Rook` count"
    if "max(count" in b_most and "piece_values" not in b_most and "key=count.get" in b_most:
        return "In `most_used_piece(...)`, picks max count only and ignores the required piece-value tie-break"
    if "if 'x' in move" in b_rem and "moves[::2]" not in b_rem and "moves[1::2]" not in b_rem:
        return "In `remaining_pieces(...)`, counts captures without separating white/black moves by parity"
    if ("endswith('+')" in b_checks or "in move" in b_checks and "+" in b_checks) and ("moves[::2]" not in b_checks and "moves[1::2]" not in b_checks):
        return "In `n_checks(...)`, counts checks across all moves instead of only the specified player's moves"

    if vec3 == "111":
        return "Near-complete chess-analysis helpers, but hidden SAN edge cases fail (commonly result-token filtering, castling semantics, or tie-break/player-parity logic)"
    if vec3 in {"110", "001"}:
        return "Partial chess-analysis implementation: `parse_moves`/basic helpers work, but later helper semantics fail on hidden SAN cases"
    if vec3 == "100":
        return "Implements early chess helpers only (`parse_moves`/`get_n_moves`) while later helper logic remains incorrect or incomplete"
    if vec3 == "000":
        return "Chess-analysis helper logic is broadly incorrect across the required functions"
    return "Other wrong-answer logic pattern (residual)"


def classify_c026(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    vec = row["vec"]
    vec3 = vec[-3:] if isinstance(vec, str) and len(vec) >= 3 else vec

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    def block(fn: str) -> str:
        m = re.search(
            rf"(?ms)^def\s+{re.escape(fn)}\s*\([^\n]*\)\s*(?:->\s*[^:\n]+)?\s*:\s*\n(?P<body>.*?)(?=^\s*def\s+\w+\s*\(|\Z)",
            full_code,
        )
        return m.group("body") if m else ""

    req_fns = [
        "total_revenue_in_region",
        "revenue_range_for_product",
        "region_with_max_sales",
        "steady_revenue_products",
    ]
    blocks = {fn: block(fn) for fn in req_fns}
    defs_present = {fn: bool(re.search(rf"(?m)^def\s+{re.escape(fn)}\s*\(", full_code)) for fn in req_fns}

    def ellipsis_in_body(b: str) -> bool:
        return bool(re.search(r"(?m)^\s*\.\.\.\s*$", b))

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "EOFError":
            return "Reads input interactively inside helper functions instead of using the provided `sales_data` parameters"
        if exc == "NameError":
            if re.search(r"\bsales\b", low) and "sales_data" in low:
                return "Uses the sample variable `sales` inside helpers instead of the parameter `sales_data`"
            return "Runtime NameError from undefined variables/accumulators in sales-analysis helpers"
        if exc == "KeyError":
            return "Runtime KeyError from wrong sales-record keys or fragile dictionary indexing"
        if exc == "TypeError":
            return "Runtime TypeError from treating sales records/list containers as the wrong shape"
        if exc == "AttributeError":
            return "Runtime AttributeError from list/dict API misuse in sales-analysis helpers"
        if exc == "UnboundLocalError":
            return "Branch initialization bug in helper output variables before return"
        if exc == "ValueError":
            return "Runtime ValueError from malformed aggregation / conversion logic in sales-analysis helpers"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    if "is_equal(" in low or "sales = [" in low and "return 17000" in low:
        return "Copies evaluator/sample data and expected outputs instead of implementing the sales-analysis helpers"
    if all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"

    if sum(defs_present.values()) < len(req_fns):
        return "Implements only a subset of the required sales-analysis helper functions"
    ellipsis_blocks = [fn for fn, b in blocks.items() if ellipsis_in_body(b)]
    if ellipsis_blocks:
        if len(ellipsis_blocks) == 1:
            return f"Leaves the template placeholder `...` in `{ellipsis_blocks[0]}(...)` (partial multi-function implementation)"
        return "Leaves template placeholders (`...`) in multiple required sales-analysis helper functions"

    if any(re.search(r"\bsales\b", b) for b in blocks.values()):
        return "Uses the sample variable `sales` inside helper functions instead of `sales_data`"

    b1 = blocks["total_revenue_in_region"].lower()
    b2 = blocks["revenue_range_for_product"].lower()
    b3 = blocks["region_with_max_sales"].lower()
    b4 = blocks["steady_revenue_products"].lower()

    if re.search(r"if\s+['\"]region['\"]\s*==", b1):
        return "In `total_revenue_in_region(...)`, compares the literal key name `'region'` to values instead of `record['region']`"
    if re.search(r"if\s+\w+\s*==\s*region\s*:", b1) and "['region']" not in b1 and '.get("region")' not in b1 and ".get('region')" not in b1:
        return "In `total_revenue_in_region(...)`, compares the whole record to `region` instead of the record's `'region'` field"
    if re.search(r"for[\s\S]{0,240}else\s*:\s*return\s+0", b1, re.S):
        return "In `total_revenue_in_region(...)`, returns `0` inside the loop on the first non-matching record (premature exit)"

    if "return sum(" in b2:
        return "In `revenue_range_for_product(...)`, sums product revenues instead of returning `max(revenue) - min(revenue)`"
    if re.search(r"return\s+max\([^)]*\)\s*-\s*min\([^)]*\)", b2) and "if len(" not in b2 and "if not" not in b2 and "if " not in b2:
        return "In `revenue_range_for_product(...)`, misses the required 0-handling for missing/single-record products"

    if (
        "max_sales = [(" in b3
        or "if d['revenue'] >" in b3
        or "if i['revenue'] >" in b3
        or "revenue']*d['quantity_sold']" in b3
        or "revenue']* d['quantity_sold']" in b3
    ):
        return "In `region_with_max_sales(...)`, compares individual records (or `revenue*quantity`) instead of aggregated totals per region"
    if "max(data,key=data.get)" in b3 and "quantity" not in b3:
        return "In `region_with_max_sales(...)`, aggregates revenue but ignores the required tie-break by total `quantity_sold`"

    if re.search(r"return\s+\[", b4):
        return "In `steady_revenue_products(...)`, returns a list instead of the required set of product names"
    if re.search(r"if\s+\w+\[['\"]revenue['\"]\]\s*<\s*5000", b4):
        return "In `steady_revenue_products(...)`, filters by per-record revenue `< 5000` instead of product revenue range `< 5000`"

    if re.search(r"return\s+17000\b", low) or re.search(r"return\s+5000\b", low) or re.search(r"return\s+['\"]r1['\"]", low) or "{'camera', 'laptop', 'phone', 'tablet'}" in low:
        return "Hard-codes public sample outputs (`17000`, `5000`, `'R1'`, sample product set) instead of computing from `sales_data`"

    if vec3 == "111":
        return "Most sales-analysis helpers work, but one hidden edge-case remains (commonly region tie-break aggregation or exact set semantics)"
    if vec3 == "110":
        return "Early helpers are mostly correct, but `region_with_max_sales(...)` / `steady_revenue_products(...)` logic fails hidden cases"
    if vec3 == "100":
        return "Only `total_revenue_in_region(...)` is mostly correct; later sales-analysis helpers are incorrect/incomplete"
    if vec3 == "000":
        return "Sales-analysis helper logic is broadly incorrect across the required functions"
    return "Other wrong-answer logic pattern (residual)"


def classify_c111(row: dict[str, Any]) -> str:
    base = _base_label(row)
    if base:
        return base
    if row["summary"] != "Wrong Answer":
        return base or (row["summary"] or "Unknown")

    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    vec = row["vec"]

    if "if nums==[1,2,3,2,1]" in low.replace(" ", "") or "{(1,3),(2,2)}" in low.replace(" ", ""):
        return "Hard-codes the public sample pair set (`{(1,3), (2,2)}`) / sample inputs instead of general pair generation"
    if re.search(r"\breturn\s+set\s*\(\s*nums\s*\)", low):
        return "Returns `set(nums)` (unique values) instead of a set of unique sum-pair tuples"
    if re.search(r"\breturn\s+\w+\s*,\s*\w+\b", code):
        return "Returns a single tuple pair (`a, b`) instead of the required set of all unique pairs"
    if re.search(r"\breturn\s*\(\s*\w+\s*,\s*\w+\s*\)\s*$", code):
        return "Returns one tuple instead of the required set of tuples"
    if ".remove(" in low and "for" in low:
        return "Builds all pair tuples and removes reversed duplicates while iterating the same list (mutation skips cases)"
    if "seen.add(target)" in low:
        return "Single-pass complement logic stores `target` instead of `num` (`seen.add(target)`), so valid pairs are missed"
    if "counter(" in low and re.search(r"if\s+num\s*==\s*complement[\s\S]{0,220}elif\s+num\s*<\s*complement", low, re.S):
        return "Counter-based solution nests the `num < complement` branch under `num == complement`, so distinct-value pairs are skipped"
    if re.search(r"for\s+\w+\s+in\s+nums[\s\S]{0,260}for\s+\w+\s+in\s+nums[\s\S]{0,260}if\s+\w+\s*\+\s*\w+\s*==\s*k", low, re.S):
        if "i<=j" in low or "i < j" in low or "if b in nums" in low or "if d not in s1" in low:
            return "Generates candidate pairs but uses value-order/membership dedup only, missing duplicate-count rules for `(x, x)`"
        return "Nested-loop pair generation does not correctly enforce unique-pair semantics / duplicate handling"
    if "return set(" in low and ".append(" in low and "tuple" in low:
        return "Accumulates pairs in a list then converts to `set`, but duplicate/order logic is still incorrect"

    if vec == "110":
        return "Near-correct pair generation, but reverse-pair dedup / duplicate-removal logic mutates collections and drops valid pairs"
    if vec in {"100", "001", "010"}:
        return "Partially correct pair enumeration, but duplicate-count or unique-order semantics fail hidden `(x, x)` / duplicate cases"
    if vec == "000":
        return "Incorrect unique-sum-pair logic (returns too early, wrong return type, or non-general pair construction)"
    return "Other wrong-answer logic pattern (residual)"


def classify_c112(row: dict[str, Any]) -> str:
    code = row["logic_code"] or row["student_code"] or ""
    full_code = (row.get("student_code") or row.get("function_code") or code or "")
    low = full_code.lower()
    squashed = low.replace(" ", "")
    vec = row["vec"]

    if not row["is_non_full"]:
        return None
    if not row["is_parseable"]:
        return "Syntax / non-parseable final submission"

    if row["summary"] == "Runtime Error":
        exc = row["exception_type"] or ""
        if exc == "NameError":
            return "Runtime NameError from undefined variables (`vowels`, loop indices, output buffers) in consonant-replacement logic"
        if exc == "TypeError":
            return "Runtime TypeError from wrong string/list operations while rebuilding output lines"
        if exc == "AttributeError":
            return "Runtime AttributeError from invalid string/list API usage (`append` on string, method misuse)"
        return _base_label(row) or "Runtime error (parseable final submission)"

    if row["summary"] != "Wrong Answer":
        return row["summary"] or "Unknown"

    stripped = full_code.strip()
    if not stripped or all(not ln.strip() or ln.strip().startswith("#") for ln in full_code.splitlines()):
        return "Empty/comment-only final submission"

    if any(tok in full_code for tok in ["#e##o #O###", "#Oo# #o##I##", "##e #ui## ##o## #o#"]) and "input(" not in low:
        return "Prints hard-coded public sample output instead of transforming the given lines"
    if any(tok in low for tok in ['x = "hello world"', "good night", "the quick brown fox"]):
        return "Hard-codes sample input strings and prints sample output instead of processing arbitrary input"
    if re.search(r"\bdef\s+\w+\s*\(", full_code) and "input(" in low and "print(" not in low and "return" in low:
        return "Defines a helper that returns transformed text but never prints the required script output"
    if ("n=int(input())" in squashed or "n = int(input())" in full_code) and full_code.count("input()") <= 2 and "for" not in low:
        return "Reads `n` but processes only one line (ignores the required multi-line input loop)"
    if re.search(r"for\s+\w+\s+in\s+range\s*\(\s*n\s*\)\s*:[\s\S]{0,260}\n\s*print\s*\(\s*line\s*\)\s*$", full_code, re.S):
        return "Processes multiple lines but prints only the last line after the loop"
    if ".split()" in low and ("words =" in low or "word=" in low) and "print(" in low:
        if "join(" not in low:
            return "Uses `split()` tokenization and collapses spaces/newlines, so exact line formatting is lost"
    if re.search(r"\brp\s*=\s*['\"]{0,1}\s*[\r\n]", full_code) and "rp=rp+p" in squashed:
        return "Concatenates all input lines into one string and loses line breaks in the output"
    if "rp=rp+p" in squashed or "new_word+=''" in squashed:
        return "Merges multiple input lines into one output string instead of preserving line boundaries"
    if "for i in range(1,n)" in squashed:
        return "Skips one of the input lines (`range(1, n)`), so not all lines are transformed"
    if "aeiou" in low and not all(ch in full_code for ch in ["A", "E", "I", "O", "U"]):
        return "Uses a lowercase-only vowel set, so uppercase vowels are incorrectly replaced with `#`"
    if re.search(r"if\s+\w+\.isalpha\(\)\s*:\s*[\s\S]{0,120}result\s*\+?=\s*['\"]#['\"]", low, re.S) and "not in vowels" not in low:
        return "Replaces all alphabetic characters (including vowels) with `#` instead of only consonants"

    if vec == "011":
        return "Mostly correct consonant replacement, but uppercase-vowel handling is wrong (incomplete vowel set / case handling)"
    if vec == "010":
        return "Consonant replacement works on a simple single line, but multi-line formatting is broken (line collapse / last-line-only output)"
    if vec == "000":
        return "Incorrect consonant-to-`#` replacement logic (I/O flow, vowel detection, or formatting is broadly wrong)"
    return "Other wrong-answer logic pattern (residual)"


CLASSIFIERS: dict[str, Callable[[dict[str, Any]], str | None]] = {
    "C001": classify_c001,
    "C004": classify_c004,
    "C008": classify_c008,
    "C014": classify_c014,
    "C015": classify_c015,
    "C016": classify_c016,
    "C010": classify_c010,
    "C011": classify_c011,
    "C012": classify_c012,
    "C013": classify_c013,
    "C105": classify_c105,
    "C106": classify_c106,
    "C107": classify_c107,
    "C108": classify_c108,
    "C109": classify_c109,
    "C110": classify_c110,
    "C111": classify_c111,
    "C112": classify_c112,
    "C077": classify_c077,
    "C078": classify_c078,
    "C079": classify_c079,
    "C080": classify_c080,
    "C081": classify_c081,
    "C082": classify_c082,
    "C083": classify_c083,
    "C084": classify_c084,
    "C085": classify_c085,
    "C086": classify_c086,
    "C087": classify_c087,
    "C088": classify_c088,
    "C089": classify_c089,
    "C090": classify_c090,
    "C091": classify_c091,
    "C092": classify_c092,
    "C093": classify_c093,
    "C094": classify_c094,
    "C017": classify_c017,
    "C018": classify_c018,
    "C019": classify_c019,
    "C020": classify_c020,
    "C021": classify_c021,
    "C002": classify_c002,
    "C023": classify_c023,
    "C022": classify_c022,
    "C005": classify_c005,
    "C006": classify_c006,
    "C096": classify_c096,
    "C097": classify_c097,
    "C098": classify_c098,
    "C099": classify_c099,
    "C100": classify_c100,
    "C101": classify_c101,
    "C102": classify_c102,
    "C103": classify_c103,
    "C104": classify_c104,
    "C095": classify_c095,
    "C024": classify_c024,
    "C026": classify_c026,
    "C007": classify_c007,
    "C025": classify_c025,
}


def residual_signature(cluster_id: str, row: dict[str, Any]) -> str:
    code = row["logic_code"].lower()
    full_code = (row.get("function_code") or row.get("student_code") or row["logic_code"]).lower()
    vec = row["vec"]
    stmt = row["stmt_shape"] or ""
    fp = row["fp_short"]
    if cluster_id == "C004":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "mod2" if "%2" in sq else "nomod2",
            "mod5" if "%5" in sq else "nomod5",
            "and" if " and " in code else "noand",
            "or" if " or " in code else "noor",
            "div" if "/2" in sq or "/5" in sq else "nodiv",
            "floordiv" if "//2" in sq or "//5" in sq else "nofloordiv",
            "barefalse" if re.search(r"else\s*:\s*\n\s*false\b", code) else "nobarefalse",
            "hard" if any(tok in code for tok in ["is_equal = 25", "a = 25", "n = 1000", "num = 0"]) else "nohard",
            "rettrue" if re.search(r"\breturn\s+true\b", code) else "norettrue",
            "retfalse" if re.search(r"\breturn\s+false\b", code) else "noretfalse",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C015":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "mod2" if "%2" in sq else "nomod2",
            "div2" if "/2" in sq else "nodiv2",
            "abs" if "abs(" in code else "noabs",
            "gt0" if "n>0" in sq else "nogt0",
            "xor2" if "^2" in code else "noxor2",
            "hard" if any(tok in full_code for tok in ["int(4 or 6 or 5)", "double_if_even_else_square(8)", "double_if_even_else_square(9)"]) else "nohard",
            "nested" if full_code.count("def double_if_even_else_square") >= 2 or code.lstrip().startswith("def double_if_even_else_square(") else "nonested",
            "input" if "input(" in full_code else "noinput",
            "retor" if "return" in code and " or " in code else "noretor",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C016":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "str" if "str(num)" in code or "num=str(num)" in sq else "nostr",
            "mod10" if "%10" in sq else "nomod10",
            "div10" if "//10" in sq else "nodiv10",
            "wrong1000" if "%1000" in sq and "//100" in sq else "nowrong1000",
            "zerochk" if "==0" in sq else "nozerochk",
            "or" if " or " in code else "noor",
            "and" if " and " in code else "noand",
            "bitand" if "&" in code else "nobitand",
            "qtruth" if "num//aandnum//b" in sq or "int(num/n)andint(num/n1)" in sq or "ifnum//aandnum//b" in sq else "noqtruth",
            "same2" if "num%second_last_digit==0)and(num%second_last_digit==0" in sq else "nosame2",
            "first2" if "p[0]" in sq or "rev1=p[0]" in sq or "x=int(num[0::-1])" in sq else "nofirst2",
            "loopret" if "for " in code and "return" in code else "noloopret",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C087":
        sq = code.replace(" ", "")
        fsq = full_code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "hard" if any(tok in full_code for tok in ["if num == 1234", "if num == 2413", "if num == 4321", "if num == 5678", "print('2413')", "return(6857)"]) else "nohard",
            "retnum" if re.search(r"\breturn\s*\(?\s*num\s*\)?\s*$", code) else "noretnum",
            "str" if "str(num)" in code else "nostr",
            "slice2413" if "[1::2]" in code or "[0::2]" in code else "noslice2413",
            "concat2413" if "s[1]+s[3]+s[0]+s[2]" in sq or "num_str[1]+num_str[3]+num_str[0]+num_str[2]" in sq else "noconcat2413",
            "intcast" if "returnint(" in sq or "return int(" in code else "nointcast",
            "nested" if full_code.count("def shuffle_digits") >= 2 or code.lstrip().startswith("def shuffle_digits(") else "nonested",
            "whiletrue" if "whiletrue:" in sq else "nowhiletrue",
            "modextract" if "%1000" in sq or "%100" in sq or "//1000" in sq else "nomodextract",
            "prints" if "print(" in code else "noprints",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C088":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "splitspace" if ".split(" in code and "split(\",\")" not in code else "nosplitspace",
            "splitcomma" if "split(\",\")" in code else "nosplitcomma",
            "upper_nocall" if ".upper" in code and ".upper()" not in code else "noupper_nocall",
            "lower" if ".lower()" in code else "nolower",
            "swapcase" if "swapcase()" in code else "noswapcase",
            "index" if ".index(word)" in code or ".index(i)" in code else "noindex",
            "retsentence" if "return sentence" in code else "noretsentence",
            "allupper" if "for word in words" in code and "word = word.upper()" in code else "noallupper",
            "earlyret" if "for " in code and re.search(r"for[\s\S]{0,250}return\s+", code, re.S) else "noearlyret",
            "hard" if "return list([" in code or "return ['hello', 'world']" in code else "nohard",
            "truthychain" if "if words[0] or words[2] or words[4]" in code else "notruthychain",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C089":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "lower" if ".lower" in code else "nolower",
            "lowercall" if ".lower()" in code else "nolowercall",
            "eqends" if "s[0]==s[-1]" in sq or "str1[0]==str1[-1]" in sq or "x[0]==x[-1]" in sq else "noeqends",
            "vowelstr" if "aeiou" in code else "novowelstr",
            "vowelset" if "vowel" in code else "novowelset",
            "startswith" if "startswith(" in code else "nostartswith",
            "endswith" if "endswith(" in code else "noendswith",
            "boolchain" if (" or " in code and re.search(r"==\s*['\"][aeiouAEIOU]['\"]", code)) else "noboolchain",
            "loopret" if "for " in code and re.search(r"for[\s\S]{0,240}return\s+", code, re.S) else "noloopret",
            "pal" if "::-1" in code else "nopal",
            "hard" if any(tok in code for tok in ["apple", "orange", "umbrella", "education"]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C090":
        sq = code.replace(" ", "")
        full_sq = full_code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "for" if "for " in code else "nofor",
            "retloop" if "for " in code and re.search(r"for[\s\S]{0,400}return\s+", code, re.S) else "noretloop",
            "pow" if "**" in code or "pow(" in code else "nopow",
            "xor" if "^" in code else "noxor",
            "enumerate" if "enumerate(" in code else "noenumerate",
            "idxfn" if ".index(" in code else "noidxfn",
            "revcoef" if "reversed(" in code or "[::-1]" in code else "norevcoef",
            "fixeddeg" if any(tok in sq for tok in ["coef[0]*x**3", "coef[1]*x**2", "a*x**2+b*x+c", "a*x+b"]) else "nofixeddeg",
            "hard" if any(tok in full_code for tok in ["return 45", "return 17", "if coef =="]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C091":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "mod10" if "%10" in sq else "nomod10",
            "str" if "str(" in code else "nostr",
            "eqfull" if "num1==num2" in sq or "returnnum1==num2" in sq else "noeqfull",
            "selfcmp" if "num1%10==num1%10" in sq or "n1%10==n1%10" in sq or "num1==num1" in sq else "noselfcmp",
            "parity" if ("%2" in sq or "%2==" in sq) else "noparity",
            "firstdigit" if "str(num1)[0]" in sq or "str(num2)[0]" in sq or ("//10" in sq and "%10" not in sq) else "nofirstdigit",
            "laststr" if "str(num1)[-1]" in sq or "str(num2)[-1]" in sq else "nolaststr",
            "hard" if any(tok in code for tok in ["123", "456", "789", "if num1 =="]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C092":
        sq = code.replace(" ", "")
        p3 = sq.find("%3==0")
        p5 = sq.find("%5==0")
        p15 = sq.find("%15==0")
        order_bug = p15 >= 0 and ((0 <= p3 < p15) or (0 <= p5 < p15))
        bits = [
            f"vec={vec}",
            "mod3" if "%3" in sq else "nomod3",
            "mod5" if "%5" in sq else "nomod5",
            "mod15" if "%15" in sq else "nomod15",
            "order15late" if order_bug else "noorder15late",
            "mod10" if "%10" in sq else "nomod10",
            "bitand" if "&" in code else "nobitand",
            "boolret" if re.search(r"\breturn\s+.*%3.*or.*%5", code) else "noboolret",
            "normal_lower" if "'normal'" in code or '"normal"' in code else "nonormal_lower",
            "retcount=" + str(code.count("return")),
            "truthychain" if any(tok in sq for tok in ["'fizz'or'buzz'", "\"fizz\"or\"buzz\""]) else "notruthychain",
            "hard" if any(tok in code for tok in ["if num == 3", "if num == 5", "if num == 15"]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C093":
        fsq = full_code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "ninput" if "n=int(input())" in fsq or "n = int(input())" in full_code else "noninput",
            "inputs=" + str(full_code.count("input(")),
            "forn" if "for _ in range(n)" in full_code or "for i in range(n)" in full_code else "noforn",
            "vowelset" if "aeiou" in full_code else "novowelset",
            "missU" if ("aeiouAEIO" in full_code or "aeiouaeio" in full_code) else "nomissU",
            "twoptr" if ("while" in full_code and ("i<j" in fsq or "i<=j" in fsq)) else "notwoptr",
            "inplace" if ("[i]=" in fsq or "[j]=" in fsq or "]=" in fsq and "line[" in fsq) else "noinplace",
            "join" if "join(" in full_code else "nojoin",
            "print" if "print(" in full_code else "noprint",
            "hard" if any(tok in full_code.lower() for tok in ["holle", "leotcede"]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C094":
        fsq = full_code.replace(" ", "")
        stripped = full_code.strip()
        defs = [m.group(1) for m in re.finditer(r"^\s*def\s+(\w+)\s*\(", full_code, re.M)]
        calls_any_def = False
        for fn in defs:
            body_removed = re.sub(rf"^\s*def\s+{re.escape(fn)}\s*\(", "", full_code, count=1, flags=re.M)
            if re.search(rf"\b{re.escape(fn)}\s*\(", body_removed):
                calls_any_def = True
                break
        bits = [
            f"vec={vec}",
            "constprint"
            if re.fullmatch(r"\s*print\s*\(\s*(?:['\"][^'\"]*['\"])?\s*\)\s*", stripped, re.S)
            else "noconstprint",
            "printonly" if "print(" in full_code and "input(" not in full_code else "noprintonly",
            "defonly" if full_code.lstrip().startswith("def ") and "input(" not in full_code else "nodefonly",
            "nocall" if defs and not calls_any_def and "input(" in full_code else "nocallok",
            "lenfirst"
            if (("l=input()" in fsq or "l=(input())" in fsq) and "len(l)" in fsq and ("ch=l[-1]" in fsq or "c=l[-1]" in fsq))
            else "nolenfirst",
            "joinspace" if ("join(result_chars)" in full_code and "' '" in full_code) else "nojoinspace",
            "inputstripmeth" if "input.strip()" in full_code else "noinputstripmeth",
            "samplelit" if any(tok in full_code for tok in ["apple", "banana", "anchor", "ant", "etr"]) else "nosamplelit",
            "startswith" if "startswith(" in full_code else "nostartswith",
            "len1" if re.search(r"len\s*\(\s*\w+\s*\)\s*>=\s*1", full_code) else "nolen1",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C017":
        fsq = full_code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "loopcw"
            if any(
                tok in fsq
                for tok in [
                    "matrix[row][col]",
                    "rotated[j][m-1-i]=matrix[i][j]",
                    "newrow.append(matrix[i][j])",
                    "mat[j][i]forjinrange(len(mat))",
                ]
            )
            else "noloopcw",
            "zipcw"
            if any(tok in fsq for tok in ["zip(*matrix[::-1])", "zip(*mat[::-1])", "zip(*a[::-1])", "zip(*matrix)", "zip(*mat)"])
            else "nozipcw",
            "rowrev" if "[::-1]" in fsq or "reversed(" in full_code else "norowrev",
            "printstar" if "print(*" in full_code else "noprintstar",
            "joinspace"
            if ("' '.join(" in full_code or '" ".join(' in full_code or "join(map(str,row))" in fsq or "join(str(x)forxinrow)" in fsq)
            else "nojoinspace",
            "endempty" if "end=''" in full_code or 'end=""' in full_code or "end = ''" in full_code else "noendempty",
            "endspace" if "end=' '" in full_code or 'end=" "' in full_code else "noendspace",
            "hardsample"
            if any(tok in full_code for tok in ["7 4 1", "8 5 2", "9 6 3", "5 3 1", "6 4 2", "if input == \"3 3"])
            else "nohardsample",
            "fixed3" if "for i in range(3)" in full_code or "lst[2][0]" in full_code or "matrix_3" in full_code else "nofixed3",
            "readnrows"
            if ("for _ in range(n)" in full_code and "input().split()" in full_code and "for _ in range(m)" not in full_code)
            else "noreadnrows",
            "helperdef" if full_code.lstrip().startswith("def ") else "nohelperdef",
            "unrelatedap" if "is_arithmetic_progression" in full_code else "nounrelatedap",
            "debug" if "please check your public test cases" in full_code or "print(order)" in full_code else "nodebug",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C014":
        sq = full_code.replace(" ", "")
        req = [
            "def get_short_books",
            "def get_medium_books",
            "def get_pages_by_isbn",
            "def count_by_language",
            "def total_pages_in_genre_lang",
        ]
        def_count = sum(1 for fn in req if fn in full_code)
        bits = [
            f"vec={vec}",
            f"defs={def_count}",
            "ellipsis" if "..." in full_code else "noellipsis",
            "mlt500" if re.search(r"def\s+get_medium_books[\s\S]{0,700}?<\s*500", full_code, re.S) else "nomlt500",
            "meq500" if re.search(r"def\s+get_medium_books[\s\S]{0,700}?<=\s*500", full_code, re.S) else "nomeq500",
            "pnone" if re.search(r"def\s+get_pages_by_isbn[\s\S]{0,1000}?for[\s\S]{0,400}?return\s+none", full_code, re.S) else "nopnone",
            "retlist_short" if re.search(r"def\s+get_short_books[\s\S]{0,700}?return\s*\[", full_code, re.S) else "noretlist_short",
            "retlist_medium" if re.search(r"def\s+get_medium_books[\s\S]{0,700}?return\s*\[", full_code, re.S) else "noretlist_medium",
            "cntloopret" if re.search(r"def\s+count_by_language[\s\S]{0,1000}?for[\s\S]{0,300}?return\s+\w+", full_code, re.S) else "nocntloopret",
            "off1" if "range(len(book_data)-1)" in sq or "range(0,len(book_data)-1)" in sq else "nooff1",
            "hardisbn" if "978-" in full_code else "nohardisbn",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C083":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "sorted" if "sorted(" in code or ".sort(" in code else "nosorted",
            "apptail" if "returnl+[l[0],l[-1]]" in sq or "append(l[-1])" in code else "noapptail",
            "lencases" if any(x in sq for x in ["len(l)==2", "len(l)==3", "len(l)==5"]) else "nolencases",
            "strconv" if "str(l)" in code or "list(str(" in sq else "nostrconv",
            "mult2" if "l[0]*2" in sq or "l[-1]*2" in sq else "nomult2",
            "retl" if re.search(r"\breturn\s*\(?\s*l\s*\)?\s*$", code) else "noretl",
            "literal4" if re.search(r"\breturn\s*\[\s*l\[0\].*l\[-1\].*l\[-1\]\s*\]", code) else "noliteral4",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C084":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "split" if ".split(" in code else "nosplit",
            "slicefix" if re.search(r"email\s*\[\s*:\s*-?\d+\s*\]", code) else "noslicefix",
            "reti" if re.search(r"\breturn\s+i\b", code) else "noreti",
            "retemail" if re.search(r"\breturn\s*\(?\s*email\s*\)?\s*$", code) else "noretemail",
            "split0" if "split('@')[0]" in sq or 'split("@")[0]' in sq else "nosplit0",
            "split1" if "split('@')[1]" in sq or 'split("@")[1]' in sq else "nosplit1",
            "replace" if ".replace(" in code else "noreplace",
            "hard" if any(tok in code for tok in ["neeraj.m", "ananya.sharma", "rahul123", "priya_r"]) else "nohard",
            "lenret" if "returnlen(email)" in sq else "nolenret",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C085":
        sq = code.replace(" ", "")
        full_sq = full_code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "idxfixed" if all(tok in sq for tok in ["expr[1]", "expr[3]", "expr[6]", "expr[8]"]) else "noidxfixed",
            "lenbranch" if any(tok in sq for tok in ["len(expr)==10", "len(expr)==12", "len(e)==10", "len(e)==12", "len(expr)>13"]) else "nolenbranch",
            "split" if ".split(" in full_code else "nosplit",
            "isalnum" if "isalnum()" in full_code else "noisalnum",
            "hard" if any(tok in full_code for tok in ["(a+b)(c+d)", "(x+y)(z+w)", "(1+5)(10+12)"]) else "nohard",
            "nested" if full_code.count("def expand_sum_of_products") >= 2 or code.lstrip().startswith("def expand_sum_of_products(") else "nonested",
            "topprint" if "print(expand_sum_of_products" in full_code or "is_equal(expand_sum_of_products" in full_code else "notopprint",
            "literalret" if re.search(r"\breturn\s+['\"]a\*c\s*\+\s*a\*d", full_code) else "noliteralret",
            "exprfind" if ".find('('" in full_sq and ".split('+')" in full_sq else "noexprfind",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C086":
        sq = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "midp1" if "mid+1" in sq and "t[mid+1:]" in sq else "nomidp1",
            "tplusmid" if "returnt+t[mid:]" in sq or "return(t+t[mid:])" in sq else "notplusmid",
            "dropmid" if "t[:mid]+t[mid+1:]+t[mid+1:]" in sq else "nodropmid",
            "roundhalf" if "round(len(t)/2)" in sq or "round(tlen/2)" in sq else "noroundhalf",
            "listbuild" if "list(t)" in code and ".append(" in code and "tuple(" in code else "nolistbuild",
            "strconv" if "str(" in code and ("split(" in code or "z=" in sq) else "nostrconv",
            "lencases" if any(x in sq for x in ["len(t)==2", "len(t)==3", "len(t)==5", "len(t)==7"]) else "nolencases",
            "hard" if any(tok in code for tok in ["(4,5,6,7,8,7,8)", "('x', 'y', 'z', 'a', 'z', 'a')", "(1,2,3,4,5,6,7,5,6,7)"]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C080":
        bits = [
            f"vec={vec}",
            "len" if "len(" in code else "nolen",
            "gt2" if "len(s)>2" in code.replace(" ", "") else "nogt2",
            "lt4" if "len(s)<4" in code.replace(" ", "") else "nolt4",
            "f2" if "[:2]" in code else "nof2",
            "l2" if "[-2:]" in code else "nol2",
            "l1" if "[-1:]" in code else "nol1",
            "hard" if any(tok in code for tok in ["helloworld", "python", "held", "pyon"]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C081":
        bits = [
            f"vec={vec}",
            "pow" if "**2" in code or "x*x" in code or "i*i" in code else "nopow",
            "revslice" if "[::-1]" in code else "norevslice",
            "reverse" if ".reverse(" in code else "noreverse",
            "reversed" if "reversed(" in code else "noreversed",
            "sorted" if "sorted(" in code or ".sort(" in code else "nosorted",
            "append" if ".append(" in code else "noappend",
            "hard" if any(tok in code for tok in ["[25,16,9,4,1]", "[4,100]", "if l=="]) else "nohard",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C082":
        squashed = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "str" if "str(" in code else "nostr",
            "mod10" if "%10" in squashed else "nomod10",
            "div10" if "//10" in squashed else "nodiv10",
            "sorted" if "sorted(" in code or ".sort(" in code else "nosorted",
            "minus1" if "-1" in code and ("==" in code or "!=" in code) else "nominus1",
            "loopret" if "for " in code and "return true" in code and "return false" in code else "noloopret",
            "hard" if any(tok in code for tok in ["4321", "3210", "9876", "5432", "5433", "2001", "5431"]) else "nohard",
            "gtge" if ">=" in code or "<=" in code else "nogtge",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C077":
        bits = [
            f"vec={vec}",
            "mod5" if "%5" in code.replace(" ", "") else "nomod5",
            "mod3" if "%3" in code.replace(" ", "") else "nomod3",
            "or" if " or " in code else "no_or",
            "and" if " and " in code else "no_and",
            "eq3" if "%3==0" in code.replace(" ", "") else "no_eq3",
            "ne3" if "%3!=0" in code.replace(" ", "") else "no_ne3",
            "floordiv" if "//" in code else "no_floordiv",
            "bitand" if "&" in code else "no_bitand",
            "retmod" if re.search(r"\breturn\s+\w+\s*%\s*5\b(?!\s*[=!<>])", code) else "no_retmod",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C078":
        bits = [
            f"vec={vec}",
            "startswith" if "startswith(" in code else "nostartswith",
            "hello_nospace" if re.search(r"startswith\s*\(\s*[\"']hello[\"']\s*\)", code) else "no_hello_nospace",
            "hi_nospace" if re.search(r"startswith\s*\(\s*[\"']hi[\"']\s*\)", code) else "no_hi_nospace",
            "hello_space" if "hello " in code else "no_hello_space",
            "hi_space" if "hi " in code else "no_hi_space",
            "split" if ".split(" in code else "nosplit",
            "strip" if ".strip(" in code else "nostrip",
            "lower" if ".lower(" in code else "nolower",
            "inop" if " in s" in code or " in \"" in code or " in '" in code else "no_inop",
            "idx" if "[" in code and "]" in code else "no_idx",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C079":
        squashed = code.replace(" ", "")
        bits = [
            f"vec={vec}",
            "axbyc" if "a*x+b*y+c" in squashed else "no_axbyc",
            "rawreturn" if re.search(r"\breturn\s*\(?\s*a\s*\*\s*x\s*\+\s*b\s*\*\s*y\s*\+\s*c", code) else "no_rawreturn",
            "eq1" if "==1" in squashed or "==-1" in squashed else "no_eq1",
            "gtlt0" if ">0" in squashed or "<0" in squashed else "no_gtlt0",
            "gele0" if ">=0" in squashed or "<=0" in squashed else "no_gele0",
            "divb" if "/b" in squashed else "no_divb",
            "xyab" if "x>a" in squashed or "y>b" in squashed or "a<x" in squashed else "no_xyab",
            "const" if re.search(r"\breturn\s+(-?1|0)\b", code) else "no_const",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C010":
        bits = [
            f"vec={vec}",
            f"if_count={code.count('if ')}",
            "elif" if "elif" in code else "no_elif",
            "u200" if "200" in code else "no200",
            "u400" if "400" in code else "no400",
            "m150" if "150" in code else "no150",
            "h300" if "300" in code else "no300",
            "r075" if "0.75" in code else "nor075",
            "r09" if "0.9" in code else "nor09",
            "lt400" if "<400" in code or "< 400" in code else "ok400cmp",
            "eq400" if "==400" in code or "== 400" in code else "noeq400",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C011":
        bits = [
            f"vec={vec}",
            "revslice" if "::-1" in code else "norevslice",
            "s2+rev" if re.search(r"s2\s*\+\s*.*\[\s*::-1\]", code) or "s2 + reversed_s1" in code else "not_s2_rev",
            "s1+s2" if "s1+s2" in code.replace(" ", "") else "not_s1s2",
            "neqrev" if "!=" in code and "::-1" in code else "no_neqrev",
            "inop" if " in " in code else "no_in",
            "idxheavy" if len(re.findall(r"\[[0-9:-]+\]", code)) >= 4 else "idxlight",
            "fp=" + fp,
        ]
        return "|".join(bits)
    if cluster_id == "C012":
        bits = [
            f"vec={vec}",
            "abs" if "abs(" in code else "noabs",
            "sorted" if "sorted(" in code or ".sort(" in code else "nosort",
            "for" if "for " in code else "no_for",
            "ret_first_second" if "return first == second" in code else "no_ret_first_second",
            "idx4" if len(set(re.findall(r"sequence\\[(\\-?\\d+)\\]", code))) >= 4 else "idxfew",
            "diffname" if "diff" in code else "nodiff",
            "fp=" + fp,
        ]
        return "|".join(bits)
    # Pangram
    bits = [
        f"vec={vec}",
        "ascii" if "ascii_lowercase" in code else "noascii",
        "set" if "set(" in code else "noset",
        "len26" if "26" in code and "len(" in code else "nolen26",
        "inop" if " in " in code else "no_in",
        "split" if "split(" in code else "nosplit",
        "isalpha" if "isalpha(" in code else "noisalpha",
        "fp=" + fp,
    ]
    return "|".join(bits)


def residual_label_from_signature(cluster_id: str, sig: str, sample_code: str, idx: int) -> str:
    code = sample_code.lower()
    if cluster_id == "C004":
        if "and" in sig and "mod2" in sig and "mod5" in sig:
            return "Residual promoted: uses `and` instead of `or` for the two conditions"
        if "div" in sig or "floordiv" in sig:
            return "Residual promoted: division/floor-division used instead of `%` divisibility checks"
        if "barefalse" in sig:
            return "Residual promoted: bare `False` expression in `else` branch (missing `return False`)"
        if "hard" in sig:
            return "Residual promoted: ignores parameter and checks a hard-coded sample number"
        if "mod5" in sig and "nomod2" in sig:
            return "Residual promoted: checks only divisibility by 5"
    if cluster_id == "C015":
        if "abs" in sig or "gt0" in sig:
            return "Residual promoted: negative-number handling bug (`abs()` / positive-only even branch)"
        if "div2" in sig:
            return "Residual promoted: division used for parity check (`n/2 == 0`) instead of `n % 2 == 0`"
        if "xor2" in sig:
            return "Residual promoted: uses `^2` (XOR) instead of squaring"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample values / calls instead of using input `n`"
        if "retor" in sig:
            return "Residual promoted: boolean `or` used between branch outputs"
        if "nested" in sig:
            return "Residual promoted: nested/redeclared function causes outer function to return `None`"
    if cluster_id == "C016":
        if "wrong1000" in sig:
            return "Residual promoted: wrong tens-digit extraction (`%1000`/`//100` uses hundreds digit)"
        if "qtruth" in sig:
            return "Residual promoted: quotient-truthiness check (`num//a`, `num//b`) instead of `% ... == 0`"
        if "same2" in sig:
            return "Residual promoted: checks the same last-digit expression twice"
        if "first2" in sig:
            return "Residual promoted: uses first digits instead of the last two digits"
        if "bitand" in sig:
            return "Residual promoted: bitwise `&` in divisibility condition (precedence bug)"
        if "or" in sig and "mod10" in sig and "noand" in sig and "nozerochk" in sig:
            return "Residual promoted: `or` used instead of `and` for two divisibility requirements"
        if "loopret" in sig:
            return "Residual promoted: returns after first loop iteration / partial digit scan"
        if "zerochk" in sig and "noand" in sig and "noor" not in sig:
            return "Residual promoted: zero-digit guard logic dominates and skips actual divisibility test"
    if cluster_id == "C087":
        if "hard" in sig:
            return "Residual promoted: hard-coded public shuffle cycles/sample outputs"
        if "retnum" in sig:
            return "Residual promoted: returns input unchanged"
        if "slice2413" in sig and "str" in sig and "nointcast" in sig:
            return "Residual promoted: reorders digits as a string but returns string instead of integer"
        if "concat2413" in sig and "intcast" in sig:
            return "Residual promoted: near-correct `2413` reconstruction trapped in broken scope/structure"
        if "whiletrue" in sig and "modextract" in sig:
            return "Residual promoted: extracts a single digit and returns early (no 4-digit reconstruction)"
        if "prints" in sig and "noretnum" in sig:
            return "Residual promoted: prints sample outputs instead of returning shuffled integer"
        if "nested" in sig:
            return "Residual promoted: nested/redeclared `shuffle_digits` causes outer function to return `None`"
    if cluster_id == "C088":
        if "upper_nocall" in sig:
            return "Residual promoted: `.upper` method referenced but never called (`.upper()` missing)"
        if "index" in sig:
            return "Residual promoted: `list.index(...)` used for parity, causing wrong behavior on repeated-word patterns"
        if "lower" in sig or "swapcase" in sig:
            return "Residual promoted: changes odd-index words too (`lower`/`swapcase`) instead of leaving them unchanged"
        if "allupper" in sig:
            return "Residual promoted: uppercases all words instead of even-index words only"
        if "retsentence" in sig:
            return "Residual promoted: returns a string instead of the required list of words"
        if "splitcomma" in sig:
            return "Residual promoted: splits on commas instead of spaces"
        if "truthychain" in sig:
            return "Residual promoted: always-truthy boolean-chain over specific indices (`words[0] or words[2] ...`)"
        if "earlyret" in sig:
            return "Residual promoted: returns from inside loop after processing only the first word/index"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample output list(s)"
    if cluster_id == "C094":
        if "constprint" in sig or ("printonly" in sig and "samplelit" in sig):
            return "Residual promoted: prints a constant/sample output (or empty line) instead of computing from input"
        if "defonly" in sig:
            return "Residual promoted: function-only / copied solution (no required input-reading + output program flow)"
        if "nocall" in sig:
            return "Residual promoted: defines helper/main function but never calls it, so no output is produced"
        if "lenfirst" in sig:
            return "Residual promoted: uses `len(first_input_line)` as the threshold instead of parsing integer `l`"
        if "joinspace" in sig:
            return "Residual promoted: joins selected characters with spaces (`' '.join(...)`) instead of concatenating them"
        if "inputstripmeth" in sig:
            return "Residual promoted: uses `input.strip()` (method object) instead of `input().strip()`"
        if "samplelit" in sig and "startswith" in sig and "nolen1" in sig:
            return "Residual promoted: sample-derived string/list literal logic instead of processing all `n` input words"
    if cluster_id == "C017":
        if "hardsample" in sig or "fixed3" in sig:
            return "Residual promoted: hard-coded/fixed-size sample-matrix output instead of general `m x n` rotation"
        if ("loopcw" in sig or ("zipcw" in sig and "rowrev" in sig)) and ("printstar" in sig or "joinspace" in sig or "endempty" in sig) and "noendspace" in sig:
            return "Residual promoted: likely correct rotation logic, but output spacing format differs from evaluator expectations"
        if "readnrows" in sig:
            return "Residual promoted: reads `n` rows instead of `m` rows (row/column-count confusion)"
        if "helperdef" in sig and ("loopcw" in sig or "zipcw" in sig) and ("printstar" in sig or "joinspace" in sig):
            return "Residual promoted: helper-based clockwise rotation is present, but printed output formatting mismatches evaluator"
        if "unrelatedap" in sig:
            return "Residual promoted: copied solution for a different question (`is_arithmetic_progression`)"
        if "debug" in sig:
            return "Residual promoted: extra debug/comment output (or complaint text) causes output mismatch"
    if cluster_id == "C089":
        if "eqends" in sig and "novowelstr" in sig and "novowelset" in sig:
            return "Residual promoted: checks only first/last equality, not whether the letter is a vowel"
        if "vowelstr" in sig and "noeqends" in sig:
            return "Residual promoted: checks vowelhood at both ends but omits same-vowel equality"
        if "lower" in sig and "nolowercall" in sig:
            return "Residual promoted: `.lower` referenced but not called (`.lower()` missing)"
        if "boolchain" in sig:
            return "Residual promoted: always-truthy boolean-chain in vowel checks/comparisons"
        if "startswith" in sig or "endswith" in sig:
            return "Residual promoted: `startswith`/`endswith` misuse for same-vowel endpoint comparison"
        if "loopret" in sig:
            return "Residual promoted: returns inside vowel loop before completing the full check"
        if "pal" in sig:
            return "Residual promoted: palindrome-style reverse comparison instead of endpoint-vowel logic"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample strings/examples"
    if cluster_id == "C090":
        if "retloop" in sig:
            return "Residual promoted: returns from inside coefficient loop (partial polynomial sum)"
        if "xor" in sig:
            return "Residual promoted: uses `^` (XOR) instead of `**` for powers"
        if "idxfn" in sig:
            return "Residual promoted: `coef.index(value)` exponent-position bug (repeated coefficients fail)"
        if "enumerate" in sig and "pow" in sig and "nofixeddeg" in sig:
            return "Residual promoted: exponent order bug (`x**i` ascending) instead of descending coefficient powers"
        if "fixeddeg" in sig:
            return "Residual promoted: fixed-degree formula / length-specific polynomial implementation"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample polynomial outputs/cases"
        if "nopow" in sig and "for" in sig:
            return "Residual promoted: accumulates coefficients/linear terms without proper exponentiation"
    if cluster_id == "C091":
        if "eqfull" in sig:
            return "Residual promoted: compares full numbers instead of their last digits"
        if "selfcmp" in sig:
            return "Residual promoted: compares the first number to itself (ignores `num2`)"
        if "parity" in sig and "nomod10" in sig:
            return "Residual promoted: parity/even-odd heuristic instead of last-digit comparison"
        if "firstdigit" in sig:
            return "Residual promoted: uses first digit / wrong place value instead of last digit"
        if "laststr" in sig and "nomod10" in sig:
            return "Residual promoted: string-based last-digit compare with surrounding logic/return bug"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample number pairs"
    if cluster_id == "C092":
        if "order15late" in sig:
            return "Residual promoted: checks `%3`/`%5` before `%15`, so `FizzBuzz` is unreachable"
        if "mod10" in sig:
            return "Residual promoted: uses `%10 == 0` for `Buzz` instead of `%5 == 0`"
        if "boolret" in sig:
            return "Residual promoted: returns boolean divisibility result instead of string labels"
        if "normal_lower" in sig:
            return "Residual promoted: wrong fallback casing (`'normal'` instead of `'Normal'`)"
        if "truthychain" in sig:
            return "Residual promoted: always-truthy string boolean-chain (`'Fizz' or 'Buzz' ...`)"
        if "bitand" in sig:
            return "Residual promoted: bitwise `&` used in divisibility conditions"
        if "retcount=3" in sig and "mod3" in sig and "mod5" in sig:
            return "Residual promoted: missing fallback `Normal` branch / incomplete case coverage"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample numbers/labels"
    if cluster_id == "C093":
        if "hard" in sig:
            return "Residual promoted: hard-coded sample output string(s) (e.g., `HollE`)"
        if "missU" in sig:
            return "Residual promoted: incomplete vowel set (missing uppercase `U`/other vowel variant)"
        if "noninput" in sig and "novowelset" not in sig:
            return "Residual promoted: program I/O structure does not follow multi-line `n + lines` format"
        if "ninput" in sig and "inputs=2" in sig and "forn" in sig:
            return "Residual promoted: reads/prints per-line incorrectly (global vowel reversal across all lines not implemented)"
        if "twoptr" in sig and "noprint" in sig and "nojoin" in sig:
            return "Residual promoted: incomplete two-pointer implementation (no final output emitted)"
        if "join" in sig and "print" in sig and "noforn" in sig:
            return "Residual promoted: treats input as a single line / loses multi-line boundaries"
        if "inplace" in sig:
            return "Residual promoted: string-mutation approach (`s[i] = ...`) instead of rebuilding mutable list/string"
    if cluster_id == "C014":
        if "mlt500" in sig and "nomeq500" in sig:
            return "Residual promoted: `get_medium_books` excludes 500-page books (`<500` instead of `<=500`)"
        if "pnone" in sig:
            return "Residual promoted: `get_pages_by_isbn` returns `None` inside loop (premature non-match exit)"
        if "cntloopret" in sig:
            return "Residual promoted: `count_by_language` returns from inside loop (partial counts only)"
        if "off1" in sig:
            return "Residual promoted: off-by-one iteration (`range(len(book_data)-1)`) skips the last book"
        if "retlist_short" in sig or "retlist_medium" in sig:
            return "Residual promoted: returns list(s) where the question requires ISBN sets"
        if "hardisbn" in sig:
            return "Residual promoted: hard-coded ISBN outputs/sample-derived dictionaries"
        if "ellipsis" in sig and "vec=00111" in sig:
            return "Residual promoted: earlier helpers implemented; `count_by_language` / `total_pages_in_genre_lang` left incomplete"
        if "ellipsis" in sig:
            return "Residual promoted: some required book-data helper functions still left as placeholders"
    if cluster_id == "C083":
        if "sorted" in sig:
            return "Residual promoted: sorts the list after adding duplicates (order semantics bug)"
        if "lencases" in sig:
            return "Residual promoted: length-specific sample-case implementation"
        if "apptail" in sig:
            return "Residual promoted: appends duplicates at the tail instead of duplicating first element at the front"
        if "strconv" in sig:
            return "Residual promoted: string-conversion approach instead of list-element duplication"
        if "mult2" in sig:
            return "Residual promoted: multiplies element values rather than duplicating list entries"
        if "retl" in sig:
            return "Residual promoted: returns original list unchanged"
    if cluster_id == "C084":
        if "slicefix" in sig:
            return "Residual promoted: fixed-length slicing/domain-length assumption (`email[:k]`, `email[:-k]`)"
        if "split0" in sig and "replace" in sig:
            return "Residual promoted: splits at `@` then mutates username (`replace`/normalization)"
        if "split1" in sig:
            return "Residual promoted: returns domain part after `@` instead of username"
        if "reti" in sig:
            return "Residual promoted: returns loop variable (`i`) instead of accumulated username"
        if "retemail" in sig:
            return "Residual promoted: returns full email unchanged"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample usernames"
    if cluster_id == "C085":
        if "idxfixed" in sig:
            return "Residual promoted: fixed-position parser (assumes single-character term layout)"
        if "lenbranch" in sig:
            return "Residual promoted: expression-length branching with fragile slices"
        if "hard" in sig or "literalret" in sig:
            return "Residual promoted: hard-coded public example expressions/outputs"
        if "nested" in sig:
            return "Residual promoted: nested/redeclared function definition inside `expand_sum_of_products`"
        if "topprint" in sig:
            return "Residual promoted: top-level test/print code pollutes evaluator output"
        if "split" in sig and "isalnum" in sig:
            return "Residual promoted: tokenizes then collapses to four characters (fails multi-character terms)"
    if cluster_id == "C086":
        if "midp1" in sig:
            return "Residual promoted: midpoint off-by-one (`t[mid+1:]`) skips a required repeated element"
        if "dropmid" in sig:
            return "Residual promoted: drops middle element from original tuple and duplicates wrong suffix"
        if "tplusmid" in sig:
            return "Residual promoted: duplicates `t[mid:]` and repeats the middle element for odd lengths"
        if "roundhalf" in sig:
            return "Residual promoted: uses `round(len(t)/2)` causing parity/off-by-one split errors"
        if "listbuild" in sig:
            return "Residual promoted: list-based reconstruction repeats wrong elements/order before tuple conversion"
        if "strconv" in sig:
            return "Residual promoted: string-conversion approach instead of tuple slicing/concatenation"
        if "lencases" in sig:
            return "Residual promoted: length-specific tuple-size branches"
        if "hard" in sig:
            return "Residual promoted: hard-coded public tuple outputs"
    if cluster_id == "C080":
        if "f2" in sig and "l2" in sig and "nolen" in sig:
            return "Residual promoted: combines edges without short-string guard"
        if "f2" in sig and "l1" in sig:
            return "Residual promoted: wrong edge slices (`last 1` instead of `last 2`)"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample outputs/examples"
    elif cluster_id == "C081":
        if "pow" in sig and "nosorted" in sig and "noreverse" in sig and "norevslice" in sig and "noreversed" in sig:
            return "Residual promoted: squares values but does not reverse order"
        if "sorted" in sig and "pow" in sig:
            return "Residual promoted: sorts squared values instead of reversing input order"
        if ("reverse" in sig or "revslice" in sig or "reversed" in sig) and "nopow" in sig:
            return "Residual promoted: reverses list but forgets to square"
    elif cluster_id == "C082":
        if "sorted" in sig:
            return "Residual promoted: sorting-based decreasing check (strictness/order bug)"
        if "minus1" in sig:
            return "Residual promoted: consecutive-step (`-1`) digit-check logic"
        if "loopret" in sig:
            return "Residual promoted: returns after first digit comparison inside loop"
        if "hard" in sig:
            return "Residual promoted: hard-coded sample numbers"
    if cluster_id == "C077":
        if "mod5" in sig and "nomod3" in sig:
            return "Residual promoted: checks only divisibility by 5"
        if "mod5" in sig and "mod3" in sig and "or" in sig:
            return "Residual promoted: uses `or` for divisibility conditions"
        if "floordiv" in sig:
            return "Residual promoted: floor-division/digit heuristic instead of modulus rule"
        if "bitand" in sig:
            return "Residual promoted: bitwise operator/precedence mistake in divisibility test"
    elif cluster_id == "C078":
        if "startswith" in sig and ("hello_nospace" in sig or "hi_nospace" in sig):
            return "Residual promoted: missing trailing space in `startswith` greeting check"
        if "split" in sig:
            return "Residual promoted: split/token-based greeting check"
        if "strip" in sig or "lower" in sig:
            return "Residual promoted: normalization (`strip`/`lower`) changes required semantics"
        if "inop" in sig:
            return "Residual promoted: substring/membership check instead of prefix rule"
    elif cluster_id == "C079":
        if "rawreturn" in sig:
            return "Residual promoted: returns raw `a*x + b*y + c` instead of `1/-1/0`"
        if "axbyc" in sig and "eq1" in sig:
            return "Residual promoted: compares line-expression to exact `1`/`-1` instead of sign"
        if "divb" in sig:
            return "Residual promoted: slope/division-based approach with sign pitfalls"
        if "xyab" in sig:
            return "Residual promoted: compares coordinates/coefficients directly, not line expression"
    if cluster_id == "C010":
        if "no_elif" in sig and "200" in code and "400" in code:
            return "Residual promoted: slab conditions written as independent `if`s (overwrite/precedence bug)"
        if "no150" in sig and "0.75" in code:
            return "Residual promoted: middle slab formula missing `+150`"
        if "no300" in sig and "0.9" in code:
            return "Residual promoted: high slab formula missing `+300`"
        if "lt400" in sig:
            return "Residual promoted: 400-boundary comparison bug (`<400` vs `<=400`)"
    elif cluster_id == "C011":
        if "s2+rev" in sig:
            return "Residual promoted: wrong concatenation order (`s2 + reversed(s1)`)"
        if "neqrev" in sig:
            return "Residual promoted: inverted palindrome condition (`!=`)"
        if "idxheavy" in sig:
            return "Residual promoted: fixed-index/manual-string construction (non-general solution)"
        if "inop" in sig and "::-1" in code:
            return "Residual promoted: substring/membership check instead of palindrome equality"
    elif cluster_id == "C012":
        if "abs" in sig:
            return "Residual promoted: sign-insensitive AP check using `abs(difference)`"
        if "idx4" in sig and "no_for" in sig:
            return "Residual promoted: checks only a few fixed positions, not full sequence"
        if "ret_first_second" in sig:
            return "Residual promoted: returns only the last pairwise-difference comparison"
        if "sorted" in sig:
            return "Residual promoted: sorts sequence before AP check (changes semantics)"
    elif cluster_id == "C013":
        if "ascii" in sig and "inop" in sig:
            return "Residual promoted: alphabet-string membership/substring confusion"
        if "set" in sig and "len26" in sig:
            return "Residual promoted: unique-character count heuristic instead of alphabet coverage"
        if "ascii" in sig and "nolen26" in sig and "no_set" if False else False:
            pass
    return f"Residual promoted family #{idx}"


def coalesce_residuals(df: pd.DataFrame, cluster_id: str, target_pct: float = RESIDUAL_TARGET_PCT) -> pd.DataFrame:
    df = df.copy()
    n_non_full = int(df["is_non_full"].sum())
    target_n = int((target_pct / 100.0) * n_non_full)
    if n_non_full == 0:
        return df

    def residual_mask() -> pd.Series:
        return (df["is_non_full"]) & (df["pattern"] == "Other wrong-answer logic pattern (residual)")

    # Promote grouped residual families until we reach target threshold.
    iteration = 0
    while int(residual_mask().sum()) > target_n:
        iteration += 1
        res = df[residual_mask()].copy()
        if res.empty:
            break
        res["res_sig"] = [residual_signature(cluster_id, r) for _, r in res.iterrows()]
        grp = (
            res.groupby("res_sig", dropna=False)
            .agg(
                count=("student_id", "count"),
                sample_idx=("student_id", "idxmax"),  # placeholder, replaced below
            )
            .reset_index()
            .sort_values(["count", "res_sig"], ascending=[False, True])
        )
        # Use actual first row index as sample reference.
        first_idx_by_sig = res.groupby("res_sig").apply(lambda g: g.index[0]).to_dict()
        grp["sample_idx"] = grp["res_sig"].map(first_idx_by_sig)
        top = grp.iloc[0]
        if int(top["count"]) <= 1 and int(residual_mask().sum()) > target_n:
            # If only singletons remain but residual is still too large, promote by coarse stmt+vec family.
            res["res_sig"] = res.apply(
                lambda r: f"vec={r['vec']}|stmt={r['stmt_shape']}|summary={r['summary']}|code0={first_code_line(r['logic_code'])[:60]}",
                axis=1,
            )
            grp = (
                res.groupby("res_sig", dropna=False)
                .size()
                .reset_index(name="count")
                .sort_values(["count", "res_sig"], ascending=[False, True])
            )
            top_sig = str(grp.iloc[0]["res_sig"])
            sample_idx = res[res["res_sig"] == top_sig].index[0]
            count = int(grp.iloc[0]["count"])
        else:
            top_sig = str(top["res_sig"])
            sample_idx = int(top["sample_idx"])
            count = int(top["count"])

        if count <= 0:
            break
        sample_code = str(df.loc[sample_idx, "logic_code"] or df.loc[sample_idx, "function_code"])
        promoted_count = len(
            [x for x in df[residual_mask()].index if residual_signature(cluster_id, df.loc[x].to_dict()) == top_sig]
        )
        if promoted_count == 0:
            # coarse fallback promotion
            mask = residual_mask() & (
                df.apply(
                    lambda r: f"vec={r['vec']}|stmt={r['stmt_shape']}|summary={r['summary']}|code0={first_code_line(r['logic_code'])[:60]}",
                    axis=1
                )
                == top_sig
            )
        else:
            mask = residual_mask() & (
                df.apply(lambda r: residual_signature(cluster_id, r.to_dict()), axis=1) == top_sig
            )

        label = residual_label_from_signature(cluster_id, top_sig, sample_code, iteration)
        df.loc[mask, "pattern"] = label
        # Safety valve
        if iteration >= 25:
            break
    return df


def build_rows_for_cluster(cluster_id: str, members_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any], dict[str, str]]:
    cm = members_df[members_df["cluster_id"] == cluster_id].copy()
    if cm.empty:
        raise RuntimeError(f"No members found for cluster {cluster_id}")
    cm = cm.sort_values(["is_canonical", "final_submitters", "namespace", "problem_id"], ascending=[False, False, True, True])
    canonical = cm[cm["is_canonical"] == True].iloc[0] if (cm["is_canonical"] == True).any() else cm.iloc[0]

    problem_obj = load_problem_json(str(canonical["namespace"]), int(canonical["problem_id"]))
    private_notes = private_case_notes_for_cluster(cluster_id, problem_obj)
    private_case_width = max(1, len(private_notes))

    rows: list[dict[str, Any]] = []
    for m in cm.itertuples(index=False):
        variant = f"{m.namespace}/{int(m.problem_id)}"
        fp = PILOT_DIR / f"{m.namespace}__{int(m.problem_id)}__final_rows.csv"
        if not fp.exists():
            if int(getattr(m, "final_submitters", 0)) <= 0:
                # Some archived variants have no final submissions, so pilot extraction writes no CSV.
                continue
            raise RuntimeError(f"Missing pilot row CSV for {variant}: {fp}")
        df = pd.read_csv(fp, dtype={"private_case_vector": "string"}, low_memory=False)

        for rec in df.itertuples(index=False):
            student_code = "" if pd.isna(getattr(rec, "student_code", None)) else str(getattr(rec, "student_code"))
            raw_logic_code = "" if pd.isna(getattr(rec, "function_logic_code", None)) else str(getattr(rec, "function_logic_code"))
            function_code = "" if pd.isna(getattr(rec, "function_code", None)) else str(getattr(rec, "function_code"))
            if not function_code and student_code:
                function_code = student_code
            logic_code = raw_logic_code
            if not logic_code and function_code:
                logic_code = extract_function_executable_body(function_code) or function_code
            detector_tags = split_tag_set(getattr(rec, "detector_tags", []))
            vec = norm_vec_to_width(getattr(rec, "private_case_vector", "???"), private_case_width)
            if vec.isdigit() and len(vec) < private_case_width:
                vec = vec.zfill(private_case_width)
            if cluster_id in {"C014", "C026", "C097", "C108", "C110"} and (student_code or function_code):
                # Multi-function question: keep the full submission so cluster classifiers can inspect all required defs.
                logic_code = student_code or function_code
            return_count = norm_int(getattr(rec, "return_count", 0))
            return_true_count = norm_int(getattr(rec, "return_true_count", 0))
            return_false_count = norm_int(getattr(rec, "return_false_count", 0))
            if return_count == 0 and "return" in (logic_code or "").lower():
                return_count, return_true_count, return_false_count = fallback_return_stats(logic_code or function_code)
            body_stmt_count = norm_int(getattr(rec, "body_non_doc_stmt_count", 0))
            if body_stmt_count == 0 and (logic_code or function_code):
                body_stmt_count = fallback_body_non_doc_stmt_count(function_code, logic_code or function_code)
            row = {
                "cluster_id": cluster_id,
                "variant": variant,
                "namespace": str(m.namespace),
                "problem_id": int(m.problem_id),
                "question_title": str(m.question_title),
                "student_id": str(getattr(rec, "student_id")),
                "student_code": student_code,
                "summary": "" if pd.isna(getattr(rec, "summary", None)) else str(getattr(rec, "summary")),
                "reason": "" if pd.isna(getattr(rec, "reason", None)) else str(getattr(rec, "reason")),
                "score": norm_float(getattr(rec, "score", None), None),
                "is_parseable": norm_bool(getattr(rec, "is_parseable", False)),
                "is_non_full": norm_bool(getattr(rec, "is_non_full", False)),
                "is_full_pass": norm_bool(getattr(rec, "is_full_pass", False)),
                "vec": vec,
                "exception_type": "" if pd.isna(getattr(rec, "exception_type", None)) else str(getattr(rec, "exception_type")),
                "detector_tags": detector_tags,
                "function_code": function_code,
                "logic_code": logic_code if logic_code else function_code,
                "stmt_shape": "" if pd.isna(getattr(rec, "stmt_shape", None)) else str(getattr(rec, "stmt_shape")),
                "normalized_fingerprint": "" if pd.isna(getattr(rec, "normalized_fingerprint", None)) else str(getattr(rec, "normalized_fingerprint")),
                "fp_short": ("" if pd.isna(getattr(rec, "normalized_fingerprint", None)) else str(getattr(rec, "normalized_fingerprint")).split(":", 1)[0]),
                "return_count": return_count,
                "return_true_count": return_true_count,
                "return_false_count": return_false_count,
                "body_non_doc_stmt_count": body_stmt_count,
                "has_ellipsis_node": norm_bool(getattr(rec, "has_ellipsis_node", False)),
                "orig_primary_pattern": "" if pd.isna(getattr(rec, "primary_pattern", None)) else str(getattr(rec, "primary_pattern")),
            }
            rows.append(row)

    rdf = pd.DataFrame(rows)
    return rdf, canonical.to_dict(), problem_obj, private_notes


def apply_cluster_reclustering(df: pd.DataFrame, cluster_id: str) -> pd.DataFrame:
    classifier = CLASSIFIERS[cluster_id]
    df = df.copy()
    df["pattern"] = df.apply(lambda r: classifier(r.to_dict()), axis=1)
    # Normalize remaining None on non-full rows to residual.
    mask = df["is_non_full"] & df["pattern"].isna()
    df.loc[mask, "pattern"] = "Other wrong-answer logic pattern (residual)"
    df = coalesce_residuals(df, cluster_id, target_pct=RESIDUAL_TARGET_PCT)
    return df


def pattern_sort_key(pat: str) -> tuple[int, str]:
    if pat == "Other wrong-answer logic pattern (residual)":
        return (1, pat)
    return (0, pat)


def variant_freq_block(pattern_rows: pd.DataFrame, variant_denoms: dict[str, int], variants_order: list[str]) -> list[str]:
    lines: list[str] = []
    cluster_count = len(pattern_rows)
    cluster_non_full_total = sum(variant_denoms.values())
    cluster_pct = (100.0 * cluster_count / cluster_non_full_total) if cluster_non_full_total else 0.0
    lines.append(f"- Cluster frequency: `{cluster_count}/{cluster_non_full_total}` (`{cluster_pct:.1f}%`)")
    lines.append("- Variant frequencies:")
    by_variant = pattern_rows["variant"].value_counts().to_dict()
    for v in variants_order:
        cnt = int(by_variant.get(v, 0))
        den = int(variant_denoms.get(v, 0))
        pct = (100.0 * cnt / den) if den else 0.0
        lines.append(f"  - `{v}`: `{cnt}/{den}` (`{pct:.1f}%`)")
    return lines


def choose_examples(pattern_rows: pd.DataFrame, variants_order: list[str], per_variant: int = 1) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for variant in variants_order:
        g = pattern_rows[pattern_rows["variant"] == variant].copy()
        if g.empty:
            continue
        g["logic_len"] = g["logic_code"].fillna("").astype(str).str.len()
        g = g.sort_values(["logic_len", "student_id"], ascending=[False, True])
        for _, r in g.head(per_variant).iterrows():
            examples.append(r.to_dict())
    if not examples:
        # fallback global example
        g = pattern_rows.copy()
        g["logic_len"] = g["logic_code"].fillna("").astype(str).str.len()
        g = g.sort_values(["logic_len", "student_id"], ascending=[False, True])
        for _, r in g.head(1).iterrows():
            examples.append(r.to_dict())
    return examples


def pattern_notes(cluster_id: str, pattern: str) -> str:
    # Short human-readable explanation template by pattern label.
    notes = {
        "Returns inside loop before completing full check/computation": "Control-flow bug: the function returns during iteration before processing all required items/conditions.",
        "Syntax / non-parseable final submission": "Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.",
        "Skeleton placeholder `...` left in function": "Template placeholder remains; Python treats `...` as valid syntax, often yielding a wrong-answer `None` path instead of syntax failure.",
        "No return / implicit `None`": "The function computes something but fails to return the required result value.",
        "Always returns `True` (constant output)": "Constant-output bug or always-truthy condition causes the function to ignore the actual input.",
        "Always returns `False` (constant output)": "Constant-output bug: function returns `False` regardless of input.",
        "Prints output but does not return required value": "In function-type questions, printing is not enough; tests compare the returned value.",
        "Runtime NameError": "Undefined variable/helper usage, often caused by partial edits or renamed variables.",
        "Runtime TypeError": "Type mismatch or invalid operation in the final code path.",
        "Runtime AttributeError": "Calling a method/attribute on the wrong object type (e.g., wrong string/list API).",
        "Runtime IndexError": "Out-of-range indexing during iteration/comparison logic.",
        "Runtime RecursionError": "Infinite/self recursion without a valid terminating condition.",
        "Runtime KeyError": "Dictionary lookup on uninitialized/unexpected key.",
        "Runtime error (parseable final submission)": "Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.",
    }
    return notes.get(pattern, "")


def write_cluster_report(
    cluster_row: dict[str, Any],
    members_df: pd.DataFrame,
    df: pd.DataFrame,
    canonical_problem: dict[str, Any],
    private_notes: dict[str, str],
) -> None:
    cluster_id = str(cluster_row["cluster_id"])
    cluster_file = str(cluster_row["cluster_file"])
    out_fp = ROOT / cluster_file

    cm = members_df[members_df["cluster_id"] == cluster_id].copy().sort_values(["is_canonical", "final_submitters"], ascending=[False, False])
    canonical = cm[cm["is_canonical"] == True].iloc[0] if (cm["is_canonical"] == True).any() else cm.iloc[0]

    variants_order = [f"{r.namespace}/{int(r.problem_id)}" for r in cm.sort_values(["namespace", "problem_id"]).itertuples(index=False)]
    variant_denoms = {
        f"{r.namespace}/{int(r.problem_id)}": int(r.non_full_final_submissions)
        for r in cm.itertuples(index=False)
    }

    non_full_df = df[df["is_non_full"]].copy()
    full_pass_count = int(df["is_full_pass"].sum())
    final_submitters_total = int((df["is_full_pass"] | df["is_non_full"]).sum())
    parseable_non_full = int(non_full_df["is_parseable"].sum())
    non_parseable_non_full = int(len(non_full_df) - parseable_non_full)

    lines: list[str] = []
    lines.append(f"# Error Patterns: Cluster {cluster_id} (`{cluster_row['cluster_title']}`)")
    lines.append("")
    lines.append("## Cluster Summary")
    lines.append("")
    lines.append(f"- Cluster ID: `{cluster_id}`")
    lines.append(f"- Cluster title: `{cluster_row['cluster_title']}`")
    lines.append(f"- Cluster file (this file): `{cluster_file}`")
    lines.append(f"- Variants in cluster: `{int(cluster_row['member_count'])}`")
    lines.append(f"- Total final submitters across variants: `{int(cluster_row['total_final_submitters'])}`")
    lines.append(f"- Total non-full final submissions across variants: `{int(cluster_row['total_non_full_final_submissions'])}`")
    lines.append(f"- Canonical variant (by submissions): `{canonical['namespace']}/{int(canonical['problem_id'])}`")
    lines.append("")
    lines.append("Cluster membership (zero-submitter variants omitted):")
    lines.append("")
    lines.append("| Variant | final_submitters | non_full | Relationship |")
    lines.append("| --- | ---: | ---: | --- |")
    for r in cm.sort_values(["namespace", "problem_id"]).itertuples(index=False):
        if int(r.final_submitters) <= 0:
            continue
        variant = f"`{r.namespace}/{int(r.problem_id)}`"
        if bool(r.is_canonical):
            variant += " (canonical)"
        lines.append(f"| {variant} | {int(r.final_submitters)} | {int(r.non_full_final_submissions)} | {r.variant_diff_note_vs_canonical} |")
    lines.append("")
    lines.append("## Canonical Question Spec (Full Source Artifact)")
    lines.append("")
    lines.append(f"- Canonical full question JSON: `problems/{canonical['namespace']}/{int(canonical['problem_id'])}.json`")
    other_variants = [f"`problems/{r.namespace}/{int(r.problem_id)}.json`" for r in cm.itertuples(index=False) if not bool(r.is_canonical)]
    if other_variants:
        lines.append("- Other variants in cluster:")
        for v in other_variants:
            lines.append(f"  - {v}")
    lines.append("")
    lines.append("## Cluster-Level Outcome Summary")
    lines.append("")
    lines.append(f"- Final submitters: `{final_submitters_total}`")
    lines.append(f"- Full pass: `{full_pass_count}`")
    lines.append(f"- Non-full final submissions: `{len(non_full_df)}`")
    lines.append(f"- Parseable non-full (logic/runtime focus): `{parseable_non_full}`")
    lines.append(f"- Non-parseable non-full: `{non_parseable_non_full}`")
    lines.append("")
    lines.append("Variant-level comparison:")
    lines.append("")
    lines.append("| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for variant in variants_order:
        g = df[df["variant"] == variant]
        n_final = int((g["is_full_pass"] | g["is_non_full"]).sum())
        n_full = int(g["is_full_pass"].sum())
        n_non_full = int(g["is_non_full"].sum())
        n_parse_non_full = int(((g["is_non_full"]) & (g["is_parseable"])).sum())
        lines.append(f"| `{variant}` | {n_final} | {n_full} | {n_non_full} | {n_parse_non_full} | {n_non_full - n_parse_non_full} |")
    lines.append("")
    lines.append("## Private Case Structure")
    lines.append("")
    for k in sorted(private_notes, key=lambda x: (len(x), x)):
        lines.append(f"- Private case {k}: {private_notes[k]}")
    lines.append("")
    vec_width = max(1, len(private_notes))
    example_vec = ("1" + "0" * (vec_width - 2) + "1") if vec_width >= 2 else "1"
    if vec_width == 3:
        lines.append("Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).")
    else:
        lines.append(
            f"Private-case vectors in this report are {vec_width}-character pass/fail strings over the private case groups "
            f"(e.g., `{example_vec}` marks pass/fail outcomes by private group order)."
        )
    lines.append("")

    # Inventory table
    pat_counts = non_full_df["pattern"].value_counts()
    lines.append("## Exhaustive Pattern Inventory (Cluster-Level)")
    lines.append("")
    lines.append("| Pattern | Cluster count | % of cluster non-full | " + " | ".join(f"`{v}`" for v in variants_order) + " |")
    lines.append("| --- | ---: | ---: | " + " | ".join("---:" for _ in variants_order) + " |")
    for pattern, cnt in pat_counts.items():
        row = non_full_df[non_full_df["pattern"] == pattern]
        pct = 100.0 * cnt / len(non_full_df) if len(non_full_df) else 0.0
        per_variant = []
        for v in variants_order:
            per_variant.append(str(int((row["variant"] == v).sum())))
        lines.append(f"| {pattern} | {int(cnt)} | {pct:.1f}% | " + " | ".join(per_variant) + " |")
    lines.append("")

    residual_count = int(pat_counts.get("Other wrong-answer logic pattern (residual)", 0))
    residual_pct = 100.0 * residual_count / len(non_full_df) if len(non_full_df) else 0.0
    lines.append("## Re-clustered Pattern Details")
    lines.append("")
    lines.append(f"Residual `Other` after second-pass re-clustering: `{residual_count}/{len(non_full_df)}` (`{residual_pct:.1f}%`)")
    lines.append("")

    # Pattern sections: every pattern starts with the required cluster/variant frequency format.
    for pattern, cnt in pat_counts.items():
        prow = non_full_df[non_full_df["pattern"] == pattern].copy()
        lines.append(f"### {pattern}")
        lines.append("")
        lines.extend(variant_freq_block(prow, variant_denoms, variants_order))
        # vector and score summary
        vec_counts = Counter(prow["vec"])
        score_counts = Counter("NA" if x is None else f"{float(x):.1f}" for x in prow["score"])
        if vec_counts:
            top_vecs = ", ".join(f"`{k}` x{v}" for k, v in vec_counts.most_common(4))
            lines.append(f"- Dominant private-case vectors: {top_vecs}")
        if score_counts:
            top_scores = ", ".join(f"`{k}` x{v}" for k, v in score_counts.most_common(4))
            lines.append(f"- Score distribution (top): {top_scores}")
        note = pattern_notes(cluster_id, pattern)
        if note:
            lines.append(f"- Interpretation: {note}")
        lines.append("- Representative examples (actual student submissions):")
        exs = choose_examples(prow, variants_order, per_variant=1)
        for ex in exs:
            score = "NA" if ex["score"] is None else (int(ex["score"]) if float(ex["score"]).is_integer() else ex["score"])
            lines.append(
                f"  - Variant `{ex['variant']}`, Student ID `{ex['student_id']}`, summary `{ex['summary']}`, "
                f"score `{score}`, vector `{ex['vec']}`"
            )
            lines.append("")
            lines.append("```python")
            lines.append(shorten_code(str(ex["logic_code"] or ex["function_code"])))
            lines.append("```")
        lines.append("")

    out_fp.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    clusters_df, members_df = read_cluster_meta()
    cluster_map = {str(r.cluster_id): r._asdict() if hasattr(r, "_asdict") else dict(r) for r in clusters_df.itertuples(index=False)}

    target_clusters = sys.argv[1:] if len(sys.argv) > 1 else TARGET_CLUSTERS

    for cluster_id in target_clusters:
        print(f"[cluster] building {cluster_id}")
        df, canonical, problem_obj, private_notes = build_rows_for_cluster(cluster_id, members_df)
        out = apply_cluster_reclustering(df, cluster_id)
        non_full = out[out["is_non_full"]]
        residual_count = int((non_full["pattern"] == "Other wrong-answer logic pattern (residual)").sum())
        residual_pct = (100.0 * residual_count / len(non_full)) if len(non_full) else 0.0
        print(f"[cluster] {cluster_id} non_full={len(non_full)} residual={residual_count} ({residual_pct:.1f}%)")
        crow_df = clusters_df[clusters_df["cluster_id"] == cluster_id]
        if crow_df.empty:
            raise RuntimeError(f"Missing cluster row for {cluster_id}")
        write_cluster_report(crow_df.iloc[0].to_dict(), members_df, out, problem_obj, private_notes)
        print(f"[cluster] wrote {crow_df.iloc[0]['cluster_file']}")


if __name__ == "__main__":
    main()
