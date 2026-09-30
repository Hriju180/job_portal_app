from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Import here (not at the top) to avoid circular imports at startup.
        import accounts.signals  # noqa: F401