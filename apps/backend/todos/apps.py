from django.apps import AppConfig


class TodosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "todos"

    def ready(self):
        # Sinyalleri bağla
        from . import signals  # noqa: F401
