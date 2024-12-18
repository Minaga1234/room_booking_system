from django.db import models

class Branding(models.Model):
    institution_name = models.CharField(max_length=100)
    logo_path = models.ImageField(upload_to='branding/logos/', blank=True, null=True)
    favicon_path = models.ImageField(upload_to='branding/favicons/', blank=True, null=True)
    cover_photo_path = models.ImageField(upload_to='branding/covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institution_name
