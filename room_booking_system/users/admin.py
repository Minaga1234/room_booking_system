# users/admin.py
from django.contrib import admin
from .models import CustomUser

<<<<<<< HEAD

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    actions = ['deactivate_users', 'activate_users', 'set_to_staff']

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

    def set_to_staff(self, request, queryset):
        queryset.update(role='staff')
        self.message_user(request, "Selected users have been updated to 'staff' role.")
    set_to_staff.short_description = "Set selected users as staff"
=======
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'phone_number', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_active']
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
