import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    # Gender choices
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    # Privacy choices
    PRIVACY_CHOICES = [
        ("public", "Public"),
        ("friends", "Friends only"),
        ("private", "Private"),
    ]

    # AbstractUser already has: username, password, email, first_name, last_name

    # Profile fields
    avatar = models.URLField(
        blank=True, max_length=500, help_text="Profile picture URL"
    )

    full_name = models.CharField(
        max_length=255,
        blank=True,
        validators=[
            MinLengthValidator(2, "Full name must be at least 2 characters long.")
        ],
        help_text="User's full name",
    )

    gender = models.CharField(
        max_length=32,
        blank=True,
        choices=GENDER_CHOICES,
        help_text="User's gender identity",
    )

    # Phone validation
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Phone number with country code",
    )

    # Address with validation
    address = models.TextField(
        blank=True, max_length=1000, help_text="User's address (max 1000 characters)"
    )

    # About section
    about = models.TextField(
        blank=True,
        max_length=2000,
        help_text="User's bio or description (max 2000 characters)",
    )

    # Premium and privacy settings
    is_premium = models.BooleanField(
        default=False, help_text="Whether user has premium subscription"
    )

    is_private = models.BooleanField(
        default=False, help_text="Whether user's profile is private"
    )

    # Privacy level for different content
    profile_privacy = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default="public",
        help_text="Privacy level for profile information",
    )

    # Account security
    email_verified = models.BooleanField(
        default=False, help_text="Whether email has been verified"
    )

    phone_verified = models.BooleanField(
        default=False, help_text="Whether phone number has been verified"
    )

    # Account status
    is_active = models.BooleanField(default=True, help_text="Whether account is active")

    # Safe timestamps with defaults for existing rows
    created_at = models.DateTimeField(
        default=timezone.now, help_text="When the user account was created"
    )

    updated_at = models.DateTimeField(
        default=timezone.now, help_text="When the user account was last updated"
    )

    # Meta information
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

        # Indexes for performance
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_premium"]),
            models.Index(fields=["is_private"]),
            models.Index(fields=["date_joined"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self) -> str:
        return self.username

    def clean(self):
        """Custom validation"""
        super().clean()

        # Validate email format
        if self.email:
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, self.email):
                raise ValidationError({"email": "Enter a valid email address."})

        # Validate username format
        username_regex = r"^[a-zA-Z0-9_]{3,30}$"
        if not re.match(username_regex, self.username):
            raise ValidationError(
                {
                    "username": "Username must be 3-30 characters long and contain only letters, numbers, and underscores."
                }
            )

        # Validate full name if provided
        if self.full_name:
            if len(self.full_name.strip()) < 2:
                raise ValidationError(
                    {"full_name": "Full name must be at least 2 characters long."}
                )

            # Check for inappropriate content
            inappropriate_words = ["admin", "root", "system", "test", "demo"]
            if any(word in self.full_name.lower() for word in inappropriate_words):
                raise ValidationError({"full_name": "This name is not allowed."})

    def save(self, *args, **kwargs):
        """Custom save method with validation"""
        self.clean()

        # Ensure username is lowercase
        self.username = self.username.lower()

        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower()

        # Set full name from first and last name if not provided
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()

        # Set timestamps for new users
        if not self.pk:  # New user
            self.created_at = timezone.now()

        self.updated_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Get display name for UI"""
        return self.full_name or self.username

    @property
    def initials(self):
        """Get user initials for avatar"""
        if self.full_name:
            names = self.full_name.split()
            if len(names) >= 2:
                return f"{names[0][0]}{names[-1][0]}".upper()
            return names[0][0].upper()
        return self.username[0].upper()

    @property
    def is_verified(self):
        """Check if user has verified contact methods"""
        return self.email_verified or self.phone_verified

    def get_public_profile(self):
        """Get public profile data based on privacy settings"""
        if self.profile_privacy == "private":
            return {
                "id": self.id,
                "username": self.username,
                "is_premium": self.is_premium,
                "is_private": True,
            }

        profile = {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name if self.profile_privacy == "public" else None,
            "is_premium": self.is_premium,
            "is_private": self.is_private,
            "created_at": self.created_at,
        }

        if self.profile_privacy == "public":
            profile.update(
                {
                    "avatar": self.avatar,
                    "about": self.about,
                    "last_login": self.last_login,
                }
            )

        return profile
