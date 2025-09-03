from rest_framework.throttling import UserRateThrottle


class PremiumUserRateThrottle(UserRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return super().get_cache_key(request, view)
        # Use premium scope if user is premium
        if getattr(request.user, "is_premium", False):
            self.scope = "premium"
        else:
            self.scope = "user"
        return super().get_cache_key(request, view)
