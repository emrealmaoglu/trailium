from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Q
from .models import TodoList, TodoItem, TodoSubItem, TodoPriority
from .serializers import TodoListSerializer, TodoItemSerializer, TodoSubItemSerializer, TodoPrioritySerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, TodoList):
            return obj.user_id == request.user.id
        if isinstance(obj, TodoItem):
            return obj.list.user_id == request.user.id
        if isinstance(obj, TodoSubItem):
            return obj.parent.list.user_id == request.user.id
        return False


class TodoPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoPriority.objects.all().order_by("sort_order", "id")
    serializer_class = TodoPrioritySerializer
    permission_classes = [permissions.IsAuthenticated]


class TodoListViewSet(viewsets.ModelViewSet):
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        return TodoList.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoItemViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        return TodoItem.objects.filter(list__user=user)

    @decorators.action(detail=True, methods=["post"], url_path="toggle-done")
    def toggle_done(self, request, pk=None):
        item = self.get_object()
        item.is_done = not item.is_done
        item.save(update_fields=["is_done", "updated_at"])
        return response.Response(self.get_serializer(item).data, status=status.HTTP_200_OK)


class TodoSubItemViewSet(viewsets.ModelViewSet):
    queryset = TodoSubItem.objects.all()
    serializer_class = TodoSubItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        return TodoSubItem.objects.filter(parent__list__user=user)


