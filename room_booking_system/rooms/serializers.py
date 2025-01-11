<<<<<<< HEAD
# rooms/serializers.py
=======
#rooms/serializers.py
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
from rest_framework import serializers
from .models import Room, UsageLog

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'  # Expose all fields in the API
<<<<<<< HEAD

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

=======
        
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
class UsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageLog
        fields = "__all__"
<<<<<<< HEAD
=======


>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
