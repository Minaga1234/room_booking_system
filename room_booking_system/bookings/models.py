from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from rooms.models import Room
from notifications.models import Notification
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('checked_in', 'Checked In'),
        ('canceled', 'Canceled'),
        ('checked_out', 'Checked Out'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    penalty_flag = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    degree_major = models.TextField(null=True, blank=True)  # Changed to TextField
    purpose = models.TextField(default="N/A")

    class Meta:
        ordering = ['start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'start_time', 'end_time'],
                name='unique_booking_per_room_time'
            ),
        ]

    def __str__(self):
        return f"Booking: {self.room.name} by {self.user.username} ({self.status})"

    def clean(self):
        """
        Validate booking to prevent overlapping times and ensure logical booking times.
        """
        # Prevent overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            start_time__lt=self.end_time,  # Overlap condition
            end_time__gt=self.start_time   # Overlap condition
        ).exclude(id=self.id)  # Exclude current instance during updates

        if overlapping_bookings.exists():
            raise ValidationError("This booking overlaps with an existing booking.")

        # Validate that start time is before end time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def save(self, *args, **kwargs):
        """
        Save the booking after validation.
        """
        self.clean()  # Ensure validations are applied
        super().save(*args, **kwargs)

    def approve(self):
        """
        Approve the booking and notify the user.
        """
        self.status = 'approved'
        self.is_approved = True
        self.save()

        # Notify the user
        Notification.create_notification(
            user=self.user,
            message=f"Your booking for {self.room.name} has been approved.",
            notification_type='booking_update'
        )

    def cancel(self):
        """
        Cancel the booking and notify the user.
        """
        self.status = 'canceled'
        self.save()

        # Notify the user
        Notification.create_notification(
            user=self.user,
            message=f"Your booking for {self.room.name} has been canceled.",
            notification_type='booking_update'
        )

    def check_in(self):
        """
        Mark the booking as checked in and notify the user.
        """
        if self.status != 'approved':
            raise ValidationError("Only approved bookings can be checked in.")
        self.checked_in = True
        self.status = "checked_in"
        self.save()

        # Notify the user
        Notification.create_notification(
            user=self.user,
            message=f"You have successfully checked in for your booking at {self.room.name}.",
            notification_type='booking_update'
        )

    def calculate_penalty(self):
        """
        Calculate penalty for various booking violations:
        - Late cancellation
        - No-show (approved but not checked in)
        - Overstaying (checked in but not checked out after end_time)
        """
        current_time = timezone.now()
        print(f"Debug: Calculating penalty for booking {self.id}. Current time: {current_time}.")  # Debugging log

        # Penalty for late cancellation
        if self.status == 'canceled' and self.end_time < current_time:
            print("Debug: Late cancellation penalty applied.")  # Debugging log
            return 50.00

        # Penalty for no-show
        if self.status == 'approved' and not self.checked_in and self.start_time < current_time:
            print("Debug: No-show penalty applied.")  # Debugging log
            return 100.00

        # Penalty for overstaying (checked in but end_time has passed)
        if self.status == 'checked_in' and current_time > self.end_time:
            overstay_duration = (current_time - self.end_time).total_seconds() / 60  # Overstay duration in minutes
            penalty_rate = 2.00  # Example penalty rate per minute
            penalty = round(overstay_duration * penalty_rate, 2)
            print(f"Debug: Overstay penalty calculated: {penalty}.")  # Debugging log
            return penalty

        print("Debug: No penalty applicable.")  # Debugging log
        return 0.00  # No penalty
