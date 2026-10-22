"""Скрипт переноса существующих данных предметной области из JSON в SQLite."""

import json
from pathlib import Path
import sqlite3
from db.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
STUDENTS_FILE = BASE_DIR / "data" / "students.json"
SUPERVISORS_FILE = BASE_DIR / "data" / "supervisors.json"
TOPICS_FILE = BASE_DIR / "data" / "topics.json"
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"


def load_json(filepath: Path | str) -> list[dict]:
    """Прочитать список объектов из JSON-файла с кодировкой UTF-8."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def init_schema(conn: sqlite3.Connection) -> None:
    """Применить схему базы данных, если таблицы ещё не созданы."""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)


def clear_data(conn: sqlite3.Connection) -> None:
    """Очистить таблицы в порядке зависимостей для повторного безопасного импорта."""
    conn.execute("DELETE FROM status_history;")
    conn.execute("DELETE FROM topics;")
    conn.execute("DELETE FROM students;")
    conn.execute("DELETE FROM supervisors;")


def import_students(conn: sqlite3.Connection) -> int:
    """Импортировать список студентов в таблицу students."""
    students = load_json(STUDENTS_FILE)
    rows = [
        (
            item["id"],
            item["full_name"],
            item.get("group_name") or item.get("group", ""),
            item.get("direction", ""),
            item.get("email") or f"student_{item['id']}@example.com",
        )
        for item in students
    ]
    conn.executemany(
        """
        INSERT INTO students (
            id,
            full_name,
            group_name,
            direction,
            email
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def import_supervisors(conn: sqlite3.Connection) -> int:
    """Импортировать список научных руководителей в таблицу supervisors."""
    supervisors = load_json(SUPERVISORS_FILE)
    rows = [
        (
            item["id"],
            item["full_name"],
            item.get("degree", ""),
            item.get("position", ""),
            item.get("email") or f"supervisor_{item['id']}@example.com",
            item.get("max_topics", 5),
        )
        for item in supervisors
    ]
    conn.executemany(
        """
        INSERT INTO supervisors (
            id,
            full_name,
            degree,
            position,
            email,
            max_topics
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def import_topics(conn: sqlite3.Connection) -> int:
    """Импортировать список тем курсовых работ в таблицу topics."""
    topics = load_json(TOPICS_FILE)
    rows = [
        (
            item["id"],
            item["title"],
            item.get("description", ""),
            item["supervisor_id"],
            item.get("student_id"),
            item.get("status", "свободна"),
            item.get("deadline", "2026-12-15"),
        )
        for item in topics
    ]
    conn.executemany(
        """
        INSERT INTO topics (
            id,
            title,
            description,
            supervisor_id,
            student_id,
            status,
            deadline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def main():
    """Точка входа скрипта импорта данных."""
    conn = get_connection()
    try:
        init_schema(conn)
        clear_data(conn)
        n_students = import_students(conn)
        n_supervisors = import_supervisors(conn)
        n_topics = import_topics(conn)
        conn.commit()
        print(f"Успешный импорт: {n_students} студентов, "
              f"{n_supervisors} руководителей, {n_topics} тем.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
