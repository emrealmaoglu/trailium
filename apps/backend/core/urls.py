from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", TemplateView.as_view(template_name="health.html")),
    path(
        "api/", include("users.urls")
    ),  # This will include both /api/users/ and /api/auth/
    path("api/todos/", include("todos.urls")),
    path("api/", include("social.urls")),
    path("api/admin-tools/", include("users.admin_urls")),
]
