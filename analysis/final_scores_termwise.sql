COPY (
  SELECT
    StudentID,
    regexp_extract(Namespace, '^ns_([0-9]{2}t[0-9]+)_', 1) AS YearTerm,
    SUM(TRY_CAST("CompilationResult.score" AS DOUBLE)) AS Score,
    COUNT(*) * 100.0 AS Max
  FROM read_csv_auto('analysis/final_scores.csv', header = true)
  GROUP BY StudentID, YearTerm
  ORDER BY StudentID, YearTerm
) TO 'analysis/final_scores_termwise.csv' (HEADER, DELIMITER ',');
