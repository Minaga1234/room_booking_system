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
from django.core.management.base import BaseCommand
from prophet import Prophet
import pandas as pd
import csv
from rest_framework.permissions import AllowAny
from .models import Analytics
from bookings.models import Booking
from .serializers import AnalyticsSerializer
from collections import defaultdict
from django.db.models import Sum, Avg
from rooms.models import Room  
class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing analytics data.
    """
    queryset = Analytics.objects.select_related('room').all()
    serializer_class = AnalyticsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Optionally filter analytics data by room_id, start_date, and end_date.
        """
        queryset = self.queryset
        room_id = self.request.query_params.get('room_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

class AnalyticsChartData(APIView):
    """
    API endpoint for time-series data analytics.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Define date range (last 7 days)
            past_week = now().date() - timedelta(days=7)

            # Fetch time-series data grouped by room and date
            analytics_data = Analytics.objects.filter(date__gte=past_week).values(
                "date", "room__name"
            ).annotate(
                total_bookings=Sum("total_bookings"),
                total_cancellations=Sum("total_cancellations"),
                avg_utilization=Avg("utilization_rate"),
            )

            # Format data for chart
            response_data = defaultdict(lambda: {"bookings": [], "cancellations": [], "utilization": []})
            dates = sorted(set(entry["date"] for entry in analytics_data))

            for entry in analytics_data:
                room = entry["room__name"]
                response_data[room]["bookings"].append(entry["total_bookings"])
                response_data[room]["cancellations"].append(entry["total_cancellations"])
                response_data[room]["utilization"].append(entry["avg_utilization"])

            return Response({
                "dates": dates,
                "data": response_data,
            })

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

        # Create bar chart
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
    try:
        # Calculate the past week range
        past_week = now().date() - timedelta(days=7)
        analytics_data = Analytics.objects.filter(date__gte=past_week)

        if not analytics_data.exists():
            return HttpResponse("No data available for the past week.", status=404)

        # Extract data for the heatmap
        rooms = [analytics.room.name for analytics in analytics_data]
        utilization_rates = [analytics.utilization_rate for analytics in analytics_data]

        # Create the heatmap
        plt.figure(figsize=(10, 6))
        plt.barh(rooms, utilization_rates, color='green')
        plt.xlabel('Utilization Rate (%)')
        plt.ylabel('Rooms')
        plt.title('Weekly Room Utilization Heatmap')

        # Save the plot to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='image/png')
        buffer.close()
        return response
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return HttpResponse("An error occurred while generating the heatmap.", status=500)

class ExportCSVView(APIView):
    """
    API to export aggregated analytics data as a CSV file.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Prepare the HTTP response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="room_analytics.csv"'

            # Fetch analytics data for the past 30 days
            past_month = now().date() - timedelta(days=30)
            analytics_data = Analytics.objects.filter(date__gte=past_month).select_related("room")

            # Room mapping
            room_mapping = {room.id: room.name for room in Room.objects.all()}

            # Aggregated data
            aggregated_data = defaultdict(lambda: defaultdict(lambda: {
                "total_bookings": 0,
                "total_checkins": 0,
                "total_cancellations": 0,
                "total_usage_time": 0.0,
                "utilization_rate": 0.0,
                "peak_hours": defaultdict(int)
            }))

            # Process analytics data
            for entry in analytics_data:
                room_name = room_mapping.get(entry.room.id, "Unknown Room")
                date = entry.date
                aggregated_data[room_name][date]["total_bookings"] += entry.total_bookings
                aggregated_data[room_name][date]["total_checkins"] += entry.total_checkins
                aggregated_data[room_name][date]["total_cancellations"] += entry.total_cancellations
                aggregated_data[room_name][date]["total_usage_time"] += entry.total_usage_time

                # Aggregate peak hours
                for hour, count in entry.peak_hours.items():
                    aggregated_data[room_name][date]["peak_hours"][hour] += count

                # Calculate utilization rate
                total_available_time = 8.0  # Example: 8 hours/day
                if aggregated_data[room_name][date]["total_usage_time"] > 0:
                    utilization = (
                        aggregated_data[room_name][date]["total_usage_time"] / total_available_time
                    ) * 100
                    aggregated_data[room_name][date]["utilization_rate"] = min(utilization, 100.0)  # Cap at 100%

            # Write CSV headers
            writer = csv.writer(response)
            writer.writerow([
                "Room Name",
                "Date",
                "Total Bookings",
                "Total Check-ins",
                "Total Cancellations",
                "Total Usage Time (hours)",
                "Utilization Rate (%)",
                "Peak Hours"
            ])

            # Write rows for each room and date
            for room_name, room_data in aggregated_data.items():
                for date, metrics in room_data.items():
                    if (
                        metrics["total_bookings"] > 0 or
                        metrics["total_checkins"] > 0 or
                        metrics["total_cancellations"] > 0 or
                        metrics["total_usage_time"] > 0
                    ):
                        writer.writerow([
                            room_name,
                            date,
                            metrics["total_bookings"],
                            metrics["total_checkins"],
                            metrics["total_cancellations"],
                            f"{metrics['total_usage_time']:.1f}",
                            f"{metrics['utilization_rate']:.2f}",
                            dict(metrics["peak_hours"])  # Convert defaultdict to dict for readability
                        ])

            return response

        except Exception as e:
            print(f"Error in ExportCSVView: {e}")
            return HttpResponse("An error occurred while exporting the CSV.", status=500)


class RoomUsageForecastCommand(BaseCommand):
    """
    Command to forecast room usage for the next 30 days.
    """
    help = "Generate room usage forecasts"

    def handle(self, *args, **kwargs):
        data = Analytics.objects.values("date", "total_bookings")
        df = pd.DataFrame(data)
        df.rename(columns={"date": "ds", "total_bookings": "y"}, inplace=True)

        # Train and forecast
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Visualization
        model.plot(forecast)
        plt.title("Room Usage Forecast")
        plt.xlabel("Date")
        plt.ylabel("Total Bookings")
        plt.savefig("forecast.png")
        plt.show()

class TransformedAnalyticsData(APIView):
    """
    API endpoint to return analytics data in the desired transformed structure.
    """
    def get(self, request, *args, **kwargs):
        try:
            # Fetch analytics data for the past 7 days
            past_week = now().date() - timedelta(days=7)
            analytics_data = Analytics.objects.filter(date__gte=past_week).select_related("room")

            # Prepare the transformed structure
            response_data = {
                "dates": sorted(set(analytics.date for analytics in analytics_data)),
                "data": defaultdict(lambda: {"bookings": [], "utilization": []})
            }

            # Group data by room
            room_mapping = {room.id: room.name for room in Room.objects.all()}
            for date in response_data["dates"]:
                for room_id, room_name in room_mapping.items():
                    room_analytics = analytics_data.filter(date=date, room_id=room_id).first()
                    if room_analytics:
                        response_data["data"][room_name]["bookings"].append(room_analytics.total_bookings)
                        response_data["data"][room_name]["utilization"].append(room_analytics.utilization_rate)
                    else:
                        response_data["data"][room_name]["bookings"].append(0)
                        response_data["data"][room_name]["utilization"].append(0.0)

            # Convert defaultdict to a standard dict for serialization
            response_data["data"] = dict(response_data["data"])
            return Response(response_data)

        except Exception as e:
            print(f"Error in TransformedAnalyticsData: {e}")
            return Response({"error": str(e)}, status=500)