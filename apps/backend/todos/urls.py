from rest_framework.routers import DefaultRouter

from .views import (TodoItemViewSet, TodoListViewSet, TodoPriorityViewSet,
                    TodoSubItemViewSet)

router = DefaultRouter()
router.register(r"todo-lists", TodoListViewSet, basename="todo-list")
router.register(r"todo-items", TodoItemViewSet, basename="todo-item")
router.register(r"todo-subitems", TodoSubItemViewSet, basename="todo-subitem")
router.register(r"todos/priorities", TodoPriorityViewSet, basename="todo-priority")

urlpatterns = router.urls
