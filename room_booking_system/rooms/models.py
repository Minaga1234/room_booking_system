#rooms/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField  # Use ArrayField for a list of features (PostgreSQL)

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Unique room name
    location = models.CharField(max_length=100)  # Location details
    capacity = models.IntegerField()  # Maximum capacity of the room
    is_available = models.BooleanField(default=True)  # Room availability
    requires_approval = models.BooleanField(default=False)  # Booking approval required
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # Image upload
    description = models.TextField(blank=True, null=True)  # Detailed room description
    features = models.JSONField(blank=True, null=True)  # Store features as a JSON object (compatible with MySQL)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for room creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update

    def __str__(self):
        return f"{self.name} - {self.location}"
    
class UsageLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="usage_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usage Log for {self.room.name} by {self.user.username}"


