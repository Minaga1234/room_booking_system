from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

app_name = 'notifications'  # Set the namespace

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = router.urls
