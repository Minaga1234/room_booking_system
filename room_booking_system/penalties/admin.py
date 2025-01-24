from django.contrib import admin
from .models import Penalty


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    # Customize the list display
    list_display = ('user', 'booking', 'reason', 'amount', 'get_status_display', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reason')

    # Add bulk actions
    actions = ['mark_as_paid', 'mark_as_active']

    # Display 'Unpaid' instead of 'Active' in the admin panel
    def get_status_display(self, obj):
        return 'Unpaid' if obj.status == 'Active' else obj.status
    get_status_display.short_description = 'Status'

    # Action to mark penalties as paid
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, "Selected penalties have been marked as paid.")
    mark_as_paid.short_description = "Mark selected penalties as paid"

    # Action to mark penalties as active (unpaid)
    def mark_as_active(self, request, queryset):
        queryset.update(status='Active')
        self.message_user(request, "Selected penalties have been marked as unpaid (Active).")
    mark_as_active.short_description = "Mark selected penalties as unpaid"
