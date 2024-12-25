from bookings.models import Booking
from notifications.models import Notification
from django.contrib.auth import get_user_model
from celery import shared_task

User = get_user_model()

@shared_task
def track_no_shows():
    """
    Track no-shows and apply penalties.
    """
    no_shows = Booking.objects.filter(checked_in=False, end_time__lt=now())
    for booking in no_shows:
        user = booking.user
        Notification.objects.create(
            user=user,
            message="You missed your booking. A penalty has been applied."
        )
        # Apply penalty logic here
