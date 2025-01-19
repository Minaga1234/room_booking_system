from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, room_availability
from django.urls import path, include

router = DefaultRouter()
router.register(r'', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),  # Standard router URLs
    path('<int:pk>/availability/', room_availability, name='room-availability'),  # Add room availability endpoint
]
