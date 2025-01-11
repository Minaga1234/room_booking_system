from rest_framework import serializers
from .models import Branding, Degree, Theme

class ThemeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Theme model.
    """
    class Meta:
        model = Theme
        fields = '__all__'

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ['id', 'name']  # Removed the non-existent `branding` field

class BrandingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Branding model, including related degrees and theme.
    """
    degrees = DegreeSerializer(many=True, read_only=True)  # Include related degrees dynamically
    theme = ThemeSerializer(read_only=True)  # Include theme details dynamically
    theme_id = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(),
        source='theme',
        write_only=True
    )  # Allows assigning a theme by ID during updates

    class Meta:
        model = Branding
        fields = [
            'id',
            'institute_name',
            'favicon',
            'login_background',
            'theme',
            'theme_id',  # For theme assignment
            'degrees',
            'updated_at',
        ]
