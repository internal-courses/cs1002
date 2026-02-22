#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "anomalous_accounts.csv"

QUERY = r'''
WITH submissions AS (
  SELECT
    StudentID,
    Namespace,
    regexp_extract(Namespace, '^ns_([0-9]{2}t[0-9]+)_', 1) AS term,
    regexp_replace(Namespace, '_(1|2)$', '') AS base_ns
  FROM read_json(
    'submissions/*.json',
    format='newline_delimited',
    columns={StudentID:'VARCHAR', Namespace:'VARCHAR'}
  )
),
sub_metrics AS (
  SELECT
    StudentID,
    COUNT(*) AS total_event_rows,
    COUNT(DISTINCT Namespace) AS namespace_count,
    COUNT(DISTINCT term) AS term_count,
    COUNT(*)::DOUBLE / NULLIF(COUNT(DISTINCT Namespace), 0) AS avg_events_per_namespace
  FROM submissions
  GROUP BY StudentID
),
final_metrics AS (
  SELECT
    StudentID,
    COUNT(*) AS final_rows,
    COUNT(DISTINCT Namespace) AS final_namespace_count
  FROM read_csv_auto('analysis/final_scores.csv', header=true)
  GROUP BY StudentID
),
variant_overlap AS (
  SELECT
    StudentID,
    COUNT(*) FILTER (WHERE variant_count > 1) AS base_exams_with_both_variants
  FROM (
    SELECT StudentID, base_ns, COUNT(DISTINCT Namespace) AS variant_count
    FROM submissions
    GROUP BY StudentID, base_ns
  ) t
  GROUP BY StudentID
),
joined AS (
  SELECT
    s.StudentID,
    s.namespace_count,
    s.term_count,
    s.total_event_rows,
    s.avg_events_per_namespace,
    COALESCE(f.final_rows, 0) AS final_rows,
    COALESCE(f.final_namespace_count, 0) AS final_namespace_count,
    COALESCE(v.base_exams_with_both_variants, 0) AS base_exams_with_both_variants
  FROM sub_metrics s
  LEFT JOIN final_metrics f USING (StudentID)
  LEFT JOIN variant_overlap v USING (StudentID)
),
thresholds AS (
  SELECT
    GREATEST(CAST(ceil(quantile_cont(namespace_count, 0.99)) AS BIGINT), 7) AS namespace_threshold,
    CAST(ceil(quantile_cont(total_event_rows, 0.99)) AS BIGINT) AS event_rows_threshold,
    CAST(ceil(quantile_cont(final_rows, 0.99)) AS BIGINT) AS final_rows_threshold,
    quantile_cont(avg_events_per_namespace, 0.99) AS avg_events_per_namespace_threshold
  FROM joined
),
scored AS (
  SELECT
    j.*,
    t.namespace_threshold,
    t.event_rows_threshold,
    t.final_rows_threshold,
    t.avg_events_per_namespace_threshold,
    (j.namespace_count >= t.namespace_threshold) AS flag_namespace_count_outlier,
    (j.total_event_rows >= t.event_rows_threshold) AS flag_event_volume_outlier,
    (j.final_rows >= t.final_rows_threshold) AS flag_final_rows_outlier,
    (j.base_exams_with_both_variants > 0) AS flag_dual_variant,
    ((j.namespace_count::DOUBLE / NULLIF(j.term_count, 0)) > 3.0) AS flag_high_namespace_per_term
  FROM joined j
  CROSS JOIN thresholds t
),
final AS (
  SELECT
    StudentID AS student_id,
    namespace_count,
    term_count,
    total_event_rows,
    final_rows,
    final_namespace_count,
    base_exams_with_both_variants,
    ROUND(avg_events_per_namespace, 2) AS avg_events_per_namespace,
    namespace_threshold,
    event_rows_threshold,
    final_rows_threshold,
    ROUND(avg_events_per_namespace_threshold, 2) AS avg_events_per_namespace_threshold,
    flag_namespace_count_outlier,
    flag_event_volume_outlier,
    flag_final_rows_outlier,
    flag_dual_variant,
    flag_high_namespace_per_term,
    (
      CAST(flag_namespace_count_outlier AS INT)
      + CAST(flag_event_volume_outlier AS INT)
      + CAST(flag_final_rows_outlier AS INT)
      + CAST(flag_dual_variant AS INT)
      + CAST(flag_high_namespace_per_term AS INT)
    ) AS anomaly_score,
    trim(both ',' FROM
      CASE WHEN flag_namespace_count_outlier THEN 'namespace_count_outlier,' ELSE '' END ||
      CASE WHEN flag_event_volume_outlier THEN 'event_volume_outlier,' ELSE '' END ||
      CASE WHEN flag_final_rows_outlier THEN 'final_rows_outlier,' ELSE '' END ||
      CASE WHEN flag_dual_variant THEN 'dual_variant_assignment,' ELSE '' END ||
      CASE WHEN flag_high_namespace_per_term THEN 'high_namespace_per_term,' ELSE '' END
    ) AS anomaly_reasons
  FROM scored
)
SELECT *
FROM final
WHERE anomaly_score > 0
ORDER BY anomaly_score DESC, namespace_count DESC, total_event_rows DESC, final_rows DESC, student_id;
'''


def main() -> None:
    res = subprocess.run(
        ["duckdb", "-csv", "-c", QUERY],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(res.stdout, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
