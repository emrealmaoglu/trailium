from rest_framework import serializers
from .models import TodoList, TodoItem, TodoSubItem


class TodoSubItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoSubItem
        fields = [
            "id",
            "parent",
            "title",
            "description",
            "is_done",
            "created_at",
            "updated_at",
        ]


class TodoItemSerializer(serializers.ModelSerializer):
    subitems = TodoSubItemSerializer(many=True, read_only=True)

    class Meta:
        model = TodoItem
        fields = [
            "id",
            "list",
            "title",
            "description",
            "is_done",
            "due_date",
            "progress_cached",
            "subitems",
            "created_at",
            "updated_at",
        ]


class TodoListSerializer(serializers.ModelSerializer):
    items = TodoItemSerializer(many=True, read_only=True)

    class Meta:
        model = TodoList
        fields = [
            "id",
            "user",
            "name",
            "description",
            "kind",
            "progress_cached",
            "items",
            "created_at",
            "updated_at",
        ]


