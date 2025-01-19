# users/admin.py
from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'phone_number', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_active']
