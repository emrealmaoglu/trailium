"""
Görünürlük politikaları: public / followers / private.

Kurallar
--------
- Sahip veya admin → her şeyi görebilir.
- public → herkes görebilir.
- followers → yalnızca kabul edilmiş takipçiler görebilir.
- private → yalnızca sahip (ve admin) görebilir.
"""
from typing import Iterable

from django.contrib.auth import get_user_model
from django.db.models import Q

from social.models import Follow


User = get_user_model()


def is_follower(request_user: User, target_user: User) -> bool:
    """Kullanıcı, hedef kullanıcıyı kabul edilmiş olarak takip ediyor mu?"""
    if not request_user or not request_user.is_authenticated:
        return False
    if request_user.id == getattr(target_user, "id", None):
        return True
    return Follow.objects.filter(
        follower=request_user, followed=target_user, status="accepted"
    ).exists()


def can_view_profile(request_user: User, target_user: User) -> bool:
    """Profil görünürlüğünü değerlendirir.

    - Admin/Sahip → True
    - profile_privacy == public → True
    - profile_privacy == friends (followers) → takipçi ise True
    - profile_privacy == private veya is_private True → False
    """
    if not target_user:
        return False
    if not request_user or not request_user.is_authenticated:
        return False
    if request_user.is_staff or request_user.is_superuser:
        return True
    if request_user.id == target_user.id:
        return True

    privacy = getattr(target_user, "profile_privacy", "public")
    is_private = bool(getattr(target_user, "is_private", False))

    if is_private:
        return False
    if privacy == "public":
        return True
    if privacy in ("friends", "followers"):
        return is_follower(request_user, target_user)
    if privacy == "private":
        return False
    return False


def filter_queryset_by_visibility(qs, request_user: User, owner_field: str = "user"):
    """Verilen queryset'i görünürlük politikasına göre filtreler.

    Parametreler
    -----------
    qs : QuerySet
        Sahip alanı `owner_field` olan nesneler.
    request_user : User
        İstemi yapan kullanıcı.
    owner_field : str, default "user"
        Sahip alanının adı (ör. "user").

    Dönüş
    -----
    QuerySet
        Görülebilen kayıtlarla sınırlandırılmış queryset.
    """
    if not request_user or not request_user.is_authenticated:
        return qs.none()
    if request_user.is_staff or request_user.is_superuser:
        return qs

    owner_id_field = f"{owner_field}_id"

    # İzinli sahipler: self + public kullanıcılar + kabul edilmiş takip edilenler
    public_owner_ids = User.objects.filter(
        Q(profile_privacy="public") & Q(is_private=False)
    ).values_list("id", flat=True)

    follower_owner_ids = Follow.objects.filter(
        follower=request_user, status="accepted"
    ).values_list("followed_id", flat=True)

    allowed_ids = set(public_owner_ids).union(set(follower_owner_ids))
    allowed_ids.add(request_user.id)

    return qs.filter(**{owner_id_field: list(allowed_ids)})


