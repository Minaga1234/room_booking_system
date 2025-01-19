# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from django.utils.crypto import get_random_string

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'phone_number', 'is_active']
        extra_kwargs = {
            'username': {'required': False},  # Allow partial updates
            'username': {'read_only': True},  # Auto-generated
            'email': {'required': False},
            'password': {'write_only': True, 'required': False},  # Make password optional for updates
            'phone_number': {'required': False},
        }

    def create(self, validated_data):
        email = validated_data.get('email')
        validated_data['username'] = email.split('@')[0]  # Generate username from email

        if 'password' not in validated_data:
            validated_data['password'] = get_random_string(8)  # Generate random 8-character password

        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle password updates only if provided
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)

        # Ensure the username is unique only if changed
        username = validated_data.get('username', instance.username)
        if username != instance.username and CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) not in [10, 15]:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

