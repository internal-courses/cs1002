#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
# ]
# ///
"""Process-first "Teachable 10%" identification after OPPE-1.

This script intentionally avoids score-based or historical-improvement-based
selection. It uses only:
- engagement signals (runs, edits, persistence patterns),
- error-pattern structure (syntax/runtime/logic signatures),
- concept-struggle structure (failed concept profiles).

Outputs:
- analysis/teachable.csv
- analysis/teachable.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"


# We require enough evidence to classify a student reliably.
MIN_ATTEMPT_ROWS = 3


@dataclass(frozen=True)
class Paths:
    process_features: Path = ANALYSIS_DIR / "process_analysis" / "attempt_process_features_with_patterns.csv"
    wave_error_profile: Path = ANALYSIS_DIR / "longitudinal_analysis" / "student_wave_primary_error_profile.csv"
    concept_wave_summary: Path = ANALYSIS_DIR / "concept_knowledge_modeling" / "student_concept_wave_summary.csv"

    out_csv: Path = ANALYSIS_DIR / "teachable.csv"
    out_md: Path = ANALYSIS_DIR / "teachable.md"


PATHS = Paths()


PATH_METADATA: dict[str, dict[str, Any]] = {
    "D0": {
        "name": "Low Engagement / One-Shot Usage",
        "teachable_now": False,
        "intervention_track": "Re-engagement before content remediation",
        "intervention_plan": (
            "Contact quickly, resolve access/friction, set minimum process contract "
            "(>=2 runs + >=2 code edits per problem), then reassess."
        ),
    },
    "D1": {
        "name": "Severe Stuck / Chaotic Looping",
        "teachable_now": False,
        "intervention_track": "High-touch diagnostic coaching",
        "intervention_plan": (
            "Short 1:1 debugging coaching with strict protocol: predict -> run -> trace -> fix. "
            "Limit random edits, require explicit hypotheses."
        ),
    },
    "D2": {
        "name": "Already Stable (Low Immediate Need)",
        "teachable_now": False,
        "intervention_track": "Light monitoring / enrichment",
        "intervention_plan": (
            "Not priority for intensive support now. Provide stretch tasks and monitor for regression."
        ),
    },
    "T1": {
        "name": "Teachable: Syntax Foundations",
        "teachable_now": True,
        "intervention_track": "Syntax repair + scaffolded patterns",
        "intervention_plan": (
            "Use subgoal-labeled templates for function/loop/if structure, "
            "fast parse-error translation guide, and compile-repair micro-cycles."
        ),
    },
    "T2": {
        "name": "Teachable: Runtime Debugging",
        "teachable_now": True,
        "intervention_track": "Trace-driven debugging",
        "intervention_plan": (
            "Teach print/assert tracing and variable-state tables. "
            "Run hypothesis-driven debugging drills on small failing cases."
        ),
    },
    "T3": {
        "name": "Teachable: Logic / Edge Cases",
        "teachable_now": True,
        "intervention_track": "Logic decomposition + test design",
        "intervention_plan": (
            "Teach input-output decomposition, boundary/adversarial test creation, "
            "and compare expected vs actual reasoning before coding."
        ),
    },
    "D3": {
        "name": "Mixed / Diffuse Pattern (Needs Diagnostic Sprint)",
        "teachable_now": False,
        "intervention_track": "Short diagnostic triage",
        "intervention_plan": (
            "Run a 30-45 minute diagnostic sprint to find a dominant failure mode, "
            "then move to T1/T2/T3 track."
        ),
    },
}


REFERENCES: list[tuple[str, str]] = [
    (
        "Robins, Rountree, and Rountree (2003), Learning and Teaching Programming: A Review and Discussion.",
        "https://doi.org/10.1076/csed.13.2.137.14200",
    ),
    (
        "Jadud and Dorn (2015), Aggregate Compilation Behavior: Findings and Implications for Introductory Programming Pedagogy.",
        "https://doi.org/10.1145/2787622.2787718",
    ),
    (
        "Schantong et al. (2024), Toward Finding and Supporting Struggling Students in a Programming Course with an Early Warning System.",
        "https://www.diva-portal.org/smash/get/diva2:1762835/FULLTEXT01.pdf",
    ),
    (
        "Margulieux et al. (2020), Subgoal-Labeled Worked Examples in Learning to Program.",
        "https://link.springer.com/content/pdf/10.1007/s10648-020-09582-9.pdf",
    ),
    (
        "Wisniewski, Zierer, and Hattie (2020), The Power of Feedback Revisited (meta-analysis).",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC7726232/",
    ),
    (
        "Freeman et al. (2014), Active Learning Increases Student Performance in STEM.",
        "https://www.pnas.org/doi/10.1073/pnas.1319030111",
    ),
    (
        "Nickow, Oreopoulos, and Quan (2020), The Impressive Effects of Tutoring on PreK-12 Learning.",
        "https://www.nber.org/papers/w27476",
    ),
    (
        "UNESCO (2023), Guidance for Generative AI in Education and Research.",
        "https://unesdoc.unesco.org/ark:/48223/pf0000386693",
    ),
    (
        "Prather et al. (2024), The Widening Gap: The Benefits and Harms of Generative AI for Novice Programmers.",
        "https://arxiv.org/abs/2408.14238",
    ),
]


TEACHING_PLAYBOOKS: dict[str, dict[str, Any]] = {
    "T1": {
        "nickname": "The Grammar Fixers",
        "eli15_why": (
            "Their ideas are often fine, but the code is like a sentence with broken grammar. "
            "If we help them make code structurally correct quickly, they can move forward."
        ),
        "session_flow": [
            "5 min: read the error message in plain English and predict where it comes from.",
            "10 min: do one tiny parse-fix cycle (change 1 thing -> run -> observe).",
            "10 min: rewrite one full function from a subgoal-labeled template (inputs, loop, condition, return).",
        ],
        "intervention_examples": [
            "Brace-and-indent clinic: give a broken snippet and ask them to only fix structure first, not logic.",
            "Error translation card: map common parser errors to one likely fix (missing colon, wrong indent, unmatched bracket).",
            "Skeleton completion drill: fill only TODO blocks in order, run after each block.",
        ],
        "coach_script": (
            "Say: 'Let’s make the code readable by Python first. Correct structure now, smart logic next.'"
        ),
    },
    "T2": {
        "nickname": "The Bug Detectives",
        "eli15_why": (
            "Their code runs, but crashes like a machine with one loose gear. "
            "They need a debugging method, not more random edits."
        ),
        "session_flow": [
            "5 min: name one crash and one hypothesis ('I think x is None here').",
            "10 min: trace table on paper for a tiny input (variable values each step).",
            "10 min: add 2 print/assert checks, rerun, and confirm hypothesis before editing logic.",
        ],
        "intervention_examples": [
            "Crash replay: reproduce one runtime error on the smallest input possible.",
            "Two-print rule: before each code change, add two diagnostics that prove/disprove a hypothesis.",
            "Guard-rail patterns: practice safe indexing, None checks, and dictionary-key existence checks.",
        ],
        "coach_script": (
            "Say: 'Don’t guess. We investigate like detectives: predict, trace, prove, then fix.'"
        ),
    },
    "T3": {
        "nickname": "The Edge-Case Engineers",
        "eli15_why": (
            "Their code usually runs but gives wrong answers in tricky cases. "
            "They need better thinking about cases, boundaries, and hidden assumptions."
        ),
        "session_flow": [
            "5 min: restate problem as input -> transformation -> output in one sentence.",
            "10 min: generate 5 tests (easy, boundary, weird, empty/minimum, adversarial).",
            "10 min: compare expected vs actual for each failed case before touching code.",
        ],
        "intervention_examples": [
            "Boundary ladder: test min, min+1, typical, max-1, max inputs.",
            "Counterexample hunt: ask 'What input would break my rule?' before submission.",
            "Two-column reasoning sheet: left = what program should do, right = what code currently does.",
        ],
        "coach_script": (
            "Say: 'Your engine runs. Now we teach it to handle surprise roads.'"
        ),
    },
}


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path}")


def read_csv(path: Path) -> pd.DataFrame:
    ensure_exists(path)
    return pd.read_csv(path)


def fmt_pct(x: float | int | None, digits: int = 1) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{100.0 * float(x):.{digits}f}%"


def fmt_float(x: float | int | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{float(x):.{digits}f}"


def to_markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows).copy()
    if df.empty:
        return "_No rows._"
    data = df.copy()
    for col in data.columns:
        data[col] = data[col].map(lambda v: "" if pd.isna(v) else str(v))
    headers = list(data.columns)
    rows = [headers] + data.values.tolist()
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    out: list[str] = []
    out.append("| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |")
    out.append("| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |")
    for row in data.values.tolist():
        out.append("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |")
    return "\n".join(out)


def build_student_wave_features() -> pd.DataFrame:
    process = read_csv(PATHS.process_features)
    process = process[(process["wave"] == "wave1") & (process["is_python_question"].fillna(False).astype(bool))].copy()

    student_wave = (
        process.groupby(["term", "wave", "student_id"], as_index=False)
        .agg(
            attempt_rows=("problem_id", "size"),
            public_test_runs_total=("public_test_run_count", "sum"),
            meaningful_edits_total=("meaningful_edit_event_count", "sum"),
            active_seconds_total=("active_time_seconds", "sum"),
            one_shot_ratio=("one_shot_flag", "mean"),
            skeleton_only_ratio=("skeleton_only_flag", "mean"),
            thrasher_ratio=("thrasher_flag", "mean"),
            regression_ratio=("regression_flag", "mean"),
            stuck_ratio=("stuck_and_abandoned_flag", "mean"),
            incremental_ratio=("incremental_debugger_flag", "mean"),
            builder_setbacks_ratio=("builder_with_setbacks_flag", "mean"),
            steady_builder_ratio=("steady_builder_flag", "mean"),
            parseable_fraction_mean=("parseable_fraction", "mean"),
            parseability_regression_ratio=("parseability_regression_flag", "mean"),
            no_improvement_latter_half_ratio=("no_improvement_latter_half_flag", "mean"),
        )
    )
    student_wave = student_wave[student_wave["attempt_rows"] >= MIN_ATTEMPT_ROWS].copy()
    student_wave["avg_public_runs_per_attempt"] = np.where(
        student_wave["attempt_rows"] > 0,
        student_wave["public_test_runs_total"] / student_wave["attempt_rows"],
        np.nan,
    )
    student_wave["avg_edits_per_attempt"] = np.where(
        student_wave["attempt_rows"] > 0,
        student_wave["meaningful_edits_total"] / student_wave["attempt_rows"],
        np.nan,
    )
    student_wave["avg_active_minutes_per_attempt"] = np.where(
        student_wave["attempt_rows"] > 0,
        (student_wave["active_seconds_total"] / 60.0) / student_wave["attempt_rows"],
        np.nan,
    )
    student_wave["productive_process_ratio"] = (
        student_wave["incremental_ratio"] + student_wave["builder_setbacks_ratio"] + student_wave["steady_builder_ratio"]
    )

    err = read_csv(PATHS.wave_error_profile)
    err = err[err["wave"] == "wave1"][
        [
            "term",
            "wave",
            "student_id",
            "question_rows",
            "runtime_error_rows",
            "wrong_logic_rows",
            "syntax_gated_rows",
            "full_pass_rows",
            "dominant_error_profile_bucket",
            "dominant_error_profile_bucket_share",
        ]
    ].copy()
    for c in ["runtime_error_rows", "wrong_logic_rows", "syntax_gated_rows", "full_pass_rows"]:
        err[f"{c}_ratio"] = np.where(
            pd.to_numeric(err["question_rows"], errors="coerce") > 0,
            pd.to_numeric(err[c], errors="coerce") / pd.to_numeric(err["question_rows"], errors="coerce"),
            np.nan,
        )

    concept = read_csv(PATHS.concept_wave_summary)
    concept = concept[concept["wave"] == "wave1"].copy()

    concept_agg = (
        concept.groupby(["term", "wave", "student_id"], as_index=False)
        .agg(
            concept_profiles=("concept", "nunique"),
            concept_failed_count=("concept_failed_flag", "sum"),
            concept_some_mastery_count=("concept_some_mastery_flag", "sum"),
            concept_mastered_count=("concept_mastered_flag", "sum"),
        )
    )
    concept_agg["concept_failure_ratio"] = np.where(
        concept_agg["concept_profiles"] > 0,
        concept_agg["concept_failed_count"] / concept_agg["concept_profiles"],
        np.nan,
    )

    # Keep the top few concept struggles for intervention routing.
    concept_tmp = concept.copy()
    concept_tmp["concept_failed_flag"] = concept_tmp["concept_failed_flag"].fillna(False).astype(bool)
    concept_tmp["severity_score"] = (
        concept_tmp["concept_failed_flag"].astype(int) * 10
        + pd.to_numeric(concept_tmp["concept_row_cat0"], errors="coerce").fillna(0.0)
        + (1 - concept_tmp["concept_some_mastery_flag"].fillna(False).astype(int)) * 0.5
    )
    concept_tmp = concept_tmp.sort_values(
        ["term", "wave", "student_id", "severity_score", "question_rows", "concept"],
        ascending=[True, True, True, False, False, True],
    )
    concept_tmp["rank_in_student"] = concept_tmp.groupby(["term", "wave", "student_id"]).cumcount() + 1
    concept_top = concept_tmp[concept_tmp["rank_in_student"] <= 3].copy()
    concept_top = (
        concept_top.groupby(["term", "wave", "student_id"])["concept"]
        .apply(lambda s: "; ".join(pd.Series(s).dropna().astype(str).tolist()))
        .reset_index(name="top_concept_struggles")
    )

    out = student_wave.merge(err, on=["term", "wave", "student_id"], how="left")
    out = out.merge(concept_agg, on=["term", "wave", "student_id"], how="left")
    out = out.merge(concept_top, on=["term", "wave", "student_id"], how="left")

    numeric_fill_zero = [
        "runtime_error_rows_ratio",
        "wrong_logic_rows_ratio",
        "syntax_gated_rows_ratio",
        "full_pass_rows_ratio",
        "dominant_error_profile_bucket_share",
        "concept_profiles",
        "concept_failed_count",
        "concept_some_mastery_count",
        "concept_mastered_count",
        "concept_failure_ratio",
    ]
    for col in numeric_fill_zero:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    out["dominant_error_profile_bucket"] = out["dominant_error_profile_bucket"].fillna("Unknown").astype(str)
    out["top_concept_struggles"] = out["top_concept_struggles"].fillna("").astype(str)
    return out


def classify_decision_tree(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()

    # Node 1: insufficient / low engagement.
    node_d0 = (
        (x["one_shot_ratio"] >= 0.50)
        | (x["skeleton_only_ratio"] >= 0.50)
        | ((x["avg_public_runs_per_attempt"] < 2.5) & (x["avg_edits_per_attempt"] < 3.0))
    )

    # Node 2: severe stuck/chaotic process loops.
    node_d1 = (~node_d0) & (
        (x["stuck_ratio"] >= 0.40)
        | ((x["thrasher_ratio"] >= 0.35) & (x["regression_ratio"] >= 0.25))
        | ((x["parseability_regression_ratio"] >= 0.30) & (x["no_improvement_latter_half_ratio"] >= 0.50))
    )

    # Node 3: already stable (low immediate intervention need).
    stable_bucket = x["dominant_error_profile_bucket"].str.lower().str.contains("full pass", na=False)
    node_d2 = (~node_d0) & (~node_d1) & (stable_bucket | (x["productive_process_ratio"] >= 0.60))

    # Common gate for teachable-now tracks: active + persistent + focused struggles.
    common_teachable_gate = (
        (~node_d0)
        & (~node_d1)
        & (~node_d2)
        & (x["avg_public_runs_per_attempt"] >= 4.5)
        & (x["avg_edits_per_attempt"] >= 5.5)
        & (x["concept_failed_count"] >= 2)
        & (x["dominant_error_profile_bucket_share"] >= 0.45)
        & (x["productive_process_ratio"] >= 0.10)
        & (x["stuck_ratio"] < 0.30)
    )

    # Teachable leaves.
    node_t1 = common_teachable_gate & (
        (x["syntax_gated_rows_ratio"] >= 0.20) | (x["dominant_error_profile_bucket"] == "Syntax gated")
    )
    node_t2 = common_teachable_gate & (~node_t1) & (
        ((x["runtime_error_rows_ratio"] >= 0.33) | (x["dominant_error_profile_bucket"] == "Runtime error"))
        & (x["parseable_fraction_mean"] >= 0.40)
    )
    node_t3 = common_teachable_gate & (~node_t1) & (~node_t2) & (
        (
            (x["wrong_logic_rows_ratio"] >= 0.18)
            | x["dominant_error_profile_bucket"].isin(["Wrong output - edge/partial", "Wrong output - logic"])
        )
        & (x["parseable_fraction_mean"] >= 0.55)
    )

    node_d3 = (~node_d0) & (~node_d1) & (~node_d2) & (~node_t1) & (~node_t2) & (~node_t3)

    x["path_d0"] = node_d0
    x["path_d1"] = node_d1
    x["path_d2"] = node_d2
    x["path_t1"] = node_t1
    x["path_t2"] = node_t2
    x["path_t3"] = node_t3
    x["path_d3"] = node_d3

    conditions = [node_d0, node_d1, node_d2, node_t1, node_t2, node_t3, node_d3]
    choices = ["D0", "D1", "D2", "T1", "T2", "T3", "D3"]
    x["decision_path_id"] = np.select(conditions, choices, default="D3")
    x["decision_path_name"] = x["decision_path_id"].map(lambda p: PATH_METADATA[p]["name"])
    x["teachable_now"] = x["decision_path_id"].map(lambda p: bool(PATH_METADATA[p]["teachable_now"]))
    x["intervention_track"] = x["decision_path_id"].map(lambda p: PATH_METADATA[p]["intervention_track"])
    x["intervention_plan"] = x["decision_path_id"].map(lambda p: PATH_METADATA[p]["intervention_plan"])

    # Optional prioritization *within* teachable leaves, still process-only.
    x["teachability_priority_index"] = (
        np.clip(x["avg_public_runs_per_attempt"] / 20.0, 0.0, 1.0) * 0.35
        + np.clip(x["avg_edits_per_attempt"] / 20.0, 0.0, 1.0) * 0.35
        + np.clip(x["productive_process_ratio"], 0.0, 1.0) * 0.20
        + np.clip(x["dominant_error_profile_bucket_share"], 0.0, 1.0) * 0.10
    )
    x["teachability_priority_index"] = np.where(x["teachable_now"], x["teachability_priority_index"], np.nan)
    return x


def path_counts_table(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby(["decision_path_id", "decision_path_name", "teachable_now"], as_index=False)
        .agg(student_term_profiles=("student_id", "size"))
        .sort_values("decision_path_id")
    )
    total = counts["student_term_profiles"].sum()
    counts["pct_profiles"] = np.where(total > 0, counts["student_term_profiles"] / total, np.nan)
    return counts


def path_term_table(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby(["decision_path_id", "term"], as_index=False)
        .agg(student_term_profiles=("student_id", "size"))
        .pivot(index="decision_path_id", columns="term", values="student_term_profiles")
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    for t in ["25t1", "25t2", "25t3"]:
        if t not in g.columns:
            g[t] = 0
    return g[["decision_path_id", "25t1", "25t2", "25t3"]]


def examples_by_path(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for pid, g in df.groupby("decision_path_id", sort=True):
        gg = g.sort_values(["term", "student_id"]).head(n)
        for _, r in gg.iterrows():
            rows.append(
                {
                    "decision_path_id": pid,
                    "term": r["term"],
                    "student_id": r["student_id"],
                    "dominant_error_profile_bucket": r["dominant_error_profile_bucket"],
                    "top_concept_struggles": r["top_concept_struggles"],
                }
            )
    return pd.DataFrame(rows)


def build_markdown(df: pd.DataFrame, rel_csv_path: Path) -> str:
    total_students = int(len(df))
    teachable = df[df["teachable_now"]].copy()
    teachable_count = int(len(teachable))

    path_counts = path_counts_table(df)
    path_counts_disp = path_counts.copy()
    path_counts_disp["pct_profiles"] = path_counts_disp["pct_profiles"].map(lambda x: fmt_pct(x, 1))
    path_counts_disp["teachable_now"] = path_counts_disp["teachable_now"].map(lambda b: "Yes" if b else "No")

    path_terms = path_term_table(df)
    path_terms = path_terms.merge(
        path_counts[["decision_path_id", "student_term_profiles"]],
        on="decision_path_id",
        how="left",
    ).rename(columns={"student_term_profiles": "all_terms_total"})

    term_summary = (
        df.groupby("term", as_index=False)
        .agg(
            student_term_profiles=("student_id", "size"),
            teachable_profiles=("teachable_now", "sum"),
        )
        .sort_values("term")
    )
    term_summary["teachable_pct"] = np.where(
        term_summary["student_term_profiles"] > 0,
        term_summary["teachable_profiles"] / term_summary["student_term_profiles"],
        np.nan,
    )
    term_summary_disp = term_summary.copy()
    term_summary_disp["teachable_pct"] = term_summary_disp["teachable_pct"].map(lambda x: fmt_pct(x, 1))

    teachable_breakdown = (
        teachable.groupby(["decision_path_id", "decision_path_name"], as_index=False)
        .agg(student_term_profiles=("student_id", "size"))
        .sort_values("student_term_profiles", ascending=False)
    )
    if not teachable_breakdown.empty:
        teachable_breakdown["pct_of_teachable"] = teachable_breakdown["student_term_profiles"] / teachable_count
        teachable_breakdown_disp = teachable_breakdown.copy()
        teachable_breakdown_disp["pct_of_teachable"] = teachable_breakdown_disp["pct_of_teachable"].map(lambda x: fmt_pct(x, 1))
    else:
        teachable_breakdown_disp = pd.DataFrame(
            columns=["decision_path_id", "decision_path_name", "student_term_profiles", "pct_of_teachable"]
        )

    examples = examples_by_path(df, n=8)

    # Small curated examples for teachable leaves.
    teachable_examples_sections: list[str] = []
    for pid in ["T1", "T2", "T3"]:
        g = df[df["decision_path_id"] == pid].copy().sort_values(["term", "student_id"])
        g = g[
            [
                "term",
                "student_id",
                "dominant_error_profile_bucket",
                "top_concept_struggles",
                "avg_public_runs_per_attempt",
                "avg_edits_per_attempt",
            ]
        ].head(12)
        if g.empty:
            continue
        g["avg_public_runs_per_attempt"] = g["avg_public_runs_per_attempt"].map(lambda x: fmt_float(x, 1))
        g["avg_edits_per_attempt"] = g["avg_edits_per_attempt"].map(lambda x: fmt_float(x, 1))
        teachable_examples_sections.append(
            f"### {pid} — {PATH_METADATA[pid]['name']}\n\n{to_markdown_table(g)}"
        )

    playbook_sections: list[str] = []
    for pid in ["T1", "T2", "T3"]:
        meta = TEACHING_PLAYBOOKS[pid]
        steps_text = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(meta["session_flow"])])
        examples_text = "\n".join([f"{i + 1}. {ex}" for i, ex in enumerate(meta["intervention_examples"])])
        playbook_sections.append(
            f"""### {pid} — {PATH_METADATA[pid]['name']} ({meta['nickname']})

**ELI15 Why This Works**

{meta['eli15_why']}

**A 25-Minute Intervention Recipe**

{steps_text}

**Concrete Intervention Examples**

{examples_text}

**Coach Line (Use Verbatim if Useful)**

`{meta['coach_script']}`
"""
        )

    refs_lines = [f"{i + 1}. [{title}]({url})" for i, (title, url) in enumerate(REFERENCES)]

    md = f"""# Teachable Students (Process-First, Score-Free)

## Quick Summary for Administrators (ELI15)

We are **not** picking students by marks.

Instead, we ask:

- Are they engaging seriously (running tests, editing code, sticking with problems)?
- Are their mistakes **consistent and fixable** (syntax, runtime, or logic pattern)?
- Do they show concept-level struggle we can target directly?

Those students are the most teachable now. They are struggling, but in a way that coaching can realistically fix fast.

## What Changed (Compared to Score-Based Targeting)

- No exam score thresholds.
- No "who improved last time" modeling.
- No dependence on the next OPPE having similar questions.

This is built only from learning-process traces, error signatures, and concept struggle patterns.

## Decision Tree Used

```text
Start (Wave 1, with >= {MIN_ATTEMPT_ROWS} attempt rows for reliable evidence)
|
|-- D0: Low engagement / one-shot usage?
|      (one_shot>=0.50 OR skeleton_only>=0.50 OR very low runs+edits)
|      -> D0 (not teachable-now; do re-engagement first)
|
|-- D1: Severe stuck / chaotic looping?
|      (high stuck OR thrasher+regression OR repeated parse regressions + no improvement)
|      -> D1 (not teachable-now; high-touch diagnostic coaching)
|
|-- D2: Already stable / low immediate need?
|      (dominant full-pass-like pattern OR high productive process ratio)
|      -> D2 (not priority for intensive intervention)
|
|-- Common teachable gate:
|      engaged enough + concept struggle + clear dominant error pattern + some productive behavior
|      |
|      |-- T1: Syntax-heavy failure signature -> Teachable Track 1
|      |-- T2: Runtime-heavy failure signature -> Teachable Track 2
|      |-- T3: Logic/edge-case-heavy signature -> Teachable Track 3
|      `-- otherwise -> D3 (mixed; run short diagnostic sprint first)
```

## Cohort Size (Existing Exams)

- Student-term profiles classified (Wave-1, substantive evidence): `{total_students}`
- Teachable-now profiles (`T1+T2+T3`): `{teachable_count}` (`{fmt_pct(teachable_count / total_students if total_students else np.nan, 1)}`)

### By Term

{to_markdown_table(term_summary_disp)}

### Decision-Tree Path Counts (All Terms)

{to_markdown_table(path_counts_disp)}

### Decision-Tree Path Counts by Term

{to_markdown_table(path_terms)}

### Teachable Path Mix

{to_markdown_table(teachable_breakdown_disp)}

## How to Teach Each Teachable Path

1. `T1 (Syntax Foundations)`
   - Problem pattern: non-parseable/syntax-gated errors despite active effort.
   - Intervention: subgoal-labeled code skeletons, parse-error translation guide, rapid compile-repair cycles.
2. `T2 (Runtime Debugging)`
   - Problem pattern: parseable code but runtime failures dominate.
   - Intervention: trace tables, assert/print instrumentation, hypothesis-driven debugging protocol.
3. `T3 (Logic / Edge Cases)`
   - Problem pattern: parseable/runnable, but wrong outputs and edge-case misses dominate.
   - Intervention: boundary-test design drills, input-output reasoning grids, compare expected vs actual before recoding.

## How To Teach Each Teachable Segment (ELI15 Playbooks)

{chr(10).join(playbook_sections)}

## Real Student Examples by Decision Path

{to_markdown_table(examples, max_rows=56)}

## Detailed Teachable Examples

{chr(10).join(teachable_examples_sections)}

## Why This Works Better for the Next OPPE

Because this model is about **how students learn and fail**, not about specific past questions:

- Engagement style (one-shot vs persistent)
- Error mechanism (syntax vs runtime vs logic)
- Concept struggle profile

Those transfer across question variants much better than raw marks.

## Caveats

- This identifies "teachable-now" for targeted support, not guaranteed outcomes.
- Students in `D0` and `D1` still matter; they usually need different intervention intensity first.
- Thresholds should be recalibrated each term if platform behavior shifts significantly.

## Reproducibility

Run:

```bash
uv run analysis/teachable.py
```

Outputs:

- `{rel_csv_path.as_posix()}`
- `analysis/teachable.md`

## References

{chr(10).join(refs_lines)}
"""
    return md


def main() -> None:
    features = build_student_wave_features()
    classified = classify_decision_tree(features)

    # Keep the full classified cohort so path counts remain auditable.
    out_cols = [
        "term",
        "wave",
        "student_id",
        "attempt_rows",
        "decision_path_id",
        "decision_path_name",
        "teachable_now",
        "intervention_track",
        "intervention_plan",
        "teachability_priority_index",
        "dominant_error_profile_bucket",
        "dominant_error_profile_bucket_share",
        "top_concept_struggles",
        "concept_profiles",
        "concept_failed_count",
        "concept_failure_ratio",
        "avg_public_runs_per_attempt",
        "avg_edits_per_attempt",
        "avg_active_minutes_per_attempt",
        "parseable_fraction_mean",
        "runtime_error_rows_ratio",
        "syntax_gated_rows_ratio",
        "wrong_logic_rows_ratio",
        "productive_process_ratio",
        "one_shot_ratio",
        "skeleton_only_ratio",
        "thrasher_ratio",
        "regression_ratio",
        "stuck_ratio",
        "parseability_regression_ratio",
        "no_improvement_latter_half_ratio",
        "path_d0",
        "path_d1",
        "path_d2",
        "path_t1",
        "path_t2",
        "path_t3",
        "path_d3",
    ]
    out_cols = [c for c in out_cols if c in classified.columns]
    out_df = classified[out_cols].sort_values(["term", "decision_path_id", "student_id"]).reset_index(drop=True)

    PATHS.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(PATHS.out_csv, index=False)

    rel_csv_path = PATHS.out_csv.relative_to(ROOT)
    md = build_markdown(out_df, rel_csv_path)
    PATHS.out_md.write_text(md, encoding="utf-8")

    teachable_n = int(out_df["teachable_now"].sum())
    print(f"Wrote: {PATHS.out_csv}")
    print(f"Wrote: {PATHS.out_md}")
    print(f"Classified students: {len(out_df)}")
    print(f"Teachable-now students: {teachable_n} ({(100.0 * teachable_n / len(out_df)):.1f}%)")


if __name__ == "__main__":
    main()
