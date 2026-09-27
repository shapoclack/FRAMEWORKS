
-- Примеры запросов, которые будут использоваться в приложении


-- 1. Все темы со студентами и руководителями
SELECT
    t.id,
    t.title,
    t.status,
    t.deadline,
    s.full_name  AS student,
    sv.full_name AS supervisor
FROM topics t
LEFT JOIN students    s  ON s.id  = t.student_id
LEFT JOIN supervisors sv ON sv.id = t.supervisor_id
ORDER BY t.created_at DESC;

-- 2. Свободные темы
SELECT id, title, deadline
FROM topics
WHERE status = 'свободна'
ORDER BY deadline;

-- 3. Темы конкретного руководителя
SELECT id, title, status
FROM topics
WHERE supervisor_id = 1
ORDER BY title;

-- 4. Статистика по статусам
SELECT status, COUNT(*) AS count
FROM topics
GROUP BY status
ORDER BY count DESC;

-- 5. Загруженность руководителей
SELECT
    sv.full_name,
    sv.max_topics,
    COUNT(t.id) AS active_topics,
    sv.max_topics - COUNT(t.id) AS free_slots
FROM supervisors sv
LEFT JOIN topics t
       ON t.supervisor_id = sv.id
      AND t.status IN ('закреплена', 'на проверке', 'защищена')
GROUP BY sv.id, sv.full_name, sv.max_topics
ORDER BY active_topics DESC;

-- 6. Поиск по названию (триграммный индекс)
SELECT id, title, status
FROM topics
WHERE title ILIKE '%веб%'
ORDER BY similarity(title, 'веб') DESC;

-- 7. Темы с истекающим сроком (следующие 30 дней)
SELECT id, title, deadline, supervisor_id
FROM topics
WHERE deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
  AND status <> 'защищена'
ORDER BY deadline;

-- 8. История смены статуса конкретной темы
SELECT
    h.changed_at,
    h.old_status,
    h.new_status
FROM status_history h
WHERE h.topic_id = 4
ORDER BY h.changed_at;

-- 9. Студенты без закреплённой темы
SELECT s.id, s.full_name, s.group_name
FROM students s
LEFT JOIN topics t ON t.student_id = s.id
WHERE t.id IS NULL;

-- 10. Отчёт для методиста (сводный)
SELECT
    sv.full_name  AS supervisor,
    COUNT(t.id)   AS total_topics,
    SUM(CASE WHEN t.status = 'свободна'    THEN 1 ELSE 0 END) AS free,
    SUM(CASE WHEN t.status = 'закреплена'  THEN 1 ELSE 0 END) AS taken,
    SUM(CASE WHEN t.status = 'на проверке' THEN 1 ELSE 0 END) AS review,
    SUM(CASE WHEN t.status = 'защищена'    THEN 1 ELSE 0 END) AS done
FROM supervisors sv
LEFT JOIN topics t ON t.supervisor_id = sv.id
GROUP BY sv.id, sv.full_name
ORDER BY total_topics DESC;