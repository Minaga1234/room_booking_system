from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from rooms.models import Room

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    penalty_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking: {self.room.name} by {self.user.username} ({self.status})"

    def clean(self):
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(id=self.id)
        if overlapping_bookings.exists():
            raise ValidationError("This booking overlaps with an existing booking.")