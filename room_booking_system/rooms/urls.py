<<<<<<< HEAD
#rooms/urls.py
=======
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet

router = DefaultRouter()
router.register(r'', RoomViewSet, basename='room')

urlpatterns = router.urls
