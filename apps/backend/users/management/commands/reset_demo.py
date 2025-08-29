"""
Demo verisini temizler (seed_demo tarafından oluşturulanları).

Strateji
--------
- demoNN@example.test deseni ile eşleşen kullanıcıları ve bağlı içerikleri siler.
- Güvenli sıralama: photo → album → comment → like → todo sub/item/list → post → user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from social.models import Post, Comment, Like, Album, Photo, Follow
from todos.models import TodoList, TodoItem, TodoSubItem


User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo verilerini temizler."

    def handle(self, *args, **options):
        users = list(User.objects.filter(email__endswith="@example.test"))

        photo_del = Photo.objects.filter(album__user__in=users).delete()[0]
        album_del = Album.objects.filter(user__in=users).delete()[0]

        comment_del = Comment.objects.filter(post__user__in=users).delete()[0]
        like_del = Like.objects.filter(post__user__in=users).delete()[0]

        sub_del = TodoSubItem.objects.filter(parent__list__user__in=users).delete()[0]
        item_del = TodoItem.objects.filter(list__user__in=users).delete()[0]
        list_del = TodoList.objects.filter(user__in=users).delete()[0]

        post_del = Post.objects.filter(user__in=users).delete()[0]

        # Remove follow relations among demo users
        Follow.objects.filter(follower__in=users).delete()
        Follow.objects.filter(followed__in=users).delete()

        user_del = User.objects.filter(id__in=[u.id for u in users]).delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f"Silindi: photos={photo_del}, albums={album_del}, comments={comment_del}, likes={like_del}, subitems={sub_del}, items={item_del}, lists={list_del}, posts={post_del}, users={user_del}"
        ))


