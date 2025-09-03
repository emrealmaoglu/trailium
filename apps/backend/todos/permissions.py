from rest_framework.permissions import BasePermission

from .models import TodoItem, TodoList, TodoSubItem


class IsOwnerOrAdmin(BasePermission):
    """Sadece sahibi (veya admin) kaynaklara erişebilir.

    Notes
    -----
    Kullanıcı admin ise tüm kayıtlara erişebilir.
    Normal kullanıcılar yalnızca kendilerine ait TodoList/TodoItem/TodoSubItem
    kayıtlarını görebilir ve yönetebilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if isinstance(obj, TodoList):
            return obj.user_id == request.user.id
        if isinstance(obj, TodoItem):
            return obj.list.user_id == request.user.id
        if isinstance(obj, TodoSubItem):
            return obj.parent.list.user_id == request.user.id
        return False
