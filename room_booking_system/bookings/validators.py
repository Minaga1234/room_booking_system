from django.core.exceptions import ValidationError
from analytics.models import Analytics
from django.utils.timezone import localtime

def validate_peak_usage(room, start_time, end_time):
    """
    Validate booking duration during peak hours.
    """
    analytics = Analytics.objects.filter(room=room, date=start_time.date()).first()
    if not analytics:
        return  # No analytics data yet, proceed with validation.

    # Check if booking falls within peak utilization hours
    peak_hours = analytics.peak_hours or {}
    start_hour = localtime(start_time).hour
    end_hour = localtime(end_time).hour

    for hour in range(start_hour, end_hour):
        hour_label = f"{hour}:00-{hour + 1}:00"
        if peak_hours.get(hour_label, 0) > 5:  # Example threshold: >5 bookings/hour
            raise ValidationError("Booking duration exceeds allowed limit during peak hours.")

    """
    Validate if booking complies with peak usage rules.
    """
    analytics = Analytics.objects.filter(room=room, date=start_time.date()).first()
    if analytics and analytics.utilization_rate > 80:
        raise ValidationError("Peak usage restrictions apply. Please choose another time slot.")