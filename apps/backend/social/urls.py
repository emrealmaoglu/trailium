from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AlbumViewSet, FeedPosts, FollowViewSet, PostViewSet, UserContent

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"albums", AlbumViewSet, basename="album")
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = [
    *router.urls,
    path("feed/posts", FeedPosts.as_view(), name="feed-posts"),
    path("users/<int:user_id>/content", UserContent.as_view(), name="user-content"),
]
