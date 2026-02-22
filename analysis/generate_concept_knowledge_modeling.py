#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "numpy>=2.0.0",
#   "pandas>=2.2.0",
# ]
# ///
"""Step 9: Concept Dependency and Knowledge Modelling.

Builds a reproducible concept-tagged question map and downstream analyses:
- concept-question map (251 questions, multi-tag)
- concept-level mastery summaries (public-best GRM basis)
- construct-usage-vs-mastery tables
- empirical concept prerequisite graph
- repeat-student paired concept profiles
- S2 (parseable, zero public tests) concept decomposition

Outputs are written to ``analysis/concept_knowledge_modeling/``.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUT_DIR = ANALYSIS_DIR / "concept_knowledge_modeling"

SUBSTANTIVE_MIN_QUESTION_ROWS = 3
MASTERY_MEAN_GRM_THRESHOLD = 1.5  # term/wave concept mastery flag threshold

CONCEPTS = [
    "Arithmetic / conditionals",
    "String manipulation",
    "List / tuple operations",
    "Dictionary operations",
    "Loops and iteration",
    "Pattern printing",
    "Input parsing / output formatting",
    "Data analysis / aggregation",
    "File operations",
    "Mathematical / algorithmic",
]
CONCEPT_ORDER_PROXY = {concept: i + 1 for i, concept in enumerate(CONCEPTS)}

CONCEPT_ID = {
    "Arithmetic / conditionals": "arithmetic_conditionals",
    "String manipulation": "string_manipulation",
    "List / tuple operations": "list_tuple_ops",
    "Dictionary operations": "dictionary_ops",
    "Loops and iteration": "loops_iteration",
    "Pattern printing": "pattern_printing",
    "Input parsing / output formatting": "io_parsing_formatting",
    "Data analysis / aggregation": "data_analysis_aggregation",
    "File operations": "file_operations",
    "Mathematical / algorithmic": "mathematical_algorithmic",
}

# Question-level concept construct proxies (limited to constructs exposed in Step 5).
CONCEPT_CONSTRUCT_PROXIES: dict[str, dict[str, Any]] = {
    "Arithmetic / conditionals": {
        "constructs": ["if_stmt"],
        "proxy_quality": "partial",
        "proxy_note": "Conditional proxy only; arithmetic operators are not tracked in Step 5 constructs.",
    },
    "String manipulation": {
        "constructs": ["for_loop", "if_stmt"],
        "proxy_quality": "weak",
        "proxy_note": "No string-specific AST features are tracked; loops/conditionals are weak proxies.",
    },
    "List / tuple operations": {
        "constructs": ["for_loop", "list_comp"],
        "proxy_quality": "partial",
        "proxy_note": "Captures iterative/list-comprehension solutions; indexing-only solutions may be missed.",
    },
    "Dictionary operations": {
        "constructs": ["dict_comp"],
        "proxy_quality": "narrow",
        "proxy_note": "Narrow proxy: dict literals/indexing are not tracked, only dict comprehensions.",
    },
    "Loops and iteration": {
        "constructs": ["for_loop", "while_loop"],
        "proxy_quality": "direct",
        "proxy_note": "Direct proxy for explicit loops.",
    },
    "Pattern printing": {
        "constructs": ["for_loop", "while_loop", "print_call"],
        "proxy_quality": "partial",
        "proxy_note": "Captures explicit loop/print patterns; list-join string building may be undercounted.",
    },
    "Input parsing / output formatting": {
        "constructs": ["print_call", "try_stmt"],
        "proxy_quality": "weak",
        "proxy_note": "Formatting/parsing lacks direct AST proxies in Step 5; print/try are weak proxies.",
    },
    "Data analysis / aggregation": {
        "constructs": ["for_loop", "if_stmt", "list_comp", "dict_comp"],
        "proxy_quality": "partial",
        "proxy_note": "Proxy for aggregation/control-flow patterns; not all analyses require these constructs.",
    },
    "File operations": {
        "constructs": ["import_stmt", "import_from_stmt", "try_stmt"],
        "proxy_quality": "weak",
        "proxy_note": "No direct open()/path AST flags are tracked; imports/try are weak proxies.",
    },
    "Mathematical / algorithmic": {
        "constructs": ["for_loop", "while_loop", "if_stmt"],
        "proxy_quality": "partial",
        "proxy_note": "Proxy captures control-flow-heavy algorithms but misses expression-only solutions.",
    },
}

CONSTRUCT_FOCUS_ROWS = [
    {
        "focus_label": "Loops",
        "focus_group": "construct_focus",
        "constructs": ["for_loop", "while_loop"],
        "proxy_quality": "direct",
        "note": "Matches the Step 9 prompt's loop focus row.",
    },
    {
        "focus_label": "List comprehensions",
        "focus_group": "construct_focus",
        "constructs": ["list_comp"],
        "proxy_quality": "direct",
        "note": "Cross-cutting construct focus, not a standalone 9a concept.",
    },
    {
        "focus_label": "Dictionaries (dict_comp proxy)",
        "focus_group": "construct_focus",
        "constructs": ["dict_comp"],
        "proxy_quality": "narrow",
        "note": "Narrow proxy for dictionary usage; dict literals/indexing are not tracked.",
    },
    {
        "focus_label": "Error handling",
        "focus_group": "construct_focus",
        "constructs": ["try_stmt"],
        "proxy_quality": "direct",
        "note": "Cross-cutting construct focus from the Step 9 prompt example.",
    },
]

TRACKED_CONSTRUCTS = [
    "for_loop",
    "while_loop",
    "if_stmt",
    "list_comp",
    "dict_comp",
    "try_stmt",
    "print_call",
    "import_stmt",
    "import_from_stmt",
]


@dataclass(frozen=True)
class Inputs:
    question_metadata: Path = ANALYSIS_DIR / "question_metadata.csv"
    guide_md: Path = ANALYSIS_DIR / "guide.md"
    grm_rows: Path = ANALYSIS_DIR / "psychometric_irt" / "question_level_grm_rows.csv"
    attempt_construct_first: Path = ANALYSIS_DIR / "process_analysis" / "attempt_construct_first_appearance.csv"
    construct_summary_global: Path = ANALYSIS_DIR / "process_analysis" / "construct_first_appearance_summary_global.csv"
    public_state_rows: Path = ANALYSIS_DIR / "process_analysis" / "public_test_run_state_rows.parquet"
    selected_snapshot_rows: Path = ANALYSIS_DIR / "error_taxonomy" / "selected_snapshot_taxonomy_rows.csv"


INPUTS = Inputs()


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


def ensure_inputs() -> None:
    missing = [p for p in INPUTS.__dict__.values() if not p.exists()]
    if missing:
        detail = "\n".join(f"- {p}" for p in missing)
        raise FileNotFoundError(f"Missing Step 9 inputs:\n{detail}")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_manifest() -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "output_manifest.csv":
            rows.append(
                {
                    "path": path.relative_to(OUT_DIR).as_posix(),
                    "bytes": path.stat().st_size,
                }
            )
    pd.DataFrame(rows).to_csv(OUT_DIR / "output_manifest.csv", index=False)


def normalize_text(s: str | None) -> str:
    if s is None:
        return ""
    txt = str(s).strip().lower()
    txt = txt.replace("&amp;", " and ")
    txt = txt.replace("&", " and ")
    txt = re.sub(r"`", "", txt)
    txt = re.sub(r"[^a-z0-9]+", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def parse_guide_question_cues(guide_path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw_line in guide_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if "`ns_" not in line:
            continue
        # Split markdown table row. Ignore first/last empty fragments around pipes.
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 4:
            continue
        ns_cell = parts[0]
        m_ns = re.search(r"`(ns_[^`]+)`", ns_cell)
        if not m_ns:
            continue
        namespace = m_ns.group(1)
        cue_cell = parts[-1]
        cue_cell = cue_cell.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        for m in re.finditer(r"Q(\d+):\s*(.+?)(?=\nQ\d+:|\Z)", cue_cell, flags=re.S):
            problem_id = int(m.group(1))
            cue = re.sub(r"\s+", " ", m.group(2)).strip()
            rows.append(
                {
                    "namespace": namespace,
                    "problem_id": problem_id,
                    "guide_question_cue": cue,
                    "guide_question_cue_norm": normalize_text(cue),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["namespace", "problem_id", "guide_question_cue", "guide_question_cue_norm"]
        )
    # In case a namespace/problem_id appears more than once in the guide, keep all cues concatenated.
    agg = (
        df.groupby(["namespace", "problem_id"], as_index=False)
        .agg(
            guide_question_cue=("guide_question_cue", lambda x: " || ".join(sorted(set(str(v) for v in x)))),
            guide_question_cue_norm=("guide_question_cue_norm", lambda x: " || ".join(sorted(set(str(v) for v in x)))),
            guide_cue_count=("guide_question_cue", "size"),
        )
    )
    return agg


def _regex_hits(patterns: list[tuple[str, float]], text: str) -> tuple[float, list[str]]:
    score = 0.0
    hits: list[str] = []
    for pat, wt in patterns:
        if re.search(pat, text, flags=re.I):
            score += wt
            hits.append(pat)
    return score, hits


TITLE_CUE_PATTERNS: dict[str, list[tuple[str, float]]] = {
    "Pattern printing": [
        (r"\bpattern\b", 5),
        (r"\b(w pattern|z pattern|diamond|hexagon|triangle|arrow trail|number line marker|visualize pattern lock|horizontal bar chart)\b", 5),
        (r"\b(draw|visualize)\b", 2),
    ],
    "Data analysis / aggregation": [
        (r"\banalysis\b", 5),
        (r"\bfilter\b", 3),
        (r"\bleaderboard\b", 3),
        (r"\btime series\b", 4),
        (r"\brecords?\b", 2),
        (r"\bbooking\b", 2),
        (r"\bperformance\b", 2),
        (r"\bscore\b", 2),
        (r"\benrollment\b", 3),
        (r"\bscheduling\b", 3),
        (r"\bfrequency\b", 2),
    ],
    "File operations": [
        (r"\bfile\b", 5),
        (r"\bfiles\b", 5),
        (r"\bmarkdown table\b", 4),
        (r"\bmarkdown image\b", 4),
        (r"\bhtml image\b", 4),
        (r"\bimage files\b", 4),
    ],
    "Input parsing / output formatting": [
        (r"\bformat\b", 4),
        (r"\bparse\b", 4),
        (r"\bmarkdown\b", 3),
        (r"\bhtml\b", 3),
        (r"\btic tac toe\b", 3),
        (r"\bchess notation\b", 3),
        (r"\bslug\b", 3),
        (r"\babbreviate\b", 2),
        (r"\bdecode\b", 3),
        (r"\bencoder?\b", 3),
    ],
    "String manipulation": [
        (r"\bstring\b", 4),
        (r"\bstrings\b", 4),
        (r"\bcharacter\b", 4),
        (r"\bcharacters\b", 4),
        (r"\bchar\b", 3),
        (r"\bword\b", 3),
        (r"\bwords\b", 3),
        (r"\bsentence\b", 3),
        (r"\bpalindrome\b", 4),
        (r"\bvowel\b", 4),
        (r"\bconsonant\b", 4),
        (r"\bslug\b", 3),
        (r"\busername\b", 3),
        (r"\brotation\b", 2),
        (r"\bstemmer\b", 3),
        (r"\bemail\b", 2),
        (r"\bprefix\b", 2),
    ],
    "List / tuple operations": [
        (r"\blist\b", 4),
        (r"\blists\b", 4),
        (r"\btuple\b", 4),
        (r"\btuples\b", 4),
        (r"\barray\b", 4),
        (r"\bmatrix\b", 4),
        (r"\belement\b", 3),
        (r"\belements\b", 3),
        (r"\bborder elements\b", 4),
        (r"\brotate matrix\b", 4),
        (r"\bindices\b", 2),
    ],
    "Dictionary operations": [
        (r"\bdictionary\b", 5),
        (r"\bdictionaries\b", 5),
        (r"\bdict\b", 4),
        (r"\bkey\b", 3),
        (r"\bkeys\b", 3),
        (r"\bvalue\b", 3),
        (r"\bvalues\b", 3),
        (r"\bgrouping dictionary\b", 4),
    ],
    "Loops and iteration": [
        (r"\bcount\b", 3),
        (r"\bcounts\b", 3),
        (r"\bsum\b", 2),
        (r"\baverage\b", 2),
        (r"\brunning average\b", 4),
        (r"\biterate\b", 3),
        (r"\bseries\b", 2),
        (r"\bscan\b", 2),
        (r"\bpairs?\b", 1),
        (r"\btrail\b", 2),
    ],
    "Arithmetic / conditionals": [
        (r"\bdivisible\b", 4),
        (r"\bdivisibility\b", 4),
        (r"\beven\b", 3),
        (r"\bodd\b", 3),
        (r"\bmultiple\b", 3),
        (r"\bsame sign\b", 3),
        (r"\bcompare last digits\b", 3),
        (r"\bcheck if\b", 2),
        (r"\bdescribe number\b", 4),
        (r"\belectricity bill\b", 3),
        (r"\beligible voters\b", 3),
    ],
    "Mathematical / algorithmic": [
        (r"\btriangle\b", 4),
        (r"\bpolygon\b", 4),
        (r"\borthogonal\b", 4),
        (r"\bpolynomial\b", 4),
        (r"\barithmetic progression\b", 4),
        (r"\bequation\b", 4),
        (r"\bsolve for x\b", 4),
        (r"\bprime\b", 4),
        (r"\blcm\b", 4),
        (r"\bobtuse\b", 4),
        (r"\bmatrix\b", 3),
        (r"\bvector\b", 3),
        (r"\bspy number\b", 4),
        (r"\bexcel column\b", 3),
    ],
}

# Supplemental text patterns (question text, lower weight due verbosity/type hints).
QUESTION_TEXT_PATTERNS: dict[str, list[tuple[str, float]]] = {
    "Dictionary operations": [
        (r"\breturns? a dictionary\b", 1.5),
        (r"\breturn[s]?\s+(?:a\s+)?dict\b", 1.5),
        (r"\bdictionary\b", 1.5),
    ],
    "List / tuple operations": [
        (r"\btakes? (?:a )?list\b", 1.5),
        (r"\btakes? (?:a )?tuple\b", 1.5),
        (r"\b2d array\b", 2.0),
    ],
    "String manipulation": [
        (r"\btakes? a string\b", 1.2),
        (r"\binput string\b", 1.2),
        (r"\bcharacters?\b", 1.0),
    ],
    "Input parsing / output formatting": [
        (r"\bprint the output\b", 1.0),
        (r"\bformat\b", 1.0),
        (r"\bparse\b", 1.0),
    ],
    "Loops and iteration": [
        (r"\bfor each\b", 1.0),
        (r"\biterate\b", 1.0),
    ],
}


def classify_question_concepts(row: pd.Series) -> pd.Series:
    title = str(row.get("question_title", "") or "")
    cue = str(row.get("guide_question_cue", "") or "")
    qtext = str(row.get("question_text", "") or "")
    title_cue_text = normalize_text(f"{title} {cue}")
    full_text = normalize_text(qtext)

    scores = {c: 0.0 for c in CONCEPTS}
    reasons: dict[str, list[str]] = {c: [] for c in CONCEPTS}

    for concept, pats in TITLE_CUE_PATTERNS.items():
        sc, hits = _regex_hits(pats, title_cue_text)
        scores[concept] += sc
        reasons[concept].extend([f"titlecue:{h}" for h in hits])

    for concept, pats in QUESTION_TEXT_PATTERNS.items():
        sc, hits = _regex_hits(pats, full_text)
        scores[concept] += sc
        reasons[concept].extend([f"qtext:{h}" for h in hits])

    # Propagation rules: encourage multi-tagging for clearly cross-cutting items.
    if scores["Pattern printing"] >= 4:
        scores["Loops and iteration"] += 2.0
        reasons["Loops and iteration"].append("prop:pattern_printing")
        scores["Input parsing / output formatting"] += 1.5
        reasons["Input parsing / output formatting"].append("prop:pattern_printing")

    if scores["Data analysis / aggregation"] >= 4:
        scores["Loops and iteration"] += 1.5
        reasons["Loops and iteration"].append("prop:data_analysis")
        if re.search(r"\b(dict|dictionary|group|frequency|count)\b", title_cue_text, flags=re.I):
            scores["Dictionary operations"] += 1.0
            reasons["Dictionary operations"].append("prop:data_analysis_dict_signal")

    if scores["File operations"] >= 4:
        scores["Input parsing / output formatting"] += 1.5
        reasons["Input parsing / output formatting"].append("prop:file_ops")

    if scores["Mathematical / algorithmic"] >= 4 and re.search(r"\bmatrix|array|vector\b", title_cue_text, flags=re.I):
        scores["List / tuple operations"] += 1.5
        reasons["List / tuple operations"].append("prop:math_matrix_vector")

    if scores["String manipulation"] >= 4 and re.search(r"\bformat|parse|slug|decode|markdown|html\b", title_cue_text, flags=re.I):
        scores["Input parsing / output formatting"] += 1.0
        reasons["Input parsing / output formatting"].append("prop:string_parse_format")

    # Thresholding with broad coverage. Keep all concepts with meaningful evidence.
    tags = [c for c in CONCEPTS if scores[c] >= 2.0]

    # Fallbacks to guarantee coverage for every question.
    if not tags:
        if re.search(r"\bpattern|draw|print\b", title_cue_text, flags=re.I):
            tags = ["Pattern printing", "Loops and iteration", "Input parsing / output formatting"]
            reasons["Pattern printing"].append("fallback:pattern")
        elif re.search(r"\banalysis|filter|records?|schedule|booking|leaderboard|series\b", title_cue_text, flags=re.I):
            tags = ["Data analysis / aggregation", "Loops and iteration"]
            reasons["Data analysis / aggregation"].append("fallback:analysis")
        elif re.search(r"\bstring|char|word|sentence|vowel|palindrome|slug|username\b", title_cue_text, flags=re.I):
            tags = ["String manipulation"]
            reasons["String manipulation"].append("fallback:string")
        elif re.search(r"\blist|tuple|array|matrix|element\b", title_cue_text, flags=re.I):
            tags = ["List / tuple operations"]
            reasons["List / tuple operations"].append("fallback:list_tuple")
        elif re.search(r"\bdict|dictionary|key|value\b", title_cue_text, flags=re.I):
            tags = ["Dictionary operations"]
            reasons["Dictionary operations"].append("fallback:dict")
        elif re.search(r"\btriangle|polygon|equation|polynomial|prime|lcm|progression|vector\b", title_cue_text, flags=re.I):
            tags = ["Mathematical / algorithmic"]
            reasons["Mathematical / algorithmic"].append("fallback:math_algo")
        else:
            tags = ["Arithmetic / conditionals"]
            reasons["Arithmetic / conditionals"].append("fallback:default_arithmetic_conditional")

    # Add related cross-tags only when very strong.
    if "Dictionary operations" in tags and "Data analysis / aggregation" not in tags and scores["Data analysis / aggregation"] >= 3.0:
        tags.append("Data analysis / aggregation")
    if "List / tuple operations" in tags and "Loops and iteration" not in tags and scores["Loops and iteration"] >= 3.0:
        tags.append("Loops and iteration")
    if "String manipulation" in tags and "Loops and iteration" not in tags and scores["Loops and iteration"] >= 4.0:
        tags.append("Loops and iteration")

    # Keep stable order by descending score then concept list order.
    tags = sorted(set(tags), key=lambda c: (-scores[c], CONCEPT_ORDER_PROXY[c], c))
    primary = tags[0]

    score_parts = []
    for c in sorted(CONCEPTS, key=lambda x: (-scores[x], CONCEPT_ORDER_PROXY[x])):
        if scores[c] > 0:
            score_parts.append(f"{CONCEPT_ID[c]}={scores[c]:.1f}")
    reason_parts = []
    for c in tags:
        rs = sorted(set(reasons[c]))
        if rs:
            reason_parts.append(f"{CONCEPT_ID[c]}:{' ; '.join(rs[:6])}")

    return pd.Series(
        {
            "primary_concept": primary,
            "concept_tags": tags,
            "concept_tags_pipe": " | ".join(tags),
            "concept_tag_count": len(tags),
            "concept_scores_summary": " | ".join(score_parts),
            "concept_tagging_reasons": " || ".join(reason_parts),
        }
    )


def build_question_concept_map() -> tuple[pd.DataFrame, pd.DataFrame]:
    qmeta = pd.read_csv(INPUTS.question_metadata)
    qmeta["problem_id"] = qmeta["problem_id"].astype(int)
    qmeta["question_title_norm_local"] = qmeta["question_title"].map(normalize_text)

    guide_cues = parse_guide_question_cues(INPUTS.guide_md)
    write_csv(guide_cues, OUT_DIR / "guide_question_cues_extracted.csv")

    q = qmeta.merge(guide_cues, on=["namespace", "problem_id"], how="left")
    q["guide_question_cue"] = q["guide_question_cue"].fillna("")
    q["guide_question_cue_norm"] = q["guide_question_cue_norm"].fillna("")
    q["guide_cue_count"] = q.get("guide_cue_count", 0).fillna(0).astype(int)

    tags_df = q.apply(classify_question_concepts, axis=1)
    q = pd.concat([q, tags_df], axis=1)

    q["has_guide_cue"] = q["guide_question_cue"].str.len() > 0
    q["concept_tags_csv"] = q["concept_tags"].map(lambda xs: "; ".join(xs))
    q["question_key"] = q["namespace"].astype(str) + "::" + q["problem_id"].astype(str)

    map_cols = [
        "namespace",
        "problem_id",
        "question_title",
        "question_title_norm_local",
        "guide_question_cue",
        "has_guide_cue",
        "has_skeleton_code",
        "num_public_tests",
        "num_private_tests",
        "primary_concept",
        "concept_tag_count",
        "concept_tags_pipe",
        "concept_tags_csv",
        "concept_scores_summary",
        "concept_tagging_reasons",
    ]
    question_map = q[map_cols].copy()
    question_map = question_map.sort_values(["namespace", "problem_id"]).reset_index(drop=True)

    exploded = (
        q[["namespace", "problem_id", "question_title", "primary_concept", "concept_tags"]]
        .explode("concept_tags")
        .rename(columns={"concept_tags": "concept"})
        .reset_index(drop=True)
    )
    exploded["is_primary_concept"] = exploded["concept"] == exploded["primary_concept"]
    exploded["concept_order_proxy"] = exploded["concept"].map(CONCEPT_ORDER_PROXY)
    exploded["concept_id"] = exploded["concept"].map(CONCEPT_ID)
    exploded = exploded.sort_values(["concept_order_proxy", "namespace", "problem_id"]).reset_index(drop=True)

    write_csv(question_map, OUT_DIR / "concept_question_map.csv")
    write_csv(exploded, OUT_DIR / "concept_question_tag_rows.csv")

    coverage_summary = pd.DataFrame(
        [
            {
                "metric": "question_rows",
                "value": int(len(question_map)),
                "note": "Expected 251 rows from analysis/question_metadata.csv",
            },
            {
                "metric": "guide_cue_covered_questions",
                "value": int(question_map["has_guide_cue"].sum()),
                "note": "Rows with parsed OPPE guide concise cue joined by namespace+problem_id",
            },
            {
                "metric": "questions_without_guide_cue",
                "value": int((~question_map["has_guide_cue"]).sum()),
                "note": "Tagged using title/text only",
            },
            {
                "metric": "untagged_questions",
                "value": int((question_map["concept_tag_count"] == 0).sum()),
                "note": "Should be zero after fallback tagging",
            },
            {
                "metric": "avg_tags_per_question",
                "value": round(float(question_map["concept_tag_count"].mean()), 4),
                "note": "Multi-tag density for concept map",
            },
            {
                "metric": "max_tags_per_question",
                "value": int(question_map["concept_tag_count"].max()),
                "note": "Maximum number of tags on a single question",
            },
        ]
    )
    write_csv(coverage_summary, OUT_DIR / "concept_tagging_coverage_summary.csv")

    examples = (
        exploded.groupby("concept", as_index=False)
        .agg(
            question_count=("question_title", "nunique"),
            example_titles=("question_title", lambda x: " || ".join(list(dict.fromkeys(map(str, x)))[:8])),
        )
        .sort_values("concept")
        .reset_index(drop=True)
    )
    write_csv(examples, OUT_DIR / "concept_tagging_examples_by_concept.csv")
    return question_map, exploded


def load_grm_rows() -> pd.DataFrame:
    cols = [
        "namespace",
        "problem_id",
        "student_id",
        "term",
        "wave",
        "question_title",
        "question_title_norm",
        "grm_basis",
        "grm_category",
        "category_public_best",
    ]
    df = pd.read_csv(INPUTS.grm_rows, usecols=cols)
    df = df[df["grm_category"].notna()].copy()
    df["problem_id"] = df["problem_id"].astype(int)
    df["grm_category"] = df["grm_category"].astype(float)
    return df


def build_student_question_concept_rows(grm: pd.DataFrame, concept_tags: pd.DataFrame) -> pd.DataFrame:
    merged = grm.merge(
        concept_tags[["namespace", "problem_id", "concept", "is_primary_concept"]],
        on=["namespace", "problem_id"],
        how="left",
        validate="many_to_many",
    )
    if merged["concept"].isna().any():
        missing = merged[merged["concept"].isna()][["namespace", "problem_id"]].drop_duplicates()
        raise RuntimeError(f"Missing concept tags for some question rows: {len(missing)} unique question keys")
    merged["cat0"] = (merged["grm_category"] == 0).astype(int)
    merged["cat1"] = (merged["grm_category"] == 1).astype(int)
    merged["cat2"] = (merged["grm_category"] == 2).astype(int)
    merged["any_public_pass"] = (merged["grm_category"] >= 1).astype(int)
    merged["all_public_pass"] = (merged["grm_category"] == 2).astype(int)
    return merged


def summarize_concept_mastery_rows(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    out = (
        df.groupby(group_cols + ["concept"], as_index=False)
        .agg(
            student_question_rows=("student_id", "size"),
            students=("student_id", "nunique"),
            questions=("problem_id", "nunique"),
            mean_grm_category=("grm_category", "mean"),
            pct_cat0=("cat0", "mean"),
            pct_cat1=("cat1", "mean"),
            pct_cat2=("cat2", "mean"),
            any_public_pass_rate=("any_public_pass", "mean"),
            all_public_pass_rate=("all_public_pass", "mean"),
            primary_tag_row_share=("is_primary_concept", "mean"),
        )
        .sort_values(group_cols + ["concept"])
        .reset_index(drop=True)
    )
    pct_cols = ["pct_cat0", "pct_cat1", "pct_cat2", "any_public_pass_rate", "all_public_pass_rate", "primary_tag_row_share"]
    out[pct_cols] = out[pct_cols] * 100.0
    return out


def add_mastery_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["concept_mastered_flag"] = df["mean_grm_category"] >= MASTERY_MEAN_GRM_THRESHOLD
    df["concept_some_mastery_flag"] = df["mean_grm_category"] >= 1.0
    df["concept_failed_flag"] = ~df["concept_mastered_flag"]
    return df


def build_student_concept_summaries(student_question_concepts: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    wave = (
        student_question_concepts.groupby(["term", "wave", "student_id", "concept"], as_index=False)
        .agg(
            question_rows=("grm_category", "size"),
            mean_grm_category=("grm_category", "mean"),
            median_grm_category=("grm_category", "median"),
            any_public_pass_rate=("any_public_pass", "mean"),
            all_public_pass_rate=("all_public_pass", "mean"),
            concept_row_cat0=("cat0", "sum"),
            concept_row_cat1=("cat1", "sum"),
            concept_row_cat2=("cat2", "sum"),
        )
    )
    wave["any_public_pass_rate"] *= 100.0
    wave["all_public_pass_rate"] *= 100.0
    wave = add_mastery_flags(wave)

    term = (
        student_question_concepts.groupby(["term", "student_id", "concept"], as_index=False)
        .agg(
            question_rows=("grm_category", "size"),
            distinct_waves=("wave", "nunique"),
            mean_grm_category=("grm_category", "mean"),
            median_grm_category=("grm_category", "median"),
            any_public_pass_rate=("any_public_pass", "mean"),
            all_public_pass_rate=("all_public_pass", "mean"),
            concept_row_cat0=("cat0", "sum"),
            concept_row_cat1=("cat1", "sum"),
            concept_row_cat2=("cat2", "sum"),
        )
    )
    term["any_public_pass_rate"] *= 100.0
    term["all_public_pass_rate"] *= 100.0
    term = add_mastery_flags(term)
    return wave, term


def _label_change(delta: float, tol: float = 1e-9) -> str:
    if delta > tol:
        return "improve"
    if delta < -tol:
        return "decline"
    return "same"


def build_within_term_concept_wave_changes(student_concept_wave: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    w1 = student_concept_wave[student_concept_wave["wave"] == "wave1"].copy()
    w2 = student_concept_wave[student_concept_wave["wave"] == "wave2"].copy()
    merged = w1.merge(
        w2,
        on=["term", "student_id", "concept"],
        how="inner",
        suffixes=("_wave1", "_wave2"),
    )
    merged["mean_grm_delta"] = merged["mean_grm_category_wave2"] - merged["mean_grm_category_wave1"]
    merged["all_public_pass_rate_delta"] = (
        merged["all_public_pass_rate_wave2"] - merged["all_public_pass_rate_wave1"]
    )
    merged["mastery_flag_delta"] = (
        merged["concept_mastered_flag_wave2"].astype(int) - merged["concept_mastered_flag_wave1"].astype(int)
    )
    merged["mean_grm_change_label"] = merged["mean_grm_delta"].map(_label_change)
    merged["mastery_flag_change_label"] = merged["mastery_flag_delta"].map(_label_change)

    summary = (
        merged.groupby(["term", "concept"], as_index=False)
        .agg(
            paired_students=("student_id", "nunique"),
            mean_mean_grm_delta=("mean_grm_delta", "mean"),
            median_mean_grm_delta=("mean_grm_delta", "median"),
            mean_all_public_pass_rate_delta=("all_public_pass_rate_delta", "mean"),
            pct_mastery_improve=("mastery_flag_delta", lambda s: float((s > 0).mean()) * 100.0),
            pct_mastery_same=("mastery_flag_delta", lambda s: float((s == 0).mean()) * 100.0),
            pct_mastery_decline=("mastery_flag_delta", lambda s: float((s < 0).mean()) * 100.0),
            pct_mean_grm_improve=("mean_grm_delta", lambda s: float((s > 0).mean()) * 100.0),
            pct_mean_grm_same=("mean_grm_delta", lambda s: float((s == 0).mean()) * 100.0),
            pct_mean_grm_decline=("mean_grm_delta", lambda s: float((s < 0).mean()) * 100.0),
        )
        .sort_values(["term", "concept"])
        .reset_index(drop=True)
    )
    return merged, summary


def build_concept_construct_presence(
    grm: pd.DataFrame, concept_tags: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Attempt-level ever-construct presence from Step 5 first-appearance rows.
    ac = pd.read_csv(INPUTS.attempt_construct_first, usecols=["namespace", "problem_id", "student_id", "construct"])
    ac["problem_id"] = ac["problem_id"].astype(int)
    ac = ac[ac["construct"].isin(TRACKED_CONSTRUCTS)].copy()
    if ac.empty:
        raise RuntimeError("No tracked constructs found in attempt_construct_first_appearance.csv")

    ac["present"] = 1
    flags = (
        ac.pivot_table(
            index=["namespace", "problem_id", "student_id"],
            columns="construct",
            values="present",
            aggfunc="max",
            fill_value=0,
        )
        .reset_index()
    )
    flags.columns = [str(c) for c in flags.columns]
    for c in TRACKED_CONSTRUCTS:
        if c not in flags.columns:
            flags[c] = 0
        flags[f"ever_{c}"] = flags[c].astype(int)
    drop_raw = [c for c in TRACKED_CONSTRUCTS if c in flags.columns]
    flags = flags.drop(columns=drop_raw)

    attempt_base = grm[["namespace", "problem_id", "student_id", "term", "wave", "grm_category"]].copy()
    attempt_base["problem_id"] = attempt_base["problem_id"].astype(int)
    attempt_base["all_public_pass"] = (attempt_base["grm_category"] == 2).astype(int)
    attempt_base["any_public_pass"] = (attempt_base["grm_category"] >= 1).astype(int)
    attempt_base = attempt_base.merge(flags, on=["namespace", "problem_id", "student_id"], how="left")
    ever_cols = [f"ever_{c}" for c in TRACKED_CONSTRUCTS]
    for c in ever_cols:
        if c not in attempt_base:
            attempt_base[c] = 0
    attempt_base[ever_cols] = attempt_base[ever_cols].fillna(0).astype(int)

    concept_attempt_rows = attempt_base.merge(
        concept_tags[["namespace", "problem_id", "concept", "is_primary_concept"]],
        on=["namespace", "problem_id"],
        how="left",
    )
    if concept_attempt_rows["concept"].isna().any():
        raise RuntimeError("Missing concept tags while building construct usage table")

    global_construct_summary = pd.read_csv(INPUTS.construct_summary_global)
    return flags, concept_attempt_rows, global_construct_summary


def classify_gap_type(usage_rate_pct: float, mastery_users_pct: float) -> str:
    # Fixed thresholds for interpretability (reported in README).
    low_usage = usage_rate_pct < 15.0
    high_usage = usage_rate_pct >= 35.0
    high_mastery = mastery_users_pct >= 70.0
    low_mastery = mastery_users_pct < 55.0

    if low_usage and high_mastery:
        return "Low usage, high mastery when used"
    if high_usage and low_mastery:
        return "High usage, low mastery"
    if low_usage and low_mastery:
        return "Low usage, low mastery"
    return "Mixed / moderate"


def summarize_focus_usage_mastery(
    attempt_rows: pd.DataFrame,
    focus_rows: list[dict[str, Any]],
    group_context_cols: list[str] | None = None,
) -> pd.DataFrame:
    group_context_cols = group_context_cols or []
    out_rows: list[dict[str, Any]] = []
    for spec in focus_rows:
        cons = spec["constructs"]
        ever_cols = [f"ever_{c}" for c in cons]
        tmp = attempt_rows.copy()
        for ec in ever_cols:
            if ec not in tmp:
                tmp[ec] = 0
        tmp["uses_focus_construct"] = tmp[ever_cols].max(axis=1).astype(int)

        groupby_cols = list(group_context_cols)
        grouped = tmp.groupby(groupby_cols, dropna=False) if groupby_cols else [((), tmp)]

        for gkey, gdf in grouped:
            if not isinstance(gkey, tuple):
                gkey = (gkey,)
            base: dict[str, Any] = {}
            for i, col in enumerate(groupby_cols):
                base[col] = gkey[i]
            users = gdf[gdf["uses_focus_construct"] == 1]
            nonusers = gdf[gdf["uses_focus_construct"] == 0]
            usage_rate = float(gdf["uses_focus_construct"].mean() * 100.0) if len(gdf) else np.nan
            mastery_users = float(users["all_public_pass"].mean() * 100.0) if len(users) else np.nan
            mastery_nonusers = float(nonusers["all_public_pass"].mean() * 100.0) if len(nonusers) else np.nan
            row = {
                **base,
                "focus_label": spec["focus_label"],
                "focus_group": spec["focus_group"],
                "relevant_constructs": ", ".join(cons),
                "proxy_quality": spec.get("proxy_quality", ""),
                "note": spec.get("note", ""),
                "attempt_rows": int(len(gdf)),
                "users": int(len(users)),
                "nonusers": int(len(nonusers)),
                "usage_rate_ever_used_in_attempt_pct": usage_rate,
                "all_public_pass_rate_among_users_pct": mastery_users,
                "all_public_pass_rate_among_nonusers_pct": mastery_nonusers,
                "mean_grm_among_users": float(users["grm_category"].mean()) if len(users) else np.nan,
                "mean_grm_among_nonusers": float(nonusers["grm_category"].mean()) if len(nonusers) else np.nan,
                "gap_type": classify_gap_type(usage_rate, mastery_users) if not np.isnan(usage_rate) and not np.isnan(mastery_users) else "Insufficient users",
            }
            out_rows.append(row)

    out = pd.DataFrame(out_rows)
    sort_cols = [c for c in group_context_cols if c in out.columns] + ["focus_label"]
    if not out.empty:
        out = out.sort_values(sort_cols).reset_index(drop=True)
    return out


def build_prerequisite_graph(student_concept_term: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = student_concept_term[
        [
            "term",
            "student_id",
            "concept",
            "question_rows",
            "mean_grm_category",
            "concept_mastered_flag",
            "concept_some_mastery_flag",
        ]
    ].copy()
    base["exposed"] = True

    rows: list[dict[str, Any]] = []
    for a in CONCEPTS:
        a_df = base[base["concept"] == a].copy()
        a_df = a_df.rename(
            columns={
                "question_rows": "question_rows_a",
                "mean_grm_category": "mean_grm_a",
                "concept_mastered_flag": "mastered_a",
                "concept_some_mastery_flag": "some_mastery_a",
                "exposed": "exposed_a",
            }
        ).drop(columns=["concept"])
        for b in CONCEPTS:
            if a == b:
                continue
            b_df = base[base["concept"] == b].copy()
            b_df = b_df.rename(
                columns={
                    "question_rows": "question_rows_b",
                    "mean_grm_category": "mean_grm_b",
                    "concept_mastered_flag": "mastered_b",
                    "concept_some_mastery_flag": "some_mastery_b",
                    "exposed": "exposed_b",
                }
            ).drop(columns=["concept"])

            pair = a_df.merge(b_df, on=["term", "student_id"], how="inner")
            if pair.empty:
                rows.append(
                    {
                        "concept_a": a,
                        "concept_b": b,
                        "support_student_terms_both_exposed": 0,
                        "a_master_count": 0,
                        "a_fail_count": 0,
                        "p_b_master_given_a_master": np.nan,
                        "p_b_master_given_a_fail": np.nan,
                        "delta_master_prob": np.nan,
                        "p_b_some_mastery_given_a_master": np.nan,
                        "p_b_some_mastery_given_a_fail": np.nan,
                        "delta_some_mastery_prob": np.nan,
                        "mean_grm_b_given_a_master": np.nan,
                        "mean_grm_b_given_a_fail": np.nan,
                        "delta_mean_grm_b": np.nan,
                        "proxy_order_a": CONCEPT_ORDER_PROXY[a],
                        "proxy_order_b": CONCEPT_ORDER_PROXY[b],
                    }
                )
                continue

            a_master = pair[pair["mastered_a"]]
            a_fail = pair[~pair["mastered_a"]]
            p_b_master_given_a_master = float(a_master["mastered_b"].mean()) if len(a_master) else np.nan
            p_b_master_given_a_fail = float(a_fail["mastered_b"].mean()) if len(a_fail) else np.nan
            p_b_some_given_a_master = float(a_master["some_mastery_b"].mean()) if len(a_master) else np.nan
            p_b_some_given_a_fail = float(a_fail["some_mastery_b"].mean()) if len(a_fail) else np.nan
            mean_b_a_master = float(a_master["mean_grm_b"].mean()) if len(a_master) else np.nan
            mean_b_a_fail = float(a_fail["mean_grm_b"].mean()) if len(a_fail) else np.nan

            rows.append(
                {
                    "concept_a": a,
                    "concept_b": b,
                    "support_student_terms_both_exposed": int(len(pair)),
                    "a_master_count": int(len(a_master)),
                    "a_fail_count": int(len(a_fail)),
                    "p_b_master_given_a_master": p_b_master_given_a_master,
                    "p_b_master_given_a_fail": p_b_master_given_a_fail,
                    "delta_master_prob": (
                        p_b_master_given_a_master - p_b_master_given_a_fail
                        if not np.isnan(p_b_master_given_a_master) and not np.isnan(p_b_master_given_a_fail)
                        else np.nan
                    ),
                    "p_b_some_mastery_given_a_master": p_b_some_given_a_master,
                    "p_b_some_mastery_given_a_fail": p_b_some_given_a_fail,
                    "delta_some_mastery_prob": (
                        p_b_some_given_a_master - p_b_some_given_a_fail
                        if not np.isnan(p_b_some_given_a_master) and not np.isnan(p_b_some_given_a_fail)
                        else np.nan
                    ),
                    "mean_grm_b_given_a_master": mean_b_a_master,
                    "mean_grm_b_given_a_fail": mean_b_a_fail,
                    "delta_mean_grm_b": (
                        mean_b_a_master - mean_b_a_fail
                        if not np.isnan(mean_b_a_master) and not np.isnan(mean_b_a_fail)
                        else np.nan
                    ),
                    "proxy_order_a": CONCEPT_ORDER_PROXY[a],
                    "proxy_order_b": CONCEPT_ORDER_PROXY[b],
                }
            )

    full = pd.DataFrame(rows)
    if full.empty:
        return full, full, full

    # Convert probabilities to percentages for outputs.
    pct_cols = [
        "p_b_master_given_a_master",
        "p_b_master_given_a_fail",
        "delta_master_prob",
        "p_b_some_mastery_given_a_master",
        "p_b_some_mastery_given_a_fail",
        "delta_some_mastery_prob",
    ]
    full[pct_cols] = full[pct_cols] * 100.0

    # Candidate edge heuristic (empirical prerequisite signal), with directional dominance:
    # keep only the stronger direction for each unordered concept pair.
    candidates = full.copy()
    candidates["pair_key"] = candidates.apply(
        lambda r: " || ".join(sorted([str(r["concept_a"]), str(r["concept_b"])])), axis=1
    )
    reverse = candidates[
        ["concept_a", "concept_b", "delta_master_prob", "delta_mean_grm_b"]
    ].rename(
        columns={
            "concept_a": "concept_b",
            "concept_b": "concept_a",
            "delta_master_prob": "reverse_delta_master_prob",
            "delta_mean_grm_b": "reverse_delta_mean_grm_b",
        }
    )
    candidates = candidates.merge(reverse, on=["concept_a", "concept_b"], how="left")
    candidates["direction_margin_master_prob"] = (
        candidates["delta_master_prob"] - candidates["reverse_delta_master_prob"]
    )
    candidates["direction_margin_mean_grm"] = (
        candidates["delta_mean_grm_b"] - candidates["reverse_delta_mean_grm_b"]
    )
    candidates["is_stronger_direction_for_pair"] = (
        candidates.groupby("pair_key")["delta_master_prob"].transform("max") == candidates["delta_master_prob"]
    )
    # Break ties deterministically by proxy order + concept label.
    candidates = candidates.sort_values(
        [
            "pair_key",
            "delta_master_prob",
            "delta_mean_grm_b",
            "concept_a",
            "concept_b",
        ],
        ascending=[True, False, False, True, True],
    )
    candidates["pair_rank"] = candidates.groupby("pair_key").cumcount() + 1

    candidates["candidate_edge_flag"] = (
        (candidates["pair_rank"] == 1)
        & (candidates["support_student_terms_both_exposed"] >= 500)
        & (candidates["a_master_count"] >= 100)
        & (candidates["a_fail_count"] >= 100)
        & (candidates["delta_master_prob"] >= 15.0)
        & (candidates["delta_mean_grm_b"] >= 0.25)
        & (candidates["direction_margin_master_prob"] >= 5.0)
    )
    candidates["proxy_order_alignment"] = np.where(
        candidates["proxy_order_a"] < candidates["proxy_order_b"],
        "aligned_or_same_direction",
        "reverse_vs_proxy_order",
    )
    edge_candidates = (
        candidates[candidates["candidate_edge_flag"]]
        .sort_values(
            [
                "delta_master_prob",
                "direction_margin_master_prob",
                "delta_mean_grm_b",
                "support_student_terms_both_exposed",
            ],
            ascending=[False, False, False, False],
        )
        .reset_index(drop=True)
    )
    misalign = edge_candidates[edge_candidates["proxy_order_alignment"] == "reverse_vs_proxy_order"].copy()
    return full, edge_candidates, misalign


def build_repeat_student_concept_profiles(
    student_concept_term: pd.DataFrame, grm: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Recreate Step 8-style substantive term participation threshold from GRM rows.
    grm_term_basis = grm[grm["wave"].isin(["wave1", "wave2"])].copy()
    term_part = (
        grm_term_basis.groupby(["term", "student_id"], as_index=False)
        .agg(term_question_rows=("grm_category", "size"))
        .assign(substantive_term_participation=lambda d: d["term_question_rows"] >= SUBSTANTIVE_MIN_QUESTION_ROWS)
    )
    term_part = term_part[term_part["substantive_term_participation"]].copy()

    pair_specs = [("25t1", "25t2"), ("25t2", "25t3")]
    pair_rows: list[pd.DataFrame] = []
    long_rows_all: list[pd.DataFrame] = []
    retention_rows: list[pd.DataFrame] = []

    concept_term = student_concept_term.copy()
    concept_term["concept_status"] = np.where(
        concept_term["concept_mastered_flag"], "mastered", "not_mastered"
    )

    for term_from, term_to in pair_specs:
        src = term_part[term_part["term"] == term_from][["student_id"]]
        dst = term_part[term_part["term"] == term_to][["student_id"]]
        repeat = src.merge(dst, on="student_id", how="inner").drop_duplicates()
        repeat["term_pair"] = f"{term_from}->{term_to}"
        repeat["term_from"] = term_from
        repeat["term_to"] = term_to

        c_from = concept_term[concept_term["term"] == term_from].drop(columns=["term"]).copy()
        c_to = concept_term[concept_term["term"] == term_to].drop(columns=["term"]).copy()

        # Long paired concept statuses (union of concepts across terms for each student).
        long = (
            repeat[["student_id", "term_pair", "term_from", "term_to"]]
            .merge(c_from.add_suffix("_from"), left_on="student_id", right_on="student_id_from", how="left")
            .drop(columns=["student_id_from"])
        )
        long = long.rename(columns={"concept_from": "concept"})
        # merge target on same concept
        long = long.merge(
            c_to.add_suffix("_to"),
            left_on=["student_id", "concept"],
            right_on=["student_id_to", "concept_to"],
            how="outer",
        )
        # Restore repeat metadata for rows introduced by right side only.
        if "student_id_to" in long:
            long["student_id"] = long["student_id"].fillna(long["student_id_to"])
        long = long.merge(repeat[["student_id", "term_pair", "term_from", "term_to"]], on="student_id", how="left", suffixes=("", "_rep"))
        for c in ["term_pair", "term_from", "term_to"]:
            rep_col = f"{c}_rep"
            if rep_col in long.columns:
                long[c] = long[c].fillna(long[rep_col])
                long = long.drop(columns=[rep_col])
        if "concept" not in long.columns:
            long["concept"] = long["concept_to"]
        long["concept"] = long["concept"].fillna(long.get("concept_to"))
        if "concept_to" in long.columns:
            long = long.drop(columns=["concept_to"])
        if "student_id_to" in long.columns:
            long = long.drop(columns=["student_id_to"])

        # Keep only repeat students.
        long = long[long["term_pair"].notna()].copy()

        # Exposure/mastery statuses.
        long["assessed_from"] = long["question_rows_from"].notna()
        long["assessed_to"] = long["question_rows_to"].notna()
        long["assessed_both_terms"] = long["assessed_from"] & long["assessed_to"]
        long["status_from"] = np.where(
            ~long["assessed_from"],
            "not_assessed",
            np.where(long["concept_mastered_flag_from"].fillna(False), "mastered", "not_mastered"),
        )
        long["status_to"] = np.where(
            ~long["assessed_to"],
            "not_assessed",
            np.where(long["concept_mastered_flag_to"].fillna(False), "mastered", "not_mastered"),
        )
        long["transition_both_assessed"] = np.where(
            long["assessed_both_terms"],
            long["status_from"] + " -> " + long["status_to"],
            "not_assessed_both",
        )
        long["retained_mastery_flag"] = long["assessed_both_terms"] & (long["status_from"] == "mastered") & (long["status_to"] == "mastered")
        long["newly_mastered_flag"] = long["assessed_both_terms"] & (long["status_from"] == "not_mastered") & (long["status_to"] == "mastered")
        long["regressed_mastery_flag"] = long["assessed_both_terms"] & (long["status_from"] == "mastered") & (long["status_to"] == "not_mastered")
        long["persistently_not_mastered_flag"] = long["assessed_both_terms"] & (long["status_from"] == "not_mastered") & (long["status_to"] == "not_mastered")
        long_rows_all.append(long)

        # Student-level profile strings (concept lists).
        profiles = []
        for sid, sdf in long.groupby("student_id", sort=False):
            def concept_list(mask: pd.Series) -> str:
                vals = sorted(sdf.loc[mask, "concept"].dropna().astype(str).unique(), key=lambda c: CONCEPT_ORDER_PROXY.get(c, 999))
                return "; ".join(vals)

            row = {
                "term_pair": f"{term_from}->{term_to}",
                "term_from": term_from,
                "term_to": term_to,
                "student_id": sid,
                "concepts_assessed_from": concept_list(sdf["assessed_from"]),
                "concepts_assessed_to": concept_list(sdf["assessed_to"]),
                "mastered_concepts_from": concept_list(sdf["status_from"] == "mastered"),
                "mastered_concepts_to": concept_list(sdf["status_to"] == "mastered"),
                "retained_mastery_concepts": concept_list(sdf["retained_mastery_flag"]),
                "newly_mastered_concepts_assessed_both": concept_list(sdf["newly_mastered_flag"]),
                "regressed_mastery_concepts_assessed_both": concept_list(sdf["regressed_mastery_flag"]),
                "persistently_not_mastered_concepts_assessed_both": concept_list(sdf["persistently_not_mastered_flag"]),
                "assessed_both_concept_count": int(sdf["assessed_both_terms"].sum()),
                "mastered_from_count": int((sdf["status_from"] == "mastered").sum()),
                "mastered_to_count": int((sdf["status_to"] == "mastered").sum()),
                "retained_mastery_count": int(sdf["retained_mastery_flag"].sum()),
                "newly_mastered_count_assessed_both": int(sdf["newly_mastered_flag"].sum()),
                "regressed_mastery_count_assessed_both": int(sdf["regressed_mastery_flag"].sum()),
                "persistently_not_mastered_count_assessed_both": int(sdf["persistently_not_mastered_flag"].sum()),
            }
            profiles.append(row)
        pair_rows.append(pd.DataFrame(profiles))

        # Concept-level retention/acquisition summary for this pair.
        ret = (
            long.groupby("concept", as_index=False)
            .agg(
                repeat_students=("student_id", "nunique"),
                assessed_both_students=("assessed_both_terms", "sum"),
                source_mastered_students=("status_from", lambda s: int((s == "mastered").sum())),
                source_not_mastered_students=("status_from", lambda s: int((s == "not_mastered").sum())),
                retained_mastery_students=("retained_mastery_flag", "sum"),
                newly_mastered_students=("newly_mastered_flag", "sum"),
                regressed_mastery_students=("regressed_mastery_flag", "sum"),
                persistently_not_mastered_students=("persistently_not_mastered_flag", "sum"),
            )
            .copy()
        )
        ret["term_pair"] = f"{term_from}->{term_to}"
        ret["retention_rate_given_mastered_from_pct"] = np.where(
            ret["source_mastered_students"] > 0,
            ret["retained_mastery_students"] / ret["source_mastered_students"] * 100.0,
            np.nan,
        )
        ret["acquisition_rate_given_not_mastered_from_pct"] = np.where(
            ret["source_not_mastered_students"] > 0,
            ret["newly_mastered_students"] / ret["source_not_mastered_students"] * 100.0,
            np.nan,
        )
        ret["regression_rate_given_mastered_from_pct"] = np.where(
            ret["source_mastered_students"] > 0,
            ret["regressed_mastery_students"] / ret["source_mastered_students"] * 100.0,
            np.nan,
        )
        retention_rows.append(ret)

    pair_profiles = pd.concat(pair_rows, ignore_index=True) if pair_rows else pd.DataFrame()
    long_pairs = pd.concat(long_rows_all, ignore_index=True) if long_rows_all else pd.DataFrame()
    retention_summary = pd.concat(retention_rows, ignore_index=True) if retention_rows else pd.DataFrame()

    pair_summary = (
        pair_profiles.groupby("term_pair", as_index=False)
        .agg(
            repeat_students=("student_id", "nunique"),
            mean_assessed_both_concept_count=("assessed_both_concept_count", "mean"),
            mean_mastered_from_count=("mastered_from_count", "mean"),
            mean_mastered_to_count=("mastered_to_count", "mean"),
            mean_newly_mastered_count_assessed_both=("newly_mastered_count_assessed_both", "mean"),
            mean_regressed_mastery_count_assessed_both=("regressed_mastery_count_assessed_both", "mean"),
            pct_any_newly_mastered=("newly_mastered_count_assessed_both", lambda s: float((s > 0).mean()) * 100.0),
            pct_any_regressed_mastery=("regressed_mastery_count_assessed_both", lambda s: float((s > 0).mean()) * 100.0),
        )
        .sort_values("term_pair")
        .reset_index(drop=True)
    ) if not pair_profiles.empty else pd.DataFrame()

    return pair_profiles, long_pairs, retention_summary, pair_summary


def build_s2_concept_decomposition(
    concept_tags: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    conn = make_conn()
    public_state_path = str(INPUTS.public_state_rows).replace("\\", "/")
    selected_path = str(INPUTS.selected_snapshot_rows).replace("\\", "/")
    final_public = conn.execute(
        f"""
        WITH ranked AS (
          SELECT
            namespace,
            problem_id,
            student_id,
            term,
            wave,
            question_title,
            public_run_index,
            seconds_since_start,
            process_state,
            is_parseable,
            num_test_passed,
            test_case_count,
            ROW_NUMBER() OVER (
              PARTITION BY namespace, problem_id, student_id
              ORDER BY public_run_index DESC NULLS LAST, seconds_since_start DESC NULLS LAST
            ) AS rn
          FROM read_parquet('{public_state_path}')
        )
        SELECT
          namespace,
          CAST(problem_id AS BIGINT) AS problem_id,
          student_id,
          term,
          wave,
          question_title,
          public_run_index,
          seconds_since_start,
          process_state,
          is_parseable,
          num_test_passed,
          test_case_count
        FROM ranked
        WHERE rn = 1
        """
    ).df()
    conn.close()

    final_public["problem_id"] = final_public["problem_id"].astype(int)
    final_public["final_public_s2_flag"] = final_public["process_state"] == "S2_parseable_zero"
    final_s2 = final_public[final_public["final_public_s2_flag"]].copy()

    selected_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "selected_event_type",
        "selected_evaluation_type",
        "selected_is_parseable",
        "selected_num_test_passed",
        "selected_test_case_count",
        "selected_tree_sitter_parseable",
        "selected_summary",
        "ts_has_for_loop",
        "ts_has_while_loop",
        "ts_has_if_stmt",
        "ts_has_list_comp",
        "ts_has_dict_comp",
        "ts_has_try_stmt",
        "ts_has_print_call",
        "ts_has_import_stmt",
        "ts_has_import_from_stmt",
    ]
    conn2 = make_conn()
    selected_cols_sql = ",\n        ".join(selected_cols)
    selected_path_sql = str(INPUTS.selected_snapshot_rows).replace("\\", "/")
    selected = conn2.execute(
        f"""
        SELECT
          {selected_cols_sql}
        FROM read_csv_auto('{selected_path_sql}', SAMPLE_SIZE=-1)
        """
    ).df()
    conn2.close()
    selected["problem_id"] = selected["problem_id"].astype(int)
    for c in [c for c in selected.columns if c.startswith("ts_has_")]:
        selected[c] = selected[c].fillna(False).astype(bool)

    s2 = final_s2.merge(selected, on=["namespace", "problem_id", "student_id"], how="left", validate="one_to_one")
    s2["selected_snapshot_present"] = s2["selected_event_type"].notna()
    s2["selected_snapshot_public_test_run"] = (s2["selected_event_type"] == "test_run") & (
        s2["selected_evaluation_type"] == "public"
    )
    s2["selected_snapshot_s2_like"] = (
        s2["selected_snapshot_public_test_run"]
        & (s2["selected_is_parseable"].fillna(False))
        & (s2["selected_num_test_passed"].fillna(-1) == 0)
        & (s2["selected_test_case_count"].fillna(0) > 0)
    )

    s2_concepts = s2.merge(
        concept_tags[["namespace", "problem_id", "concept", "is_primary_concept"]],
        on=["namespace", "problem_id"],
        how="left",
    )
    if s2_concepts["concept"].isna().any():
        raise RuntimeError("Missing concept tags in S2 decomposition join")

    # Evaluate concept proxy construct presence.
    present_flags = []
    proxy_notes = []
    proxy_qualities = []
    constructs_used = []
    for _, row in s2_concepts.iterrows():
        spec = CONCEPT_CONSTRUCT_PROXIES.get(row["concept"])
        if not spec:
            proxy_qualities.append("none")
            proxy_notes.append("No proxy configured")
            constructs_used.append("")
            present_flags.append(np.nan)
            continue
        cons = spec["constructs"]
        any_present = False
        for c in cons:
            col = f"ts_has_{c}"
            if col in s2_concepts.columns and bool(row.get(col, False)):
                any_present = True
                break
        proxy_qualities.append(spec["proxy_quality"])
        proxy_notes.append(spec["proxy_note"])
        constructs_used.append(", ".join(cons))
        present_flags.append(any_present)

    s2_concepts["relevant_construct_proxy_list"] = constructs_used
    s2_concepts["construct_proxy_quality"] = proxy_qualities
    s2_concepts["construct_proxy_note"] = proxy_notes
    s2_concepts["relevant_construct_present_proxy"] = pd.Series(present_flags, dtype="boolean")
    s2_concepts["construct_proxy_defined_flag"] = s2_concepts["construct_proxy_quality"] != "none"
    s2_concepts["s2_failure_decomposition_proxy"] = np.select(
        [
            ~s2_concepts["construct_proxy_defined_flag"],
            s2_concepts["relevant_construct_present_proxy"].fillna(False),
            s2_concepts["construct_proxy_defined_flag"]
            & ~s2_concepts["relevant_construct_present_proxy"].fillna(False),
        ],
        [
            "No construct proxy available",
            "Application gap proxy (relevant construct present)",
            "Selection gap proxy (relevant construct absent)",
        ],
        default="Unknown",
    )

    detail_cols = [
        "namespace",
        "problem_id",
        "student_id",
        "term",
        "wave",
        "question_title",
        "concept",
        "is_primary_concept",
        "public_run_index",
        "process_state",
        "is_parseable",
        "num_test_passed",
        "test_case_count",
        "selected_snapshot_present",
        "selected_snapshot_public_test_run",
        "selected_snapshot_s2_like",
        "selected_event_type",
        "selected_evaluation_type",
        "selected_is_parseable",
        "selected_num_test_passed",
        "selected_test_case_count",
        "selected_tree_sitter_parseable",
        "relevant_construct_proxy_list",
        "construct_proxy_quality",
        "construct_proxy_note",
        "relevant_construct_present_proxy",
        "s2_failure_decomposition_proxy",
    ]
    s2_detail = s2_concepts[detail_cols].copy()

    summary = (
        s2_detail.groupby(["concept", "construct_proxy_quality", "s2_failure_decomposition_proxy"], as_index=False)
        .agg(
            s2_rows=("student_id", "size"),
            students=("student_id", "nunique"),
            questions=("problem_id", "nunique"),
            selected_snapshot_matching_final_s2_like_rows=("selected_snapshot_s2_like", "sum"),
            selected_snapshot_public_test_run_rows=("selected_snapshot_public_test_run", "sum"),
        )
    )
    concept_totals = (
        s2_detail.groupby("concept", as_index=False)
        .agg(concept_s2_rows=("student_id", "size"), concept_students=("student_id", "nunique"))
    )
    summary = summary.merge(concept_totals, on="concept", how="left")
    summary["pct_of_concept_s2_rows"] = np.where(
        summary["concept_s2_rows"] > 0, summary["s2_rows"] / summary["concept_s2_rows"] * 100.0, np.nan
    )
    summary["pct_rows_selected_snapshot_s2_like"] = np.where(
        summary["s2_rows"] > 0,
        summary["selected_snapshot_matching_final_s2_like_rows"] / summary["s2_rows"] * 100.0,
        np.nan,
    )
    summary = summary.sort_values(["concept", "s2_rows"], ascending=[True, False]).reset_index(drop=True)

    # Higher-fidelity subset where selected snapshot is itself an S2-like public test_run.
    s2_aligned = s2_detail[s2_detail["selected_snapshot_s2_like"] == True].copy()  # noqa: E712
    s2_aligned_attempts = s2[s2["selected_snapshot_s2_like"] == True].copy()  # noqa: E712
    if s2_aligned.empty:
        aligned_summary = pd.DataFrame(columns=summary.columns)
        aligned_rollup = pd.DataFrame(
            columns=[
                "concept",
                "Application gap proxy (relevant construct present)",
                "Selection gap proxy (relevant construct absent)",
                "proxy_classified_rows",
                "pct_application_gap_proxy",
                "pct_selection_gap_proxy",
            ]
        )
    else:
        aligned_summary = (
            s2_aligned.groupby(["concept", "construct_proxy_quality", "s2_failure_decomposition_proxy"], as_index=False)
            .agg(
                s2_rows=("student_id", "size"),
                students=("student_id", "nunique"),
                questions=("problem_id", "nunique"),
                selected_snapshot_matching_final_s2_like_rows=("selected_snapshot_s2_like", "sum"),
                selected_snapshot_public_test_run_rows=("selected_snapshot_public_test_run", "sum"),
            )
        )
        aligned_totals = (
            s2_aligned.groupby("concept", as_index=False)
            .agg(concept_s2_rows=("student_id", "size"), concept_students=("student_id", "nunique"))
        )
        aligned_summary = aligned_summary.merge(aligned_totals, on="concept", how="left")
        aligned_summary["pct_of_concept_s2_rows"] = np.where(
            aligned_summary["concept_s2_rows"] > 0,
            aligned_summary["s2_rows"] / aligned_summary["concept_s2_rows"] * 100.0,
            np.nan,
        )
        aligned_summary["pct_rows_selected_snapshot_s2_like"] = 100.0
        aligned_summary = aligned_summary.sort_values(["concept", "s2_rows"], ascending=[True, False]).reset_index(drop=True)

        aligned_rollup = (
            aligned_summary[aligned_summary["construct_proxy_quality"] != "none"]
            .pivot_table(
                index="concept",
                columns="s2_failure_decomposition_proxy",
                values="s2_rows",
                aggfunc="sum",
                fill_value=0,
            )
            .reset_index()
        )
        for col in [
            "Application gap proxy (relevant construct present)",
            "Selection gap proxy (relevant construct absent)",
        ]:
            if col not in aligned_rollup.columns:
                aligned_rollup[col] = 0
        aligned_rollup["proxy_classified_rows"] = (
            aligned_rollup["Application gap proxy (relevant construct present)"]
            + aligned_rollup["Selection gap proxy (relevant construct absent)"]
        )
        aligned_rollup["pct_application_gap_proxy"] = np.where(
            aligned_rollup["proxy_classified_rows"] > 0,
            aligned_rollup["Application gap proxy (relevant construct present)"]
            / aligned_rollup["proxy_classified_rows"]
            * 100.0,
            np.nan,
        )
        aligned_rollup["pct_selection_gap_proxy"] = np.where(
            aligned_rollup["proxy_classified_rows"] > 0,
            aligned_rollup["Selection gap proxy (relevant construct absent)"]
            / aligned_rollup["proxy_classified_rows"]
            * 100.0,
            np.nan,
        )

    alignment_summary = pd.DataFrame(
        [
            {
                "metric": "final_public_s2_attempts",
                "value": int(final_s2.shape[0]),
                "note": "Latest public test_run state per student-question is S2_parseable_zero",
            },
            {
                "metric": "final_public_s2_with_selected_snapshot",
                "value": int(s2["selected_snapshot_present"].sum()),
                "note": "Joined to selected snapshot taxonomy row",
            },
            {
                "metric": "final_public_s2_selected_snapshot_public_test_run",
                "value": int(s2["selected_snapshot_public_test_run"].sum()),
                "note": "Selected snapshot itself is a public test_run row",
            },
            {
                "metric": "final_public_s2_selected_snapshot_s2_like",
                "value": int(s2["selected_snapshot_s2_like"].sum()),
                "note": "Selected snapshot matches S2-like conditions on public test_run",
            },
            {
                "metric": "final_public_s2_selected_snapshot_s2_like_pct",
                "value": round(float(s2["selected_snapshot_s2_like"].mean() * 100.0), 4) if len(s2) else np.nan,
                "note": "Alignment rate for using selected snapshot constructs as S2 proxy",
            },
            {
                "metric": "final_public_s2_aligned_proxy_attempts",
                "value": int(len(s2_aligned_attempts)),
                "note": "Attempt rows retained when restricting decomposition to selected_snapshot_s2_like",
            },
            {
                "metric": "final_public_s2_aligned_proxy_concept_tag_rows",
                "value": int(len(s2_aligned)),
                "note": "Concept-tag rows retained when restricting decomposition to selected_snapshot_s2_like",
            },
        ]
    )
    return s2_detail, summary, alignment_summary, aligned_summary, aligned_rollup


def build_step9_key_metrics(
    question_map: pd.DataFrame,
    question_tags: pd.DataFrame,
    concept_mastery_overall: pd.DataFrame,
    prereq_edges: pd.DataFrame,
    prereq_misalign: pd.DataFrame,
    repeat_pair_summary: pd.DataFrame,
    s2_alignment: pd.DataFrame,
    s2_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(group: str, name: str, value: Any, unit: str, note: str) -> None:
        rows.append(
            {
                "metric_group": group,
                "metric_name": name,
                "value": value,
                "unit": unit,
                "note": note,
            }
        )

    add("Concept map", "question_rows", int(len(question_map)), "questions", "Rows in concept_question_map.csv")
    add(
        "Concept map",
        "avg_tags_per_question",
        round(float(question_map["concept_tag_count"].mean()), 4),
        "tags",
        "Mean number of concept tags per question",
    )
    add(
        "Concept map",
        "untagged_questions",
        int((question_map["concept_tag_count"] == 0).sum()),
        "questions",
        "Should be zero after fallback tagging",
    )
    add(
        "Concept map",
        "guide_cue_coverage_questions",
        int(question_map["has_guide_cue"].sum()),
        "questions",
        "Questions with parsed concise cue from analysis/guide.md",
    )
    for concept in CONCEPTS:
        add(
            "Concept map",
            f"questions_tagged_{CONCEPT_ID[concept]}",
            int((question_tags["concept"] == concept).sum()),
            "question_tag_rows",
            "Expanded question-concept rows (one row per tag)",
        )

    if not concept_mastery_overall.empty:
        for _, r in concept_mastery_overall.iterrows():
            add(
                "Concept mastery",
                f"overall_all_public_pass_rate_{CONCEPT_ID[r['concept']]}",
                round(float(r["all_public_pass_rate"]), 4),
                "pct",
                "Public-best GRM category == 2 across student-question rows tagged with concept",
            )

    add(
        "Prerequisites",
        "candidate_edges_count",
        int(len(prereq_edges)),
        "edges",
        "Empirical prerequisite candidates from delta thresholds + support",
    )
    add(
        "Prerequisites",
        "proxy_order_misaligned_candidate_edges_count",
        int(len(prereq_misalign)),
        "edges",
        "Candidates reverse to proxy concept teaching order (prompt-order proxy)",
    )

    if not repeat_pair_summary.empty:
        for _, r in repeat_pair_summary.iterrows():
            pair = str(r["term_pair"])
            add(
                "Repeat profiles",
                f"{pair}_repeat_students",
                int(r["repeat_students"]),
                "students",
                "Substantive repeat students (>=3 question rows per term by reconstruction)",
            )
            add(
                "Repeat profiles",
                f"{pair}_pct_any_newly_mastered_concept",
                round(float(r["pct_any_newly_mastered"]), 4),
                "pct",
                "Share of repeaters with >=1 newly mastered concept among concepts assessed in both terms",
            )
            add(
                "Repeat profiles",
                f"{pair}_pct_any_regressed_mastery",
                round(float(r["pct_any_regressed_mastery"]), 4),
                "pct",
                "Share of repeaters with >=1 regressed concept among concepts assessed in both terms",
            )

    for _, r in s2_alignment.iterrows():
        add("S2 decomposition", str(r["metric"]), r["value"], "value", str(r["note"]))

    if not s2_summary.empty:
        top_concepts = (
            s2_summary.groupby("concept", as_index=False)["concept_s2_rows"]
            .max()
            .sort_values("concept_s2_rows", ascending=False)
            .head(3)
        )
        for i, (_, r) in enumerate(top_concepts.iterrows(), start=1):
            add(
                "S2 decomposition",
                f"top_s2_concept_{i}",
                str(r["concept"]),
                "concept",
                f"Concept with {int(r['concept_s2_rows'])} final-S2 concept-tag rows",
            )

    return pd.DataFrame(rows)


def main() -> None:
    ensure_inputs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    question_map, question_tags = build_question_concept_map()

    grm = load_grm_rows()
    student_question_concepts = build_student_question_concept_rows(grm, question_tags)
    write_csv(student_question_concepts, OUT_DIR / "student_question_concept_rows.csv")

    concept_mastery_overall = summarize_concept_mastery_rows(student_question_concepts, [])
    concept_mastery_by_term = summarize_concept_mastery_rows(student_question_concepts, ["term"])
    concept_mastery_by_term_wave = summarize_concept_mastery_rows(student_question_concepts, ["term", "wave"])
    write_csv(concept_mastery_overall, OUT_DIR / "concept_mastery_overall.csv")
    write_csv(concept_mastery_by_term, OUT_DIR / "concept_mastery_by_term.csv")
    write_csv(concept_mastery_by_term_wave, OUT_DIR / "concept_mastery_by_term_wave.csv")

    # Simple unpaired wave deltas (population-level; not paired student comparison).
    wave_cmp = concept_mastery_by_term_wave[concept_mastery_by_term_wave["wave"].isin(["wave1", "wave2"])].copy()
    wave_pivot = wave_cmp.pivot_table(
        index=["term", "concept"],
        columns="wave",
        values=["all_public_pass_rate", "any_public_pass_rate", "mean_grm_category", "student_question_rows"],
    )
    wave_pivot.columns = [f"{a}_{b}" for a, b in wave_pivot.columns]
    wave_pivot = wave_pivot.reset_index()
    for metric in ["all_public_pass_rate", "any_public_pass_rate", "mean_grm_category"]:
        w1_col = f"{metric}_wave1"
        w2_col = f"{metric}_wave2"
        if w1_col in wave_pivot and w2_col in wave_pivot:
            wave_pivot[f"{metric}_delta_wave2_minus_wave1"] = wave_pivot[w2_col] - wave_pivot[w1_col]
    write_csv(wave_pivot, OUT_DIR / "concept_mastery_within_term_wave_unpaired_change.csv")

    student_concept_wave, student_concept_term = build_student_concept_summaries(student_question_concepts)
    write_csv(student_concept_wave, OUT_DIR / "student_concept_wave_summary.csv")
    write_csv(student_concept_term, OUT_DIR / "student_concept_term_summary.csv")

    student_concept_wave_agg = (
        student_concept_wave.groupby(["term", "wave", "concept"], as_index=False)
        .agg(
            student_concept_profiles=("student_id", "nunique"),
            mean_question_rows=("question_rows", "mean"),
            mean_mean_grm_category=("mean_grm_category", "mean"),
            pct_mastered_concept=("concept_mastered_flag", lambda s: float(s.mean()) * 100.0),
            pct_some_mastery=("concept_some_mastery_flag", lambda s: float(s.mean()) * 100.0),
        )
        .sort_values(["term", "wave", "concept"])
        .reset_index(drop=True)
    )
    student_concept_term_agg = (
        student_concept_term.groupby(["term", "concept"], as_index=False)
        .agg(
            student_concept_profiles=("student_id", "nunique"),
            mean_question_rows=("question_rows", "mean"),
            mean_mean_grm_category=("mean_grm_category", "mean"),
            pct_mastered_concept=("concept_mastered_flag", lambda s: float(s.mean()) * 100.0),
            pct_some_mastery=("concept_some_mastery_flag", lambda s: float(s.mean()) * 100.0),
        )
        .sort_values(["term", "concept"])
        .reset_index(drop=True)
    )
    write_csv(student_concept_wave_agg, OUT_DIR / "concept_mastery_student_profiles_by_term_wave.csv")
    write_csv(student_concept_term_agg, OUT_DIR / "concept_mastery_student_profiles_by_term.csv")

    within_term_pairs, within_term_pair_summary = build_within_term_concept_wave_changes(student_concept_wave)
    write_csv(within_term_pairs, OUT_DIR / "within_term_paired_student_concept_wave_changes.csv")
    write_csv(within_term_pair_summary, OUT_DIR / "within_term_paired_student_concept_wave_change_summary.csv")

    construct_flags, concept_attempt_rows, global_construct_summary = build_concept_construct_presence(grm, question_tags)
    write_csv(construct_flags, OUT_DIR / "attempt_construct_presence_flags.csv")
    write_csv(global_construct_summary, OUT_DIR / "construct_first_appearance_summary_global_step5_copy.csv")

    # Global construct focus rows (cross-cutting, not question-concept filtered).
    global_attempt_rows = grm[["namespace", "problem_id", "student_id", "term", "wave", "grm_category"]].copy()
    global_attempt_rows["all_public_pass"] = (global_attempt_rows["grm_category"] == 2).astype(int)
    global_attempt_rows["any_public_pass"] = (global_attempt_rows["grm_category"] >= 1).astype(int)
    global_attempt_rows = global_attempt_rows.merge(
        construct_flags, on=["namespace", "problem_id", "student_id"], how="left"
    ).fillna({f"ever_{c}": 0 for c in TRACKED_CONSTRUCTS})
    for c in [f"ever_{x}" for x in TRACKED_CONSTRUCTS]:
        if c not in global_attempt_rows.columns:
            global_attempt_rows[c] = 0
        global_attempt_rows[c] = global_attempt_rows[c].astype(int)

    global_focus_rows = summarize_focus_usage_mastery(
        global_attempt_rows,
        CONSTRUCT_FOCUS_ROWS,
    )
    write_csv(global_focus_rows, OUT_DIR / "construct_focus_usage_mastery.csv")

    # Concept-level proxy usage-vs-mastery (question rows filtered by concept).
    concept_proxy_rows: list[pd.DataFrame] = []
    for concept in CONCEPTS:
        spec = {
            "focus_label": concept,
            "focus_group": "question_concept_proxy",
            "constructs": CONCEPT_CONSTRUCT_PROXIES[concept]["constructs"],
            "proxy_quality": CONCEPT_CONSTRUCT_PROXIES[concept]["proxy_quality"],
            "note": CONCEPT_CONSTRUCT_PROXIES[concept]["proxy_note"],
        }
        sub = concept_attempt_rows[concept_attempt_rows["concept"] == concept].copy()
        one = summarize_focus_usage_mastery(sub, [spec])
        one["concept"] = concept
        concept_proxy_rows.append(one)
    concept_proxy_usage = pd.concat(concept_proxy_rows, ignore_index=True) if concept_proxy_rows else pd.DataFrame()
    if "focus_label" in concept_proxy_usage.columns:
        concept_proxy_usage = concept_proxy_usage.rename(columns={"focus_label": "concept_proxy_focus_label"})
    desired_cols = [
        "concept",
        "concept_proxy_focus_label",
        "focus_group",
        "relevant_constructs",
        "proxy_quality",
        "note",
        "attempt_rows",
        "users",
        "nonusers",
        "usage_rate_ever_used_in_attempt_pct",
        "all_public_pass_rate_among_users_pct",
        "all_public_pass_rate_among_nonusers_pct",
        "mean_grm_among_users",
        "mean_grm_among_nonusers",
        "gap_type",
    ]
    concept_proxy_usage = concept_proxy_usage[[c for c in desired_cols if c in concept_proxy_usage.columns]]
    write_csv(concept_proxy_usage, OUT_DIR / "concept_construct_proxy_usage_mastery.csv")

    # Also provide term breakdown for construct focus rows.
    focus_by_term = summarize_focus_usage_mastery(global_attempt_rows, CONSTRUCT_FOCUS_ROWS, group_context_cols=["term"])
    write_csv(focus_by_term, OUT_DIR / "construct_focus_usage_mastery_by_term.csv")

    prereq_matrix, prereq_edges, prereq_misalign = build_prerequisite_graph(student_concept_term)
    write_csv(prereq_matrix, OUT_DIR / "concept_prerequisite_pair_matrix.csv")
    write_csv(prereq_edges, OUT_DIR / "concept_prerequisite_edge_candidates.csv")
    write_csv(prereq_misalign, OUT_DIR / "concept_prerequisite_order_misalignment_proxy.csv")

    repeat_profiles, repeat_long_rows, repeat_retention_summary, repeat_pair_summary = build_repeat_student_concept_profiles(
        student_concept_term, grm
    )
    write_csv(repeat_profiles, OUT_DIR / "repeat_student_concept_profiles_paired.csv")
    write_csv(repeat_long_rows, OUT_DIR / "repeat_student_concept_profile_pair_rows.csv")
    write_csv(repeat_retention_summary, OUT_DIR / "repeat_student_concept_retention_acquisition_summary.csv")
    write_csv(repeat_pair_summary, OUT_DIR / "repeat_student_concept_profile_pair_summary.csv")

    (
        s2_detail,
        s2_summary,
        s2_alignment_summary,
        s2_aligned_summary,
        s2_aligned_rollup,
    ) = build_s2_concept_decomposition(question_tags)
    write_csv(s2_detail, OUT_DIR / "s2_final_attempt_concept_decomposition_rows.csv")
    write_csv(s2_summary, OUT_DIR / "s2_final_attempt_concept_decomposition_summary.csv")
    write_csv(s2_alignment_summary, OUT_DIR / "s2_final_attempt_snapshot_alignment_summary.csv")
    write_csv(s2_aligned_summary, OUT_DIR / "s2_final_attempt_concept_decomposition_summary_aligned_proxy.csv")

    # Concept-level decomposition rolled up to selection vs application (proxy only) for easier reporting.
    s2_proxy_rollup = (
        s2_summary[s2_summary["construct_proxy_quality"] != "none"]
        .pivot_table(
            index="concept",
            columns="s2_failure_decomposition_proxy",
            values="s2_rows",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    for col in [
        "Application gap proxy (relevant construct present)",
        "Selection gap proxy (relevant construct absent)",
    ]:
        if col not in s2_proxy_rollup.columns:
            s2_proxy_rollup[col] = 0
    s2_proxy_rollup["proxy_classified_rows"] = (
        s2_proxy_rollup["Application gap proxy (relevant construct present)"]
        + s2_proxy_rollup["Selection gap proxy (relevant construct absent)"]
    )
    s2_proxy_rollup["pct_application_gap_proxy"] = np.where(
        s2_proxy_rollup["proxy_classified_rows"] > 0,
        s2_proxy_rollup["Application gap proxy (relevant construct present)"]
        / s2_proxy_rollup["proxy_classified_rows"]
        * 100.0,
        np.nan,
    )
    s2_proxy_rollup["pct_selection_gap_proxy"] = np.where(
        s2_proxy_rollup["proxy_classified_rows"] > 0,
        s2_proxy_rollup["Selection gap proxy (relevant construct absent)"]
        / s2_proxy_rollup["proxy_classified_rows"]
        * 100.0,
        np.nan,
    )
    write_csv(s2_proxy_rollup, OUT_DIR / "s2_final_attempt_concept_decomposition_proxy_rollup.csv")
    write_csv(s2_aligned_rollup, OUT_DIR / "s2_final_attempt_concept_decomposition_proxy_rollup_aligned_proxy.csv")

    step9_key_metrics = build_step9_key_metrics(
        question_map=question_map,
        question_tags=question_tags,
        concept_mastery_overall=concept_mastery_overall,
        prereq_edges=prereq_edges,
        prereq_misalign=prereq_misalign,
        repeat_pair_summary=repeat_pair_summary,
        s2_alignment=s2_alignment_summary,
        s2_summary=s2_summary,
    )
    write_csv(step9_key_metrics, OUT_DIR / "step9_key_metrics.csv")

    write_manifest()
    print(f"Wrote Step 9 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
