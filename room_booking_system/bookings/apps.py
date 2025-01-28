# bookings/apps.py

from django.apps import AppConfig

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        # Import signals to ensure they are connected
        import bookings.signals
