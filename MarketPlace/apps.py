from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "MarketPlace"

    def ready(self):
        import MarketPlace.signals
