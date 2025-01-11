from rest_framework import serializers
from .models import Booking, Analytics
from branding.models import Degree  # Import the Degree model

class BookingSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for Degree
    degree_major = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all(), required=False)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'price', 'is_approved', 'penalty_flag', 'checked_in', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Additional validations for booking.
        """
        # Prevent overlapping bookings
        if Booking.objects.filter(
            room=data['room'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time'],
        ).exists():
            raise serializers.ValidationError("This room is already booked during the selected time.")

        # Validate that start_time is before end_time
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")

        # Validate dynamic price
        data['price'] = Booking.calculate_dynamic_price(
            room=data['room'],
            start_time=data['start_time'],
            base_price=100  # Default base price
        )
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

    def create(self, validated_data):
        """
        Handle the creation of a booking with associated user from the request context.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Handle the update of a booking and ensure price is recalculated if room or time changes.
        """
        if 'room' in validated_data or 'start_time' in validated_data:
            validated_data['price'] = Booking.calculate_dynamic_price(
                room=validated_data.get('room', instance.room),
                start_time=validated_data.get('start_time', instance.start_time),
                base_price=100  # Default base price
            )
        return super().update(instance, validated_data)
