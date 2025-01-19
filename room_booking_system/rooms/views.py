from rest_framework import viewsets, permissions
from rest_framework.response import Response  # Import Response
from django.utils import timezone  # Import timezone
from rest_framework.decorators import action
from .models import Room, UsageLog
from bookings.models import Booking  # Import Booking directly
from .serializers import RoomSerializer, UsageLogSerializer
from .permissions import IsAdminOrReadOnly  # Custom permission
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from users.permissions import IsAdminOrStaff, IsAdmin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read-only access for unauthenticated users

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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve_room(self, request, pk=None):
        """
        Approve a room. Only admins can perform this action.
        """
        room = self.get_object()
        room.requires_approval = False
        room.save()
        return Response({"message": f"Room {room.name} approved."})

@api_view(['GET'])
def room_availability(request, pk):
    """
    Check availability of a room for a given time slot.
    """
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    if not start_time or not end_time:
        return Response({"error": "start_time and end_time are required parameters."}, status=400)

    try:
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
    except ValueError:
        return Response({"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."}, status=400)

    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response({"error": "Room not found."}, status=404)

    overlapping_bookings = Booking.objects.filter(
        room=room,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if overlapping_bookings.exists():
        return Response({"available": False, "message": "The room is not available for the selected time slot."})

    return Response({"available": True, "message": "The room is available for the selected time slot."})