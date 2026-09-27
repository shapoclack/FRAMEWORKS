
-- Тестовые данные для разработки и демонстрации


-- Студенты
INSERT INTO students (full_name, group_name, direction, email) VALUES
    ('Иванов Иван Иванович',   'ПИ-21-1', 'Программная инженерия', 'ivanov@example.com'),
    ('Петров Пётр Петрович',   'ПИ-21-1', 'Программная инженерия', 'petrov@example.com'),
    ('Сидорова Анна Сергеевна','ПИ-21-2', 'Прикладная информатика','sidorova@example.com');

-- Руководители
INSERT INTO supervisors (full_name, degree, position, email, max_topics) VALUES
    ('Петрова Анна Сергеевна',   'к.т.н.', 'доцент',   'petrova@example.com', 5),
    ('Сидоров Пётр Алексеевич',  'д.т.н.', 'профессор','sidorov@example.com', 3),
    ('Кузнецов Дмитрий Игоревич','к.ф.-м.н.','ст. преподаватель','kuznetsov@example.com', 7);

-- Темы
INSERT INTO topics (title, description, supervisor_id, status, deadline) VALUES
    ('Разработка веб-приложения для учёта курсовых работ',
     'Django + PostgreSQL + REST API',
     1, 'свободна', '2026-12-15'),

    ('Анализ алгоритмов машинного обучения на открытых данных',
     'Сравнение ML-моделей',
     2, 'свободна', '2026-12-20'),

    ('Оптимизация SQL-запросов в высоконагруженных системах',
     'Индексы, EXPLAIN ANALYZE, денормализация',
     2, 'свободна', '2026-12-10'),

    ('Разработка Telegram-бота для учёта студенческих заявок',
     'Python + aiogram + SQLite',
     3, 'закреплена', '2026-12-25');

-- Закрепление темы за студентом (пример)
UPDATE topics
SET student_id = 1, status = 'закреплена'
WHERE id = 4;

-- Проверка
SELECT id, title, status, student_id FROM topics ORDER BY id;
SELECT id, topic_id, old_status, new_status, changed_at
FROM status_history ORDER BY id;