from django.db import models
from django.conf import settings
from bookings.models import Booking
from notifications.models import Notification  # Import Notification model

class Penalty(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Penalty for {self.user.username}: {self.amount} - {self.status}"

    @staticmethod
    def get_unpaid_penalties(user):
        """
        Calculate total unpaid penalties for a user.
        """
        return Penalty.objects.filter(user=user, status='unpaid').aggregate(total=models.Sum('amount'))['total'] or 0.00

    @staticmethod
    def create_penalty(user, booking, reason, amount):
        """
        Helper method to create a penalty and send a notification.
        """
        penalty = Penalty.objects.create(
            user=user,
            booking=booking,
            reason=reason,
            amount=amount
        )
        # Notify the user about the penalty
        Notification.create_notification(
            user=user,
            message=f"A penalty of ${amount:.2f} has been imposed for {reason}.",
            notification_type='penalty_reminder'
        )
        return penalty

    def mark_as_paid(self):
        """
        Mark the penalty as paid and notify the user.
        """
        self.status = 'paid'
        self.save()

        # Notify the user about the payment
        Notification.create_notification(
            user=self.user,
            message=f"The penalty of ${self.amount:.2f} for {self.reason} has been marked as paid.",
            notification_type='penalty_reminder'
        )
