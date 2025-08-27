import logging

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
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

logger = logging.getLogger(__name__)


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


@extend_schema_view(
    list=extend_schema(description="List all visible posts for the authenticated user"),
    create=extend_schema(description="Create a new post"),
    retrieve=extend_schema(description="Retrieve a specific post"),
    update=extend_schema(description="Update a post (owner only)"),
    partial_update=extend_schema(description="Partially update a post (owner only)"),
    destroy=extend_schema(description="Delete a post (owner only)"),
)
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

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        base = super().get_queryset()
        return base.filter(_visible_posts_for(self.request.user))

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        description="Like a post",
        responses={
            200: {"type": "object", "properties": {"status": {"type": "string"}}}
        },
    )
    @decorators.action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        post = self.get_object()

        # Check if user already liked the post
        if Like.objects.filter(post=post, user=request.user).exists():
            return response.Response(
                {"error": "Post already liked"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create like with transaction
        from django.db import transaction

        with transaction.atomic():
            Like.objects.create(post=post, user=request.user)
            post.likes_count = (post.likes_count or 0) + 1
            post.save(update_fields=["likes_count"])

        return response.Response({"status": "liked"}, status=status.HTTP_200_OK)

    @extend_schema(description="Unlike a post", responses={204: None})
    @decorators.action(detail=True, methods=["delete"], url_path="unlike")
    def unlike(self, request, pk=None):
        post = self.get_object()

        # Check if user has liked the post
        like_obj = Like.objects.filter(post=post, user=request.user).first()
        if not like_obj:
            return response.Response(
                {"error": "Post not liked"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Remove like with transaction
        from django.db import transaction

        with transaction.atomic():
            like_obj.delete()
            post.likes_count = max(0, (post.likes_count or 0) - 1)
            post.save(update_fields=["likes_count"])

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Get or create comments for a post",
        responses={200: CommentSerializer(many=True), 201: None},
    )
    @decorators.action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        try:
            post = self.get_object()
            if request.method == "GET":
                qs = post.comments.select_related("user").all()
                return response.Response(CommentSerializer(qs, many=True).data)

            ser = CommentCreateSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            Comment.objects.create(post=post, user=request.user, **ser.validated_data)
            return response.Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in comments action: {e}", exc_info=True)
            return response.Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema_view(
    list=extend_schema(description="List all albums for the authenticated user"),
    create=extend_schema(description="Create a new album"),
    retrieve=extend_schema(description="Retrieve a specific album"),
    update=extend_schema(description="Update an album (owner only)"),
    partial_update=extend_schema(description="Partially update an album (owner only)"),
    destroy=extend_schema(description="Delete an album (owner only)"),
)
class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = AlbumSerializer

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user).prefetch_related("photos")

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


@extend_schema_view(
    list=extend_schema(description="List follow requests for the authenticated user"),
    create=extend_schema(description="Create a follow request"),
    retrieve=extend_schema(description="Retrieve a specific follow relationship"),
    update=extend_schema(description="Update a follow relationship"),
    partial_update=extend_schema(description="Partially update a follow relationship"),
    destroy=extend_schema(description="Delete a follow relationship"),
)
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            # Show follow requests for the current user
            return Follow.objects.filter(followed=user)
        return Follow.objects.all()

    @decorators.action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve a follow request"""
        follow = self.get_object()

        # Check if this is a follow request for the current user
        if follow.followed != request.user:
            return response.Response(
                {"error": "You can only approve follow requests for yourself"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the request is pending
        if follow.status != "pending":
            return response.Response(
                {"error": "This follow request is not pending"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Approve the follow request
        follow.status = "accepted"
        follow.save()

        return response.Response(
            {
                "status": "approved",
                "message": f"Follow request from {follow.follower.username} approved",
            }
        )

    @decorators.action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """Reject a follow request"""
        follow = self.get_object()

        # Check if this is a follow request for the current user
        if follow.followed != request.user:
            return response.Response(
                {"error": "You can only reject follow requests for yourself"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the request is pending
        if follow.status != "pending":
            return response.Response(
                {"error": "This follow request is not pending"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reject the follow request
        follow.status = "rejected"
        follow.save()

        return response.Response(
            {
                "status": "rejected",
                "message": f"Follow request from {follow.follower.username} rejected",
            }
        )

    @decorators.action(detail=False, methods=["get"], url_path="pending")
    def pending_requests(self, request):
        """Get pending follow requests for the current user"""
        pending_follows = Follow.objects.filter(
            followed=request.user, status="pending"
        ).select_related("follower")

        serializer = FollowSerializer(pending_follows, many=True)
        return response.Response(serializer.data)

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
