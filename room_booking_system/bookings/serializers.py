from rest_framework import serializers
from .models import Booking
from analytics.models import Analytics  # Ensure this import exists

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        # Check for overlapping bookings
        if Booking.objects.filter(
            room=data['room'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time'],
        ).exists():
            raise serializers.ValidationError("Room is already booked for this time.")

        # Validate peak usage
        analytics = Analytics.objects.filter(room=data['room'], date=data['start_time'].date()).first()
        if analytics and analytics.utilization_rate > 80 and data['user'].role == "student":
            raise serializers.ValidationError("Bookings during peak usage are restricted for students.")

        # Validate start and end time logic
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be earlier than end time.")

        # Dynamic price calculation
        data['price'] = Booking.calculate_dynamic_price(data['room'], data['start_time'], base_price=100)

        return data
