import os
from django.core.wsgi import get_wsgi_application

# Set the correct path to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')

application = get_wsgi_application()
