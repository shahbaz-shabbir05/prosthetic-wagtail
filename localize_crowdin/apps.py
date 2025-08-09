from django.apps import AppConfig


class LocalizeCrowdinConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "localize_crowdin"

    def ready(self):
        from localize_crowdin import hooks  # noqa: F401

        pass
