from django.db import models
from users.models import CustomUser
from rooms.models import Room  # Assuming a Room model exists in the rooms app

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, default="Anonymous User")  # Default value
    field_of_study = models.CharField(max_length=255, default="Bsc Computer Science major in Software Engineering")  # Default value
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    student_id = models.CharField(max_length=20, default=0000000)
    content = models.TextField()
    rating = models.IntegerField()
    sentiment = models.CharField(max_length=10, blank=True, null=True)
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.content[:20]}"

    class Meta:
        ordering = ['-created_at']
