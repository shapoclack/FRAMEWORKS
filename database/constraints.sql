
-- Триггеры и дополнительные ограничения


-- 1. Автологирование смены статуса темы
CREATE OR REPLACE FUNCTION log_topic_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO status_history (topic_id, old_status, new_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_topic_status_change ON topics;
CREATE TRIGGER trg_topic_status_change
    AFTER UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION log_topic_status_change();

-- 2. Проверка: у закреплённой темы должен быть студент
CREATE OR REPLACE FUNCTION check_topic_consistency()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'закреплена' AND NEW.student_id IS NULL THEN
        RAISE EXCEPTION
            'Тема со статусом "закреплена" должна иметь student_id';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_topic_consistency ON topics;
CREATE TRIGGER trg_topic_consistency
    BEFORE INSERT OR UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION check_topic_consistency();

-- 3. Проверка лимита тем у руководителя
CREATE OR REPLACE FUNCTION check_supervisor_limit()
RETURNS TRIGGER AS $$
DECLARE
    current_count INTEGER;
    max_allowed   INTEGER;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM topics
    WHERE supervisor_id = NEW.supervisor_id
      AND status IN ('закреплена', 'на проверке', 'защищена');

    SELECT max_topics INTO max_allowed
    FROM supervisors
    WHERE id = NEW.supervisor_id;

    IF current_count >= max_allowed THEN
        RAISE EXCEPTION
            'Руководитель уже ведёт максимальное количество тем (%)',
            max_allowed;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_supervisor_limit ON topics;
CREATE TRIGGER trg_supervisor_limit
    BEFORE INSERT OR UPDATE ON topics
    FOR EACH ROW
    WHEN (NEW.status IN ('закреплена', 'на проверке', 'защищена'))
    EXECUTE FUNCTION check_supervisor_limit();