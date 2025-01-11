# users/serializers.py
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

    # Hash password before saving
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    # Optional: Ensure that updates handle password properly
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
<<<<<<< HEAD
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

=======
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) not in [10, 15]:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

