from rest_framework.routers import DefaultRouter
from .views import TodoListViewSet, TodoItemViewSet, TodoSubItemViewSet, TodoPriorityViewSet


router = DefaultRouter()
router.register(r"todos/lists", TodoListViewSet, basename="todo-list")
router.register(r"todos/items", TodoItemViewSet, basename="todo-item")
router.register(r"todos/subitems", TodoSubItemViewSet, basename="todo-subitem")
router.register(r"todos/priorities", TodoPriorityViewSet, basename="todo-priority")

urlpatterns = router.urls


