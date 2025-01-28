from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the theme")
    primary_color = models.CharField(max_length=7, default="#007BFF", help_text="Primary color in HEX.")
    secondary_color = models.CharField(max_length=7, default="#6C757D", help_text="Secondary color in HEX.")
    tertiary_color = models.CharField(max_length=7, default="#F8F9FA", help_text="Tertiary color in HEX.")
    accent_success = models.CharField(max_length=7, default="#28A745", help_text="Accent color for success.")
    accent_warning = models.CharField(max_length=7, default="#FFC107", help_text="Accent color for warnings.")
    accent_error = models.CharField(max_length=7, default="#DC3545", help_text="Accent color for errors.")
    header_font = models.CharField(max_length=100, default="Arial", help_text="Header font family.")
    body_font = models.CharField(max_length=100, default="Roboto", help_text="Body font family.")
    background_color = models.CharField(max_length=7, default="#0E1924", help_text="Background color in HEX.")
    card_background = models.CharField(max_length=7, default="#FFFFFF", help_text="Card background color in HEX.")
    text_color = models.CharField(max_length=7, default="#292E4A", help_text="Text color in HEX.")
    highlight_color = models.CharField(max_length=7, default="#FF6600", help_text="Highlight color in HEX.")
    shadow_color = models.CharField(max_length=50, default="rgba(0, 0, 0, 0.15)", help_text="Shadow color in RGBA.")
    shadow_hover_color = models.CharField(max_length=50, default="rgba(0, 0, 0, 0.25)", help_text="Shadow hover color in RGBA.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the theme was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the theme was last updated.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Theme"
        verbose_name_plural = "Themes"


class Branding(models.Model):
    institute_name = models.CharField(max_length=255, default="My Institute", help_text="The name of the institute.")
    favicon = models.ImageField(upload_to="branding/icons/", null=True, blank=True, help_text="Upload the favicon/icon.")
    login_background = models.ImageField(upload_to="branding/backgrounds/", null=True, blank=True, help_text="Upload the login page background.")
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True, related_name="brandings", help_text="The selected theme for the branding.")

    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated timestamp.")

    def __str__(self):
        return self.institute_name

    class Meta:
        verbose_name = "Branding Settings"
        verbose_name_plural = "Branding Settings"


class Degree(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the degree")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Degree"
        verbose_name_plural = "Degrees"


