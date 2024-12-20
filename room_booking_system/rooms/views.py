from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room
from .serializers import RoomSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_rooms = Room.objects.filter(is_available=True)
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)
