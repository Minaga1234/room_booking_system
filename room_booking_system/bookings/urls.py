from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'', BookingViewSet, basename="booking")  # Removed the 'bookings' prefix

<<<<<<< HEAD
urlpatterns = [
    path('', include(router.urls)),
    path('popular_rooms/', BookingViewSet.as_view({'get': 'popular_rooms'}), name='popular_rooms'),
    path('traffic_data/', BookingViewSet.as_view({'get': 'traffic_data'}), name='traffic_data'),
]
=======
urlpatterns = router.urls  # Directly use router.urls without additional prefixes
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
