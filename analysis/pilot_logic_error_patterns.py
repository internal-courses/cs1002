#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
#   "pyarrow>=16.0.0",
#   "tree-sitter>=0.22.0",
#   "tree-sitter-python>=0.23.0",
# ]
# ///
"""Pilot logic error pattern mining for a single Python question.

This script focuses on one question (namespace + problem_id), extracts only the
latest evaluated final submissions (event_type=submission, evaluation_type=private),
strips evaluator scaffolding, parses student code with tree-sitter-python, and
clusters non-full submissions into specific error patterns enriched with private
test-case failure signatures.

It is designed as a prototype for the eventual all-question `analysis/ERRORS.md`
pipeline and intentionally includes question-specific detectors for the Pangram
Check pilot while keeping the generic extraction/clustering pieces reusable.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import duckdb
import pandas as pd
import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.generate_error_taxonomy import (
    TsAnalyzer,
    extract_student_editable_code,
    load_question_skeletons,
    parse_test_case_results,
)


ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "error_pattern_pilot"

PY_LANGUAGE = Language(tspython.language())
CASE_BOOL_RE = re.compile(r"\b(True|False)\b")


@dataclass(slots=True)
class QuestionTests:
    public_tests: list[dict[str, Any]]
    private_tests: list[dict[str, Any]]
    private_case_tags: dict[int, list[str]]
    private_case_assertions: dict[int, list[dict[str, Any]]]
    question_title: str | None
    short_description: str | None


class TsWalk:
    def __init__(self) -> None:
        self.parser = Parser(PY_LANGUAGE)

    def parse(self, code: str) -> tuple[bytes, Node]:
        source = (code or "").encode("utf-8", errors="replace")
        tree = self.parser.parse(source)
        return source, tree.root_node

    @staticmethod
    def text(source: bytes, node: Node | None) -> str:
        if node is None:
            return ""
        return source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")

    @staticmethod
    def iter_nodes(root: Node) -> Iterable[Node]:
        stack = [root]
        while stack:
            node = stack.pop()
            yield node
            for child in reversed(node.children):
                stack.append(child)

    @staticmethod
    def find_function(root: Node, source: bytes, name: str) -> Node | None:
        for node in TsWalk.iter_nodes(root):
            if node.type != "function_definition":
                continue
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                if source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="ignore") == name:
                    return node
        return None

    @staticmethod
    def child_field(node: Node, field: str) -> Node | None:
        return node.child_by_field_name(field)


def normalize_code_block(s: str | None) -> str:
    if not s:
        return ""
    text = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--namespace", default="ns_25t2_py21_1")
    p.add_argument("--problem-id", type=int, default=16)
    p.add_argument("--function-name", default="is_pangram")
    p.add_argument(
        "--mode",
        default="auto",
        choices=[
            "auto",
            "pangram",
            "generic",
            "electricity_bill",
            "reverse_combined_palindrome",
            "arithmetic_progression",
        ],
        help="Detector/classifier mode. 'auto' picks based on function name.",
    )
    p.add_argument("--out-dir", default=str(OUT_DIR))
    p.add_argument("--max-examples-per-pattern", type=int, default=3)
    p.add_argument("--top-residual-clusters", type=int, default=10)
    return p.parse_args()


def make_conn() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def load_question_json(namespace: str, problem_id: int) -> dict[str, Any]:
    fp = ROOT / "problems" / namespace / f"{problem_id}.json"
    return json.loads(fp.read_text(encoding="utf-8"))


def _extract_assertions_from_test_input(inp: str) -> list[dict[str, Any]]:
    """Best-effort parser for `is_equal(is_pangram("..."), True)` test scripts."""
    out: list[dict[str, Any]] = []
    # Parse as Python source and inspect calls.
    try:
        tree = ast.parse(inp)
    except Exception:
        return out

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        fn_name = fn.id if isinstance(fn, ast.Name) else None
        if fn_name != "is_equal" or len(node.args) < 2:
            continue

        arg0 = node.args[0]
        arg1 = node.args[1]
        if not isinstance(arg0, ast.Call):
            continue
        inner_fn = arg0.func.id if isinstance(arg0.func, ast.Name) else None
        if inner_fn != "is_pangram" or len(arg0.args) < 1:
            continue
        text_val = None
        if isinstance(arg0.args[0], ast.Constant) and isinstance(arg0.args[0].value, str):
            text_val = arg0.args[0].value
        expected_val = None
        if isinstance(arg1, ast.Constant) and isinstance(arg1.value, bool):
            expected_val = arg1.value
        out.append({"input_text": text_val, "expected": expected_val})
    return out


def _tags_for_pangram_input(s: str | None, expected: bool | None) -> list[str]:
    if s is None:
        return []
    tags: list[str] = []
    if expected is True:
        tags.append("pangram_positive")
    if expected is False:
        tags.append("pangram_negative")
    if any(ch.isupper() for ch in s):
        tags.append("uppercase")
    if any(ch.isdigit() for ch in s):
        tags.append("digit")
    if any(not ch.isalnum() and not ch.isspace() for ch in s):
        tags.append("punctuation")
    if " " in s:
        tags.append("space")
    letters = [ch.lower() for ch in s if ch.isalpha()]
    uniq_letters = len(set(letters))
    if len(letters) == 26:
        tags.append("exactly_26_letters")
    if len(s) == 26:
        tags.append("exactly_26_chars")
    if uniq_letters == 26:
        tags.append("contains_all_letters")
    if uniq_letters < 26:
        tags.append("missing_letters")
    if letters and len(letters) != len(set(letters)):
        tags.append("repeated_letters")
    if s.lower() == "abcdefghijklmnopqrstuvwxyz":
        tags.append("alphabet_in_order")
    if s.lower() == "zyxwvutsrqponmlkjihgfedcba":
        tags.append("alphabet_reverse_order")
    return tags


def load_question_tests(namespace: str, problem_id: int) -> QuestionTests:
    obj = load_question_json(namespace, problem_id)
    public_tests = list(obj.get("public_testcase") or [])
    private_tests = list(obj.get("private_testcase") or [])

    private_case_tags: dict[int, list[str]] = {}
    private_case_assertions: dict[int, list[dict[str, Any]]] = {}
    for idx, tc in enumerate(private_tests, start=1):
        assertions = _extract_assertions_from_test_input(str(tc.get("input") or ""))
        private_case_assertions[idx] = assertions
        tags: set[str] = set()
        for a in assertions:
            tags.update(_tags_for_pangram_input(a.get("input_text"), a.get("expected")))
        private_case_tags[idx] = sorted(tags)

    return QuestionTests(
        public_tests=public_tests,
        private_tests=private_tests,
        private_case_tags=private_case_tags,
        private_case_assertions=private_case_assertions,
        question_title=obj.get("question_title") or None,
        short_description=obj.get("short_description") or None,
    )


def extract_final_submission_rows(conn: duckdb.DuckDBPyConnection, namespace: str, problem_id: int) -> pd.DataFrame:
    sql = f"""
    WITH finals AS (
      SELECT * EXCLUDE (rn)
      FROM (
        SELECT
          t.namespace,
          CAST(t.problem_id AS INTEGER) AS problem_id,
          t.student_id,
          CAST(t.timestamp_utc AS TIMESTAMP) AS timestamp_utc,
          t.code_sha256,
          t.is_parseable,
          t.reason,
          t.summary,
          t.score,
          t.num_test_evaluated,
          t.num_test_passed,
          t.test_case_count,
          ROW_NUMBER() OVER (
            PARTITION BY t.namespace, t.problem_id, t.student_id
            ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
          ) AS rn
        FROM read_parquet('analysis/submission_timeline.parquet') t
        WHERE t.event_type = 'submission'
          AND t.evaluation_type = 'private'
          AND t.namespace = '{namespace}'
          AND CAST(t.problem_id AS INTEGER) = {problem_id}
      ) x
      WHERE rn = 1
    ),
    raw_final AS (
      SELECT * EXCLUDE (rn)
      FROM (
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          FileName AS file_name,
          COALESCE(
            try_strptime(regexp_extract(FileName, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(regexp_extract(FileName, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
          ) AS event_ts,
          CompilationResult AS compilation_result_json,
          ROW_NUMBER() OVER (
            PARTITION BY Namespace, ProblemID, StudentID,
                         COALESCE(
                           try_strptime(regexp_extract(FileName, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
                           try_strptime(regexp_extract(FileName, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
                         )
            ORDER BY FileName DESC
          ) AS rn
        FROM read_json(
          'submissions/*.json',
          format='newline_delimited',
          columns={{
            Namespace:'VARCHAR',
            ProblemID:'VARCHAR',
            StudentID:'VARCHAR',
            FileName:'VARCHAR',
            EvaluationType:'VARCHAR',
            CompilationResult:'VARCHAR'
          }}
        )
        WHERE Namespace = '{namespace}'
          AND ProblemID = '{problem_id}'
          AND EvaluationType = 'private'
          AND FileName IS NOT NULL AND FileName <> ''
          AND regexp_extract(FileName, '/(submission)/', 1) = 'submission'
          AND json_valid(CompilationResult)
      ) x
      WHERE rn = 1
    )
    SELECT
      f.*,
      c.code_snapshot,
      r.file_name AS raw_file_name,
      r.compilation_result_json
    FROM finals f
    LEFT JOIN read_parquet('analysis/code_snapshots.parquet') c USING (code_sha256)
    LEFT JOIN raw_final r
      ON r.namespace = f.namespace
     AND r.problem_id = f.problem_id
     AND r.student_id = f.student_id
     AND r.event_ts = f.timestamp_utc
    ORDER BY f.student_id
    """
    return conn.execute(sql).df()


def _node_text(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")


def _is_name(node: Node | None, source: bytes, value: str) -> bool:
    return bool(node is not None and node.type == "identifier" and _node_text(source, node) == value)


def _call_name(node: Node, source: bytes) -> str | None:
    if node.type != "call":
        return None
    fn = node.child_by_field_name("function")
    if fn is None:
        return None
    if fn.type == "identifier":
        return _node_text(source, fn)
    if fn.type == "attribute":
        attr = fn.child_by_field_name("attribute")
        if attr is not None:
            base = fn.child_by_field_name("object")
            base_name = _node_text(source, base) if base is not None else "<?>"
            return f"{base_name}.{_node_text(source, attr)}"
    return _node_text(source, fn).strip()


def _walk(node: Node) -> Iterable[Node]:
    stack = [node]
    while stack:
        cur = stack.pop()
        yield cur
        for child in reversed(cur.children):
            stack.append(child)


def _collect_call_names(root: Node, source: bytes) -> list[str]:
    out: list[str] = []
    for n in _walk(root):
        if n.type == "call":
            name = _call_name(n, source)
            if name:
                out.append(name)
    return out


def _function_body_statements(fn_node: Node) -> list[Node]:
    body = fn_node.child_by_field_name("body")
    if body is None:
        return []
    if body.type == "block":
        return [c for c in body.children if c.type not in {"comment", "\n"}]
    return [body]


def _is_docstring_stmt(node: Node, source: bytes) -> bool:
    if node.type != "expression_statement":
        return False
    txt = _node_text(source, node).strip()
    return txt.startswith(("'''", '"""'))


def _function_executable_statements(fn_node: Node, source: bytes) -> list[Node]:
    stmts = _function_body_statements(fn_node)
    out: list[Node] = []
    for i, stmt in enumerate(stmts):
        if i == 0 and _is_docstring_stmt(stmt, source):
            continue
        out.append(stmt)
    return out


def _function_logic_code(fn_node: Node, source: bytes) -> str:
    pieces = [_node_text(source, n) for n in _function_executable_statements(fn_node, source)]
    return normalize_code_block("\n".join(pieces))


def _contains_node_type(root: Node, node_type: str) -> bool:
    return any(n.type == node_type for n in _walk(root))


def _return_literal_counts(root: Node) -> tuple[int, int, int]:
    total = 0
    true_count = 0
    false_count = 0
    for n in _walk(root):
        if n.type != "return_statement":
            continue
        total += 1
        children = [c for c in n.children if c.type not in {"return", "comment", "\n"}]
        if len(children) == 1:
            if children[0].type == "true":
                true_count += 1
            elif children[0].type == "false":
                false_count += 1
    return total, true_count, false_count


def _extract_strings(root: Node, source: bytes) -> list[str]:
    vals: list[str] = []
    for n in _walk(root):
        if n.type == "string":
            txt = _node_text(source, n).strip()
            vals.append(txt)
    return vals


def _normalized_node_sig(node: Node, source: bytes, depth: int = 0, max_depth: int = 5) -> str:
    """Normalize identifiers/literals to compare structure across submissions."""
    # Ignore comments / formatting artifacts.
    if node.type in {"comment"}:
        return ""
    if node.type in {"identifier"}:
        return "id"
    if node.type in {"integer", "float"}:
        return "num"
    if node.type in {"string", "string_content"}:
        return "str"
    if node.type in {"true", "false", "none"}:
        return node.type
    if depth >= max_depth or not node.children:
        # Preserve token-ish node types, not exact text.
        return node.type
    child_sigs = []
    for c in node.children:
        sig = _normalized_node_sig(c, source, depth + 1, max_depth=max_depth)
        if sig:
            child_sigs.append(sig)
    return f"{node.type}(" + ",".join(child_sigs) + ")"


def _normalized_function_fingerprint(fn_node: Node, source: bytes) -> str:
    body = fn_node.child_by_field_name("body")
    target = body if body is not None else fn_node
    sig = _normalized_node_sig(target, source, max_depth=6)
    return hashlib.sha1(sig.encode("utf-8")).hexdigest()[:16] + ":" + sig[:500]


def _stmt_shape_signature(fn_node: Node, source: bytes) -> str:
    body = fn_node.child_by_field_name("body")
    if body is None:
        return ""
    stmt_types: list[str] = []
    for c in body.children:
        if c.type in {"comment", "\n"}:
            continue
        if c.type == "expression_statement":
            # Drop docstring statement if present.
            txt = _node_text(source, c).strip()
            if txt.startswith(("'''", '"""')):
                continue
        if c.type == "block":
            for s in c.children:
                if s.type == "expression_statement":
                    txt = _node_text(source, s).strip()
                    if txt.startswith(("'''", '"""')):
                        continue
                if s.type not in {"comment", "\n"}:
                    stmt_types.append(s.type)
        else:
            stmt_types.append(c.type)
    return " > ".join(stmt_types)


def _comparison_signatures(root: Node, source: bytes) -> list[str]:
    out: list[str] = []
    for n in _walk(root):
        if n.type != "comparison_operator":
            continue
        left = n.child_by_field_name("left")
        right = n.child_by_field_name("right")
        op_txt = ""
        for c in n.children:
            if c.type in {"<", ">", "<=", ">=", "==", "!=", "in", "not in", "is", "is not"}:
                op_txt = c.type
                break
        left_sig = _normalized_node_sig(left, source, max_depth=3) if left is not None else "?"
        right_sig = _normalized_node_sig(right, source, max_depth=3) if right is not None else "?"
        out.append(f"{left_sig} {op_txt} {right_sig}")
    return out


def _frequent_subtree_signatures(root: Node, source: bytes) -> Counter[str]:
    """Depth-2 signatures to surface common subtrees within a cluster."""
    counts: Counter[str] = Counter()
    for n in _walk(root):
        if n.type in {"identifier", "string", "integer", "float", "comment", "string_content"}:
            continue
        child_types = [c.type for c in n.children if c.type != "comment"]
        if not child_types:
            continue
        sig = f"{n.type}(" + ",".join(child_types[:6]) + (",..." if len(child_types) > 6 else "") + ")"
        counts[sig] += 1
    return counts


def _get_exception_type_from_case_output(cases: list[dict[str, Any]]) -> str | None:
    exc_re = re.compile(
        r"\b(NameError|TypeError|IndexError|KeyError|ValueError|ZeroDivisionError|RecursionError|AttributeError|MemoryError|AssertionError|RuntimeError|OverflowError|ImportError|ModuleNotFoundError|UnboundLocalError|StopIteration|FileNotFoundError|PermissionError|OSError|EOFError)\b"
    )
    for c in cases:
        txt = str(c.get("output") or "")
        m = exc_re.search(txt)
        if m:
            return m.group(1)
    return None


def _split_bool_lines(text: str | None) -> list[str]:
    if not text:
        return []
    return CASE_BOOL_RE.findall(text)


def _private_case_failure_vector(cases: list[dict[str, Any]], expected_len: int) -> str:
    bits: list[str] = []
    for i in range(expected_len):
        if i < len(cases):
            bits.append("1" if bool(cases[i].get("passed")) else "0")
        else:
            bits.append("?")
    return "".join(bits)


def _detect_early_return_inside_loop(fn_node: Node) -> bool:
    for n in _walk(fn_node):
        if n.type not in {"for_statement", "while_statement"}:
            continue
        body = n.child_by_field_name("body")
        if body is None:
            continue
        if any(b.type == "return_statement" for b in _walk(body)):
            return True
    return False


def _detect_generic_patterns(
    fn_node: Node,
    source: bytes,
    function_logic_code: str,
    case_vector: str,
    cases: list[dict[str, Any]],
    *,
    is_parseable: bool,
) -> list[str]:
    if not is_parseable:
        return []

    tags: list[str] = []
    code_text = function_logic_code or ""
    code_low = code_text.lower()

    exec_stmts = _function_executable_statements(fn_node, source)
    stmt_count = len(exec_stmts)
    has_ellipsis = _contains_node_type(fn_node, "ellipsis")
    has_pass_stmt = _contains_node_type(fn_node, "pass_statement")
    return_count, return_true_count, return_false_count = _return_literal_counts(fn_node)
    call_names = _collect_call_names(fn_node, source)
    call_set = set(call_names)

    fn_name_node = fn_node.child_by_field_name("name")
    fn_name = _node_text(source, fn_name_node) if fn_name_node is not None else ""

    if has_ellipsis:
        tags.append("ellipsis_placeholder_present")
    if has_pass_stmt:
        tags.append("pass_statement_present")
    if stmt_count <= 1 and has_ellipsis and return_count == 0:
        tags.append("skeleton_placeholder_only")
    if return_count == 0:
        tags.append("no_return_statement")
    if return_count == 1 and return_true_count == 1:
        tags.append("always_returns_true")
    if return_count == 1 and return_false_count == 1:
        tags.append("always_returns_false")

    if _detect_early_return_inside_loop(fn_node):
        tags.append("early_return_inside_loop")

    if any(name == "print" or name.endswith(".print") for name in call_names):
        tags.append("uses_print")
        if return_count == 0:
            tags.append("prints_but_does_not_return")

    if any(name in {"input", "int", "float"} for name in call_names) and ("input(" in code_text):
        tags.append("reads_input_inside_function_type_question")

    if "sorted" in call_set:
        tags.append("uses_sorted")
    if "set" in call_set:
        tags.append("uses_set")
    if "len" in call_set:
        tags.append("uses_len")
    if "abs" in call_set:
        tags.append("uses_abs")
    if "all" in call_set:
        tags.append("uses_all")
    if "any" in call_set:
        tags.append("uses_any")

    if "[::-1]" in code_text.replace(" ", ""):
        tags.append("uses_slice_reverse")

    if fn_name and fn_name in call_set:
        tags.append("calls_function_recursively")

    if "if " in code_low:
        tags.append("uses_conditional")
    if "for " in code_low or "while " in code_low:
        tags.append("uses_loop")

    if code_text:
        if re.search(r"\breturn\s+['\"]", code_text):
            tags.append("returns_string_literal")
        if re.search(r"\breturn\s+\d+(\.\d+)?\b", code_text):
            tags.append("returns_numeric_literal")

    exc = _get_exception_type_from_case_output(cases)
    if exc:
        tags.append(f"runtime_{exc.lower()}")

    # Coarse private-case difficulty signatures are useful for cross-variant comparison.
    if case_vector and "?" not in case_vector:
        fails = case_vector.count("0")
        if fails == 1:
            tags.append("fails_one_private_case_group")
        elif fails == 2:
            tags.append("fails_two_private_case_groups")
        elif fails == 3:
            tags.append("fails_all_private_case_groups")

    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _primary_generic_pattern(row: pd.Series) -> str:
    tags = set(row.get("detector_tags") or [])
    summary = str(row.get("summary") or "")
    is_parseable = bool(row.get("is_parseable"))
    exception_type = str(row.get("exception_type") or "")
    stmt_count = int(row.get("body_non_doc_stmt_count") or 0)
    return_count = int(row.get("return_count") or 0)
    return_true_count = int(row.get("return_true_count") or 0)
    return_false_count = int(row.get("return_false_count") or 0)
    has_ellipsis = bool(row.get("has_ellipsis_node"))

    if not is_parseable:
        return "Syntax / non-parseable final submission"
    if summary == "All Cases Passed":
        return "All Cases Passed"
    if summary == "Runtime Error":
        if exception_type in {"NameError", "TypeError", "AttributeError", "IndexError", "KeyError", "ValueError", "RecursionError"}:
            return f"Runtime {exception_type}"
        return "Runtime error (parseable final submission)"

    if summary == "Wrong Answer":
        if "skeleton_placeholder_only" in tags or (has_ellipsis and stmt_count <= 1 and return_count == 0):
            return "Skeleton placeholder `...` left in function"
        if "prints_but_does_not_return" in tags:
            return "Prints output but does not return required value"
        if return_count == 0:
            return "No return / implicit `None`"
        if return_count == 1 and return_true_count == 1:
            return "Always returns `True` (constant output)"
        if return_count == 1 and return_false_count == 1:
            return "Always returns `False` (constant output)"
        if "reads_input_inside_function_type_question" in tags:
            return "Reads input inside function-type question instead of using parameters"
        if "early_return_inside_loop" in tags:
            return "Returns inside loop before completing full check/computation"
        if "returns_string_literal" in tags:
            return "Returns wrong output type / hard-coded string result"
        if "returns_numeric_literal" in tags and "uses_conditional" not in tags and "uses_loop" not in tags:
            return "Returns hard-coded numeric result"
        return "Other wrong-answer logic pattern (residual)"

    return f"{summary or 'Unknown'}"


def _detect_pangram_patterns(
    fn_node: Node,
    root: Node,
    source: bytes,
    function_logic_code: str,
    case_vector: str,
    cases: list[dict[str, Any]],
    *,
    is_parseable: bool,
) -> list[str]:
    """Question-specific detectors for Pangram Check; order matters for specificity."""
    if not is_parseable:
        return []

    tags: list[str] = []
    all_calls = _collect_call_names(fn_node, source)
    exec_stmts = _function_executable_statements(fn_node, source)
    strings: list[str] = []
    for stmt in exec_stmts:
        strings.extend(_extract_strings(stmt, source))
    code_text = function_logic_code or ""
    code_low = code_text.lower()
    stmt_count = len(exec_stmts)
    has_ellipsis = _contains_node_type(fn_node, "ellipsis")
    has_pass_stmt = _contains_node_type(fn_node, "pass_statement")
    return_count, return_true_count, return_false_count = _return_literal_counts(fn_node)

    has_lower = any(name.endswith(".lower") for name in all_calls)
    has_set = any(name == "set" for name in all_calls)
    has_len = any(name == "len" for name in all_calls)
    has_replace = any(name.endswith(".replace") for name in all_calls)
    has_split = any(name.endswith(".split") for name in all_calls)
    has_join = any(name.endswith(".join") for name in all_calls)
    has_isalpha = any(name.endswith(".isalpha") for name in all_calls)
    has_ascii_lowercase = "string.ascii_lowercase" in code_text

    if has_ellipsis:
        tags.append("ellipsis_placeholder_present")
    if has_pass_stmt:
        tags.append("pass_statement_present")
    if stmt_count <= 1 and has_ellipsis and return_count == 0:
        tags.append("skeleton_placeholder_only")
    if return_count == 0:
        tags.append("no_return_statement")
    if return_count == 1 and return_true_count == 1:
        tags.append("always_returns_true")
    if return_count == 1 and return_false_count == 1:
        tags.append("always_returns_false")

    # Early return inside loop is a classic bug for membership checks.
    for n in _walk(fn_node):
        if n.type in {"for_statement", "while_statement"}:
            body = n.child_by_field_name("body")
            if body is None:
                continue
            # Detect any return directly nested in loop body before loop completes.
            for b in _walk(body):
                if b.type == "return_statement":
                    tags.append("early_return_inside_loop")
                    break
            if "early_return_inside_loop" in tags:
                break

    # Hard-coded sample/example matching or order-sensitive exact equality to alphabet strings.
    exec_string_literals = [s for s in strings if any(ch.isalpha() for ch in s)]
    if any(k in code_low for k in ["quick brown fox", "zyxwvutsrqponmlkjihgfedcba", "abcdefghijklmnopqrstuvwxyz"]):
        if "==" in code_text and ("if " in code_low or "return " in code_low):
            tags.append("hardcodes_example_strings_or_exact_phrases")
    if ("string.ascii_lowercase" in code_text or "string.ascii_uppercase" in code_text) and "==" in code_text and not has_set:
        tags.append("checks_exact_alphabet_string_order")
    if re.search(r"\btext\s+in\s+string\.ascii_lowercase\b", code_low):
        tags.append("checks_text_as_substring_of_alphabet")

    # Length-based shortcuts (exact string length or unique char count) without filtering alphabet letters.
    if ("len(" in code_text) and ("26" in code_text):
        if ("len(text)" in code_text or "len(s)" in code_text or "len(string)" in code_text) and not has_set:
            tags.append("uses_total_length_26_heuristic")
        if "len(set(" in code_low and not (has_isalpha or has_ascii_lowercase):
            tags.append("uses_len_set_text_without_filtering_nonletters")
        if "len(set(" in code_low:
            # Often combined with ==26 and no alphabet subset check.
            if not has_ascii_lowercase and "<=" not in code_text and "issubset" not in code_low:
                tags.append("uses_unique_char_count_instead_of_alphabet_subset")
    if "len(set(" in code_low and "string.ascii_lowercase" in code_text and ("==" in code_text or ">=" in code_text):
        if "<=" not in code_text and "issubset" not in code_low:
            tags.append("uses_unique_char_count_instead_of_alphabet_subset")

    # Equality to alphabet set rejects valid pangrams with extra characters/spaces.
    if has_set and has_ascii_lowercase:
        if "==" in code_text and "string.ascii_lowercase" in code_text and "<=" not in code_text and "issubset" not in code_low:
            tags.append("requires_exact_alphabet_set_equality")
        if ("<=" in code_text or "issubset" in code_low) and not has_lower:
            tags.append("subset_check_without_case_normalization")

    # Uses lowercase but only strips spaces (still fails punctuation/digits if equality/count-based).
    if has_lower and (has_replace or (has_split and has_join)):
        if not has_isalpha and not has_ascii_lowercase:
            tags.append("normalizes_spaces_only_not_nonletters")

    if re.search(r"\btext\.isalpha\s*\(", code_low) and (has_set or has_len or has_ascii_lowercase):
        tags.append("gates_on_text_isalpha_rejecting_spaces_or_punctuation")

    # Counting/dictionary approaches often include digits or fixed alphadigit maps and crash on punctuation.
    if "dict" in code_low or "{}" in code_text or "d[" in code_text:
        if any("123" in s or "012" in s for s in strings) or "1234567890" in code_text:
            tags.append("counts_alnum_but_misses_punctuation_keyerrors")
        elif "abcdefghijklmnopqrstuvwxyz" in code_low and "d[" in code_text:
            tags.append("manual_letter_counting_dictionary")

    # Counts letters seen (including duplicates) instead of counting unique coverage.
    if (("count" in code_low or "counter" in code_low) and ("+=" in code_text or "count+=" in code_low)):
        compares_to_alphabet_len = (
            "len(string.ascii_lowercase)" in code_text or re.search(r"\bcount\s*[<>!=]=?\s*26\b", code_low) is not None
        )
        if compares_to_alphabet_len and not has_set:
            tags.append("counts_total_letters_not_unique_letters")

    # Wrong abstraction: set of words instead of letters.
    if has_split and has_set and ("word" in code_low or "words" in code_low or "split(" in code_low):
        if "for i in text.split" in code_low or "set(text.split" in code_low:
            tags.append("checks_words_not_letters")

    # Hard-coded alphabet membership loop but missing lower().
    if "abcdefghijklmnopqrstuvwxyz" in code_low and " in text" in code_low and not has_lower:
        tags.append("alphabet_membership_without_case_normalization")

    # Detect overfitting to digits/nonletters (incorrectly requiring/forbidding digits).
    if "1234567890" in code_text or "nums=" in code_low or "digit" in code_low:
        tags.append("digit_handling_logic_intrudes_on_pangram_condition")

    # Case-vector-informed refinements.
    # For this question private cases:
    # case1 has uppercase + negative;
    # case2 has digits/nonletters + positive reverse order and one negative;
    # case3 includes punctuation+digits positive and short negatives.
    if case_vector == "011" and not has_lower:
        tags.append("fails_uppercase_private_case_only")
    if case_vector in {"101", "001"} and (has_set or has_len or "count" in code_low):
        tags.append("fails_digit_nonletter_private_case")
    if case_vector == "110":
        tags.append("fails_punctuation_or_short_negative_case")
    if case_vector in {"100", "101", "001"} and "gates_on_text_isalpha_rejecting_spaces_or_punctuation" in tags:
        tags.append("isalpha_gate_matches_failure_signature")

    # Runtime pattern hints.
    exc = _get_exception_type_from_case_output(cases)
    if exc == "KeyError":
        tags.append("runtime_keyerror_on_unexpected_character")
    elif exc == "TypeError":
        tags.append("runtime_typeerror")
    elif exc:
        tags.append(f"runtime_{exc.lower()}")

    # Default semantic families (useful for residual grouping).
    if has_ascii_lowercase:
        tags.append("uses_string_ascii_lowercase")
    if has_set:
        tags.append("uses_set")
    if has_isalpha:
        tags.append("uses_isalpha")
    if has_lower:
        tags.append("uses_lower")

    # Deduplicate preserving order.
    seen: set[str] = set()
    deduped: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def _primary_pangram_pattern(
    row: pd.Series,
) -> str:
    tags = set(row.get("detector_tags") or [])
    summary = str(row.get("summary") or "")
    case_vector = str(row.get("private_case_vector") or "")
    is_parseable = bool(row.get("is_parseable"))
    exception_type = str(row.get("exception_type") or "")
    stmt_count = int(row.get("body_non_doc_stmt_count") or 0)
    return_count = int(row.get("return_count") or 0)
    return_true_count = int(row.get("return_true_count") or 0)
    return_false_count = int(row.get("return_false_count") or 0)
    has_ellipsis = bool(row.get("has_ellipsis_node"))

    if not is_parseable:
        return "Syntax / non-parseable final submission"
    if summary == "Runtime Error":
        if exception_type == "KeyError" or "runtime_keyerror_on_unexpected_character" in tags:
            return "Manual character-count dictionary crashes on punctuation/unknown characters (KeyError)"
        if exception_type == "NameError":
            return "Runtime NameError from undefined variable/helper in pangram logic"
        if exception_type == "AttributeError":
            return "Runtime AttributeError from wrong object/type method usage"
        if exception_type == "RecursionError":
            return "Infinite recursion (function calls itself without valid base case)"
        if exception_type == "TypeError" or "runtime_typeerror" in tags:
            return "Runtime TypeError in custom counting/checking logic"
        return "Runtime error in parseable final logic"
    if summary == "All Cases Passed":
        return "All Cases Passed"

    if summary == "Wrong Answer":
        if "skeleton_placeholder_only" in tags or (has_ellipsis and stmt_count <= 1 and return_count == 0):
            return "Skeleton placeholder `...` left in function (no implementation; returns None)"
        if return_count == 0:
            return "Computes values but never returns a boolean (implicit `None`)"
        if return_count == 1 and return_true_count == 1:
            return "Always returns `True` (constant output)"
        if return_count == 1 and return_false_count == 1:
            return "Always returns `False` (constant output)"

    if "early_return_inside_loop" in tags:
        return "Returns inside the alphabet-check loop (decides after first character/iteration)"
    if "hardcodes_example_strings_or_exact_phrases" in tags:
        return "Hard-codes sample pangram strings/examples instead of checking letter coverage"
    if "checks_exact_alphabet_string_order" in tags:
        return "Checks exact alphabet string order (`abcdefghijklmnopqrstuvwxyz`) instead of pangram coverage"
    if "checks_text_as_substring_of_alphabet" in tags:
        return "Checks whether full input is a substring of the alphabet string"
    if "uses_total_length_26_heuristic" in tags:
        return "Uses total string length ==/>= 26 as pangram test (counts spaces/digits/punctuation)"
    if "requires_exact_alphabet_set_equality" in tags:
        return "Compares exact set(text) to alphabet set (rejects valid pangrams with extra chars/spaces)"
    if "subset_check_without_case_normalization" in tags or (
        "alphabet_membership_without_case_normalization" in tags and "fails_uppercase_private_case_only" in tags
    ):
        return "Alphabet coverage check is case-sensitive (forgets lowercasing)"
    if "gates_on_text_isalpha_rejecting_spaces_or_punctuation" in tags:
        return "Uses `text.isalpha()` gate, rejecting valid pangrams that include spaces/punctuation/digits"
    if "counts_total_letters_not_unique_letters" in tags:
        return "Counts total alphabetic characters instead of distinct letters"
    if "uses_unique_char_count_instead_of_alphabet_subset" in tags:
        return "Counts unique characters (or len(set(...)) == 26) instead of checking all letters"
    if "uses_len_set_text_without_filtering_nonletters" in tags:
        return "Uses len(set(text)) with no letter filtering, so spaces/digits/punctuation distort the count"
    if "normalizes_spaces_only_not_nonletters" in tags:
        return "Strips spaces only but not other non-letters; digit/punctuation cases still break logic"
    if "checks_words_not_letters" in tags:
        return "Checks unique words / split tokens instead of unique letters"
    if "manual_letter_counting_dictionary" in tags:
        return "Manual letter-counting implementation has incorrect coverage logic"
    if "digit_handling_logic_intrudes_on_pangram_condition" in tags and summary == "Wrong Answer":
        return "Incorrectly mixes digit-handling rules into pangram condition"

    if summary == "Wrong Answer":
        if case_vector == "011":
            return "Fails uppercase handling but otherwise close"
        if case_vector == "101":
            return "Fails non-letter/digit-heavy private case despite passing others"
        if case_vector == "110":
            return "Fails short-negative/punctuation private case due boundary filtering mistake"
        return "Other wrong-answer logic pattern (residual)"

    return f"{summary or 'Unknown'}"


def _shorten_code_example(code: str, max_lines: int = 22) -> str:
    lines = normalize_code_block(code).split("\n")
    if lines and lines[0].lstrip().startswith("def "):
        out: list[str] = [lines[0]]
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines):
            stripped = lines[i].lstrip()
            if stripped.startswith(("'''", '"""')):
                quote = "'''" if stripped.startswith("'''") else '"""'
                # One-line docstring.
                if stripped.count(quote) >= 2 and stripped != quote:
                    i += 1
                else:
                    i += 1
                    while i < len(lines):
                        if quote in lines[i]:
                            i += 1
                            break
                        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        out.extend(lines[i:])
        lines = out

    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + "\n# ..."


def _resolve_mode(mode: str, function_name: str) -> str:
    if mode != "auto":
        return mode
    fn = (function_name or "").strip()
    if fn == "is_pangram":
        return "pangram"
    if fn == "compute_electricity_bill":
        return "electricity_bill"
    if fn == "is_reverse_combined_palindrome":
        return "reverse_combined_palindrome"
    if fn == "is_arithmetic_progression":
        return "arithmetic_progression"
    return "generic"


def build_question_rows(
    df: pd.DataFrame,
    namespace: str,
    problem_id: int,
    function_name: str,
    *,
    mode: str,
) -> pd.DataFrame:
    skel_df, skeleton_map = load_question_skeletons()
    sk = skeleton_map.get((namespace, problem_id))
    if sk is None:
        raise RuntimeError(f"Missing skeleton metadata for {namespace}/{problem_id}")

    ts_walk = TsWalk()
    ts_analyzer = TsAnalyzer()
    resolved_mode = _resolve_mode(mode, function_name)
    print(f"[pilot] detector mode: {resolved_mode} (requested={mode}, function={function_name})")

    rows: list[dict[str, Any]] = []
    missing_raw = 0
    fn_missing = 0
    for rec in df.itertuples(index=False):
        code_snapshot = rec.code_snapshot if isinstance(rec.code_snapshot, str) else ""
        compilation_result_json = rec.compilation_result_json if isinstance(rec.compilation_result_json, str) else None
        if compilation_result_json is None:
            missing_raw += 1
        cases = parse_test_case_results(compilation_result_json)
        student_code, scaffold_status = extract_student_editable_code(code_snapshot, sk)
        student_code = normalize_code_block(student_code)

        source, root = ts_walk.parse(student_code)
        fn_node = ts_walk.find_function(root, source, function_name)
        if fn_node is None:
            fn_missing += 1
        target_root = fn_node if fn_node is not None else root
        target_code = _node_text(source, fn_node) if fn_node is not None else student_code
        target_code = normalize_code_block(target_code)
        function_logic_code = _function_logic_code(fn_node, source) if fn_node is not None else ""
        is_parseable = bool(rec.is_parseable)

        ts_metrics = ts_analyzer.analyze(student_code)
        case_vector = _private_case_failure_vector(cases, expected_len=3)
        subtree_counts = _frequent_subtree_signatures(target_root, source)
        has_ellipsis_node = _contains_node_type(fn_node, "ellipsis") if fn_node is not None else False
        has_pass_statement = _contains_node_type(fn_node, "pass_statement") if fn_node is not None else False
        body_non_doc_stmt_count = len(_function_executable_statements(fn_node, source)) if fn_node is not None else 0
        return_count, return_true_count, return_false_count = (
            _return_literal_counts(fn_node) if fn_node is not None else (0, 0, 0)
        )
        if fn_node is None:
            detector_tags = []
        elif resolved_mode == "pangram":
            detector_tags = _detect_pangram_patterns(
                fn_node,
                root,
                source,
                function_logic_code,
                case_vector,
                cases,
                is_parseable=is_parseable,
            )
        else:
            detector_tags = _detect_generic_patterns(
                fn_node,
                source,
                function_logic_code,
                case_vector,
                cases,
                is_parseable=is_parseable,
            )

        row_for_primary = pd.Series(
            {
                "detector_tags": detector_tags,
                "summary": getattr(rec, "summary"),
                "private_case_vector": case_vector,
                "is_parseable": is_parseable,
                "exception_type": _get_exception_type_from_case_output(cases),
                "body_non_doc_stmt_count": body_non_doc_stmt_count,
                "return_count": return_count,
                "return_true_count": return_true_count,
                "return_false_count": return_false_count,
                "has_ellipsis_node": has_ellipsis_node,
            }
        )
        if resolved_mode == "pangram":
            primary = _primary_pangram_pattern(row_for_primary)
        else:
            primary = _primary_generic_pattern(row_for_primary)

        # Approximate nested-loop presence and early-return location.
        for_count = sum(1 for n in _walk(target_root) if n.type == "for_statement")
        while_count = sum(1 for n in _walk(target_root) if n.type == "while_statement")
        return_count_all_target = sum(1 for n in _walk(target_root) if n.type == "return_statement")
        exception_type = _get_exception_type_from_case_output(cases)

        rows.append(
            {
                "namespace": rec.namespace,
                "problem_id": int(rec.problem_id),
                "student_id": rec.student_id,
                "timestamp_utc": str(rec.timestamp_utc),
                "is_parseable": is_parseable,
                "summary": rec.summary,
                "reason": rec.reason,
                "score": None if pd.isna(rec.score) else float(rec.score),
                "num_test_evaluated": None if pd.isna(rec.num_test_evaluated) else int(rec.num_test_evaluated),
                "num_test_passed": None if pd.isna(rec.num_test_passed) else int(rec.num_test_passed),
                "test_case_count": None if pd.isna(rec.test_case_count) else int(rec.test_case_count),
                "private_case_vector": case_vector,
                "private_failed_case_indices": [i + 1 for i, c in enumerate(cases) if not bool(c.get("passed"))],
                "compilation_case_count": len(cases),
                "exception_type": exception_type,
                "scaffold_strip_status": scaffold_status,
                "student_code": student_code,
                "function_code": target_code,
                "function_logic_code": function_logic_code,
                "function_missing": fn_node is None,
                "normalized_fingerprint": (_normalized_function_fingerprint(fn_node, source) if fn_node is not None else ""),
                "stmt_shape": (_stmt_shape_signature(fn_node, source) if fn_node is not None else ""),
                "comparison_signatures": _comparison_signatures(target_root, source),
                "call_names": _collect_call_names(target_root, source),
                "detector_tags": detector_tags,
                "primary_pattern": primary,
                "for_count": for_count,
                "while_count": while_count,
                "return_count": return_count,
                "return_count_target": return_count_all_target,
                "return_true_count": return_true_count,
                "return_false_count": return_false_count,
                "body_non_doc_stmt_count": body_non_doc_stmt_count,
                "has_ellipsis_node": has_ellipsis_node,
                "has_pass_statement": has_pass_statement,
                "subtree_sig_counts": dict(subtree_counts.most_common(80)),
                **ts_metrics,
            }
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        out["is_full_pass"] = out["score"].fillna(-1).eq(100.0)
        out["is_non_full"] = ~out["is_full_pass"]
    print(
        f"[pilot] extracted {len(out)} final submissions; raw compilation_result matched for "
        f"{len(out)-missing_raw}/{len(out)} rows; missing function def in {fn_missing} rows"
    )
    return out


def summarize_patterns(rows: pd.DataFrame, tests: QuestionTests, max_examples: int = 3) -> dict[str, Any]:
    total = len(rows)
    non_full = rows[rows["is_non_full"]].copy()
    parseable_non_full = non_full[non_full["is_parseable"]].copy()
    full_pass = rows[rows["is_full_pass"]].copy()

    pattern_records: list[dict[str, Any]] = []
    for pattern, g in non_full.groupby("primary_pattern", dropna=False):
        g = g.copy()
        n = len(g)
        parseable_n = int(g["is_parseable"].sum())
        med_score = float(g["score"].median()) if g["score"].notna().any() else None
        mean_score = float(g["score"].mean()) if g["score"].notna().any() else None
        case_vec_counts = Counter(str(x) for x in g["private_case_vector"].fillna(""))
        failed_case_counts = Counter()
        for inds in g["private_failed_case_indices"]:
            if isinstance(inds, list):
                for i in inds:
                    failed_case_counts[int(i)] += 1

        detector_counts = Counter()
        for tags in g["detector_tags"]:
            if isinstance(tags, list):
                detector_counts.update(tags)

        subtree_counts = Counter()
        for d in g["subtree_sig_counts"]:
            if isinstance(d, dict):
                subtree_counts.update(d)

        examples: list[dict[str, Any]] = []
        # Prefer rows with this pattern and representative common case vectors.
        for rec in (
            g.sort_values(["score", "student_id"], ascending=[True, True])
            .head(max_examples)
            .itertuples(index=False)
        ):
            examples.append(
                {
                    "student_id": rec.student_id,
                    "score": None if pd.isna(rec.score) else float(rec.score),
                    "summary": rec.summary,
                    "private_case_vector": rec.private_case_vector,
                    "detector_tags": rec.detector_tags,
                    "function_code": _shorten_code_example(rec.function_logic_code or rec.function_code),
                }
            )

        impact_notes: list[str] = []
        top_case_indices = [idx for idx, _ in failed_case_counts.most_common(3)]
        for idx in top_case_indices:
            tags = tests.private_case_tags.get(idx, [])
            if tags:
                impact_notes.append(f"private case {idx} ({', '.join(tags)})")
            else:
                impact_notes.append(f"private case {idx}")

        pattern_records.append(
            {
                "pattern": pattern,
                "count": n,
                "pct_of_non_full": (100.0 * n / len(non_full)) if len(non_full) else 0.0,
                "pct_of_all_final_submitters": (100.0 * n / total) if total else 0.0,
                "parseable_count": parseable_n,
                "median_score": med_score,
                "mean_score": mean_score,
                "score_distribution": dict(Counter([None if pd.isna(x) else float(x) for x in g["score"]])),
                "private_case_vector_counts": dict(case_vec_counts.most_common()),
                "private_failed_case_counts": dict(failed_case_counts.most_common()),
                "top_detector_tags": dict(detector_counts.most_common(8)),
                "top_common_subtrees": dict(subtree_counts.most_common(12)),
                "stmt_shapes_top": dict(Counter(g["stmt_shape"]).most_common(8)),
                "examples": examples,
                "impact_case_notes": impact_notes,
            }
        )

    # Residual clustering among parseable non-full rows.
    residual = parseable_non_full[parseable_non_full["primary_pattern"] == "Other wrong-answer logic pattern (residual)"].copy()
    residual_clusters: list[dict[str, Any]] = []
    if not residual.empty:
        for (fp, case_vec, stmt_shape), g in residual.groupby(["normalized_fingerprint", "private_case_vector", "stmt_shape"], dropna=False):
            if not fp:
                continue
            rec0 = g.iloc[0]
            residual_clusters.append(
                {
                    "count": int(len(g)),
                    "private_case_vector": case_vec,
                    "stmt_shape": stmt_shape,
                    "fingerprint": fp,
                    "example": {
                        "student_id": rec0["student_id"],
                        "score": rec0["score"],
                        "summary": rec0["summary"],
                        "function_code": _shorten_code_example(str(rec0.get("function_logic_code") or rec0["function_code"])),
                    },
                    "detector_tags_top": dict(
                        Counter(tag for tags in g["detector_tags"] for tag in (tags or [])).most_common(10)
                    ),
                }
            )
        residual_clusters.sort(key=lambda x: (-x["count"], str(x["private_case_vector"]), str(x["stmt_shape"])))

    return {
        "question": {
            "title": tests.question_title,
            "short_description": tests.short_description,
        },
        "counts": {
            "total_final_submitters": int(total),
            "full_pass": int(len(full_pass)),
            "non_full": int(len(non_full)),
            "parseable_non_full": int(len(parseable_non_full)),
            "non_parseable_non_full": int(len(non_full) - len(parseable_non_full)),
        },
        "private_case_tags": tests.private_case_tags,
        "private_case_assertions": tests.private_case_assertions,
        "patterns": sorted(pattern_records, key=lambda x: (-x["count"], x["pattern"])),
        "residual_clusters": residual_clusters,
    }


def _json_default(o: Any) -> Any:
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"Not JSON serializable: {type(o)}")


def write_outputs(
    out_dir: Path,
    namespace: str,
    problem_id: int,
    rows: pd.DataFrame,
    summary: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{namespace}__{problem_id}"
    rows_export = rows.copy()
    # Keep a compact CSV and a JSONL with nested fields.
    nested_cols = ["private_failed_case_indices", "comparison_signatures", "call_names", "detector_tags", "subtree_sig_counts"]
    for col in nested_cols:
        if col in rows_export.columns:
            rows_export[col] = rows_export[col].apply(lambda x: json.dumps(x, ensure_ascii=False, default=_json_default))
    rows_export.to_csv(out_dir / f"{stem}__final_rows.csv", index=False)

    with (out_dir / f"{stem}__summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=_json_default)

    # Human-readable quick report for iteration.
    lines: list[str] = []
    qtitle = summary["question"].get("title") or summary["question"].get("short_description") or "(unknown title)"
    counts = summary["counts"]
    lines.append(f"# Pilot Error Pattern Summary: {qtitle}")
    lines.append("")
    lines.append(f"- Namespace / Problem: `{namespace}` / `{problem_id}`")
    lines.append(f"- Final submitters: {counts['total_final_submitters']}")
    lines.append(f"- Full pass: {counts['full_pass']}")
    lines.append(f"- Non-full final submissions: {counts['non_full']}")
    lines.append(f"- Parseable non-full (logic/runtime focus): {counts['parseable_non_full']}")
    lines.append(f"- Non-parseable non-full: {counts['non_parseable_non_full']}")
    lines.append("")
    lines.append("## Private Case Tags (derived from testcase scripts)")
    for idx in sorted(summary["private_case_tags"]):
        tags = summary["private_case_tags"][idx]
        lines.append(f"- Case {idx}: {', '.join(tags)}")
    lines.append("")
    lines.append("## Top Patterns")
    for p in summary["patterns"][:12]:
        lines.append(
            f"- {p['pattern']}: {p['count']} rows "
            f"({p['pct_of_non_full']:.1f}% of non-full; median score {p['median_score']})"
        )
        if p["private_case_vector_counts"]:
            top_vec = next(iter(p["private_case_vector_counts"].items()))
            lines.append(f"  - top private-case pass vector: `{top_vec[0]}` x{top_vec[1]}")
        if p["impact_case_notes"]:
            lines.append(f"  - impact concentrated in: {', '.join(p['impact_case_notes'])}")
        if p["top_detector_tags"]:
            lines.append(
                "  - detector tags: "
                + ", ".join(f"{k} ({v})" for k, v in list(p["top_detector_tags"].items())[:5])
            )
    lines.append("")
    lines.append("## Residual Wrong-Answer Clusters (largest)")
    for rc in summary["residual_clusters"][:10]:
        lines.append(
            f"- count={rc['count']} vector={rc['private_case_vector']} stmt_shape={rc['stmt_shape'] or '<none>'}"
        )
        ex = rc["example"]
        lines.append(f"  - example student={ex['student_id']} score={ex['score']} summary={ex['summary']}")
        code = ex["function_code"].replace("\n", "\n    ")
        lines.append("  - code:")
        lines.append(f"    {code}")

    (out_dir / f"{stem}__summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    namespace = str(args.namespace)
    problem_id = int(args.problem_id)
    out_dir = Path(args.out_dir)

    print(f"[pilot] loading tests for {namespace}/{problem_id}")
    tests = load_question_tests(namespace, problem_id)

    print("[pilot] extracting final submissions + raw compilation results")
    conn = make_conn()
    df = extract_final_submission_rows(conn, namespace, problem_id)
    if df.empty:
        raise SystemExit("No final submissions found for target question")

    print("[pilot] parsing code with tree-sitter and building row features")
    rows = build_question_rows(
        df,
        namespace,
        problem_id,
        args.function_name,
        mode=str(args.mode),
    )

    print("[pilot] summarizing patterns and residual clusters")
    summary = summarize_patterns(rows, tests, max_examples=int(args.max_examples_per_pattern))

    print("[pilot] writing outputs")
    write_outputs(out_dir, namespace, problem_id, rows, summary)
    print(f"[pilot] done; outputs in {out_dir}")


if __name__ == "__main__":
    main()
