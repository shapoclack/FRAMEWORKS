-- =====================================================================
-- Система учета тем курсовых работ
-- Набор SQL-запросов для СУБД SQLite (Практическая работа № 7)
-- =====================================================================

-- =====================================================================
-- РАЗДЕЛ 1. ВЫБОРКА СПИСКОВ ОБЪЕКТОВ (SELECT, ORDER BY, LIMIT, OFFSET)
-- =====================================================================

-- 1. Получение списка всех тем курсовых работ с сортировкой по названию
SELECT
    id,
    title,
    description,
    status,
    deadline
FROM topics
ORDER BY title ASC;

-- 2. Получение списка всех научных руководителей с сортировкой по ФИО
SELECT
    id,
    full_name,
    degree,
    position,
    email,
    max_topics
FROM supervisors
ORDER BY full_name ASC;

-- 3. Получение списка студентов с пагинацией (первые 5 записей со смещением)
SELECT
    id,
    full_name,
    group_name,
    direction,
    email
FROM students
ORDER BY full_name ASC
LIMIT 5 OFFSET 0;


-- =====================================================================
-- РАЗДЕЛ 2. ФИЛЬТРАЦИЯ ДАННЫХ (WHERE: =, LIKE, IN, NOT IN, BETWEEN)
-- =====================================================================

-- 4. Выборка свободных тем, доступных для выбора студентами
SELECT
    id,
    title,
    deadline,
    supervisor_id
FROM topics
WHERE status = 'свободна' AND student_id IS NULL
ORDER BY deadline ASC;

-- 5. Поиск тем по ключевому слову в названии или аннотации (параметризованный поиск)
SELECT
    id,
    title,
    description,
    status
FROM topics
WHERE title LIKE '%веб%' OR description LIKE '%Django%'
ORDER BY title ASC;

-- 6. Поиск студентов, у которых еще нет закрепленной темы курсовой работы (подзапрос NOT IN)
SELECT
    id,
    full_name,
    group_name,
    email
FROM students
WHERE id NOT IN (
    SELECT student_id
    FROM topics
    WHERE student_id IS NOT NULL
)
ORDER BY group_name ASC, full_name ASC;

-- 7. Темы курсовых работ с дедлайном сдачи в заданном диапазоне дат (BETWEEN)
SELECT
    id,
    title,
    status,
    deadline
FROM topics
WHERE deadline BETWEEN '2026-11-01' AND '2026-12-31'
ORDER BY deadline ASC;


-- =====================================================================
-- РАЗДЕЛ 3. СОЕДИНЕНИЕ ТАБЛИЦ (INNER JOIN, LEFT JOIN)
-- =====================================================================

-- 8. Полная информация о теме: название, статус, дедлайн, научный руководитель и студент
SELECT
    t.id,
    t.title,
    t.status,
    t.deadline,
    sv.full_name AS supervisor_name,
    sv.degree AS supervisor_degree,
    sv.email AS supervisor_email,
    s.full_name AS student_name,
    s.group_name AS student_group
FROM topics t
JOIN supervisors sv ON t.supervisor_id = sv.id
LEFT JOIN students s ON t.student_id = s.id
ORDER BY t.title ASC;

-- 9. Активные темы в работе (закреплена или на проверке) со всеми контактными данными
SELECT
    t.id,
    t.title,
    t.status,
    t.deadline,
    sv.full_name AS supervisor_name,
    sv.email AS supervisor_email,
    s.full_name AS student_name,
    s.group_name AS student_group,
    s.email AS student_email
FROM topics t
JOIN supervisors sv ON t.supervisor_id = sv.id
JOIN students s ON t.student_id = s.id
WHERE t.status IN ('закреплена', 'на проверке')
ORDER BY t.deadline ASC;

-- 10. Свободные темы конкретного научного руководителя с его реквизитами
SELECT
    t.id,
    t.title,
    t.description,
    t.deadline,
    sv.full_name AS supervisor_name,
    sv.position AS supervisor_position
FROM topics t
JOIN supervisors sv ON t.supervisor_id = sv.id
WHERE t.status = 'свободна' AND t.supervisor_id = 1
ORDER BY t.title ASC;


-- =====================================================================
-- РАЗДЕЛ 4. АГРЕГАТНЫЕ ФУНКЦИИ (COUNT, SUM, AVG, MIN, MAX)
-- =====================================================================

-- 11. Общая статистика тем по статусам (COUNT и вычисляемые суммы SUM CASE)
SELECT
    COUNT(*) AS total_topics,
    SUM(CASE WHEN status = 'свободна' THEN 1 ELSE 0 END) AS free_count,
    SUM(CASE WHEN status = 'закреплена' THEN 1 ELSE 0 END) AS assigned_count,
    SUM(CASE WHEN status = 'на проверке' THEN 1 ELSE 0 END) AS review_count,
    SUM(CASE WHEN status = 'защищена' THEN 1 ELSE 0 END) AS defended_count
FROM topics;

-- 12. Агрегатные показатели лимита тем по кафедре (COUNT, AVG, MIN, MAX)
SELECT
    COUNT(*) AS total_supervisors,
    AVG(max_topics) AS avg_max_topics,
    MIN(max_topics) AS min_topics_limit,
    MAX(max_topics) AS max_topics_limit
FROM supervisors;


-- =====================================================================
-- РАЗДЕЛ 5. ГРУППИРОВКА ЗАПИСЕЙ (GROUP BY)
-- =====================================================================

-- 13. Количество тем у каждого руководителя (LEFT JOIN + GROUP BY для учета руководителей без тем)
SELECT
    sv.id AS supervisor_id,
    sv.full_name AS supervisor_name,
    sv.max_topics,
    COUNT(t.id) AS topics_count
FROM supervisors sv
LEFT JOIN topics t ON sv.id = t.supervisor_id
GROUP BY sv.id, sv.full_name, sv.max_topics
ORDER BY topics_count DESC, sv.full_name ASC;

-- 14. Распределение тем по статусам (GROUP BY status)
SELECT
    status,
    COUNT(*) AS status_count
FROM topics
GROUP BY status
ORDER BY status_count DESC;

-- 15. Распределение студентов по учебным группам (GROUP BY group_name)
SELECT
    group_name,
    COUNT(*) AS students_count
FROM students
GROUP BY group_name
ORDER BY group_name ASC;


-- =====================================================================
-- РАЗДЕЛ 6. ФИЛЬТРАЦИЯ ГРУПП (HAVING)
-- =====================================================================

-- 16. Научные руководители, у которых количество тем больше 2 (GROUP BY + HAVING)
SELECT
    sv.id AS supervisor_id,
    sv.full_name AS supervisor_name,
    COUNT(t.id) AS topics_count
FROM supervisors sv
JOIN topics t ON sv.id = t.supervisor_id
GROUP BY sv.id, sv.full_name
HAVING COUNT(t.id) > 2
ORDER BY topics_count DESC;

-- 17. Учебные группы с количеством студентов более 1 (GROUP BY + HAVING)
SELECT
    group_name,
    COUNT(*) AS students_count
FROM students
GROUP BY group_name
HAVING COUNT(*) > 1
ORDER BY students_count DESC;
