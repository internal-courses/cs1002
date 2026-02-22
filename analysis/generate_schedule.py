#!/usr/bin/env python3
import csv
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "analysis" / "schedule.csv"
IST_OFFSET = timedelta(hours=5, minutes=30)


def floor_15(dt: datetime) -> datetime:
    return dt - timedelta(minutes=dt.minute % 15, seconds=dt.second, microseconds=dt.microsecond)


def ceil_15(dt: datetime) -> datetime:
    floored = floor_15(dt)
    if dt == floored:
        return dt
    return floored + timedelta(minutes=15)


def to_iso_ist(dt_utc: datetime) -> str:
    dt_ist = dt_utc + IST_OFFSET
    return dt_ist.strftime("%Y-%m-%dT%H:%M:%S+05:30")


def clean_text(s: str) -> str:
    s = s.replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip(" .")
    s = re.split(r"\b(Implement|Write)\b", s, maxsplit=1)[0].strip() or s
    s = re.split(r"(?<=[.!?])\s+", s, maxsplit=1)[0]
    if len(s) > 88:
        s = s[:85].rstrip() + "..."
    return s.strip(" .")


def question_summary(problem_json: Path) -> str:
    with problem_json.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    short = (obj.get("short_description") or "").strip()
    if short:
        return clean_text(short)

    question = obj.get("question") or ""
    m = re.search(r"<h1>\s*<b>([^<]+)</b>", question)
    if m:
        return clean_text(m.group(1))

    plain = re.sub(r"<[^>]+>", " ", question)
    plain = re.sub(r"\s+", " ", plain).strip()
    return clean_text(plain[:120] if plain else "[no summary]")


def load_question_lists() -> dict[str, str]:
    by_namespace: dict[str, list[tuple[int, str]]] = {}
    for p in (ROOT / "problems").glob("**/*.json"):
        rel = p.relative_to(ROOT / "problems")
        if len(rel.parts) != 2:
            continue
        namespace = rel.parts[0]
        if not rel.parts[1].endswith(".json"):
            continue
        problem_id = int(rel.parts[1].replace(".json", ""))
        by_namespace.setdefault(namespace, []).append((problem_id, question_summary(p)))

    out: dict[str, str] = {}
    for namespace, items in by_namespace.items():
        items.sort(key=lambda x: x[0])
        arr = [f"Q{problem_id}: {summary}." for problem_id, summary in items]
        out[namespace] = json.dumps(arr, ensure_ascii=True)
    return out


def fetch_namespace_windows() -> list[tuple[str, str, str, datetime, datetime, int]]:
    query = """
    WITH activity AS (
      SELECT
        Namespace,
        regexp_extract(Namespace, '^ns_([0-9]{2}t[0-9]+)_', 1) AS term,
        regexp_extract(regexp_replace(Namespace, '_(1|2)$', ''), '^ns_[0-9]{2}t[0-9]+_(.*)$', 1) AS exam_token,
        strptime(
          regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1),
          '%Y-%m-%dT%H:%M:%S.%fZ'
        ) AS ts_utc
      FROM read_json(
        'submissions/*.json',
        format='newline_delimited',
        columns={Namespace:'VARCHAR', FileName:'VARCHAR'}
      )
      WHERE Namespace IS NOT NULL AND FileName IS NOT NULL AND FileName <> ''
    ), per_ns AS (
      SELECT
        term,
        CASE
          WHEN exam_token IN ('py11','py12','py13','py14') THEN 'wave1'
          WHEN exam_token IN ('py21','py22','py23','py24') THEN 'wave2'
          ELSE 'other'
        END AS wave,
        Namespace,
        quantile_cont(ts_utc, 0.025) AS q025_utc,
        quantile_cont(ts_utc, 0.975) AS q975_utc
      FROM activity
      GROUP BY term, wave, Namespace
    ), students AS (
      SELECT
        Namespace,
        COUNT(DISTINCT StudentID) AS num_students
      FROM read_csv_auto('analysis/final_scores.csv', header=true)
      GROUP BY Namespace
    )
    SELECT
      p.term,
      p.wave,
      p.Namespace,
      p.q025_utc,
      p.q975_utc,
      coalesce(s.num_students, 0) AS num_students
    FROM per_ns p
    LEFT JOIN students s USING (Namespace)
    ORDER BY p.q025_utc, p.term, p.wave, p.Namespace
    """

    res = subprocess.run(
        ["duckdb", "-csv", "-c", query],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    rows: list[tuple[str, str, str, datetime, datetime, int]] = []
    reader = csv.DictReader(res.stdout.splitlines())
    for row in reader:
        rows.append(
            (
                row["term"],
                row["wave"],
                row["Namespace"],
                datetime.strptime(row["q025_utc"], "%Y-%m-%d %H:%M:%S.%f"),
                datetime.strptime(row["q975_utc"], "%Y-%m-%d %H:%M:%S.%f"),
                int(float(row["num_students"])),
            )
        )
    return rows


def main() -> None:
    namespace_rows = fetch_namespace_windows()
    question_lists = load_question_lists()

    output_rows = []
    for term, wave, namespace, q025_utc, q975_utc, num_students in namespace_rows:
        start_utc = floor_15(q025_utc)
        end_utc = ceil_15(q975_utc)
        output_rows.append(
            {
                "term": term,
                "wave": wave,
                "namespace": namespace,
                "start_time": to_iso_ist(start_utc),
                "end_time": to_iso_ist(end_utc),
                "num_students": num_students,
                "questions": question_lists.get(namespace, "[]"),
            }
        )

    # ISO 8601 strings sort chronologically.
    output_rows.sort(key=lambda r: (r["start_time"], r["term"], r["wave"], r["namespace"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["term", "wave", "namespace", "start_time", "end_time", "num_students", "questions"],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"wrote {OUT_CSV} rows={len(output_rows)}")


if __name__ == "__main__":
    main()
