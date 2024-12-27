from django.test import TestCase
from .models import Penalty
from bookings.models import Booking
from rooms.models import Room
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Use the custom user model

def setUp(self):
    self.user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",  # Add email field
        password="password"
    )

class PenaltyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="password")
        self.room = Room.objects.create(name="Test Room", location="Floor 1", capacity=10)
        self.booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            status='pending'
        )

    def test_create_penalty(self):
        """
        Test creating a penalty for a booking.
        """
        penalty = Penalty.objects.create(
            user=self.user,
            booking=self.booking,
            reason="No-show",
            amount=100.00,
            status="unpaid"
        )
        self.assertEqual(Penalty.objects.count(), 1)
        self.assertEqual(penalty.user, self.user)
        self.assertEqual(penalty.amount, 100.00)
        self.assertEqual(penalty.status, "unpaid")

    def test_mark_penalty_as_paid(self):
        """
        Test marking a penalty as paid.
        """
        penalty = Penalty.objects.create(
            user=self.user,
            booking=self.booking,
            reason="No-show",
            amount=100.00,
            status="unpaid"
        )
        penalty.status = "paid"
        penalty.save()

        self.assertEqual(penalty.status, "paid")

    def test_unpaid_penalty_total(self):
        """
        Test calculating total unpaid penalties for a user.
        """
        Penalty.objects.create(user=self.user, booking=self.booking, reason="No-show", amount=50.00, status="unpaid")
        Penalty.objects.create(user=self.user, booking=self.booking, reason="Late cancellation", amount=75.00, status="unpaid")

        total_unpaid = Penalty.objects.filter(user=self.user, status="unpaid").aggregate(total=models.Sum('amount'))['total']

        self.assertEqual(total_unpaid, 125.00)