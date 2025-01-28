from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id',
            'user',
            'full_name',
            'field_of_study',
            'room',
            'student_id',
            'content',
            'rating',
            'sentiment',
            'admin_response',
            'created_at',
        ]
        read_only_fields = ['user', 'sentiment', 'admin_response', 'created_at']
