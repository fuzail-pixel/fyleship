SELECT COUNT(*)
FROM assignments
WHERE grade = 'A'
  AND state = 'GRADED'
  AND teacher_id = (
      SELECT teacher_id
      FROM assignments
      WHERE state = 'GRADED'
      GROUP BY teacher_id
      ORDER BY COUNT(*) DESC
      LIMIT 1
  );