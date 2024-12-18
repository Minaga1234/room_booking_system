from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notification

class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.notification = Notification.objects.create(
            user=self.user, message="Test Notification", notification_type="general"
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.is_read, False)
        self.assertEqual(self.notification.message, "Test Notification")
