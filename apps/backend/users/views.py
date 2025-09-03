from django.contrib.auth import get_user_model
from rest_framework import (decorators, filters, permissions, response, status,
                            viewsets)
from rest_framework.views import APIView

from .serializers import (PasswordChangeSerializer, ProfileUpdateSerializer,
                          RegisterSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "full_name"]
    ordering_fields = ["id", "username"]

    def get_permissions(self):
        if self.action == "list":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["get", "patch", "delete"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return response.Response(UserSerializer(request.user).data)
        if request.method == "PATCH":
            ser = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
            return response.Response(UserSerializer(request.user).data)
        # DELETE => soft delete
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @decorators.action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return response.Response(UserSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = request.data.get("refresh")
        if not refresh:
            return response.Response(
                {"detail": "refresh is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            # even if invalid, respond 205 to clear client state
            return response.Response(status=status.HTTP_205_RESET_CONTENT)
        return response.Response(status=status.HTTP_205_RESET_CONTENT)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from datetime import timedelta

        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken

        username = request.data.get("username")
        password = request.data.get("password")
        remember_me = bool(request.data.get("rememberMe"))

        if not username or not password:
            return response.Response(
                {"detail": "username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return response.Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        # Adjust refresh lifetime based on remember_me (e.g., 1 day vs 30 days)
        refresh.set_exp(
            lifetime=timedelta(days=30) if remember_me else timedelta(hours=8)
        )

        return response.Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = PasswordChangeSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        user = request.user
        user.set_password(ser.validated_data["new_password"])
        user.save(update_fields=["password"])
        return response.Response(status=status.HTTP_204_NO_CONTENT)
