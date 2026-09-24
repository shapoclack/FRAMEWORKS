

from datetime import date



student_name = "Иванов Иван Иванович"
student_group = "ПИ-21-1"
topic_title = "Разработка веб-приложения для учета курсовых работ"
supervisor_name = "Петрова Анна Сергеевна"
supervisor_degree = "к.т.н."
topic_status = "свободна"          # возможные: свободна, закреплена, на проверке, защищена
topic_deadline = date(2026, 12, 15)
is_available = True



def check_availability(is_available: bool) -> str:
    """Проверяет, доступна ли тема для закрепления."""
    if is_available:
        return "Тема доступна для закрепления."
    return "Тема уже закреплена за другим студентом."


def assign_topic(student: str, topic: str, available: bool) -> str:
    """Закрепляет тему за студентом, если она доступна."""
    if available:
        return f"Тема «{topic}» успешно закреплена за студентом {student}."
    return f"Невозможно закрепить тему «{topic}»: она недоступна."


def change_status(current_status: str, new_status: str) -> str:
    """Меняет статус темы с проверкой допустимых переходов."""
    allowed = "свободна,закреплена,на проверке,защищена"
    if new_status not in allowed:
        return f"Ошибка: статус «{new_status}» недопустим."
    if current_status == new_status:
        return f"Статус уже равен «{current_status}»."
    return f"Статус темы изменён: «{current_status}» → «{new_status}»."


def get_topic_info(title: str, supervisor: str, degree: str, deadline: date) -> str:
    """Формирует краткую информацию о теме."""
    return (
        f"Тема: {title}\n"
        f"Руководитель: {supervisor} ({degree})\n"
        f"Срок сдачи: {deadline.strftime('%d.%m.%Y')}"
    )



if __name__ == "__main__":
    print("=== Система учета тем курсовых работ ===")
    print(get_topic_info(topic_title, supervisor_name, supervisor_degree, topic_deadline))
    print()

    print(check_availability(is_available))
    print(assign_topic(student_name, topic_title, is_available))
    print()

    print(change_status(topic_status, "закреплена"))
    print(change_status("закреплена", "на проверке"))
    print(change_status("на проверке", "неизвестный статус"))