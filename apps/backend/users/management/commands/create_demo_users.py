import os
import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from social.models import Album, Comment, Follow, Like, Photo, Post
from todos.models import TodoItem, TodoList, TodoSubItem

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users with realistic Turkish data and content"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=25,
            help="Number of demo users to create (default: 25)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing demo users before creating new ones",
        )
        parser.add_argument(
            "--admin", action="store_true", help="Create admin user (emre/emre)"
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear_existing = options["clear"]
        create_admin = options["admin"]

        # Read configurable rates from environment
        premium_rate = float(os.getenv("DEMO_PREMIUM_RATE", "0.15"))
        private_rate = float(os.getenv("DEMO_PRIVATE_RATE", "0.10"))

        self.stdout.write(
            f"Demo rates: Premium={premium_rate:.1%}, Private={private_rate:.1%}"
        )

        if clear_existing:
            self.stdout.write("Clearing existing demo users...")
            User.objects.filter(is_staff=False).delete()
            self.stdout.write(self.style.SUCCESS("Existing demo users cleared"))

        if create_admin:
            self.create_admin_user()

        self.stdout.write(f"Creating {count} demo users...")

        with transaction.atomic():
            users = self.create_demo_users(count, premium_rate, private_rate)
            self.create_social_content(users)
            self.create_todos(users)
            self.create_follows(users)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} demo users with content!")
        )

    def create_admin_user(self):
        """Create admin user emre/emre"""
        if not User.objects.filter(username="emre").exists():
            admin_user = User.objects.create_user(
                username="emre",
                email="emre@trailium.com",
                password="emre",
                full_name="Emre Almaoğlu",
                is_staff=True,
                is_superuser=True,
                is_premium=True,
                is_private=False,
                phone="+90 555 123 4567",
                address="İstanbul, Türkiye",
                about="Trailium uygulamasının geliştiricisi",
                gender="M",
            )
            self.stdout.write(
                self.style.SUCCESS(f"Admin user created: {admin_user.username}")
            )
        else:
            self.stdout.write("Admin user already exists")

    def create_demo_users(self, count, premium_rate, private_rate):
        """Create demo users with Turkish names"""
        users = []

        # Configurable demo sources via environment variables
        avatar_base = os.getenv("DEMO_AVATAR_BASE", "https://i.pravatar.cc")

        # Turkish names data
        male_names = [
            "Ahmet",
            "Mehmet",
            "Ali",
            "Mustafa",
            "Hasan",
            "Hüseyin",
            "İbrahim",
            "Murat",
            "Ömer",
            "Yusuf",
            "Emre",
            "Can",
            "Deniz",
            "Burak",
            "Serkan",
            "Tolga",
            "Kemal",
            "Orhan",
            "Cem",
            "Tamer",
            "Volkan",
            "Erkan",
            "Erkan",
            "Serdar",
        ]

        female_names = [
            "Ayşe",
            "Fatma",
            "Zeynep",
            "Emine",
            "Hatice",
            "Elif",
            "Meryem",
            "Şeyma",
            "Esra",
            "Seda",
            "Gizem",
            "Büşra",
            "Merve",
            "Derya",
            "Selin",
            "Pınar",
            "Tuğçe",
            "Sevgi",
            "Aysel",
            "Nur",
            "Gül",
            "Sevda",
            "Hande",
            "Melis",
        ]

        surnames = [
            "Yılmaz",
            "Kaya",
            "Demir",
            "Çelik",
            "Şahin",
            "Yıldız",
            "Yıldırım",
            "Özkan",
            "Aydın",
            "Özdemir",
            "Arslan",
            "Doğan",
            "Kılıç",
            "Aslan",
            "Çetin",
            "Kurt",
            "Koç",
            "Özkan",
            "Erdoğan",
            "Güneş",
            "Şen",
            "Ergün",
            "Polat",
            "Tekin",
        ]

        companies = [
            "N2Mobil",
            "Garanti BBVA",
            "İş Bankası",
            "Akbank",
            "Yapı Kredi",
            "Türk Telekom",
            "Turkcell",
            "Vodafone",
            "THY",
            "Pegasus",
            "Borusan",
            "Koç Holding",
            "Sabancı Holding",
            "Anadolu Efes",
            "Ülker",
            "Migros",
            "Carrefour",
            "Trendyol",
            "Hepsiburada",
            "N11",
        ]

        cities = [
            "İstanbul",
            "Ankara",
            "İzmir",
            "Bursa",
            "Antalya",
            "Adana",
            "Konya",
            "Gaziantep",
            "Mersin",
            "Diyarbakır",
            "Samsun",
            "Denizli",
            "Eskişehir",
            "Trabzon",
            "Erzurum",
        ]

        for i in range(count):
            # Randomly choose gender and name
            is_male = random.choice([True, False])
            first_name = random.choice(male_names if is_male else female_names)
            surname = random.choice(surnames)
            full_name = f"{first_name} {surname}"

            # Create username from name
            username = f"{first_name.lower()}{surname.lower()}{random.randint(1, 999)}"

            # Create email
            email = f"{username}@demo.trailium.com"

            # Random phone number
            phone = f"+90 5{random.randint(30, 99)} {random.randint(100, 999)} {random.randint(1000, 9999)}"

            # Random address
            city = random.choice(cities)
            district = f"Semt {random.randint(1, 20)}"
            address = f"{district}, {city}, Türkiye"

            # Random company
            company = random.choice(companies) if random.random() > 0.3 else ""

            # Random about text
            about_texts = [
                f"{full_name} olarak {city}'de yaşıyorum.",
                f"Merhaba, ben {full_name}. {company} şirketinde çalışıyorum.",
                f"{full_name} - {city} sakini, teknoloji meraklısı.",
                f"Selam! Ben {full_name}, {company} ekibindeyim.",
                f"{full_name} - Hayatı seven biriyim.",
            ]
            about = random.choice(about_texts)

            # Random premium and private status using configurable rates
            is_premium = random.random() < premium_rate
            is_private = random.random() < private_rate

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password="demo123",  # All demo users have same password
                full_name=full_name,
                phone=phone,
                address=address,
                about=about,
                is_premium=is_premium,
                is_private=is_private,
                gender="M" if is_male else "F",
                avatar=f"{avatar_base.rstrip('/')}/150?u={username}&img={random.randint(1, 70)}",
            )

            users.append(user)
            self.stdout.write(f"Created user: {full_name} ({username})")

        return users

    def create_social_content(self, users):
        """Create posts, comments, likes, albums, and photos"""
        self.stdout.write("Creating social content...")
        photo_base = os.getenv("DEMO_PHOTO_BASE", "https://picsum.photos")

        # Create posts
        post_texts = [
            "Bugün harika bir gün! ☀️",
            "Yeni projeler üzerinde çalışıyorum 💻",
            "Kahve molası zamanı ☕",
            "Hava çok güzel, dışarı çıkmak istiyorum 🌸",
            "Yeni bir kitap okumaya başladım 📚",
            "Müzik dinliyorum 🎵",
            "Spor yapmak çok önemli 💪",
            "Arkadaşlarımla buluşacağım 👥",
            "Yemek yapmayı seviyorum 👨‍🍳",
            "Seyahat etmeyi çok seviyorum ✈️",
        ]

        for user in users:
            # Create 1-3 posts per user
            for _ in range(random.randint(1, 3)):
                post = Post.objects.create(
                    user=user,
                    title=random.choice(post_texts),
                    body=f"{random.choice(post_texts)} {random.choice(post_texts)}",
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                )

                # Add likes
                for liker in random.sample(
                    users, min(random.randint(0, 5), len(users))
                ):
                    if liker != user:
                        Like.objects.get_or_create(user=liker, post=post)

                # Add comments
                for commenter in random.sample(
                    users, min(random.randint(0, 3), len(users))
                ):
                    if commenter != user:
                        Comment.objects.create(
                            user=commenter,
                            post=post,
                            body=random.choice(
                                [
                                    "Harika! 👍",
                                    "Çok güzel",
                                    "Beğendim",
                                    "Teşekkürler",
                                    "Harika bir paylaşım",
                                    "Çok doğru",
                                    "Katılıyorum",
                                ]
                            ),
                            created_at=datetime.now()
                            - timedelta(days=random.randint(0, 20)),
                        )

            # Create albums
            for _ in range(random.randint(0, 2)):
                album = Album.objects.create(
                    user=user,
                    title=f"{user.full_name}'nin Albümü {random.randint(1, 5)}",
                    created_at=datetime.now() - timedelta(days=random.randint(0, 25)),
                )

                # Add photos to album
                for _ in range(random.randint(1, 5)):
                    Photo.objects.create(
                        album=album,
                        title=f"Fotoğraf {random.randint(1, 100)}",
                        url=f"{photo_base.rstrip('/')}/400/300?random={random.randint(1, 1000)}",
                        thumbnail_url=f"{photo_base.rstrip('/')}/200/150?random={random.randint(1, 1000)}",
                        created_at=datetime.now()
                        - timedelta(days=random.randint(0, 20)),
                    )

    def create_todos(self, users):
        """Create todo lists and items"""
        self.stdout.write("Creating todos...")

        todo_titles = [
            "Günlük Görevler",
            "Haftalık Plan",
            "Proje Görevleri",
            "Kişisel Hedefler",
            "Alışveriş Listesi",
            "Okuma Listesi",
            "Spor Hedefleri",
            "Yemek Planı",
        ]

        todo_items = [
            "E-postaları kontrol et",
            "Toplantıya hazırlan",
            "Raporu tamamla",
            "Dokümanları güncelle",
            "Müşteri ile görüş",
            "Sunumu hazırla",
            "Veritabanını yedekle",
            "Kodları test et",
            "Dokümantasyon yaz",
            "Ekip toplantısı",
            "Proje planını gözden geçir",
            "Bütçeyi kontrol et",
        ]

        for user in users:
            # Create 1-2 todo lists per user
            for _ in range(random.randint(1, 2)):
                todo_list = TodoList.objects.create(
                    user=user,
                    name=random.choice(todo_titles),
                    created_at=datetime.now() - timedelta(days=random.randint(0, 20)),
                )

                # Create 3-8 todo items per list
                for _ in range(random.randint(3, 8)):
                    item = TodoItem.objects.create(
                        list=todo_list,
                        title=random.choice(todo_items),
                        description=f"Detay: {random.choice(todo_items)}",
                        due_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                        created_at=datetime.now()
                        - timedelta(days=random.randint(0, 15)),
                    )

                    # Create 1-3 sub-items per todo item
                    for _ in range(random.randint(1, 3)):
                        TodoSubItem.objects.create(
                            parent=item,
                            title=f"Alt görev {random.randint(1, 10)}",
                            is_done=random.choice([True, False]),
                            created_at=datetime.now()
                            - timedelta(days=random.randint(0, 10)),
                        )

    def create_follows(self, users):
        """Create follow relationships between users"""
        self.stdout.write("Creating follow relationships...")

        for user in users:
            # Each user follows 3-8 other users
            follow_count = random.randint(3, 8)
            potential_follows = [u for u in users if u != user]

            if len(potential_follows) >= follow_count:
                followed_users = random.sample(potential_follows, follow_count)

                for followed_user in followed_users:
                    # 80% chance of accepted follow, 20% chance of pending
                    status = "accepted" if random.random() > 0.2 else "pending"

                    Follow.objects.get_or_create(
                        follower=user,
                        followed=followed_user,
                        defaults={"status": status},
                    )

        self.stdout.write("Follow relationships created successfully!")
