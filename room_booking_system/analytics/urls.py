from django.urls import path
from .views import AnalyticsViewSet, AnalyticsChartData, ChartView, weekly_utilization_heatmap, ExportCSVView
from rest_framework.routers import DefaultRouter

# Router for API endpoints
router = DefaultRouter()
router.register(r'', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('chart-data/', AnalyticsChartData.as_view(), name='analytics-chart-data'),
    path('charts/', ChartView.as_view(), name='analytics-charts'),
    path('heatmap/', weekly_utilization_heatmap, name='weekly-utilization-heatmap'),
    path('export_csv/', ExportCSVView.as_view(), name='analytics-export-csv'),
]

urlpatterns += router.urls