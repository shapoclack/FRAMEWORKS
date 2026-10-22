"""Автоматизированные тесты моделей и представлений Django."""

from datetime import date
from django.test import Client, TestCase
from django.urls import reverse
from .models import StatusHistory, Student, Supervisor, Topic


class CourseworkModelsTestCase(TestCase):
    """Тестирование моделей предметной области."""

    def setUp(self):
        self.student = Student.objects.create(
            full_name="Иванов Иван Иванович",
            group_name="ПИ-21-1",
            direction="Программная инженерия",
            email="ivanov@example.com",
        )
        self.supervisor = Supervisor.objects.create(
            full_name="Петрова Анна Сергеевна",
            degree="к.т.н.",
            position="доцент",
            email="petrova@example.com",
            max_topics=5,
        )
        self.topic = Topic.objects.create(
            title="Разработка веб-приложения на Django",
            description="Описание темы",
            supervisor=self.supervisor,
            status=Topic.STATUS_FREE,
            deadline=date(2026, 12, 15),
        )

    def test_student_str(self):
        self.assertEqual(str(self.student), "Иванов Иван Иванович (ПИ-21-1)")

    def test_supervisor_str_and_slots(self):
        self.assertIn("Петрова Анна Сергеевна", str(self.supervisor))
        self.assertEqual(self.supervisor.active_topics_count, 0)
        self.assertEqual(self.supervisor.available_slots, 5)

    def test_topic_str_and_availability(self):
        self.assertEqual(str(self.topic), "Разработка веб-приложения на Django")
        self.assertTrue(self.topic.is_available)

    def test_topic_assignment(self):
        self.topic.student = self.student
        self.topic.status = Topic.STATUS_ASSIGNED
        self.topic.save()

        self.assertFalse(self.topic.is_available)
        self.assertEqual(self.supervisor.active_topics_count, 1)
        self.assertEqual(self.supervisor.available_slots, 4)

    def test_status_history(self):
        history = StatusHistory.objects.create(
            topic=self.topic,
            old_status=Topic.STATUS_FREE,
            new_status=Topic.STATUS_ASSIGNED,
            changed_by="Методист",
        )
        self.assertIn("Разработка веб-приложения", str(history))


class CourseworkViewsTestCase(TestCase):
    """Тестирование view-функций и HTTP-ответов со слоем SQLite (ПР7)."""

    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertIn("total_topics", response.context)
        self.assertGreaterEqual(response.context["total_topics"], 1)

    def test_about_view(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
        self.assertContains(response, "О проекте")

    def test_http_info_view(self):
        response = self.client.get(reverse("core:http_info"), {"test": "val"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/http_info.html")
        self.assertEqual(response.context["method"], "GET")
        self.assertContains(response, "HTTP/1.1 200 OK")

    def test_topic_list_view(self):
        response = self.client.get(reverse("coursework:topic_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/topic_list.html")
        self.assertContains(response, "Разработка веб-приложения")

    def test_topic_list_search_and_filter(self):
        # Поиск по подстроке
        response = self.client.get(reverse("coursework:topic_list"), {"q": "Telegram"})
        self.assertEqual(len(response.context["topics"]), 1)

        # Поиск несуществующего
        response_empty = self.client.get(reverse("coursework:topic_list"), {"q": "несуществующая тема 123"})
        self.assertEqual(len(response_empty.context["topics"]), 0)

        # Фильтрация по статусу «защищена»
        response_defended = self.client.get(reverse("coursework:topic_list"), {"status": "защищена"})
        self.assertEqual(len(response_defended.context["topics"]), 1)

        # Фильтрация по статусу «свободна»
        response_free = self.client.get(reverse("coursework:topic_list"), {"status": "свободна"})
        self.assertEqual(len(response_free.context["topics"]), 4)

    def test_topic_detail_view(self):
        response = self.client.get(reverse("coursework:topic_detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/topic_detail.html")
        self.assertContains(response, "Разработка веб-приложения")
        self.assertContains(response, "Петрова Анна Сергеевна")

    def test_topic_detail_404(self):
        response = self.client.get(reverse("coursework:topic_detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)

    def test_student_list_view(self):
        response = self.client.get(reverse("coursework:student_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/student_list.html")
        self.assertContains(response, "Иванов Иван Иванович")

    def test_supervisor_list_view(self):
        response = self.client.get(reverse("coursework:supervisor_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/supervisor_list.html")
        self.assertContains(response, "Петрова Анна Сергеевна")

    def test_active_topics_view(self):
        response = self.client.get(reverse("coursework:active_topics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/active_topics.html")
        self.assertContains(response, "Разработка Telegram-бота")

    def test_available_topics_view(self):
        response = self.client.get(reverse("coursework:available"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/available.html")
        self.assertContains(response, "Анализ алгоритмов машинного обучения")

    def test_available_topics_filter_by_date(self):
        response = self.client.get(reverse("coursework:available"), {"date": "2026-12-15"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/available.html")
        self.assertEqual(len(response.context["topics"]), 2)

    def test_statistics_view(self):
        response = self.client.get(reverse("coursework:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coursework/statistics.html")
        self.assertIn("summary", response.context)
        self.assertIn("supervisor_stats", response.context)
        self.assertIn("status_stats", response.context)
        self.assertIn("busy_supervisors", response.context)
        self.assertIn("group_stats", response.context)
