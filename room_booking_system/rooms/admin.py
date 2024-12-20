from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_available', 'requires_approval')
    search_fields = ('name', 'location')
    list_filter = ('is_available', 'requires_approval')
