from django.core.exceptions import ValidationError
from bookings.models import Booking
from django.utils.timezone import localtime

def validate_peak_usage(room, start_time, end_time):
    """
    Validate booking to ensure no overlap during the specified time.
    """
    # Prevent overlapping bookings for the same room
    overlapping_bookings = Booking.objects.filter(
        room=room,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if overlapping_bookings.exists():
        raise ValidationError("The room is already booked during the specified time.")

    # Additional validation to ensure start time is before end time
    if start_time >= end_time:
        raise ValidationError("Start time must be before end time.")
