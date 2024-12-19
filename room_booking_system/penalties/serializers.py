from rest_framework import serializers
from .models import Penalty

class PenaltySerializer(serializers.ModelSerializer):
    total_unpaid = serializers.SerializerMethodField()

    class Meta:
        model = Penalty
        fields = '__all__'

    def get_total_unpaid(self, obj):
        """Fetch total unpaid penalties for the user."""
        return Penalty.get_unpaid_penalties(obj.user)
