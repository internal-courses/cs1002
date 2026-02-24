#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["orjson>=3.10"]
# ///
"""Build compact archetype timeline examples from raw submission events.

Input:
  - analysis/errors.json
  - submissions/pyoppe_student_submissions_*.json (JSON Lines)

Output:
  - analysis/archetype_timelines.json
"""

from __future__ import annotations

import base64
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
import io
import math
import re
from pathlib import Path
from typing import Any
import zipfile

import orjson


ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
ERRORS_JSON = ANALYSIS / "errors.json"
OUT_PATH = ANALYSIS / "archetype_timelines.json"
SUBMISSIONS_DIR = ROOT / "submissions"


ARCH = {
    "Sample Overfit": {
        "label": "The Mimic",
        "color": "#7c3aed",
        "process": [
            ("See samples", "Learns the visible cases instead of the full rule"),
            ("Infer shortcut", "Builds sample-shaped logic or a brittle shortcut"),
            ("Validate locally", "Public/sample tests pass and reinforce confidence"),
            ("Hidden test shift", "A new case violates the shortcut's assumptions"),
            ("Wrong answer", "The code solved a narrower problem than the prompt"),
        ],
    },
    "Early Exit": {
        "label": "The Quitter",
        "color": "#dc2626",
        "process": [
            ("Start loop", "The code structure looks plausible"),
            ("Check first item", "A local condition is evaluated"),
            ("Return early", "Function exits before processing all required items"),
            ("Partial correctness", "Some cases still pass by accident"),
            ("Hidden test failure", "Private cases expose the incomplete scan"),
        ],
    },
    "Missing Return": {
        "label": "The Ghost",
        "color": "#ea580c",
        "process": [
            ("Compute answer", "Core logic may be mostly correct"),
            ("Print/debug", "Student sees output locally"),
            ("No return", "Function returns None or wrong object"),
            ("Contract mismatch", "Evaluator checks returned value"),
            ("Low score", "A contract bug masks the logic"),
        ],
    },
    "Wrong I/O Mode": {
        "label": "The Confused",
        "color": "#d97706",
        "process": [
            ("Read prompt loosely", "Understands the task but misses evaluation mode"),
            ("Write program-style code", "Uses input()/print() in a function question"),
            ("Local terminal success", "Manual runs seem fine"),
            ("Evaluator mismatch", "Autograder calls function directly"),
            ("Failure", "Wrong interface, even with the right idea"),
        ],
    },
    "Syntax / Unfinished": {
        "label": "The Unfinished",
        "color": "#64748b",
        "process": [
            ("Begin implementation", "Structure is started"),
            ("Partial edits", "Some sections are changed, others remain placeholders"),
            ("Time pressure", "Broken or incomplete code is submitted"),
            ("Parser/runtime stops", "Evaluator cannot meaningfully test logic"),
            ("Low score", "Completion becomes the bottleneck"),
        ],
    },
    "Runtime Crash": {
        "label": "The Crasher",
        "color": "#2563eb",
        "process": [
            ("Parseable code", "Submission can start executing"),
            ("Assumption mismatch", "Hidden input shape/values break an assumption"),
            ("Exception", "Name/type/index/key errors stop execution"),
            ("Partial progress", "Some logic may be right but hidden by the crash"),
            ("Debug gap", "Needs runtime diagnosis, not just syntax fixes"),
        ],
    },
    "Logic Error": {
        "label": "The Wanderer",
        "color": "#059669",
        "process": [
            ("Plausible rule", "Student implements a coherent algorithm"),
            ("Easy cases pass", "Visible examples reinforce confidence"),
            ("Invariant missed", "Order/uniqueness/boundary/format semantics are wrong"),
            ("Systematic wrong answers", "Fails a repeatable family of inputs"),
            ("Spec repair needed", "The issue is the rule, not syntax"),
        ],
    },
}


def classify(pattern_name: str) -> str:
    n = (pattern_name or "").lower()
    if "hard-cod" in n or ("sample" in n and any(x in n for x in ("output", "string", "result", "case"))):
        return "Sample Overfit"
    if "returns inside" in n or ("inside" in n and "loop" in n) or "first iteration" in n or "first match" in n:
        return "Early Exit"
    if "no return" in n or ("implicit" in n and "none" in n) or ("print" in n and "instead of return" in n):
        return "Missing Return"
    if "input()" in n or ("reads" in n and "input" in n):
        return "Wrong I/O Mode"
    if n.startswith("syntax") or "non-parseable" in n or "placeholder" in n or "empty final submission" in n or "skeleton" in n:
        return "Syntax / Unfinished"
    if n.startswith("runtime") or any(e in n for e in (
        "typeerror", "nameerror", "indexerror", "valueerror", "attributeerror", "recursionerror", "keyerror",
        "zerodivisionerror", "eoferror"
    )):
        return "Runtime Crash"
    return "Logic Error"


def load_errors_payload() -> dict[str, Any]:
    return orjson.loads(ERRORS_JSON.read_bytes())


def iso_to_dt_utc(s: str | None) -> datetime | None:
    if not s:
        return None
    txt = s.strip()
    try:
        dt = datetime.fromisoformat(txt.replace("Z", "+00:00"))
    except Exception:
        try:
            # "2025-02-26 14:13:29.065888"
            dt = datetime.fromisoformat(txt.replace(" ", "T"))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_time_readable(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    hour = dt.hour % 12 or 12
    suffix = "am" if dt.hour < 12 else "pm"
    return f"{hour}:{dt:%M} {suffix} UTC"


def variant_from_record(rec: dict[str, Any]) -> str:
    return f"{rec.get('Namespace','')}/{rec.get('ProblemID','')}"


def extract_action_from_filename(file_name: str | None, student_id: str | None) -> str | None:
    if not file_name:
        return None
    if student_id:
        m = re.search(rf"/{re.escape(student_id)}/([^/]+)/", file_name)
        if m:
            return m.group(1)
    parts = str(file_name).split("/")
    if len(parts) >= 4:
        return parts[-2]
    return None


def parse_compilation_result(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        obj = raw
    else:
        txt = str(raw or "")
        try:
            obj = orjson.loads(txt)
        except Exception:
            return {"parse_error": True, "raw": txt[:1000]}
    out: dict[str, Any] = {
        "status": obj.get("status"),
        "reason": obj.get("reason"),
        "summary": obj.get("summary"),
        "score": obj.get("score"),
        "num_test_evaluated": obj.get("num_test_evaluated"),
        "num_test_passed": obj.get("num_test_passed"),
    }
    tcr = obj.get("test_case_results")
    if isinstance(tcr, list):
        out["num_test_case_results"] = len(tcr)
        reasons = defaultdict(int)
        passed = 0
        sample_fails = []
        for item in tcr:
            if not isinstance(item, dict):
                continue
            if item.get("passed") is True:
                passed += 1
            else:
                reason = str(item.get("reason") or "Unknown")
                reasons[reason] += 1
                if len(sample_fails) < 2:
                    sample_fails.append({
                        "reason": reason,
                        "output_excerpt": str(item.get("output") or "")[:220],
                        "expected_excerpt": str(item.get("expected_output") or "")[:220],
                    })
        out["test_result_summary"] = {
            "passed_cases": passed,
            "failed_cases": max(0, len(tcr) - passed),
            "reasons": dict(sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))),
            "sample_fails": sample_fails,
        }
    return out


def decode_code(base64_code: str | None) -> str | None:
    if not base64_code:
        return None
    try:
        blob = base64.b64decode(base64_code)
    except Exception:
        return None
    # Most entries are zipped editor bundles.
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = zf.namelist()
            preferred = next((n for n in names if n.endswith(".py")), names[0] if names else None)
            if preferred is None:
                return None
            data = zf.read(preferred)
            return data.decode("utf-8", errors="replace")
    except Exception:
        try:
            return blob.decode("utf-8", errors="replace")
        except Exception:
            return None


@dataclass(frozen=True)
class CandidateKey:
    student_id: str
    variant: str


def collect_candidates(errors_payload: dict[str, Any], per_arch: int = 30) -> dict[str, list[dict[str, Any]]]:
    candidates: dict[str, list[dict[str, Any]]] = {k: [] for k in ARCH}
    seen: dict[str, set[tuple[str, str]]] = {k: set() for k in ARCH}
    for cluster in errors_payload.get("clusters", []):
        for pattern in cluster.get("reclustered_patterns", {}).get("patterns", []):
            arch = classify(pattern.get("name", ""))
            exs = pattern.get("representative_examples", []) or []
            for ex in exs:
                student_id = ex.get("student_id")
                variant = ex.get("variant")
                if not student_id or not variant:
                    continue
                key = (student_id, variant)
                if key in seen[arch]:
                    continue
                seen[arch].add(key)
                candidates[arch].append({
                    "archetype_key": arch,
                    "student_id": student_id,
                    "variant": variant,
                    "cluster_id": cluster.get("cluster_id"),
                    "cluster_title": cluster.get("title"),
                    "pattern_name": pattern.get("name"),
                    "pattern_count": pattern.get("cluster_frequency", {}).get("count") or 0,
                    "pattern_pct": pattern.get("cluster_frequency", {}).get("pct"),
                    "example_summary": ex.get("summary"),
                    "example_score": ex.get("score"),
                    "example_score_label": ex.get("score_label"),
                    "example_vector": ex.get("vector"),
                })
    for arch, rows in candidates.items():
        rows.sort(key=lambda r: (-(r["pattern_count"] or 0), r["cluster_id"] or "", r["student_id"]))
        candidates[arch] = rows[:per_arch]
    return candidates


def score_timeline(events: list[dict[str, Any]]) -> float:
    if not events:
        return -1e9
    n = len(events)
    score = 0.0
    score += min(n, 12) * 4
    eval_types = {e.get("evaluation_type") for e in events}
    if "public" in eval_types:
        score += 12
    if "private" in eval_types:
        score += 18
    if {"public", "private"} <= eval_types:
        score += 16
    actions = {e.get("action") for e in events}
    if "submission" in actions:
        score += 12
    if "test_run" in actions:
        score += 6
    scores = [e.get("score") for e in events if isinstance(e.get("score"), (int, float))]
    if len(scores) >= 2:
        deltas = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
        if any(d > 0 for d in deltas):
            score += 14
        if any(d < 0 for d in deltas):
            score += 4
    last = events[-1]
    if last.get("evaluation_type") == "private":
        score += 10
        last_score = last.get("score")
        if isinstance(last_score, (int, float)) and 0 <= last_score < 100:
            score += 10
    # prefer a modest timeline length for popup readability
    if n > 14:
        score -= (n - 14) * 1.5
    return score


def assign_process_steps(archetype_key: str, events: list[dict[str, Any]]) -> list[dict[str, str]]:
    process = ARCH[archetype_key]["process"]
    m = len(process)
    n = len(events)
    assigned: list[dict[str, str]] = []
    if n == 0:
        return assigned
    for i, event in enumerate(events):
        if n == 1:
            idx = m - 1
        else:
            idx = min(m - 1, math.floor(i * m / n))
        step_label, step_desc = process[idx]
        assigned.append({"step_label": step_label, "step_description": step_desc})
    return assigned


def annotate_event(i: int, events: list[dict[str, Any]], archetype_key: str) -> str:
    e = events[i]
    comp = e.get("comp", {})
    parts: list[str] = []
    if i == 0:
        parts.append("First recorded event for this student on this question in the raw submission logs.")
    else:
        prev = events[i - 1]
        prev_score = prev.get("score")
        cur_score = e.get("score")
        if isinstance(prev_score, (int, float)) and isinstance(cur_score, (int, float)):
            delta = cur_score - prev_score
            if delta > 0:
                parts.append(f"Score improves by {delta:g} points from the previous event.")
            elif delta < 0:
                parts.append(f"Score drops by {abs(delta):g} points from the previous event, suggesting a risky change or a broader test set.")
            else:
                parts.append("Score does not change from the previous event.")

    if e.get("evaluation_type") == "public":
        parts.append("This is a public-test run, which can reinforce sample-specific shortcuts.")
    elif e.get("evaluation_type") == "private":
        parts.append("This is a private evaluation, where hidden cases expose generalization and contract bugs.")

    summary = str(e.get("summary") or "")
    if "wrong answer" in summary.lower():
        parts.append("The code runs, but the logic/contract does not match the evaluator on at least one test.")
    elif "runtime error" in summary.lower():
        parts.append("Execution crashes before producing a valid answer on at least one test.")
    elif "compilation" in summary.lower() or "syntax" in summary.lower():
        parts.append("The submission is not parseable/compilable in its final form.")

    if i == len(events) - 1:
        parts.append("This is the last recorded event for the student on this question (the end of the visible timeline).")

    return " ".join(parts)


def summarize_test_results(comp: dict[str, Any]) -> dict[str, Any]:
    out = {
        "summary": comp.get("summary"),
        "score": comp.get("score"),
        "num_test_evaluated": comp.get("num_test_evaluated"),
        "num_test_passed": comp.get("num_test_passed"),
    }
    trs = comp.get("test_result_summary")
    if isinstance(trs, dict):
        out["test_result_summary"] = trs
    return out


def trim_code(code: str | None, max_chars: int = 6000) -> str | None:
    if code is None:
        return None
    if len(code) <= max_chars:
        return code
    return code[:max_chars] + "\n\n# ... [trimmed]"


def choose_timelines(candidates: dict[str, list[dict[str, Any]]], events_by_key: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    chosen: dict[str, dict[str, Any]] = {}
    for arch, rows in candidates.items():
        best = None
        best_score = -1e18
        for row in rows:
            key = (row["student_id"], row["variant"])
            events = sorted(events_by_key.get(key, []), key=lambda e: (e.get("dt") or datetime.min.replace(tzinfo=UTC), e.get("ordinal", 0)))
            if not events:
                continue
            s = score_timeline(events)
            # prefer examples where the final event matches the representative pattern's broad failure category
            if row.get("example_summary") and str(events[-1].get("summary") or "").lower() == str(row["example_summary"]).lower():
                s += 5
            if s > best_score:
                best_score = s
                best = (row, events)
        if best is None:
            continue
        row, events = best
        step_assignments = assign_process_steps(arch, events)
        timeline = []
        for i, e in enumerate(events):
            step_info = step_assignments[i] if i < len(step_assignments) else {"step_label": "Event", "step_description": ""}
            comp = e.get("comp", {})
            timeline.append({
                "step_index": i + 1,
                "step_label": step_info["step_label"],
                "step_description": step_info["step_description"],
                "event_annotation": annotate_event(i, events, arch),
                "timestamp_utc": e.get("dt").isoformat() if e.get("dt") else None,
                "timestamp_display_utc": format_time_readable(e.get("dt")),
                "timestamp_display_full_utc": e.get("dt").strftime("%b %-d, %Y %-I:%M:%S %p UTC") if e.get("dt") else None,
                "evaluation_type": e.get("evaluation_type"),
                "action": e.get("action"),
                "file_name": e.get("file_name"),
                "summary": e.get("summary"),
                "score": e.get("score"),
                "num_test_evaluated": e.get("num_test_evaluated"),
                "num_test_passed": e.get("num_test_passed"),
                "status": comp.get("status"),
                "reason": comp.get("reason"),
                "test_results": summarize_test_results(comp),
                "code": trim_code(e.get("code")),
                "code_lang": "python",
            })
        chosen[arch] = {
            "archetype_key": arch,
            "archetype_label": ARCH[arch]["label"],
            "color": ARCH[arch]["color"],
            "cluster_id": row["cluster_id"],
            "cluster_title": row["cluster_title"],
            "variant": row["variant"],
            "student_id": row["student_id"],
            "pattern_name": row["pattern_name"],
            "pattern_count": row["pattern_count"],
            "pattern_pct": row["pattern_pct"],
            "example_summary": row["example_summary"],
            "example_score": row["example_score"],
            "example_score_label": row.get("example_score_label"),
            "example_vector": row.get("example_vector"),
            "timeline_score": best_score,
            "timeline_event_count": len(timeline),
            "timeline": timeline,
        }
    return chosen


def main() -> None:
    payload = load_errors_payload()
    candidates = collect_candidates(payload, per_arch=36)
    target_keys: set[tuple[str, str]] = set()
    key_to_arches: dict[tuple[str, str], list[str]] = defaultdict(list)
    for arch, rows in candidates.items():
        for row in rows:
            key = (row["student_id"], row["variant"])
            target_keys.add(key)
            key_to_arches[key].append(arch)

    print(f"Loaded errors.json. Candidate keys: {len(target_keys)} across {len(candidates)} archetypes.")

    events_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    files = sorted(SUBMISSIONS_DIR.glob("pyoppe_student_submissions_*.json"))
    ordinal = 0
    matched_records = 0
    for fi, path in enumerate(files, start=1):
        print(f"[{fi}/{len(files)}] scanning {path.name} ...")
        with path.open("rb") as f:
            for raw_line in f:
                if not raw_line.strip():
                    continue
                try:
                    rec = orjson.loads(raw_line)
                except Exception:
                    continue
                student_id = rec.get("StudentID")
                variant = variant_from_record(rec)
                key = (student_id, variant)
                if key not in target_keys:
                    continue
                matched_records += 1
                ordinal += 1
                comp = parse_compilation_result(rec.get("CompilationResult"))
                dt = iso_to_dt_utc(rec.get("LastUpdated"))
                code = decode_code(rec.get("Base64Code"))
                ev = {
                    "ordinal": ordinal,
                    "student_id": student_id,
                    "variant": variant,
                    "namespace": rec.get("Namespace"),
                    "problem_id": rec.get("ProblemID"),
                    "evaluation_type": rec.get("EvaluationType"),
                    "file_name": rec.get("FileName"),
                    "action": extract_action_from_filename(rec.get("FileName"), student_id),
                    "dt": dt,
                    "comp": comp,
                    "summary": comp.get("summary"),
                    "score": comp.get("score"),
                    "num_test_evaluated": comp.get("num_test_evaluated"),
                    "num_test_passed": comp.get("num_test_passed"),
                    "code": code,
                }
                events_by_key[key].append(ev)
        print(f"    matched so far: {matched_records}")

    chosen = choose_timelines(candidates, events_by_key)
    missing = [k for k in ARCH if k not in chosen]
    if missing:
        print(f"Warning: no timeline found for archetypes: {missing}")

    out = {
        "schema_version": "archetype-timelines.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": {
            "errors_json": str(ERRORS_JSON.relative_to(ROOT)),
            "submission_files": [str(p.relative_to(ROOT)) for p in files],
            "candidate_key_count": len(target_keys),
            "matched_records": matched_records,
        },
        "archetypes": {k: chosen.get(k) for k in ARCH},
    }
    OUT_PATH.write_bytes(orjson.dumps(out, option=orjson.OPT_INDENT_2))
    OUT_PATH.write_text(OUT_PATH.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    for k in ARCH:
        item = chosen.get(k)
        if item:
            print(
                f"- {k}: {item['variant']} / {item['student_id'][:8]}... "
                f"{item['timeline_event_count']} events, pattern={item['pattern_name'][:70]}"
            )
        else:
            print(f"- {k}: MISSING")


if __name__ == "__main__":
    main()
