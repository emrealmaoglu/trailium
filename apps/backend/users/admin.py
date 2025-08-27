from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # List display
    list_display = [
        "username",
        "email",
        "full_name",
        "is_premium",
        "is_private",
        "is_active",
        "is_staff",
        "created_at",
        "last_login",
    ]

    # List filter
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "is_premium",
        "is_private",
        "profile_privacy",
        "gender",
        "email_verified",
        "phone_verified",
        "created_at",
        "date_joined",
        "last_login",
    ]

    # Search fields
    search_fields = ["username", "email", "full_name", "phone"]

    # Readonly fields
    readonly_fields = [
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
        "password_changed",
        "profile_link",
    ]

    # Fieldsets for add/edit forms
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal Information",
            {"fields": ("first_name", "last_name", "full_name", "email", "avatar")},
        ),
        ("Contact Details", {"fields": ("phone", "address", "gender")}),
        (
            "Profile",
            {"fields": ("about", "is_premium", "is_private", "profile_privacy")},
        ),
        (
            "Account Status",
            {"fields": ("is_active", "email_verified", "phone_verified")},
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (
            "Important Dates",
            {
                "fields": ("created_at", "updated_at", "date_joined", "last_login"),
                "classes": ("collapse",),
            },
        ),
    )

    # Add form fieldsets
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
        (
            "Personal Information",
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "full_name"),
            },
        ),
    )

    # Ordering
    ordering = ["-created_at"]

    # List per page
    list_per_page = 25

    # Actions
    actions = ["make_premium", "make_regular", "verify_users", "deactivate_users"]

    def profile_link(self, obj):
        """Generate a link to the user's profile"""
        if obj.id:
            url = reverse("admin:users_user_change", args=[obj.id])
            return format_html('<a href="{}">View Profile</a>', url)
        return "N/A"

    profile_link.short_description = "Profile Link"

    def password_changed(self, obj):
        """Show when password was last changed"""
        if obj.password:
            return "Yes"
        return "No"

    password_changed.short_description = "Password Set"

    def make_premium(self, request, queryset):
        """Make selected users premium"""
        updated = queryset.update(is_premium=True)
        self.message_user(request, f"Successfully made {updated} user(s) premium.")

    make_premium.short_description = "Make selected users premium"

    def make_regular(self, request, queryset):
        """Make selected users regular (non-premium)"""
        updated = queryset.update(is_premium=False)
        self.message_user(
            request, f"Successfully made {updated} user(s) regular users."
        )

    make_regular.short_description = "Make selected users regular"

    def verify_users(self, request, queryset):
        """Verify selected users' email and phone"""
        updated = queryset.update(email_verified=True, phone_verified=True)
        self.message_user(request, f"Successfully verified {updated} user(s).")

    verify_users.short_description = "Verify selected users"

    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} user(s).")

    deactivate_users.short_description = "Deactivate selected users"

    # Custom methods for display
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related()

    def get_list_display(self, request):
        """Customize list display based on user permissions"""
        list_display = list(super().get_list_display(request))

        # Add premium indicator for staff users
        if request.user.is_staff:
            if "premium_indicator" not in list_display:
                list_display.append("premium_indicator")

        return list_display

    def premium_indicator(self, obj):
        """Show premium status with icon"""
        if obj.is_premium:
            return mark_safe('<span style="color: gold;">⭐ Premium</span>')
        return mark_safe('<span style="color: #666;">Regular</span>')

    premium_indicator.short_description = "Premium Status"

    # Custom admin methods
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of superusers"""
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Custom change permission logic"""
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)


# Customize admin site
admin.site.site_header = "Trailium Administration"
admin.site.site_title = "Trailium Admin"
admin.site.index_title = "Welcome to Trailium Administration"
