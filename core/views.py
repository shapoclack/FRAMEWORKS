"""Представления (view-функции) приложения core."""

import sqlite3
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from coursework.views import TopicItem
from db.database import DB_PATH, get_connection


def home(request: HttpRequest) -> HttpResponse:
    """Главная страница: витрина системы и общая статистика из SQLite."""
    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_topics,
            SUM(CASE WHEN status = 'свободна' THEN 1 ELSE 0 END) AS free_topics,
            SUM(CASE WHEN status = 'закреплена' THEN 1 ELSE 0 END) AS assigned_topics,
            SUM(CASE WHEN status = 'на проверке' THEN 1 ELSE 0 END) AS in_review_topics,
            SUM(CASE WHEN status = 'защищена' THEN 1 ELSE 0 END) AS defended_topics
        FROM topics;
    """).fetchone()

    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_supervisors = conn.execute("SELECT COUNT(*) FROM supervisors").fetchone()[0]

    recent_rows = conn.execute("""
        SELECT
            t.id,
            t.title,
            t.description,
            t.status,
            t.deadline,
            sv.id AS supervisor_id,
            sv.full_name AS supervisor_name,
            sv.degree AS supervisor_degree,
            sv.position AS supervisor_position,
            sv.email AS supervisor_email,
            s.id AS student_id,
            s.full_name AS student_name,
            s.group_name AS student_group,
            s.email AS student_email
        FROM topics t
        JOIN supervisors sv ON t.supervisor_id = sv.id
        LEFT JOIN students s ON t.student_id = s.id
        ORDER BY t.id DESC
        LIMIT 6;
    """).fetchall()
    conn.close()

    recent_topics = [TopicItem(r) for r in recent_rows]

    context = {
        "title": "Главная — Система учёта курсовых работ",
        "total_topics": summary["total_topics"] or 0,
        "free_topics": summary["free_topics"] or 0,
        "assigned_topics": summary["assigned_topics"] or 0,
        "in_review_topics": summary["in_review_topics"] or 0,
        "defended_topics": summary["defended_topics"] or 0,
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

    Демонстрирует разбор входящего HTTP-запроса в Django и формат HTTP-ответа.
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
