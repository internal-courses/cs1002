#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.2.2", "pandas>=2.2"]
# ///
"""Generate a TA/faculty learning-support pack from the v2 parquet export."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import math
from pathlib import Path

import duckdb
import pandas as pd

V2_DIR = Path(__file__).resolve().parent
DATA_GLOB = (V2_DIR / "data" / "bq-results-*").as_posix()
OUT_DIR = V2_DIR / "learning-support"
OUT_MD = V2_DIR / "learning-support.md"


def pct(value: float | int | None, digits: int = 0) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{100 * float(value):.{digits}f}%"


def fmt_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{int(value):,}"


def fmt_ts(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return value.strftime("%Y-%m-%d %H:%M UTC")


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def query_df(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return con.execute(sql).df()


def build_views(con: duckdb.DuckDBPyConnection) -> None:
    path = DATA_GLOB.replace("'", "''")
    con.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW event_base AS
        SELECT
          current_namespace AS namespace,
          key AS learner_key,
          unit_id,
          submission_type,
          regexp_extract(filename, '/(saved_code|test_run|submission)/', 1) AS event_type,
          try_strptime(
            regexp_extract(filename, '_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}T[0-9:.]+Z)$', 1),
            '%Y-%m-%dT%H:%M:%S.%fZ'
          ) AS timestamp_utc,
          try_cast(json_extract_string(data, '$.num_test_evaluated') AS INTEGER) AS num_test_evaluated,
          try_cast(json_extract_string(data, '$.num_test_passed') AS INTEGER) AS num_test_passed,
          CASE
            WHEN try_cast(json_extract_string(data, '$.num_test_evaluated') AS INTEGER) > 0
            THEN
              try_cast(json_extract_string(data, '$.num_test_passed') AS DOUBLE)
              / try_cast(json_extract_string(data, '$.num_test_evaluated') AS DOUBLE)
          END AS pass_rate,
          try_cast(json_extract_string(data, '$.score') AS DOUBLE) AS score,
          json_extract_string(data, '$.summary') AS summary,
          length(data) AS data_len,
          filename
        FROM read_parquet('{path}')
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW pair_runs AS
        SELECT
          ANY_VALUE(learner_key) AS learner_key,
          ANY_VALUE(unit_id) AS unit_id,
          ANY_VALUE(timestamp_utc) AS timestamp_utc,
          filename,
          MAX(pass_rate) FILTER (WHERE submission_type = 'public') AS public_pass_rate,
          MAX(pass_rate) FILTER (WHERE submission_type = 'private') AS private_pass_rate,
          MAX(summary) FILTER (WHERE submission_type = 'public') AS public_summary,
          MAX(summary) FILTER (WHERE submission_type = 'private') AS private_summary
        FROM event_base
        WHERE event_type = 'test_run'
        GROUP BY filename
        HAVING COUNT(*) = 2 AND COUNT(DISTINCT submission_type) = 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TEMP VIEW unit_meta AS
        SELECT
          unit_id,
          MAX(timestamp_utc) AS unit_end_ts,
          COUNT(*) FILTER (
            WHERE submission_type = 'private' AND event_type = 'submission'
          ) AS submission_rows,
          COUNT(DISTINCT learner_key) AS learners
        FROM event_base
        GROUP BY unit_id
        """
    )


FEATURES_SQL = """
WITH overall AS (
  SELECT
    namespace,
    learner_key,
    unit_id,
    MIN(timestamp_utc) AS first_ts,
    MAX(timestamp_utc) AS last_ts,
    COUNT(*) AS total_rows
  FROM event_base
  GROUP BY 1, 2, 3
),
public_stats AS (
  SELECT
    learner_key,
    unit_id,
    COUNT(*) AS public_runs,
    arg_min(pass_rate, timestamp_utc) AS first_public_pass_rate,
    arg_max(pass_rate, timestamp_utc) AS last_public_pass_rate,
    arg_max(summary, timestamp_utc) AS last_public_summary,
    MAX(pass_rate) AS best_public_pass_rate,
    AVG(pass_rate) AS avg_public_pass_rate,
    SUM(pass_rate = 1) AS public_all_pass_count,
    SUM(summary = 'Runtime Error') AS runtime_count,
    SUM(summary = 'Wrong Answer') AS wrong_count,
    SUM(summary = 'All Cases Passed') AS all_pass_count,
    SUM(summary = 'Time Limit Exceeded') AS tle_count,
    SUM(summary = 'Not able to run') AS unable_count,
    SUM(data_len >= 10000) AS large_data_count,
    MAX(data_len) AS max_data_len
  FROM event_base
  WHERE submission_type = 'public'
  GROUP BY 1, 2
),
private_test_stats AS (
  SELECT
    learner_key,
    unit_id,
    COUNT(*) AS private_test_runs,
    MAX(pass_rate) AS best_private_test_pass_rate,
    arg_max(pass_rate, timestamp_utc) AS last_private_test_pass_rate,
    arg_max(summary, timestamp_utc) AS last_private_test_summary,
    SUM(pass_rate = 1) AS private_test_all_pass_count
  FROM event_base
  WHERE submission_type = 'private' AND event_type = 'test_run'
  GROUP BY 1, 2
),
submission_stats AS (
  SELECT
    learner_key,
    unit_id,
    COUNT(*) AS submissions,
    arg_max(score, timestamp_utc) AS last_submission_score,
    MAX(score) AS max_submission_score
  FROM event_base
  WHERE submission_type = 'private' AND event_type = 'submission'
  GROUP BY 1, 2
),
pair_stats AS (
  SELECT
    learner_key,
    unit_id,
    COUNT(*) AS paired_runs,
    SUM(public_pass_rate = 1) AS public_green_pairs,
    SUM(public_pass_rate = 1 AND private_pass_rate < 1) AS public_green_hidden_fail_count,
    MAX(public_pass_rate - private_pass_rate) AS max_public_private_gap,
    AVG(public_pass_rate - private_pass_rate) AS avg_public_private_gap,
    MAX(private_pass_rate) AS best_paired_private_pass_rate
  FROM pair_runs
  GROUP BY 1, 2
)
SELECT
  o.namespace,
  o.learner_key,
  o.unit_id,
  um.submission_rows > 0 AS submission_enabled,
  um.submission_rows,
  um.unit_end_ts,
  o.first_ts,
  o.last_ts,
  o.total_rows,
  COALESCE(ps.public_runs, 0) AS public_runs,
  COALESCE(pts.private_test_runs, 0) AS private_test_runs,
  COALESCE(ss.submissions, 0) AS submissions,
  ps.first_public_pass_rate,
  ps.last_public_pass_rate,
  ps.best_public_pass_rate,
  ps.avg_public_pass_rate,
  pts.best_private_test_pass_rate,
  pts.last_private_test_pass_rate,
  ss.last_submission_score,
  ss.max_submission_score,
  COALESCE(ps.public_all_pass_count, 0) AS public_all_pass_count,
  COALESCE(pts.private_test_all_pass_count, 0) AS private_test_all_pass_count,
  COALESCE(prs.paired_runs, 0) AS paired_runs,
  COALESCE(prs.public_green_pairs, 0) AS public_green_pairs,
  COALESCE(prs.public_green_hidden_fail_count, 0) AS public_green_hidden_fail_count,
  prs.max_public_private_gap,
  prs.avg_public_private_gap,
  prs.best_paired_private_pass_rate,
  COALESCE(ps.runtime_count, 0) AS runtime_count,
  COALESCE(ps.wrong_count, 0) AS wrong_count,
  COALESCE(ps.all_pass_count, 0) AS all_pass_count,
  COALESCE(ps.tle_count, 0) AS tle_count,
  COALESCE(ps.unable_count, 0) AS unable_count,
  COALESCE(ps.large_data_count, 0) AS large_data_count,
  COALESCE(ps.max_data_len, 0) AS max_data_len,
  ps.last_public_summary,
  pts.last_private_test_summary
FROM overall o
JOIN unit_meta um USING (unit_id)
LEFT JOIN public_stats ps USING (learner_key, unit_id)
LEFT JOIN private_test_stats pts USING (learner_key, unit_id)
LEFT JOIN submission_stats ss USING (learner_key, unit_id)
LEFT JOIN pair_stats prs USING (learner_key, unit_id)
"""


UNIT_STATS_SQL = """
WITH public_unit AS (
  SELECT
    unit_id,
    COUNT(*) AS public_runs,
    COUNT(DISTINCT learner_key) AS learners,
    AVG(pass_rate) AS avg_public_pass_rate,
    SUM(summary = 'Runtime Error') AS runtime_rows,
    SUM(summary = 'Wrong Answer') AS wrong_rows,
    SUM(summary = 'All Cases Passed') AS all_pass_rows,
    SUM(summary = 'Time Limit Exceeded') AS tle_rows,
    SUM(data_len >= 10000) AS large_data_rows,
    MAX(data_len) AS max_data_len
  FROM event_base
  WHERE submission_type = 'public'
  GROUP BY 1
),
pair_unit AS (
  SELECT
    unit_id,
    COUNT(*) AS paired_runs,
    AVG(CASE WHEN public_pass_rate = 1 AND private_pass_rate < 1 THEN 1 ELSE 0 END) AS public_green_hidden_fail_rate,
    AVG(CASE WHEN public_pass_rate = 1 THEN 1 ELSE 0 END) AS public_all_pass_rate,
    AVG(CASE WHEN private_pass_rate = 1 THEN 1 ELSE 0 END) AS private_all_pass_rate,
    AVG(public_pass_rate - private_pass_rate) AS avg_public_private_gap
  FROM pair_runs
  GROUP BY 1
)
SELECT
  um.unit_id,
  um.submission_rows > 0 AS submission_enabled,
  um.submission_rows,
  um.learners,
  um.unit_end_ts,
  pu.public_runs,
  pu.avg_public_pass_rate,
  pu.runtime_rows,
  pu.wrong_rows,
  pu.all_pass_rows,
  pu.tle_rows,
  pu.large_data_rows,
  pu.max_data_len,
  COALESCE(pru.paired_runs, 0) AS paired_runs,
  pru.public_green_hidden_fail_rate,
  pru.public_all_pass_rate,
  pru.private_all_pass_rate,
  pru.avg_public_private_gap
FROM unit_meta um
LEFT JOIN public_unit pu USING (unit_id)
LEFT JOIN pair_unit pru USING (unit_id)
ORDER BY try_cast(um.unit_id AS INT)
"""


@dataclass(frozen=True)
class SegmentSpec:
    label: str
    owner_role: str
    target_window: str
    goal: str
    base_priority: int


SEGMENTS = {
    "ready_to_finish": SegmentSpec(
        label="Ready to finish",
        owner_role="TA or mentor submit nudge",
        target_window="same day",
        goal="finish_and_submit",
        base_priority=100,
    ),
    "false_confidence_hidden_gap": SegmentSpec(
        label="False confidence / hidden-test risk",
        owner_role="TA edge-case clinic",
        target_window="within 48h",
        goal="close_hidden_gap",
        base_priority=95,
    ),
    "severe_thrashing": SegmentSpec(
        label="Severe thrashing without transfer",
        owner_role="TA live support",
        target_window="within 24h",
        goal="unstick_learning",
        base_priority=90,
    ),
    "no_traction": SegmentSpec(
        label="No traction yet",
        owner_role="TA foundations check-in",
        target_window="within 72h",
        goal="build_initial_traction",
        base_priority=80,
    ),
    "moderate_thrashing": SegmentSpec(
        label="Moderate thrashing",
        owner_role="TA clinic",
        target_window="within 72h",
        goal="unstick_learning",
        base_priority=75,
    ),
    "quiet_disengagement": SegmentSpec(
        label="Quiet disengagement",
        owner_role="Mentor outreach",
        target_window="within 48h",
        goal="reengage",
        base_priority=65,
    ),
}


def dominant_bug_type(row: pd.Series) -> str:
    if row["public_green_hidden_fail_count"] >= 1 and (row["best_private_test_pass_rate"] or 0) < 1:
        return "hidden_test_gap"
    if row["tle_count"] > 0 or row["large_data_count"] > 0:
        return "pathological_output_or_nontermination"
    if row["runtime_count"] >= max(row["wrong_count"], 3) and row["runtime_count"] / max(row["public_runs"], 1) >= 0.4:
        return "runtime_dominant"
    if row["wrong_count"] > row["runtime_count"] and row["wrong_count"] >= 3 and row["wrong_count"] / max(row["public_runs"], 1) >= 0.4:
        return "logic_or_edge_case_dominant"
    if (row["best_public_pass_rate"] or 0) >= 0.8:
        return "near_success"
    return "mixed_or_low_signal"


def choose_segment(row: pd.Series) -> str | None:
    best_pub = row["best_public_pass_rate"] or 0.0
    best_priv = row["best_private_test_pass_rate"] or 0.0
    last_pub = row["last_public_pass_rate"] or 0.0
    days_before_end = row["days_before_unit_end"]

    if (
        row["submission_enabled"]
        and row["submissions"] == 0
        and days_before_end <= 1
        and row["public_green_hidden_fail_count"] == 0
        and (
            best_priv >= 1.0
            or (best_pub >= 0.8 and last_pub >= 0.8 and row["public_runs"] >= 3)
        )
    ):
        return "ready_to_finish"

    if row["public_green_hidden_fail_count"] >= 1 and best_priv < 1:
        return "false_confidence_hidden_gap"

    if row["total_rows"] > 54 and best_pub < 0.8:
        return "severe_thrashing"

    if row["public_runs"] >= 5 and best_pub <= 0.2:
        return "no_traction"

    if row["total_rows"] > 21 and best_pub < 0.8:
        return "moderate_thrashing"

    if row["public_runs"] <= 8 and best_pub < 0.5 and days_before_end >= 2:
        return "quiet_disengagement"

    return None


def bug_evidence(row: pd.Series) -> str:
    parts: list[str] = []
    if row["runtime_count"] > 0:
        parts.append(f"runtime {fmt_int(row['runtime_count'])}")
    if row["wrong_count"] > 0:
        parts.append(f"wrong-answer {fmt_int(row['wrong_count'])}")
    if row["tle_count"] > 0:
        parts.append(f"TLE {fmt_int(row['tle_count'])}")
    if row["large_data_count"] > 0:
        parts.append(f"large-payload {fmt_int(row['large_data_count'])}")
    return ", ".join(parts) if parts else "low-signal errors"


def build_evidence(row: pd.Series) -> str:
    best_pub = pct(row["best_public_pass_rate"])
    best_priv = pct(row["best_private_test_pass_rate"])
    pieces = [f"{fmt_int(row['total_rows'])} rows", f"best public {best_pub}"]

    if row["submission_enabled"]:
        pieces.append(f"best hidden {best_priv}")

    if row["public_green_hidden_fail_count"] > 0:
        pieces.append(
            f"public-green/hidden-fail {fmt_int(row['public_green_hidden_fail_count'])}x"
        )

    if row["public_all_pass_count"] > 0:
        pieces.append(f"public all-pass {fmt_int(row['public_all_pass_count'])}x")

    if row["submissions"] == 0 and row["submission_enabled"]:
        pieces.append("no submission")

    pieces.append(bug_evidence(row))
    pieces.append(f"last activity {row['days_before_unit_end']:.1f}d before unit close")
    return "; ".join(pieces)


def intervention_text(row: pd.Series) -> str:
    segment = row["risk_segment"]
    bug_type = row["dominant_bug_type"]
    if segment == "ready_to_finish":
        return "Send a submit-now nudge. Ask for one final self-check on I/O and edge cases, then submit the current solution."
    if segment == "false_confidence_hidden_gap":
        return "Run a 15-minute boundary-case review. Ask the learner to write five hidden-case candidates before the next attempt."
    if segment in {"severe_thrashing", "moderate_thrashing"} and bug_type == "runtime_dominant":
        return "Book a live debugging session. Trace the code line by line on three tiny inputs before allowing another attempt burst."
    if segment in {"severe_thrashing", "moderate_thrashing"} and bug_type == "logic_or_edge_case_dominant":
        return "Do a reasoning clinic. Restate the prompt, list boundary cases, and check assumptions before re-running code."
    if segment in {"severe_thrashing", "moderate_thrashing"} and bug_type == "pathological_output_or_nontermination":
        return "Focus on loop termination and print discipline. Strip diagnostics, test on minimal inputs, and reintroduce logic incrementally."
    if segment == "no_traction":
        return "Use a foundations check-in: isolate I/O parsing, hand-simulate one tiny case, and verify one branch at a time."
    if segment == "quiet_disengagement":
        return "Do outreach, not analytics. Send a short message, ask what blocked progress, and offer one specific support slot."
    return "Review recent attempts and choose the closest matching support lane."


def faculty_action(row: pd.Series) -> str:
    if (row["public_green_hidden_fail_rate"] or 0) >= 0.05:
        return "Review public/private test alignment and add explicit edge-case coaching for TAs."
    if row["tle_rows"] > 0 or row["large_data_rows"] > 0:
        return "Add a TA note on loop termination and stripping debug prints before reruns."
    runtime_rate = row["runtime_rows"] / max(row["public_runs"], 1)
    wrong_rate = row["wrong_rows"] / max(row["public_runs"], 1)
    if runtime_rate >= wrong_rate + 0.1:
        return "Emphasize debugging help: tracing, types, indexing, and variable initialization."
    if wrong_rate >= runtime_rate + 0.1:
        return "Emphasize edge-case reasoning: interpretation, boundaries, and test design."
    return "Mixed support pattern; route by learner-level bug type."


def ta_focus(row: pd.Series) -> str:
    if (row["public_green_hidden_fail_rate"] or 0) >= 0.05:
        return "Edge-case / hidden-test coaching"
    if row["tle_rows"] > 0 or row["large_data_rows"] > 0:
        return "Loop termination and print discipline"
    runtime_rate = row["runtime_rows"] / max(row["public_runs"], 1)
    wrong_rate = row["wrong_rows"] / max(row["public_runs"], 1)
    if runtime_rate >= wrong_rate + 0.1:
        return "Debugging clinic"
    if wrong_rate >= runtime_rate + 0.1:
        return "Reasoning and edge-case clinic"
    return "Mixed support"


def priority_score(row: pd.Series) -> float:
    spec = SEGMENTS[row["risk_segment"]]
    score = float(spec.base_priority)
    score += min(float(row["total_rows"]), 80) * 0.25
    score += min(float(row["public_green_hidden_fail_count"]), 3) * 6
    score += min(float(row["days_before_unit_end"]), 3) * 0.5
    if row["recent_cycle"]:
        score += 5
    if row["submission_enabled"]:
        score += 3
    return round(score, 2)


def build_outputs(features: pd.DataFrame, unit_stats: pd.DataFrame) -> dict[str, pd.DataFrame | str]:
    features = features.copy()
    features["unit_end_ts"] = pd.to_datetime(features["unit_end_ts"], utc=True)
    features["first_ts"] = pd.to_datetime(features["first_ts"], utc=True)
    features["last_ts"] = pd.to_datetime(features["last_ts"], utc=True)

    count_cols = [
        "submission_rows",
        "total_rows",
        "public_runs",
        "private_test_runs",
        "submissions",
        "public_all_pass_count",
        "private_test_all_pass_count",
        "paired_runs",
        "public_green_pairs",
        "public_green_hidden_fail_count",
        "runtime_count",
        "wrong_count",
        "all_pass_count",
        "tle_count",
        "unable_count",
        "large_data_count",
        "max_data_len",
    ]
    for col in count_cols:
        features[col] = features[col].fillna(0).astype(int)

    rate_cols = [
        "first_public_pass_rate",
        "last_public_pass_rate",
        "best_public_pass_rate",
        "avg_public_pass_rate",
        "best_private_test_pass_rate",
        "last_private_test_pass_rate",
        "last_submission_score",
        "max_submission_score",
        "max_public_private_gap",
        "avg_public_private_gap",
        "best_paired_private_pass_rate",
    ]
    for col in rate_cols:
        features[col] = pd.to_numeric(features[col], errors="coerce")

    global_max = features["unit_end_ts"].max()
    features["days_before_unit_end"] = (
        (features["unit_end_ts"] - features["last_ts"]).dt.total_seconds() / 86400
    )
    features["recent_cycle"] = features["unit_end_ts"] >= global_max - pd.Timedelta(days=5)
    features["unit_mode"] = features["submission_enabled"].map(
        {True: "submission-enabled", False: "practice-only"}
    )
    features["dominant_bug_type"] = features.apply(dominant_bug_type, axis=1)
    features["risk_segment"] = features.apply(choose_segment, axis=1)
    flagged = features[features["risk_segment"].notna()].copy()
    flagged["segment_label"] = flagged["risk_segment"].map(lambda key: SEGMENTS[key].label)
    flagged["owner_role"] = flagged["risk_segment"].map(lambda key: SEGMENTS[key].owner_role)
    flagged["target_window"] = flagged["risk_segment"].map(lambda key: SEGMENTS[key].target_window)
    flagged["goal"] = flagged["risk_segment"].map(lambda key: SEGMENTS[key].goal)
    flagged["recommended_intervention"] = flagged.apply(intervention_text, axis=1)
    flagged["evidence"] = flagged.apply(build_evidence, axis=1)
    flagged["priority_score"] = flagged.apply(priority_score, axis=1)
    flagged = flagged.sort_values(
        ["priority_score", "recent_cycle", "submission_enabled", "total_rows"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    flagged["priority_rank"] = flagged.index + 1

    detail_cols = [
        "priority_rank",
        "priority_score",
        "recent_cycle",
        "namespace",
        "learner_key",
        "unit_id",
        "unit_mode",
        "risk_segment",
        "segment_label",
        "dominant_bug_type",
        "goal",
        "evidence",
        "recommended_intervention",
        "owner_role",
        "target_window",
        "total_rows",
        "public_runs",
        "private_test_runs",
        "submissions",
        "best_public_pass_rate",
        "best_private_test_pass_rate",
        "public_all_pass_count",
        "public_green_hidden_fail_count",
        "runtime_count",
        "wrong_count",
        "tle_count",
        "large_data_count",
        "last_ts",
        "unit_end_ts",
        "days_before_unit_end",
    ]
    priority_detail = flagged[detail_cols].copy()

    learner_queue = (
        flagged.sort_values(["priority_score"], ascending=False)
        .groupby("learner_key", as_index=False)
        .agg(
            primary_unit=("unit_id", "first"),
            focus_units=("unit_id", lambda s: ", ".join(dict.fromkeys(s.head(3).astype(str)))),
            unit_mode=("unit_mode", "first"),
            risk_segment=("segment_label", "first"),
            dominant_bug_type=("dominant_bug_type", "first"),
            goal=("goal", "first"),
            evidence=("evidence", "first"),
            recommended_intervention=("recommended_intervention", "first"),
            owner_role=("owner_role", "first"),
            target_window=("target_window", "first"),
            priority_score=("priority_score", "first"),
            recent_cycle=("recent_cycle", "max"),
            flagged_units=("unit_id", "nunique"),
        )
    )
    learner_queue = learner_queue.sort_values(
        ["priority_score", "recent_cycle", "flagged_units"], ascending=[False, False, False]
    ).reset_index(drop=True)
    learner_queue["priority_rank"] = learner_queue.index + 1
    learner_queue = learner_queue[
        [
            "priority_rank",
            "priority_score",
            "recent_cycle",
            "learner_key",
            "focus_units",
            "primary_unit",
            "unit_mode",
            "risk_segment",
            "dominant_bug_type",
            "goal",
            "evidence",
            "recommended_intervention",
            "owner_role",
            "target_window",
            "flagged_units",
        ]
    ]

    ready_to_finish = flagged[flagged["risk_segment"] == "ready_to_finish"].copy()
    thrashers = flagged[
        flagged["risk_segment"].isin(["severe_thrashing", "moderate_thrashing"])
    ].copy()
    silent_dropout = flagged[flagged["risk_segment"] == "quiet_disengagement"].copy()

    bug_members = flagged[
        flagged["dominant_bug_type"] != "mixed_or_low_signal"
    ].copy()
    bug_roster_summary = (
        bug_members.groupby("dominant_bug_type", as_index=False)
        .agg(
            learner_unit_pairs=("learner_key", "size"),
            learners=("learner_key", "nunique"),
            median_public_runs=("public_runs", "median"),
            median_best_public_pass_rate=("best_public_pass_rate", "median"),
        )
        .sort_values("learner_unit_pairs", ascending=False)
        .reset_index(drop=True)
    )
    bug_roster_summary["recommended_clinic"] = bug_roster_summary["dominant_bug_type"].map(
        {
            "hidden_test_gap": "Edge-case / hidden-case clinic",
            "runtime_dominant": "Debugging clinic",
            "logic_or_edge_case_dominant": "Reasoning and boundary-case clinic",
            "pathological_output_or_nontermination": "Loop / print-discipline clinic",
            "near_success": "Submit-now nudge",
        }
    )

    unit_stats = unit_stats.copy()
    unit_stats["unit_end_ts"] = pd.to_datetime(unit_stats["unit_end_ts"], utc=True)
    unit_stats["submission_enabled"] = unit_stats["submission_enabled"].fillna(False)
    int_cols = [
        "submission_rows",
        "learners",
        "public_runs",
        "runtime_rows",
        "wrong_rows",
        "all_pass_rows",
        "tle_rows",
        "large_data_rows",
        "max_data_len",
        "paired_runs",
    ]
    for col in int_cols:
        unit_stats[col] = unit_stats[col].fillna(0).astype(int)
    rate_unit_cols = [
        "avg_public_pass_rate",
        "public_green_hidden_fail_rate",
        "public_all_pass_rate",
        "private_all_pass_rate",
        "avg_public_private_gap",
    ]
    for col in rate_unit_cols:
        unit_stats[col] = pd.to_numeric(unit_stats[col], errors="coerce")
    unit_stats["ta_focus"] = unit_stats.apply(ta_focus, axis=1)
    unit_stats["faculty_action"] = unit_stats.apply(faculty_action, axis=1)
    unit_stats["watchlist_reason"] = unit_stats.apply(
        lambda row: (
            "high hidden-test gap"
            if (row["public_green_hidden_fail_rate"] or 0) >= 0.05
            else "pathological output / TLE"
            if row["tle_rows"] > 0 or row["large_data_rows"] > 0
            else "dominant runtime failures"
            if row["runtime_rows"] > row["wrong_rows"]
            else "dominant wrong-answer failures"
        ),
        axis=1,
    )
    hidden_watchlist = unit_stats[
        (unit_stats["paired_runs"] >= 500)
        & (unit_stats["public_green_hidden_fail_rate"].fillna(0) >= 0.02)
    ].copy()
    hidden_watchlist = hidden_watchlist.sort_values(
        ["public_green_hidden_fail_rate", "paired_runs"], ascending=[False, False]
    )

    unit_support_notes = unit_stats[
        (
            (unit_stats["paired_runs"] >= 200)
            & (unit_stats["public_green_hidden_fail_rate"].fillna(0) >= 0.05)
        )
        | (unit_stats["tle_rows"] > 0)
        | (unit_stats["large_data_rows"] > 0)
        | (unit_stats["public_runs"] >= 500)
    ].copy()
    unit_support_notes["watchlist_score"] = (
        unit_support_notes["public_green_hidden_fail_rate"].fillna(0)
        * unit_support_notes["paired_runs"].clip(lower=1).map(math.log1p)
        + unit_support_notes["large_data_rows"].clip(upper=50) / 500
        + unit_support_notes["public_runs"].clip(upper=2000) / 40000
    )
    unit_support_notes = unit_support_notes.sort_values(
        ["watchlist_score", "public_runs"],
        ascending=[False, False],
    )

    cards = []
    for row in learner_queue.head(25).itertuples(index=False):
        cards.append(f"### Learner {row.learner_key}")
        cards.append(
            f"Primary focus unit: **{row.primary_unit}**. "
            f"Other flagged units: {row.focus_units}. "
            f"Segment: **{row.risk_segment}**. "
            f"Evidence: {row.evidence}. "
            f"Recommended action: {row.recommended_intervention}. "
            f"Owner: {row.owner_role}. Target window: {row.target_window}."
        )
        cards.append("")
    cards_md = "\n".join(cards).strip() + "\n"

    return {
        "priority_detail": priority_detail,
        "learner_queue": learner_queue,
        "ready_to_finish": ready_to_finish,
        "thrashers": thrashers,
        "silent_dropout": silent_dropout,
        "bug_members": bug_members,
        "bug_roster_summary": bug_roster_summary,
        "hidden_watchlist": hidden_watchlist,
        "unit_support_notes": unit_support_notes,
        "cards_md": cards_md,
    }


def write_outputs(outputs: dict[str, pd.DataFrame | str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(outputs["priority_detail"]).to_csv(
        OUT_DIR / "ta_priority_queue_unit_detail.csv", index=False
    )
    pd.DataFrame(outputs["learner_queue"]).to_csv(
        OUT_DIR / "ta_priority_queue.csv", index=False
    )
    pd.DataFrame(outputs["ready_to_finish"]).to_csv(
        OUT_DIR / "ready_to_finish.csv", index=False
    )
    pd.DataFrame(outputs["thrashers"]).to_csv(
        OUT_DIR / "thrashers.csv", index=False
    )
    pd.DataFrame(outputs["silent_dropout"]).to_csv(
        OUT_DIR / "silent_dropout.csv", index=False
    )
    pd.DataFrame(outputs["bug_members"]).to_csv(
        OUT_DIR / "bug_type_roster_members.csv", index=False
    )
    pd.DataFrame(outputs["bug_roster_summary"]).to_csv(
        OUT_DIR / "bug_type_roster_summary.csv", index=False
    )
    pd.DataFrame(outputs["hidden_watchlist"]).to_csv(
        OUT_DIR / "hidden_test_watchlist.csv", index=False
    )
    pd.DataFrame(outputs["unit_support_notes"]).to_csv(
        OUT_DIR / "unit_support_notes.csv", index=False
    )
    (OUT_DIR / "intervention_cards.md").write_text(
        str(outputs["cards_md"]), encoding="utf-8"
    )


def write_markdown(outputs: dict[str, pd.DataFrame | str], generated_at: str) -> None:
    priority_detail = pd.DataFrame(outputs["priority_detail"])
    learner_queue = pd.DataFrame(outputs["learner_queue"])
    ready_to_finish = pd.DataFrame(outputs["ready_to_finish"])
    thrashers = pd.DataFrame(outputs["thrashers"])
    silent_dropout = pd.DataFrame(outputs["silent_dropout"])
    bug_roster_summary = pd.DataFrame(outputs["bug_roster_summary"])
    hidden_watchlist = pd.DataFrame(outputs["hidden_watchlist"])
    unit_support_notes = pd.DataFrame(outputs["unit_support_notes"])

    segment_summary = (
        priority_detail.groupby("segment_label", as_index=False)
        .agg(
            learner_unit_pairs=("learner_key", "size"),
            learners=("learner_key", "nunique"),
            median_rows=("total_rows", "median"),
        )
        .sort_values("learner_unit_pairs", ascending=False)
    )

    output_rows = [
        [
            "`learning-support/ta_priority_queue.csv`",
            f"{len(learner_queue):,} learners",
            "TA or mentor",
            "Primary learner-level queue with focus units, evidence, action, and window.",
        ],
        [
            "`learning-support/ta_priority_queue_unit_detail.csv`",
            f"{len(priority_detail):,} learner-unit rows",
            "TA leads",
            "Detailed queue with unit context and support metrics.",
        ],
        [
            "`learning-support/ready_to_finish.csv`",
            f"{len(ready_to_finish):,} rows",
            "TA or mentor",
            "Submit-now nudge list. Only meaningful on submission-enabled units.",
        ],
        [
            "`learning-support/hidden_test_watchlist.csv`",
            f"{len(hidden_watchlist):,} units",
            "Faculty + TAs",
            "Units where public green is misleading and support should emphasize edge cases.",
        ],
        [
            "`learning-support/bug_type_roster_summary.csv`",
            f"{len(bug_roster_summary):,} bug groups",
            "TA coordinators",
            "Clinic roster summary for runtime, logic, hidden-gap, and loop/print problems.",
        ],
        [
            "`learning-support/thrashers.csv`",
            f"{len(thrashers):,} rows",
            "TAs",
            "Moderate/severe high-attempt learners who need forced reflection, not more attempts.",
        ],
        [
            "`learning-support/silent_dropout.csv`",
            f"{len(silent_dropout):,} rows",
            "Mentors",
            "Quiet disengagement cases for outreach.",
        ],
        [
            "`learning-support/unit_support_notes.csv`",
            f"{len(unit_support_notes):,} units",
            "Faculty + TAs",
            "TA focus and faculty follow-up by unit.",
        ],
        [
            "`learning-support/intervention_cards.md`",
            "25 cards",
            "TAs / buddies",
            "Short learner cards for the top-priority learners.",
        ],
    ]

    top_queue_rows = []
    for row in learner_queue.head(12).itertuples(index=False):
        top_queue_rows.append(
            [
                row.learner_key,
                row.focus_units,
                row.risk_segment,
                row.dominant_bug_type,
                row.owner_role,
                row.target_window,
            ]
        )

    hidden_rows = []
    for row in hidden_watchlist.head(10).itertuples(index=False):
        hidden_rows.append(
            [
                row.unit_id,
                fmt_int(row.paired_runs),
                pct(row.public_green_hidden_fail_rate, 1),
                pct(row.public_all_pass_rate, 1),
                pct(row.private_all_pass_rate, 1),
                row.ta_focus,
            ]
        )

    bug_rows = []
    for row in bug_roster_summary.itertuples(index=False):
        bug_rows.append(
            [
                row.dominant_bug_type,
                fmt_int(row.learner_unit_pairs),
                fmt_int(row.learners),
                fmt_int(row.median_public_runs),
                pct(row.median_best_public_pass_rate, 0),
                row.recommended_clinic,
            ]
        )

    segment_rows = []
    for row in segment_summary.itertuples(index=False):
        segment_rows.append(
            [row.segment_label, fmt_int(row.learner_unit_pairs), fmt_int(row.learners), fmt_int(row.median_rows)]
        )

    note_rows = []
    note_source = unit_support_notes[
        (unit_support_notes["paired_runs"] >= 500)
        | (unit_support_notes["public_runs"] >= 500)
    ]
    for row in note_source.head(10).itertuples(index=False):
        note_rows.append(
            [
                row.unit_id,
                "yes" if row.submission_enabled else "no",
                row.watchlist_reason,
                row.ta_focus,
                row.faculty_action,
            ]
        )

    lines = [
        "# Learning Support Pack",
        "",
        f"_Generated by `v2-analysis/generate_learning_support.py` on {generated_at}. Re-run this script whenever the parquet export changes._",
        "",
        "## Executive Summary",
        "",
        "- The right artifact here is a **named action list**, not a generic risk score. This pack turns learner-unit behavior into TA and faculty actions.",
        "- The biggest structural caveat is that **only Units 144-147 show any submission events** in this export. Submission-conversion outputs are meaningful only there. Everywhere else, treat the data as learning-practice evidence, not as a failure-to-submit signal.",
        f"- The queue is built around six support segments. The largest are **{segment_summary.iloc[0]['segment_label']}** ({fmt_int(segment_summary.iloc[0]['learner_unit_pairs'])} learner-unit rows) and **{segment_summary.iloc[1]['segment_label']}** ({fmt_int(segment_summary.iloc[1]['learner_unit_pairs'])} rows).",
        f"- The hidden-test trap is real: the watchlist is led by Unit **{hidden_watchlist.iloc[0]['unit_id']}** at **{pct(hidden_watchlist.iloc[0]['public_green_hidden_fail_rate'], 1)}** public-green / hidden-fail, followed by Units **{hidden_watchlist.iloc[1]['unit_id']}**, **{hidden_watchlist.iloc[2]['unit_id']}**, and **{hidden_watchlist.iloc[3]['unit_id']}**.",
        "- The minimal pack to share now is: `ta_priority_queue.csv`, `ready_to_finish.csv`, `hidden_test_watchlist.csv`, and `bug_type_roster_summary.csv`.",
        "",
        "## What To Share",
        "",
        md_table(["output", "size", "owner", "why it matters"], output_rows),
        "",
        "## First-Read Cautions",
        "",
        "- Do **not** treat every non-submission as operational failure. Units without any cohort-wide submission events are practice-only in this extract.",
        "- Use learner-level queues for action, but use unit watchlists to avoid blaming students for public/private test-gap effects.",
        "- Queue rows include `recent_cycle = true` when the unit closed in the last five days of the export. That is the first filter to use if you want a current-ish TA list.",
        "",
        "## TA Priority Queue",
        "",
        "The queue is organized around supportable patterns, not stigma labels.",
        "",
        md_table(
            ["segment", "learner-unit rows", "learners", "median rows/pair"],
            segment_rows,
        ),
        "",
        "Top learner-level queue rows:",
        "",
        md_table(
            ["learner_key", "focus_units", "risk_segment", "bug_type", "owner", "window"],
            top_queue_rows,
        ),
        "",
        "Use the queue this way:",
        "",
        "1. `recent_cycle = true` and `target_window = same day`: submit-now nudges.",
        "2. `false_confidence_hidden_gap`: 15-minute boundary-case review before the next attempt burst.",
        "3. `severe_thrashing` or `moderate_thrashing`: live debugging or reasoning clinic, depending on bug type.",
        "4. `quiet_disengagement`: outreach by mentor or buddy, not a technical clinic.",
        "",
        "## Ready-To-Finish List",
        "",
        f"There are **{fmt_int(len(ready_to_finish))}** ready-to-finish learner-unit rows. This list is restricted by the segment logic to **submission-enabled units only** and requires strong recent evidence, not just one lucky run.",
        "",
        "Why this matters: these learners do not look conceptually blocked. They look operationally stuck. This is a high-ROI nudge list, not a reteaching list.",
        "",
        "## Hidden-Test Trap Watchlist",
        "",
        "These are the units where public green is most likely to create false confidence. TA support should emphasize boundary cases and self-authored hidden tests.",
        "",
        md_table(
            [
                "unit_id",
                "paired runs",
                "public green / hidden fail",
                "public all-pass",
                "private all-pass",
                "TA focus",
            ],
            hidden_rows,
        ),
        "",
        "Faculty guidance: on these units, student struggle is not just lack of practice. It is partly a test-gap and edge-case problem. Update TA briefing notes accordingly.",
        "",
        "## Bug-Type Rosters",
        "",
        "This is the clinic-planning view. Instead of “weak students,” route by likely failure mode.",
        "",
        md_table(
            [
                "bug_type",
                "learner-unit rows",
                "learners",
                "median public runs",
                "median best public pass-rate",
                "recommended clinic",
            ],
            bug_rows,
        ),
        "",
        "Use `learning-support/bug_type_roster_members.csv` to pull named learner-unit rows into each clinic.",
        "",
        "## Thrashers and Quiet Disengagement",
        "",
        f"- `learning-support/thrashers.csv` has **{fmt_int(len(thrashers))}** rows. These learners are over-attempting without learning transfer and need forced reflection between runs.",
        f"- `learning-support/silent_dropout.csv` has **{fmt_int(len(silent_dropout))}** rows. These learners are failing quietly and need outreach, not more analytics.",
        "",
        "## Unit Support Notes",
        "",
        md_table(
            ["unit_id", "submission enabled", "watchlist reason", "TA focus", "faculty follow-up"],
            note_rows,
        ),
        "",
        "## Recommended Operating Cadence",
        "",
        "1. Start every day with `ready_to_finish.csv` and `ta_priority_queue.csv` filtered to `recent_cycle = true`.",
        "2. Pull same-day nudges first, then edge-case reviews, then debugging/reasoning clinics.",
        "3. Use `bug_type_roster_summary.csv` to decide which clinic blocks to schedule that week.",
        "4. Review `hidden_test_watchlist.csv` and `unit_support_notes.csv` with faculty before briefing TAs.",
        "5. Use `intervention_cards.md` for one-paragraph TA/buddy handoffs instead of dashboard screenshots.",
        "",
        "## Thresholds Used",
        "",
        "- Severe thrashing: more than 54 rows on a learner-unit pair and best public pass-rate still below 80%.",
        "- Moderate thrashing: more than 21 rows and best public pass-rate still below 80%.",
        "- No traction: at least 5 public runs and best public pass-rate at or below 20%.",
        "- Quiet disengagement: at most 8 public runs, best public pass-rate below 50%, and the learner stops at least 2 days before the unit’s observed close.",
        "- Ready to finish: submission-enabled unit, no submission, recent activity near unit close, and either hidden-test perfection or repeated high public performance without a hidden-gap signal.",
        "- False confidence / hidden-test risk: at least one public-green / hidden-fail paired run and no evidence of full hidden-test success.",
        "",
        "## Rebuild",
        "",
        "```bash",
        "uv run v2-analysis/generate_learning_support.py",
        "```",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    build_views(con)
    features = query_df(con, FEATURES_SQL)
    unit_stats = query_df(con, UNIT_STATS_SQL)
    outputs = build_outputs(features, unit_stats)
    write_outputs(outputs)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    write_markdown(outputs, generated_at)
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
