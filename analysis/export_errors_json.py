#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Export analyzed error-cluster markdown reports to structured JSON.

Parses `analysis/ERRORS-cluster-*.md` files and writes `analysis/errors.json`.

The output intentionally includes:
- A hierarchical representation (cluster -> patterns -> examples)
- Flat row-style indexes for querying/visualization without reparsing nested data
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parent
CLUSTER_GLOB = "ERRORS-cluster-*.md"
OUTPUT_PATH = ROOT / "errors.json"


TITLE_RE = re.compile(r"^# Error Patterns: Cluster (?P<cluster_id>C\d+) \(`(?P<title>.+)`\)$")
INTICK_RE = re.compile(r"`([^`]*)`")
COUNT_TOTAL_PCT_RE = re.compile(r"`(?P<count>\d+)\/(?P<total>\d+)`\s+\(`(?P<pct>[\d.]+)%`\)")
RESIDUAL_RE = re.compile(
    r"^Residual `Other` after second-pass re-clustering: "
    r"`(?P<count>\d+)\/(?P<total>\d+)` \(`(?P<pct>[\d.]+)%`\)$"
)
VARIANT_FREQ_RE = re.compile(
    r"^\s{2}- `(?P<variant>[^`]+)`: `(?P<count>\d+)\/(?P<total>\d+)` \(`(?P<pct>[\d.]+)%`\)$"
)
EXAMPLE_META_RE = re.compile(
    r"^\s{2}- Variant `(?P<variant>[^`]+)`, Student ID `(?P<student_id>[^`]+)`, "
    r"summary `(?P<summary>[^`]+)`, score `(?P<score>[^`]+)`, vector `(?P<vector>[^`]+)`$"
)
TABLE_ROW_RE = re.compile(r"^\|.*\|$")


def strip_ticks(text: str) -> str:
    if text.startswith("`") and text.endswith("`") and text.count("`") == 2:
        return text[1:-1]
    return text


def parse_int(text: str) -> int | None:
    cleaned = strip_ticks(text.strip()).replace(",", "")
    return int(cleaned) if re.fullmatch(r"-?\d+", cleaned) else None


def parse_float(text: str) -> float | None:
    cleaned = strip_ticks(text.strip()).replace("%", "")
    return float(cleaned) if re.fullmatch(r"-?\d+(?:\.\d+)?", cleaned) else None


def normalize_md_text(text: str) -> str:
    return INTICK_RE.sub(lambda m: m.group(1), text).strip()


def split_markdown_row(line: str) -> list[str]:
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        raise ValueError(f"Not a markdown table row: {line}")
    cells: list[str] = []
    current: list[str] = []
    in_backticks = False
    escaped = False
    for ch in line[1:-1]:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\":
            current.append(ch)
            escaped = True
            continue
        if ch == "`":
            in_backticks = not in_backticks
            current.append(ch)
            continue
        if ch == "|" and not in_backticks:
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    cells.append("".join(current).strip())
    return cells


def parse_markdown_table(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    if start + 1 >= len(lines):
        raise ValueError("Incomplete markdown table")
    headers = split_markdown_row(lines[start])
    _sep = split_markdown_row(lines[start + 1])
    rows: list[dict[str, str]] = []
    i = start + 2
    while i < len(lines) and TABLE_ROW_RE.match(lines[i].strip()):
        cells = split_markdown_row(lines[i])
        if len(cells) != len(headers):
            raise ValueError(f"Table row has {len(cells)} cells but expected {len(headers)}: {lines[i]}")
        rows.append(dict(zip(headers, cells, strict=True)))
        i += 1
    return {"headers": headers, "rows": rows}, i


def find_top_level_sections(lines: list[str]) -> dict[str, tuple[int, int]]:
    headings: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if line.startswith("## "):
            headings.append((i, line[3:].strip()))
    sections: dict[str, tuple[int, int]] = {}
    for idx, (start, name) in enumerate(headings):
        end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        sections[name] = (start + 1, end)
    return sections


def parse_backticked_value(text: str) -> str | None:
    m = re.search(r"`([^`]*)`", text)
    return m.group(1) if m else None


def parse_distribution(text: str) -> list[dict[str, Any]]:
    # e.g. `000` x136, `001` x59
    parts = [p.strip() for p in text.split(",") if p.strip()]
    result: list[dict[str, Any]] = []
    for part in parts:
        m = re.match(r"`([^`]*)`\s+x(\d+)$", part)
        if not m:
            result.append({"label": normalize_md_text(part), "count": None})
            continue
        result.append({"label": m.group(1), "count": int(m.group(2))})
    return result


def parse_score_distribution(text: str) -> list[dict[str, Any]]:
    items = parse_distribution(text)
    out: list[dict[str, Any]] = []
    for item in items:
        label = item["label"]
        score = parse_float(str(label))
        out.append({"score": score, "score_label": str(label), "count": item["count"]})
    return out


def parse_count_total_pct(text: str) -> dict[str, Any] | None:
    m = COUNT_TOTAL_PCT_RE.search(text)
    if not m:
        return None
    return {
        "count": int(m.group("count")),
        "total": int(m.group("total")),
        "pct": float(m.group("pct")),
    }


def parse_variant_cell(cell: str) -> dict[str, Any]:
    variant = parse_backticked_value(cell) or normalize_md_text(cell)
    return {
        "variant": variant,
        "canonical": "(canonical)" in cell,
        "raw": cell.strip(),
    }


def parse_cluster_summary(section_lines: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    membership_table: dict[str, Any] | None = None
    i = 0
    while i < len(section_lines):
        line = section_lines[i].rstrip()
        if line.startswith("- Cluster ID:"):
            summary["cluster_id"] = parse_backticked_value(line)
        elif line.startswith("- Cluster title:"):
            summary["cluster_title"] = parse_backticked_value(line)
        elif line.startswith("- Cluster file (this file):"):
            summary["cluster_file"] = parse_backticked_value(line)
        elif line.startswith("- Variants in cluster:"):
            summary["variants_in_cluster"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Total final submitters across variants:"):
            summary["total_final_submitters"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Total non-full final submissions across variants:"):
            summary["total_non_full_final_submissions"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Canonical variant (by submissions):"):
            summary["canonical_variant_by_submissions"] = parse_backticked_value(line)
        elif line.startswith("Cluster membership"):
            summary["cluster_membership_note"] = line.strip()
            # next non-empty line should be table header
            j = i + 1
            while j < len(section_lines) and not section_lines[j].strip():
                j += 1
            if j < len(section_lines) and TABLE_ROW_RE.match(section_lines[j].strip()):
                membership_table, next_i = parse_markdown_table(section_lines, j)
                i = next_i - 1
        i += 1

    members: list[dict[str, Any]] = []
    if membership_table:
        for row in membership_table["rows"]:
            variant_info = parse_variant_cell(row.get("Variant", ""))
            members.append(
                {
                    **variant_info,
                    "final_submitters": parse_int(row.get("final_submitters", "")),
                    "non_full": parse_int(row.get("non_full", "")),
                    "relationship": normalize_md_text(row.get("Relationship", "")),
                }
            )
    return {"summary": summary, "membership_table": membership_table, "members": members}


def parse_canonical_spec(section_lines: list[str]) -> dict[str, Any]:
    canonical_json: str | None = None
    other_variant_jsons: list[str] = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i].rstrip()
        if line.startswith("- Canonical full question JSON:"):
            canonical_json = parse_backticked_value(line)
        elif line.startswith("- Other variants in cluster:"):
            i += 1
            while i < len(section_lines):
                sub = section_lines[i]
                if sub.startswith("  - "):
                    path = parse_backticked_value(sub) or normalize_md_text(sub[4:])
                    other_variant_jsons.append(path)
                    i += 1
                    continue
                if not sub.strip():
                    i += 1
                    continue
                i -= 1
                break
        i += 1
    return {"canonical_full_question_json": canonical_json, "other_variant_jsons": other_variant_jsons}


def parse_outcomes(section_lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    variant_table: dict[str, Any] | None = None
    i = 0
    while i < len(section_lines):
        line = section_lines[i].rstrip()
        if line.startswith("- Final submitters:"):
            out["final_submitters"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Full pass:"):
            out["full_pass"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Non-full final submissions:"):
            out["non_full_final_submissions"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Parseable non-full (logic/runtime focus):"):
            out["parseable_non_full"] = parse_int(line.split(":", 1)[1] or "")
        elif line.startswith("- Non-parseable non-full:"):
            out["non_parseable_non_full"] = parse_int(line.split(":", 1)[1] or "")
        elif line.strip() == "Variant-level comparison:":
            j = i + 1
            while j < len(section_lines) and not section_lines[j].strip():
                j += 1
            if j < len(section_lines) and TABLE_ROW_RE.match(section_lines[j].strip()):
                variant_table, next_i = parse_markdown_table(section_lines, j)
                i = next_i - 1
        i += 1

    variant_outcomes: list[dict[str, Any]] = []
    if variant_table:
        for row in variant_table["rows"]:
            variant_info = parse_variant_cell(row.get("Variant", ""))
            variant_outcomes.append(
                {
                    **variant_info,
                    "final_submitters": parse_int(row.get("Final submitters", "")),
                    "full_pass": parse_int(row.get("Full pass", "")),
                    "non_full": parse_int(row.get("Non-full", "")),
                    "parseable_non_full": parse_int(row.get("Parseable non-full", "")),
                    "non_parseable_non_full": parse_int(row.get("Non-parseable non-full", "")),
                }
            )
    out["variant_level_comparison"] = variant_outcomes
    return out


def parse_private_case_structure(section_lines: list[str]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    vector_semantics: str | None = None
    for raw in section_lines:
        line = raw.rstrip()
        if line.startswith("- Private case "):
            m = re.match(r"^- Private case (\d+):\s*(.*)$", line)
            if m:
                cases.append({"index": int(m.group(1)), "description": normalize_md_text(m.group(2))})
        elif line.startswith("Private-case vectors in this report are"):
            vector_semantics = normalize_md_text(line)
    return {"cases": cases, "vector_semantics": vector_semantics}


def parse_inventory(section_lines: list[str]) -> dict[str, Any]:
    table_start = None
    for i, line in enumerate(section_lines):
        if TABLE_ROW_RE.match(line.strip()):
            table_start = i
            break
    if table_start is None:
        return {"columns": [], "variant_columns": [], "rows": []}

    table, _ = parse_markdown_table(section_lines, table_start)
    headers = table["headers"]
    rows_out: list[dict[str, Any]] = []
    variant_columns = [h for h in headers if h not in {"Pattern", "Cluster count", "% of cluster non-full"}]
    for order, row in enumerate(table["rows"], start=1):
        variant_counts = {
            normalize_md_text(col): (parse_int(row.get(col, "")) or 0)
            for col in variant_columns
        }
        rows_out.append(
            {
                "order": order,
                "pattern": normalize_md_text(row.get("Pattern", "")),
                "cluster_count": parse_int(row.get("Cluster count", "")),
                "cluster_non_full_pct": parse_float(row.get("% of cluster non-full", "")),
                "variant_counts": variant_counts,
            }
        )
    return {
        "columns": [normalize_md_text(h) for h in headers],
        "variant_columns": [normalize_md_text(h) for h in variant_columns],
        "rows": rows_out,
    }


@dataclass
class ParsedPatternSection:
    pattern: dict[str, Any]
    next_index: int


def parse_pattern_section(
    lines: list[str],
    start_idx: int,
    cluster_non_full_total: int | None,
    inventory_by_name: dict[str, dict[str, Any]],
    section_line_offset: int = 0,
) -> ParsedPatternSection:
    heading_line = lines[start_idx]
    name = heading_line[4:].strip()
    i = start_idx + 1
    pattern: dict[str, Any] = {
        "name": name,
        "order": None,
        "cluster_frequency": None,
        "variant_frequencies": [],
        "dominant_private_case_vectors": [],
        "score_distribution_top": [],
        "interpretation": None,
        "representative_examples": [],
        "details": {},
        "source_line": section_line_offset + start_idx + 1,
    }

    inventory_row = inventory_by_name.get(name)
    if inventory_row:
        pattern["order"] = inventory_row["order"]
        pattern["inventory_cluster_count"] = inventory_row["cluster_count"]
        pattern["inventory_cluster_non_full_pct"] = inventory_row["cluster_non_full_pct"]
        pattern["inventory_variant_counts"] = inventory_row["variant_counts"]

    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            break

        if not line.strip():
            i += 1
            continue

        if line.startswith("- Cluster frequency:"):
            freq = parse_count_total_pct(line)
            if freq:
                pattern["cluster_frequency"] = freq
            else:
                pattern["details"]["Cluster frequency"] = normalize_md_text(line.split(":", 1)[1])
            i += 1
            continue

        if line.startswith("- Variant frequencies:"):
            i += 1
            vfreqs: list[dict[str, Any]] = []
            while i < len(lines):
                sub = lines[i]
                if not sub.strip():
                    i += 1
                    continue
                if sub.startswith("  - "):
                    m = VARIANT_FREQ_RE.match(sub)
                    if m:
                        vfreqs.append(
                            {
                                "variant": m.group("variant"),
                                "count": int(m.group("count")),
                                "total": int(m.group("total")),
                                "pct": float(m.group("pct")),
                            }
                        )
                    else:
                        vfreqs.append({"raw": normalize_md_text(sub[4:])})
                    i += 1
                    continue
                break
            pattern["variant_frequencies"] = vfreqs
            continue

        if line.startswith("- Dominant private-case vectors:"):
            text = line.split(":", 1)[1].strip()
            vectors = parse_distribution(text)
            pattern["dominant_private_case_vectors"] = [
                {"vector": str(v["label"]), "count": v["count"]} for v in vectors
            ]
            i += 1
            continue

        if line.startswith("- Score distribution (top):"):
            text = line.split(":", 1)[1].strip()
            pattern["score_distribution_top"] = parse_score_distribution(text)
            i += 1
            continue

        if line.startswith("- Interpretation:"):
            interpretation = normalize_md_text(line.split(":", 1)[1])
            pattern["interpretation"] = interpretation
            pattern["details"]["Interpretation"] = interpretation
            i += 1
            continue

        if line.startswith("- Representative examples (actual student submissions):"):
            i += 1
            examples: list[dict[str, Any]] = []
            while i < len(lines):
                if i < len(lines) and lines[i].startswith("### "):
                    break
                if i < len(lines) and lines[i].startswith("- "):
                    break
                if not lines[i].strip():
                    i += 1
                    continue
                if lines[i].startswith("  - Variant "):
                    m = EXAMPLE_META_RE.match(lines[i])
                    example: dict[str, Any] = {"source_line": section_line_offset + i + 1}
                    if m:
                        score_raw = m.group("score")
                        score_num = parse_float(score_raw)
                        example.update(
                            {
                                "variant": m.group("variant"),
                                "student_id": m.group("student_id"),
                                "summary": m.group("summary"),
                                "score": score_num if score_num is not None else score_raw,
                                "score_label": score_raw,
                                "vector": m.group("vector"),
                            }
                        )
                    else:
                        example["raw_meta"] = normalize_md_text(lines[i][4:])
                    i += 1
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    if i < len(lines) and lines[i].startswith("```"):
                        code_lang = lines[i].strip()[3:].strip() or None
                        i += 1
                        code_lines: list[str] = []
                        while i < len(lines) and not lines[i].startswith("```"):
                            code_lines.append(lines[i])
                            i += 1
                        example["code_lang"] = code_lang
                        example["code"] = "\n".join(code_lines)
                        if i < len(lines) and lines[i].startswith("```"):
                            i += 1
                    examples.append(example)
                    continue
                # Stray text inside examples block; preserve and continue.
                examples.append({"raw_line": lines[i], "source_line": section_line_offset + i + 1})
                i += 1
            pattern["representative_examples"] = examples
            continue

        if line.startswith("- "):
            key, _, value = line[2:].partition(":")
            key = key.strip()
            value = value.strip()
            pattern["details"][key] = normalize_md_text(value)
            i += 1
            continue

        # Preserve unexpected text in an ordered bucket for lossless-ish parsing.
        pattern.setdefault("unparsed_lines", []).append({"line": line, "source_line": section_line_offset + i + 1})
        i += 1

    # Fill missing cluster total for convenience if available.
    if pattern["cluster_frequency"] and cluster_non_full_total is not None:
        pattern["cluster_frequency"]["cluster_non_full_total"] = cluster_non_full_total

    return ParsedPatternSection(pattern=pattern, next_index=i)


def parse_reclustered_details(
    section_lines: list[str],
    outcomes: dict[str, Any],
    inventory: dict[str, Any],
    section_line_offset: int = 0,
) -> dict[str, Any]:
    residual: dict[str, Any] | None = None
    patterns: list[dict[str, Any]] = []
    inventory_by_name = {row["pattern"]: row for row in inventory.get("rows", [])}
    cluster_non_full_total = outcomes.get("non_full_final_submissions")

    i = 0
    while i < len(section_lines):
        line = section_lines[i].rstrip()
        if not line:
            i += 1
            continue
        residual_match = RESIDUAL_RE.match(line)
        if residual_match:
            residual = {
                "count": int(residual_match.group("count")),
                "total": int(residual_match.group("total")),
                "pct": float(residual_match.group("pct")),
                "source_line": section_line_offset + i + 1,
            }
            i += 1
            continue
        if line.startswith("### "):
            parsed = parse_pattern_section(
                section_lines,
                i,
                cluster_non_full_total,
                inventory_by_name,
                section_line_offset=section_line_offset,
            )
            patterns.append(parsed.pattern)
            i = parsed.next_index
            continue
        i += 1

    # Stable order: prefer parsed order from inventory, fallback source order.
    patterns.sort(key=lambda p: (p["order"] is None, p["order"] or 10**9, p["source_line"]))
    for idx, pat in enumerate(patterns, start=1):
        pat["pattern_index"] = idx
        if pat.get("order") is None:
            pat["order"] = idx

    return {"residual_other": residual, "patterns": patterns}


def parse_cluster_report(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"Empty file: {path}")
    title_match = TITLE_RE.match(lines[0].rstrip())
    if not title_match:
        raise ValueError(f"Unexpected title line in {path}: {lines[0]}")

    top_sections = find_top_level_sections(lines)
    required_sections = [
        "Cluster Summary",
        "Canonical Question Spec (Full Source Artifact)",
        "Cluster-Level Outcome Summary",
        "Private Case Structure",
        "Exhaustive Pattern Inventory (Cluster-Level)",
        "Re-clustered Pattern Details",
    ]
    missing = [s for s in required_sections if s not in top_sections]
    if missing:
        raise ValueError(f"Missing sections in {path}: {missing}")

    cluster_summary = parse_cluster_summary(lines[top_sections["Cluster Summary"][0] : top_sections["Cluster Summary"][1]])
    canonical_spec = parse_canonical_spec(
        lines[top_sections["Canonical Question Spec (Full Source Artifact)"][0] : top_sections["Canonical Question Spec (Full Source Artifact)"][1]]
    )
    outcomes = parse_outcomes(
        lines[top_sections["Cluster-Level Outcome Summary"][0] : top_sections["Cluster-Level Outcome Summary"][1]]
    )
    private_case_structure = parse_private_case_structure(
        lines[top_sections["Private Case Structure"][0] : top_sections["Private Case Structure"][1]]
    )
    inventory = parse_inventory(
        lines[top_sections["Exhaustive Pattern Inventory (Cluster-Level)"][0] : top_sections["Exhaustive Pattern Inventory (Cluster-Level)"][1]]
    )
    recluster_section_start, recluster_section_end = top_sections["Re-clustered Pattern Details"]
    reclustered = parse_reclustered_details(
        lines[recluster_section_start:recluster_section_end],
        outcomes,
        inventory,
        section_line_offset=recluster_section_start,
    )

    cluster_id = title_match.group("cluster_id")
    title = title_match.group("title")
    slug = path.stem.removeprefix(f"ERRORS-cluster-{cluster_id.lower()}-")

    # Join membership + outcome rows by variant for a query-friendly variant index.
    member_by_variant = {m["variant"]: m for m in cluster_summary["members"]}
    outcome_by_variant = {v["variant"]: v for v in outcomes.get("variant_level_comparison", [])}
    all_variants = sorted(set(member_by_variant) | set(outcome_by_variant))
    variants: list[dict[str, Any]] = []
    for variant in all_variants:
        m = member_by_variant.get(variant, {})
        o = outcome_by_variant.get(variant, {})
        variants.append(
            {
                "variant": variant,
                "canonical": bool(m.get("canonical") or o.get("canonical")),
                "relationship": m.get("relationship"),
                "final_submitters": o.get("final_submitters", m.get("final_submitters")),
                "full_pass": o.get("full_pass"),
                "non_full": o.get("non_full", m.get("non_full")),
                "parseable_non_full": o.get("parseable_non_full"),
                "non_parseable_non_full": o.get("non_parseable_non_full"),
            }
        )

    cluster = {
        "cluster_id": cluster_id,
        "title": title,
        "slug": slug,
        "analysis_file": str(path.relative_to(ROOT.parent)),
        "source_file_name": path.name,
        "cluster_summary": cluster_summary["summary"],
        "variants": variants,
        "canonical_question_spec": canonical_spec,
        "outcomes": {
            k: v
            for k, v in outcomes.items()
            if k != "variant_level_comparison"
        },
        "private_case_structure": private_case_structure,
        "pattern_inventory": inventory,
        "reclustered_patterns": reclustered,
        "source": {
            "line_count": len(lines),
        },
    }

    return cluster


def infer_pattern_tags(pattern_name: str) -> list[str]:
    name = pattern_name.lower()
    tags: set[str] = set()
    if "syntax / non-parseable" in name or "non-parseable" in name:
        tags.add("syntax")
    if name.startswith("runtime ") or " runtime " in f" {name} ":
        tags.add("runtime")
    for err in [
        "nameerror",
        "typeerror",
        "indexerror",
        "keyerror",
        "attributeerror",
        "valueerror",
        "zerodivisionerror",
        "eoferror",
        "recursionerror",
    ]:
        if err in name:
            tags.add(err)
    if "hard-code" in name or "hard-coded" in name or "copies evaluator/sample" in name:
        tags.update({"sample_overfit", "hard_coded"})
    if "placeholder" in name or "`...`" in pattern_name:
        tags.add("placeholder")
    if "returns inside" in name or "early return" in name:
        tags.update({"control_flow", "early_return"})
    if "no return" in name or "implicit `none`" in pattern_name.lower():
        tags.add("missing_return")
    if "always returns `true`" in pattern_name.lower() or "always returns `false`" in pattern_name.lower():
        tags.add("constant_output")
    if "reads input()" in name:
        tags.update({"io_contract", "reads_input_in_function"})
    if "prints" in name and "instead of return" in name:
        tags.update({"io_contract", "print_vs_return"})
    if "format" in name or "spacing" in name or "newline" in name:
        tags.add("formatting")
    if "off-by-one" in name or "threshold" in name or "boundary" in name:
        tags.add("boundary_case")
    if "duplicate" in name or "unique" in name:
        tags.add("set_uniqueness_logic")
    if "list/dict" in name or "wrong shape" in name or "container" in name:
        tags.add("data_shape")
    return sorted(tags)


def build_indexes(clusters: list[dict[str, Any]]) -> dict[str, Any]:
    cluster_rows: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    pattern_rows: list[dict[str, Any]] = []
    pattern_variant_rows: list[dict[str, Any]] = []
    example_rows: list[dict[str, Any]] = []

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        outcomes = cluster.get("outcomes", {})
        residual = cluster.get("reclustered_patterns", {}).get("residual_other")
        patterns = cluster.get("reclustered_patterns", {}).get("patterns", [])
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "title": cluster["title"],
                "analysis_file": cluster["analysis_file"],
                "variants_count": cluster.get("cluster_summary", {}).get("variants_in_cluster"),
                "final_submitters": outcomes.get("final_submitters"),
                "full_pass": outcomes.get("full_pass"),
                "non_full_final_submissions": outcomes.get("non_full_final_submissions"),
                "parseable_non_full": outcomes.get("parseable_non_full"),
                "non_parseable_non_full": outcomes.get("non_parseable_non_full"),
                "pattern_count": len(patterns),
                "residual_other_count": residual.get("count") if residual else None,
                "residual_other_pct": residual.get("pct") if residual else None,
            }
        )

        for variant in cluster.get("variants", []):
            variant_rows.append(
                {
                    "cluster_id": cluster_id,
                    "cluster_title": cluster["title"],
                    **variant,
                }
            )

        for pat in patterns:
            cf = pat.get("cluster_frequency") or {}
            pattern_rows.append(
                {
                    "cluster_id": cluster_id,
                    "cluster_title": cluster["title"],
                    "pattern_index": pat.get("pattern_index"),
                    "pattern_order": pat.get("order"),
                    "pattern_name": pat["name"],
                    "cluster_count": cf.get("count"),
                    "cluster_total_non_full": cf.get("total"),
                    "cluster_pct_non_full": cf.get("pct"),
                    "is_residual_other": pat["name"].lower().startswith("other wrong-answer logic pattern"),
                    "variant_frequencies": pat.get("variant_frequencies", []),
                    "dominant_private_case_vectors": pat.get("dominant_private_case_vectors", []),
                    "score_distribution_top": pat.get("score_distribution_top", []),
                    "interpretation": pat.get("interpretation"),
                    "example_count": len(pat.get("representative_examples", [])),
                    "tags": infer_pattern_tags(pat["name"]),
                }
            )
            for vf in pat.get("variant_frequencies", []):
                if "variant" not in vf:
                    continue
                pattern_variant_rows.append(
                    {
                        "cluster_id": cluster_id,
                        "cluster_title": cluster["title"],
                        "pattern_index": pat.get("pattern_index"),
                        "pattern_order": pat.get("order"),
                        "pattern_name": pat["name"],
                        "variant": vf.get("variant"),
                        "count": vf.get("count"),
                        "total_non_full_for_variant": vf.get("total"),
                        "pct_non_full_for_variant": vf.get("pct"),
                    }
                )
            for ex_idx, ex in enumerate(pat.get("representative_examples", []), start=1):
                if "student_id" not in ex:
                    continue
                example_rows.append(
                    {
                        "cluster_id": cluster_id,
                        "cluster_title": cluster["title"],
                        "pattern_index": pat.get("pattern_index"),
                        "pattern_name": pat["name"],
                        "example_index": ex_idx,
                        "variant": ex.get("variant"),
                        "student_id": ex.get("student_id"),
                        "summary": ex.get("summary"),
                        "score": ex.get("score"),
                        "score_label": ex.get("score_label"),
                        "vector": ex.get("vector"),
                        "code_lang": ex.get("code_lang"),
                        "code_length_chars": len(ex.get("code", "")) if isinstance(ex.get("code"), str) else None,
                        "source_line": ex.get("source_line"),
                    }
                )

    return {
        "cluster_rows": cluster_rows,
        "variant_rows": variant_rows,
        "pattern_rows": pattern_rows,
        "pattern_variant_rows": pattern_variant_rows,
        "example_rows": example_rows,
    }


def compute_summary(clusters: list[dict[str, Any]], indexes: dict[str, Any]) -> dict[str, Any]:
    totals = {
        "final_submitters": 0,
        "full_pass": 0,
        "non_full_final_submissions": 0,
        "parseable_non_full": 0,
        "non_parseable_non_full": 0,
        "pattern_sections": 0,
        "representative_examples": 0,
    }
    for cluster in clusters:
        outcomes = cluster.get("outcomes", {})
        for key in [
            "final_submitters",
            "full_pass",
            "non_full_final_submissions",
            "parseable_non_full",
            "non_parseable_non_full",
        ]:
            totals[key] += int(outcomes.get(key) or 0)
        patterns = cluster.get("reclustered_patterns", {}).get("patterns", [])
        totals["pattern_sections"] += len(patterns)
        totals["representative_examples"] += sum(
            len(p.get("representative_examples", [])) for p in patterns
        )

    return {
        "cluster_count": len(clusters),
        "variant_row_count": len(indexes["variant_rows"]),
        "pattern_row_count": len(indexes["pattern_rows"]),
        "pattern_variant_row_count": len(indexes["pattern_variant_rows"]),
        "example_row_count": len(indexes["example_rows"]),
        "totals": totals,
    }


def main() -> None:
    files = sorted(ROOT.glob(CLUSTER_GLOB))
    clusters = [parse_cluster_report(path) for path in files]
    clusters.sort(key=lambda c: c["cluster_id"])

    indexes = build_indexes(clusters)
    payload = {
        "schema_version": "errors-cluster-export.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": {
            "directory": str(ROOT.relative_to(ROOT.parent)),
            "glob": f"{ROOT.name}/{CLUSTER_GLOB}",
            "file_count": len(files),
            "files": [str(p.relative_to(ROOT.parent)) for p in files],
        },
        "summary": compute_summary(clusters, indexes),
        "clusters": clusters,
        "indexes": indexes,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUTPUT_PATH.relative_to(ROOT.parent)} "
        f"for {len(clusters)} clusters, {payload['summary']['pattern_row_count']} patterns"
    )


if __name__ == "__main__":
    main()
