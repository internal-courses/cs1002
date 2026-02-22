#!/usr/bin/env python3
import ast
import base64
import csv
import hashlib
import io
import json
import re
import subprocess
import warnings
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_TIMELINE_PARQUET = ROOT / "analysis" / "submission_timeline.parquet"
OUT_CODE_PARQUET = ROOT / "analysis" / "code_snapshots.parquet"
TEMP_TIMELINE_JSONL = ROOT / "analysis" / "_submission_timeline_tmp.jsonl"
TEMP_CODES_JSONL = ROOT / "analysis" / "_code_snapshots_tmp.jsonl"

TS_RE = re.compile(r"_(\d{4}-\d{2}-\d{2}T[0-9:.]+Z)$")
EVENT_RE = re.compile(r"/(saved_code|test_run|submission)/")
IST_OFFSET = timedelta(hours=5, minutes=30)


def parse_ts(ts: str):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            pass
    return None


def extract_ts_from_filename(filename: str):
    m = TS_RE.search(filename or "")
    if not m:
        return None
    return parse_ts(m.group(1))


def extract_event_type(filename: str):
    m = EVENT_RE.search(filename or "")
    return m.group(1) if m else None


def decode_code_snapshot(b64_code: str) -> str:
    if not b64_code:
        return ""
    try:
        raw = base64.b64decode(b64_code)
    except Exception:
        return ""

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if not names:
                return ""
            py_names = sorted([n for n in names if n.lower().endswith(".py")])
            pick = py_names[0] if py_names else sorted(names)[0]
            return zf.read(pick).decode("utf-8", errors="replace")
    except Exception:
        return raw.decode("utf-8", errors="replace")


def parse_test_metrics(compilation_result: str):
    if not compilation_result:
        return {
            "status": None,
            "reason": None,
            "summary": None,
            "score": None,
            "num_test_evaluated": None,
            "num_test_passed": None,
            "test_case_count": None,
        }

    try:
        obj = json.loads(compilation_result)
    except Exception:
        return {
            "status": None,
            "reason": None,
            "summary": None,
            "score": None,
            "num_test_evaluated": None,
            "num_test_passed": None,
            "test_case_count": None,
        }

    test_case_results = obj.get("test_case_results")
    test_case_count = len(test_case_results) if isinstance(test_case_results, list) else None

    return {
        "status": obj.get("status"),
        "reason": obj.get("reason"),
        "summary": obj.get("summary"),
        "score": obj.get("score"),
        "num_test_evaluated": obj.get("num_test_evaluated"),
        "num_test_passed": obj.get("num_test_passed"),
        "test_case_count": test_case_count,
    }


def is_parseable_python(code: str) -> bool:
    if code == "":
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ast.parse(code)
        return True
    except Exception:
        return False


def load_start_map():
    query = r'''
    SELECT
      Namespace,
      CAST(ProblemID AS INTEGER) AS problem_id,
      StudentID,
      MIN(
        strptime(
          regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1),
          '%Y-%m-%dT%H:%M:%S.%fZ'
        )
      ) AS first_event_utc
    FROM read_json(
      'submissions/*.json',
      format='newline_delimited',
      columns={Namespace:'VARCHAR', ProblemID:'VARCHAR', StudentID:'VARCHAR', FileName:'VARCHAR'}
    )
    WHERE FileName IS NOT NULL AND FileName <> ''
    GROUP BY Namespace, problem_id, StudentID
    ORDER BY Namespace, problem_id, StudentID
    '''

    res = subprocess.run(
        ["duckdb", "-csv", "-c", query],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    starts = {}
    reader = csv.DictReader(res.stdout.splitlines())
    for r in reader:
        starts[(r["Namespace"], int(r["problem_id"]), r["StudentID"])] = datetime.strptime(
            r["first_event_utc"], "%Y-%m-%d %H:%M:%S.%f"
        )
    return starts


def iter_submission_files():
    return sorted((ROOT / "submissions").glob("*.json"))


def materialize_parquet(timeline_rows_written: int, unique_code_rows_written: int):
    if timeline_rows_written == 0:
        raise RuntimeError("No timeline rows were written; aborting parquet materialization.")

    timeline_query = f"""
    COPY (
      SELECT
        namespace::VARCHAR AS namespace,
        CAST(problem_id AS INTEGER) AS problem_id,
        student_id::VARCHAR AS student_id,
        CAST(timestamp_utc AS TIMESTAMP) AS timestamp_utc,
        CAST(timestamp_ist AS TIMESTAMP) AS timestamp_ist,
        event_type::VARCHAR AS event_type,
        evaluation_type::VARCHAR AS evaluation_type,
        CAST(seconds_since_start AS BIGINT) AS seconds_since_start,
        code_sha256::VARCHAR AS code_sha256,
        CAST(code_length AS BIGINT) AS code_length,
        CAST(is_parseable AS BOOLEAN) AS is_parseable,
        CAST(status AS BIGINT) AS status,
        reason::VARCHAR AS reason,
        summary::VARCHAR AS summary,
        CAST(score AS DOUBLE) AS score,
        CAST(num_test_evaluated AS BIGINT) AS num_test_evaluated,
        CAST(num_test_passed AS BIGINT) AS num_test_passed,
        CAST(test_case_count AS BIGINT) AS test_case_count
      FROM read_json('{TEMP_TIMELINE_JSONL.as_posix()}', format='newline_delimited')
      ORDER BY timestamp_utc, namespace, problem_id, student_id
    ) TO '{OUT_TIMELINE_PARQUET.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD);
    """
    subprocess.run(["duckdb", "-bail", "-c", timeline_query], cwd=str(ROOT), check=True)

    if unique_code_rows_written > 0:
        code_query = f"""
        COPY (
          SELECT
            code_sha256::VARCHAR AS code_sha256,
            CAST(code_length AS BIGINT) AS code_length,
            CAST(is_parseable AS BOOLEAN) AS is_parseable,
            code_snapshot::VARCHAR AS code_snapshot
          FROM read_json('{TEMP_CODES_JSONL.as_posix()}', format='newline_delimited')
          ORDER BY code_sha256
        ) TO '{OUT_CODE_PARQUET.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD);
        """
    else:
        code_query = f"""
        COPY (
          SELECT
            CAST(NULL AS VARCHAR) AS code_sha256,
            CAST(NULL AS BIGINT) AS code_length,
            CAST(NULL AS BOOLEAN) AS is_parseable,
            CAST(NULL AS VARCHAR) AS code_snapshot
          WHERE FALSE
        ) TO '{OUT_CODE_PARQUET.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD);
        """

    subprocess.run(["duckdb", "-bail", "-c", code_query], cwd=str(ROOT), check=True)


def main() -> None:
    print("[1/5] Loading combo start times...")
    start_map = load_start_map()

    print("[2/5] Streaming standardized timeline rows...")
    TEMP_TIMELINE_JSONL.parent.mkdir(parents=True, exist_ok=True)

    timeline_rows_written = 0
    unique_code_rows_written = 0
    parseable_true = 0

    code_meta_cache: dict[str, tuple[int, bool]] = {}

    with TEMP_TIMELINE_JSONL.open("w", encoding="utf-8") as timeline_out, TEMP_CODES_JSONL.open(
        "w", encoding="utf-8"
    ) as codes_out:
        for fp in iter_submission_files():
            file_rows = 0
            with fp.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except Exception:
                        continue

                    namespace = row.get("Namespace")
                    problem_raw = row.get("ProblemID")
                    student_id = row.get("StudentID")
                    filename = row.get("FileName")
                    evaluation_type = row.get("EvaluationType")

                    if not namespace or not problem_raw or not student_id or not filename:
                        continue

                    try:
                        problem_id = int(problem_raw)
                    except Exception:
                        continue

                    event_ts_utc = extract_ts_from_filename(filename)
                    if event_ts_utc is None:
                        continue

                    start_ts_utc = start_map.get((namespace, problem_id, student_id))
                    if start_ts_utc is None:
                        continue

                    event_type = extract_event_type(filename)
                    code = decode_code_snapshot(row.get("Base64Code") or "")

                    if code:
                        code_sha256 = hashlib.sha256(code.encode("utf-8", errors="ignore")).hexdigest()
                        if code_sha256 in code_meta_cache:
                            code_length, parseable = code_meta_cache[code_sha256]
                        else:
                            code_length = len(code)
                            parseable = is_parseable_python(code)
                            code_meta_cache[code_sha256] = (code_length, parseable)
                            codes_out.write(
                                json.dumps(
                                    {
                                        "code_sha256": code_sha256,
                                        "code_length": code_length,
                                        "is_parseable": parseable,
                                        "code_snapshot": code,
                                    },
                                    ensure_ascii=False,
                                )
                                + "\n"
                            )
                            unique_code_rows_written += 1
                    else:
                        code_sha256 = None
                        code_length = 0
                        parseable = False

                    if parseable:
                        parseable_true += 1

                    metrics = parse_test_metrics(row.get("CompilationResult") or "")
                    event_ts_ist = event_ts_utc + IST_OFFSET

                    out_row = {
                        "namespace": namespace,
                        "problem_id": problem_id,
                        "student_id": student_id,
                        "timestamp_utc": event_ts_utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "timestamp_ist": event_ts_ist.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "event_type": event_type,
                        "evaluation_type": evaluation_type,
                        "seconds_since_start": int((event_ts_utc - start_ts_utc).total_seconds()),
                        "code_sha256": code_sha256,
                        "code_length": code_length,
                        "is_parseable": parseable,
                        "status": metrics["status"],
                        "reason": metrics["reason"],
                        "summary": metrics["summary"],
                        "score": metrics["score"],
                        "num_test_evaluated": metrics["num_test_evaluated"],
                        "num_test_passed": metrics["num_test_passed"],
                        "test_case_count": metrics["test_case_count"],
                    }

                    timeline_out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
                    timeline_rows_written += 1
                    file_rows += 1

                    if timeline_rows_written % 100000 == 0:
                        print(f"  processed {timeline_rows_written:,} rows...")

            print(f"  file done: {fp.name} ({file_rows:,} rows)")

    print("[3/5] Materializing Parquet outputs...")
    materialize_parquet(timeline_rows_written, unique_code_rows_written)

    print("[4/5] Cleaning temporary files...")
    TEMP_TIMELINE_JSONL.unlink(missing_ok=True)
    TEMP_CODES_JSONL.unlink(missing_ok=True)

    # Legacy file can be removed to save space; parquet is the canonical output.
    (ROOT / "analysis" / "submission_timeline.json").unlink(missing_ok=True)

    print("[5/5] Done")
    print(f"timeline_rows={timeline_rows_written}")
    print(f"unique_code_snapshots={unique_code_rows_written}")
    print(f"parseable_true_rows={parseable_true}")
    print(f"timeline_parquet={OUT_TIMELINE_PARQUET}")
    print(f"code_parquet={OUT_CODE_PARQUET}")


if __name__ == "__main__":
    main()
