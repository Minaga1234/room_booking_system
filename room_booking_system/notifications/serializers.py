from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_unread_count(self, obj):
        """Fetch the count of unread notifications for the user."""
        return Notification.unread_notifications(obj.user).count()
