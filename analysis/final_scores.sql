COPY (
  WITH events AS (
    SELECT
      Namespace,
      CAST(ProblemID AS INTEGER) AS ProblemID,
      StudentID,
      FileName,
      regexp_extract(FileName, '/(saved_code|test_run|submission)/', 1) AS event_type,
      strptime(
        regexp_extract(FileName, '_([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)$', 1),
        '%Y-%m-%dT%H:%M:%S.%fZ'
      ) AS event_ts,
      TRY_CAST(json_extract_string(CompilationResult, '$.score') AS DOUBLE) AS score
    FROM read_json(
      'submissions/*.json',
      format = 'newline_delimited',
      columns = {
        Namespace: 'VARCHAR',
        ProblemID: 'VARCHAR',
        StudentID: 'VARCHAR',
        FileName: 'VARCHAR',
        CompilationResult: 'VARCHAR'
      }
    )
    WHERE FileName IS NOT NULL AND FileName <> ''
  ),
  per_combo AS (
    SELECT
      Namespace,
      ProblemID,
      StudentID,
      MIN(event_ts) AS first_event,
      MAX(event_ts) AS last_event,
      COUNT(*) FILTER (WHERE event_type = 'saved_code') AS saved_code_events,
      COUNT(*) FILTER (WHERE event_type = 'test_run') AS test_run_events,
      COUNT(*) FILTER (WHERE event_type = 'submission') AS submission_events
    FROM events
    GROUP BY Namespace, ProblemID, StudentID
  ),
  latest_submission AS (
    SELECT
      Namespace,
      ProblemID,
      StudentID,
      FileName,
      score
    FROM (
      SELECT
        Namespace,
        ProblemID,
        StudentID,
        FileName,
        score,
        ROW_NUMBER() OVER (
          PARTITION BY Namespace, ProblemID, StudentID
          ORDER BY event_ts DESC, FileName DESC
        ) AS rn
      FROM events
      WHERE event_type = 'submission'
    ) s
    WHERE rn = 1
  )
  SELECT
    p.Namespace,
    p.ProblemID,
    p.StudentID,
    l.FileName,
    l.score AS "CompilationResult.score",
    p.first_event AS first_event_utc,
    p.last_event AS last_event_utc,
    p.first_event + INTERVAL 330 MINUTE AS first_event_ist,
    p.last_event + INTERVAL 330 MINUTE AS last_event_ist,
    p.saved_code_events,
    p.test_run_events,
    p.submission_events,
    p.saved_code_events + p.test_run_events + p.submission_events AS total_events
  FROM per_combo p
  LEFT JOIN latest_submission l
    USING (Namespace, ProblemID, StudentID)
  ORDER BY p.Namespace, p.ProblemID, p.StudentID
) TO 'analysis/final_scores.csv' (HEADER, DELIMITER ',');
