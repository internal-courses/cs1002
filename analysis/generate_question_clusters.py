#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb>=1.4.0",
#   "pandas>=2.2.0",
# ]
# ///
"""Cluster semantically near-identical questions and build an error-analysis index.

Outputs:
- analysis/question_cluster_members.csv
- analysis/question_clusters.csv
- analysis/ERRORS.md  (index file linking to per-cluster analyses)

Heuristic clustering:
1) Exact fingerprint on normalized title + prompt text + Python template + testcase I/O.
2) For remaining same-title questions, near-duplicate grouping using high prompt/template similarity.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
PROBLEMS_DIR = ROOT / "problems"


TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def norm_ws(s: str | None) -> str:
    return WS_RE.sub(" ", (s or "").replace("\r", " ").replace("\n", " ")).strip()


def strip_html(s: str | None) -> str:
    text = html.unescape(s or "")
    text = TAG_RE.sub(" ", text)
    return norm_ws(text)


def normalize_code(s: str | None) -> str:
    if not s:
        return ""
    text = (s or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    # keep structure but normalize trailing whitespace and extra blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    out: list[str] = []
    blank_run = 0
    for ln in lines:
        if not ln.strip():
            blank_run += 1
            if blank_run <= 1:
                out.append("")
            continue
        blank_run = 0
        out.append(ln)
    return "\n".join(out)


def normalize_json_for_hash(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha1_text(*parts: str) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(p.encode("utf-8", errors="ignore"))
        h.update(b"\x1f")
    return h.hexdigest()


def slugify(s: str, max_len: int = 60) -> str:
    s2 = NON_ALNUM_RE.sub("-", (s or "").lower()).strip("-")
    if not s2:
        s2 = "untitled"
    return s2[:max_len].strip("-") or "untitled"


def seq_sim(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


@dataclass
class UF:
    parent: dict[int, int]

    def __init__(self, n: int) -> None:
        self.parent = {i: i for i in range(n)}

    def find(self, x: int) -> int:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            # deterministic root
            self.parent[max(ra, rb)] = min(ra, rb)


def load_question_rows() -> pd.DataFrame:
    qmeta = pd.read_csv(ANALYSIS_DIR / "question_metadata.csv")
    qmeta["problem_id"] = qmeta["problem_id"].astype(int)
    qmeta_map = {
        (str(r.namespace), int(r.problem_id)): r
        for r in qmeta.itertuples(index=False)
    }

    rows: list[dict[str, Any]] = []
    for ns_dir in sorted(PROBLEMS_DIR.glob("ns_*")):
        if not ns_dir.is_dir():
            continue
        for fp in sorted(ns_dir.glob("*.json"), key=lambda p: int(p.stem)):
            try:
                problem_id = int(fp.stem)
            except Exception:
                continue
            namespace = ns_dir.name
            try:
                obj = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                obj = {}

            key = (namespace, problem_id)
            qmeta_row = qmeta_map.get(key)
            title = None
            question_text = None
            if qmeta_row is not None:
                title = None if pd.isna(qmeta_row.question_title) else str(qmeta_row.question_title)
                question_text = None if pd.isna(qmeta_row.question_text) else str(qmeta_row.question_text)
            if not title:
                title = str(obj.get("short_description") or "")
            if not question_text:
                question_text = str(obj.get("question") or "")

            allowed = obj.get("allowed_languages") or []
            py_lang_obj = None
            for lang in allowed:
                if isinstance(lang, dict) and str(lang.get("language") or "").startswith("py"):
                    py_lang_obj = lang
                    break
            if py_lang_obj is None and allowed and isinstance(allowed[0], dict):
                py_lang_obj = allowed[0]

            py_template = normalize_code(str((py_lang_obj or {}).get("code_template") or ""))
            py_prefix = normalize_code(str((py_lang_obj or {}).get("prefixed_code") or ""))
            py_suffix = normalize_code(str((py_lang_obj or {}).get("suffixed_invisible_code") or ""))

            public_tests = obj.get("public_testcase") or []
            private_tests = obj.get("private_testcase") or []
            tests_norm = {
                "public": [
                    {
                        "input": norm_ws(str(tc.get("input") or "")),
                        "output": norm_ws(str(tc.get("output") or "")),
                        "weight": tc.get("weight"),
                    }
                    for tc in public_tests
                    if isinstance(tc, dict)
                ],
                "private": [
                    {
                        "input": norm_ws(str(tc.get("input") or "")),
                        "output": norm_ws(str(tc.get("output") or "")),
                        "weight": tc.get("weight"),
                    }
                    for tc in private_tests
                    if isinstance(tc, dict)
                ],
            }

            question_text_plain = strip_html(question_text)
            # Remove platform/debug boilerplate links to focus on semantics.
            question_text_core = question_text_plain
            for marker in [
                "NOTE: You can use the below tools for working out and debugging.",
                "PythonTutor | Starboard Notebook | Pyodide Terminal",
                "Template Code(Click to Expand)",
            ]:
                question_text_core = question_text_core.replace(marker, "")
            question_text_core = norm_ws(question_text_core)

            title_norm = norm_ws(title).lower()
            template_norm_collapse = norm_ws(py_template).lower()

            full_json_hash = sha1_text(normalize_json_for_hash(obj))
            exact_fingerprint = sha1_text(
                title_norm,
                question_text_core.lower(),
                template_norm_collapse,
                normalize_json_for_hash(tests_norm),
            )
            prompt_hash = sha1_text(title_norm, question_text_core.lower())
            template_hash = sha1_text(template_norm_collapse)
            tests_hash = sha1_text(normalize_json_for_hash(tests_norm))
            function_name = ""
            m = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", py_template)
            if m:
                function_name = m.group(1)

            rows.append(
                {
                    "namespace": namespace,
                    "problem_id": problem_id,
                    "question_title": title,
                    "title_norm": title_norm,
                    "short_description": str(obj.get("short_description") or ""),
                    "question_text_plain": question_text_plain,
                    "question_text_core": question_text_core,
                    "question_text_core_len": len(question_text_core),
                    "python_template_norm": py_template,
                    "python_template_norm_compact": template_norm_collapse,
                    "python_prefix_norm": py_prefix,
                    "python_suffix_norm": py_suffix,
                    "function_name": function_name,
                    "num_public_tests": len(public_tests) if isinstance(public_tests, list) else 0,
                    "num_private_tests": len(private_tests) if isinstance(private_tests, list) else 0,
                    "exact_fingerprint": exact_fingerprint,
                    "prompt_hash": prompt_hash,
                    "template_hash": template_hash,
                    "tests_hash": tests_hash,
                    "full_problem_json_hash": full_json_hash,
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("No questions found under problems/")
    return df


def load_submission_counts() -> pd.DataFrame:
    conn = duckdb.connect()
    sql = """
    WITH latest_sub AS (
      SELECT * EXCLUDE (rn)
      FROM (
        SELECT
          namespace,
          CAST(problem_id AS INTEGER) AS problem_id,
          student_id,
          score,
          ROW_NUMBER() OVER (
            PARTITION BY namespace, CAST(problem_id AS INTEGER), student_id
            ORDER BY timestamp_utc DESC, COALESCE(code_sha256, '') DESC
          ) AS rn
        FROM read_parquet('analysis/submission_timeline.parquet')
        WHERE event_type = 'submission' AND evaluation_type = 'private'
      ) x
      WHERE rn = 1
    )
    SELECT
      namespace,
      problem_id,
      COUNT(*) AS final_submitters,
      SUM(CASE WHEN score < 100 THEN 1 ELSE 0 END) AS non_full_final_submissions
    FROM latest_sub
    GROUP BY 1,2
    """
    out = conn.execute(sql).df()
    if not out.empty:
        out["problem_id"] = out["problem_id"].astype(int)
    return out


def cluster_questions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    n = len(df)
    uf = UF(n)

    # Phase 1: exact fingerprint duplicates.
    for _, idxs in df.groupby("exact_fingerprint").groups.items():
        idxs = list(idxs)
        for i in range(1, len(idxs)):
            uf.union(idxs[0], idxs[i])

    # Phase 2: near-duplicate clustering among same-title groups only.
    # Tight thresholds to avoid false merges.
    for title, idxs in df.groupby("title_norm").groups.items():
        idxs = list(idxs)
        if len(idxs) < 2 or not title:
            continue
        for a_pos in range(len(idxs)):
            for b_pos in range(a_pos + 1, len(idxs)):
                ia = idxs[a_pos]
                ib = idxs[b_pos]
                ra = df.loc[ia]
                rb = df.loc[ib]
                # Skip pairs already exact-clustered.
                if uf.find(ia) == uf.find(ib):
                    continue

                prompt_sim = seq_sim(str(ra.question_text_core).lower(), str(rb.question_text_core).lower())
                tmpl_sim = seq_sim(str(ra.python_template_norm_compact), str(rb.python_template_norm_compact))
                tests_sim = 1.0 if ra.tests_hash == rb.tests_hash else 0.0
                counts_same = (
                    int(ra.num_public_tests) == int(rb.num_public_tests)
                    and int(ra.num_private_tests) == int(rb.num_private_tests)
                )

                should_merge = False
                if prompt_sim >= 0.985 and tmpl_sim >= 0.97:
                    should_merge = True
                elif prompt_sim >= 0.975 and tmpl_sim >= 0.94 and counts_same and tests_sim == 1.0:
                    should_merge = True
                elif prompt_sim >= 0.995 and tmpl_sim >= 0.85 and counts_same:
                    should_merge = True

                if should_merge:
                    uf.union(ia, ib)

    roots = [uf.find(i) for i in range(n)]
    df["cluster_root"] = roots
    return df


def build_cluster_tables(df: pd.DataFrame, counts: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.merge(counts, on=["namespace", "problem_id"], how="left")
    df["final_submitters"] = df["final_submitters"].fillna(0).astype(int)
    df["non_full_final_submissions"] = df["non_full_final_submissions"].fillna(0).astype(int)

    cluster_rows: list[dict[str, Any]] = []
    member_rows: list[dict[str, Any]] = []

    groups = []
    for root, g in df.groupby("cluster_root", sort=False):
        g = g.copy()
        # canonical = max final submitters, then non-full, then lexicographic key
        g["sort_key"] = list(
            zip(
                -g["final_submitters"],
                -g["non_full_final_submissions"],
                g["question_title"].fillna(""),
                g["namespace"],
                g["problem_id"],
            )
        )
        g = g.sort_values(["final_submitters", "non_full_final_submissions", "question_title", "namespace", "problem_id"], ascending=[False, False, True, True, True])
        canonical = g.iloc[0]

        cluster_title = str(canonical["question_title"] or canonical["short_description"] or "Untitled").strip() or "Untitled"
        groups.append(
            {
                "root": int(root),
                "cluster_title": cluster_title,
                "member_count": int(len(g)),
                "total_final_submitters": int(g["final_submitters"].sum()),
                "total_non_full_final_submissions": int(g["non_full_final_submissions"].sum()),
                "canonical_namespace": str(canonical["namespace"]),
                "canonical_problem_id": int(canonical["problem_id"]),
                "canonical_full_problem_json_hash": str(canonical["full_problem_json_hash"]),
                "members_df": g,
            }
        )

    groups.sort(
        key=lambda x: (
            -x["member_count"],
            -x["total_final_submitters"],
            x["cluster_title"].lower(),
            x["canonical_namespace"],
            x["canonical_problem_id"],
        )
    )

    root_to_cluster_id: dict[int, str] = {}
    for i, grp in enumerate(groups, start=1):
        cid = f"C{i:03d}"
        root_to_cluster_id[grp["root"]] = cid

    for grp in groups:
        cid = root_to_cluster_id[grp["root"]]
        g = grp["members_df"].copy()
        cluster_title = grp["cluster_title"]
        slug = slugify(cluster_title)
        cluster_hash = sha1_text(
            cluster_title.lower(),
            "|".join(sorted(f"{r.namespace}:{int(r.problem_id)}" for r in g.itertuples(index=False))),
        )[:8]
        cluster_file = f"analysis/ERRORS-cluster-{cid.lower()}-{slug}-{cluster_hash}.md"

        # Member-level diff note vs canonical.
        canon = g.iloc[0]
        for _, r in g.sort_values(["namespace", "problem_id"]).iterrows():
            diff_bits: list[str] = []
            if str(r["full_problem_json_hash"]) == str(canon["full_problem_json_hash"]):
                diff_note = "Exact duplicate problem JSON"
            else:
                if str(r["question_text_core"]) != str(canon["question_text_core"]):
                    diff_bits.append("prompt text differs")
                if str(r["python_template_norm_compact"]) != str(canon["python_template_norm_compact"]):
                    diff_bits.append("template differs")
                if str(r["tests_hash"]) != str(canon["tests_hash"]):
                    diff_bits.append("tests differ")
                if not diff_bits:
                    diff_bits.append("minor metadata differences")
                diff_note = "; ".join(diff_bits)

            member_rows.append(
                {
                    "cluster_id": cid,
                    "cluster_title": cluster_title,
                    "cluster_file": cluster_file,
                    "cluster_member_count": int(len(g)),
                    "cluster_total_final_submitters": int(g["final_submitters"].sum()),
                    "cluster_total_non_full_final_submissions": int(g["non_full_final_submissions"].sum()),
                    "is_canonical": bool(
                        str(r["namespace"]) == str(canon["namespace"]) and int(r["problem_id"]) == int(canon["problem_id"])
                    ),
                    "namespace": str(r["namespace"]),
                    "problem_id": int(r["problem_id"]),
                    "question_title": str(r["question_title"]),
                    "final_submitters": int(r["final_submitters"]),
                    "non_full_final_submissions": int(r["non_full_final_submissions"]),
                    "function_name": str(r["function_name"] or ""),
                    "num_public_tests": int(r["num_public_tests"]),
                    "num_private_tests": int(r["num_private_tests"]),
                    "exact_fingerprint": str(r["exact_fingerprint"]),
                    "full_problem_json_hash": str(r["full_problem_json_hash"]),
                    "variant_diff_note_vs_canonical": diff_note,
                }
            )

        all_exact_json = g["full_problem_json_hash"].nunique(dropna=False) == 1
        all_exact_fingerprint = g["exact_fingerprint"].nunique(dropna=False) == 1
        cluster_rows.append(
            {
                "cluster_id": cid,
                "cluster_title": cluster_title,
                "cluster_slug": slug,
                "cluster_hash": cluster_hash,
                "cluster_file": cluster_file,
                "member_count": int(len(g)),
                "total_final_submitters": int(g["final_submitters"].sum()),
                "total_non_full_final_submissions": int(g["non_full_final_submissions"].sum()),
                "canonical_namespace": str(canon["namespace"]),
                "canonical_problem_id": int(canon["problem_id"]),
                "canonical_question_title": str(canon["question_title"]),
                "all_members_exact_problem_json": bool(all_exact_json),
                "all_members_exact_fingerprint": bool(all_exact_fingerprint),
                "distinct_titles": int(g["question_title"].nunique(dropna=False)),
            }
        )

    clusters_df = pd.DataFrame(cluster_rows).sort_values("cluster_id")
    members_df = pd.DataFrame(member_rows).sort_values(["cluster_id", "namespace", "problem_id"])
    return clusters_df, members_df


def write_index_md(clusters_df: pd.DataFrame, members_df: pd.DataFrame) -> None:
    num_questions = int(len(members_df))
    num_clusters = int(len(clusters_df))
    multi_clusters = int((clusters_df["member_count"] > 1).sum())

    lines: list[str] = []
    lines.append("# Error Analysis Index (Question Clusters)")
    lines.append("")
    lines.append("This file indexes question clusters for targeted error-analysis writeups.")
    lines.append("")
    lines.append("Definitions used here:")
    lines.append("")
    lines.append("- `final_submitters`: unique student-question rows with a final evaluated private submission (latest `submission` event)")
    lines.append("- `non_full`: final submitters whose latest private submission score is `< 100`")
    lines.append("- Clusters are built by normalized prompt/template/test fingerprints, plus a strict near-duplicate fallback within same-title questions.")
    lines.append("")
    lines.append(f"- Questions indexed: `{num_questions}`")
    lines.append(f"- Question clusters: `{num_clusters}`")
    lines.append(f"- Multi-variant clusters (`>1` question): `{multi_clusters}`")
    lines.append("")
    lines.append("## Cluster List")
    lines.append("")

    # Sort clusters by priority for future work: multi-variant first, then total volume.
    cluster_sort = clusters_df.sort_values(
        ["member_count", "total_final_submitters", "cluster_title", "cluster_id"],
        ascending=[False, False, True, True],
    )

    for c in cluster_sort.itertuples(index=False):
        lines.append(
            f"### {c.cluster_id} - {c.cluster_title}"
        )
        lines.append("")
        lines.append(f"- Analysis file: [`{c.cluster_file}`]({c.cluster_file.replace('analysis/','')})")
        lines.append(f"- Variants in cluster: `{int(c.member_count)}`")
        lines.append(f"- Total final submitters across variants: `{int(c.total_final_submitters)}`")
        lines.append(f"- Total non-full finals across variants: `{int(c.total_non_full_final_submissions)}`")
        lines.append(f"- Canonical variant: `{c.canonical_namespace}/{int(c.canonical_problem_id)}`")
        if bool(c.all_members_exact_problem_json):
            lines.append("- Variant relationship: all variants are exact duplicate problem JSONs")
        elif bool(c.all_members_exact_fingerprint):
            lines.append("- Variant relationship: exact semantic fingerprint match with minor metadata differences")
        else:
            lines.append("- Variant relationship: near-duplicate semantic cluster (review variant diffs in member list)")
        lines.append("")
        lines.append("| Variant | final_submitters | non_full | Tests (pub/priv) | Difference vs canonical |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        mg_all = members_df[members_df["cluster_id"] == c.cluster_id].sort_values(["namespace", "problem_id"])
        mg = mg_all[mg_all["final_submitters"] > 0].copy()
        for m in mg.itertuples(index=False):
            variant = f"`{m.namespace}/{int(m.problem_id)}`"
            if bool(m.is_canonical):
                variant += " (canonical)"
            lines.append(
                f"| {variant} | {int(m.final_submitters)} | {int(m.non_full_final_submissions)} | "
                f"`{int(m.num_public_tests)}/{int(m.num_private_tests)}` | {m.variant_diff_note_vs_canonical} |"
            )
        lines.append("")

    (ANALYSIS_DIR / "ERRORS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    qdf = load_question_rows()
    counts = load_submission_counts()
    clustered = cluster_questions(qdf)
    clusters_df, members_df = build_cluster_tables(clustered, counts)

    clusters_df.to_csv(ANALYSIS_DIR / "question_clusters.csv", index=False)
    members_df.to_csv(ANALYSIS_DIR / "question_cluster_members.csv", index=False)
    write_index_md(clusters_df, members_df)

    print(f"Wrote {ANALYSIS_DIR / 'question_clusters.csv'}")
    print(f"Wrote {ANALYSIS_DIR / 'question_cluster_members.csv'}")
    print(f"Wrote {ANALYSIS_DIR / 'ERRORS.md'}")
    print(f"Clusters: {len(clusters_df)} (multi-variant: {(clusters_df['member_count']>1).sum()})")


if __name__ == "__main__":
    main()
