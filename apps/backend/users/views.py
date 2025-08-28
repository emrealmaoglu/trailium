import json

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from rest_framework import (decorators, filters, permissions, response, status,
                            viewsets)
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import serializers

from .serializers import (PasswordChangeSerializer, ProfileUpdateSerializer,
                          RegisterSerializer, UserSerializer)

User = get_user_model()


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    rememberMe = serializers.BooleanField(required=False)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


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

    @extend_schema(request=TokenPairSerializer, responses={205: OpenApiResponse(None)})
    def post(self, request):

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

    @extend_schema(request=LoginRequestSerializer, responses={200: TokenPairSerializer, 401: OpenApiResponse(None)})
    def post(self, request):
        from datetime import timedelta

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

    @extend_schema(request=PasswordChangeSerializer, responses={204: OpenApiResponse(None)})
    def post(self, request):
        ser = PasswordChangeSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        user = request.user
        user.set_password(ser.validated_data["new_password"])
        user.save(update_fields=["password"])
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class SetSecureCookiesView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=TokenPairSerializer, responses={200: MessageSerializer})
    def post(self, request):
        """Set httpOnly cookies for JWT tokens"""
        try:
            data = request.data if isinstance(request.data, dict) else {}
            access_token = data.get("access")
            refresh_token = data.get("refresh")

            if not access_token or not refresh_token:
                return Response(
                    {"error": "Missing tokens"}, status=status.HTTP_400_BAD_REQUEST
                )

            response = Response({"message": "Cookies set successfully"})

            # Set httpOnly, secure cookies
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=3600,
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=7 * 24 * 3600,
            )

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClearSecureCookiesView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=None, responses={200: MessageSerializer})
    def post(self, request):
        """Clear JWT token cookies"""
        response = Response({"message": "Cookies cleared successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
