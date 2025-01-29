from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import localtime
from django.db.transaction import atomic
from collections import defaultdict
from bookings.models import Booking
from analytics.models import Analytics
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

# Constants
TOTAL_AVAILABLE_HOURS = 8  # Example: 8 hours/day


def calculate_peak_hours(bookings):
    peak_hours = defaultdict(int)
    for booking in bookings:
        start_hour = booking.start_time.hour
        end_hour = booking.end_time.hour
        for hour in range(start_hour, end_hour):
            peak_hours[f"{hour}:00-{hour + 1}:00"] += 1
    return dict(peak_hours)


def calculate_total_usage_time(bookings):
    return sum((b.end_time - b.start_time).total_seconds() / 3600 for b in bookings)


@receiver(post_save, sender=Booking)
@atomic
def update_analytics_on_booking_save(sender, instance, created, **kwargs):
    date = localtime(instance.start_time).date()
    analytics, _ = Analytics.objects.get_or_create(room=instance.room, date=date)

    bookings = Booking.objects.filter(room=instance.room, start_time__date=date)

    analytics.total_bookings = bookings.count()
    analytics.total_usage_time = calculate_total_usage_time(bookings)
    analytics.utilization_rate = (analytics.total_usage_time / TOTAL_AVAILABLE_HOURS) * 100
    analytics.peak_hours = calculate_peak_hours(bookings)
    analytics.total_checkins = bookings.filter(status="checked_in").count()
    analytics.total_cancellations = bookings.filter(status="canceled").count()
    analytics.save()


@receiver(post_delete, sender=Booking)
@atomic
def update_analytics_on_booking_delete(sender, instance, **kwargs):
    date = localtime(instance.start_time).date()
    analytics, created = Analytics.objects.get_or_create(room=instance.room, date=date)

    bookings = Booking.objects.filter(room=instance.room, start_time__date=date)

    analytics.total_bookings = bookings.count()
    analytics.total_usage_time = calculate_total_usage_time(bookings)
    analytics.utilization_rate = (analytics.total_usage_time / TOTAL_AVAILABLE_HOURS) * 100
    analytics.peak_hours = calculate_peak_hours(bookings)
    analytics.total_checkins = bookings.filter(status="checked_in").count()
    analytics.total_cancellations = bookings.filter(status="canceled").count()

    if analytics.total_bookings == 0 and not created:
        analytics.delete()
    else:
        analytics.save()

@receiver(post_save, sender=Analytics)
def notify_admins_based_on_analytics(sender, instance, **kwargs):
    """
    Notify admins about analytics thresholds.
    """
    admin_users = User.objects.filter(role="admin")

    # Notify for underutilized rooms
    if instance.utilization_rate < 30:
        for admin in admin_users:
            Notification.create_notification(
                user=admin,
                message=f"Room {instance.room.name} has low utilization: {instance.utilization_rate:.2f}%.",
                notification_type="admin_alert",
            )

    # Notify for high-demand rooms
    elif instance.utilization_rate > 80:
        for admin in admin_users:
            Notification.create_notification(
                user=admin,
                message=f"Room {instance.room.name} is in high demand with utilization: {instance.utilization_rate:.2f}%.",
                notification_type="admin_alert",
            )
