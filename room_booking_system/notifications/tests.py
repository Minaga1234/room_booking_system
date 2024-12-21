# notifications/tests.py
from django.test import TestCase
from .models import Notification
from django.contrib.auth import get_user_model

class NotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password",
            email="testuser@example.com",
            role="student"
        )

    def test_create_notification(self):
        """
        Test creating a notification for a user.
        """
        notification = Notification.objects.create(
            user=self.user,
            message="Your booking has been approved.",
            notification_type="booking_update"
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "Your booking has been approved.")
        self.assertFalse(notification.is_read)

    def test_mark_notification_as_read(self):
        """
        Test marking a notification as read.
        """
        notification = Notification.objects.create(
            user=self.user,
            message="Your booking has been approved.",
            notification_type="booking_update"
        )
        notification.is_read = True
        notification.save()

        self.assertTrue(notification.is_read)

    def test_retrieve_unread_notifications(self):
        """
        Test retrieving all unread notifications for a user.
        """
        Notification.objects.create(user=self.user, message="Test 1", notification_type="general")
        Notification.objects.create(user=self.user, message="Test 2", notification_type="penalty_reminder", is_read=True)

        unread_notifications = Notification.objects.filter(user=self.user, is_read=False)
        self.assertEqual(unread_notifications.count(), 1)