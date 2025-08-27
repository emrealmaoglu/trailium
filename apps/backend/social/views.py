from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Prefetch, Count
from .models import Post, Comment, Like
from .serializers import PostSerializer, PostCreateSerializer, CommentSerializer, CommentCreateSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == request.user.id


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = (
        Post.objects.all()
        .select_related("user")
        .prefetch_related(
            Prefetch("comments", queryset=Comment.objects.select_related("user")),
            "likes",
        )
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
    )

    def get_queryset(self):
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        post = self.get_object()
        Like.objects.get_or_create(post=post, user=request.user)
        return response.Response({"status": "liked"}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["delete"], url_path="like")
    def unlike(self, request, pk=None):
        post = self.get_object()
        Like.objects.filter(post=post, user=request.user).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            qs = post.comments.select_related("user").all()
            return response.Response(CommentSerializer(qs, many=True).data)
        ser = CommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        Comment.objects.create(post=post, user=request.user, **ser.validated_data)
        return response.Response(status=status.HTTP_201_CREATED)


