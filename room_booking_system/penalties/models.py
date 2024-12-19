from django.db import models
from django.conf import settings
from bookings.models import Booking

class Penalty(models.Model):
    STATUS_CHOICES = (
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
        """Calculate total unpaid penalties for a user."""
        return Penalty.objects.filter(user=user, status='unpaid').aggregate(total=models.Sum('amount'))['total'] or 0.00
