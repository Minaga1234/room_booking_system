from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_update', 'Booking Update'),
        ('penalty_reminder', 'Penalty Reminder'),
        ('general', 'General'),
        ('admin_alert', 'Admin Alert'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."

    @staticmethod
    def unread_notifications(user):
        """Retrieve all unread notifications for a specific user."""
        return Notification.objects.filter(user=user, is_read=False)

    @staticmethod
    def create_notification(user, message, notification_type='general'):
        """Utility method to create a notification."""
        return Notification.objects.create(user=user, message=message, notification_type=notification_type)

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False
        self.save()

    def mark_as_paid(self):
        self.status = 'paid'
        self.save()
        Notification.objects.create(
            user=self.user,
            message=f"Your penalty of ${self.amount:.2f} has been marked as paid.",
            notification_type='penalty_update'
        )

