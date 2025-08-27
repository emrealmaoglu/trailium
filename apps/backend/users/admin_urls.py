from django.urls import path

from .views_admin_tools import purge_non_admin_users

urlpatterns = [
    path("purge-non-admin-users/", purge_non_admin_users, name="purge_non_admin_users"),
]
