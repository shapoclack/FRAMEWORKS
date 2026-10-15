"""Функции работы с руководителями и закреплением тем."""

from utils import next_id


def add_supervisor(
    supervisors: list[dict],
    full_name: str,
    degree: str,
    position: str,
) -> dict:
    """Добавить научного руководителя."""
    supervisor = {
        "id": next_id(supervisors),
        "full_name": full_name,
        "degree": degree,
        "position": position,
    }
    supervisors.append(supervisor)
    return supervisor


def get_supervisor_by_id(
    supervisors: list[dict], supervisor_id: int
) -> dict | None:
    """Вернуть руководителя по id или None."""
    for s in supervisors:
        if s["id"] == supervisor_id:
            return s
    return None


def get_supervisor_full_name(
    supervisors: list[dict], supervisor_id: int
) -> str:
    """Вернуть ФИО руководителя или заглушку."""
    supervisor = get_supervisor_by_id(supervisors, supervisor_id)
    return supervisor["full_name"] if supervisor else "—"


def is_topic_available(topic: dict) -> bool:
    """Проверить, свободна ли тема."""
    return topic["status"] == "свободна" and topic["student_id"] is None


def assign_topic_to_student(
    topics: list[dict], topic_id: int, student_id: int
) -> str:
    """Закрепить тему за студентом.

    Возвращает текстовое сообщение о результате.
    """
    for topic in topics:
        if topic["id"] == topic_id:
            if not is_topic_available(topic):
                return f"Тема «{topic['title']}» уже занята."
            topic["student_id"] = student_id
            topic["status"] = "закреплена"
            return f"Тема «{topic['title']}» закреплена за студентом."
    return f"Тема с id={topic_id} не найдена."


def unassign_topic(topics: list[dict], topic_id: int) -> str:
    """Освободить тему от студента."""
    for topic in topics:
        if topic["id"] == topic_id:
            if topic["status"] == "защищена":
                return "Нельзя освободить защищённую тему."
            topic["student_id"] = None
            topic["status"] = "свободна"
            return f"Тема «{topic['title']}» снова свободна."
    return f"Тема с id={topic_id} не найдена."