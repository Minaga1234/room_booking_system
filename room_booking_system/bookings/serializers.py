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

        # Validate dynamic price
        data['price'] = Booking.calculate_dynamic_price(
            data['room'], data['start_time'], base_price=100
        )
        return data
