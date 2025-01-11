from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from bookings.models import Booking
from .models import Analytics
from datetime import timedelta
from notifications.models import Notification
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from collections import defaultdict
from django.db.transaction import atomic

User = get_user_model()  # Get the User model

@receiver(post_save, sender=Booking)
@atomic
def update_analytics_on_save(sender, instance, created, **kwargs):
    """
    Update analytics when a booking is created or updated.
    """
    start_time = localtime(instance.start_time)
    analytics, _ = Analytics.objects.get_or_create(
        room=instance.room, date=start_time.date()
    )

    if created:
        analytics.total_bookings += 1

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

@receiver(post_delete, sender=Booking)
@atomic
def update_analytics_on_delete(sender, instance, **kwargs):
    """
    Update analytics when a booking is deleted.
    """
    start_time = localtime(instance.start_time)
    analytics, _ = Analytics.objects.get_or_create(room=instance.room, date=start_time.date())
    analytics.total_bookings = max(analytics.total_bookings - 1, 0)  # Prevent negative totals

    # Recalculate total usage time
    bookings = Booking.objects.filter(room=instance.room, start_time__date=start_time.date())
    analytics.total_usage_time = sum(
        (b.end_time - b.start_time).total_seconds() / 3600 for b in bookings
    )

    # Recalculate utilization rate
    total_available_hours = 8
    analytics.utilization_rate = (analytics.total_usage_time / total_available_hours) * 100

    analytics.save()


@receiver(post_save, sender=Analytics)
def analytics_notification_handler(sender, instance, **kwargs):
    """
    Notify admins based on analytics data.
    """
    admin_users = User.objects.filter(role="admin")

    # Notify for underutilized rooms
    if instance.utilization_rate < 30:
        for admin in admin_users:
            Notification.create_notification(
                user=admin,
                message=f"Room {instance.room.name} has low utilization: {instance.utilization_rate:.2f}%.",
                notification_type='admin_alert',
            )

    # Notify for overbooked rooms
    elif instance.utilization_rate > 80:
        for admin in admin_users:
            Notification.create_notification(
                user=admin,
                message=f"Room {instance.room.name} is in high demand with utilization: {instance.utilization_rate:.2f}%.",
                notification_type='admin_alert',
            )

            
@receiver(post_save, sender=Booking)
def update_total_checkins(sender, instance, created, **kwargs):
    """
    Increment total_checkins when a booking's status is changed to 'checked_in'.
    """
    if instance.status == "checked_in":
        analytics, _ = Analytics.objects.get_or_create(room=instance.room, date=instance.start_time.date())
        analytics.total_checkins += 1
        analytics.save()


@receiver(post_save, sender=Booking)
def update_total_usage_time(sender, instance, **kwargs):
    analytics, created = Analytics.objects.get_or_create(
        room=instance.room, 
        date=localtime(instance.start_time).date()
    )
    bookings = Booking.objects.filter(
        room=instance.room, 
        start_time__date=instance.start_time.date()
    )
    analytics.total_usage_time = sum(
        (b.end_time - b.start_time).total_seconds() / 3600 for b in bookings
    )
    analytics.save()
    
@receiver(post_save, sender=Booking)
def update_peak_hours(sender, instance, **kwargs):
    analytics, created = Analytics.objects.get_or_create(
        room=instance.room, 
        date=localtime(instance.start_time).date()
    )
    bookings = Booking.objects.filter(
        room=instance.room, 
        start_time__date=instance.start_time.date()
    )
    peak_hours = defaultdict(int)
    for booking in bookings:
        start_hour = booking.start_time.hour
        end_hour = booking.end_time.hour
        for hour in range(start_hour, end_hour):
            peak_hours[f"{hour}:00-{hour+1}:00"] += 1

    analytics.peak_hours = dict(peak_hours)
    analytics.save()
    
@receiver(post_save, sender=Booking)
def update_utilization_rate(sender, instance, **kwargs):
    analytics, created = Analytics.objects.get_or_create(
        room=instance.room, 
        date=localtime(instance.start_time).date()
    )
    total_available_time = 8  # Example: 8 hours/day
    analytics.utilization_rate = (analytics.total_usage_time / total_available_time) * 100
    analytics.save()
    
@receiver(post_save, sender=Analytics)
def notify_admins_about_high_demand(sender, instance, **kwargs):
    if instance.utilization_rate > 80:
        admin_users = User.objects.filter(role="admin")
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                message=f"Room {instance.room.name} is in high demand with utilization rate: {instance.utilization_rate:.2f}%."
            )
            
@receiver(post_save, sender=Booking)
def update_total_cancellations(sender, instance, **kwargs):
    if instance.status == "canceled":
        analytics, _ = Analytics.objects.get_or_create(room=instance.room, date=instance.start_time.date())
        analytics.total_cancellations += 1
        analytics.save()

