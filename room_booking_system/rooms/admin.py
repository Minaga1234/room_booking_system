from django.contrib import admin
from .models import Room, UsageLog


class UsageLogInline(admin.TabularInline):
    model = UsageLog
    fields = ('user', 'start_time', 'end_time', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_available', 'requires_approval', 'is_deleted')
    list_filter = ('is_available', 'requires_approval', 'is_deleted', 'created_at')
    search_fields = ('name', 'location')
    inlines = [UsageLogInline]
    actions = ['restore_rooms']

    def restore_rooms(self, request, queryset):
        queryset.update(is_deleted=False)
        self.message_user(request, "Selected rooms have been restored.")
    restore_rooms.short_description = "Restore selected rooms"
