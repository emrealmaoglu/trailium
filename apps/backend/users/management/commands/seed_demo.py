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
