from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from django.utils.crypto import get_random_string


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'phone_number', 'is_active']
        extra_kwargs = {
            'username': {'read_only': True},  # Auto-generated, read-only
            'email': {'required': True},  # Email is required during creation
            'password': {'write_only': True, 'required': False},  # Password is write-only and optional
            'phone_number': {'required': False},  # Optional phone number
        }

    def create(self, validated_data):
        # Auto-generate username from email
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
        validated_data['username'] = email.split('@')[0]

        # Auto-generate a random password if not provided
        if 'password' not in validated_data or not validated_data['password']:
            random_password = get_random_string(8)
            validated_data['password'] = random_password  # Pass the generated password back if needed
            print(f"Generated password for {validated_data['email']}: {random_password}")

        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])

        # Create the user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent email from being updated
        validated_data.pop('email', None)

        # Handle password updates only if provided
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate_email(self, value):
        # Ensure email is unique
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_phone_number(self, value):
        # Handle None values and validate phone number format
        if value is not None:
            if not value.isdigit() or len(value) not in [10, 15]:
                raise serializers.ValidationError("Enter a valid phone number.")
        return value