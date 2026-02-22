#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
#   "matplotlib>=3.8.0",
#   "girth>=0.8.0",
# ]
# ///
"""Step 6: Psychometric Modelling with IRT (question-level GRM).

Primary measurement choice:
- Question-level 3-category scoring (0/1/2) to respect within-question test-case
  dependence found in Step 2.

Primary GRM basis in this script:
- `best_public` (best public test_run) for *all* rows, including submitters.
  This keeps the ordinal item definition coherent across the full population and
  avoids mixing private-final and public-best categories within the same
  namespace calibration.

Track-aware categories are also exported for sensitivity checks:
- `category_hybrid_track_aware` = private-final for Track A submitters,
  otherwise best-public.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

import duckdb
import matplotlib
import numpy as np
import pandas as pd
from girth import grm_mml_eap
from girth.utilities import INVALID_RESPONSE

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "psychometric_irt"
PLOTS_DIR = OUT_DIR / "plots"
TIF_PLOTS_DIR = PLOTS_DIR / "tif"

TRACK_A_SUBMITTERS = "Track A: submitters"
TRACK_A_NON_SUBMIT = "Track A: non-submitters (submission-positive NS)"
TRACK_B = "Track B: zero-submission namespaces"

NAMESPACE_PARSE_RE = re.compile(
    r"^ns_(?P<term>[^_]+)_(?P<slot>py(?P<wave_num>\d)(?P<slot_idx>\d+))(?:_(?P<variant>\d+))?$"
)


@dataclass(slots=True)
class NamespaceMeta:
    namespace: str
    term: str | None
    wave: str | None
    start_time: pd.Timestamp | None
    end_time: pd.Timestamp | None
    exam_date: pd.Timestamp | None
    slot_order_in_day: int | None
    parsed_term: str | None
    slot_code: str | None
    parsed_wave_num: int | None
    parsed_slot_idx: int | None
    variant: str | None
    namespace_family_no_variant: str | None
    namespace_standard_pattern: bool


def cpu_threads() -> int:
    try:
        n = os.cpu_count() or 4
    except Exception:
        n = 4
    return max(1, n - 1)


def make_conn() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute(f"PRAGMA threads={cpu_threads()}")
    conn.execute("PRAGMA enable_progress_bar=false")
    return conn


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def boolify_series(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    low = s.astype(str).str.strip().str.lower()
    return low.isin({"true", "1", "t", "yes", "y"})


def normalize_title(s: str | None) -> str:
    if not s:
        return ""
    txt = str(s).strip().lower()
    txt = txt.replace("&", " and ")
    txt = re.sub(r"\bq\d+\s*:\s*", "", txt)
    txt = re.sub(r"[^a-z0-9]+", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def parse_namespace_meta(namespace: str, sched_row: dict[str, Any] | None) -> NamespaceMeta:
    m = NAMESPACE_PARSE_RE.match(namespace or "")
    parsed_term = m.group("term") if m else None
    slot_code = m.group("slot") if m else None
    parsed_wave_num = int(m.group("wave_num")) if m and m.group("wave_num") else None
    parsed_slot_idx = int(m.group("slot_idx")) if m and m.group("slot_idx") else None
    variant = m.group("variant") if m and m.group("variant") else None
    fam = namespace
    if variant and namespace.endswith(f"_{variant}"):
        fam = namespace[: -(len(variant) + 1)]

    start_time = None
    end_time = None
    term = None
    wave = None
    exam_date = None
    slot_order = None
    if sched_row:
        term = sched_row.get("term")
        wave = sched_row.get("wave")
        start_time = sched_row.get("start_time")
        end_time = sched_row.get("end_time")
        if pd.notna(start_time):
            start_time = pd.Timestamp(start_time)
            exam_date = start_time.normalize()
        if pd.notna(end_time):
            end_time = pd.Timestamp(end_time)
        if sched_row.get("slot_order_in_day") is not None and pd.notna(sched_row.get("slot_order_in_day")):
            slot_order = int(sched_row["slot_order_in_day"])

    return NamespaceMeta(
        namespace=namespace,
        term=(None if pd.isna(term) else str(term)) if term is not None else None,
        wave=(None if pd.isna(wave) else str(wave)) if wave is not None else None,
        start_time=start_time,
        end_time=end_time,
        exam_date=exam_date,
        slot_order_in_day=slot_order,
        parsed_term=parsed_term,
        slot_code=slot_code,
        parsed_wave_num=parsed_wave_num,
        parsed_slot_idx=parsed_slot_idx,
        variant=variant,
        namespace_family_no_variant=fam,
        namespace_standard_pattern=bool(m),
    )


def category_from_counts(passed: Any, total: Any) -> float:
    p = pd.to_numeric(pd.Series([passed]), errors="coerce").iloc[0]
    t = pd.to_numeric(pd.Series([total]), errors="coerce").iloc[0]
    if pd.isna(p) or pd.isna(t):
        return np.nan
    if t <= 0:
        return np.nan
    p = float(p)
    t = float(t)
    if p <= 0:
        return 0.0
    if p >= t:
        return 2.0
    return 1.0


def logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def grm_item_information(theta_grid: np.ndarray, a: float, thresholds: np.ndarray) -> np.ndarray:
    """Samejima GRM item information via category-probability derivatives."""
    th = np.asarray(theta_grid, dtype=float)
    bs = np.asarray(thresholds, dtype=float)
    bs = bs[np.isfinite(bs)]
    if bs.size == 0 or not np.isfinite(a) or a == 0:
        return np.zeros_like(th)
    bs = np.sort(bs)

    cum = logistic(np.outer(th, np.array([a])) - (a * bs)[None, :])  # [T, K-1]
    dcum = a * cum * (1.0 - cum)
    n_cat = bs.size + 1

    probs = np.zeros((th.size, n_cat), dtype=float)
    dprobs = np.zeros_like(probs)
    probs[:, 0] = 1.0 - cum[:, 0]
    dprobs[:, 0] = -dcum[:, 0]
    for k in range(1, n_cat - 1):
        probs[:, k] = cum[:, k - 1] - cum[:, k]
        dprobs[:, k] = dcum[:, k - 1] - dcum[:, k]
    probs[:, -1] = cum[:, -1]
    dprobs[:, -1] = dcum[:, -1]

    eps = 1e-12
    probs = np.clip(probs, eps, 1.0)
    info = np.sum((dprobs**2) / probs, axis=1)
    return info


def make_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TIF_PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, NamespaceMeta]]:
    print("[1/8] Loading Step 1/4 inputs and namespace metadata...")
    rows = pd.read_csv(ANALYSIS_DIR / "syntax_bottleneck_quantified" / "gating_waterfall_rows.csv", low_memory=False)
    q_metrics = pd.read_csv(ANALYSIS_DIR / "score_failure_profiles" / "question_score_metrics.csv", low_memory=False)
    schedule = pd.read_csv(ANALYSIS_DIR / "schedule.csv", low_memory=False)

    for df in (rows, q_metrics):
        df["problem_id"] = to_num(df["problem_id"]).astype("Int64")

    # Normalize typed columns we rely on.
    for c in [
        "best_public_test_case_count",
        "best_public_num_test_passed",
        "private_num_cases",
        "private_num_passed",
        "latest_submission_score",
        "problem_max_score",
    ]:
        if c in rows.columns:
            rows[c] = to_num(rows[c])
    for c in ["flag_bimodal", "flag_ceiling", "flag_floor", "flag_healthy_spread"]:
        if c in q_metrics.columns:
            q_metrics[c] = boolify_series(q_metrics[c])

    # Schedule + slot order by namespace.
    for c in ["start_time", "end_time"]:
        if c in schedule.columns:
            schedule[c] = pd.to_datetime(schedule[c], errors="coerce", utc=True)
    if "start_time" in schedule.columns:
        schedule["exam_date"] = schedule["start_time"].dt.normalize()
        schedule = schedule.sort_values(["term", "wave", "exam_date", "start_time", "namespace"], kind="mergesort")
        schedule["slot_order_in_day"] = schedule.groupby(["term", "wave", "exam_date"], dropna=False).cumcount() + 1
    else:
        schedule["exam_date"] = pd.NaT
        schedule["slot_order_in_day"] = np.nan

    sched_map = {}
    for rec in schedule[["namespace", "term", "wave", "start_time", "end_time", "exam_date", "slot_order_in_day"]].to_dict("records"):
        sched_map[str(rec["namespace"])] = rec
    ns_meta = {ns: parse_namespace_meta(ns, sched_map.get(ns)) for ns in sorted(rows["namespace"].dropna().astype(str).unique())}

    ns_meta_df = pd.DataFrame(
        [
            {
                "namespace": m.namespace,
                "term": m.term,
                "wave": m.wave,
                "start_time": m.start_time,
                "end_time": m.end_time,
                "exam_date": m.exam_date,
                "slot_order_in_day": m.slot_order_in_day,
                "parsed_term": m.parsed_term,
                "slot_code": m.slot_code,
                "parsed_wave_num": m.parsed_wave_num,
                "parsed_slot_idx": m.parsed_slot_idx,
                "variant": m.variant,
                "namespace_family_no_variant": m.namespace_family_no_variant,
                "namespace_standard_pattern": m.namespace_standard_pattern,
            }
            for m in ns_meta.values()
        ]
    )
    ns_meta_df.sort_values("namespace").to_csv(OUT_DIR / "namespace_metadata.csv", index=False)

    return rows, q_metrics, schedule, ns_meta


def build_question_level_rows(rows: pd.DataFrame, q_metrics: pd.DataFrame) -> pd.DataFrame:
    print("[2/8] Building question-level ordinal scoring rows (0/1/2) ...")
    df = rows.copy()

    # Public-best category (primary GRM basis in this script).
    df["category_public_best"] = [
        category_from_counts(p, t)
        for p, t in zip(df.get("best_public_num_test_passed", np.nan), df.get("best_public_test_case_count", np.nan))
    ]

    # Track-aware hybrid category (prompt-literal sensitivity export).
    df["category_private_final"] = [
        category_from_counts(p, t)
        for p, t in zip(df.get("private_num_passed", np.nan), df.get("private_num_cases", np.nan))
    ]
    is_submitter = df["track"].astype(str).eq(TRACK_A_SUBMITTERS)
    df["category_hybrid_track_aware"] = np.where(is_submitter, df["category_private_final"], df["category_public_best"])
    # Fallback to public if a submitter row somehow lacks private counts.
    df["category_hybrid_track_aware"] = np.where(
        np.isnan(df["category_hybrid_track_aware"]),
        df["category_public_best"],
        df["category_hybrid_track_aware"],
    )

    # Primary basis used for GRM fits (coherent full-pop basis).
    df["grm_basis"] = "public_best_all"
    df["grm_category"] = df["category_public_best"]

    # Add normalized titles and Step 1 shape flags.
    df["question_title_norm"] = df.get("question_title", pd.Series("", index=df.index)).map(normalize_title)
    qf = q_metrics[
        [
            "namespace",
            "problem_id",
            "flag_bimodal",
            "flag_ceiling",
            "flag_floor",
            "flag_healthy_spread",
            "distribution_shape",
            "submission_rate_pct",
            "submitter_full_pct",
            "submitter_zero_pct",
            "all_assigned_mean_score",
        ]
    ].copy()
    qf["problem_id"] = to_num(qf["problem_id"]).astype("Int64")
    df = df.merge(qf, on=["namespace", "problem_id"], how="left")

    keep_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "track",
        "term",
        "wave",
        "question_title",
        "question_title_norm",
        "outcome_category",
        "submission_positive_namespace",
        "latest_submission_score",
        "problem_max_score",
        "best_public_test_case_count",
        "best_public_num_test_passed",
        "private_num_cases",
        "private_num_passed",
        "category_public_best",
        "category_private_final",
        "category_hybrid_track_aware",
        "grm_basis",
        "grm_category",
        "flag_bimodal",
        "flag_ceiling",
        "flag_floor",
        "flag_healthy_spread",
        "distribution_shape",
        "submission_rate_pct",
        "submitter_full_pct",
        "submitter_zero_pct",
        "all_assigned_mean_score",
    ]
    out = df[[c for c in keep_cols if c in df.columns]].copy()
    out["problem_id"] = to_num(out["problem_id"]).astype("Int64")

    coverage_rows = []
    for track, g in out.groupby("track", dropna=False):
        n = len(g)
        coverage_rows.append(
            {
                "track": track,
                "rows": n,
                "rows_with_public_category": int(g["category_public_best"].notna().sum()),
                "rows_with_private_category": int(g["category_private_final"].notna().sum()),
                "rows_with_hybrid_category": int(g["category_hybrid_track_aware"].notna().sum()),
                "pct_with_public_category": round(100.0 * g["category_public_best"].notna().mean(), 2) if n else np.nan,
                "pct_with_private_category": round(100.0 * g["category_private_final"].notna().mean(), 2) if n else np.nan,
            }
        )
    pd.DataFrame(coverage_rows).sort_values("track").to_csv(OUT_DIR / "question_level_category_coverage_by_track.csv", index=False)

    submit = out[out["track"] == TRACK_A_SUBMITTERS].copy()
    if not submit.empty:
        both = submit["category_public_best"].notna() & submit["category_private_final"].notna()
        cmp = submit.loc[both, ["category_public_best", "category_private_final"]].copy()
        cmp["agree"] = cmp["category_public_best"] == cmp["category_private_final"]
        pd.DataFrame(
            [
                {
                    "submitter_rows": len(submit),
                    "rows_with_both_public_and_private_category": int(both.sum()),
                    "agreement_rate_pct": round(100.0 * cmp["agree"].mean(), 2) if len(cmp) else np.nan,
                    "public_higher_than_private_pct": round(100.0 * (cmp["category_public_best"] > cmp["category_private_final"]).mean(), 2) if len(cmp) else np.nan,
                    "private_higher_than_public_pct": round(100.0 * (cmp["category_private_final"] > cmp["category_public_best"]).mean(), 2) if len(cmp) else np.nan,
                }
            ]
        ).to_csv(OUT_DIR / "submitter_public_vs_private_category_agreement.csv", index=False)
        (
            cmp.groupby(["category_public_best", "category_private_final"], dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values(["category_public_best", "category_private_final"])
            .to_csv(OUT_DIR / "submitter_public_vs_private_category_crosstab.csv", index=False)
        )

    out.sort_values(["namespace", "problem_id", "student_id"], inplace=True)
    out.to_csv(OUT_DIR / "question_level_grm_rows.csv", index=False)
    return out


def fit_one_namespace_grm(ns_df: pd.DataFrame, *, theta_grid: np.ndarray) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    namespace = str(ns_df["namespace"].iloc[0])
    term = None if "term" not in ns_df.columns else (None if pd.isna(ns_df["term"].iloc[0]) else str(ns_df["term"].iloc[0]))
    wave = None if "wave" not in ns_df.columns else (None if pd.isna(ns_df["wave"].iloc[0]) else str(ns_df["wave"].iloc[0]))

    # Build student x item matrix on primary GRM category.
    work = ns_df[["student_id", "problem_id", "question_title", "question_title_norm", "grm_category"]].copy()
    work["problem_id"] = to_num(work["problem_id"]).astype("Int64")
    work["grm_category"] = to_num(work["grm_category"])

    item_meta = (
        work.groupby(["problem_id", "question_title", "question_title_norm"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("problem_id")
    )
    item_ids = item_meta["problem_id"].tolist()
    student_ids = sorted(work["student_id"].dropna().astype(str).unique().tolist())

    pivot = work.pivot(index="student_id", columns="problem_id", values="grm_category").reindex(index=student_ids, columns=item_ids)

    # Item coverage and category usage.
    item_cov_rows = []
    keep_items: list[int] = []
    for pid in item_ids:
        vals = pivot[pid]
        obs = vals.dropna()
        counts = obs.value_counts().to_dict()
        n_unique = int(obs.nunique())
        cov = int(obs.shape[0])
        item_cov_rows.append(
            {
                "namespace": namespace,
                "problem_id": int(pid),
                "question_title": item_meta.loc[item_meta["problem_id"] == pid, "question_title"].iloc[0],
                "question_title_norm": item_meta.loc[item_meta["problem_id"] == pid, "question_title_norm"].iloc[0],
                "students_total": len(student_ids),
                "students_observed": cov,
                "pct_observed": round(100.0 * cov / max(1, len(student_ids)), 2),
                "n_categories_observed": n_unique,
                "count_cat0": int(counts.get(0.0, 0)),
                "count_cat1": int(counts.get(1.0, 0)),
                "count_cat2": int(counts.get(2.0, 0)),
            }
        )
        if cov >= 30 and n_unique >= 2:
            keep_items.append(int(pid))

    item_cov_df = pd.DataFrame(item_cov_rows).sort_values("problem_id")

    summary: dict[str, Any] = {
        "namespace": namespace,
        "term": term,
        "wave": wave,
        "status": "not_fit",
        "reason": None,
        "grm_basis": "public_best_all",
        "students_total": int(len(student_ids)),
        "items_total": int(len(item_ids)),
        "items_kept_for_fit": int(len(keep_items)),
        "items_dropped_for_fit": int(len(item_ids) - len(keep_items)),
    }

    if len(keep_items) < 3:
        summary["reason"] = "too_few_informative_items_after_filter"
        return summary, item_cov_df, pd.DataFrame(), pd.DataFrame()

    pivot_fit = pivot[keep_items].copy()
    # Drop respondents with all-missing after item filter.
    respondent_nonmissing = pivot_fit.notna().sum(axis=1)
    pivot_fit = pivot_fit.loc[respondent_nonmissing > 0].copy()
    if pivot_fit.shape[0] < 50:
        summary["reason"] = "too_few_respondents_after_filter"
        return summary, item_cov_df, pd.DataFrame(), pd.DataFrame()

    data = pivot_fit.to_numpy(dtype=float, copy=True).T  # items x persons
    data_int = np.full(data.shape, INVALID_RESPONSE, dtype=int)
    valid = np.isfinite(data)
    data_int[valid] = data[valid].astype(int)

    # Fit GRM (EAP/MMLE).
    try:
        fit = grm_mml_eap(
            data_int,
            options={
                "max_iteration": 200,
                "quadrature_n": 41,
                "estimate_distribution": False,
            },
        )
        fit_status = "fit_ok"
    except Exception as exc:  # noqa: BLE001
        summary["status"] = "fit_failed"
        summary["reason"] = f"{exc.__class__.__name__}: {str(exc)[:300]}"
        return summary, item_cov_df, pd.DataFrame(), pd.DataFrame()

    a = np.asarray(fit.get("Discrimination", []), dtype=float)
    b = np.asarray(fit.get("Difficulty", []), dtype=float)
    theta = np.asarray(fit.get("Ability", []), dtype=float)

    kept_item_ids = list(pivot_fit.columns)
    if a.shape[0] != len(kept_item_ids):
        summary["status"] = "fit_failed"
        summary["reason"] = f"unexpected_discrimination_shape_{a.shape}"
        return summary, item_cov_df, pd.DataFrame(), pd.DataFrame()
    if theta.shape[0] != pivot_fit.shape[0]:
        summary["status"] = "fit_failed"
        summary["reason"] = f"unexpected_theta_shape_{theta.shape}"
        return summary, item_cov_df, pd.DataFrame(), pd.DataFrame()

    # Item parameter rows.
    item_param_rows: list[dict[str, Any]] = []
    tif_rows: list[dict[str, Any]] = []
    test_info = np.zeros_like(theta_grid, dtype=float)

    # Map step1 flags etc from ns_df one row per question.
    q_ref = (
        ns_df.drop_duplicates(subset=["problem_id"])
        .set_index("problem_id", drop=False)
    )

    for i, pid in enumerate(kept_item_ids):
        thresholds = np.asarray(b[i], dtype=float)
        finite_thr = thresholds[np.isfinite(thresholds)]
        finite_thr = np.sort(finite_thr)
        b1 = float(finite_thr[0]) if finite_thr.size >= 1 else np.nan
        b2 = float(finite_thr[1]) if finite_thr.size >= 2 else np.nan
        gap = float(b2 - b1) if finite_thr.size >= 2 else np.nan
        info = grm_item_information(theta_grid, float(a[i]), finite_thr)
        test_info += info

        qrow = q_ref.loc[pid] if pid in q_ref.index else None
        cov_row = item_cov_df[item_cov_df["problem_id"] == pid]
        cov = cov_row.iloc[0].to_dict() if not cov_row.empty else {}
        c0 = int(cov.get("count_cat0", 0))
        c1 = int(cov.get("count_cat1", 0))
        c2 = int(cov.get("count_cat2", 0))
        obs_n = int(cov.get("students_observed", 0))
        item_param_rows.append(
            {
                "namespace": namespace,
                "term": term,
                "wave": wave,
                "grm_basis": "public_best_all",
                "problem_id": int(pid),
                "question_title": (None if qrow is None else qrow.get("question_title")),
                "question_title_norm": (None if qrow is None else qrow.get("question_title_norm")),
                "students_total_namespace": int(pivot_fit.shape[0]),
                "students_observed_item": obs_n,
                "pct_observed_item": (round(100.0 * obs_n / max(1, pivot_fit.shape[0]), 2)),
                "count_cat0": c0,
                "count_cat1": c1,
                "count_cat2": c2,
                "pct_cat0": (round(100.0 * c0 / obs_n, 2) if obs_n else np.nan),
                "pct_cat1": (round(100.0 * c1 / obs_n, 2) if obs_n else np.nan),
                "pct_cat2": (round(100.0 * c2 / obs_n, 2) if obs_n else np.nan),
                "a_discrimination": float(a[i]),
                "n_thresholds_estimated": int(finite_thr.size),
                "b1_any_partial_threshold": b1,
                "b2_full_threshold": b2,
                "threshold_gap_b2_minus_b1": gap,
                "item_info_peak": float(np.max(info)),
                "item_info_peak_theta": float(theta_grid[int(np.argmax(info))]),
                "item_info_mean_low_theta_le_neg1": float(np.mean(info[theta_grid <= -1])),
                "item_info_mean_mid_abs_le_0_5": float(np.mean(info[np.abs(theta_grid) <= 0.5])),
                "item_info_mean_high_theta_ge_pos1": float(np.mean(info[theta_grid >= 1])),
                "flag_bimodal_step1": (None if qrow is None else qrow.get("flag_bimodal")),
                "flag_ceiling_step1": (None if qrow is None else qrow.get("flag_ceiling")),
                "flag_floor_step1": (None if qrow is None else qrow.get("flag_floor")),
                "flag_healthy_spread_step1": (None if qrow is None else qrow.get("flag_healthy_spread")),
                "distribution_shape_step1": (None if qrow is None else qrow.get("distribution_shape")),
                "submission_rate_pct_step1": (None if qrow is None else qrow.get("submission_rate_pct")),
                "submitter_full_pct_step1": (None if qrow is None else qrow.get("submitter_full_pct")),
                "submitter_zero_pct_step1": (None if qrow is None else qrow.get("submitter_zero_pct")),
                "all_assigned_mean_score_step1": (None if qrow is None else qrow.get("all_assigned_mean_score")),
            }
        )
        for tg, iv in zip(theta_grid, info):
            tif_rows.append(
                {
                    "namespace": namespace,
                    "term": term,
                    "wave": wave,
                    "grm_basis": "public_best_all",
                    "problem_id": int(pid),
                    "theta": float(tg),
                    "item_information": float(iv),
                }
            )

    test_info_rows = pd.DataFrame(
        {
            "namespace": namespace,
            "term": term,
            "wave": wave,
            "grm_basis": "public_best_all",
            "theta": theta_grid,
            "test_information": test_info,
        }
    )
    test_info_rows.to_csv(OUT_DIR / "tmp_tif.csv", mode="a", index=False, header=not (OUT_DIR / "tmp_tif.csv").exists())

    tif_summary = {
        "namespace": namespace,
        "term": term,
        "wave": wave,
        "grm_basis": "public_best_all",
        "info_peak_theta": float(theta_grid[int(np.argmax(test_info))]),
        "info_peak_value": float(np.max(test_info)),
        "info_mean_low_theta_le_neg1": float(np.mean(test_info[theta_grid <= -1])),
        "info_mean_mid_abs_le_0_5": float(np.mean(test_info[np.abs(theta_grid) <= 0.5])),
        "info_mean_high_theta_ge_pos1": float(np.mean(test_info[theta_grid >= 1])),
        "info_low_to_mid_ratio": (
            float(np.mean(test_info[theta_grid <= -1]) / np.mean(test_info[np.abs(theta_grid) <= 0.5]))
            if np.mean(test_info[np.abs(theta_grid) <= 0.5]) > 0
            else np.nan
        ),
        "theta_mean": float(np.nanmean(theta)),
        "theta_sd": float(np.nanstd(theta, ddof=1)) if theta.size > 1 else np.nan,
        "theta_p10": float(np.nanpercentile(theta, 10)),
        "theta_p50": float(np.nanpercentile(theta, 50)),
        "theta_p90": float(np.nanpercentile(theta, 90)),
    }

    # Student theta rows.
    theta_rows = pd.DataFrame(
        {
            "namespace": namespace,
            "term": term,
            "wave": wave,
            "grm_basis": "public_best_all",
            "student_id": pivot_fit.index.astype(str),
            "theta": theta,
            "ordinal_sum_score": np.where(pivot_fit.notna().sum(axis=1) > 0, pivot_fit.fillna(0).sum(axis=1), np.nan),
            "ordinal_mean_score": pivot_fit.mean(axis=1, skipna=True).to_numpy(dtype=float),
            "answered_items": pivot_fit.notna().sum(axis=1).to_numpy(dtype=int),
        }
    )

    # Namespace-level fit summary.
    summary.update(
        {
            "status": fit_status,
            "reason": None,
            "students_fitted": int(pivot_fit.shape[0]),
            "items_fitted": int(len(kept_item_ids)),
            "matrix_cells": int(pivot_fit.shape[0] * pivot_fit.shape[1]),
            "observed_cells": int(pivot_fit.notna().sum().sum()),
            "pct_missing_cells": round(100.0 * (1 - (pivot_fit.notna().sum().sum() / max(1, pivot_fit.shape[0] * pivot_fit.shape[1]))), 2),
            "aic_null": (fit.get("AIC", {}) or {}).get("null"),
            "aic_model": (fit.get("AIC", {}) or {}).get("final"),
            "bic_null": (fit.get("BIC", {}) or {}).get("null"),
            "bic_model": (fit.get("BIC", {}) or {}).get("final"),
            "theta_mean": tif_summary["theta_mean"],
            "theta_sd": tif_summary["theta_sd"],
            "theta_p10": tif_summary["theta_p10"],
            "theta_p50": tif_summary["theta_p50"],
            "theta_p90": tif_summary["theta_p90"],
            "info_peak_theta": tif_summary["info_peak_theta"],
            "info_peak_value": tif_summary["info_peak_value"],
            "info_low_to_mid_ratio": tif_summary["info_low_to_mid_ratio"],
            "info_mean_low_theta_le_neg1": tif_summary["info_mean_low_theta_le_neg1"],
            "info_mean_mid_abs_le_0_5": tif_summary["info_mean_mid_abs_le_0_5"],
            "info_mean_high_theta_ge_pos1": tif_summary["info_mean_high_theta_ge_pos1"],
        }
    )

    # Plot TIF for namespace.
    try:
        plt.figure(figsize=(6.8, 4.2))
        plt.plot(theta_grid, test_info, lw=2)
        plt.axvline(-1, color="#999", ls="--", lw=0.8)
        plt.axvline(0, color="#bbb", ls=":", lw=0.8)
        plt.axvline(1, color="#999", ls="--", lw=0.8)
        plt.title(f"{namespace} Test Information (Question-level GRM)")
        plt.xlabel("Theta")
        plt.ylabel("Test Information")
        plt.tight_layout()
        plt.savefig(TIF_PLOTS_DIR / f"{namespace}.png", dpi=140)
        plt.close()
    except Exception:
        plt.close("all")

    return summary, item_cov_df, pd.DataFrame(item_param_rows), theta_rows


def fit_all_namespaces_grm(grm_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print("[3/8] Fitting per-namespace question-level GRMs (public-best basis)...")
    theta_grid = np.linspace(-4.0, 4.0, 161)

    tmp_tif = OUT_DIR / "tmp_tif.csv"
    if tmp_tif.exists():
        tmp_tif.unlink()

    fit_summaries: list[dict[str, Any]] = []
    item_cov_parts: list[pd.DataFrame] = []
    item_param_parts: list[pd.DataFrame] = []
    theta_parts: list[pd.DataFrame] = []

    grouped = grm_rows.groupby("namespace", sort=True, dropna=False)
    total_ns = len(grouped)
    for idx, (namespace, ns_df) in enumerate(grouped, start=1):
        summary, item_cov_df, item_params_df, theta_df = fit_one_namespace_grm(ns_df, theta_grid=theta_grid)
        fit_summaries.append(summary)
        item_cov_parts.append(item_cov_df)
        if not item_params_df.empty:
            item_param_parts.append(item_params_df)
        if not theta_df.empty:
            theta_parts.append(theta_df)
        if idx % 5 == 0 or idx == total_ns:
            print(f"  fitted {idx:,}/{total_ns:,} namespaces...")

    fit_df = pd.DataFrame(fit_summaries).sort_values(["status", "namespace"], ascending=[True, True])
    cov_df = pd.concat(item_cov_parts, ignore_index=True) if item_cov_parts else pd.DataFrame()
    params_df = pd.concat(item_param_parts, ignore_index=True) if item_param_parts else pd.DataFrame()
    theta_df = pd.concat(theta_parts, ignore_index=True) if theta_parts else pd.DataFrame()
    tif_df = pd.read_csv(tmp_tif) if tmp_tif.exists() else pd.DataFrame()
    if tmp_tif.exists():
        tmp_tif.unlink()

    fit_df.to_csv(OUT_DIR / "namespace_grm_fit_summary.csv", index=False)
    cov_df.to_csv(OUT_DIR / "namespace_item_matrix_coverage.csv", index=False)
    params_df.to_csv(OUT_DIR / "namespace_question_grm_parameters.csv", index=False)
    theta_df.to_csv(OUT_DIR / "namespace_student_theta.csv", index=False)
    tif_df.to_csv(OUT_DIR / "namespace_test_information_grid.csv", index=False)

    # Namespace TIF summary from fit summary subset for convenience.
    tif_summary_cols = [
        "namespace",
        "term",
        "wave",
        "grm_basis",
        "status",
        "students_fitted",
        "items_fitted",
        "info_peak_theta",
        "info_peak_value",
        "info_mean_low_theta_le_neg1",
        "info_mean_mid_abs_le_0_5",
        "info_mean_high_theta_ge_pos1",
        "info_low_to_mid_ratio",
        "theta_mean",
        "theta_sd",
        "theta_p10",
        "theta_p50",
        "theta_p90",
    ]
    fit_df[[c for c in tif_summary_cols if c in fit_df.columns]].to_csv(OUT_DIR / "namespace_test_information_summary.csv", index=False)

    return fit_df, cov_df, params_df, theta_df


def build_question_parameter_analysis(params_df: pd.DataFrame) -> pd.DataFrame:
    print("[4/8] Analysing GRM question parameters and generating plots...")
    if params_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "question_parameter_flags.csv", index=False)
        return params_df

    df = params_df.copy()
    df["a_discrimination"] = to_num(df["a_discrimination"])
    df["b1_any_partial_threshold"] = to_num(df["b1_any_partial_threshold"])
    df["b2_full_threshold"] = to_num(df["b2_full_threshold"])
    df["threshold_gap_b2_minus_b1"] = to_num(df["threshold_gap_b2_minus_b1"])

    p95_a = float(np.nanpercentile(df["a_discrimination"], 95)) if df["a_discrimination"].notna().any() else np.nan
    p90_b1 = float(np.nanpercentile(df["b1_any_partial_threshold"].dropna(), 90)) if df["b1_any_partial_threshold"].notna().any() else np.nan

    df["flag_low_discrimination"] = df["a_discrimination"] < 0.5
    df["flag_very_high_discrimination"] = (df["a_discrimination"] >= 2.5) | (df["a_discrimination"] >= p95_a)
    df["flag_extreme_b1_high"] = df["b1_any_partial_threshold"] >= max(1.5, p90_b1 if np.isfinite(p90_b1) else 1.5)
    df["flag_partial_credit_low_information"] = df["threshold_gap_b2_minus_b1"] < 0.35
    df["flag_partial_credit_missing_or_collapsed"] = df["n_thresholds_estimated"] < 2
    df["b_mean"] = df[["b1_any_partial_threshold", "b2_full_threshold"]].mean(axis=1, skipna=True)

    # Simple "cliff effect" proxy from GRM + Step 1.
    df["flag_cliff_like"] = df["flag_very_high_discrimination"] & (
        boolify_series(df["flag_bimodal_step1"]) if "flag_bimodal_step1" in df.columns else False
    )

    flag_cols = [
        "flag_low_discrimination",
        "flag_very_high_discrimination",
        "flag_extreme_b1_high",
        "flag_partial_credit_low_information",
        "flag_partial_credit_missing_or_collapsed",
        "flag_cliff_like",
    ]
    qflag = df[
        [
            "namespace",
            "problem_id",
            "question_title",
            "a_discrimination",
            "b1_any_partial_threshold",
            "b2_full_threshold",
            "threshold_gap_b2_minus_b1",
            "n_thresholds_estimated",
            "count_cat0",
            "count_cat1",
            "count_cat2",
            "flag_bimodal_step1",
            "distribution_shape_step1",
            *flag_cols,
        ]
    ].copy()
    qflag.sort_values(["flag_low_discrimination", "flag_very_high_discrimination", "a_discrimination"], ascending=[False, False, False], inplace=True)
    qflag.to_csv(OUT_DIR / "question_parameter_flags.csv", index=False)

    # Aggregated counts for README.
    pd.DataFrame(
        [
            {
                "questions_fitted": len(df),
                "low_discrimination_count_a_lt_0_5": int(df["flag_low_discrimination"].sum()),
                "very_high_discrimination_count": int(df["flag_very_high_discrimination"].sum()),
                "extreme_b1_high_count": int(df["flag_extreme_b1_high"].sum()),
                "partial_credit_low_information_gap_lt_0_35_count": int(df["flag_partial_credit_low_information"].sum()),
                "partial_credit_missing_or_collapsed_count": int(df["flag_partial_credit_missing_or_collapsed"].sum()),
                "cliff_like_count_bimodal_and_high_a": int(df["flag_cliff_like"].sum()),
                "a_discrimination_median": float(np.nanmedian(df["a_discrimination"])),
                "a_discrimination_p95": float(np.nanpercentile(df["a_discrimination"], 95)),
                "b1_median": float(np.nanmedian(df["b1_any_partial_threshold"])),
                "b2_median": float(np.nanmedian(df["b2_full_threshold"])),
                "threshold_gap_median": float(np.nanmedian(df["threshold_gap_b2_minus_b1"])),
            }
        ]
    ).to_csv(OUT_DIR / "question_parameter_summary.csv", index=False)

    # Scatter plots.
    try:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
        ax = axes[0]
        m1 = df["b1_any_partial_threshold"].notna() & df["a_discrimination"].notna()
        colors = np.where(df.loc[m1, "flag_bimodal_step1"].fillna(False), "#c0392b", "#1f77b4")
        ax.scatter(df.loc[m1, "b1_any_partial_threshold"], df.loc[m1, "a_discrimination"], s=30, alpha=0.75, c=colors)
        ax.axhline(0.5, color="#666", ls="--", lw=0.9)
        ax.set_title("GRM Item Params: a vs b1 (0→1)")
        ax.set_xlabel("b1 threshold (any partial credit)")
        ax.set_ylabel("a discrimination")

        ax = axes[1]
        m2 = df["b2_full_threshold"].notna() & df["a_discrimination"].notna()
        colors2 = np.where(df.loc[m2, "flag_bimodal_step1"].fillna(False), "#c0392b", "#2ca02c")
        ax.scatter(df.loc[m2, "b2_full_threshold"], df.loc[m2, "a_discrimination"], s=30, alpha=0.75, c=colors2)
        ax.axhline(0.5, color="#666", ls="--", lw=0.9)
        ax.set_title("GRM Item Params: a vs b2 (1→2)")
        ax.set_xlabel("b2 threshold (full credit)")
        ax.set_ylabel("a discrimination")
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "question_parameter_scatter.png", dpi=150)
        plt.close(fig)
    except Exception:
        plt.close("all")

    return df


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def classify_namespace_pair_type(a: NamespaceMeta, b: NamespaceMeta) -> str:
    # Variant pair: same term+slot, different explicit variants.
    if (
        a.namespace_standard_pattern
        and b.namespace_standard_pattern
        and a.parsed_term == b.parsed_term
        and a.slot_code == b.slot_code
        and a.variant is not None
        and b.variant is not None
        and a.variant != b.variant
    ):
        return "variant_pair_same_slot"

    # Wave pair: same term, same variant (or both none), same slot index, different wave num.
    if (
        a.namespace_standard_pattern
        and b.namespace_standard_pattern
        and a.parsed_term == b.parsed_term
        and a.parsed_slot_idx is not None
        and a.parsed_slot_idx == b.parsed_slot_idx
        and a.parsed_wave_num is not None
        and b.parsed_wave_num is not None
        and a.parsed_wave_num != b.parsed_wave_num
        and (a.variant or "") == (b.variant or "")
    ):
        return "wave_pair_same_slot_index"

    # Time slot pair same day/wave/term.
    if (
        a.term is not None
        and b.term is not None
        and a.term == b.term
        and a.wave is not None
        and b.wave is not None
        and a.wave == b.wave
        and a.exam_date is not None
        and b.exam_date is not None
        and a.exam_date == b.exam_date
        and a.slot_order_in_day is not None
        and b.slot_order_in_day is not None
        and a.slot_order_in_day != b.slot_order_in_day
    ):
        return "timeslot_pair_same_day_same_wave"

    return "generic_shared_item_pair"


def build_linking_and_dif_screen(
    params_df: pd.DataFrame,
    theta_df: pd.DataFrame,
    ns_meta_map: dict[str, NamespaceMeta],
) -> None:
    print("[5/8] Building anchor-based linking feasibility and DIF screen...")
    if params_df.empty:
        for name in [
            "shared_question_anchor_catalog.csv",
            "namespace_linking_feasibility.csv",
            "namespace_pair_linking_summary.csv",
            "namespace_pair_anchor_parameter_drift.csv",
            "namespace_pair_theta_linked_comparisons.csv",
            "dif_screen_pair_summary.csv",
        ]:
            pd.DataFrame().to_csv(OUT_DIR / name, index=False)
        return

    p = params_df.copy()
    p["question_title_norm"] = p["question_title_norm"].fillna("").map(normalize_title)
    p["problem_id"] = to_num(p["problem_id"]).astype("Int64")
    for c in ["a_discrimination", "b1_any_partial_threshold", "b2_full_threshold"]:
        p[c] = to_num(p[c])

    anchors = (
        p.groupby("question_title_norm", dropna=False)
        .agg(
            titles=("question_title", lambda s: sorted({str(x) for x in s if pd.notna(x)})[0] if any(pd.notna(s)) else None),
            namespaces=("namespace", lambda s: sorted({str(x) for x in s if pd.notna(x)})),
            namespace_count=("namespace", lambda s: len({str(x) for x in s if pd.notna(x)})),
            occurrences=("namespace", "count"),
        )
        .reset_index()
    )
    anchors["is_shared_across_namespaces"] = anchors["namespace_count"] >= 2
    anchors.to_csv(OUT_DIR / "shared_question_anchor_catalog.csv", index=False)

    # Union-find linkage graph of namespaces via shared anchors.
    uf = UnionFind()
    for _, row in anchors[anchors["is_shared_across_namespaces"]].iterrows():
        nss = row["namespaces"]
        if not isinstance(nss, list):
            continue
        for a, b in combinations(sorted(nss), 2):
            uf.union(a, b)

    component_members: dict[str, list[str]] = {}
    for ns in sorted(p["namespace"].dropna().astype(str).unique()):
        root = uf.find(ns)
        component_members.setdefault(root, []).append(ns)
    comp_id_map: dict[str, str] = {}
    for i, (root, members) in enumerate(sorted(component_members.items(), key=lambda kv: (-len(kv[1]), kv[0])), start=1):
        cid = f"C{i:02d}"
        for ns in members:
            comp_id_map[ns] = cid

    # Namespace feasibility summary.
    ns_anchor_counts = (
        p.groupby("namespace", dropna=False)["question_title_norm"]
        .agg(
            items_fitted="count",
            shared_anchor_items=lambda s: int(sum((anchors.set_index("question_title_norm").loc[list(s), "namespace_count"] >= 2).fillna(False))) if len(s) else 0,
            unique_anchor_titles=lambda s: len(set(str(x) for x in s if pd.notna(x))),
        )
        .reset_index()
    )
    ns_rows: list[dict[str, Any]] = []
    for rec in ns_anchor_counts.to_dict("records"):
        ns = str(rec["namespace"])
        m = ns_meta_map.get(ns)
        cid = comp_id_map.get(ns)
        comp_size = len(component_members.get(next((r for r, mem in component_members.items() if ns in mem), ""), [])) if cid else 1
        ns_rows.append(
            {
                **rec,
                "component_id": cid,
                "component_size": comp_size,
                "linkable_component": bool(comp_size and comp_size > 1),
                "term": (m.term if m else None),
                "wave": (m.wave if m else None),
                "slot_code": (m.slot_code if m else None),
                "variant": (m.variant if m else None),
            }
        )
    pd.DataFrame(ns_rows).sort_values(["component_size", "namespace"], ascending=[False, True]).to_csv(
        OUT_DIR / "namespace_linking_feasibility.csv", index=False
    )

    # Pairwise anchor-based linking transforms and parameter drift.
    ns_item = {}
    for ns, g in p.groupby("namespace", dropna=False):
        gg = g.copy().sort_values("problem_id")
        ns_item[str(ns)] = gg.set_index("question_title_norm", drop=False)

    pair_rows: list[dict[str, Any]] = []
    drift_rows: list[dict[str, Any]] = []
    theta_comp_rows: list[dict[str, Any]] = []

    all_namespaces = sorted(ns_item.keys())
    for ns_a, ns_b in combinations(all_namespaces, 2):
        ia = ns_item[ns_a]
        ib = ns_item[ns_b]
        shared = sorted(set(ia.index).intersection(set(ib.index)))
        shared = [s for s in shared if s]
        if not shared:
            continue

        ma = ns_meta_map.get(ns_a)
        mb = ns_meta_map.get(ns_b)
        pair_type = classify_namespace_pair_type(ma, mb) if (ma and mb) else "generic_shared_item_pair"

        # Threshold-pair based linear linking (B -> A): b_A ≈ A * b_B + B
        th_a: list[float] = []
        th_b: list[float] = []
        threshold_points = 0
        for qn in shared:
            ra = ia.loc[qn]
            rb = ib.loc[qn]
            for ca, cb in [("b1_any_partial_threshold", "b1_any_partial_threshold"), ("b2_full_threshold", "b2_full_threshold")]:
                va = pd.to_numeric(pd.Series([ra.get(ca)]), errors="coerce").iloc[0]
                vb = pd.to_numeric(pd.Series([rb.get(cb)]), errors="coerce").iloc[0]
                if pd.notna(va) and pd.notna(vb):
                    th_a.append(float(va))
                    th_b.append(float(vb))
                    threshold_points += 1

        link_feasible = threshold_points >= 2
        A = np.nan
        B = np.nan
        rmse_b = np.nan
        r2_b = np.nan
        if link_feasible:
            x = np.asarray(th_b, dtype=float)
            y = np.asarray(th_a, dtype=float)
            if np.nanstd(x) < 1e-9:
                A = 1.0
                B = float(np.nanmean(y - x))
            else:
                A, B = np.polyfit(x, y, 1)  # y = A x + B
            yhat = A * x + B
            rmse_b = float(np.sqrt(np.mean((y - yhat) ** 2)))
            ss_res = float(np.sum((y - yhat) ** 2))
            ss_tot = float(np.sum((y - np.mean(y)) ** 2))
            r2_b = (1.0 - ss_res / ss_tot) if ss_tot > 0 else np.nan

        # Anchor drift rows (after transform if feasible).
        for qn in shared:
            ra = ia.loc[qn]
            rb = ib.loc[qn]
            a_a = float(pd.to_numeric(pd.Series([ra.get("a_discrimination")]), errors="coerce").iloc[0])
            a_b = float(pd.to_numeric(pd.Series([rb.get("a_discrimination")]), errors="coerce").iloc[0])
            b1_a = pd.to_numeric(pd.Series([ra.get("b1_any_partial_threshold")]), errors="coerce").iloc[0]
            b2_a = pd.to_numeric(pd.Series([ra.get("b2_full_threshold")]), errors="coerce").iloc[0]
            b1_b = pd.to_numeric(pd.Series([rb.get("b1_any_partial_threshold")]), errors="coerce").iloc[0]
            b2_b = pd.to_numeric(pd.Series([rb.get("b2_full_threshold")]), errors="coerce").iloc[0]

            if link_feasible and pd.notna(A) and A != 0:
                a_b_linked = a_b / A if pd.notna(a_b) else np.nan
                b1_b_linked = (A * b1_b + B) if pd.notna(b1_b) else np.nan
                b2_b_linked = (A * b2_b + B) if pd.notna(b2_b) else np.nan
            else:
                a_b_linked = np.nan
                b1_b_linked = np.nan
                b2_b_linked = np.nan

            drift_rows.append(
                {
                    "namespace_a": ns_a,
                    "namespace_b": ns_b,
                    "pair_type": pair_type,
                    "question_title_norm": qn,
                    "question_title_a": ra.get("question_title"),
                    "question_title_b": rb.get("question_title"),
                    "problem_id_a": int(ra.get("problem_id")),
                    "problem_id_b": int(rb.get("problem_id")),
                    "a_a": a_a,
                    "a_b": a_b,
                    "a_b_linked_to_a_scale": a_b_linked,
                    "delta_a_linked": (a_a - a_b_linked) if pd.notna(a_b_linked) else np.nan,
                    "b1_a": b1_a,
                    "b1_b": b1_b,
                    "b1_b_linked_to_a_scale": b1_b_linked,
                    "delta_b1_linked": (b1_a - b1_b_linked) if pd.notna(b1_b_linked) else np.nan,
                    "b2_a": b2_a,
                    "b2_b": b2_b,
                    "b2_b_linked_to_a_scale": b2_b_linked,
                    "delta_b2_linked": (b2_a - b2_b_linked) if pd.notna(b2_b_linked) else np.nan,
                    "link_feasible": link_feasible,
                    "link_A": A,
                    "link_B": B,
                    "link_threshold_rmse": rmse_b,
                }
            )

        drift_df_pair = pd.DataFrame([r for r in drift_rows if r["namespace_a"] == ns_a and r["namespace_b"] == ns_b])
        med_abs_db1 = float(np.nanmedian(np.abs(to_num(drift_df_pair["delta_b1_linked"])))) if (link_feasible and not drift_df_pair.empty) else np.nan
        med_abs_db2 = float(np.nanmedian(np.abs(to_num(drift_df_pair["delta_b2_linked"])))) if (link_feasible and not drift_df_pair.empty) else np.nan
        med_abs_da = float(np.nanmedian(np.abs(to_num(drift_df_pair["delta_a_linked"])))) if (link_feasible and not drift_df_pair.empty) else np.nan
        large_drift_items = int(
            (
                (to_num(drift_df_pair.get("delta_b1_linked", pd.Series(dtype=float))).abs() > 0.75)
                | (to_num(drift_df_pair.get("delta_b2_linked", pd.Series(dtype=float))).abs() > 0.75)
            ).fillna(False).sum()
        ) if link_feasible else 0

        pair_rows.append(
            {
                "namespace_a": ns_a,
                "namespace_b": ns_b,
                "pair_type": pair_type,
                "term_a": (ma.term if ma else None),
                "term_b": (mb.term if mb else None),
                "wave_a": (ma.wave if ma else None),
                "wave_b": (mb.wave if mb else None),
                "start_time_a": (ma.start_time if ma else None),
                "start_time_b": (mb.start_time if mb else None),
                "n_shared_anchor_items": len(shared),
                "n_threshold_pairs_for_linking": threshold_points,
                "link_feasible_threshold_pairs_ge_2": link_feasible,
                "link_A_b_to_a": A,
                "link_B_b_to_a": B,
                "link_threshold_rmse": rmse_b,
                "link_threshold_r2": r2_b,
                "median_abs_delta_b1_linked": med_abs_db1,
                "median_abs_delta_b2_linked": med_abs_db2,
                "median_abs_delta_a_linked": med_abs_da,
                "anchor_items_large_threshold_drift_gt_0_75": large_drift_items,
            }
        )

        # Linked theta comparisons (all students + overlap on student_id) if link feasible.
        if link_feasible and pd.notna(A):
            ta = theta_df[theta_df["namespace"] == ns_a][["student_id", "theta"]].copy()
            tb = theta_df[theta_df["namespace"] == ns_b][["student_id", "theta"]].copy()
            if not ta.empty and not tb.empty:
                ta["theta"] = to_num(ta["theta"])
                tb["theta"] = to_num(tb["theta"])
                tb["theta_linked_to_a_scale"] = A * tb["theta"] + B
                overlap = ta.merge(tb[["student_id", "theta", "theta_linked_to_a_scale"]], on="student_id", how="inner", suffixes=("_a", "_b"))

                theta_comp_rows.append(
                    {
                        "namespace_a": ns_a,
                        "namespace_b": ns_b,
                        "pair_type": pair_type,
                        "link_feasible": True,
                        "n_shared_anchor_items": len(shared),
                        "students_a": int(len(ta)),
                        "students_b": int(len(tb)),
                        "students_overlap_same_id": int(len(overlap)),
                        "theta_mean_a": float(np.nanmean(ta["theta"])),
                        "theta_mean_b": float(np.nanmean(tb["theta"])),
                        "theta_mean_b_linked_to_a_scale": float(np.nanmean(tb["theta_linked_to_a_scale"])),
                        "theta_median_a": float(np.nanmedian(ta["theta"])),
                        "theta_median_b_linked_to_a_scale": float(np.nanmedian(tb["theta_linked_to_a_scale"])),
                        "theta_overlap_mean_delta_bminus_a": (
                            float(np.nanmean(overlap["theta_linked_to_a_scale"] - overlap["theta_a"])) if len(overlap) else np.nan
                        ),
                        "theta_overlap_median_delta_bminus_a": (
                            float(np.nanmedian(overlap["theta_linked_to_a_scale"] - overlap["theta_a"])) if len(overlap) else np.nan
                        ),
                        "theta_overlap_corr": (
                            float(np.corrcoef(overlap["theta_a"], overlap["theta_linked_to_a_scale"])[0, 1])
                            if len(overlap) >= 3 and np.nanstd(overlap["theta_a"]) > 0 and np.nanstd(overlap["theta_linked_to_a_scale"]) > 0
                            else np.nan
                        ),
                        "link_A_b_to_a": A,
                        "link_B_b_to_a": B,
                        "link_threshold_rmse": rmse_b,
                    }
                )

    pair_df = pd.DataFrame(pair_rows)
    drift_df = pd.DataFrame(drift_rows)
    theta_comp_df = pd.DataFrame(theta_comp_rows)

    if not pair_df.empty:
        pair_df.sort_values(["pair_type", "n_shared_anchor_items", "namespace_a", "namespace_b"], ascending=[True, False, True, True], inplace=True)
    if not drift_df.empty:
        drift_df.sort_values(["pair_type", "namespace_a", "namespace_b", "question_title_a"], inplace=True)
    if not theta_comp_df.empty:
        theta_comp_df.sort_values(["pair_type", "namespace_a", "namespace_b"], inplace=True)

    pair_df.to_csv(OUT_DIR / "namespace_pair_linking_summary.csv", index=False)
    drift_df.to_csv(OUT_DIR / "namespace_pair_anchor_parameter_drift.csv", index=False)
    theta_comp_df.to_csv(OUT_DIR / "namespace_pair_theta_linked_comparisons.csv", index=False)

    # DIF screen summary (anchor-based parameter drift proxy, not formal DIF test).
    if pair_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "dif_screen_pair_summary.csv", index=False)
    else:
        dif = (
            pair_df.groupby("pair_type", dropna=False)
            .agg(
                pairs=("namespace_a", "count"),
                link_feasible_pairs=("link_feasible_threshold_pairs_ge_2", "sum"),
                median_shared_anchor_items=("n_shared_anchor_items", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
                median_link_threshold_rmse=("link_threshold_rmse", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                median_abs_delta_b1_linked=("median_abs_delta_b1_linked", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                median_abs_delta_b2_linked=("median_abs_delta_b2_linked", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                median_abs_delta_a_linked=("median_abs_delta_a_linked", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
                pairs_with_large_anchor_drift=("anchor_items_large_threshold_drift_gt_0_75", lambda s: int((to_num(pd.Series(s)).fillna(0) > 0).sum())),
            )
            .reset_index()
            .sort_values(["link_feasible_pairs", "pairs"], ascending=[False, False])
        )
        dif["pct_link_feasible"] = np.where(dif["pairs"] > 0, (100.0 * dif["link_feasible_pairs"] / dif["pairs"]).round(2), np.nan)
        dif.to_csv(OUT_DIR / "dif_screen_pair_summary.csv", index=False)

    # Optional wave/variant linked theta subsets for easier docs.
    if not theta_comp_df.empty:
        theta_comp_df[theta_comp_df["pair_type"] == "wave_pair_same_slot_index"].to_csv(
            OUT_DIR / "theta_linked_wave_pair_comparisons.csv",
            index=False,
        )
        theta_comp_df[theta_comp_df["pair_type"] == "variant_pair_same_slot"].to_csv(
            OUT_DIR / "theta_linked_variant_pair_comparisons.csv",
            index=False,
        )
    else:
        pd.DataFrame().to_csv(OUT_DIR / "theta_linked_wave_pair_comparisons.csv", index=False)
        pd.DataFrame().to_csv(OUT_DIR / "theta_linked_variant_pair_comparisons.csv", index=False)


def build_theta_and_tif_summaries(fit_df: pd.DataFrame, theta_df: pd.DataFrame) -> None:
    print("[6/8] Building theta and TIF summary tables...")
    if fit_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "tif_low_ability_flags.csv", index=False)
        pd.DataFrame().to_csv(OUT_DIR / "theta_distribution_by_namespace_track.csv", index=False)
        return

    tif_flags = fit_df.copy()
    tif_flags["info_low_to_mid_ratio"] = to_num(tif_flags["info_low_to_mid_ratio"])
    tif_flags["flag_low_ability_blind_ratio_lt_0_5"] = tif_flags["info_low_to_mid_ratio"] < 0.5
    tif_flags["flag_mid_peak_abs_theta_le_0_75"] = to_num(tif_flags["info_peak_theta"]).abs() <= 0.75
    tif_flags["flag_peak_high_ability_theta_gt_1"] = to_num(tif_flags["info_peak_theta"]) > 1.0
    tif_flags[
        [
            "namespace",
            "term",
            "wave",
            "status",
            "students_fitted",
            "items_fitted",
            "info_peak_theta",
            "info_peak_value",
            "info_low_to_mid_ratio",
            "info_mean_low_theta_le_neg1",
            "info_mean_mid_abs_le_0_5",
            "flag_low_ability_blind_ratio_lt_0_5",
            "flag_mid_peak_abs_theta_le_0_75",
            "flag_peak_high_ability_theta_gt_1",
        ]
    ].sort_values(["status", "namespace"]).to_csv(OUT_DIR / "tif_low_ability_flags.csv", index=False)

    if theta_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "theta_distribution_by_namespace_track.csv", index=False)
        return

    th = theta_df.copy()
    th["theta"] = to_num(th["theta"])
    qrows = pd.read_csv(OUT_DIR / "question_level_grm_rows.csv", low_memory=False)[["namespace", "student_id", "track", "term", "wave"]].drop_duplicates()
    th = th.merge(qrows, on=["namespace", "student_id"], how="left", suffixes=("", "_row"))
    theta_sum = (
        th.groupby(["namespace", "term", "wave", "track"], dropna=False)
        .agg(
            students=("student_id", "count"),
            theta_mean=("theta", "mean"),
            theta_sd=("theta", lambda s: float(np.nanstd(to_num(s), ddof=1)) if len(s) > 1 else np.nan),
            theta_p10=("theta", lambda s: float(np.nanpercentile(to_num(s), 10)) if pd.Series(s).notna().any() else np.nan),
            theta_p50=("theta", lambda s: float(np.nanpercentile(to_num(s), 50)) if pd.Series(s).notna().any() else np.nan),
            theta_p90=("theta", lambda s: float(np.nanpercentile(to_num(s), 90)) if pd.Series(s).notna().any() else np.nan),
        )
        .reset_index()
        .sort_values(["namespace", "track"])
    )
    theta_sum.to_csv(OUT_DIR / "theta_distribution_by_namespace_track.csv", index=False)


def build_high_level_summary_tables(fit_df: pd.DataFrame, param_df: pd.DataFrame) -> None:
    print("[7/8] Writing high-level IRT summary tables...")
    if fit_df.empty:
        pd.DataFrame().to_csv(OUT_DIR / "irt_summary_overall.csv", index=False)
        return

    fit_ok = fit_df[fit_df["status"] == "fit_ok"].copy()
    param_ok = param_df.copy()

    row = {
        "namespaces_total": int(len(fit_df)),
        "namespaces_fit_ok": int(len(fit_ok)),
        "namespaces_fit_failed": int((fit_df["status"] != "fit_ok").sum()),
        "median_students_fitted": float(np.nanmedian(to_num(fit_ok["students_fitted"]))) if len(fit_ok) else np.nan,
        "median_items_fitted": float(np.nanmedian(to_num(fit_ok["items_fitted"]))) if len(fit_ok) else np.nan,
        "median_info_peak_theta": float(np.nanmedian(to_num(fit_ok["info_peak_theta"]))) if len(fit_ok) else np.nan,
        "median_info_low_to_mid_ratio": float(np.nanmedian(to_num(fit_ok["info_low_to_mid_ratio"]))) if len(fit_ok) else np.nan,
        "questions_fitted_total": int(len(param_ok)),
        "low_discrimination_questions_a_lt_0_5": int(boolify_series(param_ok["flag_low_discrimination"]).sum()) if ("flag_low_discrimination" in param_ok.columns and not param_ok.empty) else 0,
    }
    pd.DataFrame([row]).to_csv(OUT_DIR / "irt_summary_overall.csv", index=False)

    by_term_wave = (
        fit_df.groupby(["term", "wave", "status"], dropna=False)
        .agg(
            namespaces=("namespace", "count"),
            median_students_fitted=("students_fitted", lambda s: float(np.nanmedian(to_num(s))) if len(s) else np.nan),
            median_info_peak_theta=("info_peak_theta", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
            median_info_low_to_mid_ratio=("info_low_to_mid_ratio", lambda s: float(np.nanmedian(to_num(s))) if pd.Series(s).notna().any() else np.nan),
        )
        .reset_index()
        .sort_values(["term", "wave", "status"])
    )
    by_term_wave.to_csv(OUT_DIR / "namespace_grm_fit_summary_by_term_wave.csv", index=False)


def write_manifest() -> None:
    files: list[dict[str, Any]] = []
    for p in sorted(OUT_DIR.rglob("*")):
        if p.is_file():
            try:
                size = p.stat().st_size
            except Exception:
                size = None
            files.append({"path": str(p.relative_to(OUT_DIR)), "bytes": size})
    pd.DataFrame(files).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def main() -> None:
    make_dirs()
    conn = make_conn()
    try:
        rows, q_metrics, schedule, ns_meta = load_inputs()
        _ = schedule  # loaded for namespace metadata generation side effect
        grm_rows = build_question_level_rows(rows, q_metrics)
        fit_df, cov_df, params_df, theta_df = fit_all_namespaces_grm(grm_rows)
        _ = cov_df
        params_flagged_df = build_question_parameter_analysis(params_df)
        build_linking_and_dif_screen(params_flagged_df, theta_df, ns_meta)
        build_theta_and_tif_summaries(fit_df, theta_df)
        build_high_level_summary_tables(fit_df, params_flagged_df)
        print("[8/8] Writing output manifest...")
        write_manifest()
        print("Done. Outputs written to analysis/psychometric_irt/")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
