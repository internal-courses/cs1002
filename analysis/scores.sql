COPY (
  SELECT
    Namespace,
    CAST(ProblemID AS INTEGER) AS ProblemID,
    StudentID,
    FileName,
    EvaluationType,
    TRY_CAST(json_extract_string(CompilationResult, '$.score') AS DOUBLE) AS "CompilationResult.score"
  FROM read_json(
    'submissions/*.json',
    format = 'newline_delimited',
    columns = {
      Namespace: 'VARCHAR',
      ProblemID: 'VARCHAR',
      StudentID: 'VARCHAR',
      FileName: 'VARCHAR',
      EvaluationType: 'VARCHAR',
      CompilationResult: 'VARCHAR'
    }
  )
  ORDER BY Namespace, ProblemID, StudentID, FileName, EvaluationType, "CompilationResult.score"
) TO 'analysis/scores.csv' (HEADER, DELIMITER ',');
