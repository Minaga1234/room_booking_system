from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'', BookingViewSet, basename="booking")

urlpatterns = [
    path('', include(router.urls)),
    path('popular_rooms/', BookingViewSet.as_view({'get': 'popular_rooms'}), name='popular_rooms'),
    path('traffic_data/', BookingViewSet.as_view({'get': 'traffic_data'}), name='traffic_data'),
    path('calendar_events/', BookingViewSet.as_view({'get': 'calendar_events'}), name='calendar_events'),
    path('my_bookings/', BookingViewSet.as_view({'get': 'my_bookings'}), name='my_bookings'),  # Added my_bookings
]
