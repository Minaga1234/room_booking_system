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
from django.core.management.base import BaseCommand
from prophet import Prophet
import pandas as pd
from analytics.models import Analytics
from datetime import timedelta, date
import matplotlib.pyplot as plt
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing analytics data.
    """
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer

    def get_queryset(self):
        """
        Optionally filter analytics by room_id, date, or date range (start_date and end_date) via query parameters.
        """
        queryset = Analytics.objects.all()
        room_id = self.request.query_params.get('room_id')
        date = self.request.query_params.get('date')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if date:
            queryset = queryset.filter(date=date)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

class AnalyticsChartData(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        try:
            past_week = now() - timedelta(days=7)
            analytics_data = Analytics.objects.filter(last_updated__gte=past_week)

            if not analytics_data.exists():
                return Response({
                    "rooms": [],
                    "total_bookings": [],
                    "utilization_rates": []
                })

            data = {
                "rooms": [analytics.room.name for analytics in analytics_data],
                "total_bookings": [analytics.total_bookings for analytics in analytics_data],
                "utilization_rates": [analytics.utilization_rate for analytics in analytics_data],
            }
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


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
 
class Command(BaseCommand):
    help = "Generate room usage forecasts"

    def handle(self, *args, **kwargs):
        # Extract historical data
        data = Analytics.objects.values("date", "total_bookings")
        df = pd.DataFrame(data)
        df.rename(columns={"date": "ds", "total_bookings": "y"}, inplace=True)

        # Train the forecasting model
        model = Prophet()
        model.fit(df)

        # Predict for the next 30 days
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Save predictions to database or notify admins
        self.stdout.write("Forecasting complete!")

        # Visualization
        model.plot(forecast)
        plt.title("Room Usage Forecast")
        plt.xlabel("Date")
        plt.ylabel("Total Bookings")
        plt.savefig("forecast.png")
        plt.show()

