#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "pandas>=2.2.0",
# ]
# ///

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
TIMELINE_PARQUET = ANALYSIS_DIR / "submission_timeline.parquet"
PROBLEMS_DIR = ROOT / "problems"

OUT_CSV = ANALYSIS_DIR / "no-private-submissions.csv"
OUT_MD = ANALYSIS_DIR / "no-private-submissions.md"
NS_RE = re.compile(r"^ns_(?P<term>[^_]+)_py(?P<wave_num>\d)")


def sql_quote_path(path: Path) -> str:
    return str(path).replace("'", "''")


def parse_namespace_term_wave(namespace: str) -> tuple[str, str]:
    m = NS_RE.match(str(namespace or ""))
    if not m:
        return "", ""
    return m.group("term") or "", f"wave{m.group('wave_num') or ''}"


def load_question_title(namespace: str, problem_id: int | str) -> str:
    p = PROBLEMS_DIR / str(namespace) / f"{int(problem_id)}.json"
    if not p.exists():
        return ""
    try:
        obj = json.loads(p.read_text())
    except Exception:
        return ""
    short = str(obj.get("short_description") or "").strip()
    if short:
        return short
    q = str(obj.get("question") or "").strip()
    if not q:
        return ""
    text = re.sub(r"<[^>]+>", " ", q)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180]


def fmt_int(x: int | float | None) -> str:
    if x is None or pd.isna(x):
        return "0"
    return f"{int(x):,}"


def fmt_pct(num: int | float, den: int | float) -> str:
    if not den:
        return "0.0%"
    return f"{(100.0 * float(num) / float(den)):.1f}%"


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        cells: list[str] = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                cells.append("")
            else:
                s = str(v).replace("\n", " ").replace("|", "\\|")
                cells.append(s)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def sample_ids(series: pd.Series, n: int = 5) -> str:
    ids = sorted({str(x) for x in series.dropna().tolist()})
    return ", ".join(ids[:n]) if ids else "-"


def _fmt_ts(ts: object) -> str:
    if ts is None or pd.isna(ts):
        return ""
    try:
        return pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def fetch_student_question_history(
    conn: duckdb.DuckDBPyConnection, *, namespace: str, problem_id: int, student_id: str
) -> pd.DataFrame:
    q = conn.execute(
        """
        SELECT
          timestamp_utc,
          event_type,
          evaluation_type,
          summary,
          score,
          num_test_passed,
          num_test_evaluated
        FROM read_parquet(?)
        WHERE namespace = ?
          AND problem_id = ?
          AND student_id = ?
        ORDER BY timestamp_utc
        """,
        [str(TIMELINE_PARQUET), namespace, int(problem_id), student_id],
    ).df()
    if q.empty:
        return q
    q = q.copy()
    q["timestamp_utc"] = q["timestamp_utc"].map(_fmt_ts)
    q.insert(0, "step", range(1, len(q) + 1))
    q.rename(
        columns={
            "timestamp_utc": "timestamp_utc",
            "event_type": "event",
            "evaluation_type": "eval_type",
            "summary": "result_summary",
            "score": "score",
            "num_test_passed": "tests_passed",
            "num_test_evaluated": "tests_total",
        },
        inplace=True,
    )
    return q


def compact_history_for_markdown(df: pd.DataFrame, max_rows: int = 24) -> pd.DataFrame:
    if df.empty or len(df) <= max_rows:
        return df
    head_n = max_rows // 2
    tail_n = max_rows - head_n
    head = df.head(head_n).copy()
    tail = df.tail(tail_n).copy()
    omitted = len(df) - len(head) - len(tail)
    marker = {c: "" for c in df.columns}
    marker[df.columns[0]] = "..."
    marker[df.columns[1]] = f"... {omitted} intermediate events omitted ..."
    marker_df = pd.DataFrame([marker], columns=df.columns)
    out = pd.concat([head, marker_df, tail], ignore_index=True)
    return out


def build_views(conn: duckdb.DuckDBPyConnection) -> None:
    timeline = sql_quote_path(TIMELINE_PARQUET)
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW attempts AS
        SELECT
          namespace,
          problem_id,
          student_id,
          COUNT(*) FILTER (WHERE event_type = 'saved_code') AS saved_code_events,
          COUNT(*) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS public_test_run_events,
          COUNT(*) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'private') AS private_test_run_events,
          COUNT(*) FILTER (WHERE event_type = 'submission' AND evaluation_type = 'private') AS private_submission_events,
          MIN(timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS first_public_test_run_utc,
          MAX(timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS last_public_test_run_utc,
          ARG_MAX(score, timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS latest_public_score,
          ARG_MAX(summary, timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS latest_public_summary,
          ARG_MAX(num_test_passed, timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS latest_public_num_test_passed,
          ARG_MAX(num_test_evaluated, timestamp_utc) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS latest_public_num_test_evaluated,
          MAX(num_test_passed) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS best_public_num_test_passed,
          MAX(num_test_evaluated) FILTER (WHERE event_type = 'test_run' AND evaluation_type = 'public') AS best_public_test_case_count
        FROM read_parquet('{timeline}')
        GROUP BY 1,2,3
        """
    )

    conn.execute(
        """
        CREATE OR REPLACE TEMP VIEW namespace_private_submission_events AS
        SELECT
          namespace,
          SUM(private_submission_events) AS namespace_private_submission_events
        FROM attempts
        GROUP BY 1
        """
    )


def export_detail_csv(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = conn.execute(
        """
        SELECT
          a.namespace,
          a.problem_id,
          a.student_id,
          a.public_test_run_events,
          a.private_test_run_events,
          a.private_submission_events,
          a.saved_code_events,
          a.first_public_test_run_utc,
          a.last_public_test_run_utc,
          a.latest_public_summary,
          a.latest_public_score,
          a.latest_public_num_test_passed,
          a.latest_public_num_test_evaluated,
          a.best_public_num_test_passed,
          a.best_public_test_case_count,
          CASE
            WHEN a.best_public_test_case_count > 0
            THEN ROUND(100.0 * a.best_public_num_test_passed / a.best_public_test_case_count, 2)
            ELSE NULL
          END AS best_public_score_pct,
          CASE
            WHEN a.best_public_test_case_count > 0 AND a.best_public_num_test_passed >= a.best_public_test_case_count THEN TRUE
            ELSE FALSE
          END AS best_public_all_pass,
          COALESCE(n.namespace_private_submission_events, 0) AS namespace_private_submission_events,
          CASE WHEN COALESCE(n.namespace_private_submission_events, 0) > 0 THEN TRUE ELSE FALSE END AS namespace_has_any_private_submission
        FROM attempts a
        LEFT JOIN namespace_private_submission_events n
          ON a.namespace = n.namespace
        WHERE a.public_test_run_events > 0
          AND a.private_submission_events = 0
        ORDER BY a.namespace, a.problem_id, a.student_id
        """
    ).df()

    # Enrich from namespace and local problem JSON metadata.
    term_wave = {ns: parse_namespace_term_wave(ns) for ns in df["namespace"].dropna().unique()}
    df["term"] = df["namespace"].map(lambda ns: term_wave.get(ns, ("", ""))[0])
    df["wave"] = df["namespace"].map(lambda ns: term_wave.get(ns, ("", ""))[1])

    titles: dict[tuple[str, int], str] = {}
    for ns, pid in df[["namespace", "problem_id"]].drop_duplicates().itertuples(index=False):
        try:
            key = (str(ns), int(pid))
        except Exception:
            key = (str(ns), int(float(pid)))
        titles[key] = load_question_title(key[0], key[1])
    df["question_title"] = [
        titles.get((str(ns), int(pid)), "")
        for ns, pid in df[["namespace", "problem_id"]].itertuples(index=False)
    ]

    ordered = [
        "namespace",
        "problem_id",
        "question_title",
        "term",
        "wave",
        "student_id",
        "public_test_run_events",
        "private_test_run_events",
        "private_submission_events",
        "saved_code_events",
        "first_public_test_run_utc",
        "last_public_test_run_utc",
        "latest_public_summary",
        "latest_public_score",
        "latest_public_num_test_passed",
        "latest_public_num_test_evaluated",
        "best_public_num_test_passed",
        "best_public_test_case_count",
        "best_public_score_pct",
        "best_public_all_pass",
        "namespace_private_submission_events",
        "namespace_has_any_private_submission",
    ]
    df = df[ordered]
    df.to_csv(OUT_CSV, index=False)
    return df


def build_markdown(conn: duckdb.DuckDBPyConnection, detail_df: pd.DataFrame) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total_student_question = int(conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0])
    total_students = int(conn.execute("SELECT COUNT(DISTINCT student_id) FROM attempts").fetchone()[0])
    total_namespaces = int(conn.execute("SELECT COUNT(DISTINCT namespace) FROM attempts").fetchone()[0])
    total_questions = int(conn.execute("SELECT COUNT(DISTINCT namespace || '::' || CAST(problem_id AS VARCHAR)) FROM attempts").fetchone()[0])

    strict_public_submission_events = int(
        conn.execute(
            """
            SELECT COUNT(*)
            FROM read_parquet(?)
            WHERE event_type = 'submission' AND evaluation_type = 'public'
            """,
            [str(TIMELINE_PARQUET)],
        ).fetchone()[0]
    )

    affected_rows = len(detail_df)
    affected_students = detail_df["student_id"].nunique()
    affected_namespaces = detail_df["namespace"].nunique()
    affected_questions = detail_df[["namespace", "problem_id"]].drop_duplicates().shape[0]

    # Namespace-level student summary.
    attempts_df = conn.execute(
        """
        SELECT namespace, problem_id, student_id, public_test_run_events, private_submission_events
        FROM attempts
        """
    ).df()

    student_ns = (
        attempts_df.groupby(["namespace", "student_id"], as_index=False)
        .agg(
            public_test_run_events=("public_test_run_events", "sum"),
            private_submission_events=("private_submission_events", "sum"),
        )
    )
    student_ns["only_public_in_namespace"] = (
        (student_ns["public_test_run_events"] > 0) & (student_ns["private_submission_events"] == 0)
    )
    student_ns["has_any_private_in_namespace"] = student_ns["private_submission_events"] > 0

    affected_ns_students = detail_df[["namespace", "student_id"]].drop_duplicates()
    affected_ns_students["has_affected_question"] = True

    ns_summary = (
        student_ns.groupby("namespace", as_index=False)
        .agg(
            total_students=("student_id", "nunique"),
            students_only_public_in_namespace=("only_public_in_namespace", "sum"),
            students_with_any_private_in_namespace=("has_any_private_in_namespace", "sum"),
        )
        .merge(
            affected_ns_students.groupby("namespace", as_index=False).agg(
                students_with_at_least_one_public_only_question=("has_affected_question", "sum")
            ),
            on="namespace",
            how="left",
        )
    )
    ns_summary["students_with_at_least_one_public_only_question"] = ns_summary[
        "students_with_at_least_one_public_only_question"
    ].fillna(0).astype(int)
    ns_rows = (
        detail_df.groupby("namespace", as_index=False)
        .agg(
            public_only_question_rows=("student_id", "size"),
            unique_students_in_public_only_rows=("student_id", "nunique"),
        )
        .astype({"public_only_question_rows": int, "unique_students_in_public_only_rows": int})
    )
    ns_examples = (
        detail_df.groupby("namespace", as_index=False)
        .agg(example_student_ids=("student_id", lambda s: sample_ids(s, n=5)))
    )
    ns_private_events = (
        detail_df.groupby("namespace", as_index=False)
        .agg(namespace_private_submission_events=("namespace_private_submission_events", "max"))
    )

    ns_summary = (
        ns_summary.merge(ns_rows, on="namespace", how="left")
        .merge(ns_examples, on="namespace", how="left")
        .merge(ns_private_events, on="namespace", how="left")
    )
    ns_summary["public_only_student_pct"] = (
        100.0 * ns_summary["students_only_public_in_namespace"] / ns_summary["total_students"].clip(lower=1)
    )
    ns_summary["namespace_type"] = ns_summary["namespace_private_submission_events"].fillna(0).map(
        lambda x: "Zero-private namespace (Track B-like)" if x == 0 else "Mixed namespace (Track A-like)"
    )
    ns_summary = ns_summary.sort_values(
        ["students_only_public_in_namespace", "total_students", "namespace"], ascending=[False, False, True]
    )

    # Distribution: how many question-combos per student are public-only.
    per_student_counts = (
        detail_df.groupby("student_id", as_index=False).size().rename(columns={"size": "public_only_question_count"})
    )
    dist = (
        per_student_counts.groupby("public_only_question_count", as_index=False)
        .agg(students=("student_id", "size"))
        .sort_values("public_only_question_count")
    )
    dist["pct_of_affected_students"] = 100.0 * dist["students"] / max(len(per_student_counts), 1)

    ex_by_k = (
        per_student_counts.groupby("public_only_question_count", as_index=False)
        .agg(example_student_ids=("student_id", lambda s: sample_ids(s, n=5)))
    )
    dist = dist.merge(ex_by_k, on="public_only_question_count", how="left")

    # Public-score distribution for affected rows.
    score_df = detail_df.copy()
    score_df["score_bucket"] = "Missing public score"
    score_df.loc[score_df["best_public_score_pct"] == 0, "score_bucket"] = "0%"
    score_df.loc[
        (score_df["best_public_score_pct"] > 0) & (score_df["best_public_score_pct"] < 100), "score_bucket"
    ] = "Partial (0-100)"
    score_df.loc[score_df["best_public_score_pct"] == 100, "score_bucket"] = "100%"
    score_dist = (
        score_df.groupby("score_bucket", as_index=False)
        .agg(rows=("student_id", "size"))
        .sort_values("rows", ascending=False)
    )
    score_dist["pct_of_public_only_rows"] = 100.0 * score_dist["rows"] / max(len(score_df), 1)

    class_summary = (
        detail_df.assign(
            namespace_type=detail_df["namespace_has_any_private_submission"].map(
                lambda b: "Mixed namespace (Track A-like)" if bool(b) else "Zero-private namespace (Track B-like)"
            )
        )
        .groupby("namespace_type", as_index=False)
        .agg(
            public_only_rows=("student_id", "size"),
            unique_students=("student_id", "nunique"),
            namespaces=("namespace", "nunique"),
            rows_with_100_public=("best_public_all_pass", "sum"),
        )
    )
    class_summary["pct_rows_with_100_public"] = 100.0 * class_summary["rows_with_100_public"] / class_summary[
        "public_only_rows"
    ].clip(lower=1)

    # Top question combos.
    top_q = (
        detail_df.groupby(["namespace", "problem_id", "question_title"], as_index=False)
        .agg(
            public_only_rows=("student_id", "size"),
            unique_students=("student_id", "nunique"),
            rows_with_100_public=("best_public_all_pass", "sum"),
        )
        .sort_values(["public_only_rows", "unique_students"], ascending=[False, False])
        .head(20)
    )
    top_q["pct_rows_with_100_public"] = 100.0 * top_q["rows_with_100_public"] / top_q["public_only_rows"].clip(lower=1)
    top_q_examples = (
        detail_df.merge(top_q[["namespace", "problem_id"]], on=["namespace", "problem_id"], how="inner")
        .groupby(["namespace", "problem_id"], as_index=False)
        .agg(example_student_ids=("student_id", lambda s: sample_ids(s, n=3)))
    )
    top_q = top_q.merge(top_q_examples, on=["namespace", "problem_id"], how="left")

    # Representative real examples for clarification.
    # Prefer moderate event histories for readability.
    moderate = detail_df[(detail_df["public_test_run_events"] >= 2) & (detail_df["public_test_run_events"] <= 12)]
    # 1) Track B-like namespace (no private submissions captured at namespace level).
    ex_track_b = (
        moderate[
            (moderate["namespace_has_any_private_submission"] == False)
            & (moderate["best_public_all_pass"] == True)
        ]
        .sort_values(["public_test_run_events", "best_public_score_pct"], ascending=[False, False])
        .head(1)
    )
    if ex_track_b.empty:
        ex_track_b = (
            detail_df[detail_df["namespace_has_any_private_submission"] == False]
            .sort_values(["public_test_run_events", "best_public_score_pct"], ascending=[True, False])
            .head(1)
        )

    # 2) Mixed namespace row where this student-question is public-only.
    ex_mixed = (
        moderate[(moderate["namespace_has_any_private_submission"] == True)]
        .sort_values(["public_test_run_events", "best_public_score_pct"], ascending=[False, False])
        .head(1)
    )
    if ex_mixed.empty:
        ex_mixed = (
            detail_df[detail_df["namespace_has_any_private_submission"] == True]
            .sort_values(["public_test_run_events", "best_public_score_pct"], ascending=[True, False])
            .head(1)
        )

    # 3) Row with private test-runs but still no private submission event.
    ex_private_runs_no_submit = (
        moderate[(moderate["private_test_run_events"] > 0)]
        .sort_values(["private_test_run_events", "public_test_run_events"], ascending=[False, False])
        .head(1)
    )
    if ex_private_runs_no_submit.empty:
        ex_private_runs_no_submit = (
            detail_df[detail_df["private_test_run_events"] > 0]
            .sort_values(["private_test_run_events", "public_test_run_events"], ascending=[False, False])
            .head(1)
        )

    example_rows = pd.concat(
        [ex_track_b, ex_mixed, ex_private_runs_no_submit], ignore_index=True
    ).drop_duplicates(subset=["namespace", "problem_id", "student_id"])

    lines: list[str] = []
    lines.append("# No-Private Submissions Report")
    lines.append("")
    lines.append("## Quick Summary for Administrators (ELI15)")
    lines.append("")
    lines.append("Think of the coding system as having two checkpoints:")
    lines.append("")
    lines.append("- **Public checks**: practice checks students run while working.")
    lines.append("- **Private checks**: hidden final checks used for official grading.")
    lines.append("")
    lines.append(
        "In this report, a “public-only” attempt means the student ran public checks for a question but has **no private submission event** for that same question."
    )
    lines.append("")
    lines.append("### What This Means")
    lines.append("")
    lines.append(
        "- We can confirm the student was active on that question, but we cannot confirm private-evaluator performance for that question."
    )
    lines.append(
        "- A high public score without a private submission may indicate: workflow confusion, no final submit action, or namespace-level capture issues."
    )
    lines.append(
        "- So this metric is both a **learning-behavior signal** and a potential **platform instrumentation signal**."
    )
    lines.append("")
    lines.append("### Simple Findings")
    lines.append("")
    lines.append(
        f"- Public-only student-question rows: **{fmt_int(affected_rows)}** out of **{fmt_int(total_student_question)}** ({fmt_pct(affected_rows, total_student_question)})."
    )
    lines.append(f"- Unique students represented: **{fmt_int(affected_students)}**.")
    lines.append(f"- Namespaces represented: **{fmt_int(affected_namespaces)}**.")
    lines.append(
        f"- Namespaces with zero private submissions at namespace level: **{fmt_int(int((ns_summary['namespace_type'] == 'Zero-private namespace (Track B-like)').sum()))}** of **{fmt_int(len(ns_summary))}**."
    )
    if not score_dist.empty:
        sb = {r["score_bucket"]: r["pct_of_public_only_rows"] for _, r in score_dist.iterrows()}
        lines.append(
            f"- Public score buckets on public-only rows: **100%: {sb.get('100%', 0):.1f}%**, **0%: {sb.get('0%', 0):.1f}%**, **Partial: {sb.get('Partial (0-100)', 0):.1f}%**."
        )
    lines.append("")
    lines.append("### Recommended Investigations / Actions")
    lines.append("")
    lines.append("1. **Audit private-submission capture first**")
    lines.append("   - Validate evaluator routing, namespace config, and ingestion for namespaces with zero private submissions.")
    lines.append("2. **Track funnel drop-offs**")
    lines.append("   - Monitor `public test_run -> private submission` conversion by namespace and wave.")
    lines.append("3. **Improve student workflow prompts**")
    lines.append("   - Show explicit warning when a student leaves with public runs but no private submission.")
    lines.append("4. **Teach public vs private test meaning explicitly**")
    lines.append("   - Reinforce that passing public tests is not equivalent to final graded success.")
    lines.append("5. **Separate platform risk from learning risk**")
    lines.append("   - Do not interpret public-only patterns as student performance alone in zero-private namespaces.")
    lines.append("")
    lines.append(f"Generated: `{now}`")
    lines.append("")
    lines.append("## Expert Framing (What We Checked First)")
    lines.append("")
    lines.append(
        "- **Event semantics check:** In this dataset, there are no `event_type='submission' AND evaluation_type='public'` events. Public-side attempts are logged as public `test_run` events."
    )
    lines.append(
        "- **Denominator integrity:** We report both student-question rows and unique students; these answer different questions."
    )
    lines.append(
        "- **Namespace instrumentation check:** We separate namespaces with zero private submissions at all (Track B-like) from mixed namespaces."
    )
    lines.append(
        "- **Behavior vs platform:** A student can be public-only for one question but still submit privately on others in the same namespace."
    )
    lines.append(
        "- **Public score caveat:** Public-best performance can overstate true mastery when private tests are absent."
    )
    lines.append("")
    lines.append("## Definitions Used")
    lines.append("")
    lines.append("- **Public-only student-question row (in CSV):** `public_test_run_events > 0` and `private_submission_events = 0`.")
    lines.append("- **Only-public student in namespace:** Student has at least one public test run in that namespace and **zero** private submissions across all questions in that namespace.")
    lines.append("- **Question combo:** one `(student_id, namespace, problem_id)` row.")
    lines.append("")
    lines.append("## Headline Numbers")
    lines.append("")
    lines.append(f"- Total student-question rows in timeline: **{fmt_int(total_student_question)}**")
    lines.append(f"- Total unique students in timeline: **{fmt_int(total_students)}**")
    lines.append(f"- Total namespaces: **{fmt_int(total_namespaces)}**")
    lines.append(f"- Total namespace-question combinations: **{fmt_int(total_questions)}**")
    lines.append(f"- Public `submission` events (strict): **{fmt_int(strict_public_submission_events)}**")
    lines.append(f"- Public-only rows exported to `analysis/no-private-submissions.csv`: **{fmt_int(affected_rows)}**")
    lines.append(f"- Unique students represented in public-only rows: **{fmt_int(affected_students)}**")
    lines.append(f"- Namespaces represented in public-only rows: **{fmt_int(affected_namespaces)}**")
    lines.append(f"- Namespace-question combinations represented in public-only rows: **{fmt_int(affected_questions)}**")
    lines.append("")

    lines.append("## Direct Clarification (Yes) + Real Examples")
    lines.append("")
    lines.append(
        "Yes. This report **does** include students who, for a specific `(namespace, question)`, ran public checks but made **no private submission** for that question."
    )
    lines.append(
        "In this dataset, public-side activity is logged as `test_run` (not `submission`), so “public submissions” here means public test-run attempts."
    )
    lines.append("")
    lines.append(
        f"- Count of such student-question rows: **{fmt_int(affected_rows)}** out of **{fmt_int(total_student_question)}** total rows ({fmt_pct(affected_rows, total_student_question)})."
    )
    lines.append(
        "- A student may still have private submissions on *other* questions; the condition is evaluated per `(student, namespace, question)`."
    )
    lines.append(
        "- Important nuance: `private_submission_events = 0` can still coexist with private `test_run` events; the report condition is specifically about missing private **submission** events."
    )
    lines.append("")

    for i, (_, r) in enumerate(example_rows.iterrows(), start=1):
        ns = str(r["namespace"])
        pid = int(r["problem_id"])
        sid = str(r["student_id"])
        history = fetch_student_question_history(conn, namespace=ns, problem_id=pid, student_id=sid)
        ns_type = "Zero-private namespace (Track B-like)" if not bool(r["namespace_has_any_private_submission"]) else "Mixed namespace (Track A-like)"
        lines.append(f"### Example {i}: `{sid}` on `{ns}/{pid}`")
        lines.append("")
        lines.append(f"- Namespace type: **{ns_type}**")
        lines.append(f"- Question title: **{str(r.get('question_title', '')).strip() or '(missing title)'}**")
        lines.append(f"- Public test runs: **{fmt_int(r['public_test_run_events'])}**")
        lines.append(f"- Private test runs: **{fmt_int(r['private_test_run_events'])}**")
        lines.append(f"- Private submissions: **{fmt_int(r['private_submission_events'])}**")
        lines.append(
            f"- Best public outcome: **{fmt_int(r['best_public_num_test_passed'])}/{fmt_int(r['best_public_test_case_count'])}** ({r['best_public_score_pct'] if pd.notna(r['best_public_score_pct']) else 'n/a'}%)"
        )
        lines.append("")
        lines.append("Submission history (event timeline for this exact student-question):")
        lines.append("")
        if history.empty:
            lines.append("_No timeline events found (unexpected)._")
        else:
            hist_out = compact_history_for_markdown(history, max_rows=24).copy()
            hist_out["score"] = hist_out["score"].map(lambda x: "" if pd.isna(x) else f"{float(x):.2f}")
            hist_out["tests_passed"] = hist_out["tests_passed"].map(lambda x: "" if pd.isna(x) else fmt_int(x))
            hist_out["tests_total"] = hist_out["tests_total"].map(lambda x: "" if pd.isna(x) else fmt_int(x))
            lines.append(md_table(hist_out))
        lines.append("")

    lines.append("## Per-Namespace: Students with Only Public Activity and No Private Submission")
    lines.append("")
    lines.append(
        "Interpretation: `students_only_public_in_namespace / total_students` answers your question directly at namespace level."
    )
    lines.append("")
    ns_out = ns_summary[
        [
            "namespace",
            "namespace_type",
            "students_only_public_in_namespace",
            "total_students",
            "public_only_student_pct",
            "students_with_at_least_one_public_only_question",
            "public_only_question_rows",
            "example_student_ids",
        ]
    ].copy()
    ns_out["students_only_public_in_namespace"] = ns_out["students_only_public_in_namespace"].map(fmt_int)
    ns_out["total_students"] = ns_out["total_students"].map(fmt_int)
    ns_out["public_only_student_pct"] = ns_summary["public_only_student_pct"].map(lambda x: f"{x:.1f}%")
    ns_out["students_with_at_least_one_public_only_question"] = ns_out[
        "students_with_at_least_one_public_only_question"
    ].map(fmt_int)
    ns_out["public_only_question_rows"] = ns_out["public_only_question_rows"].map(fmt_int)
    lines.append(md_table(ns_out))
    lines.append("")

    lines.append("## Distribution: Number of Public-Only Question Combos per Student")
    lines.append("")
    dist_out = dist.copy()
    dist_out.rename(
        columns={
            "public_only_question_count": "public_only_questions_per_student",
            "students": "student_count",
        },
        inplace=True,
    )
    dist_out["student_count"] = dist_out["student_count"].map(fmt_int)
    dist_out["pct_of_affected_students"] = dist["pct_of_affected_students"].map(lambda x: f"{x:.1f}%")
    lines.append(md_table(dist_out))
    lines.append("")

    lines.append("## Public Test Performance on Public-Only Rows")
    lines.append("")
    score_out = score_dist.copy()
    score_out["rows"] = score_out["rows"].map(fmt_int)
    score_out["pct_of_public_only_rows"] = score_dist["pct_of_public_only_rows"].map(lambda x: f"{x:.1f}%")
    lines.append(md_table(score_out))
    lines.append("")

    lines.append("## Namespace Class Comparison (Useful Operational Signal)")
    lines.append("")
    class_out = class_summary.copy()
    class_out["public_only_rows"] = class_out["public_only_rows"].map(fmt_int)
    class_out["unique_students"] = class_out["unique_students"].map(fmt_int)
    class_out["namespaces"] = class_out["namespaces"].map(fmt_int)
    class_out["rows_with_100_public"] = class_out["rows_with_100_public"].map(fmt_int)
    class_out["pct_rows_with_100_public"] = class_summary["pct_rows_with_100_public"].map(lambda x: f"{x:.1f}%")
    lines.append(md_table(class_out))
    lines.append("")

    lines.append("## Top Question Combos by Public-Only Volume")
    lines.append("")
    top_out = top_q[
        [
            "namespace",
            "problem_id",
            "question_title",
            "public_only_rows",
            "unique_students",
            "pct_rows_with_100_public",
            "example_student_ids",
        ]
    ].copy()
    top_out["public_only_rows"] = top_out["public_only_rows"].map(fmt_int)
    top_out["unique_students"] = top_out["unique_students"].map(fmt_int)
    top_out["pct_rows_with_100_public"] = top_q["pct_rows_with_100_public"].map(lambda x: f"{x:.1f}%")
    lines.append(md_table(top_out))
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append("- This report is event-log based; if private submissions were never captured for a namespace, behavior and instrumentation are confounded.")
    lines.append("- `100%` here refers to **best public test-run** coverage on visible test cases, not private-evaluator success.")
    lines.append("- Student IDs are anonymized hashes, shown only as examples for traceability.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    conn = duckdb.connect()
    conn.execute("PRAGMA enable_progress_bar=false")
    conn.execute("PRAGMA threads=4")

    build_views(conn)
    detail_df = export_detail_csv(conn)
    md = build_markdown(conn, detail_df)
    OUT_MD.write_text(md)
    print(f"Wrote {OUT_CSV.relative_to(ROOT)} ({len(detail_df):,} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
