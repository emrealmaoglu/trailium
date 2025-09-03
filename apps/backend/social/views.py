from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, Comment, Follow, Like, Photo, Post
from .serializers import (AlbumCreateSerializer, AlbumSerializer,
                          CommentCreateSerializer, CommentSerializer,
                          FollowSerializer, PhotoCreateSerializer,
                          PhotoSerializer, PostCreateSerializer,
                          PostSerializer)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == request.user.id


def _visible_posts_for(user):
    # public or own; followers-only visible to accepted followers
    following = Follow.objects.filter(follower=user, status="accepted").values_list(
        "followed_id", flat=True
    )
    return (
        Q(visibility="public")
        | Q(user=user)
        | (Q(visibility="followers") & Q(user_id__in=following))
    )


class PostPagination(PageNumberPagination):
    page_size = 10


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
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

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        base = super().get_queryset()
        # If viewing a specific user's posts and the requester follows them (accepted) or it's self, allow
        user_id = self.request.query_params.get("user_id")
        if user_id:
            try:
                uid = int(user_id)
            except ValueError:
                uid = None
            if uid:
                if uid == self.request.user.id:
                    return base.filter(user_id=uid)
                is_following = Follow.objects.filter(
                    follower=self.request.user, followed_id=uid, status="accepted"
                ).exists()
                if is_following:
                    return base.filter(user_id=uid).filter(
                        Q(visibility="public") | Q(visibility="followers")
                    )
                # else fall back to public-only
                return base.filter(user_id=uid, visibility="public")
        return base.filter(_visible_posts_for(self.request.user))

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["post", "delete"], url_path="like")
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method.lower() == "post":
            Like.objects.get_or_create(post=post, user=request.user)
            return response.Response({"status": "liked"}, status=status.HTTP_200_OK)
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


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = AlbumSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        qs = Album.objects.all().prefetch_related("photos")
        if user_id:
            try:
                uid = int(user_id)
            except ValueError:
                uid = None
            if uid:
                if uid == self.request.user.id:
                    return qs.filter(user_id=uid)
                is_following = Follow.objects.filter(
                    follower=self.request.user, followed_id=uid, status="accepted"
                ).exists()
                if is_following:
                    return qs.filter(user_id=uid).filter(
                        Q(visibility="public") | Q(visibility="followers")
                    )
                return qs.filter(user_id=uid, visibility="public")
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AlbumCreateSerializer
        return AlbumSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["get", "post"], url_path="photos")
    def photos(self, request, pk=None):
        album = self.get_object()
        if request.method == "GET":
            return response.Response(
                PhotoSerializer(album.photos.all(), many=True).data
            )
        ser = PhotoCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        Photo.objects.create(album=album, **ser.validated_data)
        return response.Response(status=status.HTTP_201_CREATED)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="users/(?P<user_id>[^/.]+)/follow")
    def follow(self, request, user_id=None):
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            user_to_follow = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user_to_follow == request.user:
            return Response({"error": "Cannot follow yourself"}, status=400)

        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            followed=user_to_follow,
            defaults={"status": "pending"},
        )

        if not created:
            if follow_obj.status == "accepted":
                return Response({"message": "Already following"}, status=200)
            elif follow_obj.status == "pending":
                return Response(
                    {"message": "Follow request already pending"}, status=200
                )

        return Response({"message": "Follow request sent"}, status=201)

    @action(
        detail=False, methods=["post"], url_path="users/(?P<user_id>[^/.]+)/unfollow"
    )
    def unfollow(self, request, user_id=None):
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            Follow.objects.filter(follower=request.user, followed_id=user_id).delete()
            return Response({"message": "Unfollowed successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["post"], url_path="users/(?P<user_id>[^/.]+)/accept")
    def accept(self, request, user_id=None):
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            follow_obj = Follow.objects.get(
                follower_id=user_id, followed=request.user, status="pending"
            )
            follow_obj.status = "accepted"
            follow_obj.save()
            return Response({"message": "Follow request accepted"}, status=200)
        except Follow.DoesNotExist:
            return Response({"error": "Follow request not found"}, status=404)

    @action(detail=False, methods=["post"], url_path="users/(?P<user_id>[^/.]+)/reject")
    def reject(self, request, user_id=None):
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            Follow.objects.filter(
                follower_id=user_id, followed=request.user, status="pending"
            ).delete()
            return Response({"message": "Follow request rejected"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="users/(?P<user_id>[^/.]+)/status")
    def status(self, request, user_id=None):
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            follow_obj = Follow.objects.get(follower=request.user, followed_id=user_id)
            return Response({"status": follow_obj.status}, status=200)
        except Follow.DoesNotExist:
            return Response({"status": "none"}, status=200)

    @action(detail=False, methods=["get"], url_path="followers")
    def followers(self, request):
        followers = Follow.objects.filter(
            followed=request.user, status="accepted"
        ).select_related("follower")
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="following")
    def following(self, request):
        following = Follow.objects.filter(
            follower=request.user, status="accepted"
        ).select_related("followed")
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


class FeedPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_size = 5


class FeedPosts(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        following_ids = Follow.objects.filter(
            follower=request.user, status="accepted"
        ).values_list("followed_id", flat=True)
        qs = (
            Post.objects.filter(user_id__in=following_ids)
            .filter(Q(visibility="public") | Q(visibility="followers"))
            .select_related("user")
            .prefetch_related("likes")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )
        paginator = FeedPagination()
        page = paginator.paginate_queryset(qs, request)
        ser = PostSerializer(page, many=True)
        return paginator.get_paginated_response(ser.data)
