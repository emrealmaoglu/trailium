from rest_framework import serializers
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import io
from drf_spectacular.utils import extend_schema_field

from .models import Album, Comment, Follow, Photo, Post, AlbumLike, AlbumComment

MAX_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png"}
THUMB_LONGEST = 512
THUMB_FMT = "JPEG"
THUMB_QUALITY = 82


def _validate_image_upload(f: UploadedFile):
    if not isinstance(f, UploadedFile):
        raise serializers.ValidationError("Invalid upload")
    if f.size > MAX_SIZE_BYTES:
        raise serializers.ValidationError("File too large (max 5MB)")
    if f.content_type not in ALLOWED_MIME:
        raise serializers.ValidationError("Unsupported type. Use JPEG/PNG")


def _generate_thumbnail(img_file: UploadedFile) -> ContentFile:
    img = Image.open(img_file)
    img = img.convert("RGB")  # ensures JPEG-friendly and strips metadata
    w, h = img.size
    if max(w, h) > THUMB_LONGEST:
        if w >= h:
            new_w = THUMB_LONGEST
            new_h = int(h * (THUMB_LONGEST / w))
        else:
            new_h = THUMB_LONGEST
            new_w = int(w * (THUMB_LONGEST / h))
        img = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format=THUMB_FMT, quality=THUMB_QUALITY, optimize=True)
    buf.seek(0)
    return ContentFile(buf.read(), name="thumb.jpg")


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user")
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "author",
            "image_url",
            "is_published",
            "visibility",
            "likes_count",
            "comments_count",
            "created_at",
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        req = self.context.get("request")
        if getattr(obj, "image", None):
            try:
                url = obj.image.url
                return req.build_absolute_uri(url) if req else url
            except Exception:
                return None
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ["title", "body", "image", "is_published", "visibility"]

    def validate_image(self, f):
        if f is None:
            return f
        _validate_image_upload(f)
        return f


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["body"]


class PhotoSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    thumbnail_url_file = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "title", "url", "thumbnail_url", "file_url", "thumbnail_url_file", "metadata", "created_at"]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_file_url(self, obj):
        if not getattr(obj, "file", None):
            return None
        req = self.context.get("request")
        try:
            url = obj.file.url
            return req.build_absolute_uri(url) if req else url
        except Exception:
            return None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_thumbnail_url_file(self, obj):
        if not getattr(obj, "thumbnail", None):
            return None
        req = self.context.get("request")
        try:
            url = obj.thumbnail.url
            return req.build_absolute_uri(url) if req else url
        except Exception:
            return None


class PhotoCreateSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Photo
        fields = ["title", "url", "thumbnail_url", "metadata", "file"]

    def validate_file(self, f):
        if f is None:
            return f
        _validate_image_upload(f)
        return f

    def create(self, validated_data):
        img = validated_data.pop("file", None)
        instance = Photo.objects.create(**validated_data)
        if img is not None:
            # save original
            instance.file.save(img.name, img, save=False)
            # generate thumbnail
            thumb_cf = _generate_thumbnail(img)
            instance.thumbnail.save("thumb.jpg", thumb_cf, save=False)
            instance.save(update_fields=["file", "thumbnail"])
        return instance


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "is_published",
            "visibility",
            "created_at",
            "photos",
            "likes_count",
            "comments_count",
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_likes_count(self, obj):
        return getattr(obj, "likes_count", None) if hasattr(obj, "likes_count") else obj.likes.count()

    @extend_schema_field(serializers.IntegerField())
    def get_comments_count(self, obj):
        return getattr(obj, "comments_count", None) if hasattr(obj, "comments_count") else obj.comments.count()


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["title", "is_published", "visibility"]


class AlbumCommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()

    class Meta:
        model = AlbumComment
        fields = ["id", "user", "body", "created_at"]


class AlbumCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumComment
        fields = ["body"]


class FollowSerializer(serializers.ModelSerializer):
    follower = AuthorSerializer(read_only=True)
    followed = AuthorSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "followed", "status", "created_at"]
