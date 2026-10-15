"""Маршруты URL для приложения coursework."""

from django.urls import path
from . import views

app_name = "coursework"

urlpatterns = [
    path("topics/", views.topic_list, name="topic_list"),
    path("topics/<int:pk>/", views.topic_detail, name="topic_detail"),
    path("students/", views.student_list, name="student_list"),
    path("supervisors/", views.supervisor_list, name="supervisor_list"),
]
