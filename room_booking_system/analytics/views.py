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
from bookings.models import Booking 
from .serializers import AnalyticsSerializer
from django.core.management.base import BaseCommand
from prophet import Prophet
import pandas as pd
from datetime import timedelta, date
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import csv


class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing analytics data.
    """
    queryset = Analytics.objects.select_related('room').all()
    serializer_class = AnalyticsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
<<<<<<< HEAD
        Optionally filter analytics data by room_id, start_date, and end_date.
        """
        queryset = self.queryset
        room_id = self.request.query_params.get('room_id')
=======
        Optionally filter analytics by room_id, date, or date range (start_date and end_date) via query parameters.
        """
        queryset = Analytics.objects.all()
        room_id = self.request.query_params.get('room_id')
        date = self.request.query_params.get('date')
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if room_id:
            queryset = queryset.filter(room_id=room_id)
<<<<<<< HEAD
=======
        if date:
            queryset = queryset.filter(date=date)
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(date__lte=end_date)
<<<<<<< HEAD

        return queryset
=======
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109

        return queryset

class AnalyticsChartData(APIView):
    """
    API endpoint to provide analytics data for frontend charts, including active users.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            # Calculate active users based on active bookings
            active_bookings = Booking.objects.filter(
                start_time__lte=now(),  # Booking has started
                end_time__gte=now(),  # Booking has not ended
                status="checked_in"  # Booking is checked in
            ).values("user").distinct()  # Get distinct users from active bookings

            active_users_count = active_bookings.count()

            # Fetch analytics data from the past 7 days
            past_week = now().date() - timedelta(days=7)
            analytics_data = Analytics.objects.filter(date__gte=past_week)

            if not analytics_data.exists():
                return Response({
                    "active_users": active_users_count,
                    "rooms": [],
                    "total_bookings": [],
                    "utilization_rates": []
                })

            # Aggregate data for response
            room_data = {}
            for analytics in analytics_data:
                room_name = analytics.room.name
                if room_name not in room_data:
                    room_data[room_name] = {
                        "total_bookings": analytics.total_bookings,
                        "utilization_rate": [analytics.utilization_rate]
                    }
                else:
                    room_data[room_name]["total_bookings"] += analytics.total_bookings
                    room_data[room_name]["utilization_rate"].append(analytics.utilization_rate)

            # Prepare response data
            rooms = list(room_data.keys())
            total_bookings = [data["total_bookings"] for data in room_data.values()]
            utilization_rates = [
                sum(data["utilization_rate"]) / len(data["utilization_rate"])
                for data in room_data.values()
            ]

            data = {
                "active_users": active_users_count,
                "rooms": rooms,
                "total_bookings": total_bookings,
                "utilization_rates": utilization_rates,
            }

            return Response(data)

        except Exception as e:
            # Handle errors
            print(f"Error in AnalyticsChartData: {e}")
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
    past_week = now().date() - timedelta(days=7)
    analytics_data = Analytics.objects.filter(date__gte=past_week)

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

class ExportCSVView(APIView):
    """
    API to export analytics data as a CSV file.
    """
    permission_classes = [AllowAny]  # Restrict this if needed for security

    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_data.csv"'

        # Create the CSV writer using the response as a file-like object
        writer = csv.writer(response)

        # Write header row
        writer.writerow([
            'Room Name',
            'Date',
            'Total Bookings',
            'Total Check-ins',
            'Total Cancellations',
            'Total Usage Time (hours)',
            'Utilization Rate (%)',
            'Peak Hours'
        ])

        # Query analytics data
        analytics_data = Analytics.objects.select_related('room').all()

        # Write data rows
        for analytics in analytics_data:
            writer.writerow([
                analytics.room.name,
                analytics.date,
                analytics.total_bookings,
                analytics.total_checkins,
                analytics.total_cancellations,
                analytics.total_usage_time,
                analytics.utilization_rate,
                analytics.peak_hours
            ])

        return response