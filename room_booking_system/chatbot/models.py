from django.db import models
from django.conf import settings

class ChatbotLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatbotLog for {self.user.username} at {self.created_at}"
