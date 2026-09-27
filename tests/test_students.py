"""Тесты функций работы со студентами."""

from students import add_student, find_student, get_student_by_id


def test_add_student():
    students = []
    add_student(students, "Иванов И. И.", "ПИ-21-1", "Программная инженерия")
    assert len(students) == 1
    assert students[0]["group"] == "ПИ-21-1"


def test_find_student_by_group():
    students = []
    add_student(students, "Иванов И. И.", "ПИ-21-1", "ПИ")
    add_student(students, "Петров П. П.", "ПИ-22-2", "ПИ")
    found = find_student(students, "21")
    assert len(found) == 1

def test_get_student_by_id():
    students = []
    add_student(students, "Иванов И. И.", "ПИ-21-1", "ПИ")

    student = get_student_by_id(students, 1)
    assert student is not None
    assert student["full_name"] == "Иванов И. И."

    assert get_student_by_id(students, 999) is None