from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (ChangePasswordView, LoginView, LogoutView, RegisterViewSet,
                    UserViewSet)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"auth", RegisterViewSet, basename="auth")

urlpatterns = [
    *router.urls,
    path("auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="token_logout"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
]
