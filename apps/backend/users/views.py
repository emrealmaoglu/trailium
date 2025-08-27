from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return response.Response(UserSerializer(request.user).data)


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
            return response.Response({"detail": "refresh is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            # even if invalid, respond 205 to clear client state
            return response.Response(status=status.HTTP_205_RESET_CONTENT)
        return response.Response(status=status.HTTP_205_RESET_CONTENT)


