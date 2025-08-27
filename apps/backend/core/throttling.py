import logging

from django.core.cache import cache
from rest_framework.throttling import (AnonRateThrottle, ScopedRateThrottle,
                                       UserRateThrottle)

logger = logging.getLogger(__name__)


class CustomUserRateThrottle(UserRateThrottle):
    """Custom user rate limiting with better logging"""

    def allow_request(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return True

        # Get user-specific rate limit
        user_id = request.user.id
        cache_key = f"user_throttle_{user_id}"

        # Check current usage
        current_usage = cache.get(cache_key, 0)

        if current_usage >= self.rate:
            logger.warning(
                f"Rate limit exceeded for user {user_id}: {current_usage}/{self.rate}"
            )
            return False

        # Increment usage
        cache.set(cache_key, current_usage + 1, self.duration)
        return True


class CustomAnonRateThrottle(AnonRateThrottle):
    """Custom anonymous rate limiting with IP tracking"""

    def get_cache_key(self, request, view):
        # Use IP address for anonymous users
        ip = self.get_client_ip(request)
        return f"anon_throttle_{ip}"

    def get_client_ip(self, request):
        # Get real IP address (handles proxies)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class LoginRateThrottle(ScopedRateThrottle):
    """Strict rate limiting for authentication endpoints"""

    scope = "login"
    rate = "5/minute"  # 5 attempts per minute

    def get_cache_key(self, request, view):
        # Use IP address for login attempts
        ip = self.get_client_ip(request)
        return f"login_throttle_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class RegistrationRateThrottle(ScopedRateThrottle):
    """Rate limiting for user registration"""

    scope = "register"
    rate = "3/hour"  # 3 registrations per hour per IP

    def get_cache_key(self, request, view):
        ip = self.get_client_ip(request)
        return f"register_throttle_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PostCreationThrottle(ScopedRateThrottle):
    """Rate limiting for post creation"""

    scope = "post_creation"
    rate = "10/hour"  # 10 posts per hour per user

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"post_creation_throttle_user_{request.user.id}"
        else:
            ip = self.get_client_ip(request)
            return f"post_creation_throttle_ip_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CommentThrottle(ScopedRateThrottle):
    """Rate limiting for comments"""

    scope = "comment"
    rate = "30/hour"  # 30 comments per hour per user

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"comment_throttle_user_{request.user.id}"
        else:
            ip = self.get_client_ip(request)
            return f"comment_throttle_ip_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class FileUploadThrottle(ScopedRateThrottle):
    """Rate limiting for file uploads"""

    scope = "file_upload"
    rate = "20/hour"  # 20 uploads per hour per user

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"file_upload_throttle_user_{request.user.id}"
        else:
            ip = self.get_client_ip(request)
            return f"file_upload_throttle_ip_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class AdminThrottle(ScopedRateThrottle):
    """Rate limiting for admin actions"""

    scope = "admin"
    rate = "100/hour"  # 100 admin actions per hour per user

    def get_cache_key(self, request, view):
        if request.user.is_authenticated and request.user.is_staff:
            return f"admin_throttle_user_{request.user.id}"
        else:
            # Non-admin users get very strict limits
            ip = self.get_client_ip(request)
            return f"admin_throttle_ip_{ip}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


# Rate limit configuration
RATE_LIMIT_CONFIG = {
    "DEFAULT_THROTTLE_CLASSES": [
        "core.throttling.CustomUserRateThrottle",
        "core.throttling.CustomAnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/hour",  # 1000 requests per hour for authenticated users
        "anon": "100/hour",  # 100 requests per hour for anonymous users
        "login": "5/minute",  # 5 login attempts per minute per IP
        "register": "3/hour",  # 3 registrations per hour per IP
        "post_creation": "10/hour",  # 10 posts per hour per user
        "comment": "30/hour",  # 30 comments per hour per user
        "file_upload": "20/hour",  # 20 file uploads per hour per user
        "admin": "100/hour",  # 100 admin actions per hour per user
    },
    "DEFAULT_THROTTLE_SCOPE": "user",
}
