"""Настройка панели администратора Django для моделей учета курсовых работ."""

from django.contrib import admin
from .models import StatusHistory, Student, Supervisor, Topic


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "group_name", "direction", "email", "created_at")
    search_fields = ("full_name", "group_name", "email")
    list_filter = ("group_name", "direction")


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "degree", "position", "email", "max_topics", "created_at")
    search_fields = ("full_name", "degree", "position", "email")
    list_filter = ("degree", "position")


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_at", "changed_by")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "supervisor", "student", "status", "deadline", "created_at")
    list_filter = ("status", "supervisor", "deadline")
    search_fields = ("title", "description", "supervisor__full_name", "student__full_name")
    inlines = [StatusHistoryInline]


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "old_status", "new_status", "changed_at", "changed_by")
    list_filter = ("old_status", "new_status", "changed_at")
    search_fields = ("topic__title", "changed_by")
