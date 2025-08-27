from rest_framework import serializers
from .models import Post, Comment, Like


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(source="user")

    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user")
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "author",
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


