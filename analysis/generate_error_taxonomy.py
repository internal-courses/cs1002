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
"""Generate Step 3 error taxonomy (tree-sitter-enabled) outputs.

Outputs are written under ``analysis/error_taxonomy/`` and support the manual
README section "# Error Taxonomy".

Scope:
- Full student-question population (151,778 rows from ``analysis/final_scores.csv``)
- Tree-sitter structural analysis for Python questions (plus explicit unsupported
  language flags for non-Python rows)
- Runtime/wrong-output classification from best public ``test_run`` via raw
  ``CompilationResult.test_case_results``
"""

from __future__ import annotations

import ast
import json
import math
import os
import re
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "error_taxonomy"

PY_LANGUAGE = Language(tspython.language())

CONSTRUCT_NODE_MAP: dict[str, tuple[str, ...]] = {
    "function_def": ("function_definition",),
    "for_loop": ("for_statement",),
    "while_loop": ("while_statement",),
    "if_stmt": ("if_statement",),
    "elif_clause": ("elif_clause",),
    "else_clause": ("else_clause",),
    "list_comp": ("list_comprehension",),
    "dict_comp": ("dictionary_comprehension",),
    "try_stmt": ("try_statement",),
    "except_clause": ("except_clause",),
    "class_def": ("class_definition",),
    "return_stmt": ("return_statement",),
    "import_stmt": ("import_statement",),
    "import_from_stmt": ("import_from_statement",),
}
CONSTRUCT_COLUMNS = list(CONSTRUCT_NODE_MAP.keys()) + ["print_call"]

EXC_PATTERN = re.compile(
    r"\b(NameError|TypeError|IndexError|KeyError|ValueError|ZeroDivisionError|RecursionError|AttributeError|MemoryError|AssertionError|RuntimeError|OverflowError|ImportError|ModuleNotFoundError|UnboundLocalError|StopIteration|FileNotFoundError|PermissionError|OSError|EOFError)\b"
)
NUM_PATTERN = re.compile(r"[-+]?\d+(?:\.\d+)?")


@dataclass(slots=True)
class SkeletonInfo:
    namespace: str
    problem_id: int
    question_title: str | None
    language: str
    is_python: bool
    has_skeleton: bool
    prefixed_code: str
    uneditable_code: str
    suffixed_invisible_code: str
    skeleton_code: str
    skeleton_norm: str
    skeleton_meaningful_lines: int
    skeleton_feature_hash: dict[str, Any]


class TsAnalyzer:
    """Tree-sitter Python feature extractor that tolerates broken code."""

    def __init__(self) -> None:
        self.parser = Parser(PY_LANGUAGE)

    def analyze(self, code: str) -> dict[str, Any]:
        if code is None:
            code = ""
        source = code.encode("utf-8", errors="replace")
        tree = self.parser.parse(source)
        root = tree.root_node

        counts: dict[str, int] = {k: 0 for k in CONSTRUCT_COLUMNS}
        error_count = 0
        missing_count = 0
        node_count = 0
        max_depth = 0
        error_context_counts: Counter[str] = Counter()
        error_parent_counts: Counter[str] = Counter()
        first_error_line: int | None = None
        first_error_parent: str | None = None

        stack: list[tuple[Node, int, tuple[str, ...]]] = [(root, 0, ())]
        while stack:
            node, depth, ancestors = stack.pop()
            node_count += 1
            if depth > max_depth:
                max_depth = depth

            ntype = node.type
            for col, node_types in CONSTRUCT_NODE_MAP.items():
                if ntype in node_types:
                    counts[col] += 1

            if ntype == "call":
                fn_node = node.child_by_field_name("function")
                if fn_node is not None:
                    fn_text = source[fn_node.start_byte : fn_node.end_byte].decode(
                        "utf-8", errors="ignore"
                    )
                    if fn_text.strip() == "print":
                        counts["print_call"] += 1

            if node.is_missing:
                missing_count += 1

            if ntype == "ERROR":
                error_count += 1
                parent_type = node.parent.type if node.parent is not None else "<root>"
                error_parent_counts[parent_type] += 1
                if first_error_line is None:
                    first_error_line = int(node.start_point[0]) + 1
                    first_error_parent = parent_type

                ctx_labels: set[str] = set()
                if node.parent is None or node.parent.type == "module":
                    ctx_labels.add("top_level")
                for atype in ancestors:
                    if atype in {"function_definition", "parameters"}:
                        ctx_labels.add("in_function")
                        if atype == "parameters":
                            ctx_labels.add("function_signature")
                    if atype in {"for_statement", "while_statement"}:
                        ctx_labels.add("in_loop")
                    if atype in {"if_statement", "elif_clause", "else_clause"}:
                        ctx_labels.add("in_conditional")
                    if atype in {"list_comprehension", "dictionary_comprehension", "generator_expression"}:
                        ctx_labels.add("in_comprehension")
                    if atype in {"class_definition"}:
                        ctx_labels.add("in_class")
                if not ctx_labels:
                    ctx_labels.add("other")
                for label in ctx_labels:
                    error_context_counts[label] += 1

            next_ancestors = ancestors + (ntype,)
            # Reverse to preserve source order roughly when popping from stack
            for child in reversed(node.children):
                stack.append((child, depth + 1, next_ancestors))

        complexity_score = (
            counts["function_def"] * 3
            + counts["class_def"] * 4
            + counts["for_loop"] * 2
            + counts["while_loop"] * 2
            + counts["if_stmt"]
            + counts["elif_clause"]
            + counts["else_clause"]
            + counts["list_comp"] * 2
            + counts["dict_comp"] * 2
            + counts["try_stmt"] * 2
            + counts["except_clause"] * 2
            + counts["return_stmt"]
            + counts["print_call"]
            + counts["import_stmt"]
            + counts["import_from_stmt"]
        )

        return {
            **{f"ts_count_{k}": int(v) for k, v in counts.items()},
            **{f"ts_has_{k}": bool(v > 0) for k, v in counts.items()},
            "ts_error_count": int(error_count),
            "ts_missing_token_count": int(missing_count),
            "ts_node_count": int(node_count),
            "ts_max_depth": int(max_depth),
            "ts_complexity_score": int(complexity_score),
            "ts_error_ctx_top_level": int(error_context_counts.get("top_level", 0)),
            "ts_error_ctx_in_function": int(error_context_counts.get("in_function", 0)),
            "ts_error_ctx_function_signature": int(error_context_counts.get("function_signature", 0)),
            "ts_error_ctx_in_loop": int(error_context_counts.get("in_loop", 0)),
            "ts_error_ctx_in_conditional": int(error_context_counts.get("in_conditional", 0)),
            "ts_error_ctx_in_comprehension": int(error_context_counts.get("in_comprehension", 0)),
            "ts_error_ctx_in_class": int(error_context_counts.get("in_class", 0)),
            "ts_error_ctx_other": int(error_context_counts.get("other", 0)),
            "ts_first_error_line": first_error_line,
            "ts_first_error_parent": first_error_parent,
            "ts_top_error_parent_1": (error_parent_counts.most_common(1)[0][0] if error_parent_counts else None),
            "ts_top_error_parent_1_count": (int(error_parent_counts.most_common(1)[0][1]) if error_parent_counts else 0),
            "ts_top_error_parent_2": (error_parent_counts.most_common(2)[1][0] if len(error_parent_counts) > 1 else None),
            "ts_top_error_parent_2_count": (int(error_parent_counts.most_common(2)[1][1]) if len(error_parent_counts) > 1 else 0),
        }


def cpu_threads() -> int:
    try:
        n = os.cpu_count() or 4
    except Exception:
        n = 4
    return max(1, n - 1)


def make_conn() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute(f"PRAGMA threads={cpu_threads()}")
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def copy_query(conn: duckdb.DuckDBPyConnection, sql: str, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    escaped = out_csv.as_posix().replace("'", "''")
    conn.execute(f"COPY ({sql}) TO '{escaped}' (HEADER, DELIMITER ',')")


def qdf(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


def one_row(conn: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    df = qdf(conn, sql)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def normalize_code_text(s: str | None) -> str:
    if not s:
        return ""
    lines = [ln.rstrip() for ln in s.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def extract_student_editable_code(full_code: str, sk: SkeletonInfo) -> tuple[str, str]:
    """Strip evaluator prefix/suffix scaffolding from a saved snapshot."""
    if full_code is None:
        return "", "missing_full_code"

    code = full_code
    prefix = sk.prefixed_code or ""
    suffix = sk.suffixed_invisible_code or ""
    uneditable = sk.uneditable_code or ""
    prefix_stripped = False
    suffix_stripped = False

    if prefix:
        if code.startswith(prefix):
            code = code[len(prefix) :]
            prefix_stripped = True
        else:
            idx = code.find(prefix)
            if 0 <= idx <= 8:
                code = code[idx + len(prefix) :]
                prefix_stripped = True

    if suffix:
        if code.endswith(suffix):
            code = code[: -len(suffix)]
            suffix_stripped = True
        else:
            idx = code.rfind(suffix)
            if idx >= 0 and (len(code) - (idx + len(suffix))) <= 8:
                code = code[:idx]
                suffix_stripped = True

    if uneditable and code.startswith(uneditable):
        code = code[len(uneditable) :]

    if prefix or suffix:
        if prefix_stripped and suffix_stripped:
            status = "exact_prefix_suffix"
        elif prefix_stripped or suffix_stripped:
            status = "partial_prefix_suffix"
        else:
            status = "prefix_suffix_not_found"
    else:
        status = "no_scaffolding_config"

    return code, status


def meaningful_lines(s: str | None) -> list[str]:
    if not s:
        return []
    out: list[str] = []
    for raw in s.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        out.append(stripped)
    return out


def count_meaningful_lines(s: str | None) -> int:
    return len(meaningful_lines(s))


def meaningful_line_delta(student_code: str, skeleton_code: str) -> int:
    sc = Counter(meaningful_lines(student_code))
    kc = Counter(meaningful_lines(skeleton_code))
    extra = 0
    for line, cnt in sc.items():
        extra += max(0, cnt - kc.get(line, 0))
    return int(extra)


def classify_ast_syntax_error(code: str, ts_metrics: dict[str, Any]) -> dict[str, Any]:
    result = {
        "ast_parseable_recheck": None,
        "ast_error_class": None,
        "ast_error_msg": None,
        "ast_error_line": None,
        "ast_error_offset": None,
        "syntax_error_category": None,
        "syntax_intent_context": None,
    }
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ast.parse(code)
        result["ast_parseable_recheck"] = True
        return result
    except Exception as exc:  # noqa: BLE001
        result["ast_parseable_recheck"] = False
        result["ast_error_class"] = exc.__class__.__name__
        msg = getattr(exc, "msg", None) or str(exc)
        result["ast_error_msg"] = str(msg)[:500]
        lineno = getattr(exc, "lineno", None)
        offset = getattr(exc, "offset", None)
        if lineno is not None:
            result["ast_error_line"] = int(lineno)
        if offset is not None:
            result["ast_error_offset"] = int(offset)

        low = str(msg).lower()
        if isinstance(exc, (IndentationError, TabError)) or "indent" in low:
            cat = "Indentation error"
        elif any(k in low for k in ["never closed", "unmatched", "closing parenthesis", "was never closed"]):
            cat = "Missing delimiters"
        elif "expected ':'" in low or "expected an indented block" in low or "expected ':'" in low:
            cat = "Missing delimiters"
        elif any(k in low for k in ["invalid syntax", "cannot assign", "positional argument follows"]):
            cat = "Invalid syntax"
        else:
            cat = "Invalid syntax"
        result["syntax_error_category"] = cat

        ctx_candidates = [
            ("function signature", ts_metrics.get("ts_error_ctx_function_signature", 0)),
            ("loop", ts_metrics.get("ts_error_ctx_in_loop", 0)),
            ("conditional", ts_metrics.get("ts_error_ctx_in_conditional", 0)),
            ("function body", ts_metrics.get("ts_error_ctx_in_function", 0)),
            ("comprehension", ts_metrics.get("ts_error_ctx_in_comprehension", 0)),
            ("top level", ts_metrics.get("ts_error_ctx_top_level", 0)),
        ]
        ctx_candidates = [x for x in ctx_candidates if x[1] and x[1] > 0]
        if ctx_candidates:
            ctx_candidates.sort(key=lambda x: (-x[1], x[0]))
            result["syntax_intent_context"] = ctx_candidates[0][0]
        return result


def classify_runtime_type_from_case_output(output_text: str | None, summary: str | None) -> str | None:
    summary = (summary or "").strip()
    if summary == "Time Limit Exceeded":
        return "Timeout"
    if summary == "Not able to run":
        return "Not able to run"
    text = output_text or ""
    m = EXC_PATTERN.search(text)
    if m:
        return m.group(1)
    if summary == "Runtime Error":
        return "Runtime Error (unspecified)"
    return None


def first_failing_case(cases: list[dict[str, Any]]) -> tuple[int | None, dict[str, Any] | None]:
    for i, case in enumerate(cases, start=1):
        if not bool(case.get("passed")):
            return i, case
    return None, None


def normalize_ws(s: str | None) -> str:
    return " ".join((s or "").split())


def normalize_ws_case(s: str | None) -> str:
    return normalize_ws(s).lower()


def numbers_from_text(s: str | None) -> list[float]:
    vals: list[float] = []
    for tok in NUM_PATTERN.findall(s or ""):
        try:
            vals.append(float(tok))
        except Exception:
            continue
    return vals


def classify_wrong_output_subtype(
    summary: str | None,
    num_test_passed: int | None,
    test_case_count: int | None,
    first_fail_output: str | None,
    first_fail_expected: str | None,
) -> str | None:
    if (summary or "") != "Wrong Answer":
        return None

    out = first_fail_output or ""
    exp = first_fail_expected or ""
    if out != exp:
        if normalize_ws(out) == normalize_ws(exp) or normalize_ws_case(out) == normalize_ws_case(exp):
            return "Wrong output - formatting"
        nums_out = numbers_from_text(out)
        nums_exp = numbers_from_text(exp)
        if nums_out and nums_exp and len(nums_out) == len(nums_exp):
            diffs = [a - b for a, b in zip(nums_out, nums_exp)]
            if any(abs(d) == 1 for d in diffs) and all(abs(d) <= 1 for d in diffs):
                return "Wrong output - off-by-one/boundary"

    if (num_test_passed or 0) > 0 and (test_case_count or 0) > 0:
        return "Wrong output - partial correctness"
    return "Wrong output - logic/completely wrong"


def classify_skeleton_mod_status(row: pd.Series) -> str:
    is_python_question = row.get("is_python_question")
    if pd.notna(is_python_question) and (not bool(is_python_question)):
        return "Unsupported language (non-Python)"

    if bool(row.get("code_missing", False)):
        return "No code snapshot"

    extra_lines = int(row.get("meaningful_lines_beyond_skeleton", 0) or 0)
    total_meaningful = int(row.get("student_meaningful_lines", 0) or 0)
    has_skel = bool(row.get("has_skeleton_code_effective", False))
    ts_error_count = int(row.get("ts_error_count", 0) or 0)
    missing_tokens = int(row.get("ts_missing_token_count", 0) or 0)
    new_constructs = int(row.get("new_constructs_added", 0) or 0)
    removed_constructs = int(row.get("skeleton_constructs_removed_or_missing", 0) or 0)
    code_norm_equals_skeleton = bool(row.get("normalized_equals_skeleton", False))

    if total_meaningful == 0:
        return "Empty / trivial"
    if has_skel and (code_norm_equals_skeleton or (extra_lines <= 2 and new_constructs == 0 and removed_constructs == 0 and ts_error_count == 0)):
        return "Unmodified skeleton"
    if extra_lines < 3 and (not has_skel or (new_constructs == 0 and removed_constructs == 0)):
        return "Empty / trivial"

    if ts_error_count == 0 and missing_tokens == 0:
        return "Modified, structurally valid"

    # Distinguish localized syntax damage from globally broken code.
    error_density = (ts_error_count + missing_tokens) / max(1, int(row.get("ts_node_count", 1) or 1))
    if ts_error_count <= 3 and missing_tokens <= 5 and error_density < 0.08 and (new_constructs > 0 or extra_lines >= 3):
        return "Modified, partially broken"
    if (new_constructs > 0 or extra_lines >= 3) and (ts_error_count > 0 or missing_tokens > 0):
        return "Modified, fundamentally broken"
    return "Modified, partially broken"


def load_question_skeletons() -> tuple[pd.DataFrame, dict[tuple[str, int], SkeletonInfo]]:
    rows: list[dict[str, Any]] = []
    skeleton_map: dict[tuple[str, int], SkeletonInfo] = {}

    qmeta = pd.read_csv(ANALYSIS_DIR / "question_metadata.csv")
    qmeta = qmeta[["namespace", "problem_id", "question_title"]].copy()
    qmeta["problem_id"] = qmeta["problem_id"].astype(int)
    qtitle_map = {
        (str(r.namespace), int(r.problem_id)): (None if pd.isna(r.question_title) else str(r.question_title))
        for r in qmeta.itertuples(index=False)
    }

    analyzer = TsAnalyzer()

    for namespace_dir in sorted((ROOT / "problems").glob("ns_*")):
        if not namespace_dir.is_dir():
            continue
        namespace = namespace_dir.name
        for fp in sorted(namespace_dir.glob("*.json"), key=lambda p: int(p.stem)):
            try:
                problem_id = int(fp.stem)
            except Exception:
                continue
            try:
                obj = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                obj = {}
            langs = obj.get("allowed_languages") or []
            lang_codes = [str((x or {}).get("language") or "").strip() for x in langs if isinstance(x, dict)]
            primary_lang = next((x for x in lang_codes if x), "") or "unknown"
            py_lang = next((x for x in lang_codes if x.startswith("py")), None)
            lang_obj: dict[str, Any] | None = None
            if py_lang is not None:
                for x in langs:
                    if isinstance(x, dict) and str(x.get("language") or "") == py_lang:
                        lang_obj = x
                        break
            elif langs and isinstance(langs[0], dict):
                lang_obj = langs[0]

            skeleton_code = ""
            has_skeleton = False
            if lang_obj is not None:
                template = str(lang_obj.get("code_template") or "")
                if template.strip():
                    skeleton_code = template
                    has_skeleton = True
            is_python = bool(py_lang)
            if not is_python:
                primary_lang = primary_lang or "unknown"

            title = qtitle_map.get((namespace, problem_id))
            skeleton_norm = normalize_code_text(skeleton_code)
            skeleton_metrics = analyzer.analyze(skeleton_code if is_python else "") if is_python else {
                **{f"ts_count_{k}": 0 for k in CONSTRUCT_COLUMNS},
                **{f"ts_has_{k}": False for k in CONSTRUCT_COLUMNS},
                "ts_error_count": 0,
                "ts_missing_token_count": 0,
                "ts_node_count": 0,
                "ts_max_depth": 0,
                "ts_complexity_score": 0,
                "ts_error_ctx_top_level": 0,
                "ts_error_ctx_in_function": 0,
                "ts_error_ctx_function_signature": 0,
                "ts_error_ctx_in_loop": 0,
                "ts_error_ctx_in_conditional": 0,
                "ts_error_ctx_in_comprehension": 0,
                "ts_error_ctx_in_class": 0,
                "ts_error_ctx_other": 0,
                "ts_first_error_line": None,
                "ts_first_error_parent": None,
                "ts_top_error_parent_1": None,
                "ts_top_error_parent_1_count": 0,
                "ts_top_error_parent_2": None,
                "ts_top_error_parent_2_count": 0,
            }
            sk = SkeletonInfo(
                namespace=namespace,
                problem_id=problem_id,
                question_title=title,
                language=primary_lang,
                is_python=is_python,
                has_skeleton=has_skeleton,
                prefixed_code=str((lang_obj or {}).get("prefixed_code") or ""),
                uneditable_code=str((lang_obj or {}).get("uneditable_code") or ""),
                suffixed_invisible_code=str((lang_obj or {}).get("suffixed_invisible_code") or ""),
                skeleton_code=skeleton_code,
                skeleton_norm=skeleton_norm,
                skeleton_meaningful_lines=count_meaningful_lines(skeleton_code),
                skeleton_feature_hash=skeleton_metrics,
            )
            skeleton_map[(namespace, problem_id)] = sk
            rows.append(
                {
                    "namespace": namespace,
                    "problem_id": problem_id,
                    "question_title": title,
                    "primary_language": primary_lang,
                    "is_python_question": is_python,
                    "has_skeleton_code_effective": has_skeleton,
                    "prefixed_code_length": len(sk.prefixed_code),
                    "uneditable_code_length": len(sk.uneditable_code),
                    "suffixed_invisible_code_length": len(sk.suffixed_invisible_code),
                    "skeleton_code_length": len(skeleton_code),
                    "skeleton_meaningful_lines": sk.skeleton_meaningful_lines,
                    **{f"skeleton_{k}": v for k, v in skeleton_metrics.items()},
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(["namespace", "problem_id"], inplace=True)
    return df, skeleton_map


def setup_views(conn: duckdb.DuckDBPyConnection) -> None:
    print("[1/9] Building base DuckDB views and selection tables...")
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW fs_v AS
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          FileName AS final_submission_file,
          TRY_CAST("CompilationResult.score" AS DOUBLE) AS latest_submission_score,
          CAST(saved_code_events AS BIGINT) AS saved_code_events,
          CAST(test_run_events AS BIGINT) AS test_run_events,
          CAST(submission_events AS BIGINT) AS submission_events,
          CAST(total_events AS BIGINT) AS total_events,
          CAST(first_event_utc AS TIMESTAMP) AS first_event_utc,
          CAST(last_event_utc AS TIMESTAMP) AS last_event_utc,
          CAST(first_event_ist AS TIMESTAMP) AS first_event_ist,
          CAST(last_event_ist AS TIMESTAMP) AS last_event_ist
        FROM read_csv_auto('analysis/final_scores.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW schedule_v AS
        SELECT term, wave, namespace, start_time, end_time
        FROM read_csv_auto('analysis/schedule.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW qmeta_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          question_title,
          CAST(num_public_tests AS INTEGER) AS num_public_tests,
          CAST(num_private_tests AS INTEGER) AS num_private_tests
        FROM read_csv_auto('analysis/question_metadata.csv', header=true);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW timeline_v AS
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          student_id,
          CAST(timestamp_utc AS TIMESTAMP) AS timestamp_utc,
          CAST(timestamp_ist AS TIMESTAMP) AS timestamp_ist,
          event_type,
          evaluation_type,
          seconds_since_start,
          code_sha256,
          code_length,
          is_parseable,
          status,
          reason,
          summary,
          score,
          num_test_evaluated,
          num_test_passed,
          test_case_count
        FROM read_parquet('analysis/submission_timeline.parquet');
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW problem_max_score_v AS
        SELECT namespace, problem_id, COALESCE(MAX(latest_submission_score), 100.0) AS problem_max_score
        FROM fs_v
        GROUP BY namespace, problem_id;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW ns_submission_coverage_v AS
        SELECT namespace,
               SUM(submission_events) AS submission_events_sum,
               CASE WHEN SUM(submission_events) > 0 THEN TRUE ELSE FALSE END AS submission_positive_namespace
        FROM fs_v
        GROUP BY namespace;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW base_rows_v AS
        SELECT
          fs.namespace,
          fs.problem_id,
          fs.student_id,
          fs.final_submission_file,
          fs.latest_submission_score,
          fs.saved_code_events,
          fs.test_run_events,
          fs.submission_events,
          fs.total_events,
          fs.first_event_utc,
          fs.last_event_utc,
          fs.first_event_ist,
          fs.last_event_ist,
          date_diff('second', fs.first_event_utc, fs.last_event_utc) AS active_time_seconds,
          pm.problem_max_score,
          ns.submission_positive_namespace,
          CASE
            WHEN fs.submission_events > 0 AND abs(fs.latest_submission_score - pm.problem_max_score) < 1e-9 THEN 'Full pass'
            WHEN fs.submission_events > 0 AND fs.latest_submission_score > 0 AND fs.latest_submission_score < pm.problem_max_score THEN 'Partial pass'
            WHEN fs.submission_events > 0 AND fs.latest_submission_score = 0 THEN 'Submitted, zero'
            WHEN fs.submission_events = 0 AND fs.total_events > 0 THEN 'Active, never submitted'
            ELSE 'No activity'
          END AS outcome_category
        FROM fs_v fs
        JOIN problem_max_score_v pm USING (namespace, problem_id)
        JOIN ns_submission_coverage_v ns USING (namespace);
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW final_submission_rows_v AS
        SELECT
          b.namespace,
          b.problem_id,
          b.student_id,
          b.final_submission_file,
          COALESCE(
            try_strptime(regexp_extract(b.final_submission_file, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(regexp_extract(b.final_submission_file, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
          ) AS final_submission_ts
        FROM base_rows_v b
        WHERE b.submission_events > 0;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW final_submission_code_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            s.namespace,
            s.problem_id,
            s.student_id,
            s.final_submission_file,
            s.final_submission_ts,
            t.timestamp_utc AS selected_event_ts,
            t.timestamp_ist AS selected_event_ts_ist,
            t.event_type AS selected_event_type,
            t.evaluation_type AS selected_evaluation_type,
            t.code_sha256,
            t.code_length,
            t.is_parseable,
            t.status,
            t.reason,
            t.summary,
            t.score,
            t.num_test_evaluated,
            t.num_test_passed,
            t.test_case_count,
            ROW_NUMBER() OVER (
              PARTITION BY s.namespace, s.problem_id, s.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM final_submission_rows_v s
          JOIN timeline_v t
            ON t.namespace = s.namespace
           AND t.problem_id = s.problem_id
           AND t.student_id = s.student_id
          WHERE t.event_type = 'submission'
            AND t.evaluation_type = 'private'
            AND t.timestamp_utc = s.final_submission_ts
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW last_test_run_non_submit_submission_positive_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            b.namespace,
            b.problem_id,
            b.student_id,
            t.timestamp_utc AS selected_event_ts,
            t.timestamp_ist AS selected_event_ts_ist,
            t.event_type AS selected_event_type,
            t.evaluation_type AS selected_evaluation_type,
            t.code_sha256,
            t.code_length,
            t.is_parseable,
            t.status,
            t.reason,
            t.summary,
            t.score,
            t.num_test_evaluated,
            t.num_test_passed,
            t.test_case_count,
            ROW_NUMBER() OVER (
              PARTITION BY b.namespace, b.problem_id, b.student_id
              ORDER BY t.timestamp_utc DESC,
                       CASE WHEN t.evaluation_type = 'private' THEN 1 ELSE 0 END DESC,
                       COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM base_rows_v b
          JOIN timeline_v t
            ON t.namespace = b.namespace
           AND t.problem_id = b.problem_id
           AND t.student_id = b.student_id
          WHERE b.submission_events = 0
            AND b.submission_positive_namespace
            AND t.event_type = 'test_run'
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW best_public_test_run_zero_submission_ns_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            b.namespace,
            b.problem_id,
            b.student_id,
            t.timestamp_utc AS selected_event_ts,
            t.timestamp_ist AS selected_event_ts_ist,
            t.event_type AS selected_event_type,
            t.evaluation_type AS selected_evaluation_type,
            t.code_sha256,
            t.code_length,
            t.is_parseable,
            t.status,
            t.reason,
            t.summary,
            t.score,
            t.num_test_evaluated,
            t.num_test_passed,
            t.test_case_count,
            ROW_NUMBER() OVER (
              PARTITION BY b.namespace, b.problem_id, b.student_id
              ORDER BY COALESCE(t.num_test_passed, -1) DESC,
                       COALESCE(t.test_case_count, -1) DESC,
                       t.timestamp_utc DESC,
                       COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM base_rows_v b
          JOIN timeline_v t
            ON t.namespace = b.namespace
           AND t.problem_id = b.problem_id
           AND t.student_id = b.student_id
          WHERE b.submission_events = 0
            AND NOT b.submission_positive_namespace
            AND t.event_type = 'test_run'
            AND t.evaluation_type = 'public'
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW selected_snapshots_v AS
        SELECT
          b.*,
          s.term,
          s.wave,
          q.question_title,
          q.num_public_tests,
          q.num_private_tests,
          'Track A: submitters' AS track,
          'latest_submission' AS track_code_source,
          fs.selected_event_ts,
          fs.selected_event_ts_ist,
          fs.selected_event_type,
          fs.selected_evaluation_type,
          fs.code_sha256,
          fs.code_length,
          fs.is_parseable AS selected_is_parseable,
          fs.status AS selected_status,
          fs.reason AS selected_reason,
          fs.summary AS selected_summary,
          fs.score AS selected_score,
          fs.num_test_passed AS selected_num_test_passed,
          fs.test_case_count AS selected_test_case_count
        FROM base_rows_v b
        JOIN final_submission_code_v fs USING (namespace, problem_id, student_id)
        LEFT JOIN schedule_v s USING (namespace)
        LEFT JOIN qmeta_v q USING (namespace, problem_id)
        WHERE b.submission_events > 0
        UNION ALL
        SELECT
          b.*,
          s.term,
          s.wave,
          q.question_title,
          q.num_public_tests,
          q.num_private_tests,
          'Track A: non-submitters (submission-positive NS)' AS track,
          'last_test_run' AS track_code_source,
          n.selected_event_ts,
          n.selected_event_ts_ist,
          n.selected_event_type,
          n.selected_evaluation_type,
          n.code_sha256,
          n.code_length,
          n.is_parseable AS selected_is_parseable,
          n.status AS selected_status,
          n.reason AS selected_reason,
          n.summary AS selected_summary,
          n.score AS selected_score,
          n.num_test_passed AS selected_num_test_passed,
          n.test_case_count AS selected_test_case_count
        FROM base_rows_v b
        LEFT JOIN last_test_run_non_submit_submission_positive_v n USING (namespace, problem_id, student_id)
        LEFT JOIN schedule_v s USING (namespace)
        LEFT JOIN qmeta_v q USING (namespace, problem_id)
        WHERE b.submission_events = 0 AND b.submission_positive_namespace
        UNION ALL
        SELECT
          b.*,
          s.term,
          s.wave,
          q.question_title,
          q.num_public_tests,
          q.num_private_tests,
          'Track B: zero-submission namespaces' AS track,
          'best_public_test_run' AS track_code_source,
          z.selected_event_ts,
          z.selected_event_ts_ist,
          z.selected_event_type,
          z.selected_evaluation_type,
          z.code_sha256,
          z.code_length,
          z.is_parseable AS selected_is_parseable,
          z.status AS selected_status,
          z.reason AS selected_reason,
          z.summary AS selected_summary,
          z.score AS selected_score,
          z.num_test_passed AS selected_num_test_passed,
          z.test_case_count AS selected_test_case_count
        FROM base_rows_v b
        LEFT JOIN best_public_test_run_zero_submission_ns_v z USING (namespace, problem_id, student_id)
        LEFT JOIN schedule_v s USING (namespace)
        LEFT JOIN qmeta_v q USING (namespace, problem_id)
        WHERE b.submission_events = 0 AND NOT b.submission_positive_namespace;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW attempt_final_event_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            t.*,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY t.timestamp_utc DESC,
                       CASE t.event_type WHEN 'submission' THEN 3 WHEN 'test_run' THEN 2 ELSE 1 END DESC,
                       COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW best_public_test_run_all_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            t.*,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY COALESCE(t.num_test_passed, -1) DESC,
                       COALESCE(t.test_case_count, -1) DESC,
                       t.timestamp_utc DESC,
                       COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
          WHERE t.event_type = 'test_run' AND t.evaluation_type = 'public'
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW last_public_test_run_all_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            t.*,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
          WHERE t.event_type = 'test_run' AND t.evaluation_type = 'public'
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW last_parseable_before_final_v AS
        SELECT * EXCLUDE(rn)
        FROM (
          SELECT
            t.namespace,
            t.problem_id,
            t.student_id,
            t.timestamp_utc,
            t.event_type,
            t.evaluation_type,
            t.code_sha256,
            t.code_length,
            t.is_parseable,
            ROW_NUMBER() OVER (
              PARTITION BY t.namespace, t.problem_id, t.student_id
              ORDER BY t.timestamp_utc DESC, COALESCE(t.code_sha256, '') DESC
            ) AS rn
          FROM timeline_v t
          JOIN attempt_final_event_v f
            ON f.namespace = t.namespace
           AND f.problem_id = t.problem_id
           AND f.student_id = t.student_id
          WHERE COALESCE(t.is_parseable, FALSE) = TRUE
            AND t.timestamp_utc < f.timestamp_utc
        ) x
        WHERE rn = 1;
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW timeline_regression_agg_v AS
        SELECT
          t.namespace,
          t.problem_id,
          t.student_id,
          COUNT(*) AS timeline_events,
          COUNT(*) FILTER (WHERE t.event_type = 'test_run') AS test_run_events_timeline,
          COUNT(*) FILTER (WHERE t.event_type = 'saved_code') AS saved_code_events_timeline,
          COUNT(*) FILTER (WHERE t.event_type = 'submission') AS submission_events_timeline,
          MAX(CASE WHEN COALESCE(t.is_parseable, FALSE) THEN 1 ELSE 0 END) AS ever_parseable_any,
          MAX(CASE WHEN t.event_type = 'test_run' AND COALESCE(t.is_parseable, FALSE) THEN 1 ELSE 0 END) AS ever_parseable_test_run,
          MAX(CASE WHEN t.event_type = 'test_run' AND t.evaluation_type = 'public' THEN COALESCE(t.num_test_passed, 0) ELSE NULL END) AS max_public_num_test_passed,
          MAX(CASE WHEN t.event_type = 'test_run' AND t.evaluation_type = 'public' AND COALESCE(t.num_test_passed, 0) > 0 THEN 1 ELSE 0 END) AS any_public_test_pass,
          MAX(CASE WHEN t.event_type = 'test_run' AND t.evaluation_type = 'public' AND COALESCE(t.num_test_passed, 0) = COALESCE(t.test_case_count, -999) AND COALESCE(t.test_case_count, 0) > 0 THEN 1 ELSE 0 END) AS any_public_all_pass
        FROM timeline_v t
        GROUP BY t.namespace, t.problem_id, t.student_id;
        """
    )

    copy_query(
        conn,
        """
        SELECT *
        FROM selected_snapshots_v
        ORDER BY namespace, problem_id, student_id
        """,
        OUT_DIR / "selected_snapshot_rows_base.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          track,
          COUNT(*) AS rows,
          COUNT(*) FILTER (WHERE code_sha256 IS NOT NULL) AS rows_with_selected_hash,
          COUNT(*) FILTER (WHERE selected_event_ts IS NOT NULL) AS rows_with_selected_event,
          ROUND(100.0 * COUNT(*) FILTER (WHERE code_sha256 IS NOT NULL) / COUNT(*), 2) AS pct_with_selected_hash,
          COUNT(*) FILTER (WHERE outcome_category = 'Full pass') AS full_pass_rows,
          COUNT(*) FILTER (WHERE outcome_category = 'Partial pass') AS partial_pass_rows,
          COUNT(*) FILTER (WHERE outcome_category = 'Submitted, zero') AS submitted_zero_rows,
          COUNT(*) FILTER (WHERE outcome_category = 'Active, never submitted') AS active_never_submitted_rows,
          COUNT(*) FILTER (WHERE outcome_category = 'No activity') AS no_activity_rows
        FROM selected_snapshots_v
        GROUP BY track
        ORDER BY track
        """,
        OUT_DIR / "track_summary.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          COUNT(*) AS total_rows,
          COUNT(*) FILTER (WHERE code_sha256 IS NOT NULL) AS selected_code_rows,
          COUNT(*) FILTER (WHERE code_sha256 IS NULL) AS selected_code_rows_missing,
          ROUND(100.0 * COUNT(*) FILTER (WHERE code_sha256 IS NOT NULL) / COUNT(*), 2) AS pct_selected_code_rows,
          COUNT(*) FILTER (WHERE selected_event_ts IS NULL) AS selected_event_missing,
          COUNT(*) FILTER (WHERE outcome_category = 'No activity') AS no_activity_rows
        FROM selected_snapshots_v
        """,
        OUT_DIR / "code_selection_coverage.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          b.namespace,
          b.problem_id,
          b.student_id,
          b.track,
          b.term,
          b.wave,
          b.outcome_category,
          b.submission_positive_namespace,
          b.code_sha256 AS selected_track_code_sha256,
          b.selected_event_ts AS selected_track_event_ts,
          b.selected_is_parseable AS selected_track_is_parseable,
          f.timestamp_utc AS attempt_final_ts,
          f.event_type AS attempt_final_event_type,
          f.evaluation_type AS attempt_final_evaluation_type,
          f.code_sha256 AS attempt_final_code_sha256,
          f.code_length AS attempt_final_code_length,
          f.is_parseable AS attempt_final_is_parseable,
          f.summary AS attempt_final_summary,
          f.num_test_passed AS attempt_final_num_test_passed,
          f.test_case_count AS attempt_final_test_case_count,
          bp.timestamp_utc AS best_public_ts,
          bp.code_sha256 AS best_public_code_sha256,
          bp.code_length AS best_public_code_length,
          bp.summary AS best_public_summary,
          bp.num_test_passed AS best_public_num_test_passed,
          bp.test_case_count AS best_public_test_case_count,
          lp.timestamp_utc AS last_public_ts,
          lp.code_sha256 AS last_public_code_sha256,
          lp.num_test_passed AS last_public_num_test_passed,
          lp.test_case_count AS last_public_test_case_count,
          lpf.timestamp_utc AS last_parseable_before_final_ts,
          lpf.code_sha256 AS last_parseable_before_final_code_sha256,
          tra.timeline_events,
          tra.test_run_events_timeline,
          tra.saved_code_events_timeline,
          tra.submission_events_timeline,
          tra.ever_parseable_any,
          tra.ever_parseable_test_run,
          tra.max_public_num_test_passed,
          tra.any_public_test_pass,
          tra.any_public_all_pass
        FROM selected_snapshots_v b
        LEFT JOIN attempt_final_event_v f USING (namespace, problem_id, student_id)
        LEFT JOIN best_public_test_run_all_v bp USING (namespace, problem_id, student_id)
        LEFT JOIN last_public_test_run_all_v lp USING (namespace, problem_id, student_id)
        LEFT JOIN last_parseable_before_final_v lpf USING (namespace, problem_id, student_id)
        LEFT JOIN timeline_regression_agg_v tra USING (namespace, problem_id, student_id)
        ORDER BY b.namespace, b.problem_id, b.student_id
        """,
        OUT_DIR / "regression_inputs.csv",
    )

    copy_query(
        conn,
        """
        SELECT
          bp.namespace,
          bp.problem_id,
          bp.student_id,
          bp.timestamp_utc AS best_public_ts,
          bp.code_sha256 AS best_public_code_sha256,
          bp.code_length AS best_public_code_length,
          bp.summary AS best_public_summary,
          bp.num_test_passed AS best_public_num_test_passed,
          bp.test_case_count AS best_public_test_case_count,
          bp.status AS best_public_status,
          bp.reason AS best_public_reason
        FROM best_public_test_run_all_v bp
        ORDER BY bp.namespace, bp.problem_id, bp.student_id
        """,
        OUT_DIR / "best_public_test_run_rows_base.csv",
    )


def write_question_skeleton_outputs(skel_df: pd.DataFrame) -> None:
    print("[2/9] Writing question skeleton metadata...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    skel_df.to_csv(OUT_DIR / "question_skeletons.csv", index=False)
    if not skel_df.empty:
        summary = (
            skel_df.groupby(["primary_language", "is_python_question"], dropna=False)
            .agg(
                questions=("problem_id", "count"),
                with_skeleton=("has_skeleton_code_effective", "sum"),
            )
            .reset_index()
        )
        summary.to_csv(OUT_DIR / "question_skeletons_language_summary.csv", index=False)


def _fetch_df_chunks(
    cursor: duckdb.DuckDBPyConnection,
    *,
    vectors_per_chunk: int = 50,
) -> Iterable[pd.DataFrame]:
    if hasattr(cursor, "fetch_df_chunk"):
        while True:
            chunk = cursor.fetch_df_chunk(vectors_per_chunk=vectors_per_chunk)
            if chunk is None or chunk.empty:
                break
            yield chunk
        return

    # Fallback for older APIs
    cols = [d[0] for d in cursor.description]
    while True:
        rows = cursor.fetchmany(50_000)
        if not rows:
            break
        yield pd.DataFrame(rows, columns=cols)


def build_hash_feature_table(
    conn: duckdb.DuckDBPyConnection,
    python_selected_rows: pd.DataFrame,
    regression_inputs: pd.DataFrame,
) -> pd.DataFrame:
    print("[3/9] Parsing tree-sitter features for required Python code hashes...")
    analyzer = TsAnalyzer()

    # Hashes needed for selected classification snapshots + regression boundary snapshots.
    hash_cols = [
        "code_sha256",
    ]
    needed_hashes: set[str] = set()
    if not python_selected_rows.empty:
        needed_hashes.update(x for x in python_selected_rows["code_sha256"].dropna().astype(str).tolist() if x)

    if not regression_inputs.empty:
        py_reg = regression_inputs[regression_inputs["is_python_question"] == True]  # noqa: E712
        for col in [
            "selected_track_code_sha256",
            "attempt_final_code_sha256",
            "best_public_code_sha256",
            "last_parseable_before_final_code_sha256",
        ]:
            if col in py_reg.columns:
                needed_hashes.update(x for x in py_reg[col].dropna().astype(str).tolist() if x)

    if not needed_hashes:
        out = pd.DataFrame(columns=["code_sha256"])
        out.to_csv(OUT_DIR / "hash_tree_sitter_features.csv", index=False)
        return out

    cache_path = OUT_DIR / "hash_tree_sitter_features.csv"
    cached_df = pd.DataFrame()
    if cache_path.exists():
        try:
            cached_df = pd.read_csv(cache_path, low_memory=False)
            if "code_sha256" in cached_df.columns:
                cached_df["code_sha256"] = cached_df["code_sha256"].astype(str)
        except Exception:
            cached_df = pd.DataFrame()
    cached_hashes = set(cached_df["code_sha256"].tolist()) if (not cached_df.empty and "code_sha256" in cached_df.columns) else set()
    missing_hashes = sorted(needed_hashes - cached_hashes)
    if not missing_hashes:
        print(f"  reusing cached hash features for {len(cached_hashes):,} hashes")
        out = cached_df[cached_df["code_sha256"].isin(needed_hashes)].copy()
        out.sort_values("code_sha256", inplace=True)
        out.to_csv(cache_path, index=False)
        return out

    hashes_df = pd.DataFrame({"code_sha256": missing_hashes})
    conn.register("hashes_to_parse_df", hashes_df)
    conn.execute("CREATE OR REPLACE TEMP VIEW hashes_to_parse_v AS SELECT DISTINCT code_sha256 FROM hashes_to_parse_df")

    total = int(one_row(conn, "SELECT COUNT(*) AS n FROM hashes_to_parse_v").get("n", 0) or 0)
    if cached_hashes:
        print(
            f"  hashes to parse (python): {total:,} missing of {len(needed_hashes):,} total "
            f"(cache has {len(cached_hashes):,})"
        )
    else:
        print(f"  hashes to parse (python): {total:,}")

    cursor = conn.execute(
        """
        SELECT h.code_sha256, c.code_snapshot
        FROM hashes_to_parse_v h
        JOIN read_parquet('analysis/code_snapshots.parquet') c USING (code_sha256)
        ORDER BY h.code_sha256
        """
    )

    rows: list[dict[str, Any]] = []
    parsed = 0
    for chunk in _fetch_df_chunks(cursor, vectors_per_chunk=40):
        for rec in chunk.itertuples(index=False):
            code_sha256 = rec.code_sha256
            code = rec.code_snapshot if isinstance(rec.code_snapshot, str) else ("" if pd.isna(rec.code_snapshot) else str(rec.code_snapshot))
            metrics = analyzer.analyze(code)
            rows.append({"code_sha256": code_sha256, **metrics})
            parsed += 1
        if parsed and parsed % 25_000 == 0:
            print(f"  parsed {parsed:,}/{total:,} hashes...")

    feat_df = pd.DataFrame(rows)
    if not cached_df.empty:
        feat_df = pd.concat([cached_df, feat_df], ignore_index=True)
        feat_df = feat_df.drop_duplicates(subset=["code_sha256"], keep="last")
    if feat_df.empty:
        feat_df = pd.DataFrame(columns=["code_sha256"])
    feat_df = feat_df[feat_df["code_sha256"].isin(needed_hashes)].copy()
    feat_df.sort_values("code_sha256", inplace=True)
    feat_df.to_csv(OUT_DIR / "hash_tree_sitter_features.csv", index=False)
    print(f"  wrote hash tree-sitter features for {len(feat_df):,} hashes")
    return feat_df


def build_selected_snapshot_taxonomy(
    conn: duckdb.DuckDBPyConnection,
    skeleton_df: pd.DataFrame,
    skeleton_map: dict[tuple[str, int], SkeletonInfo],
    hash_features: pd.DataFrame,
) -> pd.DataFrame:
    print("[4/9] Building selected-snapshot tree-sitter + skeleton taxonomy rows...")
    base = pd.read_csv(OUT_DIR / "selected_snapshot_rows_base.csv", low_memory=False)
    if base.empty:
        out = base.copy()
        out.to_csv(OUT_DIR / "selected_snapshot_taxonomy_rows.csv", index=False)
        return out

    base["problem_id"] = base["problem_id"].astype(int)
    skeleton_df2 = skeleton_df.copy()
    skeleton_df2["problem_id"] = skeleton_df2["problem_id"].astype(int)
    df = base.merge(skeleton_df2, on=["namespace", "problem_id"], how="left")
    if "question_title" not in df.columns and "question_title_x" in df.columns:
        if "question_title_y" in df.columns:
            df["question_title"] = df["question_title_x"].combine_first(df["question_title_y"])
            df.drop(columns=["question_title_x", "question_title_y"], inplace=True)
        else:
            df.rename(columns={"question_title_x": "question_title"}, inplace=True)

    # Do not reuse hash-level tree-sitter features here: code snapshots include
    # evaluator-injected scaffolding. We recompute row-level metrics on the
    # extracted student-editable region below.

    # Bring code text only for selected rows (chunked) and derive row-level skeleton comparisons.
    selected_hashes = sorted({x for x in df["code_sha256"].dropna().astype(str).tolist() if x})
    code_map: dict[str, str] = {}
    if selected_hashes:
        conn.register("selected_hashes_df", pd.DataFrame({"code_sha256": selected_hashes}))
        conn.execute(
            "CREATE OR REPLACE TEMP VIEW selected_hashes_v AS SELECT DISTINCT code_sha256 FROM selected_hashes_df"
        )
        cursor = conn.execute(
            """
            SELECT c.code_sha256, c.code_snapshot
            FROM selected_hashes_v s
            JOIN read_parquet('analysis/code_snapshots.parquet') c USING (code_sha256)
            ORDER BY c.code_sha256
            """
        )
        loaded = 0
        for chunk in _fetch_df_chunks(cursor, vectors_per_chunk=40):
            for rec in chunk.itertuples(index=False):
                code_map[str(rec.code_sha256)] = rec.code_snapshot if isinstance(rec.code_snapshot, str) else ""
                loaded += 1
            if loaded and loaded % 25_000 == 0:
                print(f"  loaded {loaded:,}/{len(selected_hashes):,} selected code snapshots...")

    row_extra: list[dict[str, Any]] = []
    ts_analyzer = TsAnalyzer()
    for rec in df.itertuples(index=False):
        key = (str(rec.namespace), int(rec.problem_id))
        sk = skeleton_map.get(key)
        code = code_map.get(str(rec.code_sha256), "") if pd.notna(rec.code_sha256) else ""
        code_missing = pd.isna(rec.code_sha256) or str(rec.code_sha256) not in code_map
        student_code = code
        scaffold_strip_status = "code_missing"
        if (sk is not None) and (not code_missing):
            student_code, scaffold_strip_status = extract_student_editable_code(code, sk)
        code_norm = normalize_code_text(student_code)

        info: dict[str, Any] = {
            "namespace": rec.namespace,
            "problem_id": int(rec.problem_id),
            "student_id": rec.student_id,
            "code_missing": bool(code_missing),
            "selected_code_length_actual": (len(code) if not code_missing else None),
            "student_editable_code_length": (len(student_code) if not code_missing else None),
            "scaffold_strip_status": scaffold_strip_status,
            "student_meaningful_lines": (count_meaningful_lines(student_code) if not code_missing else None),
            "normalized_equals_skeleton": None,
            "meaningful_lines_beyond_skeleton": None,
            "new_constructs_added": None,
            "skeleton_constructs_removed_or_missing": None,
            "added_regions_structurally_coherent": None,
            "ast_parseable_recheck": None,
            "ast_error_class": None,
            "ast_error_msg": None,
            "ast_error_line": None,
            "ast_error_offset": None,
            "syntax_error_category": None,
            "syntax_intent_context": None,
            **{f"ts_count_{k}": None for k in CONSTRUCT_COLUMNS},
            **{f"ts_has_{k}": None for k in CONSTRUCT_COLUMNS},
            "ts_error_count": None,
            "ts_missing_token_count": None,
            "ts_node_count": None,
            "ts_max_depth": None,
            "ts_complexity_score": None,
            "ts_error_ctx_top_level": None,
            "ts_error_ctx_in_function": None,
            "ts_error_ctx_function_signature": None,
            "ts_error_ctx_in_loop": None,
            "ts_error_ctx_in_conditional": None,
            "ts_error_ctx_in_comprehension": None,
            "ts_error_ctx_in_class": None,
            "ts_error_ctx_other": None,
            "ts_first_error_line": None,
            "ts_first_error_parent": None,
            "ts_top_error_parent_1": None,
            "ts_top_error_parent_1_count": None,
            "ts_top_error_parent_2": None,
            "ts_top_error_parent_2_count": None,
        }

        if sk is None:
            info["is_python_question"] = None
            info["primary_language"] = None
            row_extra.append(info)
            continue

        info["is_python_question"] = bool(sk.is_python)
        info["primary_language"] = sk.language
        if code_missing:
            row_extra.append(info)
            continue

        if sk.is_python:
            ts_metrics = ts_analyzer.analyze(student_code)
            info.update(ts_metrics)
            info["normalized_equals_skeleton"] = bool(code_norm == sk.skeleton_norm)
            info["meaningful_lines_beyond_skeleton"] = meaningful_line_delta(student_code, sk.skeleton_code)

            # Structural distance from skeleton uses tree-sitter construct counts.
            new_constructs = 0
            removed_constructs = 0
            for construct in CONSTRUCT_COLUMNS:
                student_count = int(ts_metrics.get(f"ts_count_{construct}", 0) or 0)
                sk_count = int(sk.skeleton_feature_hash.get(f"ts_count_{construct}", 0) or 0)
                new_constructs += max(0, student_count - sk_count)
                removed_constructs += max(0, sk_count - student_count)
            info["new_constructs_added"] = int(new_constructs)
            info["skeleton_constructs_removed_or_missing"] = int(removed_constructs)

            ts_error_count = ts_metrics.get("ts_error_count")
            ts_missing = ts_metrics.get("ts_missing_token_count")
            info["added_regions_structurally_coherent"] = bool(
                (new_constructs > 0)
                and (0 if pd.isna(ts_error_count) else int(ts_error_count)) == 0
                and (0 if pd.isna(ts_missing) else int(ts_missing)) == 0
            )

            ast_info = classify_ast_syntax_error(student_code, info | {
                "ts_error_ctx_function_signature": ts_metrics.get("ts_error_ctx_function_signature", 0),
                "ts_error_ctx_in_loop": ts_metrics.get("ts_error_ctx_in_loop", 0),
                "ts_error_ctx_in_conditional": ts_metrics.get("ts_error_ctx_in_conditional", 0),
                "ts_error_ctx_in_function": ts_metrics.get("ts_error_ctx_in_function", 0),
                "ts_error_ctx_in_comprehension": ts_metrics.get("ts_error_ctx_in_comprehension", 0),
                "ts_error_ctx_top_level": ts_metrics.get("ts_error_ctx_top_level", 0),
            })
            info.update(ast_info)
        else:
            # Non-Python rows are preserved but excluded from Python syntax/tree logic.
            info["normalized_equals_skeleton"] = None
            info["meaningful_lines_beyond_skeleton"] = None
            info["new_constructs_added"] = None
            info["skeleton_constructs_removed_or_missing"] = None
            info["added_regions_structurally_coherent"] = None

        row_extra.append(info)

    extra_df = pd.DataFrame(row_extra)
    out = df.merge(extra_df, on=["namespace", "problem_id", "student_id"], how="left", suffixes=("", "_extra"))

    # Prefer the explicit row-level language flags from skeleton map.
    if "is_python_question_extra" in out.columns:
        out["is_python_question"] = out["is_python_question_extra"].combine_first(out.get("is_python_question"))
        out.drop(columns=["is_python_question_extra"], inplace=True)
    if "primary_language_extra" in out.columns:
        out["primary_language"] = out["primary_language_extra"].combine_first(out.get("primary_language"))
        out.drop(columns=["primary_language_extra"], inplace=True)

    out["skeleton_modification_status"] = out.apply(classify_skeleton_mod_status, axis=1)
    out["ts_has_any_error"] = (out["ts_error_count"].fillna(0) > 0) | (out["ts_missing_token_count"].fillna(0) > 0)
    out["selected_tree_sitter_parseable"] = ~out["ts_has_any_error"]

    out.sort_values(["namespace", "problem_id", "student_id"], inplace=True)
    out.to_csv(OUT_DIR / "selected_snapshot_taxonomy_rows.csv", index=False)

    (
        out.groupby(["track", "scaffold_strip_status"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["track", "rows"], ascending=[True, False])
        .to_csv(OUT_DIR / "scaffold_strip_status_summary.csv", index=False)
    )

    # Summaries
    (
        out.groupby(["track", "skeleton_modification_status"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["track", "rows"], ascending=[True, False])
        .to_csv(OUT_DIR / "skeleton_modification_status_summary.csv", index=False)
    )

    py_nonparse = out[(out["is_python_question"] == True) & (out["ast_parseable_recheck"] == False)]  # noqa: E712
    if py_nonparse.empty:
        pd.DataFrame(columns=["track", "syntax_error_category", "syntax_intent_context", "rows"]).to_csv(
            OUT_DIR / "syntax_error_taxonomy_summary.csv", index=False
        )
    else:
        (
            py_nonparse.groupby(["track", "syntax_error_category", "syntax_intent_context"], dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values(["track", "rows"], ascending=[True, False])
            .to_csv(OUT_DIR / "syntax_error_taxonomy_summary.csv", index=False)
        )
    py_nonparse.to_csv(OUT_DIR / "syntax_error_taxonomy_rows.csv", index=False)

    error_loc = out[out["is_python_question"] == True].copy()  # noqa: E712
    if error_loc.empty:
        pd.DataFrame().to_csv(OUT_DIR / "tree_sitter_error_location_summary.csv", index=False)
    else:
        loc_cols = [
            "track",
            "term",
            "ts_error_ctx_top_level",
            "ts_error_ctx_in_function",
            "ts_error_ctx_function_signature",
            "ts_error_ctx_in_loop",
            "ts_error_ctx_in_conditional",
            "ts_error_ctx_in_comprehension",
            "ts_error_ctx_in_class",
            "ts_error_ctx_other",
            "ts_error_count",
            "ts_missing_token_count",
        ]
        keep = [c for c in loc_cols if c in error_loc.columns]
        loc_summary = (
            error_loc.groupby(["track"], dropna=False)
            .agg(
                python_rows=("student_id", "count"),
                rows_with_errors=("ts_has_any_error", "sum"),
                total_error_nodes=("ts_error_count", "sum"),
                total_missing_tokens=("ts_missing_token_count", "sum"),
                error_ctx_top_level=("ts_error_ctx_top_level", "sum"),
                error_ctx_in_function=("ts_error_ctx_in_function", "sum"),
                error_ctx_function_signature=("ts_error_ctx_function_signature", "sum"),
                error_ctx_in_loop=("ts_error_ctx_in_loop", "sum"),
                error_ctx_in_conditional=("ts_error_ctx_in_conditional", "sum"),
                error_ctx_in_comprehension=("ts_error_ctx_in_comprehension", "sum"),
                error_ctx_in_class=("ts_error_ctx_in_class", "sum"),
                error_ctx_other=("ts_error_ctx_other", "sum"),
            )
            .reset_index()
        )
        loc_summary.to_csv(OUT_DIR / "tree_sitter_error_location_summary.csv", index=False)

    # Structural inventory (fractions of selected snapshots using construct)
    py_rows = out[out["is_python_question"] == True].copy()  # noqa: E712
    if py_rows.empty:
        pd.DataFrame(columns=["scope", "construct", "rows", "rows_with_construct", "pct_rows_with_construct"]).to_csv(
            OUT_DIR / "structural_inventory_by_track.csv", index=False
        )
    else:
        track_rows: list[dict[str, Any]] = []
        for track, g in py_rows.groupby("track", dropna=False):
            n = len(g)
            for construct in CONSTRUCT_COLUMNS:
                col = f"ts_has_{construct}"
                yes = int(g[col].fillna(False).astype(bool).sum()) if col in g.columns else 0
                track_rows.append(
                    {
                        "track": track,
                        "construct": construct,
                        "rows": n,
                        "rows_with_construct": yes,
                        "pct_rows_with_construct": round(100.0 * yes / n, 2) if n else np.nan,
                    }
                )
        pd.DataFrame(track_rows).sort_values(["track", "construct"]).to_csv(
            OUT_DIR / "structural_inventory_by_track.csv", index=False
        )

        term_rows: list[dict[str, Any]] = []
        for (term, track), g in py_rows.groupby(["term", "track"], dropna=False):
            n = len(g)
            for construct in CONSTRUCT_COLUMNS:
                col = f"ts_has_{construct}"
                yes = int(g[col].fillna(False).astype(bool).sum()) if col in g.columns else 0
                term_rows.append(
                    {
                        "term": term,
                        "track": track,
                        "construct": construct,
                        "rows": n,
                        "rows_with_construct": yes,
                        "pct_rows_with_construct": round(100.0 * yes / n, 2) if n else np.nan,
                    }
                )
        pd.DataFrame(term_rows).sort_values(["term", "track", "construct"]).to_csv(
            OUT_DIR / "structural_inventory_by_term.csv", index=False
        )

        q_rows: list[dict[str, Any]] = []
        for keys, g in py_rows.groupby(["namespace", "problem_id", "question_title", "track"], dropna=False):
            namespace, problem_id, title, track = keys
            n = len(g)
            for construct in CONSTRUCT_COLUMNS:
                col = f"ts_has_{construct}"
                yes = int(g[col].fillna(False).astype(bool).sum()) if col in g.columns else 0
                q_rows.append(
                    {
                        "namespace": namespace,
                        "problem_id": problem_id,
                        "question_title": title,
                        "track": track,
                        "construct": construct,
                        "rows": n,
                        "rows_with_construct": yes,
                        "pct_rows_with_construct": round(100.0 * yes / n, 2) if n else np.nan,
                    }
                )
        pd.DataFrame(q_rows).sort_values(["namespace", "problem_id", "track", "construct"]).to_csv(
            OUT_DIR / "structural_inventory_by_question.csv", index=False
        )

    return out


def parse_test_case_results(compilation_result: str | None) -> list[dict[str, Any]]:
    if not compilation_result:
        return []
    try:
        obj = json.loads(compilation_result)
    except Exception:
        return []
    tcr = obj.get("test_case_results")
    return tcr if isinstance(tcr, list) else []


def build_best_public_failure_taxonomy(conn: duckdb.DuckDBPyConnection, selected_rows: pd.DataFrame) -> pd.DataFrame:
    print("[5/9] Extracting best-public test_run case results and classifying runtime/wrong-output failures...")
    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW raw_public_test_run_events_v AS
        SELECT
          Namespace AS namespace,
          CAST(ProblemID AS INTEGER) AS problem_id,
          StudentID AS student_id,
          FileName AS file_name,
          COALESCE(
            try_strptime(regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1), '%Y-%m-%dT%H:%M:%SZ')
          ) AS event_ts,
          CompilationResult
        FROM read_json(
          'submissions/*.json',
          format='newline_delimited',
          columns={
            Namespace:'VARCHAR',
            ProblemID:'VARCHAR',
            StudentID:'VARCHAR',
            FileName:'VARCHAR',
            EvaluationType:'VARCHAR',
            CompilationResult:'VARCHAR'
          }
        )
        WHERE FileName IS NOT NULL
          AND FileName <> ''
          AND regexp_extract(FileName, '/(test_run)/', 1) = 'test_run'
          AND json_valid(CompilationResult)
          AND EvaluationType = 'public';
        """
    )

    # Join best public rows to raw compilation results (timestamp-based; tie-broken by latest file name if duplicated).
    cursor = conn.execute(
        """
        SELECT
          b.namespace,
          b.problem_id,
          b.student_id,
          s.track,
          s.term,
          s.wave,
          s.question_title,
          s.outcome_category,
          s.submission_positive_namespace,
          b.best_public_ts,
          b.best_public_code_sha256,
          b.best_public_summary,
          b.best_public_status,
          b.best_public_reason,
          b.best_public_num_test_passed,
          b.best_public_test_case_count,
          r.file_name AS best_public_file_name,
          r.CompilationResult AS best_public_compilation_result
        FROM read_csv_auto('analysis/error_taxonomy/best_public_test_run_rows_base.csv', header=true) b
        LEFT JOIN raw_public_test_run_events_v r
          ON r.namespace = b.namespace
         AND r.problem_id = b.problem_id
         AND r.student_id = b.student_id
         AND r.event_ts = CAST(b.best_public_ts AS TIMESTAMP)
        LEFT JOIN read_csv_auto('analysis/error_taxonomy/selected_snapshot_taxonomy_rows.csv', header=true) s
          ON s.namespace = b.namespace
         AND CAST(s.problem_id AS INTEGER) = CAST(b.problem_id AS INTEGER)
         AND s.student_id = b.student_id
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY b.namespace, b.problem_id, b.student_id
          ORDER BY r.file_name DESC NULLS LAST
        ) = 1
        ORDER BY b.namespace, CAST(b.problem_id AS INTEGER), b.student_id
        """
    )

    rows: list[dict[str, Any]] = []
    processed = 0
    for chunk in _fetch_df_chunks(cursor, vectors_per_chunk=20):
        for rec in chunk.itertuples(index=False):
            tcr = parse_test_case_results(getattr(rec, "best_public_compilation_result", None))
            n_cases = len(tcr)
            n_passed = sum(1 for c in tcr if bool(c.get("passed")))
            fail_idx, fail_case = first_failing_case(tcr)
            fail_reason = (str(fail_case.get("reason")) if fail_case is not None and fail_case.get("reason") is not None else None)
            fail_output = (str(fail_case.get("output")) if fail_case is not None and fail_case.get("output") is not None else None)
            fail_expected = (
                str(fail_case.get("expected_output"))
                if fail_case is not None and fail_case.get("expected_output") is not None
                else None
            )
            summary = None if pd.isna(rec.best_public_summary) else str(rec.best_public_summary)
            runtime_type = classify_runtime_type_from_case_output(fail_output, summary)
            wrong_subtype = classify_wrong_output_subtype(
                summary,
                None if pd.isna(rec.best_public_num_test_passed) else int(rec.best_public_num_test_passed),
                None if pd.isna(rec.best_public_test_case_count) else int(rec.best_public_test_case_count),
                fail_output,
                fail_expected,
            )

            if summary == "All Cases Passed":
                primary_failure_mode = "Best public full pass"
            elif summary == "Runtime Error":
                primary_failure_mode = f"Runtime error - {runtime_type or 'unknown'}"
            elif summary == "Wrong Answer":
                primary_failure_mode = wrong_subtype or "Wrong output - unknown"
            elif summary == "Time Limit Exceeded":
                primary_failure_mode = "Timeout"
            elif summary == "Not able to run":
                primary_failure_mode = "Not able to run"
            elif summary is None:
                primary_failure_mode = "No best public test_run"
            else:
                primary_failure_mode = f"Other - {summary}"

            rows.append(
                {
                    "namespace": rec.namespace,
                    "problem_id": int(rec.problem_id),
                    "student_id": rec.student_id,
                    "track": rec.track,
                    "term": rec.term,
                    "wave": rec.wave,
                    "question_title": rec.question_title,
                    "outcome_category": rec.outcome_category,
                    "submission_positive_namespace": rec.submission_positive_namespace,
                    "best_public_ts": rec.best_public_ts,
                    "best_public_code_sha256": rec.best_public_code_sha256,
                    "best_public_file_name": rec.best_public_file_name,
                    "best_public_summary": summary,
                    "best_public_status": (None if pd.isna(rec.best_public_status) else int(rec.best_public_status)),
                    "best_public_num_test_passed": (None if pd.isna(rec.best_public_num_test_passed) else int(rec.best_public_num_test_passed)),
                    "best_public_test_case_count": (None if pd.isna(rec.best_public_test_case_count) else int(rec.best_public_test_case_count)),
                    "best_public_tcr_case_count_extracted": n_cases,
                    "best_public_tcr_num_passed_extracted": n_passed,
                    "best_public_first_fail_index": fail_idx,
                    "best_public_first_fail_reason": fail_reason,
                    "best_public_first_fail_output": fail_output,
                    "best_public_first_fail_expected_output": fail_expected,
                    "best_public_runtime_error_type": runtime_type,
                    "best_public_wrong_output_subtype": wrong_subtype,
                    "best_public_primary_failure_mode": primary_failure_mode,
                }
            )
            processed += 1
        if processed and processed % 25_000 == 0:
            print(f"  processed {processed:,} best-public rows...")

    out = pd.DataFrame(rows)
    if out.empty:
        out = pd.DataFrame(columns=["namespace", "problem_id", "student_id"])
    out.sort_values(["namespace", "problem_id", "student_id"], inplace=True)
    out.to_csv(OUT_DIR / "best_public_test_run_classification_rows.csv", index=False)

    # Runtime summary
    runtime_df = out[out["best_public_summary"] == "Runtime Error"].copy() if not out.empty else out.copy()
    if runtime_df.empty:
        pd.DataFrame(columns=["track", "best_public_runtime_error_type", "rows"]).to_csv(
            OUT_DIR / "runtime_error_type_summary.csv", index=False
        )
    else:
        (
            runtime_df.groupby(["track", "best_public_runtime_error_type"], dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values(["track", "rows"], ascending=[True, False])
            .to_csv(OUT_DIR / "runtime_error_type_summary.csv", index=False)
        )

    # Wrong-output summary + sample for future LLM/manual review
    wrong_df = out[out["best_public_summary"] == "Wrong Answer"].copy() if not out.empty else out.copy()
    if wrong_df.empty:
        pd.DataFrame(columns=["track", "best_public_wrong_output_subtype", "rows"]).to_csv(
            OUT_DIR / "wrong_output_subtype_summary.csv", index=False
        )
        pd.DataFrame(columns=out.columns).to_csv(OUT_DIR / "wrong_output_llm_review_sample.csv", index=False)
    else:
        (
            wrong_df.groupby(["track", "best_public_wrong_output_subtype"], dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values(["track", "rows"], ascending=[True, False])
            .to_csv(OUT_DIR / "wrong_output_subtype_summary.csv", index=False)
        )
        sample_parts: list[pd.DataFrame] = []
        for _, gq in wrong_df.groupby(["namespace", "problem_id"], dropna=False):
            sample_parts.append(gq.sample(n=min(40, len(gq)), random_state=42))
        sample_df = pd.concat(sample_parts, ignore_index=True) if sample_parts else wrong_df.head(0)
        sample_df.to_csv(OUT_DIR / "wrong_output_llm_review_sample.csv", index=False)

    # Public failure mode summary (all best-public rows)
    (
        out.groupby(["track", "best_public_primary_failure_mode"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["track", "rows"], ascending=[True, False])
        .to_csv(OUT_DIR / "best_public_primary_failure_mode_summary.csv", index=False)
    )

    return out


def build_regression_outputs(
    selected_rows: pd.DataFrame,
    regression_inputs_path: Path,
    hash_features: pd.DataFrame,
) -> pd.DataFrame:
    print("[6/9] Computing parseability and structural regression flags...")
    reg = pd.read_csv(regression_inputs_path)
    if reg.empty:
        reg.to_csv(OUT_DIR / "regression_rows.csv", index=False)
        return reg

    # Join language flags from selected rows.
    lang_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "is_python_question",
        "primary_language",
        "track",
        "term",
        "wave",
        "question_title",
    ]
    lang_df = selected_rows[lang_cols].drop_duplicates().copy()
    reg["problem_id"] = reg["problem_id"].astype(int)
    lang_df["problem_id"] = lang_df["problem_id"].astype(int)
    reg = reg.merge(lang_df, on=["namespace", "problem_id", "student_id"], how="left", suffixes=("", "_sel"))

    if not hash_features.empty:
        feat = hash_features.copy()
        keep = ["code_sha256", "ts_complexity_score", "ts_error_count", "ts_missing_token_count"]
        feat = feat[[c for c in keep if c in feat.columns]]
        reg = reg.merge(
            feat.rename(columns={
                "code_sha256": "attempt_final_code_sha256",
                "ts_complexity_score": "attempt_final_ts_complexity_score",
                "ts_error_count": "attempt_final_ts_error_count",
                "ts_missing_token_count": "attempt_final_ts_missing_token_count",
            }),
            on="attempt_final_code_sha256",
            how="left",
        )
        reg = reg.merge(
            feat.rename(columns={
                "code_sha256": "best_public_code_sha256",
                "ts_complexity_score": "best_public_ts_complexity_score",
                "ts_error_count": "best_public_ts_error_count",
                "ts_missing_token_count": "best_public_ts_missing_token_count",
            }),
            on="best_public_code_sha256",
            how="left",
        )
        reg = reg.merge(
            feat.rename(columns={
                "code_sha256": "last_parseable_before_final_code_sha256",
                "ts_complexity_score": "last_parseable_before_final_ts_complexity_score",
                "ts_error_count": "last_parseable_before_final_ts_error_count",
                "ts_missing_token_count": "last_parseable_before_final_ts_missing_token_count",
            }),
            on="last_parseable_before_final_code_sha256",
            how="left",
        )
        reg = reg.merge(
            feat.rename(columns={
                "code_sha256": "selected_track_code_sha256",
                "ts_complexity_score": "selected_track_ts_complexity_score",
                "ts_error_count": "selected_track_ts_error_count",
                "ts_missing_token_count": "selected_track_ts_missing_token_count",
            }),
            on="selected_track_code_sha256",
            how="left",
        )

    for c in [
        "ever_parseable_any",
        "ever_parseable_test_run",
        "any_public_test_pass",
        "any_public_all_pass",
    ]:
        if c in reg.columns:
            reg[c] = reg[c].fillna(0).astype(int)

    # Parseability regression: ended non-parseable but earlier parseable.
    reg["attempt_final_is_parseable_bool"] = reg["attempt_final_is_parseable"].fillna(False).astype(bool)
    reg["parseability_regression_flag"] = (
        (reg["is_python_question"] == True)  # noqa: E712
        & (reg["attempt_final_is_parseable_bool"] == False)  # noqa: E712
        & (reg["ever_parseable_any"] > 0)
    )

    # Peak-to-final public regression (public tests)
    reg["last_public_num_test_passed"] = pd.to_numeric(reg["last_public_num_test_passed"], errors="coerce")
    reg["max_public_num_test_passed"] = pd.to_numeric(reg["max_public_num_test_passed"], errors="coerce")
    reg["peak_to_last_public_regression_flag"] = (
        reg["max_public_num_test_passed"].notna()
        & reg["last_public_num_test_passed"].notna()
        & (reg["max_public_num_test_passed"] > reg["last_public_num_test_passed"])
    )

    # Structural regression proxies using tree-sitter complexity on boundary snapshots.
    reg["structural_regression_vs_best_public_flag"] = (
        (reg["is_python_question"] == True)  # noqa: E712
        & reg["best_public_ts_complexity_score"].notna()
        & reg["attempt_final_ts_complexity_score"].notna()
        & (reg["best_public_ts_complexity_score"] > reg["attempt_final_ts_complexity_score"])
    )
    reg["structural_regression_vs_last_parseable_flag"] = (
        (reg["is_python_question"] == True)  # noqa: E712
        & reg["last_parseable_before_final_ts_complexity_score"].notna()
        & reg["attempt_final_ts_complexity_score"].notna()
        & (reg["last_parseable_before_final_ts_complexity_score"] > reg["attempt_final_ts_complexity_score"])
    )

    reg.sort_values(["namespace", "problem_id", "student_id"], inplace=True)
    reg.to_csv(OUT_DIR / "regression_rows.csv", index=False)

    # Summaries
    summary_rows: list[dict[str, Any]] = []
    for track, g in reg.groupby("track", dropna=False):
        n = len(g)
        py = g[g["is_python_question"] == True]  # noqa: E712
        py_n = len(py)
        ended_nonparseable = py[py["attempt_final_is_parseable_bool"] == False]  # noqa: E712
        ended_nonparseable_n = len(ended_nonparseable)
        summary_rows.append(
            {
                "track": track,
                "rows": n,
                "python_rows": py_n,
                "ended_nonparseable_python_rows": ended_nonparseable_n,
                "ended_nonparseable_with_earlier_parseable": int(ended_nonparseable["parseability_regression_flag"].sum()) if ended_nonparseable_n else 0,
                "pct_ended_nonparseable_with_earlier_parseable": (
                    round(100.0 * float(ended_nonparseable["parseability_regression_flag"].sum()) / ended_nonparseable_n, 2)
                    if ended_nonparseable_n
                    else np.nan
                ),
                "peak_to_last_public_regression_rows": int(g["peak_to_last_public_regression_flag"].sum()),
                "pct_peak_to_last_public_regression": round(100.0 * float(g["peak_to_last_public_regression_flag"].sum()) / n, 2) if n else np.nan,
                "structural_regression_vs_best_public_rows": int(py["structural_regression_vs_best_public_flag"].sum()) if py_n else 0,
                "pct_structural_regression_vs_best_public_python": round(100.0 * float(py["structural_regression_vs_best_public_flag"].sum()) / py_n, 2) if py_n else np.nan,
                "structural_regression_vs_last_parseable_rows": int(py["structural_regression_vs_last_parseable_flag"].sum()) if py_n else 0,
                "pct_structural_regression_vs_last_parseable_python": round(100.0 * float(py["structural_regression_vs_last_parseable_flag"].sum()) / py_n, 2) if py_n else np.nan,
            }
        )
    pd.DataFrame(summary_rows).sort_values("track").to_csv(OUT_DIR / "regression_summary.csv", index=False)

    return reg


def build_global_error_profile(
    selected_rows: pd.DataFrame,
    best_public_rows: pd.DataFrame,
    reg_rows: pd.DataFrame,
) -> None:
    print("[7/9] Building global error profile tables...")
    df = selected_rows.copy()
    join_cols = ["namespace", "problem_id", "student_id"]
    if not best_public_rows.empty:
        df = df.merge(
            best_public_rows[
                join_cols
                + [
                    "best_public_summary",
                    "best_public_num_test_passed",
                    "best_public_runtime_error_type",
                    "best_public_wrong_output_subtype",
                    "best_public_primary_failure_mode",
                ]
            ],
            on=join_cols,
            how="left",
        )
    if not reg_rows.empty:
        df = df.merge(
            reg_rows[
                join_cols
                + [
                    "attempt_final_is_parseable_bool",
                    "parseability_regression_flag",
                    "peak_to_last_public_regression_flag",
                    "structural_regression_vs_best_public_flag",
                    "structural_regression_vs_last_parseable_flag",
                ]
            ],
            on=join_cols,
            how="left",
        )

    # Multi-label category table in the shape requested (counts can overlap).
    category_masks: list[tuple[str, pd.Series]] = []
    category_masks.append(("Unmodified skeleton", df["skeleton_modification_status"] == "Unmodified skeleton"))
    category_masks.append(("Modified, structurally valid", df["skeleton_modification_status"] == "Modified, structurally valid"))
    category_masks.append(("Modified, partially broken", df["skeleton_modification_status"] == "Modified, partially broken"))
    category_masks.append(("Modified, fundamentally broken", df["skeleton_modification_status"] == "Modified, fundamentally broken"))
    category_masks.append(("Empty / trivial", df["skeleton_modification_status"] == "Empty / trivial"))
    category_masks.append(("Unsupported language (non-Python)", df["skeleton_modification_status"] == "Unsupported language (non-Python)"))

    # Runtime error subtypes from best public run.
    if "best_public_runtime_error_type" in df.columns:
        for runtime_type in [
            "NameError",
            "TypeError",
            "IndexError",
            "KeyError",
            "ValueError",
            "ZeroDivisionError",
            "RecursionError",
            "AttributeError",
            "MemoryError",
            "Timeout",
            "Runtime Error (unspecified)",
        ]:
            category_masks.append((f"Runtime error - {runtime_type}", df["best_public_runtime_error_type"] == runtime_type))

    if "best_public_wrong_output_subtype" in df.columns:
        for subtype in [
            "Wrong output - formatting",
            "Wrong output - off-by-one/boundary",
            "Wrong output - partial correctness",
            "Wrong output - logic/completely wrong",
        ]:
            category_masks.append((subtype, df["best_public_wrong_output_subtype"] == subtype))

    category_masks.append(("Timeout", df.get("best_public_summary", pd.Series(index=df.index, dtype=object)) == "Time Limit Exceeded"))
    category_masks.append(("Partial pass", df["outcome_category"] == "Partial pass"))
    category_masks.append(("Full pass", df["outcome_category"] == "Full pass"))
    category_masks.append(("Submitted, zero", df["outcome_category"] == "Submitted, zero"))
    category_masks.append(("Regression: earlier parseable, final non-parseable", df.get("parseability_regression_flag", pd.Series(False, index=df.index)).fillna(False)))
    category_masks.append(("Regression: peak public > last public", df.get("peak_to_last_public_regression_flag", pd.Series(False, index=df.index)).fillna(False)))
    category_masks.append(("Structural regression vs best public", df.get("structural_regression_vs_best_public_flag", pd.Series(False, index=df.index)).fillna(False)))
    category_masks.append(("Structural regression vs last parseable", df.get("structural_regression_vs_last_parseable_flag", pd.Series(False, index=df.index)).fillna(False)))

    track_order = [
        "Track A: submitters",
        "Track A: non-submitters (submission-positive NS)",
        "Track B: zero-submission namespaces",
    ]

    rows: list[dict[str, Any]] = []
    for label, mask in category_masks:
        mask = mask.fillna(False).astype(bool)
        row: dict[str, Any] = {"category": label}
        total = int(mask.sum())
        row["Total"] = total
        for track in track_order:
            row[track] = int((mask & (df["track"] == track)).sum())
        rows.append(row)

    profile = pd.DataFrame(rows)
    profile.to_csv(OUT_DIR / "global_error_profile_multilabel.csv", index=False)

    # A mutually exclusive final-state taxonomy (useful for percentages)
    def _final_primary(row: pd.Series) -> str:
        oc = row.get("outcome_category")
        if oc == "Full pass":
            return "Full pass"
        if oc == "Partial pass":
            return "Partial pass"
        if oc == "Submitted, zero":
            return "Submitted, zero"
        if oc == "No activity":
            return "No activity"
        # Non-submitters / unsubmitted rows: structural taxonomy first, then best-public failure signal.
        status = row.get("skeleton_modification_status")
        if isinstance(status, str) and status:
            if status in {
                "Unmodified skeleton",
                "Empty / trivial",
                "Modified, partially broken",
                "Modified, fundamentally broken",
                "Unsupported language (non-Python)",
            }:
                return status
        bsum = row.get("best_public_summary")
        if bsum == "Runtime Error":
            return "Runtime error"
        if bsum == "Time Limit Exceeded":
            return "Timeout"
        if bsum == "Wrong Answer":
            return "Wrong output"
        if bsum == "All Cases Passed":
            return "Public full pass, no submit"
        return "Active, unresolved"

    df["final_primary_taxonomy"] = df.apply(_final_primary, axis=1)
    (
        df.groupby(["track", "final_primary_taxonomy"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["track", "rows"], ascending=[True, False])
        .to_csv(OUT_DIR / "final_primary_taxonomy_summary.csv", index=False)
    )

    # By term and question for future analysis.
    (
        df.groupby(["term", "track", "final_primary_taxonomy"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["term", "track", "rows"], ascending=[True, True, False])
        .to_csv(OUT_DIR / "final_primary_taxonomy_by_term.csv", index=False)
    )
    (
        df.groupby(["namespace", "problem_id", "question_title", "track", "final_primary_taxonomy"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["namespace", "problem_id", "track", "rows"], ascending=[True, True, True, False])
        .to_csv(OUT_DIR / "final_primary_taxonomy_by_question.csv", index=False)
    )

    # Non-submission profile by term (user-requested cheap split).
    non_submit = df[df["outcome_category"] == "Active, never submitted"].copy()
    if not non_submit.empty:
        thrash = (
            (non_submit.get("test_run_events", 0).fillna(0).astype(float) > 10)
            & (non_submit.get("best_public_num_test_passed", pd.Series(index=non_submit.index, dtype=float)).fillna(0) <= 0)
        )
        non_submit["stuck_thrash_proxy"] = thrash
        non_submit["any_public_pass_evidence"] = non_submit.get("best_public_num_test_passed", pd.Series(index=non_submit.index, dtype=float)).fillna(0) > 0
        (
            non_submit.groupby(["term", "track"], dropna=False)
            .agg(
                rows=("student_id", "count"),
                any_public_pass_evidence_rows=("any_public_pass_evidence", "sum"),
                stuck_thrash_proxy_rows=("stuck_thrash_proxy", "sum"),
            )
            .reset_index()
            .assign(
                pct_any_public_pass_evidence=lambda x: (100 * x["any_public_pass_evidence_rows"] / x["rows"]).round(2),
                pct_stuck_thrash_proxy=lambda x: (100 * x["stuck_thrash_proxy_rows"] / x["rows"]).round(2),
            )
            .to_csv(OUT_DIR / "non_submission_behaviour_by_term.csv", index=False)
        )


def write_rebuild_manifest() -> None:
    print("[8/9] Writing manifest / output index...")
    files = []
    for p in sorted(OUT_DIR.rglob("*")):
        if p.is_file():
            files.append({"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size})
    pd.DataFrame(files).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = make_conn()
    setup_views(conn)

    skeleton_df, skeleton_map = load_question_skeletons()
    write_question_skeleton_outputs(skeleton_df)

    # Merge language metadata into regression inputs early for hash parsing scope.
    regression_inputs = pd.read_csv(OUT_DIR / "regression_inputs.csv", low_memory=False)
    if not regression_inputs.empty:
        regression_inputs["problem_id"] = regression_inputs["problem_id"].astype(int)
        regression_inputs = regression_inputs.merge(
            skeleton_df[["namespace", "problem_id", "is_python_question", "primary_language"]],
            on=["namespace", "problem_id"],
            how="left",
        )
        regression_inputs.to_csv(OUT_DIR / "regression_inputs.csv", index=False)

    selected_base = pd.read_csv(OUT_DIR / "selected_snapshot_rows_base.csv", low_memory=False)
    selected_base["problem_id"] = selected_base["problem_id"].astype(int)
    python_selected = selected_base.merge(
        skeleton_df[["namespace", "problem_id", "is_python_question"]],
        on=["namespace", "problem_id"],
        how="left",
    )
    python_selected = python_selected[python_selected["is_python_question"] == True].copy()  # noqa: E712

    hash_features = build_hash_feature_table(conn, python_selected, regression_inputs)
    selected_rows = build_selected_snapshot_taxonomy(conn, skeleton_df, skeleton_map, hash_features)
    best_public_rows = build_best_public_failure_taxonomy(conn, selected_rows)
    reg_rows = build_regression_outputs(selected_rows, OUT_DIR / "regression_inputs.csv", hash_features)
    build_global_error_profile(selected_rows, best_public_rows, reg_rows)
    write_rebuild_manifest()

    print("[9/9] Done.")
    print(f"Outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
