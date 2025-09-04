"""
Todo serileştiricileri.

Türkçe NumPy tarzı docstringler içerir.
"""

from rest_framework import serializers

from .models import TodoItem, TodoList, TodoPriority, TodoSubItem


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
    """Alt öğe serileştiricisi.

    Notes
    -----
    `parent` alanı, kullanıcının sahibi olduğu bir TodoItem olmalıdır.
    """

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

    def validate_parent(self, parent: TodoItem):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            if parent.list.user_id != request.user.id:
                raise serializers.ValidationError("Bu öğe size ait değil.")
        return parent


class TodoItemSerializer(serializers.ModelSerializer):
    """Todo öğesi serileştiricisi.

    Read-only olarak alt öğeleri döner; oluşturma/güncellemede sadece referanslar alınır.
    """

    subitems = TodoSubItemSerializer(many=True, read_only=True)
    priority = TodoPrioritySerializer(read_only=True)
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=TodoPriority.objects.all(),
        source="priority",
        write_only=True,
        required=False,
    )
    title = serializers.CharField(min_length=1, max_length=200, help_text="Todo title (1-200 characters)")
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True, help_text="Optional description (max 1000 characters)")

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
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Todo title cannot be empty.")
        return value.strip()

    def validate_list(self, tlist: TodoList):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            if tlist.user_id != request.user.id:
                raise serializers.ValidationError("Bu listeye erişim yetkiniz yok.")
        return tlist


class TodoListSerializer(serializers.ModelSerializer):
    """Todo listesi serileştiricisi.

    Ek alanlar:
    - items_count: listedeki öğe sayısı
    - progress: öğe ilerlemelerinin ortalaması (0..100)
    """

    items = TodoItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField(read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TodoList
        fields = [
            "id",
            "user",
            "name",
            "description",
            "kind",
            "progress_cached",
            "items_count",
            "progress",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_items_count(self, obj: TodoList) -> int:
        return obj.items.count()

    def get_progress(self, obj: TodoList) -> int:
        count = obj.items.count()
        if count == 0:
            return 0
        total = sum(i.progress_cached for i in obj.items.all())
        return int(round(total / count))
