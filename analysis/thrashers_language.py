#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy>=2.1.0",
#   "pandas>=2.2.0",
#   "scipy>=1.14.0",
# ]
# ///
"""Analyze whether question-language complexity is linked to thrasher behavior.

Outputs:
- analysis/thrashers_language.csv
- analysis/thrashers_language_tests.csv
- analysis/thrashers_language_pairs.csv
- analysis/thrashers_language.md

Important caveat:
This dataset does NOT contain students' native language. So we can only test an
indirect hypothesis: whether English prompt linguistic load is associated with
thrasher behavior.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
PROBLEMS_DIR = ROOT / "problems"

ATTEMPTS_CSV = ANALYSIS_DIR / "process_analysis" / "attempt_archetypes.csv"
OUT_Q_CSV = ANALYSIS_DIR / "thrashers_language.csv"
OUT_TESTS_CSV = ANALYSIS_DIR / "thrashers_language_tests.csv"
OUT_PAIRS_CSV = ANALYSIS_DIR / "thrashers_language_pairs.csv"
OUT_CLUSTER_CSV = ANALYSIS_DIR / "thrashers_language_clusters.csv"
OUT_MD = ANALYSIS_DIR / "thrashers_language.md"

CONSTRAINT_PATTERNS = [
    r"\bif\b",
    r"\belse\b",
    r"\belif\b",
    r"\bunless\b",
    r"\bonly if\b",
    r"\bat least\b",
    r"\bat most\b",
    r"\bexactly\b",
    r"\bwithout\b",
    r"\bnot\b",
    r"\beither\b",
    r"\bneither\b",
    r"\bboth\b",
    r"\bfirst\b",
    r"\blast\b",
    r"\breverse\b",
    r"\bsort\b",
]

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_SPLIT_RE = re.compile(r"[.!?;:\n]+")
HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class ModelResult:
    beta: np.ndarray
    se: np.ndarray
    p_values: np.ndarray
    dof: int
    rss: float


def strip_html(text: str) -> str:
    """Return plain text from question HTML."""
    clean = HTML_TAG_RE.sub(" ", text or "")
    clean = clean.replace("&nbsp;", " ")
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def boolify(series: pd.Series) -> pd.Series:
    """Parse mixed True/False style values to bool."""
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    low = series.astype(str).str.strip().str.lower()
    return low.isin({"true", "1", "t", "yes", "y"})


def safe_div(n: float, d: float) -> float:
    return float(n / d) if d else math.nan


def zscore(series: pd.Series) -> pd.Series:
    vals = pd.to_numeric(series, errors="coerce")
    mu = vals.mean(skipna=True)
    sigma = vals.std(skipna=True, ddof=0)
    if pd.isna(sigma) or sigma == 0:
        return pd.Series(0.0, index=series.index)
    return (vals - mu) / sigma


def tokenize_words(text: str) -> list[str]:
    return WORD_RE.findall(text or "")


def estimate_syllables(word: str) -> int:
    """Cheap syllable estimator (good enough for relative readability ranking)."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    groups = re.findall(r"[aeiouy]+", w)
    syllables = len(groups)
    if w.endswith("e"):
        syllables -= 1
    if w.endswith("le") and len(w) > 2 and w[-3] not in "aeiouy":
        syllables += 1
    return max(1, syllables)


def readability_features(question_html: str, question_text: str) -> dict[str, float]:
    words = tokenize_words(question_text)
    word_count = len(words)
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(question_text) if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_len = safe_div(word_count, sentence_count) if sentence_count else math.nan
    avg_word_len = float(np.mean([len(w) for w in words])) if words else math.nan
    long_word_ratio = safe_div(sum(len(w) >= 7 for w in words), word_count) if word_count else math.nan
    syllables = sum(estimate_syllables(w) for w in words)
    syllables_per_word = safe_div(syllables, word_count) if word_count else math.nan

    # Flesch metrics; invalid for very short prompts but still useful at scale.
    if word_count > 0 and sentence_count > 0:
        flesch_reading_ease = 206.835 - 1.015 * safe_div(word_count, sentence_count) - 84.6 * safe_div(syllables, word_count)
        fk_grade_level = 0.39 * safe_div(word_count, sentence_count) + 11.8 * safe_div(syllables, word_count) - 15.59
    else:
        flesch_reading_ease = math.nan
        fk_grade_level = math.nan

    lowered = question_text.lower()
    constraint_hits = sum(len(re.findall(pat, lowered)) for pat in CONSTRAINT_PATTERNS)
    constraint_density_per_100_words = 100.0 * safe_div(constraint_hits, word_count) if word_count else math.nan

    # Quick proxy for procedural instruction load.
    bullet_markers = len(re.findall(r"(?:^|[\n\r])\s*(?:[-*•]|\d+\.)\s+", question_html or ""))
    numbered_steps = len(re.findall(r"\b\d+\)", question_text))
    procedural_markers = bullet_markers + numbered_steps

    return {
        "word_count": float(word_count),
        "sentence_count": float(sentence_count),
        "avg_sentence_len_words": float(avg_sentence_len) if not pd.isna(avg_sentence_len) else math.nan,
        "avg_word_len_chars": float(avg_word_len) if not pd.isna(avg_word_len) else math.nan,
        "long_word_ratio": float(long_word_ratio) if not pd.isna(long_word_ratio) else math.nan,
        "syllables_per_word": float(syllables_per_word) if not pd.isna(syllables_per_word) else math.nan,
        "flesch_reading_ease": float(flesch_reading_ease) if not pd.isna(flesch_reading_ease) else math.nan,
        "fk_grade_level": float(fk_grade_level) if not pd.isna(fk_grade_level) else math.nan,
        "constraint_hits": float(constraint_hits),
        "constraint_density_per_100_words": float(constraint_density_per_100_words)
        if not pd.isna(constraint_density_per_100_words)
        else math.nan,
        "procedural_marker_count": float(procedural_markers),
    }


def problem_features() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for ns_dir in sorted(PROBLEMS_DIR.glob("*")):
        if not ns_dir.is_dir():
            continue
        namespace = ns_dir.name
        for pfile in sorted(ns_dir.glob("*.json"), key=lambda p: int(p.stem)):
            problem_id = int(pfile.stem)
            with pfile.open("r", encoding="utf-8") as f:
                obj = json.load(f)

            question_html = str(obj.get("question") or "")
            question_text = strip_html(question_html)
            title = question_text[:120].strip()
            m = re.search(r"<h1>\s*<b>([^<]+)</b>", question_html)
            if m:
                title = m.group(1).strip()

            langs = obj.get("allowed_languages") or []
            py_templates = [
                str(lang.get("code_template") or "")
                for lang in langs
                if isinstance(lang, dict) and str(lang.get("language") or "").startswith("py")
            ]
            py_template = max(py_templates, key=len) if py_templates else ""
            py_template_line_count = len([ln for ln in py_template.splitlines() if ln.strip()])
            py_template_def_count = len(re.findall(r"^\s*def\s+\w+\s*\(", py_template, flags=re.M))

            base = {
                "namespace": namespace,
                "problem_id": problem_id,
                "question_title_problem": title,
                "question_text": question_text,
                "question_text_preview": question_text[:220],
                "num_public_tests": len(obj.get("public_testcase") or []),
                "num_private_tests": len(obj.get("private_testcase") or []),
                "python_template_line_count": py_template_line_count,
                "python_template_def_count": py_template_def_count,
            }
            base.update(readability_features(question_html, question_text))
            rows.append(base)
    return pd.DataFrame(rows)


def attempt_features() -> pd.DataFrame:
    df = pd.read_csv(ATTEMPTS_CSV, low_memory=False)
    df["is_python_question"] = boolify(df["is_python_question"])
    df = df[df["is_python_question"]].copy()
    df["thrasher_flag"] = boolify(df["thrasher_flag"])
    df["process_outcome_success_flag"] = boolify(df["process_outcome_success_flag"])

    num_cols = [
        "public_test_run_count",
        "public_pass_oscillation_events",
        "parseability_regression_flag",
        "structural_complexity_max",
        "total_active_time_seconds",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["parseability_regression_flag"] = boolify(df["parseability_regression_flag"])

    g = (
        df.groupby(["namespace", "problem_id", "question_title"], dropna=False)
        .agg(
            attempts=("student_id", "size"),
            thrashers=("thrasher_flag", "sum"),
            thrasher_rate=("thrasher_flag", "mean"),
            success_rate=("process_outcome_success_flag", "mean"),
            mean_public_runs=("public_test_run_count", "mean"),
            mean_public_oscillation=("public_pass_oscillation_events", "mean"),
            parseability_regression_rate=("parseability_regression_flag", "mean"),
            median_structural_complexity_max=("structural_complexity_max", "median"),
            median_active_time_s=("total_active_time_seconds", "median"),
        )
        .reset_index()
    )
    return g


def weighted_corr(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    wsum = w.sum()
    if wsum <= 0:
        return math.nan
    mx = np.sum(w * x) / wsum
    my = np.sum(w * y) / wsum
    cov = np.sum(w * (x - mx) * (y - my)) / wsum
    vx = np.sum(w * (x - mx) ** 2) / wsum
    vy = np.sum(w * (y - my) ** 2) / wsum
    if vx <= 0 or vy <= 0:
        return math.nan
    return float(cov / math.sqrt(vx * vy))


def fit_wls(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> ModelResult:
    sw = np.sqrt(w)
    xw = x * sw[:, None]
    yw = y * sw
    xtx = xw.T @ xw
    xty = xw.T @ yw
    beta = np.linalg.solve(xtx, xty)
    resid = y - x @ beta
    rss = float(np.sum(w * resid**2))
    n, k = x.shape
    dof = max(1, n - k)
    sigma2 = rss / dof
    cov = sigma2 * np.linalg.inv(xtx)
    se = np.sqrt(np.diag(cov))
    t_vals = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    p_vals = 2.0 * (1.0 - stats.t.cdf(np.abs(t_vals), dof))
    return ModelResult(beta=beta, se=se, p_values=p_vals, dof=dof, rss=rss)


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def top_bottom_quartile_test(df: pd.DataFrame) -> dict[str, float]:
    q25 = float(df["linguistic_load_index"].quantile(0.25))
    q75 = float(df["linguistic_load_index"].quantile(0.75))
    low = df[df["linguistic_load_index"] <= q25]
    high = df[df["linguistic_load_index"] >= q75]

    low_thr = float(low["thrashers"].sum())
    low_n = float(low["attempts"].sum())
    high_thr = float(high["thrashers"].sum())
    high_n = float(high["attempts"].sum())
    p_low = safe_div(low_thr, low_n)
    p_high = safe_div(high_thr, high_n)
    p_pool = safe_div(low_thr + high_thr, low_n + high_n)
    se = math.sqrt(p_pool * (1.0 - p_pool) * ((1.0 / low_n) + (1.0 / high_n))) if low_n > 0 and high_n > 0 else math.nan
    z = (p_high - p_low) / se if se and se > 0 else math.nan
    p = 2.0 * (1.0 - stats.norm.cdf(abs(z))) if not pd.isna(z) else math.nan
    rr = safe_div(p_high, p_low) if p_low and p_low > 0 else math.nan

    return {
        "low_question_count": float(len(low)),
        "high_question_count": float(len(high)),
        "low_attempts": low_n,
        "high_attempts": high_n,
        "low_thrasher_rate": p_low,
        "high_thrasher_rate": p_high,
        "absolute_diff_pp": (p_high - p_low) * 100.0,
        "relative_risk": rr,
        "z_stat": z,
        "p_value": p,
    }


def make_pairwise_examples(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    idx = list(df.index)
    for i, j in combinations(idx, 2):
        a = df.loc[i]
        b = df.loc[j]
        if min(a["attempts"], b["attempts"]) < 120:
            continue
        tech_gap = abs(float(a["technical_difficulty_index"]) - float(b["technical_difficulty_index"]))
        load_gap = abs(float(a["linguistic_load_index"]) - float(b["linguistic_load_index"]))
        if tech_gap > 0.35 or load_gap < 1.0:
            continue
        rows.append(
            {
                "namespace_a": a["namespace"],
                "problem_id_a": int(a["problem_id"]),
                "title_a": a["question_title"],
                "attempts_a": int(a["attempts"]),
                "thrasher_rate_a": float(a["thrasher_rate"]),
                "linguistic_load_a": float(a["linguistic_load_index"]),
                "namespace_b": b["namespace"],
                "problem_id_b": int(b["problem_id"]),
                "title_b": b["question_title"],
                "attempts_b": int(b["attempts"]),
                "thrasher_rate_b": float(b["thrasher_rate"]),
                "linguistic_load_b": float(b["linguistic_load_index"]),
                "tech_gap": tech_gap,
                "load_gap": load_gap,
                "thrasher_rate_diff_pp": 100.0 * (float(a["thrasher_rate"]) - float(b["thrasher_rate"])),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values("thrasher_rate_diff_pp", key=np.abs, ascending=False).head(30).reset_index(drop=True)


def build_report_md(
    qdf: pd.DataFrame,
    tests_df: pd.DataFrame,
    quartile_result: dict[str, float],
    pair_df: pd.DataFrame,
) -> str:
    total_attempts = int(qdf["attempts"].sum())
    total_thrashers = int(qdf["thrashers"].sum())
    overall_rate = safe_div(total_thrashers, total_attempts)
    q_count = int(len(qdf))

    weighted_corr_row = tests_df.loc[tests_df["test_name"] == "weighted_corr_load_vs_thrasher_rate"].iloc[0]
    spearman_row = tests_df.loc[tests_df["test_name"] == "spearman_load_vs_thrasher_rate"].iloc[0]
    wls_row = tests_df.loc[tests_df["test_name"] == "wls_beta_load_adjusted_for_technical_difficulty"].iloc[0]
    cluster_weighted_corr_row = tests_df.loc[
        tests_df["test_name"] == "cluster_weighted_corr_load_vs_thrasher_rate"
    ].iloc[0]
    cluster_spearman_row = tests_df.loc[tests_df["test_name"] == "cluster_spearman_load_vs_thrasher_rate"].iloc[0]

    sig_any = (
        bool(weighted_corr_row["p_value"] < 0.05)
        or bool(spearman_row["p_value"] < 0.05)
        or bool(wls_row["p_value"] < 0.05)
        or bool(cluster_weighted_corr_row["p_value"] < 0.05)
        or bool(cluster_spearman_row["p_value"] < 0.05)
    )
    headline = (
        "There is a measurable link between language load and thrashing, but it is not proof about native Hindi speakers."
        if sig_any
        else "No statistically significant evidence that prompt language load alone explains thrashing."
    )

    high_load = qdf.sort_values("linguistic_load_index", ascending=False).head(8)
    high_thrash = qdf.sort_values("thrasher_rate", ascending=False).head(10)
    top15 = qdf.sort_values(["thrasher_rate", "attempts"], ascending=[False, False]).head(15)
    top15_mean_load = float(top15["linguistic_load_index"].mean())
    rest_mean_load = float(qdf.loc[~qdf.index.isin(top15.index), "linguistic_load_index"].mean())

    pair_section = ""
    if not pair_df.empty:
        top_pairs = pair_df.head(5)
        pair_lines = []
        for r in top_pairs.itertuples(index=False):
            pair_lines.append(
                f"- `{r.namespace_a}/{r.problem_id_a}` ({r.title_a}) vs `{r.namespace_b}/{r.problem_id_b}` ({r.title_b}): "
                f"tech gap `{r.tech_gap:.2f}`, language-load gap `{r.load_gap:.2f}`, thrasher-rate gap `{r.thrasher_rate_diff_pp:+.2f} pp`."
            )
        pair_section = "\n".join(pair_lines)
    else:
        pair_section = "- No high-confidence matched pairs met the strict filtering thresholds."

    lines: list[str] = []
    lines.append("# Thrashers and Question-Language Load")
    lines.append("")
    lines.append("## Direct Answer")
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append("You asked specifically about native Hindi speakers. This dataset does **not** include each student's native language, so we cannot directly test that claim.")
    lines.append("What we can test is an indirect signal: do linguistically heavier English prompts coincide with more thrasher behavior?")
    lines.append("")
    lines.append("## Data Used")
    lines.append("")
    lines.append(f"- Attempt rows analyzed: `{total_attempts:,}`")
    lines.append(f"- Thrasher rows: `{total_thrashers:,}` (`{overall_rate * 100:.2f}%`)")
    lines.append(f"- Python question instances: `{q_count}`")
    lines.append("- Thrashers source: `analysis/process_analysis/attempt_archetypes.csv` (`thrasher_flag`)")
    lines.append("- Prompt source: `problems/*/*.json` question text + testcase counts + template structure")
    lines.append("")
    lines.append("## Main Statistical Evidence")
    lines.append("")
    lines.append(
        f"- Weighted correlation (language-load index vs question thrasher rate): `{weighted_corr_row['statistic']:.3f}`, "
        f"permutation `p={weighted_corr_row['p_value']:.4f}`."
    )
    lines.append(
        f"- Spearman correlation (unweighted): `{spearman_row['statistic']:.3f}`, `p={spearman_row['p_value']:.4f}`."
    )
    lines.append(
        f"- Adjusted model (controls: technical difficulty index + log attempts): beta(load) `{wls_row['statistic']:.3f}`, "
        f"permutation `p={wls_row['p_value']:.4f}`."
    )
    lines.append(
        f"- High-language-load questions (top quartile) vs low-language-load (bottom quartile): "
        f"`{quartile_result['high_thrasher_rate'] * 100:.2f}%` vs `{quartile_result['low_thrasher_rate'] * 100:.2f}%`, "
        f"diff `{quartile_result['absolute_diff_pp']:.2f} pp`, `p={quartile_result['p_value']:.4f}`."
    )
    lines.append(
        f"- Robustness (collapse near-duplicate variants into semantic signatures): weighted corr "
        f"`{cluster_weighted_corr_row['statistic']:.3f}`, `p={cluster_weighted_corr_row['p_value']:.4f}`; "
        f"Spearman `{cluster_spearman_row['statistic']:.3f}`, `p={cluster_spearman_row['p_value']:.4f}`."
    )
    lines.append(
        f"- Mean language-load index among top 15 thrasher-rate questions vs the rest: "
        f"`{top15_mean_load:.2f}` vs `{rest_mean_load:.2f}`."
    )
    lines.append("")
    lines.append("## What This Means (Plain Language)")
    lines.append("")
    lines.append("- If p-values are small (<0.05), language-heavy prompts are likely adding extra confusion load.")
    lines.append("- If p-values are not small, the data does not support language-load as a major standalone explanation.")
    lines.append("- Either way, this is an indirect signal. It does **not** prove which students are native Hindi speakers or why any one student thrashed.")
    lines.append("")
    lines.append("## Where Language Load Looks High")
    lines.append("")
    for r in high_load.itertuples(index=False):
        lines.append(
            f"- `{r.namespace}/{int(r.problem_id)}` `{r.question_title}`: "
            f"language-load index `{r.linguistic_load_index:.2f}`, thrasher rate `{r.thrasher_rate * 100:.2f}%` over `{int(r.attempts)}` attempts."
        )
    lines.append("")
    lines.append("## Highest Thrasher-Rate Questions")
    lines.append("")
    for r in high_thrash.itertuples(index=False):
        lines.append(
            f"- `{r.namespace}/{int(r.problem_id)}` `{r.question_title}`: "
            f"thrasher rate `{r.thrasher_rate * 100:.2f}%`, language-load index `{r.linguistic_load_index:.2f}`, attempts `{int(r.attempts)}`."
        )
    lines.append("")
    lines.append("## Matched-Pair Evidence (Similar technical difficulty, different language load)")
    lines.append("")
    lines.append(pair_section)
    lines.append("")
    lines.append("## Caveats (Important)")
    lines.append("")
    lines.append("- No native-language labels are available. We cannot identify Hindi speakers from this data.")
    lines.append("- Readability formulas are rough for programming prompts; they are proxies, not ground truth.")
    lines.append("- Correlation is not causation. Some high-load prompts may also hide concept ambiguity.")
    lines.append("- Thrashing itself is a process label, not a fixed student identity.")
    lines.append("")
    lines.append("## Files Produced")
    lines.append("")
    lines.append("- `analysis/thrashers_language.csv` (question-level feature table)")
    lines.append("- `analysis/thrashers_language_clusters.csv` (collapsed semantic-signature table)")
    lines.append("- `analysis/thrashers_language_tests.csv` (all statistical test outputs)")
    lines.append("- `analysis/thrashers_language_pairs.csv` (matched-pair evidence)")
    lines.append("- `analysis/thrashers_language.md` (this report)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    np.random.seed(42)

    attempts = attempt_features()
    probs = problem_features()
    qdf = attempts.merge(probs, on=["namespace", "problem_id"], how="left")
    qdf["question_title"] = qdf["question_title"].fillna(qdf["question_title_problem"])
    qdf.drop(columns=[c for c in ["question_title_problem"] if c in qdf.columns], inplace=True)

    lang_index = (
        zscore(qdf["word_count"])
        + zscore(qdf["avg_sentence_len_words"])
        + zscore(qdf["long_word_ratio"])
        + zscore(qdf["constraint_density_per_100_words"])
        + zscore(qdf["fk_grade_level"])
        + zscore(-qdf["flesch_reading_ease"])
        + zscore(qdf["procedural_marker_count"])
    ) / 7.0
    qdf["linguistic_load_index"] = lang_index

    qdf["total_test_count"] = pd.to_numeric(qdf["num_public_tests"], errors="coerce").fillna(0) + pd.to_numeric(
        qdf["num_private_tests"], errors="coerce"
    ).fillna(0)
    tech_index = (
        zscore(qdf["total_test_count"])
        + zscore(qdf["python_template_def_count"])
        + zscore(qdf["median_structural_complexity_max"])
    ) / 3.0
    qdf["technical_difficulty_index"] = tech_index

    qdf["attempts"] = pd.to_numeric(qdf["attempts"], errors="coerce")
    qdf["thrashers"] = pd.to_numeric(qdf["thrashers"], errors="coerce")
    qdf["thrasher_rate"] = qdf["thrashers"] / qdf["attempts"]
    qdf = qdf[qdf["attempts"] >= 30].copy()

    x = qdf["linguistic_load_index"].to_numpy(dtype=float)
    y = qdf["thrasher_rate"].to_numpy(dtype=float)
    w = qdf["attempts"].to_numpy(dtype=float)

    weighted_r = weighted_corr(x, y, w)
    spearman_rho, spearman_p = stats.spearmanr(x, y, nan_policy="omit")

    # Robustness: collapse likely variant duplicates by normalized semantic signature.
    def _norm(s: str) -> str:
        s = re.sub(r"[^a-z0-9 ]+", " ", str(s).lower())
        return re.sub(r"\s+", " ", s).strip()

    qdf["semantic_signature"] = (
        qdf["question_title"].map(_norm)
        + "|"
        + qdf["total_test_count"].astype(str)
        + "|"
        + qdf["python_template_def_count"].astype(str)
    )
    cdf = (
        qdf.groupby("semantic_signature", as_index=False)
        .agg(
            variants=("namespace", "size"),
            attempts=("attempts", "sum"),
            thrashers=("thrashers", "sum"),
            linguistic_load_index=("linguistic_load_index", "mean"),
            technical_difficulty_index=("technical_difficulty_index", "mean"),
        )
        .sort_values("attempts", ascending=False)
    )
    cdf["thrasher_rate"] = cdf["thrashers"] / cdf["attempts"]
    cx = cdf["linguistic_load_index"].to_numpy(dtype=float)
    cy = cdf["thrasher_rate"].to_numpy(dtype=float)
    cw = cdf["attempts"].to_numpy(dtype=float)
    cluster_weighted_r = weighted_corr(cx, cy, cw)
    cluster_spearman_rho, cluster_spearman_p = stats.spearmanr(cx, cy, nan_policy="omit")

    # Weighted-correlation permutation test.
    n_perm = 5000
    r_perm = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        xp = np.random.permutation(x)
        r_perm[i] = weighted_corr(xp, y, w)
    p_weighted_corr = (np.sum(np.abs(r_perm) >= abs(weighted_r)) + 1.0) / (n_perm + 1.0)

    cluster_r_perm = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        cxp = np.random.permutation(cx)
        cluster_r_perm[i] = weighted_corr(cxp, cy, cw)
    p_cluster_weighted_corr = (np.sum(np.abs(cluster_r_perm) >= abs(cluster_weighted_r)) + 1.0) / (n_perm + 1.0)

    # WLS on logit(thrasher_rate), with continuity correction.
    y_logit = np.log((qdf["thrashers"] + 0.5) / (qdf["attempts"] - qdf["thrashers"] + 0.5))
    x_full = np.column_stack(
        [
            np.ones(len(qdf)),
            qdf["linguistic_load_index"].to_numpy(dtype=float),
            qdf["technical_difficulty_index"].to_numpy(dtype=float),
            np.log(qdf["attempts"].to_numpy(dtype=float)),
        ]
    )
    x_base = np.column_stack(
        [
            np.ones(len(qdf)),
            qdf["technical_difficulty_index"].to_numpy(dtype=float),
            np.log(qdf["attempts"].to_numpy(dtype=float)),
        ]
    )

    wls_full = fit_wls(y_logit.to_numpy(dtype=float), x_full, w)
    wls_base = fit_wls(y_logit.to_numpy(dtype=float), x_base, w)
    r2_gain = safe_div(wls_base.rss - wls_full.rss, wls_base.rss)

    beta_load = float(wls_full.beta[1])
    beta_perm = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        xp = np.random.permutation(qdf["linguistic_load_index"].to_numpy(dtype=float))
        x_perm = x_full.copy()
        x_perm[:, 1] = xp
        beta_perm[i] = float(fit_wls(y_logit.to_numpy(dtype=float), x_perm, w).beta[1])
    p_beta_perm = (np.sum(np.abs(beta_perm) >= abs(beta_load)) + 1.0) / (n_perm + 1.0)

    q25 = float(qdf["linguistic_load_index"].quantile(0.25))
    q75 = float(qdf["linguistic_load_index"].quantile(0.75))
    ctrl_tech = float(qdf["technical_difficulty_index"].median())
    ctrl_log_attempts = float(np.log(qdf["attempts"]).median())
    p25 = float(sigmoid(np.dot(wls_full.beta, np.array([1.0, q25, ctrl_tech, ctrl_log_attempts]))))
    p75 = float(sigmoid(np.dot(wls_full.beta, np.array([1.0, q75, ctrl_tech, ctrl_log_attempts]))))
    predicted_delta_pp = (p75 - p25) * 100.0

    quartile = top_bottom_quartile_test(qdf)

    tests = [
        {
            "test_name": "weighted_corr_load_vs_thrasher_rate",
            "statistic": weighted_r,
            "p_value": p_weighted_corr,
            "n_questions": len(qdf),
            "details": "Permutation p-value (5000 shuffles), weighted by attempts.",
        },
        {
            "test_name": "spearman_load_vs_thrasher_rate",
            "statistic": float(spearman_rho),
            "p_value": float(spearman_p),
            "n_questions": len(qdf),
            "details": "Unweighted Spearman correlation.",
        },
        {
            "test_name": "wls_beta_load_adjusted_for_technical_difficulty",
            "statistic": beta_load,
            "p_value": p_beta_perm,
            "n_questions": len(qdf),
            "details": "WLS on logit(thrasher_rate), controls for technical difficulty + log attempts; permutation p-value.",
        },
        {
            "test_name": "cluster_weighted_corr_load_vs_thrasher_rate",
            "statistic": cluster_weighted_r,
            "p_value": p_cluster_weighted_corr,
            "n_questions": len(cdf),
            "details": "Variant-collapsed semantic signatures; weighted correlation with permutation p-value.",
        },
        {
            "test_name": "cluster_spearman_load_vs_thrasher_rate",
            "statistic": float(cluster_spearman_rho),
            "p_value": float(cluster_spearman_p),
            "n_questions": len(cdf),
            "details": "Variant-collapsed semantic signatures; unweighted Spearman.",
        },
        {
            "test_name": "wls_model_delta_rss_ratio_from_adding_load",
            "statistic": r2_gain,
            "p_value": math.nan,
            "n_questions": len(qdf),
            "details": "Relative RSS reduction vs control-only model.",
        },
        {
            "test_name": "predicted_thrasher_delta_pp_p75_minus_p25_load",
            "statistic": predicted_delta_pp,
            "p_value": math.nan,
            "n_questions": len(qdf),
            "details": "Model-predicted thrasher-rate change for p25->p75 language load at median controls.",
        },
        {
            "test_name": "top_vs_bottom_quartile_two_proportion_z",
            "statistic": quartile["z_stat"],
            "p_value": quartile["p_value"],
            "n_questions": int(quartile["low_question_count"] + quartile["high_question_count"]),
            "details": (
                f"High load rate={quartile['high_thrasher_rate']:.4f}, "
                f"low load rate={quartile['low_thrasher_rate']:.4f}, "
                f"diff={quartile['absolute_diff_pp']:.2f}pp."
            ),
        },
    ]
    tests_df = pd.DataFrame(tests)
    tests_df["significant_at_0_05"] = tests_df["p_value"] < 0.05

    # Residual signal vs control-only model.
    pred_base = sigmoid(x_base @ wls_base.beta)
    qdf["expected_thrasher_rate_control_only"] = pred_base
    qdf["residual_thrasher_rate_pp"] = 100.0 * (qdf["thrasher_rate"] - qdf["expected_thrasher_rate_control_only"])

    pairs_df = make_pairwise_examples(qdf)

    out_cols = [
        "namespace",
        "problem_id",
        "question_title",
        "attempts",
        "thrashers",
        "thrasher_rate",
        "success_rate",
        "mean_public_runs",
        "mean_public_oscillation",
        "parseability_regression_rate",
        "median_structural_complexity_max",
        "median_active_time_s",
        "word_count",
        "sentence_count",
        "avg_sentence_len_words",
        "avg_word_len_chars",
        "long_word_ratio",
        "flesch_reading_ease",
        "fk_grade_level",
        "constraint_hits",
        "constraint_density_per_100_words",
        "procedural_marker_count",
        "num_public_tests",
        "num_private_tests",
        "python_template_line_count",
        "python_template_def_count",
        "linguistic_load_index",
        "technical_difficulty_index",
        "expected_thrasher_rate_control_only",
        "residual_thrasher_rate_pp",
        "question_text_preview",
    ]
    out = qdf[out_cols].sort_values(["thrasher_rate", "attempts"], ascending=[False, False]).reset_index(drop=True)

    out.to_csv(OUT_Q_CSV, index=False)
    cdf.to_csv(OUT_CLUSTER_CSV, index=False)
    tests_df.to_csv(OUT_TESTS_CSV, index=False)
    pairs_df.to_csv(OUT_PAIRS_CSV, index=False)

    report = build_report_md(out, tests_df, quartile, pairs_df)
    OUT_MD.write_text(report, encoding="utf-8")

    print(f"Wrote: {OUT_Q_CSV}")
    print(f"Wrote: {OUT_CLUSTER_CSV}")
    print(f"Wrote: {OUT_TESTS_CSV}")
    print(f"Wrote: {OUT_PAIRS_CSV}")
    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
