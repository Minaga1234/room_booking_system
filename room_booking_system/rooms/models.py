from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"
