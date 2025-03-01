from django.apps import AppConfig


class PenaltiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'penalties'

    def ready(self):
        import penalties.signals  # Import the signals module
