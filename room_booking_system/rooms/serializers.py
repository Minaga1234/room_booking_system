# rooms/serializers.py
from rest_framework import serializers
from .models import Room, UsageLog

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'  # Expose all fields in the API

    def validate(self, data):
        """
        Validate room data before saving.
        """
        # Check if the context contains a request
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role in ['staff', 'student'] and data.get('is_available') is False:
                raise serializers.ValidationError("You are not authorized to mark rooms as unavailable.")
        return data

class UsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageLog
        fields = "__all__"
