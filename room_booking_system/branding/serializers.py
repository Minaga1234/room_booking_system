from rest_framework import serializers
from .models import Branding

class BrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branding
        fields = '__all__'
