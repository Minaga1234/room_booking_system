from rest_framework import viewsets, permissions
from rest_framework.response import Response  # Import Response
from django.utils import timezone  # Import timezone
from rest_framework.decorators import action
from .models import Room, UsageLog
from bookings.models import Booking  # Import Booking directly
from .serializers import RoomSerializer, UsageLogSerializer
from .permissions import IsAdminOrReadOnly  # Custom permission

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]  # Admins can modify; others can only view

    def get_queryset(self):
        """
        Override the default queryset to apply filters dynamically.
        """
        queryset = super().get_queryset()
        # Filter out soft-deleted rooms
        queryset = queryset.filter(is_deleted=False)

        # Filter by availability
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')

        # Filter by requires_approval
        requires_approval = self.request.query_params.get('requires_approval')
        if requires_approval is not None:
            queryset = queryset.filter(requires_approval=requires_approval.lower() == 'true')

        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by minimum capacity
        capacity = self.request.query_params.get('capacity')
        if capacity:
            try:
                capacity = int(capacity)
                queryset = queryset.filter(capacity__gte=capacity)
            except ValueError:
                pass  # Ignore invalid capacity values

        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a room by marking it as deleted.
        """
        room = self.get_object()
        room.is_deleted = True
        room.save()
        return Response({"message": "Room deleted (soft delete)"}, status=204)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start_usage(self, request, pk=None):
        """
        Start room usage for a user.
        """
        room = self.get_object()
        log = UsageLog.objects.create(
            room=room, user=request.user, start_time=timezone.now()
        )
        return Response({"message": "Room usage started.", "log": UsageLogSerializer(log).data})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def end_usage(self, request, pk=None):
        """
        End room usage for a user.
        """
        room = self.get_object()
        log = UsageLog.objects.filter(room=room, user=request.user, end_time__isnull=True).last()
        if not log:
            return Response({"error": "No active usage found."}, status=400)

        log.end_time = timezone.now()
        log.save()
        return Response({"message": "Room usage ended.", "log": UsageLogSerializer(log).data})
