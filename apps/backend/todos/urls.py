from rest_framework.routers import DefaultRouter
from .views import TodoListViewSet, TodoItemViewSet, TodoSubItemViewSet


router = DefaultRouter()
router.register(r"todos/lists", TodoListViewSet, basename="todo-list")
router.register(r"todos/items", TodoItemViewSet, basename="todo-item")
router.register(r"todos/subitems", TodoSubItemViewSet, basename="todo-subitem")

urlpatterns = router.urls


