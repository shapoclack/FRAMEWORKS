"""Модуль подключения к базе данных SQLite."""

import os
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "coursework.sqlite"
DB_PATH = str(DB_FILE)


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Создать и вернуть соединение с базой данных SQLite.

    Включает проверку внешних ключей командой PRAGMA foreign_keys = ON.
    """
    target_path = str(db_path) if db_path else DB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
