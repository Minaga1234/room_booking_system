from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now
from notifications.models import Notification
from users.models import CustomUser
from bookings.models import Booking
from rooms.models import Room
from datetime import timedelta  # Add this import

class NotificationModelTestCase(TestCase):
    """
    Test cases for Notification model methods.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.notification = Notification.objects.create(
            user=self.user,
            message="Test notification message",
            notification_type="general",
        )

    def test_create_notification(self):
        """
        Test the creation of a notification.
        """
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(self.notification.user, self.user)
        self.assertFalse(self.notification.is_read)

    def test_mark_as_read(self):
        """
        Test marking a notification as read.
        """
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)

    def test_mark_as_unread(self):
        """
        Test marking a notification as unread.
        """
        self.notification.mark_as_read()
        self.notification.mark_as_unread()
        self.assertFalse(self.notification.is_read)

    def test_unread_notifications(self):
        """
        Test retrieving unread notifications.
        """
        unread = Notification.unread_notifications(self.user)
        self.assertIn(self.notification, unread)


class NotificationAPITestCase(TestCase):
    """
    Test cases for Notification API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)
        self.booking = Booking.objects.create(
            user=self.user, room=self.room, start_time=now(), end_time=now() + timedelta(hours=1)
        )
        self.notification1 = Notification.objects.create(
            user=self.user,
            booking=self.booking,
            message="Test notification for booking",
            notification_type="booking_update",
        )
        self.notification2 = Notification.objects.create(
            user=self.user,
            message="Test penalty reminder",
            notification_type="penalty_reminder",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_notifications(self):
        """
        Test retrieving the list of notifications for a user.
        """
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Dynamically calculate the expected number of notifications
        expected_count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(len(response.data), expected_count)

    def test_filter_unread_notifications(self):
        """
        Test filtering unread notifications.
        """
        response = self.client.get("/notifications/", {"unread": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Dynamically calculate the expected unread notifications
        unread_count = Notification.unread_notifications(self.user).count()
        self.assertEqual(len(response.data), unread_count)  # Verify unread notifications

    def test_mark_as_read(self):
        """
        Test marking a notification as read.
        """
        notification = Notification.objects.first()
        response = self.client.post(f"/notifications/{notification.id}/mark_as_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_as_read(self):
        """
        Test marking all notifications as read.
        """
        response = self.client.post("/notifications/mark_all_as_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread_notifications = Notification.unread_notifications(self.user)
        self.assertFalse(unread_notifications.exists())