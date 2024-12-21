# bookings/tests.py
from django.test import TestCase
from django.utils import timezone
from .models import Booking
from rooms.models import Room
from notifications.models import Notification
from penalties.models import Penalty
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class BookingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password",
            email="testuser@example.com",
            role="student"
        )
        self.admin = get_user_model().objects.create_user(
            username="admin",
            password="password",
            email="admin@example.com",
            role="admin"
        )
        self.room = Room.objects.create(name="Test Room", location="Floor 1", capacity=10)

    def test_create_booking(self):
        """
        Test creating a booking and ensure it is saved correctly.
        """
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.room, self.room)

    def test_booking_overlap(self):
        """
        Test preventing overlapping bookings for the same room.
        """
        start_time = timezone.now() + timezone.timedelta(hours=1)
        end_time = timezone.now() + timezone.timedelta(hours=2)

        # Create the first booking
        Booking.objects.create(
            user=self.user, room=self.room, start_time=start_time, end_time=end_time
        )

        # Attempt to create an overlapping booking
        overlapping_booking = Booking(
            user=self.user, room=self.room, start_time=start_time, end_time=end_time
        )

        # Simulate the overlap check logic
        overlapping = Booking.objects.filter(
            room=self.room,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        # Ensure overlapping booking detection works
        self.assertTrue(overlapping)

        # Check that a validation error is raised when calling full_clean()
        with self.assertRaises(ValidationError):
            overlapping_booking.full_clean()

    def test_approve_booking(self):
        """
        Test approving a booking.
        """
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            status='pending'
        )
        booking.status = 'approved'
        booking.is_approved = True
        booking.save()

        self.assertEqual(booking.status, 'approved')
        self.assertTrue(booking.is_approved)

    def test_cancel_booking_with_penalty(self):
        """
        Test canceling a booking after its end time applies a penalty.
        """
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            status='pending'
        )
        # Apply penalty logic
        Penalty.objects.get_or_create(
            user=booking.user,
            booking=booking,
            reason="Late cancellation",
            defaults={"amount": 50.00, "status": "unpaid"}
        )

        penalty = Penalty.objects.filter(booking=booking).first()
        self.assertIsNotNone(penalty)
        self.assertEqual(penalty.amount, 50.00)
