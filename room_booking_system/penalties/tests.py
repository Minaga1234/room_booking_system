from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Penalty
from bookings.models import Booking
from rooms.models import Room

class PenaltyTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10)
        self.booking = Booking.objects.create(
            user=self.user, room=self.room, start_time="2024-12-20T10:00:00Z", end_time="2024-12-20T12:00:00Z"
        )
        self.penalty = Penalty.objects.create(
            user=self.user, booking=self.booking, reason="Test Penalty", amount=25.00
        )

    def test_penalty_creation(self):
        self.assertEqual(self.penalty.status, "unpaid")
        self.assertEqual(self.penalty.amount, 25.00)
