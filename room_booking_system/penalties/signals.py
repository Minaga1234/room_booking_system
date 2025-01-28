from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from .models import Penalty
from django.utils import timezone

@receiver(post_save, sender=Booking)
def handle_booking_events(sender, instance, **kwargs):
    """Apply penalties automatically for certain booking events."""
    if instance.status == 'canceled' and instance.end_time < timezone.now():
        Penalty.create_penalty(
            user=instance.user,
            booking=instance,
            reason="Late cancellation",
            amount=50.00
        )
    elif instance.status == 'pending' and instance.start_time < timezone.now():
        Penalty.create_penalty(
            user=instance.user,
            booking=instance,
            reason="No-show",
            amount=100.00
        )
