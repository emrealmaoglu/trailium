import os

from django.contrib import admin
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Health check endpoint for monitoring and deployment verification"""
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "checks": {},
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Cache check
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            health_status["checks"]["cache"] = "healthy"
        else:
            health_status["checks"]["cache"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["cache"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Environment check
    health_status["checks"]["environment"] = "healthy"
    if (
        not os.environ.get("SECRET_KEY")
        or os.environ.get("SECRET_KEY") == "django-insecure-your-secret-key-here"
    ):
        health_status["checks"]["environment"] = "unhealthy: SECRET_KEY not set"
        health_status["status"] = "unhealthy"

    # Set appropriate HTTP status
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JsonResponse(health_status, status=status_code)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("todos.urls")),
    path("api/", include("social.urls")),
    path("health/", health_check, name="health_check"),
]
