from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, FeedbackReportView

router = DefaultRouter()
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),  # Main router paths
    path('feedback/report/', FeedbackReportView.as_view(), name='feedback-report'),
]
