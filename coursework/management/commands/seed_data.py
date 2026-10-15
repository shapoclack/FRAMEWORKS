"""Команда наполнения базы данных начальными данными из ПР3."""

from datetime import date
from django.core.management.base import BaseCommand
from coursework.models import StatusHistory, Student, Supervisor, Topic


class Command(BaseCommand):
    help = "Наполняет базу данных демонстрационными данными из ПР3"

    def handle(self, *args, **options):
        self.stdout.write("Очистка существующих данных...")
        StatusHistory.objects.all().delete()
        Topic.objects.all().delete()
        Student.objects.all().delete()
        Supervisor.objects.all().delete()

        self.stdout.write("Создание студентов...")
        s1 = Student.objects.create(
            full_name="Иванов Иван Иванович",
            group_name="ПИ-21-1",
            direction="Программная инженерия",
            email="ivanov@example.com",
        )
        Student.objects.create(
            full_name="Петров Пётр Петрович",
            group_name="ПИ-21-1",
            direction="Программная инженерия",
            email="petrov@example.com",
        )
        Student.objects.create(
            full_name="Сидорова Анна Сергеевна",
            group_name="ПИ-21-2",
            direction="Прикладная информатика",
            email="sidorova@example.com",
        )

        self.stdout.write("Создание научных руководителей...")
        sup1 = Supervisor.objects.create(
            full_name="Петрова Анна Сергеевна",
            degree="к.т.н.",
            position="доцент",
            email="petrova@example.com",
            max_topics=5,
        )
        sup2 = Supervisor.objects.create(
            full_name="Сидоров Пётр Алексеевич",
            degree="д.т.н.",
            position="профессор",
            email="sidorov@example.com",
            max_topics=3,
        )
        sup3 = Supervisor.objects.create(
            full_name="Кузнецов Дмитрий Игоревич",
            degree="к.ф.-м.н.",
            position="ст. преподаватель",
            email="kuznetsov@example.com",
            max_topics=7,
        )

        self.stdout.write("Создание тем курсовых работ...")
        Topic.objects.create(
            title="Разработка веб-приложения для учёта курсовых работ",
            description="Полнофункциональное веб-приложение на Django c базой данных, аутентификацией и REST API.",
            supervisor=sup1,
            student=None,
            status=Topic.STATUS_FREE,
            deadline=date(2026, 12, 15),
        )

        Topic.objects.create(
            title="Анализ алгоритмов машинного обучения на открытых данных",
            description=(
                "Сравнение точности и производительности классических моделей ML "
                "и нейросетей на датасетах Kaggle."
            ),
            supervisor=sup2,
            student=None,
            status=Topic.STATUS_FREE,
            deadline=date(2026, 12, 20),
        )

        Topic.objects.create(
            title="Оптимизация SQL-запросов в высоконагруженных системах",
            description="Исследование планов выполнения EXPLAIN ANALYZE, построение индексов и методов денормализации.",
            supervisor=sup2,
            student=None,
            status=Topic.STATUS_FREE,
            deadline=date(2026, 12, 10),
        )

        t4 = Topic.objects.create(
            title="Разработка Telegram-бота для учёта студенческих заявок",
            description="Асинхронный бот на Python (aiogram) для оперативного оповещения студентов и кафедры.",
            supervisor=sup3,
            student=s1,
            status=Topic.STATUS_ASSIGNED,
            deadline=date(2026, 12, 25),
        )

        self.stdout.write("Создание истории статусов...")
        StatusHistory.objects.create(
            topic=t4,
            old_status=Topic.STATUS_FREE,
            new_status=Topic.STATUS_ASSIGNED,
            changed_by="Методист кафедры",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно создано: студентов={Student.objects.count()}, "
                f"руководителей={Supervisor.objects.count()}, "
                f"тем={Topic.objects.count()}."
            )
        )
