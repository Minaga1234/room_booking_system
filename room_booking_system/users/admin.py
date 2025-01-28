from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing CustomUser objects.
    """
    list_display = ('id', 'username', 'email', 'role', 'phone_number', 'is_active', 'is_staff')  # Comprehensive display
    list_filter = ('role', 'is_active')  # Filter by role and active status
    search_fields = ('username', 'email')  # Enable search by username and email
    actions = ['deactivate_users', 'activate_users', 'set_to_staff']  # Bulk actions

    def deactivate_users(self, request, queryset):
        """
        Admin action to deactivate selected users.
        """
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def activate_users(self, request, queryset):
        """
        Admin action to activate selected users.
        """
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

    def set_to_staff(self, request, queryset):
        """
        Admin action to set selected users' role to staff.
        """
        queryset.update(role='staff')
        self.message_user(request, "Selected users have been updated to 'staff' role.")
    set_to_staff.short_description = "Set selected users as staff"
