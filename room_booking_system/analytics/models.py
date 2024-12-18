from django.db import models
from rooms.models import Room

class Analytics(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_bookings = models.IntegerField(default=0)
    total_checkins = models.IntegerField(default=0)
    peak_hours = models.TextField(null=True, blank=True)  # JSON or text format for hourly usage

    def __str__(self):
        return f"Analytics for {self.room.name} on {self.date}"
