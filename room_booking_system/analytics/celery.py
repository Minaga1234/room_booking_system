from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')

app = Celery('room_booking_system')

# Using a string here means the worker doesn't need to serialize
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')