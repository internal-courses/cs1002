COPY (
  SELECT DISTINCT
    Namespace,
    CAST(ProblemID AS INTEGER) AS ProblemID,
    StudentID
  FROM read_json(
    'submissions/*.json',
    format = 'newline_delimited',
    columns = {
      Namespace: 'VARCHAR',
      ProblemID: 'VARCHAR',
      StudentID: 'VARCHAR'
    }
  )
  ORDER BY Namespace, ProblemID, StudentID
) TO 'analysis/student-question-pairs.csv' (HEADER, DELIMITER ',');
