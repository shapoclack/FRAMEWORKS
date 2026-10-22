"""Маршруты URL для приложения coursework (Практическая работа № 7)."""

from django.urls import path
from . import views

app_name = "coursework"

urlpatterns = [
    path("topics/", views.topic_list, name="topic_list"),
    path("topics/<int:pk>/", views.topic_detail, name="topic_detail"),
    path("students/", views.student_list, name="student_list"),
    path("supervisors/", views.supervisor_list, name="supervisor_list"),
    path("available/", views.available_topics, name="available"),
    path("available-topics/", views.available_topics, name="available_topics"),
    path("active/", views.active_topics, name="active_topics"),
    path("statistics/", views.statistics, name="statistics"),
]
