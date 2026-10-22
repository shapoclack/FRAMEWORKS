"""Тесты базы данных SQLite, схемы и SQL-запросов (Практическая работа № 7)."""

import sqlite3
from db.database import get_connection


def test_db_connection():
    """Проверка подключения к SQLite и включения PRAGMA foreign_keys."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    fk_status = cursor.fetchone()[0]
    conn.close()
    assert fk_status == 1, "PRAGMA foreign_keys должна быть включена (1)"


def test_tables_exist():
    """Проверка наличия всех требуемых таблиц предметной области."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected_tables = {"students", "supervisors", "topics", "status_history"}
    for table in expected_tables:
        assert table in tables, f"Таблица {table} должна присутствовать в БД"


def test_foreign_keys_configured():
    """Проверка внешних ключей в таблице topics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_key_list(topics)")
    fks = cursor.fetchall()
    conn.close()

    fk_tables = {row[2] for row in fks}
    assert "supervisors" in fk_tables
    assert "students" in fk_tables


def test_sqlite_row_factory():
    """Проверка доступа к полям через sqlite3.Row по именам."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT id, title, status FROM topics LIMIT 1").fetchone()
    conn.close()

    assert row is not None
    assert row["id"] >= 1
    assert isinstance(row["title"], str)
    assert isinstance(row["status"], str)


def test_parameterized_query():
    """Проверка выполнения параметризованного запроса со знаком вопроса (?)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    status_target = "свободна"
    rows = conn.execute(
        "SELECT id, title FROM topics WHERE status = ? ORDER BY title",
        (status_target,),
    ).fetchall()
    conn.close()

    assert len(rows) > 0
    for r in rows:
        assert r["title"]


def test_all_queries_from_sql_file():
    """Проверка синтаксиса и выполнения всех 17 запросов из sql/queries.sql."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    with open("sql/queries.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Разделяем на отдельные запросы по точке с запятой
    queries = [q.strip() for q in sql_content.split(";") if q.strip()]

    for idx, raw_query in enumerate(queries, 1):
        # Удаляем комментарии в начале, если есть
        lines = [line for line in raw_query.splitlines() if not line.strip().startswith("--")]
        clean_query = "\n".join(lines).strip()
        if not clean_query:
            continue
        cursor = conn.execute(clean_query)
        result = cursor.fetchall()
        assert result is not None, f"Запрос #{idx} завершился без результата"

    conn.close()
