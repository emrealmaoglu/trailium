from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # AbstractUser already has: username, password, email, first_name, last_name
    avatar = models.URLField(blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=32, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    about = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.username


