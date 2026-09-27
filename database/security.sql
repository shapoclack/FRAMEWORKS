
-- Разграничение доступа (роли и права)

-- Приложение: читает и пишет данные
CREATE ROLE app_user LOGIN PASSWORD 'change_me_in_prod';

GRANT CONNECT ON DATABASE coursework TO app_user;
GRANT USAGE   ON SCHEMA   public     TO app_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON topics, students, supervisors
    TO app_user;
GRANT SELECT, INSERT                 ON status_history TO app_user;

-- Последовательности для SERIAL
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Аналитик: только чтение
CREATE ROLE analyst LOGIN PASSWORD 'change_me_in_prod';
GRANT CONNECT ON DATABASE coursework TO analyst;
GRANT USAGE   ON SCHEMA   public     TO analyst;
GRANT SELECT  ON ALL TABLES IN SCHEMA public TO analyst;

-- Убираем доступ у public
REVOKE ALL ON SCHEMA public FROM PUBLIC;