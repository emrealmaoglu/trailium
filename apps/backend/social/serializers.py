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
    body = serializers.CharField(min_length=1, max_length=2000, help_text="Post content (1-2000 characters)")
    title = serializers.CharField(max_length=200, required=False, allow_blank=True, help_text="Optional post title (max 200 characters)")
    
    class Meta:
        model = Post
        fields = ["title", "body", "is_published", "visibility"]
    
    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Post content cannot be empty.")
        return value.strip()


class CommentCreateSerializer(serializers.ModelSerializer):
    body = serializers.CharField(min_length=1, max_length=1000, help_text="Comment content (1-1000 characters)")
    
    class Meta:
        model = Comment
        fields = ["body"]
    
    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        return value.strip()


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "title", "url", "thumbnail_url", "metadata", "created_at"]


class PhotoCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, help_text="Image file (max 5MB)")
    title = serializers.CharField(max_length=200, required=False, allow_blank=True, help_text="Optional photo title")
    caption = serializers.CharField(max_length=500, required=False, allow_blank=True, help_text="Optional photo caption")
    
    class Meta:
        model = Photo
        fields = ["title", "caption", "image"]
    
    def validate_image(self, value):
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
        return value
    
    def create(self, validated_data):
        # Set url and thumbnail_url from the uploaded image
        photo = super().create(validated_data)
        if photo.image:
            photo.url = photo.image.url
            photo.thumbnail_url = photo.image.url  # For now, use same URL
            photo.save()
        return photo


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "is_published", "visibility", "created_at", "photos"]


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["id", "title", "is_published", "visibility", "created_at"]


class FollowSerializer(serializers.ModelSerializer):
    follower = AuthorSerializer(read_only=True)
    followed = AuthorSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "followed", "status", "created_at"]
