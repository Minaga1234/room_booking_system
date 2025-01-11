from django.contrib import admin
from .models import Analytics


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'total_bookings', 'total_checkins', 'utilization_rate', 'last_updated')
    list_filter = ('date', 'room')
    search_fields = ('room__name',)
