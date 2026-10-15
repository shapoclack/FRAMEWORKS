"""Тесты функций работы с темами."""

from topics import (
    add_topic,
    change_topic_status,
    filter_topics_by_status,
    find_topic,
    get_topic_statistics,
    sort_topics_by_title,
)


def test_add_topic():
    topics = []
    add_topic(topics, "Тема А", "Описание", 1)
    assert len(topics) == 1
    assert topics[0]["title"] == "Тема А"
    assert topics[0]["status"] == "свободна"


def test_find_topic_case_insensitive():
    topics = []
    add_topic(topics, "Разработка Django-приложения", "…", 1)
    add_topic(topics, "Анализ данных", "…", 1)
    found = find_topic(topics, "django")
    assert len(found) == 1
    assert "Django" in found[0]["title"]


def test_filter_topics_by_status():
    topics = []
    add_topic(topics, "Т1", "…", 1)
    add_topic(topics, "Т2", "…", 1)
    topics[1]["status"] = "закреплена"
    free = filter_topics_by_status(topics, "свободна")
    assert len(free) == 1
    assert free[0]["title"] == "Т1"


def test_sort_topics_by_title():
    topics = []
    add_topic(topics, "Яблоко", "…", 1)
    add_topic(topics, "Апельсин", "…", 1)
    sorted_topics = sort_topics_by_title(topics)
    assert sorted_topics[0]["title"] == "Апельсин"


def test_change_topic_status():
    topics = []
    add_topic(topics, "Тема X", "…", 1)
    result = change_topic_status(topics, topics[0]["id"], "закреплена")
    assert topics[0]["status"] == "закреплена"
    assert "изменён" in result


def test_change_topic_status_invalid():
    topics = []
    add_topic(topics, "Тема X", "…", 1)
    result = change_topic_status(topics, topics[0]["id"], "некорректный")
    assert "Ошибка" in result


def test_get_topic_statistics():
    topics = []
    add_topic(topics, "Т1", "…", 1)
    add_topic(topics, "Т2", "…", 1)
    topics[1]["status"] = "закреплена"
    stats = get_topic_statistics(topics)
    assert stats["свободна"] == 1
    assert stats["закреплена"] == 1