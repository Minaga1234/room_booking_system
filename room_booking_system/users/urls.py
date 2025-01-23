from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, get_csrf_token

# Create a DefaultRouter and register the UserViewSet
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Main ViewSet registration

# Define urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Register routes from the DefaultRouter
    path('register/', UserViewSet.as_view({'post': 'register_user'}), name='register_user'),  # Registration endpoint
    path('login/', UserViewSet.as_view({'post': 'login'}), name='user_login'),  # Login endpoint
    path('profile/', UserViewSet.as_view({'get': 'profile', 'put': 'update_profile'}), name='user_profile'),  # Profile endpoint
    path('change_password/', UserViewSet.as_view({'post': 'change_password'}), name='change_password'),  # Password change
    path('deactivate/', UserViewSet.as_view({'post': 'deactivate_self'}), name='deactivate_self'),  # Self-deactivation
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),  # CSRF token endpoint
]
