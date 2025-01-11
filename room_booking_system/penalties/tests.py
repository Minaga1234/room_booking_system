from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now, timedelta
from penalties.models import Penalty
from bookings.models import Booking
from rooms.models import Room
from users.models import CustomUser
from notifications.models import Notification


class PenaltyModelTestCase(TestCase):
    """
    Test cases for the Penalty model methods.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="student"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)
        self.booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=now() + timedelta(hours=1),
            end_time=now() + timedelta(hours=2),
            status="canceled"
        )

    def test_create_penalty(self):
        """
        Test creating a penalty and notification generation.
        """
        penalty = Penalty.create_penalty(
            user=self.user,
            booking=self.booking,
            reason="Late cancellation",
            amount=50.00
        )
        self.assertEqual(Penalty.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)
        self.assertEqual(penalty.amount, 50.00)

    def test_mark_as_paid(self):
        """
        Test marking a penalty as paid and sending a notification.
        """
        penalty = Penalty.create_penalty(
            user=self.user,
            booking=self.booking,
            reason="No-show",
            amount=100.00
        )
        penalty.mark_as_paid()
        self.assertEqual(penalty.status, "paid")
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2)

    def test_get_unpaid_penalties(self):
        """
        Test retrieving the total unpaid penalties for a user.
        """
        Penalty.create_penalty(
            user=self.user,
            booking=self.booking,
            reason="Late cancellation",
            amount=50.00
        )
        unpaid_total = Penalty.get_unpaid_penalties(self.user)
        self.assertEqual(unpaid_total, 50.00)


class PenaltyAPITestCase(TestCase):
    """
    Test cases for the Penalty API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="student"
        )
        self.admin = CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass", role="admin"
        )
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10, is_available=True)
        self.booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=now() + timedelta(hours=1),
            end_time=now() + timedelta(hours=2),
            status="canceled"
        )
        self.penalty = Penalty.create_penalty(
            user=self.user,
            booking=self.booking,
            reason="Late cancellation",
            amount=50.00
        )

    def test_list_user_penalties(self):
        """
        Test retrieving penalties for the logged-in user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/penalties/user_penalties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_pay_penalty(self):
        """
        Test paying a penalty through the API.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/penalties/{self.penalty.id}/pay/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.penalty.refresh_from_db()
        self.assertEqual(self.penalty.status, "paid")
