from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, get_csrf_token

# Create a DefaultRouter and register the UserViewSet
router = DefaultRouter()
<<<<<<< HEAD
router.register(r'', UserViewSet, basename='customuser')

# Define urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Register all routes from the router
    path('register/', UserViewSet.as_view({'post': 'register_user'}), name='register_user'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='user_login'),  # Login endpoint
    path('profile/', UserViewSet.as_view({'get': 'profile', 'put': 'update_profile'}), name='user_profile'),  # Profile endpoint
    path('change_password/', UserViewSet.as_view({'post': 'change_password'}), name='change_password'),  # Password change
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),  # CSRF token endpoint
]
=======
router.register(r'', UserViewSet, basename='user')  # Register the main viewset

urlpatterns = router.urls
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
