"""Функции работы с темами курсовых работ."""

from utils import next_id


def add_topic(
    topics: list[dict],
    title: str,
    description: str,
    supervisor_id: int,
) -> dict:
    """Добавить новую тему.

    Возвращает созданный словарь темы.
    """
    topic = {
        "id": next_id(topics),
        "title": title,
        "description": description,
        "supervisor_id": supervisor_id,
        "student_id": None,
        "status": "свободна",
    }
    topics.append(topic)
    return topic


def find_topic(topics: list[dict], query: str) -> list[dict]:
    """Найти темы по подстроке в названии (без учёта регистра)."""
    query_lower = query.lower()
    return [t for t in topics if query_lower in t["title"].lower()]


def filter_topics_by_status(topics: list[dict], status: str) -> list[dict]:
    """Отобрать темы по статусу.

    Использует генератор.
    """
    return [t for t in topics if t["status"] == status]


def filter_topics_by_supervisor(
    topics: list[dict], supervisor_id: int
) -> list[dict]:
    """Отобрать темы конкретного руководителя."""
    return [t for t in topics if t["supervisor_id"] == supervisor_id]


def sort_topics_by_title(topics: list[dict]) -> list[dict]:
    """Отсортировать темы по названию (lambda-функция как ключ)."""
    return sorted(topics, key=lambda t: t["title"].lower())


def change_topic_status(
    topics: list[dict], topic_id: int, new_status: str
) -> str:
    """Изменить статус темы с проверкой допустимых значений.

    Возвращает текстовое сообщение о результате.
    """
    allowed = {"свободна", "закреплена", "на проверке", "защищена"}
    if new_status not in allowed:
        return f"Ошибка: статус «{new_status}» недопустим."

    for topic in topics:
        if topic["id"] == topic_id:
            old_status = topic["status"]
            topic["status"] = new_status
            return f"Статус темы изменён: «{old_status}» → «{new_status}»."
    return f"Тема с id={topic_id} не найдена."


def get_topic_statistics(topics: list[dict]) -> dict[str, int]:
    """Вернуть статистику по статусам тем."""
    stats: dict[str, int] = {}
    for topic in topics:
        stats[topic["status"]] = stats.get(topic["status"], 0) + 1
    return stats