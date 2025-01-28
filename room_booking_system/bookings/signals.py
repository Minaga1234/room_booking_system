# bookings/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from analytics.models import Analytics
from collections import defaultdict
from django.utils.timezone import localtime
from django.db.transaction import atomic

@receiver(post_save, sender=Booking)
@atomic
def update_analytics_on_save(sender, instance, created, **kwargs):
    """
    Update analytics when a booking is created or updated.
    """
    start_time = localtime(instance.start_time)
    
    # Fetch existing Analytics record or create a new one
    analytics = Analytics.objects.filter(room=instance.room, date=start_time.date()).first()

    if not analytics:
        analytics = Analytics.objects.create(
            room=instance.room,
            date=start_time.date(),
            total_bookings=0,
            total_checkins=0,
            total_cancellations=0,
            total_usage_time=0.0,
            peak_hours={},
            utilization_rate=0.0,
        )

    if created:
        analytics.total_bookings += 1  # Increment bookings count

    # Calculate total usage time
    bookings = Booking.objects.filter(room=instance.room, start_time__date=start_time.date())
    analytics.total_usage_time = sum(
        (b.end_time - b.start_time).total_seconds() / 3600 for b in bookings
    )

    # Update utilization rate
    total_available_hours = 8  # Example: 8 hours/day
    analytics.utilization_rate = (analytics.total_usage_time / total_available_hours) * 100

    # Update peak hours
    peak_hours = defaultdict(int)
    for booking in bookings:
        start_hour = booking.start_time.hour
        end_hour = booking.end_time.hour
        for hour in range(start_hour, end_hour):
            peak_hours[f"{hour}:00-{hour + 1}:00"] += 1
    analytics.peak_hours = dict(peak_hours)

    analytics.save()
