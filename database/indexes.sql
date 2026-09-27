
-- Индексы для оптимизации запросов


-- Быстрый фильтр по статусу (частый запрос: "свободные темы")
CREATE INDEX idx_topics_status
    ON topics(status);

-- Нагрузка руководителя (запрос: "темы руководителя X")
CREATE INDEX idx_topics_supervisor
    ON topics(supervisor_id);

-- Темы студента (запрос: "моя тема")
CREATE INDEX idx_topics_student
    ON topics(student_id);

-- Поиск по названию (LIKE / trigram)
CREATE INDEX idx_topics_title
    ON topics(title);

-- Триграммный индекс для быстрого LIKE '%...%'
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_topics_title_trgm
    ON topics USING gin (title gin_trgm_ops);

-- Сортировка по сроку сдачи
CREATE INDEX idx_topics_deadline
    ON topics(deadline);

-- Составной индекс для частой комбинации
CREATE INDEX idx_topics_status_supervisor
    ON topics(status, supervisor_id);

-- История по теме
CREATE INDEX idx_history_topic
    ON status_history(topic_id);

-- История по дате (для отчётов)
CREATE INDEX idx_history_changed_at
    ON status_history(changed_at);