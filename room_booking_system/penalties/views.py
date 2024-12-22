from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Penalty
from .serializers import PenaltySerializer

class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        penalty = self.get_object()
        if penalty.status == 'unpaid':
            penalty.status = 'paid'
            penalty.save()
            return Response({"message": "Penalty marked as paid."})
        return Response({"message": "Penalty is already paid."}, status=400)

    @action(detail=False, methods=['get'])
    def user_penalties(self, request):
        user = request.user
        penalties = Penalty.objects.filter(user=user)
        serializer = self.get_serializer(penalties, many=True)
        return Response(serializer.data)
