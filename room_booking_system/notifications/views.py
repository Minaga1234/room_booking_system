from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.exceptions import NotAuthenticated

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]  # Allows both authenticated and anonymous users

    def get_queryset(self):
        """
        Allow anonymous users to access general notifications.
        Authenticated users see their specific notifications.
        """
        user = self.request.user
        print(f"Authenticated user: {user} | Authenticated? {user.is_authenticated}")  # Debugging
        
        if user.is_authenticated:
            return Notification.objects.filter(user=user)  # Return user-specific notifications
        else:
            return Notification.objects.all()  # Allow anonymous users to see all notifications

    def list(self, request, *args, **kwargs):
        """
        Override default list() to return JSON object instead of array.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {"notifications": serializer.data}  # Wrap response inside a dictionary

        print("📌 Returning Notifications:", response_data)  # Debugging log

        return Response(response_data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        if not notification.is_read:
            notification.mark_as_read()
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
