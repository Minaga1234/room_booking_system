#rooms/serializers.py
from rest_framework import serializers
from .models import Room, UsageLog

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'  # Expose all fields in the API
    
    def validate_features(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be provided as a list.")
        return value
class UsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageLog
        fields = "__all__"


