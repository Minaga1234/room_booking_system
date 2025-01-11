from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'', BookingViewSet, basename="booking")  # Removed the 'bookings' prefix

urlpatterns = router.urls  # Directly use router.urls without additional prefixes
