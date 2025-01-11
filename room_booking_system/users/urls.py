#Users/urls.py
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
<<<<<<< HEAD

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Register the main viewset

urlpatterns = router.urls
=======

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Register the main viewset

urlpatterns = router.urls

>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
