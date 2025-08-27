from django.contrib import admin
from .models import TodoList, TodoItem, TodoSubItem


class TodoSubItemInline(admin.TabularInline):
    model = TodoSubItem
    extra = 0


class TodoItemInline(admin.StackedInline):
    model = TodoItem
    extra = 0
    readonly_fields = ("progress_cached",)
    show_change_link = True


@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "progress_cached", "created_at")
    list_filter = ("user",)
    search_fields = ("name", "user__username", "user__email")
    readonly_fields = ("progress_cached",)
    date_hierarchy = "created_at"
    inlines = [TodoItemInline]


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ("id", "list", "title", "is_done", "progress_cached")
    list_filter = ("is_done", "list__user")
    search_fields = ("title", "list__name", "list__user__username")
    readonly_fields = ("progress_cached",)


@admin.register(TodoSubItem)
class TodoSubItemAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "title", "is_done")
    list_filter = ("is_done", "parent__list__user")
    search_fields = ("title", "parent__title", "parent__list__name")


