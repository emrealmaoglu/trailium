from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def health(_request):
    """
    Basit sağlık kontrol ucu.

    Neden?
    -------
    Servisin ayakta olup olmadığını dışarıya hızlıca göstermek.

    Nasıl?
    ------
    Basit bir JSON döner; CI/monitoring ve frontend bu ucu ping'ler.

    Sonuç?
    ------
    200 OK ile {"status":"ok","service":"trailium"} beklenir.
    """
    return JsonResponse({"status": "ok", "service": "trailium"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health),
    path("api/", include("users.urls")),
    path("api/", include("todos.urls")),
    path("api/", include("social.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
