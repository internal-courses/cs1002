COPY (
  WITH base AS (
    SELECT
      StudentID,
      Namespace,
      TRY_CAST("CompilationResult.score" AS DOUBLE) AS score
    FROM read_csv_auto('analysis/final_scores.csv', header = true)
  )
  PIVOT base
  ON Namespace
  USING SUM(score)
  GROUP BY StudentID
  ORDER BY StudentID
) TO 'analysis/final_scores_pivot.csv' (HEADER, DELIMITER ',');
