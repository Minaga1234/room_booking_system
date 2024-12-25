from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class NotificationTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")
        self.notification = Notification.objects.create(
            user=self.user,
            message="Test notification",
            notification_type="general"
        )

    def test_notification_creation(self):
        """Test that a notification is created correctly."""
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.message, "Test notification")
        self.assertEqual(self.notification.notification_type, "general")
        self.assertFalse(self.notification.is_read)

    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        self.notification.mark_as_read()
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
