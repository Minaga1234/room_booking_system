from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now, timedelta
from bookings.models import Booking
from rooms.models import Room
from analytics.models import Analytics
from users.models import CustomUser
from notifications.models import Notification


class BookingModelTestCase(TestCase):
    """
    Test cases for Booking model methods.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="student"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)
        self.analytics = Analytics.objects.create(room=self.room, date=now().date(), utilization_rate=50)

    def test_clean_overlapping_bookings(self):
        """
        Test that overlapping bookings are not allowed.
        """
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        Booking.objects.create(user=self.user, room=self.room, start_time=start_time, end_time=end_time)

        with self.assertRaises(Exception):
            Booking.objects.create(user=self.user, room=self.room, start_time=start_time, end_time=end_time)

    def test_dynamic_pricing(self):
        """
        Test price adjustments based on utilization rates.
        """
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        # High utilization
        self.user.role = "staff"
        self.user.save()
        self.analytics.utilization_rate = 90
        self.analytics.save()
        booking1 = Booking.objects.create(user=self.user, room=self.room, start_time=start_time, end_time=end_time)
        self.assertEqual(booking1.price, 150)

        # Low utilization (create a new Analytics object with the correct date)
        start_time_low_utilization = start_time + timedelta(days=1)
        end_time_low_utilization = end_time + timedelta(days=1)

        # Create Analytics object for low utilization
        low_utilization_analytics = Analytics.objects.create(
            room=self.room,
            date=start_time_low_utilization.date(),
            utilization_rate=20
        )

        # Debugging output
        print(f"Low utilization Analytics: Room: {low_utilization_analytics.room.name}, "
            f"Date: {low_utilization_analytics.date}, Utilization Rate: {low_utilization_analytics.utilization_rate}")

        booking2 = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=start_time_low_utilization,
            end_time=end_time_low_utilization,
        )

        print(f"Price for booking2 under low utilization: {booking2.price}")
        self.assertEqual(booking2.price, 80)  # Expect 20% discount

    def test_notifications_on_approve(self):
        """
        Test that notifications are created when a booking is approved.
        """
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        booking = Booking.objects.create(user=self.user, room=self.room, start_time=start_time, end_time=end_time)
        booking.approve()
        self.assertTrue(Notification.objects.filter(user=self.user, notification_type="booking_update").exists())


class BookingSerializerTestCase(TestCase):
    """
    Test cases for Booking serializer.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="student"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)

    def test_validate_serializer(self):
        """
        Test serializer validation for overlapping bookings and peak usage.
        """
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        data = {
            "user": self.user.id,
            "room": self.room.id,
            "start_time": start_time,
            "end_time": end_time,
        }
        from bookings.serializers import BookingSerializer
        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class BookingAPITestCase(TestCase):
    """
    Test cases for Booking API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass", role="admin"
        )
        self.student_user = CustomUser.objects.create_user(
            username="studentuser", email="student@example.com", password="password", role="student"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)
        self.start_time = now() + timedelta(hours=1)
        self.end_time = self.start_time + timedelta(hours=2)

    def test_create_booking(self):
        """
        Test booking creation.
        """
        self.client.force_authenticate(user=self.student_user)
        data = {
            "user": self.student_user.id,
            "room": self.room.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
        response = self.client.post("/api/bookings/", data, format="json")  # Ensure format="json"
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_approve_booking(self):
        """
        Test approving a booking by an admin.
        """
        booking = Booking.objects.create(
            user=self.student_user, room=self.room, start_time=self.start_time, end_time=self.end_time
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f"/api/bookings/{booking.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_booking(self):
        """
        Test canceling a booking.
        """
        booking = Booking.objects.create(
            user=self.student_user, room=self.room, start_time=self.start_time, end_time=self.end_time
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f"/api/bookings/{booking.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

