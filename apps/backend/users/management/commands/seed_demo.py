"""
Deterministik yerel demo verisi oluşturucu.

Amaç
-----
- 25 Türkçe kullanıcı (Faker tr_TR) oluşturur/günceller.
- Küçük hacimli içerik: gönderiler, yorum/like, yapılacaklar, albüm/fotoğraflar.
- Idempotent-vari: Aynı e-posta ile var olan kullanıcılar güncellenir.

Notlar
------
- Yalnızca yerel demo için tasarlanmıştır. Üretim amaçlı değildir.
"""
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from faker import Faker

from social.models import Post, Comment, Like, Album, Photo, Follow
from todos.models import TodoList, TodoItem, TodoSubItem


RANDOM_SEED = 20250823
User = get_user_model()


class Command(BaseCommand):
    help = "Yerel demo datası üretir (25 kullanıcı + sınırlı içerik)."

    def handle(self, *args, **options):
        random.seed(RANDOM_SEED)
        Faker.seed(RANDOM_SEED)
        fake = Faker("tr_TR")

        created_users = 0
        updated_users = 0
        posts_cnt = 0
        comments_cnt = 0
        likes_cnt = 0
        lists_cnt = 0
        items_cnt = 0
        subitems_cnt = 0
        albums_cnt = 0
        photos_cnt = 0
        follows_cnt = 0

        with transaction.atomic():
            # Kullanıcıları oluştur/güncelle
            for i in range(1, 26):
                username = f"demo{i:02d}"
                email = f"{username}@example.test"
                full_name = fake.name()
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "full_name": full_name,
                    },
                )
                if created:
                    user.set_password("Demo1234!")
                    created_users += 1
                else:
                    user.email = email
                    user.full_name = full_name
                    updated_users += 1

                # Demo bayrakları
                # görünürlük: ~%60 public, %25 followers, %15 private
                r = random.random()
                if r < 0.6:
                    user.profile_privacy = "public"
                    user.is_private = False
                elif r < 0.85:
                    user.profile_privacy = "friends"
                    user.is_private = False
                else:
                    user.profile_privacy = "private"
                    user.is_private = True
                user.is_premium = random.random() < 0.15
                user.save()

            users = list(User.objects.filter(email__endswith="@example.test"))

            # Basit takip ilişkileri: herkes bir sonrakini takip etsin
            for idx, u in enumerate(users):
                target = users[(idx + 1) % len(users)]
                if target.id != u.id:
                    _, created = Follow.objects.get_or_create(
                        follower=u, followed=target, defaults={"status": "accepted"}
                    )
                    if created:
                        follows_cnt += 1

            # İçerikler
            for u in users:
                # Gönderiler 1-3
                for _ in range(random.randint(1, 3)):
                    p = Post.objects.create(
                        user=u,
                        title=fake.sentence(nb_words=5)[:60],
                        body=fake.paragraph(nb_sentences=3)[:400],
                        is_published=True,
                        visibility=random.choice(["public", "followers", "public"]),
                    )
                    posts_cnt += 1

                # Todos: 0-2 liste → 1-3 item → 0-2 subitem
                for _ in range(random.randint(0, 2)):
                    tl = TodoList.objects.create(user=u, name=fake.word().title(), kind=random.choice(["personal","work","other"]))
                    lists_cnt += 1
                    for _ in range(random.randint(1, 3)):
                        it = TodoItem.objects.create(list=tl, title=fake.sentence(nb_words=3)[:40], description=fake.sentence(nb_words=6)[:120], is_done=random.random()<0.3)
                        items_cnt += 1
                        for _ in range(random.randint(0, 2)):
                            si = TodoSubItem.objects.create(parent=it, title=fake.word().title(), is_done=random.random()<0.4)
                            subitems_cnt += 1

                # Albüm: 0-1 album, 1-3 foto
                if random.random() < 0.5:
                    al = Album.objects.create(user=u, title=f"{fake.word().title()} Albümü")
                    albums_cnt += 1
                    for _ in range(random.randint(1, 3)):
                        seed = fake.uuid4()
                        url = f"https://picsum.photos/seed/{seed}/320/240"
                        Photo.objects.create(album=al, title=fake.word().title(), url=url, thumbnail_url=url)
                        photos_cnt += 1

            # Yorumlar ve beğeniler (küçük hacimli)
            all_posts = list(Post.objects.all())
            for u in users:
                for _ in range(random.randint(0, 2)):
                    if not all_posts:
                        break
                    p = random.choice(all_posts)
                    if p.user_id != u.id or random.random() < 0.5:
                        Comment.objects.create(post=p, user=u, body=fake.sentence(nb_words=10)[:120])
                        comments_cnt += 1
                for _ in range(random.randint(0, 3)):
                    if not all_posts:
                        break
                    p = random.choice(all_posts)
                    if not Like.objects.filter(post=p, user=u).exists():
                        Like.objects.create(post=p, user=u)
                        likes_cnt += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed tamamlandı: users+ ({created_users} yeni, {updated_users} güncellendi), posts={posts_cnt}, comments={comments_cnt}, likes={likes_cnt}, todos: lists={lists_cnt}, items={items_cnt}, subitems={subitems_cnt}, albums={albums_cnt}, photos={photos_cnt}, follows={follows_cnt}"
        ))

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from social.models import Post
from todos.models import TodoItem, TodoList, TodoSubItem

NAMES = [
    "Ahmet",
    "Mehmet",
    "Ayşe",
    "Fatma",
    "Emre",
    "Elif",
    "Can",
    "Zeynep",
    "Mert",
    "Selin",
    "Ali",
    "Veli",
    "Derya",
    "Burak",
    "Ece",
    "Kerem",
    "Hakan",
    "Seda",
    "Gizem",
    "Cem",
    "Baran",
    "Deniz",
    "Sude",
    "Ömer",
    "Beril",
]


class Command(BaseCommand):
    help = "Seed deterministic demo data"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=25)
        parser.add_argument("--deterministic", action="store_true")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts.get("deterministic"):
            random.seed(42)
        User = get_user_model()
        created_users = []
        for i in range(opts["users"]):
            username = f"user{i+1}"
            full_name = NAMES[i % len(NAMES)]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "full_name": full_name,
                },
            )
            if created:
                user.set_password("password")
                user.save()
            created_users.append(user)

        # Simple posts per user
        for u in created_users:
            for j in range(2):
                Post.objects.get_or_create(
                    user=u,
                    title=f"Post {j+1} by {u.username}",
                    defaults={
                        "body": "Lorem ipsum dolor sit amet.",
                        "visibility": "public",
                    },
                )
        # Simple todos
        for u in created_users:
            tlist, _ = TodoList.objects.get_or_create(
                user=u, name=f"Starter list for {u.username}"
            )
            for k in range(3):
                item, _ = TodoItem.objects.get_or_create(
                    list=tlist, title=f"Task {k+1}"
                )
                for m in range(2):
                    TodoSubItem.objects.get_or_create(
                        parent=item, title=f"Subtask {k+1}.{m+1}"
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {len(created_users)} users with content")
        )
