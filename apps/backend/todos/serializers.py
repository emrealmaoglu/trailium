from rest_framework import serializers
from .models import TodoList, TodoItem, TodoSubItem, TodoPriority


class TodoPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoPriority
        fields = [
            "id",
            "key",
            "name",
            "color",
            "sort_order",
            "is_default",
        ]


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
    priority = TodoPrioritySerializer(read_only=True)
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=TodoPriority.objects.all(), source="priority", write_only=True, required=False
    )

    class Meta:
        model = TodoItem
        fields = [
            "id",
            "list",
            "title",
            "description",
            "is_done",
            "due_date",
            "priority",
            "priority_id",
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


