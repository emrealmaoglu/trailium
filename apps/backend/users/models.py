from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # AbstractUser already has: username, password, email, first_name, last_name
    avatar = models.URLField(blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=32, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    about = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.username
