from django.contrib import admin

from .models import TodoItem, TodoList, TodoSubItem, TodoPriority


@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "kind", "progress_cached", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("kind",)


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ("id", "list", "title", "is_done", "progress_cached")
    search_fields = ("title", "list__name")
    list_filter = ("is_done",)


@admin.register(TodoSubItem)
class TodoSubItemAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "title", "is_done")
    search_fields = ("title", "parent__title")
    list_filter = ("is_done",)


@admin.register(TodoPriority)
class TodoPriorityAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "sort_order", "is_default")
    search_fields = ("key", "name")
