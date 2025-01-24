from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Booking, Room
from users.models import CustomUser 
from rest_framework.exceptions import ValidationError

User = get_user_model()

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username in responses
    room = serializers.StringRelatedField(read_only=True)  # Display room name in responses
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # Accept user ID
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), write_only=True)  # Accept room ID

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'price', 'is_approved', 'penalty_flag', 'checked_in', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Handle the creation of a booking.
        """
        user = validated_data.pop('user_id')
        room = validated_data.pop('room_id')
        # Pass validation before saving
        booking = Booking(user=user, room=room, **validated_data)
        booking.clean()  # Call validation logic
        booking.save()
        return booking

    def validate(self, data):
        """
        Validate booking data to prevent overlaps and ensure logical times.
        """
        room = data.get('room_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        print(f"Validating booking: room={room}, start_time={start_time}, end_time={end_time}")

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            room=room,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if overlapping:
            print(f"Overlapping booking detected for room={room}, start_time={start_time}, end_time={end_time}")
            raise serializers.ValidationError({"non_field_errors": ["Room is already booked for this time slot."]})

        # Validate start and end times
        if start_time >= end_time:
            print(f"Invalid time range: start_time={start_time}, end_time={end_time}")
            raise serializers.ValidationError({"non_field_errors": ["Start time must be earlier than end time."]})

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

