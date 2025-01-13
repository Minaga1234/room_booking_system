from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from rooms.models import Room
from analytics.models import Analytics
from branding.models import Degree

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('checked_in', 'Checked In'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    degree_major = models.ForeignKey(Degree, on_delete=models.SET_NULL, null=True, blank=True, help_text="Degree associated with the booking.")  # New Field
    purpose = models.TextField(help_text="Detailed purpose for the booking.")  # New Field
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    penalty_flag = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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
        Validate booking to prevent overlapping times and apply rules.
        """
        # Prevent overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(id=self.id)
        if overlapping_bookings.exists():
            raise ValidationError("This booking overlaps with an existing booking.")

        # Validate user roles and peak usage
        analytics = Analytics.objects.filter(room=self.room, date=self.start_time.date()).first()
        if analytics:
            peak_hours = analytics.peak_hours or {}
            start_hour = self.start_time.hour
            end_hour = self.end_time.hour
            for hour in range(start_hour, end_hour):
                hour_label = f"{hour}:00-{hour + 1}:00"
                if peak_hours.get(hour_label, 0) > 5:
                    raise ValidationError("Cannot book during peak hours.")
            if analytics.utilization_rate > 80 and self.user.role not in ["staff", "admin"]:
                raise ValidationError("Bookings during peak usage are restricted to staff and admins.")

        # Validate start and end times
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def save(self, *args, **kwargs):
        """
        Save the booking after validation and apply dynamic pricing.
        """
        self.clean()

        # Apply dynamic pricing for new bookings
        if not self.pk:  # Only for new bookings
            self.price = self.calculate_dynamic_price(self.room, self.start_time)

        super().save(*args, **kwargs)

    @staticmethod
    def calculate_dynamic_price(room, start_time, base_price=100):
        """
        Adjust booking price dynamically based on room utilization.
        """
        analytics = Analytics.objects.filter(room=room, date=start_time.date()).first()
        if analytics:
            if analytics.utilization_rate > 80:
                return base_price * 1.5  # Increase price by 50%
            elif analytics.utilization_rate < 30:
                return base_price * 0.8  # Offer a 20% discount
        return base_price

    def approve(self):
        """
        Approve the booking and validate peak-hour restrictions.
        """
        analytics = Analytics.objects.filter(room=self.room, date=self.start_time.date()).first()
        if analytics and analytics.utilization_rate > 80:
            if self.user.role == 'student':
                raise ValidationError("Students are not allowed to book during peak hours.")
        self.status = 'approved'
        self.is_approved = True
        self.save()

    def cancel(self):
        """
        Cancel the booking and update analytics if necessary.
        """
        self.status = 'canceled'
        self.save()

    def check_in(self):
        """
        Mark the booking as checked in.
        """
        if self.status != 'approved':
            raise ValidationError("Only approved bookings can be checked in.")
        self.checked_in = True
        self.status = "checked_in"  # Update status to 'checked_in'
        self.save()

