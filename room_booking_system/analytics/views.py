import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.utils.timezone import now, timedelta
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Analytics
from .serializers import AnalyticsSerializer


class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing analytics data.
    """
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer

    def get_queryset(self):
        """
        Optionally filter analytics by room_id or date via query parameters.
        """
        room_id = self.request.query_params.get('room_id')
        date = self.request.query_params.get('date')
        queryset = Analytics.objects.all()
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset


class AnalyticsChartData(APIView):
    """
    API endpoint to provide analytics data for frontend charts.
    """

    def get(self, request, *args, **kwargs):
        past_week = now() - timedelta(days=7)
        analytics_data = Analytics.objects.filter(last_updated__gte=past_week)

        data = {
            "rooms": [analytics.room.name for analytics in analytics_data],
            "total_bookings": [analytics.total_bookings for analytics in analytics_data],
            "utilization_rates": [analytics.utilization_rate for analytics in analytics_data],
        }

        return Response(data)


class ChartView(View):
    """
    Generate and return a bar chart for total bookings per room.
    """

    def get(self, request):
        analytics_data = Analytics.objects.all()
        rooms = [analytics.room.name for analytics in analytics_data]
        bookings = [analytics.total_bookings for analytics in analytics_data]

        plt.figure(figsize=(10, 6))
        plt.bar(rooms, bookings, color='blue')
        plt.xlabel('Rooms')
        plt.ylabel('Total Bookings')
        plt.title('Total Bookings per Room')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='image/png')
        buffer.close()
        return response

def weekly_utilization_heatmap(request):
    """
    Generate and return a heatmap for room utilization over the past week.
    """
    past_week = now() - timedelta(days=7)
    analytics_data = Analytics.objects.filter(last_updated__gte=past_week)

    rooms = [analytics.room.name for analytics in analytics_data]
    utilization_rates = [analytics.utilization_rate for analytics in analytics_data]

    plt.figure(figsize=(10, 6))
    plt.barh(rooms, utilization_rates, color='green')
    plt.xlabel('Utilization Rate (%)')
    plt.ylabel('Rooms')
    plt.title('Weekly Room Utilization')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='image/png')
    buffer.close()
    return response
  
  
