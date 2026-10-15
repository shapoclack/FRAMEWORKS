"""Маршруты URL для приложения core."""

from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("http-info/", views.http_info, name="http_info"),
]
