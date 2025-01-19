from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Booking, Analytics
from branding.models import Degree
from datetime import datetime, timedelta
from users.models import CustomUser  # Import the correct user model
from django.utils.timezone import is_naive, make_aware

class BookingSerializer(serializers.ModelSerializer):
    degree_major = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all(), required=False)
    email = serializers.EmailField(write_only=True, required=False)  # Optional email field for dynamic user identification

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'price', 'is_approved', 'penalty_flag', 'checked_in', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Additional validations for booking.
        """
        # Ensure start_time and end_time are timezone-aware
        if is_naive(data['start_time']):
            data['start_time'] = make_aware(data['start_time'])
        if is_naive(data['end_time']):
            data['end_time'] = make_aware(data['end_time'])

        # Prevent overlapping bookings
        if Booking.objects.filter(
            room=data['room'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time'],
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise ValidationError("This room is already booked during the selected time.")

        # Validate that start_time is before end_time
        if data['start_time'] >= data['end_time']:
            raise ValidationError("Start time must be before end time.")

        # Validate role-based booking restrictions
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        role = getattr(user, 'role', 'student')  # Default to 'student' if no user is authenticated
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        if role == 'student':
            # Students can only book for today
            if data['start_time'].date() != today.date():
                raise ValidationError("Students can only book for today.")
        elif role == 'staff':
            # Staff can book for today or tomorrow
            if data['start_time'].date() not in [today.date(), tomorrow.date()]:
                raise ValidationError("Staff can only book for today or tomorrow.")

        # Validate dynamic price
        data['price'] = Booking.calculate_dynamic_price(
            room=data['room'],
            start_time=data['start_time'],
            base_price=100  # Default base price
        )

        # Validate peak usage for students
        analytics = Analytics.objects.filter(room=data['room'], date=data['start_time'].date()).first()
        if analytics and analytics.utilization_rate > 80 and role == "student":
            raise ValidationError("Bookings during peak usage are restricted for students.")

        return data

    def create(self, validated_data):
        """
        Handle the creation of a booking and associate the user dynamically by email or authenticated request.
        """
        email = validated_data.pop('email', None)
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None

        if email and not user:
            # Dynamically fetch the user if email is provided and no authenticated user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise ValidationError("User with the provided email does not exist.")

        if not user:
            raise ValidationError("User identification is required (email or authenticated user).")

        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update a booking and recalculate the price if necessary.
        """
        if 'room' in validated_data or 'start_time' in validated_data:
            validated_data['price'] = Booking.calculate_dynamic_price(
                room=validated_data.get('room', instance.room),
                start_time=validated_data.get('start_time', instance.start_time),
                base_price=100  # Default base price
            )
        return super().update(instance, validated_data)

    def perform_create(self, serializer):
        """
        Finalize booking creation and notify if applicable.
        """
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        serializer.save(user=user)  # Assign user if authenticated

