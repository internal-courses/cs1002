#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy>=2.1.0",
#   "pandas>=2.2.0",
# ]
# ///
"""Evaluate the repeater buddy program using existing OPPE analysis evidence.

Outputs:
- analysis/buddy_program_evaluation.csv
- analysis/buddy_program_evaluation_recommendations.csv
- analysis/buddy_program_evaluation.md
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"

# Program details provided by user.
PROGRAM_COHORT_SIZE = 2233
BUDDY_STUDENT_RATIO = 60
WEEK1_ATTENDANCE_RATE = 0.30
ATTENDANCE_REQUIREMENT = 0.75

OUT_METRICS = ANALYSIS / "buddy_program_evaluation.csv"
OUT_RECS = ANALYSIS / "buddy_program_evaluation_recommendations.csv"
OUT_MD = ANALYSIS / "buddy_program_evaluation.md"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def split_concepts(series: pd.Series) -> pd.Series:
    exploded = (
        series.fillna("")
        .astype(str)
        .str.split(";")
        .explode()
        .astype(str)
        .str.strip()
    )
    return exploded[exploded.ne("")]


def pct(x: float) -> float:
    return round(100.0 * x, 2)


def maybe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    st_arche = read_csv(ANALYSIS / "longitudinal_analysis" / "student_term_primary_archetype.csv")
    teachable = read_csv(ANALYSIS / "teachable.csv")
    state_traj = read_csv(ANALYSIS / "longitudinal_analysis" / "all_three_term_state_trajectory_summary.csv")
    all_three = read_csv(ANALYSIS / "longitudinal_analysis" / "all_three_term_trajectories.csv")
    inc_thr = read_csv(ANALYSIS / "evaluation_redesign" / "archetype_incremental_vs_thrasher_comparison.csv")
    s2 = read_csv(ANALYSIS / "evaluation_redesign" / "s2_bottleneck_summary.csv")
    sub_capture = read_csv(ANALYSIS / "evaluation_redesign" / "submission_capture_overall_summary.csv")
    concept_ret = read_csv(ANALYSIS / "concept_knowledge_modeling" / "repeat_student_concept_retention_acquisition_summary.csv")
    thr_lang = None
    thr_lang_path = ANALYSIS / "thrashers_language_tests.csv"
    if thr_lang_path.exists():
        thr_lang = read_csv(thr_lang_path)

    # Repeater definitions from existing longitudinal analysis.
    terms_per_student = st_arche.groupby("student_id", as_index=False)["term"].nunique().rename(columns={"term": "terms"})
    repeaters_ge2 = terms_per_student.loc[terms_per_student["terms"] >= 2, "student_id"]
    repeaters_ge3 = terms_per_student.loc[terms_per_student["terms"] >= 3, "student_id"]
    rep_set = set(repeaters_ge2.tolist())

    rep_teach = teachable[teachable["student_id"].isin(rep_set)].copy()
    rep_teach["teachable_now"] = rep_teach["teachable_now"].astype(str).str.lower().isin({"true", "1", "yes"})
    teachable_rep_students = rep_teach.loc[rep_teach["teachable_now"], "student_id"].nunique()

    path_counts = (
        rep_teach["decision_path_id"]
        .value_counts(dropna=False)
        .rename_axis("decision_path_id")
        .reset_index(name="profiles")
    )
    path_name = rep_teach[["decision_path_id", "decision_path_name"]].drop_duplicates()
    path_counts = path_counts.merge(path_name, on="decision_path_id", how="left")
    path_counts["profile_share"] = path_counts["profiles"] / path_counts["profiles"].sum()
    path_counts["estimated_students_in_2233"] = (path_counts["profile_share"] * PROGRAM_COHORT_SIZE).round().astype(int)

    teach_tracks = (
        rep_teach.loc[rep_teach["teachable_now"], "intervention_track"]
        .value_counts(dropna=False)
        .rename_axis("intervention_track")
        .reset_index(name="profiles")
    )
    teach_tracks["share_of_teachable_profiles"] = teach_tracks["profiles"] / max(1, int(teach_tracks["profiles"].sum()))
    teach_tracks["estimated_students_in_2233"] = (
        teach_tracks["share_of_teachable_profiles"] * (PROGRAM_COHORT_SIZE * (teachable_rep_students / max(1, len(rep_set))))
    ).round().astype(int)

    concept_mentions = split_concepts(rep_teach.loc[rep_teach["teachable_now"], "top_concept_struggles"])
    concept_top = concept_mentions.value_counts().reset_index()
    concept_top.columns = ["concept", "mentions"]

    # Weighted acquisition rates across repeat-term transitions.
    c = concept_ret.copy()
    for col in ["source_not_mastered_students", "newly_mastered_students"]:
        c[col] = pd.to_numeric(c[col], errors="coerce").fillna(0.0)
    concept_acq = (
        c.groupby("concept", as_index=False)
        .agg(
            source_not_mastered_students=("source_not_mastered_students", "sum"),
            newly_mastered_students=("newly_mastered_students", "sum"),
        )
    )
    concept_acq["acquisition_rate_pct_weighted"] = np.where(
        concept_acq["source_not_mastered_students"] > 0,
        100.0 * concept_acq["newly_mastered_students"] / concept_acq["source_not_mastered_students"],
        np.nan,
    )
    hardest_concepts = concept_acq.sort_values("acquisition_rate_pct_weighted").head(5)

    # All-three cohort state signal.
    state_traj["students"] = pd.to_numeric(state_traj["students"], errors="coerce").fillna(0).astype(int)
    all_three_n = int(len(all_three))
    starts_fund = state_traj.loc[
        state_traj["state_trajectory"].astype(str).str.startswith(
            ("S0_no_code", "S1_syntax_fundamental", "S1b_syntax_structure")
        ),
        "students",
    ].sum()
    top_state_row = state_traj.sort_values("students", ascending=False).iloc[0]

    # Process efficiency signal: incremental debugger vs thrasher.
    row_inc = inc_thr.loc[inc_thr["archetype"] == "Incremental debugger"].iloc[0]
    row_thr = inc_thr.loc[inc_thr["archetype"] == "Thrasher"].iloc[0]

    # S2 bottleneck.
    s2_row = s2.iloc[0]

    # Submission capture confound.
    sub_row = sub_capture.iloc[0]

    # Attendance/capacity scenario from program details.
    buddies_needed = math.ceil(PROGRAM_COHORT_SIZE / BUDDY_STUDENT_RATIO)
    students_per_buddy = PROGRAM_COHORT_SIZE / buddies_needed
    week1_attendees = round(PROGRAM_COHORT_SIZE * WEEK1_ATTENDANCE_RATE)
    attendance_gap_pp = 100.0 * (ATTENDANCE_REQUIREMENT - WEEK1_ATTENDANCE_RATE)

    # High-touch estimate by segment share.
    high_touch_share = float(
        path_counts.loc[path_counts["decision_path_id"].isin(["D1", "D3"]), "profile_share"].sum()
    )
    high_touch_students_est = round(PROGRAM_COHORT_SIZE * high_touch_share)
    reengage_share = float(path_counts.loc[path_counts["decision_path_id"].eq("D0"), "profile_share"].sum())
    reengage_students_est = round(PROGRAM_COHORT_SIZE * reengage_share)

    metrics: list[dict[str, Any]] = []
    add = metrics.append

    add(
        {
            "domain": "Cohort",
            "metric_id": "repeaters_ge2_students",
            "metric": "Students seen in >=2 terms",
            "value": len(rep_set),
            "unit": "students",
            "source_file": "analysis/longitudinal_analysis/student_term_primary_archetype.csv",
            "implication": "Large repeater pool is heterogeneous; one-size mentoring is risky.",
        }
    )
    add(
        {
            "domain": "Cohort",
            "metric_id": "repeaters_ge3_students",
            "metric": "Students seen in all 3 terms (from student-term table)",
            "value": len(set(repeaters_ge3.tolist())),
            "unit": "students",
            "source_file": "analysis/longitudinal_analysis/student_term_primary_archetype.csv",
            "implication": "Persistent subgroup exists and likely needs foundational remediation.",
        }
    )
    add(
        {
            "domain": "Cohort",
            "metric_id": "all_three_substantive_students",
            "metric": "All-three substantive trajectory cohort",
            "value": all_three_n,
            "unit": "students",
            "source_file": "analysis/longitudinal_analysis/all_three_term_trajectories.csv",
            "implication": "This is the highest-need persistent cohort for specialized support.",
        }
    )
    add(
        {
            "domain": "State Trajectory",
            "metric_id": "all_three_starts_syntax_or_no_code_pct",
            "metric": "All-three cohort starting in S0/S1/S1b",
            "value": round(100.0 * starts_fund / max(1, all_three_n), 2),
            "unit": "pct",
            "source_file": "analysis/longitudinal_analysis/all_three_term_state_trajectory_summary.csv",
            "implication": "Persistent repeaters are mostly foundational syntax/no-code, not advanced logic-only.",
        }
    )
    add(
        {
            "domain": "State Trajectory",
            "metric_id": "top_all_three_state_trajectory_share_pct",
            "metric": f"Top all-three state trajectory share ({top_state_row['state_trajectory']})",
            "value": round(100.0 * int(top_state_row["students"]) / max(1, all_three_n), 2),
            "unit": "pct",
            "source_file": "analysis/longitudinal_analysis/all_three_term_state_trajectory_summary.csv",
            "implication": "A large subgroup repeatedly fails at parsing/code construction basics.",
        }
    )
    add(
        {
            "domain": "Segmentation",
            "metric_id": "repeaters_teachable_any_pct",
            "metric": "Repeaters with >=1 teachable-now profile",
            "value": round(100.0 * teachable_rep_students / max(1, len(rep_set)), 2),
            "unit": "pct",
            "source_file": "analysis/teachable.csv + analysis/longitudinal_analysis/student_term_primary_archetype.csv",
            "implication": "Only a minority is immediately teachable under standard mentoring.",
        }
    )
    add(
        {
            "domain": "Segmentation",
            "metric_id": "repeaters_path_d1_profile_pct",
            "metric": "Repeater profiles in D1 (severe stuck/chaotic)",
            "value": round(100.0 * float(path_counts.loc[path_counts["decision_path_id"].eq("D1"), "profile_share"].sum()), 2),
            "unit": "pct_profiles",
            "source_file": "analysis/teachable.csv",
            "implication": "Needs high-touch protocol; not suitable for light group mentoring alone.",
        }
    )
    add(
        {
            "domain": "Segmentation",
            "metric_id": "repeaters_path_d3_profile_pct",
            "metric": "Repeater profiles in D3 (mixed/diffuse)",
            "value": round(100.0 * float(path_counts.loc[path_counts["decision_path_id"].eq("D3"), "profile_share"].sum()), 2),
            "unit": "pct_profiles",
            "source_file": "analysis/teachable.csv",
            "implication": "Needs rapid diagnostic triage before generic practice sessions.",
        }
    )
    add(
        {
            "domain": "Process",
            "metric_id": "thrasher_vs_incremental_success_gap_pp",
            "metric": "Thrasher minus Incremental success-rate gap",
            "value": round(maybe_float(row_thr["success_rate_gap_vs_incremental_pp"]), 2),
            "unit": "pp",
            "source_file": "analysis/evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv",
            "implication": "Process quality matters more than raw effort; mentors must coach process explicitly.",
        }
    )
    add(
        {
            "domain": "Process",
            "metric_id": "thrasher_vs_incremental_time_ratio",
            "metric": "Thrasher vs Incremental median active-time ratio",
            "value": round(maybe_float(row_thr["time_ratio_vs_incremental"]), 2),
            "unit": "x",
            "source_file": "analysis/evaluation_redesign/archetype_incremental_vs_thrasher_comparison.csv",
            "implication": "Without process correction, students can spend much longer for worse outcomes.",
        }
    )
    add(
        {
            "domain": "Bottleneck",
            "metric_id": "s2_share_public_runs_pct",
            "metric": "Public run rows in S2 (parseable but 0 pass)",
            "value": round(maybe_float(s2_row["pct_all_public_runs"]), 2),
            "unit": "pct",
            "source_file": "analysis/evaluation_redesign/s2_bottleneck_summary.csv",
            "implication": "S2 is the main debugging loop where buddy sessions should focus.",
        }
    )
    add(
        {
            "domain": "Bottleneck",
            "metric_id": "s2_self_loop_pct",
            "metric": "S2 self-loop transition rate",
            "value": round(maybe_float(s2_row["pct_self_loop"]), 2),
            "unit": "pct",
            "source_file": "analysis/evaluation_redesign/s2_bottleneck_summary.csv",
            "implication": "Students repeat ineffective moves; mentors need hypothesis-run-fix protocol.",
        }
    )
    add(
        {
            "domain": "Data Quality",
            "metric_id": "zero_submission_namespaces",
            "metric": "Namespaces with zero captured submissions",
            "value": int(sub_row["zero_submission_namespaces"]),
            "unit": "count",
            "source_file": "analysis/evaluation_redesign/submission_capture_overall_summary.csv",
            "implication": "Submission metrics can be confounded; avoid judging students solely on private submit behavior.",
        }
    )
    add(
        {
            "domain": "Data Quality",
            "metric_id": "track_b_rows",
            "metric": "Track B rows (zero-submission namespaces)",
            "value": int(sub_row["track_b_rows"]),
            "unit": "rows",
            "source_file": "analysis/evaluation_redesign/submission_capture_overall_summary.csv",
            "implication": "Mentor dashboards need explicit flags for capture-limited namespaces.",
        }
    )
    add(
        {
            "domain": "Concepts",
            "metric_id": "hardest_concept_acquisition_min_pct",
            "metric": f"Lowest weighted acquisition concept ({hardest_concepts.iloc[0]['concept']})",
            "value": round(float(hardest_concepts.iloc[0]["acquisition_rate_pct_weighted"]), 2),
            "unit": "pct",
            "source_file": "analysis/concept_knowledge_modeling/repeat_student_concept_retention_acquisition_summary.csv",
            "implication": "Buddy content should prioritize low-acquisition concepts, not random practice.",
        }
    )
    add(
        {
            "domain": "Capacity",
            "metric_id": "program_buddies_needed_at_1_to_60",
            "metric": "Buddies required for 2233 students at 1:60",
            "value": buddies_needed,
            "unit": "buddies",
            "source_file": "Program details (user-provided)",
            "implication": "At least this many buddies are needed; quality depends on session design and triage.",
        }
    )
    add(
        {
            "domain": "Capacity",
            "metric_id": "program_week1_attendance_pct",
            "metric": "Week-1 attendance",
            "value": round(100.0 * WEEK1_ATTENDANCE_RATE, 2),
            "unit": "pct",
            "source_file": "Program details (user-provided)",
            "implication": "Current engagement is far below mandatory threshold; compliance-first behavior risk is high.",
        }
    )
    add(
        {
            "domain": "Capacity",
            "metric_id": "program_attendance_gap_to_requirement_pp",
            "metric": "Gap between week-1 attendance and 75% requirement",
            "value": round(attendance_gap_pp, 2),
            "unit": "pp",
            "source_file": "Program details (user-provided)",
            "implication": "Need activation interventions before content mentoring can work at scale.",
        }
    )
    add(
        {
            "domain": "Capacity",
            "metric_id": "program_est_high_touch_students_2233",
            "metric": "Estimated high-touch students in 2233 cohort (D1+D3 share)",
            "value": high_touch_students_est,
            "unit": "students_est",
            "source_file": "analysis/teachable.csv + Program details",
            "implication": "A large subgroup likely needs triage/1:1 bursts beyond normal buddy sessions.",
        }
    )
    add(
        {
            "domain": "Capacity",
            "metric_id": "program_est_reengagement_students_2233",
            "metric": "Estimated re-engagement-first students in 2233 cohort (D0 share)",
            "value": reengage_students_est,
            "unit": "students_est",
            "source_file": "analysis/teachable.csv + Program details",
            "implication": "Engagement contract needs its own track, separate from coding remediation.",
        }
    )

    if thr_lang is not None and not thr_lang.empty:
        row = thr_lang.loc[thr_lang["test_name"] == "wls_beta_load_adjusted_for_technical_difficulty"]
        if not row.empty:
            add(
                {
                    "domain": "Language Hypothesis",
                    "metric_id": "prompt_language_load_p_value",
                    "metric": "Prompt language-load adjusted association p-value",
                    "value": round(float(row.iloc[0]["p_value"]), 4),
                    "unit": "p_value",
                    "source_file": "analysis/thrashers_language_tests.csv",
                    "implication": "No strong evidence that language complexity alone explains thrashing; focus on process+concept support.",
                }
            )

    metrics_df = pd.DataFrame(metrics)

    # Recommendations table.
    recs = [
        {
            "priority": "P0",
            "recommendation": "Replace one-size buddying with triage tracks (D0/D1/D3/T1/T2/T3).",
            "why": "Repeater profiles are heterogeneous; high-touch vs teachable segments need different intervention intensity.",
            "evidence_metric_ids": "repeaters_path_d1_profile_pct;repeaters_path_d3_profile_pct;repeaters_teachable_any_pct",
            "kpi": "% students assigned to correct track within first 2 weeks",
            "target": ">=90%",
        },
        {
            "priority": "P0",
            "recommendation": "Add 30-45 minute diagnostic sprint for D3 before regular sessions.",
            "why": "Mixed/diffuse students need diagnosis first; generic practice wastes mentor time.",
            "evidence_metric_ids": "program_est_high_touch_students_2233;repeaters_path_d3_profile_pct",
            "kpi": "D3 -> T1/T2/T3 conversion by week 3",
            "target": ">=50%",
        },
        {
            "priority": "P0",
            "recommendation": "Teach process protocol explicitly: predict -> run -> trace -> fix.",
            "why": "Thrashing costs 2.25x time with much lower success; process quality is the lever.",
            "evidence_metric_ids": "thrasher_vs_incremental_time_ratio;thrasher_vs_incremental_success_gap_pp;s2_self_loop_pct",
            "kpi": "S2 self-loop rate among mentored students",
            "target": "drop by >=15% in 4 weeks",
        },
        {
            "priority": "P0",
            "recommendation": "Create a foundational syntax bootcamp track for persistent all-three cohort.",
            "why": "Persistent cohort is overwhelmingly syntax/no-code; advanced debugging clinics miss the root need.",
            "evidence_metric_ids": "all_three_starts_syntax_or_no_code_pct;top_all_three_state_trajectory_share_pct",
            "kpi": "Parseable-fraction uplift in bootcamp students",
            "target": ">=+0.20 in 4 weeks",
        },
        {
            "priority": "P1",
            "recommendation": "Use concept-first weekly plans: arithmetic/IO/loops/data-aggregation first.",
            "why": "These concepts dominate teachable struggler signals; low-acquisition concepts need deliberate practice.",
            "evidence_metric_ids": "hardest_concept_acquisition_min_pct",
            "kpi": "Concept acquisition rate for targeted concepts",
            "target": ">=+10 pp term-over-term",
        },
        {
            "priority": "P1",
            "recommendation": "Separate engagement enforcement from learning support.",
            "why": "30% early attendance vs 75% requirement risks attendance theater and low-trust interactions.",
            "evidence_metric_ids": "program_week1_attendance_pct;program_attendance_gap_to_requirement_pp",
            "kpi": "Meaningful participation rate (>=2 runs + >=2 edits/week)",
            "target": ">=70%",
        },
        {
            "priority": "P1",
            "recommendation": "Instrument buddy quality: session checklist + random audit + outcomes dashboard.",
            "why": "At ~38 buddies, mentor quality variance can dominate outcomes.",
            "evidence_metric_ids": "program_buddies_needed_at_1_to_60",
            "kpi": "Buddy fidelity score (protocol adherence)",
            "target": ">=85%",
        },
        {
            "priority": "P1",
            "recommendation": "Do not evaluate students using raw private-submission counts alone.",
            "why": "Submission capture gaps create false negatives in many namespaces.",
            "evidence_metric_ids": "zero_submission_namespaces;track_b_rows",
            "kpi": "Dashboards with capture-status flag enabled",
            "target": "100%",
        },
    ]
    recs_df = pd.DataFrame(recs)

    # Persist supporting segment breakdown as separate block in main CSV.
    segment_rows = path_counts[["decision_path_id", "decision_path_name", "profiles", "profile_share", "estimated_students_in_2233"]].copy()
    segment_rows["domain"] = "Segment Estimate"
    segment_rows["metric_id"] = "segment_" + segment_rows["decision_path_id"].astype(str).str.lower() + "_share_pct"
    segment_rows["metric"] = "Segment share (" + segment_rows["decision_path_name"].astype(str) + ")"
    segment_rows["value"] = (100.0 * segment_rows["profile_share"]).round(2)
    segment_rows["unit"] = "pct_profiles"
    segment_rows["source_file"] = "analysis/teachable.csv"
    segment_rows["implication"] = (
        "Estimated in-program students: " + segment_rows["estimated_students_in_2233"].astype(str) + " out of 2233"
    )
    segment_metrics = segment_rows[
        ["domain", "metric_id", "metric", "value", "unit", "source_file", "implication"]
    ]
    metrics_df = pd.concat([metrics_df, segment_metrics], ignore_index=True)

    return metrics_df, recs_df


def render_markdown(metrics_df: pd.DataFrame, recs_df: pd.DataFrame) -> str:
    m = metrics_df.set_index("metric_id")

    def mv(metric_id: str, default: str = "NA") -> str:
        if metric_id not in m.index:
            return default
        v = m.loc[metric_id, "value"]
        if isinstance(v, pd.Series):
            v = v.iloc[0]
        if pd.isna(v):
            return default
        if float(v).is_integer():
            return f"{int(v):,}"
        return f"{float(v):.2f}"

    repeaters_ge2 = mv("repeaters_ge2_students")
    all_three = mv("all_three_substantive_students")
    syntax_pct = mv("all_three_starts_syntax_or_no_code_pct")
    teachable_pct = mv("repeaters_teachable_any_pct")
    s2_pct = mv("s2_share_public_runs_pct")
    s2_loop = mv("s2_self_loop_pct")
    thr_gap = mv("thrasher_vs_incremental_success_gap_pp")
    thr_time = mv("thrasher_vs_incremental_time_ratio")
    week1_att = mv("program_week1_attendance_pct")
    att_gap = mv("program_attendance_gap_to_requirement_pp")
    buddies = mv("program_buddies_needed_at_1_to_60")
    high_touch_est = mv("program_est_high_touch_students_2233")
    reengage_est = mv("program_est_reengagement_students_2233")
    hard_acq = mv("hardest_concept_acquisition_min_pct")
    capture_zero = mv("zero_submission_namespaces")
    lang_p = mv("prompt_language_load_p_value", default="NA")
    try:
        thr_gap_abs = abs(float(thr_gap.replace(",", "")))
    except Exception:
        thr_gap_abs = math.nan

    lines: list[str] = []
    lines.append("# Buddy Program Evaluation (ELI15 Version)")
    lines.append("")
    lines.append("## One-Minute Summary")
    lines.append("")
    lines.append(
        "The buddy program is a good idea and should continue. "
        "But right now, too many very different students are being treated the same way. "
        "That is why progress is uneven."
    )
    lines.append("")
    lines.append(
        f"We analyzed `{repeaters_ge2}` repeaters. Only about `{teachable_pct}%` are ready for standard mentoring immediately. "
        "Many others first need either re-engagement support, a quick diagnosis, or high-touch help."
    )
    lines.append("")
    lines.append("## Quick Glossary (Plain English)")
    lines.append("")
    lines.append("- **Repeater:** A student who appears in the exam data across multiple terms.")
    lines.append("- **Thrashing / Thrasher:** A student keeps making many changes and test runs, but without a clear debugging plan.")
    lines.append("- **Success gap:** Difference in pass rate between two groups.")
    lines.append("- **Self-loop rate:** How often students stay stuck in the same state instead of moving forward.")
    lines.append("- **S2 state:** Code runs, but passes **zero** tests. This is a major “stuck zone.”")
    lines.append("")
    lines.append("## Simple Examples")
    lines.append("")
    lines.append("1. **Thrashing example**")
    lines.append(
        "Student A runs tests again and again, makes random edits, and still does not improve. "
        "Student B makes a hypothesis, tests one change, checks result, then makes the next change. "
        "Student B usually succeeds faster."
    )
    lines.append(
        f"In our data, the thrashing group spends about `{thr_time}x` more time "
        f"and has about `{thr_gap_abs:.2f} percentage points` lower success."
    )
    lines.append("")
    lines.append("2. **Self-loop example**")
    lines.append(
        "Imagine a student is stuck where code runs but no tests pass. They keep trying similar edits and stay stuck."
    )
    lines.append(
        f"In our data, this stuck state (S2) appears in `{s2_pct}%` of public runs, and `{s2_loop}%` of S2 transitions stay in S2."
    )
    lines.append("")
    lines.append("## What Is Good in the Current Program")
    lines.append("")
    lines.append("1. Peer buddies are a strong support model.")
    lines.append("2. Weekly sessions are the right rhythm.")
    lines.append("3. Progress tracking is already part of the plan.")
    lines.append("")
    lines.append("## What Must Be Improved")
    lines.append("")
    lines.append(
        "1. **Do not use one style for everyone.** Students are different and need different support tracks."
    )
    lines.append(
        f"2. **Add explicit debugging method training.** Right now, many students are stuck in high-effort, low-learning loops."
    )
    lines.append(
        f"3. **Treat the all-three-term persistent group as foundational learners.** In that group (`{all_three}` students), `{syntax_pct}%` begin in syntax/no-code states."
    )
    lines.append(
        f"4. **Fix engagement design.** Week-1 attendance was `{week1_att}%`, which is `{att_gap} percentage points` below requirement."
    )
    lines.append(
        f"5. **Use caution with submission counts.** `{capture_zero}` namespaces have zero captured submissions, so raw submit counts can be misleading."
    )
    lines.append("")
    lines.append("## What Is Missing and Should Be Added")
    lines.append("")
    lines.append("1. **Week-0 triage**: quickly classify students before regular sessions.")
    lines.append("2. **Track-specific playbooks** for syntax, runtime debugging, and logic/edge cases.")
    lines.append("3. **High-touch lane** for severe stuck and diffuse-pattern students.")
    lines.append("4. **Meaningful participation KPI**: at least 2 test runs + 2 real edits per week.")
    lines.append("5. **Buddy quality checks**: simple checklist + periodic review.")
    lines.append(
        f"6. **Concept-priority plan** for hardest concepts (lowest weighted acquisition observed: `{hard_acq}%`)."
    )
    if lang_p != "NA":
        lines.append(
            f"7. **Do not over-focus on question language complexity alone** (p-value `{lang_p}`: not strong evidence by itself)."
        )
    lines.append("")
    lines.append("## Capacity Reality (For 2233 Students)")
    lines.append("")
    lines.append(f"- At 1:60, you need about **{buddies} buddies**.")
    lines.append(f"- Estimated students needing high-touch support: **~{high_touch_est}**.")
    lines.append(f"- Estimated students needing re-engagement-first support: **~{reengage_est}**.")
    lines.append("")
    lines.append("## Practical 4–6 Week Plan")
    lines.append("")
    lines.append("1. Week 0-1: triage all students and assign tracks.")
    lines.append("2. Week 1-2: run diagnostic sprints for mixed/diffuse students.")
    lines.append("3. Week 2-4: teach debugging protocol in every session.")
    lines.append("4. Week 2-6: run syntax bootcamp for persistent foundational subgroup.")
    lines.append("5. Every week: measure meaningful participation, not just attendance.")
    lines.append("")
    lines.append("## Recommended Actions Table")
    lines.append("")
    # Lightweight markdown table renderer to avoid optional tabulate dependency.
    cols = list(recs_df.columns)
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for row in recs_df.itertuples(index=False):
        vals = [str(getattr(row, c)) for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## Evidence Files")
    lines.append("")
    lines.append("- `analysis/buddy_program_evaluation.csv`")
    lines.append("- `analysis/buddy_program_evaluation_recommendations.csv`")
    lines.append("- Source files referenced in the `source_file` column of the metrics CSV.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    metrics_df, recs_df = build()
    metrics_df.to_csv(OUT_METRICS, index=False)
    recs_df.to_csv(OUT_RECS, index=False)
    OUT_MD.write_text(render_markdown(metrics_df, recs_df), encoding="utf-8")
    print(f"Wrote: {OUT_METRICS}")
    print(f"Wrote: {OUT_RECS}")
    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
