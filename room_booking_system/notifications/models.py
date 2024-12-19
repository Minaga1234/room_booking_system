from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_update', 'Booking Update'),
        ('penalty_reminder', 'Penalty Reminder'),
        ('general', 'General'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()