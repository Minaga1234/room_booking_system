from django.db import models
from rooms.models import Room
from django.utils.timezone import now

class Analytics(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(auto_now_add=True)  # Matches the migration
    total_bookings = models.IntegerField(default=0)
    total_checkins = models.IntegerField(default=0)
    total_cancellations = models.IntegerField(default=0)
    total_usage_time = models.FloatField(default=0.0)
    peak_hours = models.JSONField(default=dict)
    utilization_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for Room {self.room.name}"
