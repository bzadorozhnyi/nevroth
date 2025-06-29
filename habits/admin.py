from django.contrib import admin
from .models import Habit, HabitProgress


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(HabitProgress)
class HabitProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "habit", "status", "date", "updated_at")
    list_filter = ("status", "date", "updated_at", "habit")
    search_fields = ("user__email", "habit__name")
    ordering = ("-date",)
    autocomplete_fields = ("user", "habit")
    readonly_fields = ("date", "updated_at")
