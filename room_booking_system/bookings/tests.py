from django.test import TestCase
from django.utils.timezone import now, timedelta
from bookings.models import Booking
from rooms.models import Room
from analytics.models import Analytics
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class BookingTestCase(TestCase):
    def setUp(self):
        # Create test room and user
        self.room = Room.objects.create(name="Test Room", capacity=10, location="Test Building")
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")
        self.start_time = now()
        self.end_time = self.start_time + timedelta(hours=2)

    def test_overlapping_booking_restriction(self):
        """Ensure overlapping bookings are restricted."""
        Booking.objects.create(user=self.user, room=self.room, start_time=self.start_time, end_time=self.end_time, status="approved")
        with self.assertRaises(ValidationError):
            Booking.objects.create(user=self.user, room=self.room, start_time=self.start_time, end_time=self.end_time)

    def test_approve_booking(self):
        """Test approving a booking."""
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.start_time,
            end_time=self.end_time,
            price=100.0,  # Include price
        )
        booking.approve()
        self.assertTrue(booking.is_approved)
        self.assertEqual(booking.status, "approved")

    def test_cancel_booking(self):
        """Test canceling a booking."""
        booking = Booking.objects.create(user=self.user, room=self.room, start_time=self.start_time, end_time=self.end_time)
        booking.cancel()
        self.assertEqual(booking.status, "canceled")

    def test_check_in_booking(self):
        """Test checking in a booking."""
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.start_time,
            end_time=self.end_time,
            status="approved",
            price=100.0,
        )
        booking.check_in()
        self.assertTrue(booking.checked_in)
        self.assertEqual(booking.status, "checked_in")  # Verify status is updated

    def test_dynamic_pricing(self):
        """Ensure dynamic pricing is applied based on utilization rate."""
        analytics = Analytics.objects.create(room=self.room, date=self.start_time.date(), utilization_rate=85.0)
        price = Booking.calculate_dynamic_price(self.room, self.start_time, base_price=100)
        self.assertEqual(price, 150.0)  # 50% increase for high utilization

    def test_peak_usage_restriction(self):
        """Test restriction of booking during peak hours."""
        analytics = Analytics.objects.create(room=self.room, date=self.start_time.date(), utilization_rate=85.0, peak_hours={"10:00-11:00": 6})
        booking = Booking(
            user=self.user,
            room=self.room,
            start_time=self.start_time.replace(hour=10, minute=0),
            end_time=self.start_time.replace(hour=11, minute=0),
        )
        with self.assertRaises(ValidationError):
            booking.clean()

    def test_booking_duration_validation(self):
        """Ensure start time is before end time."""
        with self.assertRaises(ValidationError):
            Booking.objects.create(user=self.user, room=self.room, start_time=self.end_time, end_time=self.start_time)
