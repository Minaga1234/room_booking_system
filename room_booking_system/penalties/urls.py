from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PenaltyViewSet

router = DefaultRouter()
router.register(r'', PenaltyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
