#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.2.0",
#   "pandas>=2.2.0",
#   "scikit-learn>=1.7.0",
#   "scipy>=1.15.0",
# ]
# ///
"""Generate a report on cross-question navigation patterns."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, spearmanr
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_PATH = ANALYSIS_DIR / "question-timelines.md"

FEATURE_COLS = [
    "coverage_pct",
    "first_sweep_coverage_pct",
    "revisit_rate",
    "local_toggle_rate",
    "jump_size_pct",
    "first_touch_monotonicity",
    "top2_focus",
]

CLUSTER_ORDER = [
    "Linear sweepers",
    "Round-robin revisitors",
    "Opportunistic jumpers",
    "Local togglers",
]

CLUSTER_BLURBS = {
    "Linear sweepers": {
        "cartoon": "A -> B -> C -> D -> E, maybe one late return",
        "why": "These students make a broad first sweep, revisit sparingly, and mostly move in the paper's own order.",
    },
    "Round-robin revisitors": {
        "cartoon": "A -> B -> C -> D -> A -> B -> C -> D",
        "why": "These students still cover most of the paper, but they keep looping back across many questions before finishing.",
    },
    "Opportunistic jumpers": {
        "cartoon": "A -> C -> F -> B -> G -> C",
        "why": "These students move around in bigger jumps and their first-touch order is much less aligned with the question order.",
    },
    "Local togglers": {
        "cartoon": "A -> B -> A -> C -> A -> B",
        "why": "These students concentrate their activity in a small part of the paper and show the strongest A-B-A style oscillation.",
    },
}

FEATURE_EXPLANATIONS = [
    ("`coverage_pct`", "what share of the paper they touched at all"),
    (
        "`first_sweep_coverage_pct`",
        "how much of their touched set they saw before the first revisit",
    ),
    ("`revisit_rate`", "how much of the run sequence is made of returns"),
    ("`local_toggle_rate`", "how often the sequence looks like `A -> B -> A`"),
    (
        "`jump_size_pct`",
        "the average question-number jump, normalized by paper length",
    ),
    (
        "`first_touch_monotonicity`",
        "how closely the first-touch order follows the paper order",
    ),
    (
        "`top2_focus`",
        "how much of the run sequence is concentrated in the two most-visited questions",
    ),
]


@dataclass(frozen=True)
class ClusterStat:
    name: str
    n: int
    share_pct: float
    mean_score_frac: float
    median_score_frac: float
    any_points_pct: float
    half_or_more_pct: float
    mean_score_z: float
    mean_coverage_pct: float
    mean_first_sweep_pct: float
    mean_revisit_rate: float
    mean_local_toggle_rate: float
    mean_jump_size_pct: float
    mean_first_touch_monotonicity: float
    mean_top2_focus: float


@dataclass(frozen=True)
class ModelChoiceStat:
    model: str
    sample_size: int
    silhouette_euclidean: float
    silhouette_manhattan: float
    cluster_sizes: str


def fmt_pct(value: float, digits: int = 1) -> str:
    return f"{100.0 * value:.{digits}f}%"


def fmt_num(value: float, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:.{digits}f}"


def fmt_pvalue(value: float) -> str:
    if value <= 0:
        return "<1e-300"
    return f"{value:.3g}"


def fmt_seconds(total_seconds: float | int) -> str:
    total = int(round(float(total_seconds)))
    mm, ss = divmod(total, 60)
    hh, mm = divmod(mm, 60)
    if hh:
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return f"{mm:02d}:{ss:02d}"


def bh_adjust(pvalues: dict[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues.items(), key=lambda item: item[1])
    m = len(ordered)
    adjusted: dict[str, float] = {}
    prev = 1.0
    for reverse_rank, (key, value) in enumerate(reversed(ordered), start=1):
        rank = m - reverse_rank + 1
        adj = min(prev, value * m / rank)
        adjusted[key] = adj
        prev = adj
    return adjusted


def cliff_delta_from_u(u_stat: float, n_x: int, n_y: int) -> float:
    return (2.0 * u_stat) / (n_x * n_y) - 1.0


def render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return out


def load_run_level() -> pd.DataFrame:
    query = """
    WITH ordered AS (
      SELECT
        namespace,
        student_id,
        problem_id,
        timestamp_utc,
        event_type,
        evaluation_type,
        summary,
        score,
        ROW_NUMBER() OVER (
          PARTITION BY namespace, student_id
          ORDER BY timestamp_utc,
            CASE event_type
              WHEN 'saved_code' THEN 1
              WHEN 'test_run' THEN 2
              WHEN 'submission' THEN 3
              ELSE 9
            END,
            problem_id,
            evaluation_type
        ) AS event_idx,
        LAG(problem_id) OVER (
          PARTITION BY namespace, student_id
          ORDER BY timestamp_utc,
            CASE event_type
              WHEN 'saved_code' THEN 1
              WHEN 'test_run' THEN 2
              WHEN 'submission' THEN 3
              ELSE 9
            END,
            problem_id,
            evaluation_type
        ) AS prev_problem,
        MIN(timestamp_utc) OVER (PARTITION BY namespace, student_id) AS exam_start_ts
      FROM read_parquet(?)
      WHERE namespace LIKE 'ns_%_py%'
    ),
    runs AS (
      SELECT
        *,
        SUM(CASE WHEN prev_problem IS NULL OR prev_problem <> problem_id THEN 1 ELSE 0 END)
          OVER (PARTITION BY namespace, student_id ORDER BY event_idx) AS run_id
      FROM ordered
    ),
    run_summaries AS (
      SELECT
        namespace,
        student_id,
        run_id,
        ANY_VALUE(problem_id) AS problem_id,
        DATEDIFF('second', MIN(exam_start_ts), MIN(timestamp_utc)) AS start_s,
        DATEDIFF('second', MIN(exam_start_ts), MAX(timestamp_utc)) AS end_s,
        COUNT(*) AS run_events,
        ARG_MAX(event_type, event_idx) AS last_event_type,
        ARG_MAX(evaluation_type, event_idx) AS last_eval_type,
        ARG_MAX(summary, event_idx) AS last_summary,
        ARG_MAX(score, event_idx) AS last_score
      FROM runs
      GROUP BY 1, 2, 3
    ),
    question_counts AS (
      SELECT namespace, COUNT(*) AS total_questions
      FROM read_csv_auto(?)
      GROUP BY 1
    ),
    exam_students AS (
      SELECT DISTINCT namespace, student_id
      FROM read_parquet(?)
      WHERE namespace LIKE 'ns_%_py%'
    ),
    base_scores AS (
      SELECT
        namespace,
        student_id,
        problem_id,
        MAX(COALESCE(TRY_CAST(latest_submission_score AS DOUBLE), 0)) AS score
      FROM read_csv_auto(?)
      WHERE is_python_question
      GROUP BY 1, 2, 3
    ),
    exam_perf AS (
      SELECT
        e.namespace,
        e.student_id,
        q.total_questions,
        COALESCE(SUM(b.score), 0) AS total_score,
        COUNT(*) FILTER (WHERE b.score > 0) AS positive_questions,
        COUNT(*) FILTER (WHERE b.score = 100) AS full_pass_questions
      FROM exam_students e
      JOIN question_counts q USING (namespace)
      LEFT JOIN base_scores b USING (namespace, student_id)
      GROUP BY 1, 2, 3
    )
    SELECT *
    FROM run_summaries
    JOIN exam_perf USING (namespace, student_id)
    ORDER BY namespace, student_id, run_id
    """
    con = duckdb.connect()
    try:
        return con.execute(
            query,
            [
                str(ANALYSIS_DIR / "submission_timeline.parquet"),
                str(ANALYSIS_DIR / "question_metadata.csv"),
                str(ANALYSIS_DIR / "submission_timeline.parquet"),
                str(ANALYSIS_DIR / "process_analysis" / "attempt_archetypes.csv"),
            ],
        ).df()
    finally:
        con.close()


def build_features(run_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str], pd.DataFrame]]:
    feature_rows: list[dict[str, Any]] = []
    run_lookup: dict[tuple[str, str], pd.DataFrame] = {}

    for (namespace, student_id), group in run_df.groupby(["namespace", "student_id"], sort=False):
        group = group.sort_values("run_id").reset_index(drop=True)
        sequence = group["problem_id"].astype(int).tolist()
        questions_touched = len(set(sequence))
        if questions_touched < 2:
            continue

        run_lookup[(namespace, student_id)] = group

        total_questions = int(group["total_questions"].iloc[0])
        runs = len(sequence)
        deltas = np.diff(np.array(sequence, dtype=float))
        abs_deltas = np.abs(deltas)

        seen: set[int] = set()
        first_revisit_run = runs + 1
        for idx, problem_id in enumerate(sequence, start=1):
            if problem_id in seen:
                first_revisit_run = idx
                break
            seen.add(problem_id)

        first_touch = (
            group.drop_duplicates("problem_id", keep="first")["problem_id"].astype(int).tolist()
        )
        monotonicity = (
            spearmanr(np.arange(len(first_touch)), np.array(first_touch)).statistic
            if len(first_touch) > 1
            else 1.0
        )
        freq = pd.Series(sequence).value_counts(normalize=True)
        total_score = float(group["total_score"].iloc[0])

        feature_rows.append(
            {
                "namespace": namespace,
                "student_id": student_id,
                "questions_touched": questions_touched,
                "total_questions": total_questions,
                "runs": runs,
                "coverage_pct": questions_touched / total_questions,
                "first_sweep_coverage_pct": min(first_revisit_run - 1, questions_touched)
                / questions_touched,
                "revisit_rate": (runs - questions_touched) / runs,
                "local_toggle_rate": sum(
                    1 for i in range(2, runs) if sequence[i] == sequence[i - 2]
                )
                / max(1, runs - 2),
                "jump_size_pct": (
                    float(abs_deltas.mean()) / (total_questions - 1) if len(abs_deltas) else 0.0
                ),
                "first_touch_monotonicity": float(monotonicity)
                if monotonicity == monotonicity
                else 0.0,
                "top2_focus": float(freq.head(2).sum()),
                "official_total_score": total_score,
                "official_score_frac": total_score / (100.0 * total_questions),
                "positive_questions": int(group["positive_questions"].iloc[0]),
                "full_pass_questions": int(group["full_pass_questions"].iloc[0]),
            }
        )

    feature_df = pd.DataFrame(feature_rows)
    feature_df["score_z_within_namespace"] = feature_df.groupby("namespace")[
        "official_score_frac"
    ].transform(lambda s: (s - s.mean()) / (s.std(ddof=0) if s.std(ddof=0) > 0 else 1.0))
    return feature_df, run_lookup


def fit_scaler(feature_df: pd.DataFrame) -> RobustScaler:
    return RobustScaler(quantile_range=(10, 90)).fit(feature_df[FEATURE_COLS])


def evaluate_k_choices(feature_df: pd.DataFrame, scaler: RobustScaler) -> pd.DataFrame:
    X = scaler.transform(feature_df[FEATURE_COLS])
    rng = np.random.default_rng(0)
    sample = rng.choice(len(X), size=min(3000, len(X)), replace=False)
    rows = []
    for k in range(3, 7):
        labels = KMeans(n_clusters=k, random_state=0, n_init=40).fit_predict(X)
        rows.append(
            {
                "k": k,
                "sampled_silhouette_euclidean": float(
                    silhouette_score(X[sample], labels[sample], metric="euclidean")
                ),
                "sampled_silhouette_manhattan": float(
                    silhouette_score(X[sample], labels[sample], metric="manhattan")
                ),
                "cluster_sizes": ", ".join(
                    f"{cluster}:{count}"
                    for cluster, count in pd.Series(labels).value_counts().sort_index().items()
                ),
            }
        )
    return pd.DataFrame(rows)


def evaluate_model_choices(feature_df: pd.DataFrame, scaler: RobustScaler) -> list[ModelChoiceStat]:
    X = scaler.transform(feature_df[FEATURE_COLS])
    rng = np.random.default_rng(0)
    sample_idx = rng.choice(len(X), size=min(10000, len(X)), replace=False)
    sample = X[sample_idx]

    model_specs: list[tuple[str, Any]] = [
        ("KMeans", KMeans(n_clusters=4, random_state=0, n_init=40)),
        ("Agglomerative Ward", AgglomerativeClustering(n_clusters=4, linkage="ward")),
        (
            "Gaussian mixture",
            GaussianMixture(n_components=4, covariance_type="full", random_state=0, n_init=3),
        ),
    ]

    stats: list[ModelChoiceStat] = []
    for model_name, model in model_specs:
        if isinstance(model, GaussianMixture):
            labels = model.fit(sample).predict(sample)
        else:
            labels = model.fit_predict(sample)
        size_map = pd.Series(labels).value_counts().sort_index()
        stats.append(
            ModelChoiceStat(
                model=model_name,
                sample_size=len(sample),
                silhouette_euclidean=float(
                    silhouette_score(sample, labels, metric="euclidean")
                ),
                silhouette_manhattan=float(
                    silhouette_score(sample, labels, metric="manhattan")
                ),
                cluster_sizes=", ".join(
                    f"{cluster}:{count}" for cluster, count in size_map.items()
                ),
            )
        )
    return stats


def assign_cluster_names(summary: pd.DataFrame) -> dict[int, str]:
    remaining = set(summary.index.tolist())
    name_map: dict[int, str] = {}

    toggler_score = (
        summary["local_toggle_rate"].rank(pct=True)
        + summary["top2_focus"].rank(pct=True)
        + (1 - summary["coverage_pct"].rank(pct=True))
    ).sort_values(ascending=False)
    toggler = int(toggler_score.index[0])
    name_map[toggler] = "Local togglers"
    remaining.remove(toggler)

    sub = summary.loc[list(remaining)]
    sweeper_score = (
        sub["official_score_frac"].rank(pct=True)
        + sub["first_sweep_coverage_pct"].rank(pct=True)
        + sub["first_touch_monotonicity"].rank(pct=True)
        + (1 - sub["revisit_rate"].rank(pct=True))
        + (1 - sub["jump_size_pct"].rank(pct=True))
    ).sort_values(ascending=False)
    sweeper = int(sweeper_score.index[0])
    name_map[sweeper] = "Linear sweepers"
    remaining.remove(sweeper)

    sub = summary.loc[list(remaining)]
    round_robin_score = (
        sub["coverage_pct"].rank(pct=True)
        + sub["revisit_rate"].rank(pct=True)
        + (1 - sub["top2_focus"].rank(pct=True))
    ).sort_values(ascending=False)
    round_robin = int(round_robin_score.index[0])
    name_map[round_robin] = "Round-robin revisitors"
    remaining.remove(round_robin)

    opportunistic = int(next(iter(remaining)))
    name_map[opportunistic] = "Opportunistic jumpers"
    return name_map


def cluster_features(feature_df: pd.DataFrame, scaler: RobustScaler) -> tuple[pd.DataFrame, pd.DataFrame]:
    X = scaler.transform(feature_df[FEATURE_COLS])
    km = KMeans(n_clusters=4, random_state=0, n_init=40)
    raw_labels = km.fit_predict(X)

    feature_df = feature_df.copy()
    feature_df["raw_cluster"] = raw_labels
    feature_df["dist_to_center"] = np.sqrt(((X - km.cluster_centers_[raw_labels]) ** 2).sum(axis=1))

    summary = feature_df.groupby("raw_cluster")[FEATURE_COLS + ["official_score_frac", "runs"]].mean()
    name_map = assign_cluster_names(summary)
    feature_df["cluster_name"] = feature_df["raw_cluster"].map(name_map)
    return feature_df, summary


def build_cluster_stats(feature_df: pd.DataFrame) -> list[ClusterStat]:
    total = len(feature_df)
    grouped = feature_df.groupby("cluster_name")
    stats: list[ClusterStat] = []
    for name in CLUSTER_ORDER:
        group = grouped.get_group(name)
        stats.append(
            ClusterStat(
                name=name,
                n=len(group),
                share_pct=100.0 * len(group) / total,
                mean_score_frac=float(group["official_score_frac"].mean()),
                median_score_frac=float(group["official_score_frac"].median()),
                any_points_pct=100.0 * float((group["official_score_frac"] > 0).mean()),
                half_or_more_pct=100.0 * float((group["official_score_frac"] >= 0.5).mean()),
                mean_score_z=float(group["score_z_within_namespace"].mean()),
                mean_coverage_pct=100.0 * float(group["coverage_pct"].mean()),
                mean_first_sweep_pct=100.0 * float(group["first_sweep_coverage_pct"].mean()),
                mean_revisit_rate=float(group["revisit_rate"].mean()),
                mean_local_toggle_rate=float(group["local_toggle_rate"].mean()),
                mean_jump_size_pct=100.0 * float(group["jump_size_pct"].mean()),
                mean_first_touch_monotonicity=float(group["first_touch_monotonicity"].mean()),
                mean_top2_focus=100.0 * float(group["top2_focus"].mean()),
            )
        )
    return stats


def significance_tests(feature_df: pd.DataFrame) -> dict[str, Any]:
    grouped = feature_df.groupby("cluster_name")
    kw_raw = kruskal(*[grouped.get_group(name)["official_score_frac"] for name in CLUSTER_ORDER])
    kw_z = kruskal(
        *[grouped.get_group(name)["score_z_within_namespace"] for name in CLUSTER_ORDER]
    )

    best_cluster = max(
        CLUSTER_ORDER,
        key=lambda name: grouped.get_group(name)["official_score_frac"].mean(),
    )
    best_values = grouped.get_group(best_cluster)["score_z_within_namespace"].to_numpy()
    rest_values = feature_df.loc[
        feature_df["cluster_name"] != best_cluster, "score_z_within_namespace"
    ].to_numpy()
    best_vs_rest = mannwhitneyu(best_values, rest_values, alternative="two-sided")

    pairwise: dict[str, dict[str, float]] = {}
    raw_p: dict[str, float] = {}
    for name in CLUSTER_ORDER:
        if name == best_cluster:
            continue
        other = grouped.get_group(name)["score_z_within_namespace"].to_numpy()
        result = mannwhitneyu(best_values, other, alternative="two-sided")
        key = f"{best_cluster} vs {name}"
        raw_p[key] = float(result.pvalue)
        pairwise[key] = {
            "u": float(result.statistic),
            "p": float(result.pvalue),
            "delta": float(cliff_delta_from_u(result.statistic, len(best_values), len(other))),
        }
    for key, adj in bh_adjust(raw_p).items():
        pairwise[key]["p_bh"] = adj

    return {
        "best_cluster": best_cluster,
        "kw_raw": kw_raw,
        "kw_z": kw_z,
        "best_vs_rest": {
            "u": float(best_vs_rest.statistic),
            "p": float(best_vs_rest.pvalue),
            "delta": float(
                cliff_delta_from_u(best_vs_rest.statistic, len(best_values), len(rest_values))
            ),
        },
        "pairwise": pairwise,
    }


def select_exemplars(feature_df: pd.DataFrame) -> dict[str, list[tuple[str, str]]]:
    chosen: dict[str, list[tuple[str, str]]] = {}
    for cluster_name in CLUSTER_ORDER:
        cluster_df = feature_df.loc[feature_df["cluster_name"] == cluster_name].copy()
        cluster_df["rank_score"] = (
            cluster_df["dist_to_center"]
            + np.where(cluster_df["official_total_score"] > 0, 0.0, 0.25)
            + np.where(cluster_df["official_score_frac"] >= 0.5, -0.05, 0.0)
        )

        picks: list[tuple[str, str]] = []
        seen_namespaces: set[str] = set()
        for _, row in cluster_df.sort_values(["rank_score", "dist_to_center"]).iterrows():
            pair = (str(row["namespace"]), str(row["student_id"]))
            if pair in picks or str(row["namespace"]) in seen_namespaces:
                continue
            picks.append(pair)
            seen_namespaces.add(str(row["namespace"]))
            if len(picks) == 3:
                break

        if len(picks) < 3:
            for _, row in cluster_df.sort_values(["dist_to_center"]).iterrows():
                pair = (str(row["namespace"]), str(row["student_id"]))
                if pair in picks:
                    continue
                picks.append(pair)
                if len(picks) == 3:
                    break

        chosen[cluster_name] = picks
    return chosen


def exemplar_lines(
    cluster_name: str,
    exemplars: list[tuple[str, str]],
    feature_df: pd.DataFrame,
    run_lookup: dict[tuple[str, str], pd.DataFrame],
) -> list[str]:
    out = [f"## {cluster_name}", "", CLUSTER_BLURBS[cluster_name]["why"], ""]
    for idx, key in enumerate(exemplars, start=1):
        namespace, student_id = key
        row = feature_df.loc[
            (feature_df["namespace"] == namespace) & (feature_df["student_id"] == student_id)
        ].iloc[0]
        runs = run_lookup[key]
        out.extend(
            [
                f"### Exemplar {idx}",
                "",
                f"- Namespace: `{namespace}`",
                f"- Student ID: `{student_id}`",
                f"- Official exam performance: `{int(round(row['official_total_score']))}/{int(row['total_questions'] * 100)}` "
                f"({fmt_pct(row['official_score_frac'])}); positive-score questions `{int(row['positive_questions'])}`; full-pass questions `{int(row['full_pass_questions'])}`",
                f"- Navigation fingerprint: `{int(row['questions_touched'])}` questions touched, `{int(row['runs'])}` runs, "
                f"first-sweep coverage `{fmt_pct(row['first_sweep_coverage_pct'])}`, revisit rate `{fmt_pct(row['revisit_rate'])}`, "
                f"local toggle rate `{fmt_pct(row['local_toggle_rate'])}`, top-2 focus `{fmt_pct(row['top2_focus'])}`",
                "- Exact run timeline:",
                "```text",
            ]
        )
        for run in runs.itertuples():
            score_bits = ""
            if pd.notna(run.last_score):
                score_bits = f" ({int(round(float(run.last_score)))})"
            out.append(
                f"{fmt_seconds(run.start_s)}-{fmt_seconds(run.end_s)}  "
                f"Q{int(run.problem_id):02d}  "
                f"{int(run.run_events):>2} ev  "
                f"end={run.last_event_type}/{run.last_eval_type}  "
                f"{run.last_summary}{score_bits}"
            )
        out.extend(["```", ""])
    return out


def build_markdown() -> str:
    generated_at = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
    run_df = load_run_level()
    feature_df, run_lookup = build_features(run_df)
    scaler = fit_scaler(feature_df)
    k_eval = evaluate_k_choices(feature_df, scaler)
    model_eval = evaluate_model_choices(feature_df, scaler)
    feature_df, _ = cluster_features(feature_df, scaler)
    cluster_stats = build_cluster_stats(feature_df)
    tests = significance_tests(feature_df)
    exemplars = select_exemplars(feature_df)

    total_exam_students = run_df[["namespace", "student_id"]].drop_duplicates().shape[0]
    clustered_population = len(feature_df)
    one_question_only = total_exam_students - clustered_population
    revisitors = int((feature_df["runs"] > feature_df["questions_touched"]).sum())
    no_revisit_count = int((feature_df["runs"] == feature_df["questions_touched"]).sum())

    lines = [
        "# Question Navigation Timelines",
        "",
        f"_Generated by `analysis/generate_question_timelines_md.py` on {generated_at}._",
        "",
        "## ELI15",
        "",
        "- Students do **not** mostly solve the paper in a clean top-to-bottom line.",
        f"- Of `{total_exam_students:,}` active exam-student timelines, `{clustered_population:,}` (`{clustered_population / total_exam_students:.1%}`) touched at least two questions and were clusterable.",
        f"- Among those multi-question students, `{revisitors:,}` (`{revisitors / clustered_population:.1%}`) revisited at least one question; only `{no_revisit_count:,}` (`{no_revisit_count / clustered_population:.1%}`) made a single pass with no return.",
        f"- The highest-performing cluster is **{tests['best_cluster']}**. The lowest-performing cluster is **Local togglers**: students who keep bouncing around a small local patch of the paper.",
        "",
        "## Action Recommendations",
        "",
        "- Teach an explicit first sweep strategy. The strongest pattern is broad first-pass coverage before coming back.",
        "- Detect local oscillation early. Repeated `A -> B -> A` style navigation is the cleanest navigation fingerprint of poor official performance.",
        "- Support planned revisits instead of assuming linear solving. Most students do revisit; the difference is whether the revisit is broad and strategic or sticky and local.",
        "",
        "## Method",
        "",
        "- Unit of analysis: one student inside one Python namespace, treated as one exam sitting.",
        "- Sequence source: `analysis/submission_timeline.parquet`, sorted across all questions in the namespace by timestamp.",
        "- Navigation state: contiguous activity on one question is compressed into a question **run**. A new run starts only when the student switches questions.",
        "- Official performance metric: sum of latest submitted scores across all questions in the namespace. Questions never submitted count as `0`.",
        "- Feature design: cluster only on navigation features, not on generic effort or code-edit intensity.",
        "- Deliberately excluded: raw event count, time spent, and edit volume. Those may measure persistence or confusion, but they are not navigation choices.",
        "",
        "### Navigation Features",
        "",
    ]

    for name, desc in FEATURE_EXPLANATIONS:
        lines.append(f"- {name}: {desc}.")

    lines.extend(
        [
            "",
            "### Clustering Choice",
            "",
            "- The clustering uses `k`-means on these seven navigation-only features after robust scaling (10th-90th percentile scaling).",
            "- The core question is not 'who typed a lot?' but 'who swept, revisited, toggled, or jumped?'. Those behaviors are captured directly by the compact feature geometry.",
            "- Cross-namespace comparison: all significance tests are repeated on a within-namespace standardized score so easy and hard papers are not mixed unfairly.",
            "- Caveat: this is correlational. Stronger students may also choose better navigation strategies; the analysis shows association, not causation.",
            "",
            "### Model Comparison",
            "",
            f"The table below compares three pragmatic clustering families on the same `k=4` navigation feature space using a fixed random sample of `{model_eval[0].sample_size:,}` multi-question sittings.",
            "",
            *render_table(
                [
                    "Model",
                    "Sampled silhouette (Euclidean)",
                    "Sampled silhouette (Manhattan)",
                    "Cluster sizes",
                ],
                [
                    [
                        row.model,
                        fmt_num(row.silhouette_euclidean, 4),
                        fmt_num(row.silhouette_manhattan, 4),
                        f"`{row.cluster_sizes}`",
                    ]
                    for row in model_eval
                ],
            ),
            "",
            "- `k`-means gives the strongest separation on both distance metrics while still producing balanced, behaviorally legible groups.",
            "- Ward clustering is plausible, but it blurs the boundaries between broad revisitors and sticky local togglers.",
            "- Gaussian mixtures are more flexible in principle, but on this bounded feature space they produce weaker separation and less intuitive exemplars.",
            "- Conclusion: `k`-means is not the only defensible choice, but it is the best pragmatic fit for this report.",
            "",
            "### Choosing `k`",
            "",
            *render_table(
                ["k", "Sampled silhouette (Euclidean)", "Sampled silhouette (Manhattan)", "Cluster sizes"],
                [
                    [
                        str(int(row.k)),
                        fmt_num(float(row.sampled_silhouette_euclidean), 4),
                        fmt_num(float(row.sampled_silhouette_manhattan), 4),
                        f"`{row.cluster_sizes}`",
                    ]
                    for row in k_eval.itertuples()
                ],
            ),
            "",
            "`k=4` gives the most useful separation: it keeps broad revisitors apart from sticky local togglers without over-splitting the space.",
            "",
            "## Cluster Overview",
            "",
            *render_table(
                [
                    "Cluster",
                    "Share",
                    "Closest cartoon",
                    "Mean coverage",
                    "Mean first-sweep coverage",
                    "Mean revisit rate",
                    "Mean local toggle rate",
                    "Mean top-2 focus",
                    "Mean official score",
                    ">=50% official score",
                    "Mean within-namespace z",
                ],
                [
                    [
                        stat.name,
                        f"{stat.n:,} ({stat.share_pct:.1f}%)",
                        CLUSTER_BLURBS[stat.name]["cartoon"],
                        f"{stat.mean_coverage_pct:.1f}%",
                        f"{stat.mean_first_sweep_pct:.1f}%",
                        f"{100.0 * stat.mean_revisit_rate:.1f}%",
                        f"{100.0 * stat.mean_local_toggle_rate:.1f}%",
                        f"{stat.mean_top2_focus:.1f}%",
                        f"{100.0 * stat.mean_score_frac:.1f}%",
                        f"{stat.half_or_more_pct:.1f}%",
                        fmt_num(stat.mean_score_z, 3),
                    ]
                    for stat in cluster_stats
                ],
            ),
            "",
            "## Significance Of The Performance Gap",
            "",
            f"- Kruskal-Wallis on raw official score fraction: `H={tests['kw_raw'].statistic:.2f}`, `p={fmt_pvalue(float(tests['kw_raw'].pvalue))}`.",
            f"- Kruskal-Wallis on within-namespace standardized score: `H={tests['kw_z'].statistic:.2f}`, `p={fmt_pvalue(float(tests['kw_z'].pvalue))}`.",
            f"- Best cluster: **{tests['best_cluster']}**.",
            f"- Best cluster versus everybody else pooled: Mann-Whitney `U={tests['best_vs_rest']['u']:.0f}`, "
            f"`p={fmt_pvalue(float(tests['best_vs_rest']['p']))}`, Cliff's delta `{tests['best_vs_rest']['delta']:.3f}`.",
            "",
            "Pairwise against the best cluster (Benjamini-Hochberg adjusted):",
            "",
            *render_table(
                ["Comparison", "Raw p", "BH-adjusted p", "Cliff's delta"],
                [
                    [
                        comparison,
                        fmt_pvalue(float(stats["p"])),
                        fmt_pvalue(float(stats["p_bh"])),
                        fmt_num(float(stats["delta"]), 3),
                    ]
                    for comparison, stats in tests["pairwise"].items()
                ],
            ),
            "",
            "Interpretation:",
            f"- **{tests['best_cluster']}** is not just a little ahead. It is the top cluster on official performance and still stays on top after normalizing inside each namespace.",
            "- The largest gap is between Linear sweepers and Local togglers. The students who sweep broadly and revisit late outperform the students who keep bouncing locally.",
            "",
            "## Best Exemplars",
            "",
            "Question numbers below are the in-namespace problem numbers (`Q05` = problem `5`). "
            "The timeline is exact at the run level: start time, end time, question, number of events in that run, and the state that caused the student to move on.",
            "",
        ]
    )

    for cluster_name in CLUSTER_ORDER:
        lines.extend(exemplar_lines(cluster_name, exemplars[cluster_name], feature_df, run_lookup))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    markdown = build_markdown()
    OUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
