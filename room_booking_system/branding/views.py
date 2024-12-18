from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Branding
from .serializers import BrandingSerializer

class BrandingViewSet(viewsets.ModelViewSet):
    queryset = Branding.objects.all()
    serializer_class = BrandingSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        branding = Branding.objects.last()  # Assuming the latest branding is the active one
        serializer = self.get_serializer(branding)
        return Response(serializer.data)
