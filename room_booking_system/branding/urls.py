from django.urls import path
from .views import (
    BrandingSettingsView,
    BrandingSettingsAPI,
    BrandingAssetsAPI,  
    DegreeView,
    ThemeListCreateAPIView,
    ThemeDetailAPIView,
)

app_name = "branding"

urlpatterns = [
    path("", BrandingSettingsView.as_view(), name="branding-settings"),
    path("settings/", BrandingSettingsAPI.as_view(), name="branding-settings-api"),
    path("assets/", BrandingAssetsAPI.as_view(), name="branding-assets"),  # Add this
    path("degrees/", DegreeView.as_view(), name="degrees"),
    path("themes/", ThemeListCreateAPIView.as_view(), name="theme-list-create"),
    path("themes/<int:pk>/", ThemeDetailAPIView.as_view(), name="theme-detail"),
]
