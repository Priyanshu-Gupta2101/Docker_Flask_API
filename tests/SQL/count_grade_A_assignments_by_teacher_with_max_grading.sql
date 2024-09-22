-- Write query to find the number of grade A's given by the teacher who has graded the most assignments

WITH teacher_graded_counts AS (
    SELECT teacher_id, COUNT(*) as graded_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
),
top_grading_teacher AS (
    SELECT teacher_id
    FROM teacher_graded_counts
    ORDER BY graded_count DESC
    LIMIT 1
)
SELECT COUNT(*) as grade_a_count
FROM assignments a
JOIN top_grading_teacher t ON a.teacher_id = t.teacher_id
WHERE a.grade = 'A' AND a.state = 'GRADED';