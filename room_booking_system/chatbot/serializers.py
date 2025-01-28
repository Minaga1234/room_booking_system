from rest_framework import serializers
from .models import ChatbotLog

class ChatbotLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotLog
        fields = '__all__'
