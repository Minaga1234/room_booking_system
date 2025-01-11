from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'phone_number', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def create(self, validated_data):
        """
        Hash password before saving a new user.
        """
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Handle password updates separately while ensuring password is hashed.
        """
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

    def validate_email(self, value):
        """
        Validate email to ensure uniqueness.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
<<<<<<< HEAD
=======
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109

    def validate_phone_number(self, value):
        """
        Validate phone number format.
        """
        if not value.isdigit() or len(value) not in [10, 15]:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value
