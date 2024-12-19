from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'start_time', 'end_time', 'status', 'is_approved')
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('user__username', 'room__name')
