#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "typer>=0.12.3",
# ]
# ///
"""Generate an asciinema cast for one student's work on one question.

The cast includes every timeline event available for the
``(namespace, problem_id, student_id)`` tuple (for example: save/test/submission
events), rendered with consistent, prominent event indicators.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
PROBLEMS_DIR = ROOT / "problems"

TIMELINE_PATH = ANALYSIS_DIR / "submission_timeline.parquet"
SNAPSHOTS_PATH = ANALYSIS_DIR / "code_snapshots.parquet"
DEFAULT_OUT_DIR = ANALYSIS_DIR / "asciinema"


CLEAR_SCREEN = "\x1b[2J\x1b[H"
RESET = "\x1b[0m"
EOL = "\r\n"

EVENT_STYLE: dict[str, tuple[str, str]] = {
    "saved_code": ("SAVE", "\x1b[1;30;46m"),
    "test_run": ("TEST", "\x1b[1;30;43m"),
    "submission": ("SUBMIT", "\x1b[1;37;45m"),
}


@dataclass(frozen=True)
class SkeletonInfo:
    prefixed_code: str
    uneditable_code: str
    suffixed_invisible_code: str


@dataclass(frozen=True)
class EventRow:
    timestamp_utc: datetime
    timestamp_ist: datetime | None
    event_type: str
    evaluation_type: str | None
    summary: str | None
    reason: str | None
    score: float | None
    num_test_evaluated: int | None
    num_test_passed: int | None
    test_case_count: int | None
    code_sha256: str | None
    code_length: int | None
    is_parseable: bool | None
    code_snapshot: str | None


@dataclass(frozen=True)
class QuestionInfo:
    title: str
    skeleton: SkeletonInfo


def normalize_newlines(text: str | None) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_html(text: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = plain.replace("&nbsp;", " ")
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def extract_title(question_html: str) -> str:
    match = re.search(r"<h1>\s*<b>([^<]+)</b>", question_html or "")
    if match:
        return match.group(1).strip()
    plain = strip_html(question_html or "")
    return plain[:120].strip() or "(untitled question)"


def load_question_info(namespace: str, problem_id: int) -> QuestionInfo:
    question_path = PROBLEMS_DIR / namespace / f"{problem_id}.json"
    if not question_path.exists():
        return QuestionInfo(
            title="(question metadata not found)",
            skeleton=SkeletonInfo(prefixed_code="", uneditable_code="", suffixed_invisible_code=""),
        )

    obj = json.loads(question_path.read_text(encoding="utf-8"))
    allowed = obj.get("allowed_languages") or []
    lang_obj = next((item for item in allowed if (item or {}).get("language") == "py3"), None)
    if lang_obj is None and allowed:
        lang_obj = allowed[0]
    lang_obj = lang_obj or {}
    return QuestionInfo(
        title=extract_title(str(obj.get("question") or "")),
        skeleton=SkeletonInfo(
            prefixed_code=str(lang_obj.get("prefixed_code") or ""),
            uneditable_code=str(lang_obj.get("uneditable_code") or ""),
            suffixed_invisible_code=str(lang_obj.get("suffixed_invisible_code") or ""),
        ),
    )


def extract_student_editable_code(full_code: str, sk: SkeletonInfo) -> tuple[str, str]:
    """Best-effort scaffold stripping from evaluator wrappers."""
    code = normalize_newlines(full_code)
    prefix = normalize_newlines(sk.prefixed_code)
    suffix = normalize_newlines(sk.suffixed_invisible_code)
    uneditable = normalize_newlines(sk.uneditable_code)

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

    cleaned = code.strip("\n")
    return cleaned, status


def load_events(namespace: str, problem_id: int, student_id: str) -> list[EventRow]:
    if not TIMELINE_PATH.exists():
        raise FileNotFoundError(f"Missing required file: {TIMELINE_PATH}")
    if not SNAPSHOTS_PATH.exists():
        raise FileNotFoundError(f"Missing required file: {SNAPSHOTS_PATH}")

    conn = duckdb.connect()
    try:
        sql = """
        SELECT
          t.timestamp_utc,
          t.timestamp_ist,
          t.event_type,
          t.evaluation_type,
          t.summary,
          t.reason,
          t.score,
          t.num_test_evaluated,
          t.num_test_passed,
          t.test_case_count,
          t.code_sha256,
          t.code_length,
          t.is_parseable,
          c.code_snapshot
        FROM read_parquet(?) t
        LEFT JOIN read_parquet(?) c USING (code_sha256)
        WHERE t.namespace = ?
          AND t.problem_id = ?
          AND t.student_id = ?
        ORDER BY
          t.timestamp_utc,
          CASE t.event_type
            WHEN 'saved_code' THEN 1
            WHEN 'test_run' THEN 2
            WHEN 'submission' THEN 3
            ELSE 9
          END,
          t.evaluation_type
        """
        rows = conn.execute(
            sql,
            [str(TIMELINE_PATH), str(SNAPSHOTS_PATH), namespace, problem_id, student_id],
        ).fetchall()
    finally:
        conn.close()

    events: list[EventRow] = []
    for row in rows:
        events.append(
            EventRow(
                timestamp_utc=row[0],
                timestamp_ist=row[1],
                event_type=str(row[2] or ""),
                evaluation_type=(str(row[3]) if row[3] is not None else None),
                summary=(str(row[4]) if row[4] is not None else None),
                reason=(str(row[5]) if row[5] is not None else None),
                score=(float(row[6]) if row[6] is not None else None),
                num_test_evaluated=(int(row[7]) if row[7] is not None else None),
                num_test_passed=(int(row[8]) if row[8] is not None else None),
                test_case_count=(int(row[9]) if row[9] is not None else None),
                code_sha256=(str(row[10]) if row[10] is not None else None),
                code_length=(int(row[11]) if row[11] is not None else None),
                is_parseable=(bool(row[12]) if row[12] is not None else None),
                code_snapshot=(str(row[13]) if row[13] is not None else None),
            )
        )
    return events


def fmt_ts(ts: datetime | None) -> str:
    if ts is None:
        return "-"
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def fmt_secs(total_seconds: float) -> str:
    seconds = max(0, int(round(total_seconds)))
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def badge_for_event(event_type: str) -> str:
    label, color = EVENT_STYLE.get(event_type, ("EVENT", "\x1b[1;37;40m"))
    return f"{color} {label:^8} {RESET}"


def render_code_block(code: str, max_lines: int) -> list[str]:
    if not code.strip():
        return ["(empty code snapshot)"]
    lines = code.split("\n")
    visible = lines[:max_lines]
    out: list[str] = [f"{idx + 1:>4} | {line}" for idx, line in enumerate(visible)]
    if len(lines) > max_lines:
        out.append(f"... ({len(lines) - max_lines} more lines truncated)")
    return out


def build_frame_text(
    event: EventRow,
    index: int,
    total: int,
    namespace: str,
    problem_id: int,
    student_id: str,
    question_title: str,
    elapsed_from_start: float,
    code_text: str,
    strip_status: str,
    code_changed: bool,
    next_gap_seconds: float | None,
    max_code_lines: int,
    show_code: bool,
) -> str:
    meta_parts = [
        f"summary={event.summary or '-'}",
        f"score={event.score if event.score is not None else '-'}",
    ]
    if event.num_test_passed is not None or event.test_case_count is not None:
        meta_parts.append(
            f"tests={event.num_test_passed if event.num_test_passed is not None else '-'}"
            f"/{event.test_case_count if event.test_case_count is not None else '-'}"
        )
    if event.reason:
        meta_parts.append(f"reason={event.reason}")

    lines: list[str] = [
        CLEAR_SCREEN + "PyOPPE Asciinema Replay",
        "=" * 80,
        f"Namespace: {namespace}    Problem: {problem_id}    Student: {student_id}",
        f"Question : {question_title}",
        f"Event    : {index}/{total}    +{fmt_secs(elapsed_from_start)} from first event",
        (
            f"When     : UTC {fmt_ts(event.timestamp_utc)}"
            f" | IST {fmt_ts(event.timestamp_ist)}"
        ),
        "=" * 80,
        f"{badge_for_event(event.event_type)}  type={event.event_type}"
        + (f" ({event.evaluation_type})" if event.evaluation_type else ""),
        " | ".join(meta_parts),
        (
            f"Code     : sha={event.code_sha256[:12] if event.code_sha256 else '-'}"
            f" len={event.code_length if event.code_length is not None else '-'}"
            f" parseable={event.is_parseable if event.is_parseable is not None else '-'}"
            f" changed={code_changed}"
            f" strip={strip_status}"
        ),
        "-" * 80,
    ]

    if show_code:
        lines.extend(render_code_block(code_text, max_lines=max_code_lines))
    else:
        lines.append("(code unchanged from previous event)")

    lines.append("-" * 80)
    if next_gap_seconds is not None:
        lines.append(f"Next event in {next_gap_seconds:.2f}s (after speed/idle settings)")
    else:
        lines.append("End of event timeline")
    lines.append("")
    return EOL.join(lines)


def event_times(
    events: list[EventRow],
    speed: float,
    max_idle_seconds: float | None,
) -> list[float]:
    if not events:
        return []
    out: list[float] = [0.0]
    current = 0.0
    prev_ts = events[0].timestamp_utc
    for event in events[1:]:
        raw_gap = max(0.0, (event.timestamp_utc - prev_ts).total_seconds())
        scaled = raw_gap / speed
        if max_idle_seconds is not None:
            scaled = min(scaled, max_idle_seconds)
        current += scaled
        out.append(current)
        prev_ts = event.timestamp_utc
    return out


def write_cast(
    out_path: Path,
    header: dict[str, Any],
    frames: list[tuple[float, str]],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for ts, payload in frames:
            f.write(json.dumps([round(ts, 6), "o", payload], ensure_ascii=False) + "\n")


def validate_cast(path: Path) -> tuple[int, float]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("Cast file is empty")
    header = json.loads(lines[0])
    if int(header.get("version", -1)) != 2:
        raise ValueError("Cast header must have version=2")

    prev = -1.0
    count = 0
    for idx, raw in enumerate(lines[1:], start=2):
        row = json.loads(raw)
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(f"Invalid event row at line {idx}")
        ts, kind, payload = row
        if kind != "o":
            raise ValueError(f"Unsupported event kind at line {idx}: {kind}")
        if not isinstance(payload, str):
            raise ValueError(f"Payload must be string at line {idx}")
        if float(ts) < prev:
            raise ValueError(f"Non-monotonic timestamp at line {idx}")
        prev = float(ts)
        count += 1
    return count, prev if prev >= 0 else 0.0


@app.command()
def main(
    namespace: str = typer.Option(..., help="Namespace, e.g. ns_25t2_py21_1"),
    problem_id: int = typer.Option(..., help="Problem id within namespace"),
    student_id: str = typer.Option(..., help="Student ID hash"),
    out: Path | None = typer.Option(
        None,
        help="Output .cast path. Default: analysis/asciinema/<namespace>__p<id>__<student>.cast",
    ),
    width: int = typer.Option(140, min=40, help="Asciinema terminal width"),
    height: int = typer.Option(40, min=10, help="Asciinema terminal height"),
    speed: float = typer.Option(
        1.0,
        min=0.01,
        help="Time compression factor; 2.0 means twice as fast (half the delays).",
    ),
    max_idle_seconds: float | None = typer.Option(
        None,
        min=0.0,
        help="Optional cap for long idle gaps after speed compression.",
    ),
    max_code_lines: int = typer.Option(60, min=5, help="Max code lines shown per event"),
    always_show_code: bool = typer.Option(
        False,
        help="Show code block even when hash did not change since previous event.",
    ),
    keep_scaffold: bool = typer.Option(
        False,
        help="Show full snapshot without stripping evaluator prefix/suffix code.",
    ),
    validate: bool = typer.Option(True, help="Validate generated cast format"),
) -> None:
    """Generate an asciinema cast from timeline data for one student-question tuple."""
    events = load_events(namespace=namespace, problem_id=problem_id, student_id=student_id)
    if not events:
        raise typer.BadParameter("No events found for the provided namespace/problem_id/student_id.")

    question = load_question_info(namespace=namespace, problem_id=problem_id)
    times = event_times(events=events, speed=speed, max_idle_seconds=max_idle_seconds)
    if out is None:
        safe_student = re.sub(r"[^A-Za-z0-9_.-]+", "_", student_id)
        out = DEFAULT_OUT_DIR / f"{namespace}__p{problem_id}__{safe_student}.cast"

    first_ts = events[0].timestamp_utc
    header = {
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(first_ts.timestamp()),
        "title": f"{namespace}/{problem_id} - {student_id[:10]}...",
        "env": {
            "SHELL": "/bin/bash",
            "TERM": "xterm-256color",
        },
    }

    frames: list[tuple[float, str]] = []
    previous_hash: str | None = None
    total = len(events)

    for idx, event in enumerate(events, start=1):
        raw_code = normalize_newlines(event.code_snapshot)
        if keep_scaffold:
            student_code = raw_code.strip("\n")
            strip_status = "kept_full_snapshot"
        else:
            student_code, strip_status = extract_student_editable_code(raw_code, question.skeleton)

        code_changed = event.code_sha256 != previous_hash
        show_code = always_show_code or code_changed or idx == 1

        next_gap = None
        if idx < total:
            next_gap = max(0.0, times[idx] - times[idx - 1])

        payload = build_frame_text(
            event=event,
            index=idx,
            total=total,
            namespace=namespace,
            problem_id=problem_id,
            student_id=student_id,
            question_title=question.title,
            elapsed_from_start=max(0.0, (event.timestamp_utc - first_ts).total_seconds()),
            code_text=student_code,
            strip_status=strip_status,
            code_changed=code_changed,
            next_gap_seconds=next_gap,
            max_code_lines=max_code_lines,
            show_code=show_code,
        )
        frames.append((times[idx - 1], payload))
        previous_hash = event.code_sha256

    write_cast(out_path=out, header=header, frames=frames)
    typer.echo(f"Wrote cast: {out} (events={len(frames)})")

    if validate:
        event_count, duration = validate_cast(out)
        typer.echo(f"Validated cast: rows={event_count}, duration={duration:.2f}s")


if __name__ == "__main__":
    app()
