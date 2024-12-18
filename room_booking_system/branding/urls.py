from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandingViewSet

router = DefaultRouter()
router.register(r'', BrandingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
