from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """
        Retrieve notifications for the logged-in user.
        Optional query parameter `unread` to filter unread notifications.
        """
        user = request.user
        unread_only = request.query_params.get('unread', 'false').lower() == 'true'
        notifications = Notification.objects.filter(user=user)
        if unread_only:
            notifications = notifications.filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read."})
        return Response({"message": "Notification is already marked as read."}, status=400)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications for the logged-in user as read.
        """
        user = request.user
        unread_notifications = Notification.unread_notifications(user)
        unread_notifications.update(is_read=True)
        return Response({"message": f"All unread notifications marked as read for user {user.username}."})
