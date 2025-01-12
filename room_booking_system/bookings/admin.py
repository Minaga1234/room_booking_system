from django.contrib import admin
from .models import Booking
from notifications.models import Notification


class NotificationInline(admin.TabularInline):
    model = Notification
    fields = ('message', 'notification_type', 'is_read', 'created_at')
    readonly_fields = ('message', 'notification_type', 'is_read', 'created_at')
    extra = 0
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'degree_major', 'purpose', 'start_time', 'end_time', 'status', 'is_approved')
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('user__username', 'room__name')
    inlines = [NotificationInline]  # Include related notifications inline

    actions = ['approve_bookings', 'cancel_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(status='approved', is_approved=True)
        self.message_user(request, "Selected bookings have been approved.")
    approve_bookings.short_description = "Approve selected bookings"

    def cancel_bookings(self, request, queryset):
        queryset.update(status='canceled', is_approved=False)
        self.message_user(request, "Selected bookings have been canceled.")
    cancel_bookings.short_description = "Cancel selected bookings"
