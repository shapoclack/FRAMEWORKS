"""Представления (view-функции) приложения coursework."""

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Student, Supervisor, Topic


def topic_list(request: HttpRequest) -> HttpResponse:
    """Список тем курсовых работ с возможностью поиска и фильтрации."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    supervisor_filter = request.GET.get("supervisor", "").strip()

    topics = Topic.objects.select_related("supervisor", "student").all()

    if query:
        topics = topics.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        topics = topics.filter(status=status_filter)

    if supervisor_filter:
        topics = topics.filter(supervisor_id=supervisor_filter)

    supervisors = Supervisor.objects.all()

    context = {
        "title": "Каталог тем курсовых работ",
        "topics": topics,
        "query": query,
        "current_status": status_filter,
        "current_supervisor": supervisor_filter,
        "statuses": Topic.STATUS_CHOICES,
        "supervisors": supervisors,
        "total_found": topics.count(),
    }
    return render(request, "coursework/topic_list.html", context)


def topic_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Детальный просмотр темы курсовой работы и истории её статусов."""
    topic = get_object_or_404(
        Topic.objects.select_related("supervisor", "student").prefetch_related("status_history"),
        pk=pk,
    )
    context = {
        "title": f"Тема: {topic.title}",
        "topic": topic,
    }
    return render(request, "coursework/topic_detail.html", context)


def student_list(request: HttpRequest) -> HttpResponse:
    """Список студентов с информацией об их курсовых работах."""
    query = request.GET.get("q", "").strip()
    students = Student.objects.prefetch_related("topics").all()

    if query:
        students = students.filter(
            Q(full_name__icontains=query)
            | Q(group_name__icontains=query)
            | Q(direction__icontains=query)
        )

    context = {
        "title": "Список студентов",
        "students": students,
        "query": query,
        "total_count": students.count(),
    }
    return render(request, "coursework/student_list.html", context)


def supervisor_list(request: HttpRequest) -> HttpResponse:
    """Список научных руководителей с индикацией текущей нагрузки."""
    query = request.GET.get("q", "").strip()
    supervisors = Supervisor.objects.prefetch_related("topics").all()

    if query:
        supervisors = supervisors.filter(
            Q(full_name__icontains=query)
            | Q(degree__icontains=query)
            | Q(position__icontains=query)
        )

    context = {
        "title": "Научные руководители",
        "supervisors": supervisors,
        "query": query,
        "total_count": supervisors.count(),
    }
    return render(request, "coursework/supervisor_list.html", context)
