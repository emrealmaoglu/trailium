import logging

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiParameter
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers

from .models import Album, Comment, Follow, Like, Photo, Post, AlbumLike, AlbumComment
from users.policies import filter_queryset_by_visibility
from .serializers import (
    AlbumCreateSerializer,
    AlbumSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    FollowSerializer,
    PhotoCreateSerializer,
    PhotoSerializer,
    PostCreateSerializer,
    PostSerializer,
    AlbumCommentSerializer,
    AlbumCommentCreateSerializer,
)

logger = logging.getLogger(__name__)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == request.user.id


class UserContentResponseSerializer(serializers.Serializer):
    private = serializers.BooleanField()
    message = serializers.CharField(required=False)
    posts = PostSerializer(many=True, required=False)
    albums = AlbumSerializer(many=True, required=False)


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
    parser_classes = [MultiPartParser, FormParser]
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
        # Görünürlük filtresi: public/followers/owner
        return filter_queryset_by_visibility(base, self.request.user, owner_field="user")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        # image is handled by serializer field; no extra processing here
        return instance

    @extend_schema(
        description="Like a post",
        parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)],
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

    @extend_schema(
        description="Unlike a post",
        parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)],
        responses={204: None},
    )
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
        parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)],
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
    retrieve=extend_schema(description="Retrieve a specific album", parameters=[OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH)]),
    update=extend_schema(description="Update an album (owner only)", parameters=[OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH)]),
    partial_update=extend_schema(description="Partially update an album (owner only)", parameters=[OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH)]),
    destroy=extend_schema(description="Delete an album (owner only)", parameters=[OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH)]),
)
class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = AlbumSerializer
    parser_classes = [MultiPartParser, FormParser]
    queryset = Album.objects.all()

    def get_queryset(self):
        qs = Album.objects.all().prefetch_related("photos").annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        return filter_queryset_by_visibility(qs, self.request.user, owner_field="user")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AlbumCreateSerializer
        return AlbumSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
    @decorators.action(detail=True, methods=["get", "post"], url_path="photos")
    def photos(self, request, pk=None):
        album = self.get_object()
        if request.method == "GET":
            return response.Response(
                PhotoSerializer(album.photos.all(), many=True, context={"request": request}).data
            )
        ser = PhotoCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(album=album)
        return response.Response(PhotoSerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
    @decorators.action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        # Allow liking visible albums of other users
        album = Album.objects.filter(pk=pk).first()
        if not album:
            return response.Response(status=404)
        # Visibility: owner, public, or followers (accepted)
        is_owner = album.user_id == request.user.id
        is_public = getattr(album, "visibility", "public") == "public"
        is_followers = getattr(album, "visibility", "public") == "followers"
        is_accepted = False
        if is_followers and not is_owner:
            is_accepted = Follow.objects.filter(
                follower=request.user, followed_id=album.user_id, status="accepted"
            ).exists()
        if not (is_owner or is_public or is_accepted):
            return response.Response({"error": "Not allowed"}, status=403)
        if AlbumLike.objects.filter(album=album, user=request.user).exists():
            return response.Response({"error": "Album already liked"}, status=400)
        AlbumLike.objects.create(album=album, user=request.user)
        return response.Response({"status": "liked"})

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
    @decorators.action(detail=True, methods=["delete"], url_path="unlike")
    def unlike(self, request, pk=None):
        album = Album.objects.filter(pk=pk).first()
        if not album:
            return response.Response(status=404)
        like_obj = AlbumLike.objects.filter(album=album, user=request.user).first()
        if not like_obj:
            return response.Response({"error": "Album not liked"}, status=400)
        like_obj.delete()
        return response.Response(status=204)

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
    @decorators.action(detail=True, methods=["get", "post"], url_path="comments")
    def album_comments(self, request, pk=None):
        album = Album.objects.filter(pk=pk).first()
        if not album:
            return response.Response(status=404)
        # Visibility check (same as like)
        is_owner = album.user_id == request.user.id
        is_public = getattr(album, "visibility", "public") == "public"
        is_followers = getattr(album, "visibility", "public") == "followers"
        is_accepted = False
        if is_followers and not is_owner:
            is_accepted = Follow.objects.filter(
                follower=request.user, followed_id=album.user_id, status="accepted"
            ).exists()
        if not (is_owner or is_public or is_accepted):
            return response.Response({"error": "Not allowed"}, status=403)
        if request.method == "GET":
            qs = album.comments.select_related("user").all()
            return response.Response(AlbumCommentSerializer(qs, many=True).data)
        ser = AlbumCommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        AlbumComment.objects.create(album=album, user=request.user, **ser.validated_data)
        return response.Response(status=201)


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

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)])
    @action(detail=False, methods=["get"], url_path="pending")
    def pending_requests(self, request):
        """Get pending follow requests for the current user"""
        pending_follows = Follow.objects.filter(
            followed=request.user, status="pending"
        ).select_related("follower")

        serializer = FollowSerializer(pending_follows, many=True)
        return response.Response(serializer.data)

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)])
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

    @extend_schema(responses={200: PostSerializer(many=True)})
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
        if page is None:
            return Response(PostSerializer(qs, many=True, context={"request": request}).data)
        ser = PostSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(ser.data)


class UserContent(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(parameters=[OpenApiParameter(name="user_id", type=int, location=OpenApiParameter.PATH)], responses={200: UserContentResponseSerializer})
    def get(self, request, user_id):
        from users.models import User

        try:
            owner = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        status_str = self.get_follow_status(request.user, owner.id)
        is_open = not owner.is_private or status_str == "accepted" or status_str == "self"
        if not is_open:
            return Response({"private": True, "message": "Bu hesap gizlidir."}, status=200)

        # visible posts
        posts_qs = (
            Post.objects.filter(user=owner)
            .filter(Q(visibility="public") | Q(visibility="followers"))
            .select_related("user")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

        # visible albums: same visibility logic (assuming album.visibility semantics)
        albums_qs = (
            Album.objects.filter(user=owner)
            .filter(Q(visibility="public") | Q(visibility="followers"))
            .prefetch_related("photos")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

        return Response(
            {
                "private": False,
                "posts": PostSerializer(posts_qs, many=True, context={"request": request}).data,
                "albums": AlbumSerializer(albums_qs, many=True, context={"request": request}).data,
            }
        )

    def get_follow_status(self, viewer, owner_id):
        if viewer.id == owner_id:
            return "self"
        try:
            f = Follow.objects.get(follower=viewer, followed_id=owner_id)
            return f.status
        except Follow.DoesNotExist:
            return "none"
