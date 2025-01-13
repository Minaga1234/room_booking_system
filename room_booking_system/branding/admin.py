from django.contrib import admin
from .models import Branding, Degree, Theme

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Admin interface for the Theme model.
    """
    list_display = ("name", "primary_color", "secondary_color", "tertiary_color", "updated_at")
    fieldsets = (
        ("General Information", {
            "fields": ("name",)
        }),
        ("Colors", {
            "fields": ("primary_color", "secondary_color", "tertiary_color", 
                       "accent_success", "accent_warning", "accent_error")
        }),
        ("Typography", {
            "fields": ("header_font", "body_font")
        }),
    )
    search_fields = ("name",)
    list_filter = ("updated_at",)


@admin.register(Branding)
class BrandingAdmin(admin.ModelAdmin):
    """
    Admin interface for the Branding model.
    """
    list_display = ("institute_name", "theme", "updated_at")
    fieldsets = (
        ("General", {
            "fields": ("institute_name", "favicon", "login_background", "theme")
        }),
    )
    search_fields = ("institute_name",)
    list_filter = ("updated_at",)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Remove 'branding'
    search_fields = ('name',)  # Search functionality for degree names
    list_filter = ()  # Remove 'branding' from filters if it was there
    ordering = ('name',)


from django.contrib import admin
from .models import Degree, Theme, Branding



