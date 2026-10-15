"""Представления (view-функции) приложения core."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from coursework.models import Student, Supervisor, Topic


def home(request: HttpRequest) -> HttpResponse:
    """Главная страница: витрина системы и общая статистика."""
    total_topics = Topic.objects.count()
    free_topics = Topic.objects.filter(status=Topic.STATUS_FREE).count()
    assigned_topics = Topic.objects.filter(status=Topic.STATUS_ASSIGNED).count()
    in_review_topics = Topic.objects.filter(status=Topic.STATUS_IN_REVIEW).count()
    defended_topics = Topic.objects.filter(status=Topic.STATUS_DEFENDED).count()
    total_students = Student.objects.count()
    total_supervisors = Supervisor.objects.count()

    recent_topics = Topic.objects.select_related("supervisor", "student").order_by("-created_at")[:6]

    context = {
        "title": "Главная — Система учёта курсовых работ",
        "total_topics": total_topics,
        "free_topics": free_topics,
        "assigned_topics": assigned_topics,
        "in_review_topics": in_review_topics,
        "defended_topics": defended_topics,
        "total_students": total_students,
        "total_supervisors": total_supervisors,
        "recent_topics": recent_topics,
    }
    return render(request, "core/home.html", context)


def about(request: HttpRequest) -> HttpResponse:
    """Страница «О проекте»: архитектура, предметная область и стек технологий."""
    context = {
        "title": "О проекте — Система учёта курсовых работ",
    }
    return render(request, "core/about.html", context)


def http_info(request: HttpRequest) -> HttpResponse:
    """Информационная страница об HTTP-протоколе и элементах запроса/ответа.

    Демонстрирует разбор входящего HTTP-запроса в Django и формат HTTP-ответа,
    выполняя требование практической работы №5.
    """
    interesting_headers = {
        "Host": request.META.get("HTTP_HOST", "—"),
        "User-Agent": request.META.get("HTTP_USER_AGENT", "—"),
        "Accept": request.META.get("HTTP_ACCEPT", "—"),
        "Accept-Language": request.META.get("HTTP_ACCEPT_LANGUAGE", "—"),
        "Accept-Encoding": request.META.get("HTTP_ACCEPT_ENCODING", "—"),
        "Connection": request.META.get("HTTP_CONNECTION", "—"),
    }

    context = {
        "title": "HTTP Протокол: Запросы и Ответы",
        "method": request.method,
        "path": request.path,
        "full_path": request.get_full_path(),
        "scheme": request.scheme,
        "is_secure": request.is_secure(),
        "headers": interesting_headers,
        "query_params": dict(request.GET),
    }
    return render(request, "core/http_info.html", context)
