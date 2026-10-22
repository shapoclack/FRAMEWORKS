"""Представления (view-функции) приложения coursework на основе SQLite (ПР7).

Все данные извлекаются напрямую из СУБД SQLite через стандартную библиотеку sqlite3
с использованием sqlite3.Row и параметризованных запросов без подстановки строк.
"""

import sqlite3
from typing import Any
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from db.database import DB_PATH, get_connection

STATUS_CHOICES = [
    ("свободна", "Свободна"),
    ("закреплена", "Закреплена"),
    ("на проверке", "На проверке"),
    ("защищена", "Защищена"),
]


class TopicItem:
    """Обёртка над строкой таблицы topics для удобного использования в шаблонах."""

    def __init__(self, row: Any):
        self._row = row
        self.id = row["id"]
        self.title = row["title"]
        self.description = row["description"] or ""
        self.status = row["status"]
        self.deadline = row["deadline"] or ""
        self.created_at = row["created_at"] if "created_at" in row.keys() else ""
        self.supervisor_id = row["supervisor_id"]
        self.supervisor_name = row["supervisor_name"]
        self.supervisor_degree = row["supervisor_degree"] if "supervisor_degree" in row.keys() else ""
        self.supervisor_position = row["supervisor_position"] if "supervisor_position" in row.keys() else ""
        self.supervisor_email = row["supervisor_email"] if "supervisor_email" in row.keys() else ""
        self.student_id = row["student_id"] if "student_id" in row.keys() else None
        self.student_name = row["student_name"] if "student_name" in row.keys() else ""
        self.student_group = row["student_group"] if "student_group" in row.keys() else ""
        self.student_email = row["student_email"] if "student_email" in row.keys() else ""

    @property
    def supervisor(self):
        if not self.supervisor_name:
            return None
        return {
            "id": self.supervisor_id,
            "full_name": self.supervisor_name,
            "degree": self.supervisor_degree,
            "position": self.supervisor_position,
            "email": self.supervisor_email,
        }

    @property
    def student(self):
        if not self.student_name:
            return None
        return {
            "id": self.student_id,
            "full_name": self.student_name,
            "group_name": self.student_group,
            "email": self.student_email,
        }

    @property
    def status_badge_class(self) -> str:
        mapping = {
            "свободна": "success",
            "закреплена": "primary",
            "на проверке": "warning text-dark",
            "защищена": "secondary",
        }
        return mapping.get(self.status, "info")

    @property
    def get_status_display(self) -> str:
        return self.status

    @property
    def is_available(self) -> bool:
        return self.status == "свободна" and not self.student_id

    def __getitem__(self, key: str) -> Any:
        return self._row[key]


class StudentItem:
    """Обёртка над строкой таблицы students."""

    def __init__(self, row: Any, topics: list | None = None):
        self._row = row
        self.id = row["id"]
        self.full_name = row["full_name"]
        self.group_name = row["group_name"]
        self.direction = row["direction"] or ""
        self.email = row["email"]
        self._topics = topics or []

    @property
    def topics(self):
        class TopicManager:
            def __init__(self, items):
                self._items = items

            def all(self):
                return self._items

            def count(self):
                return len(self._items)

            def __iter__(self):
                return iter(self._items)

        return TopicManager(self._topics)

    def __getitem__(self, key: str) -> Any:
        return self._row[key]


class SupervisorItem:
    """Обёртка над строкой таблицы supervisors."""

    def __init__(self, row: Any, topics_count: int = 0, topics: list | None = None):
        self._row = row
        self.id = row["id"]
        self.full_name = row["full_name"]
        self.degree = row["degree"] or ""
        self.position = row["position"] or ""
        self.email = row["email"]
        self.max_topics = row["max_topics"]
        self.topics_count = topics_count
        self._topics = topics or []

    @property
    def active_topics_count(self) -> int:
        return self.topics_count

    @property
    def available_slots(self) -> int:
        return max(0, self.max_topics - self.topics_count)

    @property
    def workload_percentage(self) -> int:
        if self.max_topics <= 0:
            return 0
        return min(100, int((self.topics_count / self.max_topics) * 100))

    @property
    def workload_bar_class(self) -> str:
        if self.workload_percentage >= 100:
            return "danger"
        if self.workload_percentage >= 70:
            return "warning"
        return "success"

    @property
    def topics(self):
        class TopicManager:
            def __init__(self, items):
                self._items = items

            def all(self):
                return self._items

            def count(self):
                return len(self._items)

            def __iter__(self):
                return iter(self._items)

        return TopicManager(self._topics)

    def __getitem__(self, key: str) -> Any:
        return self._row[key]


def topic_list(request: HttpRequest) -> HttpResponse:
    """Каталог всех тем курсовых работ с возможностью фильтрации и поиска (SQLite)."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    supervisor_filter = request.GET.get("supervisor", "").strip()

    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    sql = """
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
        WHERE (? = '' OR t.title LIKE ? OR t.description LIKE ?)
          AND (? = '' OR t.status = ?)
          AND (? = '' OR t.supervisor_id = ?)
        ORDER BY t.title ASC;
    """
    like_q = f"%{query}%"
    params = [
        query,
        like_q,
        like_q,
        status_filter,
        status_filter,
        supervisor_filter,
        supervisor_filter,
    ]
    rows = conn.execute(sql, params).fetchall()

    supervisors_rows = conn.execute(
        "SELECT id, full_name, degree FROM supervisors ORDER BY full_name ASC"
    ).fetchall()
    conn.close()

    topics = [TopicItem(r) for r in rows]

    context = {
        "title": "Каталог тем курсовых работ",
        "topics": topics,
        "query": query,
        "current_status": status_filter,
        "current_supervisor": supervisor_filter,
        "statuses": STATUS_CHOICES,
        "supervisors": supervisors_rows,
        "total_found": len(topics),
    }
    return render(request, "coursework/topic_list.html", context)


def topic_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Детальная карточка темы, участники и история аудита статусов (SQLite)."""
    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            t.id,
            t.title,
            t.description,
            t.status,
            t.deadline,
            t.created_at,
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
        WHERE t.id = ?;
    """
    row = conn.execute(sql, (pk,)).fetchone()
    if not row:
        conn.close()
        raise Http404("Тема курсовой работы не найдена")

    history_rows = conn.execute(
        """
        SELECT old_status, new_status, changed_at, changed_by
        FROM status_history
        WHERE topic_id = ?
        ORDER BY changed_at ASC;
    """,
        (pk,),
    ).fetchall()
    conn.close()

    topic = TopicItem(row)
    topic.status_history = type(
        "HistoryManager",
        (),
        {
            "all": lambda self: history_rows,
        },
    )()

    context = {
        "title": f"Тема: {topic.title}",
        "topic": topic,
    }
    return render(request, "coursework/topic_detail.html", context)


def active_topics(request: HttpRequest) -> HttpResponse:
    """Отображение активных тем в работе (JOIN topics, supervisors, students)."""
    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            t.id,
            t.title,
            t.description,
            t.status,
            t.deadline,
            sv.full_name AS supervisor_name,
            sv.degree AS supervisor_degree,
            sv.email AS supervisor_email,
            s.full_name AS student_name,
            s.group_name AS student_group,
            s.email AS student_email
        FROM topics t
        JOIN supervisors sv ON t.supervisor_id = sv.id
        JOIN students s ON t.student_id = s.id
        WHERE t.status IN ('закреплена', 'на проверке')
        ORDER BY t.deadline ASC;
    """
    rows = conn.execute(sql).fetchall()
    conn.close()

    return render(
        request,
        "coursework/active_topics.html",
        {
            "title": "Активные темы в работе",
            "topics": rows,
        },
    )


def available_topics(request: HttpRequest) -> HttpResponse:
    """Поиск свободных тем курсовых работ по параметрам (параметризованный SQL)."""
    booking_date = request.GET.get("date", "").strip()
    query = request.GET.get("q", "").strip()

    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Запрос с подзапросом NOT IN для исключения занятых тем
    sql = """
        SELECT
            t.id,
            t.title,
            t.description,
            t.status,
            t.deadline,
            sv.full_name AS supervisor_name,
            sv.degree AS supervisor_degree
        FROM topics t
        JOIN supervisors sv ON t.supervisor_id = sv.id
        WHERE t.id NOT IN (
            SELECT id
            FROM topics
            WHERE student_id IS NOT NULL OR status != 'свободна'
        )
        AND (? = '' OR t.deadline <= ?)
        AND (? = '' OR t.title LIKE ? OR t.description LIKE ?)
        ORDER BY t.title ASC;
    """
    like_q = f"%{query}%"
    params = [booking_date, booking_date, query, like_q, like_q]
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return render(
        request,
        "coursework/available.html",
        {
            "title": "Поиск свободных тем",
            "topics": rows,
            "booking_date": booking_date,
            "query": query,
        },
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Страница статистики и аналитики курсовых работ (GROUP BY, HAVING, агрегаты)."""
    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1. Агрегатный запрос: общие сводные показатели
    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_topics,
            SUM(CASE WHEN status = 'свободна' THEN 1 ELSE 0 END) AS free_topics,
            SUM(CASE WHEN status IN ('закреплена', 'на проверке') THEN 1 ELSE 0 END) AS active_topics,
            SUM(CASE WHEN status = 'защищена' THEN 1 ELSE 0 END) AS defended_topics
        FROM topics;
    """).fetchone()

    # 2. Нагрузка руководителей (LEFT JOIN + GROUP BY)
    supervisor_stats = conn.execute("""
        SELECT
            sv.id,
            sv.full_name AS supervisor_name,
            sv.degree,
            sv.position,
            sv.max_topics,
            COUNT(t.id) AS topics_count
        FROM supervisors sv
        LEFT JOIN topics t ON sv.id = t.supervisor_id
        GROUP BY sv.id, sv.full_name, sv.degree, sv.position, sv.max_topics
        ORDER BY topics_count DESC, sv.full_name ASC;
    """).fetchall()

    # 3. Распределение по статусам (GROUP BY status)
    status_stats = conn.execute("""
        SELECT
            status,
            COUNT(*) AS count
        FROM topics
        GROUP BY status
        ORDER BY count DESC;
    """).fetchall()

    # 4. Фильтрация групп (HAVING): руководители с более чем 1 темой
    busy_supervisors = conn.execute("""
        SELECT
            sv.full_name AS supervisor_name,
            COUNT(t.id) AS topics_count
        FROM supervisors sv
        JOIN topics t ON sv.id = t.supervisor_id
        GROUP BY sv.id, sv.full_name
        HAVING COUNT(t.id) > 1
        ORDER BY topics_count DESC;
    """).fetchall()

    # 5. Распределение студентов по группам (GROUP BY group_name)
    group_stats = conn.execute("""
        SELECT
            group_name,
            COUNT(*) AS students_count
        FROM students
        GROUP BY group_name
        ORDER BY group_name ASC;
    """).fetchall()

    conn.close()

    context = {
        "title": "Статистика курсовых работ",
        "summary": summary,
        "supervisor_stats": supervisor_stats,
        "status_stats": status_stats,
        "busy_supervisors": busy_supervisors,
        "group_stats": group_stats,
    }
    return render(request, "coursework/statistics.html", context)


def student_list(request: HttpRequest) -> HttpResponse:
    """Список студентов кафедры и их тем курсовых работ (SQLite)."""
    query = request.GET.get("q", "").strip()

    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            s.id,
            s.full_name,
            s.group_name,
            s.direction,
            s.email,
            t.id AS topic_id,
            t.title AS topic_title
        FROM students s
        LEFT JOIN topics t ON s.id = t.student_id
        WHERE (? = '' OR s.full_name LIKE ? OR s.group_name LIKE ? OR s.direction LIKE ?)
        ORDER BY s.full_name ASC;
    """
    like_q = f"%{query}%"
    rows = conn.execute(sql, [query, like_q, like_q, like_q]).fetchall()
    conn.close()

    # Группируем темы по студентам
    students_map: dict[int, dict] = {}
    for r in rows:
        sid = r["id"]
        if sid not in students_map:
            students_map[sid] = {"row": r, "topics": []}
        if r["topic_id"]:
            students_map[sid]["topics"].append({
                "id": r["topic_id"],
                "title": r["topic_title"],
            })

    student_items = [
        StudentItem(data["row"], data["topics"])
        for data in students_map.values()
    ]

    context = {
        "title": "Список студентов",
        "students": student_items,
        "query": query,
        "total_count": len(student_items),
    }
    return render(request, "coursework/student_list.html", context)


def supervisor_list(request: HttpRequest) -> HttpResponse:
    """Список научных руководителей кафедры с индикацией их нагрузки (SQLite)."""
    query = request.GET.get("q", "").strip()

    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            sv.id,
            sv.full_name,
            sv.degree,
            sv.position,
            sv.email,
            sv.max_topics,
            COUNT(t.id) AS topics_count
        FROM supervisors sv
        LEFT JOIN topics t ON sv.id = t.supervisor_id
        WHERE (? = '' OR sv.full_name LIKE ? OR sv.degree LIKE ? OR sv.position LIKE ?)
        GROUP BY sv.id, sv.full_name, sv.degree, sv.position, sv.email, sv.max_topics
        ORDER BY sv.full_name ASC;
    """
    like_q = f"%{query}%"
    rows = conn.execute(sql, [query, like_q, like_q, like_q]).fetchall()

    # Загружаем темы каждого руководителя
    all_topics = conn.execute(
        "SELECT id, title, status, supervisor_id FROM topics ORDER BY title ASC"
    ).fetchall()
    conn.close()

    topics_by_sup: dict[int, list] = {}
    for t in all_topics:
        topics_by_sup.setdefault(t["supervisor_id"], []).append(t)

    supervisor_items = [
        SupervisorItem(
            r,
            topics_count=r["topics_count"],
            topics=topics_by_sup.get(r["id"], []),
        )
        for r in rows
    ]

    context = {
        "title": "Научные руководители",
        "supervisors": supervisor_items,
        "query": query,
        "total_count": len(supervisor_items),
    }
    return render(request, "coursework/supervisor_list.html", context)
