"""Тесты функций работы с руководителями и закрепления тем."""

from topics import add_topic
from supervisors import (
    add_supervisor,
    assign_topic_to_student,
    get_supervisor_full_name,
    is_topic_available,
    unassign_topic,
)


def test_add_supervisor():
    supervisors = []
    add_supervisor(supervisors, "Петрова А. С.", "к.т.н.", "доцент")
    assert len(supervisors) == 1


def test_is_topic_available_true():
    topics = []
    add_topic(topics, "Тема", "…", 1)
    assert is_topic_available(topics[0])


def test_assign_topic_to_student():
    topics = []
    add_topic(topics, "Тема", "…", 1)
    result = assign_topic_to_student(topics, 1, 100)
    assert topics[0]["student_id"] == 100
    assert topics[0]["status"] == "закреплена"
    assert "закреплена" in result


def test_assign_taken_topic():
    topics = []
    add_topic(topics, "Тема", "…", 1)
    assign_topic_to_student(topics, 1, 100)
    result = assign_topic_to_student(topics, 1, 200)
    assert "занята" in result


def test_unassign_topic():
    topics = []
    add_topic(topics, "Тема", "…", 1)
    assign_topic_to_student(topics, 1, 100)
    result = unassign_topic(topics, 1)
    assert topics[0]["student_id"] is None
    assert topics[0]["status"] == "свободна"
    assert "свободна" in result


def test_get_supervisor_full_name():
    supervisors = []
    add_supervisor(supervisors, "Петрова А. С.", "к.т.н.", "доцент")
    assert get_supervisor_full_name(supervisors, 1) == "Петрова А. С."
    assert get_supervisor_full_name(supervisors, 999) == "—"