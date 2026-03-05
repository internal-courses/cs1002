# AGENTS.md

1. Reproducibility is mandatory.
   - Generate new analysis via by checked-in code (`analysis/*.py`, `analysis/*.sql`), rerunnable from raw/canonical data.
   - If a report is generated, keep the generator and output in sync (edit via generator, then rerun).
2. Treat generated files as ephemeral unless explicitly needed by a story/app.
   - `analysis/*.csv` is ignored by default.
   - If an HTML story depends on a generated file at runtime, explicitly unignore and commit that file (example pattern already used: `analysis/teachable.csv`).
3. Keep stakeholder-facing docs stable on reruns.
   - For non-technical audiences, preserve a top-level plain-language summary (ELI15) and clear action recommendations.
   - Do not let reruns remove these sections.
4. Check if your claims are naive, or based on a lack of understanding of the course design. For example:
   - Terms are progression-filtered (later terms contain more repeaters by design). Any cross-term pass-rate comparison must explicitly state this and/or factor this in.
