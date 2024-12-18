from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Booking
from rooms.models import Room

class BookingTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10)
        self.booking = Booking.objects.create(
            user=self.user, room=self.room, start_time="2024-12-20T10:00:00Z", end_time="2024-12-20T12:00:00Z"
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.status, "pending")
        self.assertEqual(self.booking.is_approved, False)
