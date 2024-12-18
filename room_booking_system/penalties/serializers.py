from rest_framework import serializers
from .models import Penalty

class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        fields = '__all__'
