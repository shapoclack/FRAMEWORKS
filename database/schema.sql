
-- Система учета тем курсовых работ
-- Схема базы данных (Postgre)
DROP TABLE IF EXISTS status_history CASCADE;
DROP TABLE IF EXISTS topics CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS supervisors CASCADE;

-- ---------- Студенты ----------
CREATE TABLE students (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(150) NOT NULL,
    group_name  VARCHAR(20)  NOT NULL,
    direction   VARCHAR(200),
    email       VARCHAR(100) NOT NULL UNIQUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  students IS 'Студенты, выполняющие курсовые работы';
COMMENT ON COLUMN students.group_name IS 'Номер группы, например ПИ-21-1';

-- ---------- Руководители ----------
CREATE TABLE supervisors (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(150) NOT NULL,
    degree      VARCHAR(50),
    position    VARCHAR(100),
    email       VARCHAR(100) NOT NULL UNIQUE,
    max_topics  SMALLINT     NOT NULL DEFAULT 5
        CHECK (max_topics BETWEEN 1 AND 20),
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  supervisors IS 'Научные руководители курсовых работ';
COMMENT ON COLUMN supervisors.max_topics IS 'Максимум тем, которые может вести';

-- ---------- Темы ----------
CREATE TABLE topics (
    id             SERIAL PRIMARY KEY,
    title          VARCHAR(300) NOT NULL,
    description    TEXT,
    supervisor_id  INTEGER      NOT NULL
        REFERENCES supervisors(id) ON DELETE RESTRICT,
    student_id     INTEGER
        REFERENCES students(id)    ON DELETE SET NULL,
    status         VARCHAR(20)  NOT NULL DEFAULT 'свободна'
        CHECK (status IN ('свободна', 'закреплена',
                          'на проверке', 'защищена')),
    deadline       DATE,
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  topics IS 'Темы курсовых работ';
COMMENT ON COLUMN topics.status IS 'свободна | закреплена | на проверке | защищена';

-- ---------- История статусов ----------
CREATE TABLE status_history (
    id          SERIAL PRIMARY KEY,
    topic_id    INTEGER      NOT NULL
        REFERENCES topics(id) ON DELETE CASCADE,
    old_status  VARCHAR(20)  NOT NULL,
    new_status  VARCHAR(20)  NOT NULL,
    changed_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    changed_by  INTEGER
);

COMMENT ON TABLE status_history IS 'Аудит смены статусов тем';