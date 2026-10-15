"""Сохранение и загрузка данных проекта в JSON-файлы."""

import json
import os


def load_json(filename: str) -> list[dict]:
    """Загрузить список словарей из JSON.

    При отсутствии файла или ошибке чтения возвращает пустой список.
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(filename: str, data: list[dict]) -> None:
    """Сохранить список словарей в JSON с отступами."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- Специализированные обёртки ---

def load_topics(filename: str = "data/topics.json") -> list[dict]:
    return load_json(filename)


def save_topics(topics: list[dict], filename: str = "data/topics.json") -> None:
    save_json(filename, topics)


def load_students(filename: str = "data/students.json") -> list[dict]:
    return load_json(filename)


def save_students(
    students: list[dict], filename: str = "data/students.json"
) -> None:
    save_json(filename, students)


def load_supervisors(filename: str = "data/supervisors.json") -> list[dict]:
    return load_json(filename)


def save_supervisors(
    supervisors: list[dict], filename: str = "data/supervisors.json"
) -> None:
    save_json(filename, supervisors)