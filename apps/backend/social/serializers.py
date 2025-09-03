from rest_framework import serializers

from .models import Album, Comment, Follow, Photo, Post


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "user",
            "is_published",
            "visibility",
            "likes_count",
            "comments_count",
            "created_at",
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "body", "is_published", "visibility"]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["body"]


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "title", "url", "thumbnail_url", "metadata", "created_at"]


class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["title", "url", "thumbnail_url", "metadata"]


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "is_published", "visibility", "created_at", "photos"]


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["title", "is_published", "visibility"]


class FollowSerializer(serializers.ModelSerializer):
    follower = AuthorSerializer(read_only=True)
    followed = AuthorSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "followed", "status", "created_at"]
