"""Модели предметной области системы учета тем курсовых работ.

Сущности полностью соответствуют спроектированной схеме базы данных (ПР3):
- Студенты (Student)
- Научные руководители (Supervisor)
- Темы курсовых работ (Topic)
- История изменения статусов тем (StatusHistory)
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
    """Студент, выполняющий курсовую работу."""

    full_name = models.CharField(
        "ФИО студента",
        max_length=150,
        help_text="Фамилия, имя и отчество студента",
    )
    group_name = models.CharField(
        "Учебная группа",
        max_length=20,
        help_text="Например: ПИ-21-1",
    )
    direction = models.CharField(
        "Направление подготовки",
        max_length=200,
        blank=True,
        default="",
        help_text="Например: Программная инженерия",
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=100,
        unique=True,
    )
    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.group_name})"


class Supervisor(models.Model):
    """Научный руководитель курсовых работ."""

    full_name = models.CharField(
        "ФИО руководителя",
        max_length=150,
        help_text="Фамилия, имя и отчество преподавателя",
    )
    degree = models.CharField(
        "Учёная степень",
        max_length=50,
        blank=True,
        default="",
        help_text="Например: к.т.н., д.т.н.",
    )
    position = models.CharField(
        "Должность",
        max_length=100,
        blank=True,
        default="",
        help_text="Например: доцент, профессор",
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=100,
        unique=True,
    )
    max_topics = models.PositiveSmallIntegerField(
        "Максимум тем",
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Лимит тем, которые может вести руководитель (от 1 до 20)",
    )
    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Научный руководитель"
        verbose_name_plural = "Научные руководители"
        ordering = ["full_name"]

    def __str__(self) -> str:
        degree_part = f" ({self.degree})" if self.degree else ""
        return f"{self.full_name}{degree_part}"

    @property
    def active_topics_count(self) -> int:
        """Количество активных тем (закреплена, на проверке, защищена)."""
        return self.topics.exclude(status="свободна").count()

    @property
    def available_slots(self) -> int:
        """Количество оставшихся доступных мест для ведения тем."""
        return max(0, self.max_topics - self.active_topics_count)


class Topic(models.Model):
    """Тема курсовой работы."""

    STATUS_FREE = "свободна"
    STATUS_ASSIGNED = "закреплена"
    STATUS_IN_REVIEW = "на проверке"
    STATUS_DEFENDED = "защищена"

    STATUS_CHOICES = [
        (STATUS_FREE, "Свободна"),
        (STATUS_ASSIGNED, "Закреплена"),
        (STATUS_IN_REVIEW, "На проверке"),
        (STATUS_DEFENDED, "Защищена"),
    ]

    title = models.CharField(
        "Название темы",
        max_length=300,
        help_text="Формулировка темы курсовой работы",
    )
    description = models.TextField(
        "Описание темы",
        blank=True,
        default="",
        help_text="Аннотация, стек технологий и задачи работы",
    )
    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.RESTRICT,
        related_name="topics",
        verbose_name="Научный руководитель",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topics",
        verbose_name="Студент",
    )
    status = models.CharField(
        "Статус темы",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_FREE,
    )
    deadline = models.DateField(
        "Срок сдачи",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Тема курсовой работы"
        verbose_name_plural = "Темы курсовых работ"
        ordering = ["-created_at", "title"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_available(self) -> bool:
        """Доступна ли тема для закрепления."""
        return self.status == self.STATUS_FREE and self.student is None

    @property
    def status_badge_class(self) -> str:
        """CSS-класс Bootstrap для красивого отображения статуса."""
        mapping = {
            self.STATUS_FREE: "success",
            self.STATUS_ASSIGNED: "primary",
            self.STATUS_IN_REVIEW: "warning text-dark",
            self.STATUS_DEFENDED: "secondary",
        }
        return mapping.get(self.status, "info")


class StatusHistory(models.Model):
    """Аудит изменения статусов тем курсовых работ."""

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Тема курсовой работы",
    )
    old_status = models.CharField(
        "Предыдущий статус",
        max_length=20,
    )
    new_status = models.CharField(
        "Новый статус",
        max_length=20,
    )
    changed_at = models.DateTimeField(
        "Дата изменения",
        auto_now_add=True,
    )
    changed_by = models.CharField(
        "Кем изменено",
        max_length=100,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = "История статуса"
        verbose_name_plural = "История статусов"
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return f"{self.topic.title}: {self.old_status} → {self.new_status}"
