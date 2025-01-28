from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PenaltyViewSet, penalties_overview

router = DefaultRouter()
router.register(r'', PenaltyViewSet)

urlpatterns = [
    path('overview/', penalties_overview, name='penalties-overview'),  # Add the overview endpoint
    path('download-report/', PenaltyViewSet.as_view({'get': 'download_report'}), name='penalties-download-report'),  # Add the download report endpoint
    path('penalties/user/', PenaltyViewSet.as_view({'get': 'user_penalties'}), name='user-penalties'),
    path('penalties/<int:pk>/request-review/', PenaltyViewSet.as_view({'post': 'request_review'}), name='request-review'),
    path('', include(router.urls)),
]
