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
"""Step 4: The Syntax Bottleneck — Quantified (dual-track).

This script synthesizes Step 3 outputs into a gating decomposition and runs a
conservative rule-based syntax repair + re-evaluation pass for Python code:
- Track A submitters (private tests)
- Track B zero-submission namespaces (public tests)

LLM-based syntax correction is scaffolded as an explicit skipped stage when no
API key is configured; the script writes outputs documenting that skip.
"""

from __future__ import annotations

import ast
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import warnings
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.generate_error_taxonomy import (  # noqa: E402
    SkeletonInfo,
    TsAnalyzer,
    classify_runtime_type_from_case_output,
    classify_wrong_output_subtype,
    extract_student_editable_code,
    first_failing_case,
    load_question_skeletons,
    parse_test_case_results,
)

ANALYSIS_DIR = ROOT / "analysis"
STEP3_DIR = ANALYSIS_DIR / "error_taxonomy"
OUT_DIR = ANALYSIS_DIR / "syntax_bottleneck_quantified"

TRACK_A_SUBMITTERS = "Track A: submitters"
TRACK_A_NON_SUBMIT = "Track A: non-submitters (submission-positive NS)"
TRACK_B = "Track B: zero-submission namespaces"

HEADER_COLON_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<kw>if|elif|else|for|while|def|class|try|except|finally|with|match|case)\b(?P<rest>.*)$"
)
UNMATCHED_DELIM_RE = re.compile(r"'(?P<ch>[\(\[\{])' was never closed")
INVALID_NONPRINT_RE = re.compile(r"[^\x09\x0A\x0D\x20-\x7E]")


@dataclass(slots=True)
class QuestionRuntimeConfig:
    namespace: str
    problem_id: int
    language: str
    is_python: bool
    prefixed_code: str
    code_template: str
    uneditable_code: str
    suffixed_invisible_code: str
    ignore_presentation_errors: bool
    public_testcases: list[dict[str, Any]]
    private_testcases: list[dict[str, Any]]


@dataclass(slots=True)
class EvalCaseResult:
    passed: bool
    timeout: bool
    runtime_error: bool
    output: str | None
    expected_output: str | None
    stderr: str | None
    duration_ms: float


@dataclass(slots=True)
class RepairEvalResult:
    parseable_after_rule_fix: bool
    fixed_code: str | None
    rule_fix_applied: bool
    rule_fix_kinds: str
    original_ast_error_class: str | None
    original_ast_error_msg: str | None
    reeval_scope: str | None
    reeval_num_passed: int | None
    reeval_num_cases: int | None
    reeval_score_pct: float | None
    reeval_all_pass: bool | None
    timeout_count: int | None
    runtime_error_case_count: int | None


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


def qdf(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


def copy_query(conn: duckdb.DuckDBPyConnection, sql: str, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    escaped = out_csv.as_posix().replace("'", "''")
    conn.execute(f"COPY ({sql}) TO '{escaped}' (HEADER, DELIMITER ',')")


def normalize_output_for_formatting(s: str | None) -> str:
    if s is None:
        return ""
    txt = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in txt.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def outputs_equal(actual: str | None, expected: str | None, ignore_presentation_errors: bool) -> bool:
    actual_s = "" if actual is None else actual
    expected_s = "" if expected is None else expected
    if actual_s == expected_s:
        return True
    if ignore_presentation_errors:
        return normalize_output_for_formatting(actual_s) == normalize_output_for_formatting(expected_s)
    return False


def load_step3_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = pd.read_csv(STEP3_DIR / "selected_snapshot_taxonomy_rows.csv", low_memory=False)
    best_public = pd.read_csv(STEP3_DIR / "best_public_test_run_classification_rows.csv", low_memory=False)
    regression = pd.read_csv(STEP3_DIR / "regression_rows.csv", low_memory=False)

    for df in (selected, best_public, regression):
        if "problem_id" in df.columns:
            df["problem_id"] = pd.to_numeric(df["problem_id"], errors="coerce").astype("Int64")
    return selected, best_public, regression


def load_question_runtime_configs() -> dict[tuple[str, int], QuestionRuntimeConfig]:
    configs: dict[tuple[str, int], QuestionRuntimeConfig] = {}
    for ns_dir in sorted((ROOT / "problems").glob("ns_*")):
        if not ns_dir.is_dir():
            continue
        namespace = ns_dir.name
        for fp in sorted(ns_dir.glob("*.json"), key=lambda p: int(p.stem)):
            try:
                problem_id = int(fp.stem)
            except Exception:
                continue
            try:
                obj = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                obj = {}
            langs = [x for x in (obj.get("allowed_languages") or []) if isinstance(x, dict)]
            py_obj = next((x for x in langs if str(x.get("language") or "").startswith("py")), None)
            primary = py_obj or (langs[0] if langs else {})
            lang_name = str((primary or {}).get("language") or "unknown")
            is_python = lang_name.startswith("py")
            cfg = QuestionRuntimeConfig(
                namespace=namespace,
                problem_id=problem_id,
                language=lang_name,
                is_python=is_python,
                prefixed_code=str((primary or {}).get("prefixed_code") or ""),
                code_template=str((primary or {}).get("code_template") or ""),
                uneditable_code=str((primary or {}).get("uneditable_code") or ""),
                suffixed_invisible_code=str((primary or {}).get("suffixed_invisible_code") or ""),
                ignore_presentation_errors=bool(obj.get("ignore_presentation_errors", False)),
                public_testcases=list(obj.get("public_testcase") or []),
                private_testcases=list(obj.get("private_testcase") or []),
            )
            configs[(namespace, problem_id)] = cfg
    return configs


def fetch_code_map_for_hashes(conn: duckdb.DuckDBPyConnection, hashes: list[str]) -> dict[str, str]:
    if not hashes:
        return {}
    conn.register("step4_hashes_df", pd.DataFrame({"code_sha256": sorted(set(hashes))}))
    cur = conn.execute(
        """
        SELECT c.code_sha256, c.code_snapshot
        FROM step4_hashes_df h
        JOIN read_parquet('analysis/code_snapshots.parquet') c USING (code_sha256)
        ORDER BY c.code_sha256
        """
    )
    out: dict[str, str] = {}
    while True:
        chunk = cur.fetch_df_chunk(vectors_per_chunk=40)
        if chunk is None or chunk.empty:
            break
        for rec in chunk.itertuples(index=False):
            out[str(rec.code_sha256)] = rec.code_snapshot if isinstance(rec.code_snapshot, str) else ""
    return out


def ast_error_info(code: str) -> tuple[bool, str | None, str | None, int | None]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ast.parse(code)
        return True, None, None, None
    except Exception as exc:  # noqa: BLE001
        msg = getattr(exc, "msg", None) or str(exc)
        return False, exc.__class__.__name__, str(msg), getattr(exc, "lineno", None)


def _append_colon_if_header(code: str, lineno: int | None) -> tuple[str, bool]:
    if not lineno:
        return code, False
    lines = code.splitlines(keepends=False)
    idx = lineno - 1
    if idx < 0 or idx >= len(lines):
        return code, False
    line = lines[idx]
    m = HEADER_COLON_RE.match(line)
    if not m:
        return code, False
    stripped = line.rstrip()
    if stripped.endswith(":"):
        return code, False
    # Avoid one-line lambdas/expressions that merely start with keyword text inside strings/comments.
    if stripped.lstrip().startswith("#"):
        return code, False
    lines[idx] = stripped + ":"
    return "\n".join(lines), True


def _balance_delimiters(code: str) -> tuple[str, bool]:
    # Conservative: append missing closers to end of file only.
    stack: list[str] = []
    in_single = in_double = False
    escape = False
    for ch in code:
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if in_single:
            if ch == "'":
                in_single = False
            continue
        if in_double:
            if ch == '"':
                in_double = False
            continue
        if ch == "'":
            in_single = True
            continue
        if ch == '"':
            in_double = True
            continue
        if ch in "([{" :
            stack.append(ch)
        elif ch in ")]}" and stack:
            top = stack[-1]
            if (top, ch) in {("(", ")"), ("[", "]"), ("{", "}")}:
                stack.pop()
    if not stack:
        return code, False
    closing_map = {"(": ")", "[": "]", "{": "}"}
    suffix = "".join(closing_map[ch] for ch in reversed(stack))
    return code + suffix, True


def _insert_pass_after_block_header(code: str, lineno: int | None) -> tuple[str, bool]:
    if not lineno:
        return code, False
    lines = code.splitlines(keepends=False)
    idx = lineno - 1
    if idx < 0 or idx >= len(lines):
        return code, False
    line = lines[idx]
    m = HEADER_COLON_RE.match(line)
    if not m or not line.rstrip().endswith(":"):
        return code, False
    indent = m.group("indent") + "    "
    insert_idx = idx + 1
    if insert_idx < len(lines) and lines[insert_idx].strip():
        # Already has non-empty next line; don't force pass.
        return code, False
    lines.insert(insert_idx, indent + "pass")
    return "\n".join(lines), True


def apply_rule_based_syntax_fix(original_code: str, max_iters: int = 4) -> tuple[str, bool, list[str], tuple[str | None, str | None]]:
    code = (original_code or "").replace("\r\n", "\n").replace("\r", "\n").expandtabs(4)
    applied: list[str] = []
    parseable, err_cls, err_msg, err_lineno = ast_error_info(code)
    first_err = (err_cls, err_msg)
    if parseable:
        return code, False, applied, first_err

    for _ in range(max_iters):
        changed = False
        parseable, err_cls, err_msg, err_lineno = ast_error_info(code)
        if parseable:
            break
        msg_low = (err_msg or "").lower()

        if "expected ':'" in msg_low:
            code2, ok = _append_colon_if_header(code, err_lineno)
            if ok:
                code = code2
                applied.append("add_missing_colon")
                changed = True
        if (not changed) and ("expected an indented block" in msg_low or "indentationerror" in (err_cls or "").lower()):
            # First try normalizing non-printables and tabs; then insert pass for empty block.
            cleaned = INVALID_NONPRINT_RE.sub("", code)
            if cleaned != code:
                code = cleaned
                applied.append("strip_nonprintable")
                changed = True
            if not changed:
                code2, ok = _insert_pass_after_block_header(code, max(1, (err_lineno or 1) - 1))
                if ok:
                    code = code2
                    applied.append("insert_pass_block")
                    changed = True
        if (not changed) and ("was never closed" in msg_low or "unexpected eof while parsing" in msg_low):
            m = UNMATCHED_DELIM_RE.search(err_msg or "")
            if m:
                ch = m.group("ch")
                closing_map = {"(": ")", "[": "]", "{": "}"}
                code = code + closing_map.get(ch, "")
                applied.append(f"append_close_{closing_map.get(ch,'?')}")
                changed = True
            else:
                code2, ok = _balance_delimiters(code)
                if ok:
                    code = code2
                    applied.append("balance_delimiters")
                    changed = True
        if (not changed) and ("invalid syntax" in msg_low or "indent" in msg_low):
            # Generic low-risk fixes.
            code2, ok = _append_colon_if_header(code, err_lineno)
            if ok:
                code = code2
                applied.append("add_colon_generic")
                changed = True
            else:
                cleaned = INVALID_NONPRINT_RE.sub("", code)
                if cleaned != code:
                    code = cleaned
                    applied.append("strip_nonprintable")
                    changed = True

        if not changed:
            break

    parseable, _, _, _ = ast_error_info(code)
    return code, bool(applied), applied, first_err


def assemble_python_code(student_editable_code: str, qcfg: QuestionRuntimeConfig) -> str:
    # Observed snapshot layout for Python is prefix + editable + uneditable + suffix.
    return f"{qcfg.prefixed_code}{student_editable_code}{qcfg.uneditable_code}{qcfg.suffixed_invisible_code}"


def run_python_code_on_testcase(assembled_code: str, testcase_input: str, timeout_s: float = 2.0) -> EvalCaseResult:
    start = time.perf_counter()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(assembled_code)
    try:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", str(tmp_path)],
                input=(testcase_input or ""),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=str(ROOT),
            )
            dur_ms = (time.perf_counter() - start) * 1000.0
            # Evaluator wrappers often return exit code 0 even on failed assertions; output comparison determines pass.
            return EvalCaseResult(
                passed=False,
                timeout=False,
                runtime_error=(proc.returncode != 0),
                output=proc.stdout,
                expected_output=None,
                stderr=proc.stderr,
                duration_ms=dur_ms,
            )
        except subprocess.TimeoutExpired as exc:
            dur_ms = (time.perf_counter() - start) * 1000.0
            return EvalCaseResult(
                passed=False,
                timeout=True,
                runtime_error=False,
                output=(exc.stdout if isinstance(exc.stdout, str) else None),
                expected_output=None,
                stderr=(exc.stderr if isinstance(exc.stderr, str) else None),
                duration_ms=dur_ms,
            )
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def evaluate_python_code_against_tests(
    student_editable_code: str,
    qcfg: QuestionRuntimeConfig,
    scope: str,
    timeout_s: float = 2.0,
) -> RepairEvalResult:
    if not qcfg.is_python:
        return RepairEvalResult(
            parseable_after_rule_fix=False,
            fixed_code=None,
            rule_fix_applied=False,
            rule_fix_kinds="",
            original_ast_error_class=None,
            original_ast_error_msg=None,
            reeval_scope=None,
            reeval_num_passed=None,
            reeval_num_cases=None,
            reeval_score_pct=None,
            reeval_all_pass=None,
            timeout_count=None,
            runtime_error_case_count=None,
        )

    fixed_code, any_fix, fix_kinds, first_err = apply_rule_based_syntax_fix(student_editable_code)
    parseable, _, _, _ = ast_error_info(fixed_code)
    if not parseable:
        return RepairEvalResult(
            parseable_after_rule_fix=False,
            fixed_code=fixed_code,
            rule_fix_applied=any_fix,
            rule_fix_kinds=";".join(fix_kinds),
            original_ast_error_class=first_err[0],
            original_ast_error_msg=(first_err[1][:500] if first_err[1] else None),
            reeval_scope=scope,
            reeval_num_passed=None,
            reeval_num_cases=None,
            reeval_score_pct=None,
            reeval_all_pass=None,
            timeout_count=None,
            runtime_error_case_count=None,
        )

    tests = qcfg.private_testcases if scope == "private" else qcfg.public_testcases
    assembled = assemble_python_code(fixed_code, qcfg)
    num_passed = 0
    total_weight = 0.0
    passed_weight = 0.0
    timeout_count = 0
    runtime_error_case_count = 0

    for tc in tests:
        expected = str(tc.get("output") or "")
        inp = str(tc.get("input") or "")
        weight = float(tc.get("weight") or 1.0)
        total_weight += weight
        res = run_python_code_on_testcase(assembled, inp, timeout_s=timeout_s)
        actual = res.output if res.output is not None else ""
        is_pass = outputs_equal(actual, expected, qcfg.ignore_presentation_errors)
        if is_pass:
            num_passed += 1
            passed_weight += weight
        if res.timeout:
            timeout_count += 1
        if (not is_pass) and (not res.timeout) and res.runtime_error:
            runtime_error_case_count += 1

    score_pct = (100.0 * passed_weight / total_weight) if total_weight > 0 else None
    return RepairEvalResult(
        parseable_after_rule_fix=True,
        fixed_code=fixed_code,
        rule_fix_applied=any_fix,
        rule_fix_kinds=";".join(fix_kinds),
        original_ast_error_class=first_err[0],
        original_ast_error_msg=(first_err[1][:500] if first_err[1] else None),
        reeval_scope=scope,
        reeval_num_passed=num_passed,
        reeval_num_cases=len(tests),
        reeval_score_pct=score_pct,
        reeval_all_pass=(num_passed == len(tests) if tests else None),
        timeout_count=timeout_count,
        runtime_error_case_count=runtime_error_case_count,
    )


def build_parseability_baseline(selected: pd.DataFrame) -> None:
    print("[1/10] Building parseability baseline tables (4a)...")
    df = selected.copy()
    df = df[df["track"].isin([TRACK_A_SUBMITTERS, TRACK_A_NON_SUBMIT, TRACK_B])].copy()
    df["is_python_question"] = df["is_python_question"].fillna(False).astype(bool)
    df["ast_parseable_recheck"] = df["ast_parseable_recheck"].fillna(False).astype(bool)

    # Inclusive metrics (requested rows can overlap, especially unmodified/empty).
    rows = []
    for track in [TRACK_A_SUBMITTERS, TRACK_A_NON_SUBMIT, TRACK_B]:
        g = df[df["track"] == track]
        n = len(g)
        if n == 0:
            continue
        rows.extend(
            [
                {
                    "track": track,
                    "metric": "Parseable (ast.parse)",
                    "rows": int(g["ast_parseable_recheck"].sum()),
                    "pct_track": round(100.0 * float(g["ast_parseable_recheck"].sum()) / n, 2),
                },
                {
                    "track": track,
                    "metric": "Non-parseable, structure evident (tree-sitter few/local errors)",
                    "rows": int(
                        ((~g["ast_parseable_recheck"]) & (g["skeleton_modification_status"] == "Modified, partially broken")).sum()
                    ),
                    "pct_track": round(
                        100.0
                        * float(
                            ((~g["ast_parseable_recheck"]) & (g["skeleton_modification_status"] == "Modified, partially broken")).sum()
                        )
                        / n,
                        2,
                    ),
                },
                {
                    "track": track,
                    "metric": "Non-parseable, fundamentally broken",
                    "rows": int(
                        ((~g["ast_parseable_recheck"]) & (g["skeleton_modification_status"] == "Modified, fundamentally broken")).sum()
                    ),
                    "pct_track": round(
                        100.0
                        * float(
                            ((~g["ast_parseable_recheck"]) & (g["skeleton_modification_status"] == "Modified, fundamentally broken")).sum()
                        )
                        / n,
                        2,
                    ),
                },
                {
                    "track": track,
                    "metric": "Unmodified skeleton / empty",
                    "rows": int(g["skeleton_modification_status"].isin(["Unmodified skeleton", "Empty / trivial"]).sum()),
                    "pct_track": round(
                        100.0 * float(g["skeleton_modification_status"].isin(["Unmodified skeleton", "Empty / trivial"]).sum()) / n,
                        2,
                    ),
                },
            ]
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "parseability_baseline_dual_track_inclusive.csv", index=False)

    # Exclusive decomposition (useful for waterfall-like accounting within selected snapshot states).
    exc_rows = []
    for track in [TRACK_A_SUBMITTERS, TRACK_A_NON_SUBMIT, TRACK_B]:
        g = df[df["track"] == track].copy()
        n = len(g)
        unmod = g["skeleton_modification_status"].isin(["Unmodified skeleton", "Empty / trivial"])
        parseable = g["ast_parseable_recheck"]
        mech = (~parseable) & (g["skeleton_modification_status"] == "Modified, partially broken")
        fund = (~parseable) & (g["skeleton_modification_status"] == "Modified, fundamentally broken")
        residual = ~(unmod | parseable | mech | fund)
        for metric, mask in [
            ("Unmodified skeleton / empty (exclusive)", unmod),
            ("Parseable (ast.parse, excluding unmodified/empty)", parseable & ~unmod),
            ("Non-parseable, structure evident (exclusive)", mech),
            ("Non-parseable, fundamentally broken (exclusive)", fund),
            ("Other / residual", residual),
        ]:
            exc_rows.append(
                {
                    "track": track,
                    "metric": metric,
                    "rows": int(mask.sum()),
                    "pct_track": round(100.0 * float(mask.sum()) / n, 2) if n else np.nan,
                }
            )
    pd.DataFrame(exc_rows).to_csv(OUT_DIR / "parseability_baseline_dual_track_exclusive.csv", index=False)

    # Wide table matching prompt style (inclusive metrics)
    wide = (
        pd.DataFrame(rows)
        .pivot(index="metric", columns="track", values="pct_track")
        .reset_index()
        .rename_axis(None, axis=1)
    )
    wide.to_csv(OUT_DIR / "parseability_baseline_dual_track_prompt_table_pct.csv", index=False)


def build_regression_summary(regression: pd.DataFrame) -> None:
    print("[2/10] Building regression summary tables (4b)...")
    reg = regression.copy()
    reg["track_group"] = np.where(reg["track"] == TRACK_B, "Track B", "Track A")

    # Use Step 3 exported track-level summaries directly, and also aggregate to Track A combined.
    step3 = pd.read_csv(STEP3_DIR / "regression_summary.csv")
    step3.to_csv(OUT_DIR / "regression_summary_by_step3_track.csv", index=False)

    rows = []
    for group, g in reg.groupby("track_group", dropna=False):
        n = len(g)
        py = g[g["is_python_question"] == True].copy()  # noqa: E712
        py_n = len(py)
        ended_nonparseable = py[py["attempt_final_is_parseable_bool"].fillna(False) == False]  # noqa: E712
        end_nonparse_n = len(ended_nonparseable)
        earlier_parseable = int(ended_nonparseable["parseability_regression_flag"].fillna(False).sum()) if end_nonparse_n else 0
        peak_reg = int(g["peak_to_last_public_regression_flag"].fillna(False).sum())
        struct_best = int(py["structural_regression_vs_best_public_flag"].fillna(False).sum()) if py_n else 0
        struct_last_parseable = int(py["structural_regression_vs_last_parseable_flag"].fillna(False).sum()) if py_n else 0
        rows.append(
            {
                "track_group": group,
                "rows": n,
                "python_rows": py_n,
                "ended_nonparseable_python_rows": end_nonparse_n,
                "ended_nonparseable_with_earlier_parseable": earlier_parseable,
                "pct_ended_nonparseable_with_earlier_parseable": round(100.0 * earlier_parseable / end_nonparse_n, 2)
                if end_nonparse_n
                else np.nan,
                "peak_to_final_test_pass_regression_rows": peak_reg,
                "pct_peak_to_final_test_pass_regression": round(100.0 * peak_reg / n, 2) if n else np.nan,
                "structural_regression_vs_best_public_rows": struct_best,
                "pct_structural_regression_vs_best_public_python": round(100.0 * struct_best / py_n, 2) if py_n else np.nan,
                "structural_regression_vs_last_parseable_rows": struct_last_parseable,
                "pct_structural_regression_vs_last_parseable_python": round(100.0 * struct_last_parseable / py_n, 2)
                if py_n
                else np.nan,
            }
        )
    pd.DataFrame(rows).sort_values("track_group").to_csv(OUT_DIR / "regression_summary_dual_track.csv", index=False)


def build_track_a_private_final_results(conn: duckdb.DuckDBPyConnection, selected: pd.DataFrame) -> pd.DataFrame:
    print("[3/10] Extracting Track A final private submission test-case results (4e and Track A waterfall support)...")
    submitters = selected[selected["track"] == TRACK_A_SUBMITTERS].copy()
    if submitters.empty:
        out = pd.DataFrame(columns=["namespace", "problem_id", "student_id"])
        out.to_csv(OUT_DIR / "track_a_private_final_rows.csv", index=False)
        return out

    keep = submitters[["namespace", "problem_id", "student_id", "final_submission_file", "ast_parseable_recheck"]].copy()
    keep["problem_id"] = keep["problem_id"].astype(int)
    conn.register("step4_submitters_df", keep)

    cur = conn.execute(
        """
        SELECT
          s.namespace,
          CAST(s.problem_id AS INTEGER) AS problem_id,
          s.student_id,
          s.final_submission_file,
          s.ast_parseable_recheck,
          r.CompilationResult
        FROM step4_submitters_df s
        LEFT JOIN read_json(
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
        ) r
          ON r.Namespace = s.namespace
         AND TRY_CAST(r.ProblemID AS INTEGER) = CAST(s.problem_id AS INTEGER)
         AND r.StudentID = s.student_id
         AND r.FileName = s.final_submission_file
        WHERE r.EvaluationType = 'private' OR r.EvaluationType IS NULL
        ORDER BY s.namespace, CAST(s.problem_id AS INTEGER), s.student_id
        """
    )

    rows: list[dict[str, Any]] = []
    while True:
        chunk = cur.fetch_df_chunk(vectors_per_chunk=20)
        if chunk is None or chunk.empty:
            break
        for rec in chunk.itertuples(index=False):
            comp = rec.CompilationResult if isinstance(rec.CompilationResult, str) else None
            try:
                obj = json.loads(comp) if comp else {}
            except Exception:
                obj = {}
            summary = obj.get("summary")
            status = obj.get("status")
            tcr = parse_test_case_results(comp)
            n_cases = len(tcr)
            n_passed = sum(1 for c in tcr if bool(c.get("passed")))
            fail_idx, fail_case = first_failing_case(tcr)
            fail_output = str(fail_case.get("output")) if fail_case and fail_case.get("output") is not None else None
            fail_expected = (
                str(fail_case.get("expected_output")) if fail_case and fail_case.get("expected_output") is not None else None
            )
            runtime_type = classify_runtime_type_from_case_output(fail_output, summary)
            wrong_subtype = classify_wrong_output_subtype(
                summary,
                int(obj.get("num_test_passed") or 0) if obj.get("num_test_passed") is not None else None,
                n_cases,
                fail_output,
                fail_expected,
            )
            # Formatting tax on final private submission outputs (whitespace-only normalization).
            formatting_rescued_cases = 0
            for c in tcr:
                passed = bool(c.get("passed"))
                if passed:
                    continue
                if str(c.get("reason") or "") != "Wrong Answer":
                    continue
                if normalize_output_for_formatting(str(c.get("output") or "")) == normalize_output_for_formatting(
                    str(c.get("expected_output") or "")
                ):
                    formatting_rescued_cases += 1
            total_wrong_answer_fail_cases = sum(1 for c in tcr if (not bool(c.get("passed"))) and str(c.get("reason") or "") == "Wrong Answer")
            formatting_full_row_rescue = (
                (summary == "Wrong Answer")
                and bool(rec.ast_parseable_recheck)
                and total_wrong_answer_fail_cases > 0
                and formatting_rescued_cases == total_wrong_answer_fail_cases
                and all(str(c.get("reason") or "") == "Wrong Answer" for c in tcr if not bool(c.get("passed")))
            )
            rows.append(
                {
                    "namespace": rec.namespace,
                    "problem_id": int(rec.problem_id),
                    "student_id": rec.student_id,
                    "final_submission_file": rec.final_submission_file,
                    "ast_parseable_recheck": bool(rec.ast_parseable_recheck),
                    "private_summary": summary,
                    "private_status": status,
                    "private_num_cases": n_cases,
                    "private_num_passed": n_passed,
                    "private_all_pass": (n_cases > 0 and n_passed == n_cases),
                    "private_runtime_error_type": runtime_type,
                    "private_wrong_output_subtype": wrong_subtype,
                    "formatting_rescued_cases_whitespace_norm": formatting_rescued_cases,
                    "total_wrong_answer_fail_cases": total_wrong_answer_fail_cases,
                    "formatting_full_row_rescue_whitespace_norm": formatting_full_row_rescue,
                }
            )
    out = pd.DataFrame(rows)
    if not out.empty:
        out.sort_values(
            ["namespace", "problem_id", "student_id", "private_num_cases", "private_num_passed"],
            ascending=[True, True, True, False, False],
            inplace=True,
        )
        out = out.drop_duplicates(subset=["namespace", "problem_id", "student_id"], keep="first")
        out.sort_values(["namespace", "problem_id", "student_id"], inplace=True)
    out.to_csv(OUT_DIR / "track_a_private_final_rows.csv", index=False)

    # Formatting tax summary (4e)
    fmt_df = out[
        (out["ast_parseable_recheck"] == True)  # noqa: E712
        & (out["private_summary"] == "Wrong Answer")
    ].copy()
    if fmt_df.empty:
        pd.DataFrame(
            [
                {
                    "parseable_wrong_answer_rows": 0,
                    "rows_with_any_formatting_rescue": 0,
                    "rows_fully_rescued_by_formatting_norm": 0,
                    "pct_rows_fully_rescued": np.nan,
                    "wrong_answer_fail_cases": 0,
                    "formatting_rescued_fail_cases": 0,
                    "pct_fail_cases_rescued": np.nan,
                }
            ]
        ).to_csv(OUT_DIR / "formatting_tax_track_a_summary.csv", index=False)
    else:
        rows_with_any = int((fmt_df["formatting_rescued_cases_whitespace_norm"] > 0).sum())
        full_rows = int(fmt_df["formatting_full_row_rescue_whitespace_norm"].sum())
        total_cases = int(fmt_df["total_wrong_answer_fail_cases"].sum())
        rescued_cases = int(fmt_df["formatting_rescued_cases_whitespace_norm"].sum())
        pd.DataFrame(
            [
                {
                    "parseable_wrong_answer_rows": int(len(fmt_df)),
                    "rows_with_any_formatting_rescue": rows_with_any,
                    "rows_fully_rescued_by_formatting_norm": full_rows,
                    "pct_rows_fully_rescued": round(100.0 * full_rows / len(fmt_df), 2),
                    "wrong_answer_fail_cases": total_cases,
                    "formatting_rescued_fail_cases": rescued_cases,
                    "pct_fail_cases_rescued": round(100.0 * rescued_cases / total_cases, 2) if total_cases else np.nan,
                }
            ]
        ).to_csv(OUT_DIR / "formatting_tax_track_a_summary.csv", index=False)

    return out


def _prepare_repair_targets(
    selected: pd.DataFrame,
    track: str,
) -> pd.DataFrame:
    df = selected[
        (selected["track"] == track)
        & (selected["is_python_question"] == True)  # noqa: E712
        & (selected["ast_parseable_recheck"] == False)  # noqa: E712
        & (selected["code_sha256"].notna())
    ].copy()
    use_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "track",
        "term",
        "wave",
        "question_title",
        "code_sha256",
        "skeleton_modification_status",
        "syntax_error_category",
        "syntax_intent_context",
        "ts_error_count",
        "ts_missing_token_count",
        "selected_num_test_passed",
        "selected_test_case_count",
        "selected_summary",
        "selected_score",
    ]
    df = df[use_cols].copy()
    df["problem_id"] = df["problem_id"].astype(int)
    return df


def _repair_and_eval_row(
    row: dict[str, Any],
    full_code: str,
    sk: SkeletonInfo,
    qcfg: QuestionRuntimeConfig,
    scope: str,
) -> dict[str, Any]:
    student_code, strip_status = extract_student_editable_code(full_code, sk)
    res = evaluate_python_code_against_tests(student_code, qcfg, scope=scope, timeout_s=1.5)
    orig_passed = row.get("selected_num_test_passed")
    orig_cases = row.get("selected_test_case_count")
    try:
        orig_passed_i = int(orig_passed) if orig_passed is not None and not pd.isna(orig_passed) else None
    except Exception:
        orig_passed_i = None
    try:
        orig_cases_i = int(orig_cases) if orig_cases is not None and not pd.isna(orig_cases) else None
    except Exception:
        orig_cases_i = None
    score_gain = None
    pass_gain = None
    if res.reeval_num_passed is not None and orig_passed_i is not None:
        pass_gain = res.reeval_num_passed - orig_passed_i
    if res.reeval_score_pct is not None and row.get("selected_score") is not None and not pd.isna(row.get("selected_score")):
        try:
            score_gain = float(res.reeval_score_pct) - float(row.get("selected_score"))
        except Exception:
            score_gain = None
    return {
        **row,
        "scope": scope,
        "scaffold_strip_status": strip_status,
        "student_editable_code_length": len(student_code),
        "rule_fix_applied": res.rule_fix_applied,
        "rule_fix_kinds": res.rule_fix_kinds,
        "rule_parseable_after_fix": res.parseable_after_rule_fix,
        "rule_original_ast_error_class": res.original_ast_error_class,
        "rule_original_ast_error_msg": res.original_ast_error_msg,
        "rule_reeval_num_passed": res.reeval_num_passed,
        "rule_reeval_num_cases": res.reeval_num_cases,
        "rule_reeval_score_pct": res.reeval_score_pct,
        "rule_reeval_all_pass": res.reeval_all_pass,
        "rule_timeout_count": res.timeout_count,
        "rule_runtime_error_case_count": res.runtime_error_case_count,
        "rule_pass_gain_vs_original_selected": pass_gain,
        "rule_score_gain_vs_original_selected": score_gain,
    }


def run_rule_based_syntax_repair_eval(
    conn: duckdb.DuckDBPyConnection,
    selected: pd.DataFrame,
    skeleton_map: dict[tuple[str, int], SkeletonInfo],
    qcfg_map: dict[tuple[str, int], QuestionRuntimeConfig],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[4/10] Running rule-based syntax repair + re-evaluation (4c, 4d)...")
    targets_a = _prepare_repair_targets(selected, TRACK_A_SUBMITTERS)
    targets_b = _prepare_repair_targets(selected, TRACK_B)

    all_targets = pd.concat([targets_a, targets_b], ignore_index=True)
    if all_targets.empty:
        empty = pd.DataFrame(columns=["namespace", "problem_id", "student_id"])
        empty.to_csv(OUT_DIR / "syntax_repair_rule_based_rows.csv", index=False)
        return empty, empty

    code_map = fetch_code_map_for_hashes(conn, [str(x) for x in all_targets["code_sha256"].dropna().tolist()])

    jobs: list[dict[str, Any]] = []
    for rec in all_targets.itertuples(index=False):
        key = (str(rec.namespace), int(rec.problem_id))
        sk = skeleton_map.get(key)
        qcfg = qcfg_map.get(key)
        if sk is None or qcfg is None or not qcfg.is_python:
            continue
        full_code = code_map.get(str(rec.code_sha256))
        if full_code is None:
            continue
        scope = "private" if rec.track == TRACK_A_SUBMITTERS else "public"
        jobs.append(
            {
                "row": rec._asdict(),
                "full_code": full_code,
                "sk": sk,
                "qcfg": qcfg,
                "scope": scope,
            }
        )

    print(f"  repair targets: {len(jobs):,} rows (Track A submitters + Track B parse-fail Python)")

    results: list[dict[str, Any]] = []
    workers = min(8, cpu_threads())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [
            ex.submit(_repair_and_eval_row, j["row"], j["full_code"], j["sk"], j["qcfg"], j["scope"])
            for j in jobs
        ]
        done = 0
        for fut in as_completed(futs):
            results.append(fut.result())
            done += 1
            if done % 500 == 0:
                print(f"  repaired/evaluated {done:,}/{len(futs):,} rows...")

    rule_df = pd.DataFrame(results)
    if rule_df.empty:
        rule_df = pd.DataFrame(columns=["namespace", "problem_id", "student_id"])
    else:
        rule_df.sort_values(["track", "namespace", "problem_id", "student_id"], inplace=True)

    # Outcome labels for summaries.
    if not rule_df.empty:
        def _outcome(r: pd.Series) -> str:
            if not bool(r.get("rule_parseable_after_fix", False)):
                return "Not parseable after rule fix"
            gain = r.get("rule_pass_gain_vs_original_selected")
            if gain is None or pd.isna(gain):
                return "Parse rescued (no re-eval score)"
            if int(gain) <= 0:
                return "Parse rescued, no test-pass gain"
            if bool(r.get("rule_reeval_all_pass", False)):
                return "Parse rescued, full pass after rule fix"
            return "Parse rescued, some test-pass gain"

        rule_df["rule_repair_outcome"] = rule_df.apply(_outcome, axis=1)

    rule_df.to_csv(OUT_DIR / "syntax_repair_rule_based_rows.csv", index=False)

    # Split exports for prompt tracks.
    rule_a = rule_df[rule_df["track"] == TRACK_A_SUBMITTERS].copy()
    rule_b = rule_df[rule_df["track"] == TRACK_B].copy()
    rule_a.to_csv(OUT_DIR / "syntax_repair_rule_based_track_a_rows.csv", index=False)
    rule_b.to_csv(OUT_DIR / "syntax_repair_rule_based_track_b_rows.csv", index=False)

    # Summaries by track and structural subtype
    summary_rows: list[dict[str, Any]] = []
    for name, part in [("Track A submissions (private)", rule_a), ("Track B best snapshot (public)", rule_b)]:
        if part.empty:
            summary_rows.append({"track_analysis": name, "rows": 0})
            continue
        n = len(part)
        parse_rescued = int(part["rule_parseable_after_fix"].fillna(False).sum())
        pass_gain_rows = int((pd.to_numeric(part["rule_pass_gain_vs_original_selected"], errors="coerce").fillna(0) > 0).sum())
        full_pass_rows = int(part["rule_reeval_all_pass"].fillna(False).sum())
        summary_rows.append(
            {
                "track_analysis": name,
                "rows": n,
                "parse_rescued_rows": parse_rescued,
                "pct_parse_rescued": round(100.0 * parse_rescued / n, 2),
                "test_pass_gain_rows": pass_gain_rows,
                "pct_test_pass_gain": round(100.0 * pass_gain_rows / n, 2),
                "full_pass_after_rule_fix_rows": full_pass_rows,
                "pct_full_pass_after_rule_fix": round(100.0 * full_pass_rows / n, 2),
                "mean_pass_gain": round(
                    float(pd.to_numeric(part["rule_pass_gain_vs_original_selected"], errors="coerce").dropna().mean()), 3
                )
                if pd.to_numeric(part["rule_pass_gain_vs_original_selected"], errors="coerce").notna().any()
                else np.nan,
                "mean_score_gain": round(
                    float(pd.to_numeric(part["rule_score_gain_vs_original_selected"], errors="coerce").dropna().mean()), 3
                )
                if pd.to_numeric(part["rule_score_gain_vs_original_selected"], errors="coerce").notna().any()
                else np.nan,
            }
        )
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "syntax_repair_rule_based_summary.csv", index=False)

    # More detailed summaries requested for partial-broken vs fundamental comparison
    if not rule_df.empty:
        (
            rule_df.groupby(["track", "skeleton_modification_status", "rule_repair_outcome"], dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values(["track", "skeleton_modification_status", "rows"], ascending=[True, True, False])
            .to_csv(OUT_DIR / "syntax_repair_rule_based_outcomes_by_structural_status.csv", index=False)
        )

    return rule_a, rule_b


def write_llm_skip_outputs(selected: pd.DataFrame) -> None:
    print("[5/10] Writing LLM syntax-correction skip summaries (no API key configured)...")
    targets = selected[
        (selected["track"].isin([TRACK_A_SUBMITTERS, TRACK_B]))
        & (selected["is_python_question"] == True)  # noqa: E712
        & (selected["ast_parseable_recheck"] == False)  # noqa: E712
    ].copy()
    rows = []
    for track in [TRACK_A_SUBMITTERS, TRACK_B]:
        g = targets[targets["track"] == track]
        rows.append(
            {
                "track": track,
                "target_rows": int(len(g)),
                "status": "skipped_no_api_key",
                "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")),
                "anthropic_api_key_present": bool(os.environ.get("ANTHROPIC_API_KEY")),
                "gemini_api_key_present": bool(os.environ.get("GEMINI_API_KEY")),
                "note": "LLM correction pipeline intentionally not run because no non-empty API key is configured in this environment.",
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "syntax_repair_llm_summary.csv", index=False)
    # Comparison file stub so README/process remains reproducible.
    pd.DataFrame(
        [
            {
                "comparison": "rule_based_vs_llm",
                "status": "llm_skipped",
                "rule_based_summary_file": "syntax_repair_rule_based_summary.csv",
                "llm_summary_file": "syntax_repair_llm_summary.csv",
            }
        ]
    ).to_csv(OUT_DIR / "syntax_repair_comparison_summary.csv", index=False)


def build_gating_waterfall(
    selected: pd.DataFrame,
    best_public: pd.DataFrame,
    regression: pd.DataFrame,
    private_final: pd.DataFrame,
) -> pd.DataFrame:
    print("[6/10] Building gating waterfall decomposition (4f)...")
    df = selected.copy()
    for c in ["problem_id"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    join_cols = ["namespace", "problem_id", "student_id"]
    bp = best_public[[
        *join_cols,
        "best_public_summary",
        "best_public_num_test_passed",
        "best_public_test_case_count",
        "best_public_wrong_output_subtype",
        "best_public_runtime_error_type",
    ]].copy()
    bp["problem_id"] = pd.to_numeric(bp["problem_id"], errors="coerce").astype("Int64")
    df = df.merge(bp, on=join_cols, how="left")

    pf = private_final[[
        *join_cols,
        "private_summary",
        "private_num_cases",
        "private_num_passed",
        "private_wrong_output_subtype",
        "private_runtime_error_type",
        "formatting_full_row_rescue_whitespace_norm",
    ]].copy()
    pf["problem_id"] = pd.to_numeric(pf["problem_id"], errors="coerce").astype("Int64")
    df = df.merge(pf, on=join_cols, how="left")

    # Optional regression flags for reference in row-level export.
    reg = regression[[*join_cols, "parseability_regression_flag", "peak_to_last_public_regression_flag", "structural_regression_vs_last_parseable_flag"]].copy()
    reg["problem_id"] = pd.to_numeric(reg["problem_id"], errors="coerce").astype("Int64")
    df = df.merge(reg, on=join_cols, how="left")

    def assign_gate(row: pd.Series) -> str:
        status = row.get("skeleton_modification_status")
        ast_parse = bool(row.get("ast_parseable_recheck", False))
        track = row.get("track")
        outcome = row.get("outcome_category")

        # 1) Non-attempt / trivial
        if status in {"Unmodified skeleton", "Empty / trivial"}:
            return "Unmodified skeleton / didn't attempt"

        # 2-3) Syntax gated split
        if (not ast_parse) and status == "Modified, partially broken":
            return "Syntax gated — mechanical"
        if (not ast_parse) and status == "Modified, fundamentally broken":
            return "Syntax gated — fundamental"

        # 7-8) Final scored outcomes for submitters (private) where available.
        if track == TRACK_A_SUBMITTERS:
            if outcome == "Full pass":
                return "Full pass"
            if outcome == "Partial pass":
                return "Partial pass"

            # Submitted-zero and other failures need decomposition from private final test results.
            if bool(row.get("formatting_full_row_rescue_whitespace_norm", False)):
                return "Formatting gated"
            priv_summary = row.get("private_summary")
            if priv_summary == "Wrong Answer":
                subtype = row.get("private_wrong_output_subtype")
                if subtype == "Wrong output - formatting":
                    return "Formatting gated"
                if subtype == "Wrong output - partial correctness":
                    return "Edge-case gated"
                return "Genuine logic failure"
            if priv_summary in {"Runtime Error", "Time Limit Exceeded", "Not able to run"}:
                return "Genuine logic failure"
            if outcome == "Submitted, zero":
                return "Genuine logic failure"
            # Fallback (rare)
            return "Genuine logic failure"

        # Non-submitters (Track A non-submitters and Track B) use best public snapshot.
        bp_summary = row.get("best_public_summary")
        bp_passed = row.get("best_public_num_test_passed")
        bp_cases = row.get("best_public_test_case_count")
        if bp_summary == "All Cases Passed":
            return "Full pass"
        if bp_summary == "Wrong Answer":
            subtype = row.get("best_public_wrong_output_subtype")
            if subtype == "Wrong output - formatting":
                return "Formatting gated"
            if subtype == "Wrong output - partial correctness":
                return "Edge-case gated"
            return "Genuine logic failure"
        if bp_summary in {"Runtime Error", "Time Limit Exceeded", "Not able to run"}:
            return "Genuine logic failure"

        # If parseable and some public cases passed, call it edge-case/partial correctness proxy.
        try:
            if bp_passed is not None and bp_cases is not None and not pd.isna(bp_passed) and not pd.isna(bp_cases):
                bp_passed_i = int(bp_passed)
                bp_cases_i = int(bp_cases)
                if bp_cases_i > 0 and 0 < bp_passed_i < bp_cases_i:
                    return "Edge-case gated"
        except Exception:
            pass
        return "Genuine logic failure"

    df["waterfall_gate"] = df.apply(assign_gate, axis=1)
    df.to_csv(OUT_DIR / "gating_waterfall_rows.csv", index=False)

    # Track grouping for prompt table.
    df["waterfall_track_group"] = np.where(df["track"] == TRACK_B, "Track B", "Track A")

    order = [
        "Unmodified skeleton / didn't attempt",
        "Syntax gated — mechanical",
        "Syntax gated — fundamental",
        "Formatting gated",
        "Edge-case gated",
        "Genuine logic failure",
        "Partial pass",
        "Full pass",
    ]

    rows = []
    for gate in order:
        mask = df["waterfall_gate"] == gate
        rows.append(
            {
                "gate": gate,
                "Track A": int((mask & (df["waterfall_track_group"] == "Track A")).sum()),
                "Track B": int((mask & (df["waterfall_track_group"] == "Track B")).sum()),
                "Combined": int(mask.sum()),
            }
        )
    waterfall = pd.DataFrame(rows)
    waterfall.to_csv(OUT_DIR / "gating_waterfall_counts.csv", index=False)

    # Percent version.
    totals = {
        "Track A": int((df["waterfall_track_group"] == "Track A").sum()),
        "Track B": int((df["waterfall_track_group"] == "Track B").sum()),
        "Combined": int(len(df)),
    }
    pct = waterfall.copy()
    for col in ["Track A", "Track B", "Combined"]:
        denom = totals[col]
        pct[col] = pct[col].apply(lambda x: round(100.0 * x / denom, 2) if denom else np.nan)
    pct.to_csv(OUT_DIR / "gating_waterfall_pct.csv", index=False)

    return df


def build_skeleton_effectiveness_analysis(
    conn: duckdb.DuckDBPyConnection,
    selected: pd.DataFrame,
    skeleton_map: dict[tuple[str, int], SkeletonInfo],
) -> None:
    print("[7/10] Building skeleton effectiveness analysis (4g)...")
    # Relationship between modification extent and error rate.
    df = selected[selected["is_python_question"] == True].copy()  # noqa: E712
    if df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "skeleton_effectiveness_error_rate_by_modification_extent.csv", index=False)
        pd.DataFrame().to_csv(OUT_DIR / "skeleton_effectiveness_error_location_summary.csv", index=False)
        return

    df["ast_nonparseable"] = ~df["ast_parseable_recheck"].fillna(False).astype(bool)
    df["ts_broken"] = (df["ts_error_count"].fillna(0) > 0) | (df["ts_missing_token_count"].fillna(0) > 0)
    df["meaningful_lines_beyond_skeleton"] = pd.to_numeric(df["meaningful_lines_beyond_skeleton"], errors="coerce").fillna(0)
    df["new_constructs_added"] = pd.to_numeric(df["new_constructs_added"], errors="coerce").fillna(0)

    def _bin_lines(x: float) -> str:
        x = int(x)
        if x == 0:
            return "0"
        if x <= 2:
            return "1-2"
        if x <= 5:
            return "3-5"
        if x <= 10:
            return "6-10"
        return "11+"

    def _bin_constructs(x: float) -> str:
        x = int(x)
        if x == 0:
            return "0"
        if x == 1:
            return "1"
        if x <= 3:
            return "2-3"
        if x <= 6:
            return "4-6"
        return "7+"

    df["mod_extent_lines_bin"] = df["meaningful_lines_beyond_skeleton"].apply(_bin_lines)
    df["mod_extent_constructs_bin"] = df["new_constructs_added"].apply(_bin_constructs)

    rate_rows = []
    for (track, bin_type, bin_val), g in pd.concat(
        [
            df.assign(mod_bin_type="meaningful_lines_beyond_skeleton", mod_bin_value=df["mod_extent_lines_bin"]),
            df.assign(mod_bin_type="new_constructs_added", mod_bin_value=df["mod_extent_constructs_bin"]),
        ],
        ignore_index=True,
    ).groupby(["track", "mod_bin_type", "mod_bin_value"], dropna=False):
        n = len(g)
        rate_rows.append(
            {
                "track": track,
                "modification_measure": bin_type,
                "bin": bin_val,
                "rows": n,
                "ast_nonparseable_rows": int(g["ast_nonparseable"].sum()),
                "pct_ast_nonparseable": round(100.0 * float(g["ast_nonparseable"].sum()) / n, 2),
                "ts_broken_rows": int(g["ts_broken"].sum()),
                "pct_ts_broken": round(100.0 * float(g["ts_broken"].sum()) / n, 2),
            }
        )
    pd.DataFrame(rate_rows).sort_values(["track", "modification_measure", "bin"]).to_csv(
        OUT_DIR / "skeleton_effectiveness_error_rate_by_modification_extent.csv", index=False
    )

    # Error location vs skeleton/additions (line-position proxy using all ERROR nodes on selected syntax-error rows).
    syntax_rows = df[df["ast_nonparseable"]].copy()
    if syntax_rows.empty:
        pd.DataFrame().to_csv(OUT_DIR / "skeleton_effectiveness_error_location_summary.csv", index=False)
        return

    code_map = fetch_code_map_for_hashes(conn, [str(x) for x in syntax_rows["code_sha256"].dropna().tolist()])
    analyzer = TsAnalyzer()

    # We need raw error node lines; TsAnalyzer doesn't expose them, so parse directly with its parser.
    line_loc_rows: list[dict[str, Any]] = []
    for rec in syntax_rows.itertuples(index=False):
        key = (str(rec.namespace), int(rec.problem_id))
        sk = skeleton_map.get(key)
        if sk is None or not sk.is_python:
            continue
        full_code = code_map.get(str(rec.code_sha256))
        if full_code is None:
            continue
        student_code, _ = extract_student_editable_code(full_code, sk)
        source = student_code.encode("utf-8", errors="replace")
        tree = analyzer.parser.parse(source)
        student_lines = student_code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        sk_lines = (sk.skeleton_code or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            if node.type == "ERROR":
                line_no = int(node.start_point[0]) + 1
                sline = student_lines[line_no - 1] if 0 <= line_no - 1 < len(student_lines) else ""
                in_skeleton_line_range = line_no <= len(sk_lines)
                sk_line = sk_lines[line_no - 1] if in_skeleton_line_range else ""
                s_norm = sline.strip()
                sk_norm = sk_line.strip()
                if in_skeleton_line_range and s_norm and (s_norm == sk_norm):
                    loc = "skeleton_unchanged_line"
                elif in_skeleton_line_range:
                    loc = "skeleton_line_modified"
                else:
                    loc = "beyond_skeleton_line_range"
                line_loc_rows.append(
                    {
                        "track": rec.track,
                        "namespace": rec.namespace,
                        "problem_id": int(rec.problem_id),
                        "student_id": rec.student_id,
                        "syntax_error_category": rec.syntax_error_category,
                        "error_line_location_proxy": loc,
                    }
                )
            for child in reversed(node.children):
                stack.append(child)

    loc_df = pd.DataFrame(line_loc_rows)
    if loc_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "skeleton_effectiveness_error_location_summary.csv", index=False)
    else:
        (
            loc_df.groupby(["track", "syntax_error_category", "error_line_location_proxy"], dropna=False)
            .size()
            .reset_index(name="error_nodes")
            .sort_values(["track", "syntax_error_category", "error_nodes"], ascending=[True, True, False])
            .to_csv(OUT_DIR / "skeleton_effectiveness_error_location_summary.csv", index=False)
        )
        (
            loc_df.groupby(["track", "error_line_location_proxy"], dropna=False)
            .size()
            .reset_index(name="error_nodes")
            .sort_values(["track", "error_nodes"], ascending=[True, False])
            .to_csv(OUT_DIR / "skeleton_effectiveness_error_location_summary_track_only.csv", index=False)
        )


def build_syntax_bottleneck_decomposition_tables(
    selected: pd.DataFrame,
    rule_a: pd.DataFrame,
    rule_b: pd.DataFrame,
) -> None:
    print("[8/10] Building syntax bottleneck decomposition summary tables...")
    # 4a + 4b + repairs + formatting tax are already exported; add compact track decomposition dashboard.
    rows = []
    for track in [TRACK_A_SUBMITTERS, TRACK_A_NON_SUBMIT, TRACK_B]:
        g = selected[(selected["track"] == track) & (selected["is_python_question"] == True)].copy()  # noqa: E712
        if g.empty:
            continue
        n = len(g)
        rows.append(
            {
                "track": track,
                "python_rows": n,
                "unmodified_or_empty": int(g["skeleton_modification_status"].isin(["Unmodified skeleton", "Empty / trivial"]).sum()),
                "syntax_mechanical": int(((g["ast_parseable_recheck"] == False) & (g["skeleton_modification_status"] == "Modified, partially broken")).sum()),
                "syntax_fundamental": int(((g["ast_parseable_recheck"] == False) & (g["skeleton_modification_status"] == "Modified, fundamentally broken")).sum()),
                "parseable_ast": int(g["ast_parseable_recheck"].fillna(False).sum()),
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "syntax_bottleneck_decomposition_by_track.csv", index=False)

    # Rule-based repair effect compact table by structural subtype.
    rule_all = pd.concat([rule_a, rule_b], ignore_index=True)
    if not rule_all.empty:
        tmp = rule_all.copy()
        tmp["parse_rescued"] = tmp["rule_parseable_after_fix"].fillna(False)
        tmp["test_pass_gain"] = pd.to_numeric(tmp["rule_pass_gain_vs_original_selected"], errors="coerce").fillna(0) > 0
        (
            tmp.groupby(["track", "skeleton_modification_status"], dropna=False)
            .agg(
                rows=("student_id", "count"),
                parse_rescued_rows=("parse_rescued", "sum"),
                test_pass_gain_rows=("test_pass_gain", "sum"),
            )
            .reset_index()
            .assign(
                pct_parse_rescued=lambda x: (100 * x["parse_rescued_rows"] / x["rows"]).round(2),
                pct_test_pass_gain=lambda x: (100 * x["test_pass_gain_rows"] / x["rows"]).round(2),
            )
            .to_csv(OUT_DIR / "syntax_repair_rule_based_effect_by_structural_status.csv", index=False)
        )


def write_manifest() -> None:
    print("[9/10] Writing manifest...")
    files = []
    for p in sorted(OUT_DIR.rglob("*")):
        if p.is_file():
            files.append({"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size})
    pd.DataFrame(files).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = make_conn()

    selected, best_public, regression = load_step3_tables()
    build_parseability_baseline(selected)
    build_regression_summary(regression)

    # Load question structures/runtime configs once.
    _, skeleton_map = load_question_skeletons()
    qcfg_map = load_question_runtime_configs()

    private_final = build_track_a_private_final_results(conn, selected)
    rule_a, rule_b = run_rule_based_syntax_repair_eval(conn, selected, skeleton_map, qcfg_map)
    write_llm_skip_outputs(selected)
    build_gating_waterfall(selected, best_public, regression, private_final)
    build_skeleton_effectiveness_analysis(conn, selected, skeleton_map)
    build_syntax_bottleneck_decomposition_tables(selected, rule_a, rule_b)
    write_manifest()

    print("[10/10] Done.")
    print(f"Outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
