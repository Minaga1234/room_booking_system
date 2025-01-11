from django.contrib import admin
from .models import Penalty


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'reason', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reason')

    actions = ['mark_as_paid', 'mark_as_unpaid']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, "Selected penalties have been marked as paid.")
    mark_as_paid.short_description = "Mark selected penalties as paid"

    def mark_as_unpaid(self, request, queryset):
        queryset.update(status='unpaid')
        self.message_user(request, "Selected penalties have been marked as unpaid.")
    mark_as_unpaid.short_description = "Mark selected penalties as unpaid"
