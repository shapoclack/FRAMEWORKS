-- =====================================================================
-- Система учета тем курсовых работ
-- Схема базы данных SQLite (Практическая работа № 7)
-- =====================================================================

-- 1. Таблица студентов
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    direction TEXT,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. Таблица научных руководителей
CREATE TABLE IF NOT EXISTS supervisors (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    degree TEXT,
    position TEXT,
    email TEXT NOT NULL UNIQUE,
    max_topics INTEGER NOT NULL DEFAULT 5 CHECK (max_topics BETWEEN 1 AND 20),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 3. Таблица тем курсовых работ
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    supervisor_id INTEGER NOT NULL,
    student_id INTEGER,
    status TEXT NOT NULL DEFAULT 'свободна' CHECK (status IN ('свободна', 'закреплена', 'на проверке', 'защищена')),
    deadline TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (supervisor_id) REFERENCES supervisors(id) ON DELETE RESTRICT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

-- 4. Таблица истории изменения статусов (аудит)
CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now')),
    changed_by TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);
