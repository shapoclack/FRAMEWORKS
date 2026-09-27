"""Функции работы со студентами."""

from utils import next_id


def add_student(
    students: list[dict],
    full_name: str,
    group: str,
    direction: str,
) -> dict:
    """Добавить студента."""
    student = {
        "id": next_id(students),
        "full_name": full_name,
        "group": group,
        "direction": direction,
    }
    students.append(student)
    return student


def find_student(students: list[dict], query: str) -> list[dict]:
    """Найти студентов по подстроке в ФИО или группе."""
    q = query.lower()
    return [
        s for s in students
        if q in s["full_name"].lower() or q in s["group"].lower()
    ]


def get_student_by_id(students: list[dict], student_id: int) -> dict | None:
    """Вернуть студента по id или None."""
    for s in students:
        if s["id"] == student_id:
            return s
    return None
