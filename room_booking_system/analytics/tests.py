from django.test import TestCase
from django.utils.timezone import now, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from analytics.models import Analytics
from rooms.models import Room
from bookings.models import Booking
from users.models import CustomUser


class AnalyticsModelTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Room 1", location="First Floor", capacity=10, is_available=True)
        self.analytics = Analytics.objects.create(
            room=self.room,
            total_bookings=5,
            total_checkins=3,
            total_cancellations=2,
            utilization_rate=50.0
        )

    def test_analytics_creation(self):
        """Test that analytics records are created correctly."""
        self.assertEqual(self.analytics.total_bookings, 5)
        self.assertEqual(self.analytics.utilization_rate, 50.0)

    def test_analytics_update_on_booking_creation(self):
        """Test that analytics are updated when a booking is created."""
        Booking.objects.create(
            user=CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password"),
            room=self.room,
            start_time=now(),
            end_time=now() + timedelta(hours=1),
        )
        updated_analytics = Analytics.objects.get(room=self.room)
        self.assertEqual(updated_analytics.total_bookings, 6)


class AnalyticsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="admin"
        )
        self.client.force_authenticate(user=self.user)
        self.room = Room.objects.create(name="Room 1", location="First Floor", capacity=10, is_available=True)
        self.analytics = Analytics.objects.create(
            room=self.room,
            total_bookings=5,
            total_checkins=3,
            total_cancellations=2,
            utilization_rate=50.0
        )

    def test_get_analytics_list(self):
        """Test retrieving analytics list."""
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_bookings', response.data[0])

    def test_get_chart_data(self):
        """Test retrieving chart data."""
        response = self.client.get('/analytics/chart-data/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rooms', response.data)


class AnalyticsSignalTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Room 1", location="First Floor", capacity=10, is_available=True)
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")

    def test_signal_on_booking_creation(self):
        """Test analytics update on booking creation via signal."""
        Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=now(),
            end_time=now() + timedelta(hours=1),
        )
        analytics = Analytics.objects.get(room=self.room)
        self.assertEqual(analytics.total_bookings, 1)

    def test_signal_on_booking_deletion(self):
        """Test analytics update on booking deletion via signal."""
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=now(),
            end_time=now() + timedelta(hours=1),
        )
        booking.delete()
        analytics = Analytics.objects.get(room=self.room)
        self.assertEqual(analytics.total_bookings, 0)
