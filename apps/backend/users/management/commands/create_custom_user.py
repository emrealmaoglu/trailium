import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from social.models import Album, Comment, Follow, Like, Photo, Post
from todos.models import TodoItem, TodoList, TodoSubItem

User = get_user_model()


class Command(BaseCommand):
    help = "Create a custom user with specified content and photos from JSONPlaceholder API"

    def add_arguments(self, parser):
        # User profile arguments
        parser.add_argument(
            "--username", type=str, required=False, help="Username for the user"
        )
        parser.add_argument(
            "--email", type=str, required=False, help="Email for the user"
        )
        parser.add_argument(
            "--full_name", type=str, required=False, help="Full name of the user"
        )
        parser.add_argument("--phone", type=str, required=False, help="Phone number")
        parser.add_argument("--city", type=str, required=False, help="City")
        parser.add_argument(
            "--gender", type=str, choices=["M", "F", "O"], required=False, help="Gender"
        )
        parser.add_argument(
            "--is_premium",
            type=str,
            choices=["true", "false"],
            default="false",
            help="Premium status",
        )
        parser.add_argument(
            "--is_private",
            type=str,
            choices=["true", "false"],
            default="false",
            help="Private account",
        )
        parser.add_argument("--avatar_url", type=str, required=False, help="Avatar URL")
        parser.add_argument("--company", type=str, default="", help="Company name")
        parser.add_argument("--about", type=str, default="", help="About text")

        # JSON data support
        parser.add_argument(
            "--data", type=str, required=False, help="JSON data for user creation"
        )

        # Posts arguments (dynamic)
        for i in range(5):  # Support up to 5 posts
            parser.add_argument(
                f"--post_title_{i}", type=str, help=f"Title for post {i+1}"
            )
            parser.add_argument(
                f"--post_body_{i}", type=str, help=f"Body for post {i+1}"
            )

        # Todo lists arguments (dynamic)
        for i in range(3):  # Support up to 3 todo lists
            parser.add_argument(
                f"--todo_list_{i}_title", type=str, help=f"Title for todo list {i+1}"
            )
            for j in range(8):  # Support up to 8 items per list
                parser.add_argument(
                    f"--todo_list_{i}_item_{j}_title",
                    type=str,
                    help=f"Title for item {j+1} in list {i+1}",
                )
                parser.add_argument(
                    f"--todo_list_{i}_item_{j}_desc",
                    type=str,
                    help=f"Description for item {j+1} in list {i+1}",
                )
                for k in range(3):  # Support up to 3 sub-items per item
                    parser.add_argument(
                        f"--todo_list_{i}_item_{j}_sub_{k}",
                        type=str,
                        help=f"Sub-item {k+1} for item {j+1} in list {i+1}",
                    )

        # Albums arguments (dynamic)
        for i in range(3):  # Support up to 3 albums
            parser.add_argument(
                f"--album_{i}_title", type=str, help=f"Title for album {i+1}"
            )
            for j in range(5):  # Support up to 5 photos per album
                parser.add_argument(
                    f"--album_{i}_photo_{j}_title",
                    type=str,
                    help=f"Title for photo {j+1} in album {i+1}",
                )
                parser.add_argument(
                    f"--album_{i}_photo_{j}_url",
                    type=str,
                    help=f"URL for photo {j+1} in album {i+1}",
                )
                parser.add_argument(
                    f"--album_{i}_photo_{j}_thumb",
                    type=str,
                    help=f"Thumbnail URL for photo {j+1} in album {i+1}",
                )

    def handle(self, *args, **options):
        try:
            # Check if JSON data is provided
            if options.get("data"):
                # Parse JSON data
                import json

                data = json.loads(options["data"])

                # Extract data from JSON
                profile = data["profile"]
                posts = data["posts"]
                todos = data["todos"]
                albums = data["albums"]

                # Create user with JSON data
                user = self.create_user_from_json(profile)
                if user:
                    self.create_posts_from_json(user, posts)
                    self.create_todos_from_json(user, todos)
                    self.create_albums_from_json(user, albums)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Kullanıcı başarıyla oluşturuldu: {user.username}"
                        )
                    )
                else:
                    self.stdout.write(self.style.ERROR("❌ Kullanıcı oluşturulamadı!"))
            else:
                # Use individual arguments (existing logic)
                with transaction.atomic():
                    # Create user
                    user = self.create_user(options)
                    self.stdout.write(f"✅ User created: {user.username}")

                    # Create posts
                    posts = self.create_posts(user, options)
                    self.stdout.write(f"✅ Created {len(posts)} posts")

                    # Create todos
                    todos = self.create_todos(user, options)
                    self.stdout.write(f"✅ Created {len(todos)} todo lists")

                    # Create albums and photos
                    albums = self.create_albums(user, options)
                    self.stdout.write(f"✅ Created {len(albums)} albums")

                    # Create some random follows (optional)
                    self.create_random_follows(user)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"🎉 Custom user {user.username} created successfully!"
                        )
                    )
                    self.stdout.write(f"📱 Login: {user.username} / demo123")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Hata: {str(e)}"))
            raise

    def create_user(self, options):
        """Create the user with specified profile"""
        # Check if user already exists
        if User.objects.filter(username=options["username"]).exists():
            raise CommandError(
                f'User with username {options["username"]} already exists'
            )

        if User.objects.filter(email=options["email"]).exists():
            raise CommandError(f'User with email {options["email"]} already exists')

        # Create address
        address = f"{options['city']}, Türkiye"
        if options["company"]:
            address = f"{options['company']}, {address}"

        # Create about text
        about = options["about"]
        if not about:
            about = f"{options['full_name']} olarak {options['city']}'de yaşıyorum."
            if options["company"]:
                about += f" {options['company']} şirketinde çalışıyorum."

        user = User.objects.create_user(
            username=options["username"],
            email=options["email"],
            password="demo123",  # Default password
            full_name=options["full_name"],
            phone=options["phone"],
            address=address,
            about=about,
            is_premium=options["is_premium"] == "true",
            is_private=options["is_private"] == "true",
            gender=options["gender"],
            avatar=options["avatar_url"],
        )

        return user

    def create_user_from_json(self, profile_data):
        """Create user from JSON profile data"""
        try:
            # Check if user already exists
            if User.objects.filter(username=profile_data["username"]).exists():
                self.stdout.write(
                    f'⚠️ Kullanıcı {profile_data["username"]} zaten mevcut.'
                )
                return None

            if User.objects.filter(email=profile_data["email"]).exists():
                self.stdout.write(f'⚠️ Kullanıcı {profile_data["email"]} zaten mevcut.')
                return None

            # Create address
            address = f"{profile_data['city']}, Türkiye"
            if profile_data["company"]:
                address = f"{profile_data['company']}, {address}"

            # Create about text
            about = profile_data["about"]
            if not about:
                about = f"{profile_data['full_name']} olarak {profile_data['city']}'de yaşıyorum."
                if profile_data["company"]:
                    about += f" {profile_data['company']} şirketinde çalışıyorum."

            user = User.objects.create_user(
                username=profile_data["username"],
                email=profile_data["email"],
                password="demo123",  # Default password
                full_name=profile_data["full_name"],
                phone=profile_data["phone"],
                address=address,
                about=about,
                is_premium=profile_data["is_premium"] == "true",
                is_private=profile_data["is_private"] == "true",
                gender=profile_data["gender"],
                avatar=profile_data["avatar_url"],
            )

            self.stdout.write(f"✅ Kullanıcı oluşturuldu: {user.username}")
            return user

        except Exception as e:
            self.stdout.write(f"❌ Kullanıcı oluşturulamadı: {e}")
            return None

    def create_posts(self, user, options):
        """Create posts for the user"""
        posts = []

        # Create posts from arguments
        for i in range(5):
            title = options.get(f"post_title_{i}")
            body = options.get(f"post_body_{i}")

            if title and body:
                post = Post.objects.create(user=user, title=title, body=body)
                posts.append(post)

                # Add random engagement
                self.add_random_post_engagement(post)

        return posts

    def create_posts_from_json(self, user, posts):
        """Create posts from JSON data"""
        for post_data in posts:
            try:
                Post.objects.create(
                    user=user, title=post_data["title"], body=post_data["body"]
                )
                self.stdout.write(f'📝 Post oluşturuldu: {post_data["title"]}')
            except Exception as e:
                self.stdout.write(f"❌ Post oluşturulamadı: {e}")

    def create_todos(self, user, options):
        """Create todo lists and items for the user"""
        todos = []

        # Create todo lists from arguments
        for i in range(3):
            list_title = options.get(f"todo_list_{i}_title")
            if not list_title:
                continue

            todo_list = TodoList.objects.create(user=user, name=list_title)
            todos.append(todo_list)

            # Create items for this list
            for j in range(8):
                item_title = options.get(f"todo_list_{i}_item_{j}_title")
                item_desc = options.get(f"todo_list_{i}_item_{j}_desc")

                if not item_title:
                    continue

                item = TodoItem.objects.create(
                    list=todo_list,
                    title=item_title,
                    description=item_desc or f"Description for {item_title}",
                )

                # Create sub-items
                for k in range(3):
                    sub_title = options.get(f"todo_list_{i}_item_{j}_sub_{k}")
                    if sub_title:
                        TodoSubItem.objects.create(parent=item, title=sub_title)

        return todos

    def create_todos_from_json(self, user, todos):
        """Create todos from JSON data"""
        for todo_data in todos:
            try:
                # Create todo list
                todo_list = TodoList.objects.create(user=user, name=todo_data["title"])
                self.stdout.write(f'✅ Todo listesi oluşturuldu: {todo_data["title"]}')

                # Create todo items
                for item_data in todo_data["items"]:
                    item = TodoItem.objects.create(
                        list=todo_list,
                        title=item_data["task"],
                        description=item_data["description"],
                    )

                    # Create sub-items
                    for subtask in item_data["subtasks"]:
                        TodoSubItem.objects.create(parent=item, title=subtask)

            except Exception as e:
                self.stdout.write(f"❌ Todo oluşturulamadı: {e}")

    def create_albums(self, user, options):
        """Create albums and photos for the user"""
        albums = []

        # Create albums from arguments
        for i in range(3):
            album_title = options.get(f"album_{i}_title")
            if not album_title:
                continue

            album = Album.objects.create(user=user, title=album_title)
            albums.append(album)

            # Create photos for this album
            for j in range(5):
                photo_title = options.get(f"album_{i}_photo_{j}_title")
                photo_url = options.get(f"album_{i}_photo_{j}_url")
                photo_thumb = options.get(f"album_{i}_photo_{j}_thumb")

                if not photo_title:
                    continue

                # Generate gender-appropriate photo URLs if not provided
                if not photo_url:
                    photo_url, photo_thumb = self.get_gender_appropriate_photo_urls(
                        user.gender, hash(f"{album_title}_{photo_title}")
                    )

                Photo.objects.create(
                    album=album,
                    title=photo_title,
                    url=photo_url,
                    thumbnail_url=photo_thumb or photo_url,
                )

        return albums

    def create_albums_from_json(self, user, albums):
        """Create albums from JSON data"""
        for album_data in albums:
            try:
                # Create album
                album = Album.objects.create(user=user, title=album_data["title"])
                self.stdout.write(f'📸 Albüm oluşturuldu: {album_data["title"]}')

                # Create photos with gender-appropriate URLs
                for photo_title in album_data["photos"]:
                    photo_url = self.get_gender_appropriate_photo_urls(
                        user.gender, hash(photo_title)
                    )
                    Photo.objects.create(
                        album=album,
                        title=photo_title,
                        url=photo_url,
                        thumbnail_url=photo_url,
                    )

            except Exception as e:
                self.stdout.write(f"❌ Albüm oluşturulamadı: {e}")

    def add_random_post_engagement(self, post):
        """Add random likes and comments to a post"""
        # Get some random users for engagement
        other_users = list(User.objects.exclude(id=post.user.id)[:5])

        # Add likes
        for liker in other_users:
            if random.random() > 0.5:  # 50% chance
                Like.objects.get_or_create(user=liker, post=post)

        # Add comments
        comment_texts = [
            "Harika bir paylaşım! 👍",
            "Çok güzel",
            "Beğendim",
            "Teşekkürler",
            "Harika!",
            "Çok doğru",
            "Katılıyorum",
            "Güzel yazı",
        ]

        for commenter in other_users:
            if random.random() > 0.7:  # 30% chance
                Comment.objects.create(
                    user=commenter,
                    post=post,
                    body=random.choice(comment_texts),
                    created_at=datetime.now() - timedelta(days=random.randint(0, 20)),
                )

    def create_random_follows(self, user):
        """Create some random follow relationships"""
        other_users = list(User.objects.exclude(id=user.id)[:10])

        # User follows some others
        for followed_user in random.sample(other_users, min(5, len(other_users))):
            Follow.objects.get_or_create(
                follower=user,
                followed=followed_user,
                defaults={"status": "accepted" if random.random() > 0.2 else "pending"},
            )

        # Some others follow the user
        for follower_user in random.sample(other_users, min(3, len(other_users))):
            Follow.objects.get_or_create(
                follower=follower_user,
                followed=user,
                defaults={"status": "accepted" if random.random() > 0.2 else "pending"},
            )

    def get_gender_appropriate_photo_urls(self, gender, seed):
        """Generate gender-appropriate photo URLs"""
        # Cinsiyete uygun fotoğraf kategorileri
        if gender == "M":
            # Erkekler için: iş, spor, araba, teknoloji temalı
            categories = ["business", "sports", "cars", "technology", "architecture"]
            colors = ["4a90e2", "50c878", "708090", "2e8b57", "4682b4"]
        elif gender == "F":
            # Kadınlar için: moda, güzellik, sanat, doğa temalı
            categories = ["fashion", "beauty", "art", "nature", "flowers"]
            colors = ["ff69b4", "da70d6", "ffd700", "ff1493", "c71585"]
        else:
            # Nötr/Diğer için: genel, soyut, mimari temalı
            categories = ["abstract", "minimal", "geometric", "modern", "vintage"]
            colors = ["ffa500", "8b4513", "f5f5dc", "cd853f", "d2691e"]

        # Rastgele kategori ve renk seç
        category = random.choice(categories)
        color = random.choice(colors)

        # Seed'e göre tutarlı fotoğraflar oluştur
        import hashlib

        hash_seed = hashlib.md5(f"{seed}_{category}_{color}".encode()).hexdigest()[:8]

        # Picsum Photos ile cinsiyete uygun fotoğraflar
        photo_url = f"https://picsum.photos/400/300?random={hash_seed}&blur=1"
        thumb_url = f"https://picsum.photos/200/150?random={hash_seed}&blur=1"

        return photo_url, thumb_url
