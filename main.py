

from topics import (
    add_topic,
    change_topic_status,
    filter_topics_by_status,
    find_topic,
    get_topic_statistics,
    sort_topics_by_title,
)
from students import (
    add_student,
    find_student,
    get_student_by_id,
)
from supervisors import (
    add_supervisor,
    assign_topic_to_student,
    get_supervisor_by_id,
    get_supervisor_full_name,
    unassign_topic,
)
from storage import (
    load_students,
    load_supervisors,
    load_topics,
    save_students,
    save_supervisors,
    save_topics,
)
from utils import input_int, input_str


# ---------- Функции вывода ----------

def show_topics(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Вывести список тем в табличном виде."""
    if not topics:
        print("Тем пока нет.")
        return

    print(f"{'ID':<4}{'Название':<48}{'Руководитель':<26}{'Статус':<15}")
    print("-" * 95)
    for topic in topics:
        supervisor_name = get_supervisor_full_name(
            supervisors, topic["supervisor_id"]
        )
        title = topic["title"]
        if len(title) > 45:
            title = title[:42] + "..."
        print(
            f"{topic['id']:<4}{title:<48}"
            f"{supervisor_name:<26}{topic['status']:<15}"
        )


def show_students(students: list[dict]) -> None:
    """Вывести список студентов."""
    if not students:
        print("Студентов пока нет.")
        return

    print(f"{'ID':<4}{'ФИО':<32}{'Группа':<14}{'Направление':<28}")
    print("-" * 80)
    for student in students:
        print(
            f"{student['id']:<4}{student['full_name']:<32}"
            f"{student['group']:<14}{student['direction']:<28}"
        )


def show_supervisors(supervisors: list[dict]) -> None:
    """Вывести список научных руководителей."""
    if not supervisors:
        print("Руководителей пока нет.")
        return

    print(f"{'ID':<4}{'ФИО':<32}{'Степень':<12}{'Должность':<20}")
    print("-" * 70)
    for supervisor in supervisors:
        print(
            f"{supervisor['id']:<4}{supervisor['full_name']:<32}"
            f"{supervisor['degree']:<12}{supervisor['position']:<20}"
        )


def show_statistics(topics: list[dict]) -> None:
    """Вывести статистику по статусам тем."""
    stats = get_topic_statistics(topics)
    if not stats:
        print("Нет данных для статистики.")
        return

    print("Статистика по статусам тем:")
    for status, count in stats.items():
        print(f"  {status:<15}: {count}")
    print(f"  Всего тем      : {len(topics)}")


def show_my_topics(
    topics: list[dict],
    student_id: int,
    supervisors: list[dict],
) -> None:
    """Показать темы, закреплённые за конкретным студентом."""
    my_topics = [t for t in topics if t["student_id"] == student_id]
    if not my_topics:
        print("За вами не закреплено ни одной темы.")
        return

    print("Ваши темы:")
    for topic in my_topics:
        supervisor_name = get_supervisor_full_name(
            supervisors, topic["supervisor_id"]
        )
        print(
            f"  [{topic['id']}] {topic['title']} — "
            f"{supervisor_name} ({topic['status']})"
        )


# ---------- Функции меню ----------

def handle_show_all_topics(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Пункт 1: показать все темы."""
    show_topics(topics, supervisors)


def handle_find_topic(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Пункт 2: поиск темы по подстроке."""
    query = input_str("Введите подстроку для поиска: ")
    found = find_topic(topics, query)
    if not found:
        print(f"Темы по запросу «{query}» не найдены.")
        return
    show_topics(found, supervisors)


def handle_free_topics(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Пункт 3: показать свободные темы."""
    free = filter_topics_by_status(topics, "свободна")
    if not free:
        print("Свободных тем нет.")
        return
    show_topics(free, supervisors)


def handle_sorted_topics(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Пункт 4: сортировка тем по названию."""
    sorted_topics = sort_topics_by_title(topics)
    show_topics(sorted_topics, supervisors)


def handle_add_topic(topics: list[dict]) -> None:
    """Пункт 5: добавить новую тему."""
    title = input_str("Название темы: ")
    description = input_str("Описание темы: ")
    supervisor_id = input_int("ID руководителя: ")

    topic = add_topic(topics, title, description, supervisor_id)
    print(f"Тема добавлена с id={topic['id']}.")


def handle_assign_topic(topics: list[dict]) -> None:
    """Пункт 6: закрепить тему за студентом."""
    topic_id = input_int("ID темы: ")
    student_id = input_int("ID студента: ")
    result = assign_topic_to_student(topics, topic_id, student_id)
    print(result)


def handle_unassign_topic(topics: list[dict]) -> None:
    """Пункт 7: освободить тему."""
    topic_id = input_int("ID темы: ")
    result = unassign_topic(topics, topic_id)
    print(result)


def handle_change_status(topics: list[dict]) -> None:
    """Пункт 8: изменить статус темы."""
    topic_id = input_int("ID темы: ")
    print("Допустимые статусы: свободна, закреплена, на проверке, защищена.")
    new_status = input_str("Новый статус: ")
    result = change_topic_status(topics, topic_id, new_status)
    print(result)


def handle_add_student(students: list[dict]) -> None:
    """Пункт 10: добавить студента."""
    full_name = input_str("ФИО студента: ")
    group = input_str("Группа: ")
    direction = input_str("Направление: ")
    student = add_student(students, full_name, group, direction)
    print(f"Студент добавлен с id={student['id']}.")


def handle_add_supervisor(supervisors: list[dict]) -> None:
    """Пункт 11: добавить руководителя."""
    full_name = input_str("ФИО руководителя: ")
    degree = input_str("Учёная степень: ")
    position = input_str("Должность: ")
    supervisor = add_supervisor(supervisors, full_name, degree, position)
    print(f"Руководитель добавлен с id={supervisor['id']}.")


def handle_find_student(students: list[dict]) -> None:
    """Пункт 12: найти студента."""
    query = input_str("Подстрока (ФИО или группа): ")
    found = find_student(students, query)
    if not found:
        print(f"Студенты по запросу «{query}» не найдены.")
        return
    show_students(found)


def handle_show_student_topics(
    topics: list[dict],
    supervisors: list[dict],
) -> None:
    """Пункт 13: показать темы конкретного студента."""
    student_id = input_int("ID студента: ")
    show_my_topics(topics, student_id, supervisors)


# ---------- Основной цикл ----------

def print_menu() -> None:
    """Вывести главное меню приложения."""
    print()
    print("=== Система учета тем курсовых работ ===")
    print(" 1. Показать все темы")
    print(" 2. Найти тему по названию")
    print(" 3. Показать свободные темы")
    print(" 4. Отсортировать темы по названию")
    print(" 5. Добавить тему")
    print(" 6. Закрепить тему за студентом")
    print(" 7. Освободить тему")
    print(" 8. Изменить статус темы")
    print(" 9. Показать статистику")
    print("10. Добавить студента")
    print("11. Добавить руководителя")
    print("12. Найти студента")
    print("13. Показать темы студента")
    print("14. Показать всех студентов")
    print("15. Показать всех руководителей")
    print(" 0. Выход")


def main() -> None:
    """Точка входа в приложение."""
    topics = load_topics()
    students = load_students()
    supervisors = load_supervisors()

    print("Данные загружены:")
    print(f"  тем — {len(topics)}, студентов — {len(students)}, "
          f"руководителей — {len(supervisors)}")

    while True:
        print_menu()
        choice = input_int("Выберите действие: ")

        if choice == 0:
            save_topics(topics)
            save_students(students)
            save_supervisors(supervisors)
            print("Данные сохранены. До свидания!")
            break

        elif choice == 1:
            handle_show_all_topics(topics, supervisors)

        elif choice == 2:
            handle_find_topic(topics, supervisors)

        elif choice == 3:
            handle_free_topics(topics, supervisors)

        elif choice == 4:
            handle_sorted_topics(topics, supervisors)

        elif choice == 5:
            handle_add_topic(topics)

        elif choice == 6:
            handle_assign_topic(topics)

        elif choice == 7:
            handle_unassign_topic(topics)

        elif choice == 8:
            handle_change_status(topics)

        elif choice == 9:
            show_statistics(topics)

        elif choice == 10:
            handle_add_student(students)

        elif choice == 11:
            handle_add_supervisor(supervisors)

        elif choice == 12:
            handle_find_student(students)

        elif choice == 13:
            handle_show_student_topics(topics, supervisors)

        elif choice == 14:
            show_students(students)

        elif choice == 15:
            show_supervisors(supervisors)

        else:
            print("Неизвестное действие. Попробуйте снова.")


if __name__ == "__main__":
    main()