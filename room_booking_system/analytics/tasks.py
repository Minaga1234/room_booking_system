from django.contrib.auth import get_user_model  # Import the user model
from datetime import timedelta
from django.utils.timezone import now
from celery import shared_task
from analytics.models import Analytics
from notifications.models import Notification


User = get_user_model()  # Assign the user model to the variable 'User'
@shared_task
def calculate_weekly_trends():
    """
    Calculate weekly trends and notify admins about insights.
    """
    past_week = now() - timedelta(days=7)
    analytics = Analytics.objects.filter(last_updated__gte=past_week)

    underutilized_rooms = analytics.filter(utilization_rate__lt=30)
    overbooked_rooms = analytics.filter(utilization_rate__gt=80)

    admin_users = User.objects.filter(role="admin")

    for admin in admin_users:
        messages = []

        if underutilized_rooms.exists():
            rooms = ', '.join([a.room.name for a in underutilized_rooms])
            messages.append(f"The following rooms are underutilized: {rooms}")

        if overbooked_rooms.exists():
            rooms = ', '.join([a.room.name for a in overbooked_rooms])
            messages.append(f"The following rooms are overbooked: {rooms}")

        if messages:
            Notification.objects.create(
                user=admin,
                message="\n".join(messages)
            )
            
@shared_task
def alert_underutilized_rooms():
    """
    Notify admins about underutilized rooms.
    """
    analytics = Analytics.objects.filter(utilization_rate__lt=30)
    admin_users = User.objects.filter(role="admin")

    for analytic in analytics:
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                message=f"Room {analytic.room.name} has a low utilization rate of {analytic.utilization_rate:.2f}%."
            )
            
@shared_task
def auto_adjust_room_management():
    """
    Automatically adjust room settings based on analytics trends.
    """
    underutilized_rooms = Analytics.objects.filter(utilization_rate__lt=30)
    overbooked_rooms = Analytics.objects.filter(utilization_rate__gt=80)

    for analytics in overbooked_rooms:
        room = analytics.room
        # Example: Reduce max booking duration
        room.max_booking_duration = timedelta(hours=2)
        room.save()

    for analytics in underutilized_rooms:
        room = analytics.room
        # Example: Increase max booking duration or add promotions
        room.max_booking_duration = timedelta(hours=8)
        room.save()