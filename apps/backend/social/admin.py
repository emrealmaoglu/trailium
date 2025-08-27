from django.contrib import admin

from .models import Album, Comment, Follow, Like, Photo, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_published", "visibility", "created_at")
    search_fields = ("title", "user__username")
    list_filter = ("is_published", "visibility")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("post__title", "user__username", "body")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user")
    search_fields = ("post__title", "user__username")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_published", "visibility", "created_at")
    search_fields = ("title", "user__username")
    list_filter = ("is_published", "visibility")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "album", "title")
    search_fields = ("title", "album__title")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "followed", "status", "created_at")
    search_fields = ("follower__username", "followed__username")
    list_filter = ("status",)
