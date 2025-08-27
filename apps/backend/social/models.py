from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="albums"
    )
    title = models.CharField(max_length=200)
    is_published = models.BooleanField(default=True)
    visibility = models.CharField(max_length=16, default="public")
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
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["album", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title or self.url


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
