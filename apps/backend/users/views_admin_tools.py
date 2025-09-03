import logging

from django.contrib.auth import get_user_model
from django.db import models, transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.models import Album, Comment, Follow, Like, Photo, Post
from todos.models import TodoItem, TodoList, TodoSubItem

from .permissions import IsSuperUser

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsSuperUser])
def purge_non_admin_users(request):
    """
    🚨 DANGER: Permanently delete all non-admin users and their related content.

    This endpoint requires:
    - User must be authenticated
    - User must be a superuser
    - Explicit confirmation with exact phrase
    - Proper request body format

    Request body:
    {
        "confirm": "PURGE_NON_ADMIN_USERS",
        "keep": ["admin", "page_manager@example.com"],
        "dry_run": false
    }
    """

    # Validate request data
    confirm = request.data.get("confirm")
    keep_list = request.data.get("keep", [])
    dry_run = request.data.get("dry_run", True)  # Default to dry-run for safety

    # Safety check - require exact confirmation phrase
    if confirm != "PURGE_NON_ADMIN_USERS":
        return Response(
            {
                "error": "Confirmation required",
                "message": 'You must type exactly "PURGE_NON_ADMIN_USERS" to confirm this operation',
                "required_phrase": "PURGE_NON_ADMIN_USERS",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate keep_list format
    if not isinstance(keep_list, list):
        return Response(
            {
                "error": "Invalid keep_list format",
                "message": "keep_list must be an array of usernames or emails",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if dry_run:
            # Dry run - just show what would be deleted
            deletion_summary = get_deletion_summary(keep_list)

            # Log the dry run
            logger.info(
                f"PURGE_NON_ADMIN_USERS dry run by {request.user.username} ({request.user.id}) "
                f'from {request.META.get("REMOTE_ADDR", "unknown")}. '
                f'Would delete {deletion_summary["users"]} users and {deletion_summary["total_related"]} related objects.'
            )

            return Response(
                {
                    "mode": "dry_run",
                    "message": "Dry run completed - no data was deleted",
                    "would_delete": deletion_summary,
                },
                status=status.HTTP_200_OK,
            )

        else:
            # Actual purge
            deletion_summary = purge_users(keep_list)

            # Log the actual purge
            logger.warning(
                f"PURGE_NON_ADMIN_USERS executed by {request.user.username} ({request.user.id}) "
                f'from {request.META.get("REMOTE_ADDR", "unknown")}. '
                f'Deleted {deletion_summary["users"]} users and {deletion_summary["total_related"]} related objects.'
            )

            return Response(
                {
                    "mode": "executed",
                    "message": "Purge completed successfully",
                    "deleted": deletion_summary,
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        error_msg = f"Purge operation failed: {str(e)}"
        logger.error(f"PURGE_NON_ADMIN_USERS failed: {error_msg}")

        return Response(
            {"error": "Purge failed", "message": error_msg},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_deletion_summary(keep_list):
    """Get summary of what would be deleted"""
    # Users to preserve
    preserved_users = get_preserved_users(keep_list)
    preserved_user_ids = list(preserved_users.values_list("id", flat=True))

    # Users to delete
    users_to_delete = User.objects.exclude(id__in=preserved_user_ids)

    # Count related objects
    summary = {
        "users": users_to_delete.count(),
        "posts": Post.objects.filter(user__in=users_to_delete).count(),
        "comments": Comment.objects.filter(user__in=users_to_delete).count(),
        "likes": Like.objects.filter(user__in=users_to_delete).count(),
        "albums": Album.objects.filter(user__in=users_to_delete).count(),
        "photos": Photo.objects.filter(album__user__in=users_to_delete).count(),
        "follows": Follow.objects.filter(
            models.Q(follower__in=users_to_delete)
            | models.Q(followed__in=users_to_delete)
        ).count(),
        "todo_lists": TodoList.objects.filter(user__in=users_to_delete).count(),
        "todo_items": TodoItem.objects.filter(list__user__in=users_to_delete).count(),
        "todo_sub_items": TodoSubItem.objects.filter(
            parent__list__user__in=users_to_delete
        ).count(),
        "kept_users": preserved_users.count(),
        "kept_usernames": list(preserved_users.values_list("username", flat=True)),
    }

    summary["total_related"] = (
        summary["posts"]
        + summary["comments"]
        + summary["likes"]
        + summary["albums"]
        + summary["photos"]
        + summary["follows"]
        + summary["todo_lists"]
        + summary["todo_items"]
        + summary["todo_sub_items"]
    )

    return summary


def get_preserved_users(keep_list):
    """Get users that should be preserved"""
    preserved = User.objects.filter(is_superuser=True)

    if keep_list:
        # Add users from keep_list (by username or email)
        keep_users = User.objects.filter(
            models.Q(username__in=keep_list) | models.Q(email__in=keep_list)
        )
        preserved = preserved | keep_users

    return preserved.distinct()


def purge_users(keep_list):
    """Actually delete the users and related content"""
    with transaction.atomic():
        # Get users to preserve
        preserved_users = get_preserved_users(keep_list)
        preserved_user_ids = list(preserved_users.values_list("id", flat=True))

        # Get users to delete
        users_to_delete = User.objects.exclude(id__in=preserved_user_ids)

        # Delete in proper order to handle CASCADE relationships
        # First, delete objects that might have PROTECT relationships

        # Delete follows (both as follower and followed)
        Follow.objects.filter(
            models.Q(follower__in=users_to_delete)
            | models.Q(followed__in=users_to_delete)
        ).delete()

        # Delete likes
        Like.objects.filter(user__in=users_to_delete).delete()

        # Delete comments
        Comment.objects.filter(user__in=users_to_delete).delete()

        # Delete photos (albums will cascade)
        Photo.objects.filter(album__user__in=users_to_delete).delete()

        # Delete albums
        Album.objects.filter(user__in=users_to_delete).delete()

        # Delete todo sub-items
        TodoSubItem.objects.filter(parent__list__user__in=users_to_delete).delete()

        # Delete todo items
        TodoItem.objects.filter(list__user__in=users_to_delete).delete()

        # Delete todo lists
        TodoList.objects.filter(user__in=users_to_delete).delete()

        # Delete posts
        Post.objects.filter(user__in=users_to_delete).delete()

        # Finally, delete the users
        users_to_delete.delete()

        # Get final summary
        return get_deletion_summary(keep_list)
