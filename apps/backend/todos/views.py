"""
Todos API görünümleri.

Sahiplik bazlı yetkilendirme ve sayfalama desteği içerir.
"""

from rest_framework import viewsets, permissions, decorators, response, status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import TodoList, TodoItem, TodoSubItem, TodoPriority
from .serializers import TodoListSerializer, TodoItemSerializer, TodoSubItemSerializer, TodoPrioritySerializer
from .permissions import IsOwnerOrAdmin
from users.policies import filter_queryset_by_visibility


class TodoPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoPriority.objects.all().order_by("sort_order", "id")
    serializer_class = TodoPrioritySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Todos"], summary="Todo listeleri", description="Kullanıcıya ait todo listeleri.")
class TodoListViewSet(viewsets.ModelViewSet):
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = TodoList.objects.all()
        return filter_queryset_by_visibility(qs, self.request.user, owner_field="user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Todos"], summary="Todo öğeleri", description="Kullanıcıya ait todo öğeleri.")
class TodoItemViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = TodoItem.objects.select_related("list")
        # Sahiplik alanı list.user
        return filter_queryset_by_visibility(qs, self.request.user, owner_field="list__user")

    @decorators.action(detail=True, methods=["post"], url_path="toggle-done")
    def toggle_done(self, request, pk=None):
        item = self.get_object()
        item.is_done = not item.is_done
        item.save(update_fields=["is_done", "updated_at"])
        return response.Response(self.get_serializer(item).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Todos"], summary="Alt öğeler", description="Kullanıcıya ait alt öğeler.")
class TodoSubItemViewSet(viewsets.ModelViewSet):
    queryset = TodoSubItem.objects.all()
    serializer_class = TodoSubItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = TodoSubItem.objects.select_related("parent", "parent__list")
        return filter_queryset_by_visibility(qs, self.request.user, owner_field="parent__list__user")


