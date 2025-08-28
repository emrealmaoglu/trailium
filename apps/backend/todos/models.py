from django.conf import settings
from django.db import models


class TodoPriority(models.Model):
    key = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=16, default="#6b7280")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.key})"


class TodoList(models.Model):
    KIND_CHOICES = (
        ("personal", "Personal"),
        ("work", "Work"),
        ("other", "Other"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="todo_lists")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=24, choices=KIND_CHOICES, default="personal")
    progress_cached = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.user_id})"


class TodoItem(models.Model):
    list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)
    priority = models.ForeignKey(TodoPriority, on_delete=models.PROTECT, related_name="items", null=True, blank=True)
    progress_cached = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title


class TodoSubItem(models.Model):
    parent = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name="subitems")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title


