from rest_framework import serializers
from .models import Penalty

class PenaltySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    booking = serializers.StringRelatedField(read_only=True)
    total_unpaid = serializers.SerializerMethodField()

    class Meta:
        model = Penalty
        fields = [
            'id',
            'user',
            'booking',
            'reason',
            'amount',
            'status',
            'created_at',
            'updated_at',
            'total_unpaid',
        ]
        
    def get_total_unpaid(self, obj):
        return Penalty.get_unpaid_penalties(obj.user)

