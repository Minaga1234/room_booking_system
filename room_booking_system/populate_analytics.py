from analytics.models import Analytics
from bookings.models import Booking
from django.utils.timezone import localtime
from collections import defaultdict
from datetime import timedelta

def backfill_analytics():
    bookings = Booking.objects.all()
    for booking in bookings:
        start_time = localtime(booking.start_time)
        analytics, created = Analytics.objects.get_or_create(
            room=booking.room, date=start_time.date()
        )
        # Increment total bookings
        analytics.total_bookings += 1

        # Calculate total usage time
        bookings_for_day = Booking.objects.filter(
            room=booking.room, start_time__date=start_time.date()
        )
        analytics.total_usage_time = sum(
            (b.end_time - b.start_time).total_seconds() / 3600 for b in bookings_for_day
        )

        # Update utilization rate
        total_available_hours = 8  # Example: 8 hours/day
        analytics.utilization_rate = (analytics.total_usage_time / total_available_hours) * 100

        # Update peak hours
        peak_hours = defaultdict(int)
        for b in bookings_for_day:
            start_hour = b.start_time.hour
            end_hour = b.end_time.hour
            for hour in range(start_hour, end_hour):
                peak_hours[f"{hour}:00-{hour + 1}:00"] += 1
        analytics.peak_hours = dict(peak_hours)

        # Save analytics
        analytics.save()

    print("Analytics backfill complete!")

if __name__ == "__main__":
    backfill_analytics()
