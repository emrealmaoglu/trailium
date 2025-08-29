"""
Kullanıcı serileştiricileri.

Bu modül, kullanıcıya ilişkin veri dönüşümlerini sağlar.
NumPy tarzı (Türkçe) docstring formatı kullanılmıştır.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı nesnesini API yanıtı için serileştirir.

    Returns
    -------
    dict
        Kullanıcıya ait temel alanlar (id, username, email vb.).
    """
    visibility = serializers.CharField(source="profile_privacy", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "full_name",
            "gender",
            "phone",
            "address",
            "about",
            "is_premium",
            "is_private",
            "visibility",
            "is_superuser",
            "is_staff",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Kullanıcı kayıt verilerini doğrular ve yeni kullanıcı oluşturur.

    Attributes
    ----------
    password : str
        Yazma-özel şifre alanı.

    Notes
    -----
    Şifre, `create` sırasında `set_password` ile hash'lenir.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        """Yeni kullanıcı oluşturur.

        Parameters
        ----------
        validated_data : dict
            Doğrulanmış kullanıcı kayıt verileri.

        Returns
        -------
        users.models.User
            Oluşturulan kullanıcı örneği.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Kullanıcı profil güncelleme serileştiricisi.

    Opsiyonel alanlarla kısmi güncellemeleri destekler.
    """
    visibility = serializers.ChoiceField(
        choices=("public", "friends", "private"), required=False, source="profile_privacy"
    )
    class Meta:
        model = User
        fields = [
            "email",
            "avatar",
            "full_name",
            "gender",
            "phone",
            "address",
            "about",
            "is_private",
            "is_premium",
            "visibility",
        ]
        extra_kwargs = {f: {"required": False} for f in fields}


class PasswordChangeSerializer(serializers.Serializer):
    """Şifre değiştirme isteğini doğrular.

    Attributes
    ----------
    old_password : str
        Mevcut şifre.
    new_password : str
        Yeni şifre (parola doğrulamalarına tabi).
    """

    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        """Şifre değişikliği için doğrulamaları çalıştırır.

        Parameters
        ----------
        attrs : dict
            İstekten alınan `old_password` ve `new_password` alanları.

        Returns
        -------
        dict
            Doğrulanmış alanlar.

        Raises
        ------
        serializers.ValidationError
            Eski şifre hatalıysa veya yeni şifre politikaya uymuyorsa.
        """
        user = self.context["request"].user
        if not user.check_password(attrs.get("old_password")):
            raise serializers.ValidationError({"old_password": "Incorrect password"})
        validate_password(attrs.get("new_password"), user)
        return attrs
