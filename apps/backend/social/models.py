from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
import uuid
import os


def _uuid_filename(instance, filename, prefix="uploads"):
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    return os.path.join(prefix, f"{uuid.uuid4().hex}{ext}")


def post_image_upload_to(instance, filename):
    return _uuid_filename(instance, filename, "posts")


def photo_file_upload_to(instance, filename):
    return _uuid_filename(instance, filename, "photos")


def photo_thumb_upload_to(instance, filename):
    return _uuid_filename(instance, filename, "photos/thumbs")


class Post(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("followers", "Followers only"),
        ("private", "Private"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(5, "Title must be at least 5 characters long."),
            MaxLengthValidator(200, "Title cannot exceed 200 characters."),
        ],
    )
    body = models.TextField(
        blank=True,
        validators=[
            MaxLengthValidator(5000, "Post content cannot exceed 5000 characters.")
        ],
    )
    # New (optional) image file for uploads; UUID naming
    image = models.ImageField(upload_to=post_image_upload_to, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    visibility = models.CharField(
        max_length=16, choices=VISIBILITY_CHOICES, default="public"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["visibility", "created_at"]),
            models.Index(fields=["is_published", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField(
        validators=[
            MinLengthValidator(1, "Comment cannot be empty."),
            MaxLengthValidator(1000, "Comment cannot exceed 1000 characters."),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"], name="uniq_like_post_user"
            ),
        ]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]


class Album(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("followers", "Followers only"),
        ("private", "Private"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="albums"
    )
    title = models.CharField(max_length=200)
    is_published = models.BooleanField(default=True)
    visibility = models.CharField(max_length=16, default="public", choices=VISIBILITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["visibility", "created_at"]),
            models.Index(fields=["is_published", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")
    title = models.CharField(max_length=200, blank=True)
    # Existing URL fields kept for compatibility
    url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    # New upload fields
    file = models.ImageField(upload_to=photo_file_upload_to, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=photo_thumb_upload_to, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["album", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title or self.url or (self.file.name if self.file else "")


class AlbumComment(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="album_comments"
    )
    body = models.TextField(
        validators=[
            MinLengthValidator(1, "Comment cannot be empty."),
            MaxLengthValidator(1000, "Comment cannot exceed 1000 characters."),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["album", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]


class AlbumLike(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="album_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["album", "user"], name="uniq_like_album_user"),
        ]
        indexes = [
            models.Index(fields=["album", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]


class Follow(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("accepted", "accepted"),
        ("rejected", "rejected"),
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="uniq_follow_pair"
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "status", "created_at"]),
            models.Index(fields=["followed", "status", "created_at"]),
        ]
