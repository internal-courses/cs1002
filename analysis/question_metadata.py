#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_DIR = ROOT / "problems"
OUT_CSV = ROOT / "analysis" / "question_metadata.csv"


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_title(question_html: str) -> str:
    m = re.search(r"<h1>\s*<b>([^<]+)</b>", question_html or "")
    if m:
        return m.group(1).strip()
    plain = strip_html(question_html)
    return plain[:120].strip()


def has_skeleton_code(problem: dict) -> bool:
    langs = problem.get("allowed_languages") or []
    for lang in langs:
        template = (lang.get("code_template") or "").strip()
        if template:
            return True
    return "Template Code" in (problem.get("question") or "")


def main() -> None:
    rows = []
    for namespace_dir in sorted(PROBLEMS_DIR.glob("*")):
        if not namespace_dir.is_dir():
            continue
        namespace = namespace_dir.name

        files = sorted(namespace_dir.glob("*.json"), key=lambda p: int(p.stem))
        for problem_file in files:
            problem_id = int(problem_file.stem)
            with problem_file.open("r", encoding="utf-8") as f:
                obj = json.load(f)

            question_html = obj.get("question") or ""
            question_text = strip_html(question_html)
            question_title = extract_title(question_html)
            public_tests = obj.get("public_testcase") or []
            private_tests = obj.get("private_testcase") or []

            rows.append(
                {
                    "namespace": namespace,
                    "problem_id": problem_id,
                    "question_title": question_title,
                    "question_text": question_text,
                    "has_skeleton_code": has_skeleton_code(obj),
                    "num_public_tests": len(public_tests),
                    "num_private_tests": len(private_tests),
                }
            )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "namespace",
                "problem_id",
                "question_title",
                "question_text",
                "has_skeleton_code",
                "num_public_tests",
                "num_private_tests",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT_CSV} rows={len(rows)}")


if __name__ == "__main__":
    main()
