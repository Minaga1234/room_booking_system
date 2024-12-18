from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Analytics
from .serializers import AnalyticsSerializer

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer

    @action(detail=False, methods=['get'])
    def room_usage(self, request):
        room_id = request.query_params.get('room_id')
        if not room_id:
            return Response({"error": "room_id is required"}, status=400)

        analytics = Analytics.objects.filter(room_id=room_id)
        serializer = self.get_serializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        data = Analytics.objects.values(
            'room__name'
        ).annotate(
            total_bookings=models.Sum('total_bookings'),
            total_checkins=models.Sum('total_checkins')
        )
        return Response(data)
