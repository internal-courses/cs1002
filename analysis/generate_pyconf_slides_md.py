#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.4.0"]
# ///
"""Generate an expanded Marp slideshow for the replay talk."""

from __future__ import annotations

import re
from pathlib import Path

import generate_replays_extracts_md as extracts

OUT_PATH = Path(__file__).resolve().parent / "pyconf-slides.md"

QUESTION_COMMENTARY = {
    ("ns_25t2_py11_1", 6): "Use this opener to show the difference between parsing the shape of the input and parroting the visible examples.",
    ("ns_25t2_py22_1", 15): "This tiny prompt is perfect for showing how students negotiate with tests instead of reading the full contract.",
    ("ns_25t3_py13_1", 7): "This is the cleanest exhibit in the repo of solving the examples instead of solving the transformation.",
    ("ns_25t2_py21_2", 18): "Close here: the invariant is simple, but the path to discovering it is where the teaching insight lives.",
}

BEAT_EVENT_OVERRIDES = {
    (
        "ns_25t2_py21_2",
        18,
        "Funny Moment 6 — The Pangram Checker That Forgot C",
        "a2316b024ae946b59ebe2f04090321d9",
    ): [
        extracts.EventRef(2, "The broken internal alphabet is visible in the lowercase scan."),
        extracts.EventRef(3, "Adding uppercase handling still leaves the missing-letter representation bug in place."),
        extracts.EventRef(30, "The student finally abandons the broken alphabet string and reaches a real full pass."),
        extracts.EventRef(35, "Submission locks in the repaired representation."),
    ],
}


def sanitize_question_html(question_html: str) -> str:
    """Trim the LMS wrapper and keep the actual prompt content visible on the slide."""
    html = question_html.strip()
    html = re.sub(r"(?is)^<div[^>]*>\s*", "", html)
    html = re.sub(r"(?is)</div>\s*$", "", html)
    html = re.sub(r"(?is)<main[^>]*>", "", html)
    html = re.sub(r"(?is)</main>", "", html)
    html = re.sub(r"(?is)<h1>.*?</h1>", "", html, count=1)
    html = re.sub(r"(?is)<details.*$", "", html)
    html = re.sub(r"(?is)<p><b>NOTE: You can use.*$", "", html)
    html = re.sub(r"(?is)<span>.*$", "", html)
    return html.strip()


def effective_event_refs(
    qcfg: extracts.QuestionConfig,
    beat: extracts.BeatConfig,
) -> list[extracts.EventRef]:
    """Return overridden event refs where the talk selection has been corrected."""
    key = (qcfg.namespace, qcfg.problem_id, beat.label, beat.student_id)
    return BEAT_EVENT_OVERRIDES.get(key, beat.event_refs)


def extract_function_body(code: str) -> str:
    """Strip the template docstring and show the actual student implementation for the event."""
    lines = code.rstrip().splitlines()
    if not lines:
        return "# [missing code snapshot]"

    def_idx = next(
        (idx for idx, line in enumerate(lines) if line.lstrip().startswith("def ")),
        None,
    )
    if def_idx is None:
        return code.strip() or "# [missing code snapshot]"

    out = [lines[def_idx]]
    idx = def_idx + 1

    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    if idx < len(lines):
        stripped = lines[idx].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            idx += 1
            while idx < len(lines):
                if quote in lines[idx]:
                    idx += 1
                    break
                idx += 1
            while idx < len(lines) and not lines[idx].strip():
                idx += 1

    out.extend(lines[idx:])
    snippet = "\n".join(out).rstrip()
    return snippet or code.strip() or "# [missing code snapshot]"


def slide_class_for_code(code: str) -> str | None:
    """Pick a smaller code font for longer event snapshots."""
    line_count = code.count("\n") + 1
    if line_count >= 26:
        return "dense"
    if line_count >= 14:
        return "compact"
    return None


def fmt_tests(event: dict[str, object]) -> str:
    passed = event.get("num_test_passed")
    total = event.get("test_case_count")
    if passed is None or total is None:
        return "-"
    return f"{passed}/{total}"


def fmt_score(event: dict[str, object]) -> str | None:
    score = event.get("score")
    if score is None:
        return None
    value = float(score)
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.1f}"


def event_commentary(ref: extracts.EventRef, event: dict[str, object]) -> str:
    """Build a one-line slide commentary from the evaluator state plus the talk note."""
    event_type = str(event.get("event_type") or "").replace("_", " ")
    evaluation = str(event.get("evaluation_type") or "")
    prefix = f"{event_type.title()} · {evaluation.title()} · {event.get('summary')} · {fmt_tests(event)}"
    if evaluation == "private" or event_type == "submission":
        score = fmt_score(event)
        if score is not None:
            prefix += f" · score {score}"
    return f"{prefix}: {ref.note}"


def render_question_slide(
    qcfg: extracts.QuestionConfig,
    problem: dict[str, object],
) -> list[str]:
    """Render the section-opening slide with the actual question prompt."""
    title = str(problem.get("short_description") or f"Question {qcfg.order}")
    prompt_html = sanitize_question_html(str(problem["question"]))
    commentary = QUESTION_COMMENTARY[(qcfg.namespace, qcfg.problem_id)]
    return [
        "<!--",
        f"namespace: {qcfg.namespace}",
        f"problem_id: {qcfg.problem_id}",
        f"section: question_{qcfg.order}",
        "-->",
        "<!-- _class: question -->",
        f"# Question {qcfg.order} · {title}",
        "",
        prompt_html,
        "",
        commentary,
    ]


def render_event_slide(
    qcfg: extracts.QuestionConfig,
    beat: extracts.BeatConfig,
    ref: extracts.EventRef,
    event: dict[str, object],
    code: str,
) -> list[str]:
    """Render one event-level slide for a student attempt."""
    class_name = slide_class_for_code(code)
    lines = [
        "<!--",
        f"namespace: {qcfg.namespace}",
        f"problem_id: {qcfg.problem_id}",
        f"student_id: {beat.student_id}",
        f"beat: {beat.label}",
        f"event_no: {ref.event_no}",
        "-->",
    ]
    if class_name:
        lines.append(f"<!-- _class: {class_name} -->")
    lines.extend(
        [
            f"# Q{qcfg.order} · {beat.label} · Event {ref.event_no}",
            "",
            "```python",
            code,
            "```",
            "",
            event_commentary(ref, event),
        ]
    )
    return lines


def build_markdown() -> str:
    """Build the full expanded deck."""
    lines = [
        "---",
        "marp: true",
        "theme: default",
        "paginate: true",
        "size: 16:9",
        "style: |",
        "  section {",
        "    font-size: 28px;",
        "  }",
        "  section h1 {",
        "    font-size: 1.25em;",
        "  }",
        "  section pre {",
        "    font-size: 0.74em;",
        "  }",
        "  section.compact pre {",
        "    font-size: 0.60em;",
        "  }",
        "  section.dense pre {",
        "    font-size: 0.48em;",
        "  }",
        "  section.question {",
        "    font-size: 22px;",
        "  }",
        "  section.question pre {",
        "    font-size: 0.58em;",
        "  }",
        "  section.question li {",
        "    margin-bottom: 0.15em;",
        "  }",
        "---",
    ]

    first_slide = True
    event_cache: dict[tuple[str, int, str], dict[int, dict[str, object]]] = {}

    for qcfg in extracts.QUESTIONS:
        problem = extracts.load_problem(qcfg.namespace, qcfg.problem_id)
        question_slide = render_question_slide(qcfg, problem)
        if first_slide:
            lines.append("")
            first_slide = False
        else:
            lines.extend(["", "---", ""])
        lines.extend(question_slide)

        skeleton = extracts.extract_skeleton(problem)
        for beat in qcfg.beats:
            key = (qcfg.namespace, qcfg.problem_id, beat.student_id)
            if key not in event_cache:
                event_cache[key] = extracts.load_events(
                    qcfg.namespace,
                    qcfg.problem_id,
                    beat.student_id,
                    skeleton,
                )
            events = event_cache[key]
            for ref in effective_event_refs(qcfg, beat):
                event = events[ref.event_no]
                code = extract_function_body(str(event["student_code"]))
                lines.extend(
                    [
                        "",
                        "---",
                        "",
                        *render_event_slide(qcfg, beat, ref, event, code),
                    ]
                )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    markdown = build_markdown()
    OUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
