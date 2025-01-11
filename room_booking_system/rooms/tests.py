from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now, timedelta
from rooms.models import Room, UsageLog
from users.models import CustomUser
from rest_framework.test import APIRequestFactory
from rooms.serializers import RoomSerializer

class RoomModelTestCase(TestCase):
    """
    Test cases for Room model.
    """

    def setUp(self):
        self.room = Room.objects.create(
            name="Test Room",
            location="First Floor",
            capacity=10,
            is_available=True,
        )

    def test_room_creation(self):
        """
        Test that a room can be created successfully.
        """
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(self.room.name, "Test Room")

    def test_room_soft_delete(self):
        """
        Test soft delete functionality for a room.
        """
        self.room.is_deleted = True
        self.room.save()
        self.assertTrue(self.room.is_deleted)

    def test_usage_log_creation(self):
        """
        Test usage log creation for a room.
        """
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        log = UsageLog.objects.create(
            room=self.room,
            user=user,
            start_time=now(),
        )
        self.assertEqual(log.room, self.room)
        self.assertEqual(log.user, user)


class RoomSerializerTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password", role="staff"
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/rooms/')
        self.request.user = self.user

    def test_room_serializer_valid_data(self):
        """
        Test RoomSerializer with valid data.
        """
        data = {
            "name": "Valid Room",
            "location": "First Floor",
            "capacity": 10,
            "is_available": True,
            "requires_approval": False,
        }
        serializer = RoomSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

    def test_room_serializer_invalid_data(self):
        """
        Test RoomSerializer with invalid data (e.g., marking unavailable).
        """
        data = {
            "name": "Invalid Room",
            "location": "First Floor",
            "capacity": 10,
            "is_available": False,
            "requires_approval": False,
        }
        serializer = RoomSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

    def _get_mock_request(self):
        """
        Helper method to mock a request with a user.
        """
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.user  # Set the test user
        return Request(request)


class RoomAPITestCase(TestCase):
    """
    Test cases for Room API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass"
        )
        self.staff_user = CustomUser.objects.create_user(
            username="staffuser", email="staff@example.com", password="staffpass", role="staff"
        )
        self.student_user = CustomUser.objects.create_user(
            username="studentuser", email="student@example.com", password="studentpass", role="student"
        )
        self.room = Room.objects.create(
            name="Test Room",
            location="First Floor",
            capacity=10,
            is_available=True,
        )

    def test_get_room_list(self):
        """
        Test retrieving the list of rooms.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get("/api/rooms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_room_as_admin(self):
        """
        Test room creation by an admin.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "New Room",
            "location": "Second Floor",
            "capacity": 20,
            "is_available": True,
        }
        response = self.client.post("/api/rooms/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_create_room_as_non_admin(self):
        """
        Test room creation is denied for non-admin users.
        """
        self.client.force_authenticate(user=self.student_user)
        data = {
            "name": "Unauthorized Room",
            "location": "Third Floor",
            "capacity": 15,
            "is_available": True,
        }
        response = self.client.post("/api/rooms/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_room_usage(self):
        """
        Test starting room usage by an authenticated user.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(f"/api/rooms/{self.room.id}/start_usage/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_end_room_usage(self):
        """
        Test ending room usage by an authenticated user.
        """
        self.client.force_authenticate(user=self.student_user)
        # Start usage first
        self.client.post(f"/api/rooms/{self.room.id}/start_usage/")
        response = self.client.post(f"/api/rooms/{self.room.id}/end_usage/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_room_as_admin(self):
        """
        Test approving a room by an admin.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f"/api/rooms/{self.room.id}/approve_room/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertFalse(self.room.requires_approval)


class RoomPermissionTestCase(TestCase):
    """
    Test cases for Room API permissions.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass"
        )
        self.student_user = CustomUser.objects.create_user(
            username="studentuser", email="student@example.com", password="studentpass", role="student"
        )
        self.room = Room.objects.create(
            name="Restricted Room",
            location="First Floor",
            capacity=5,
            is_available=True,
        )

    def test_access_room_as_student(self):
        """
        Test that a student can view rooms but cannot modify them.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f"/api/rooms/{self.room.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {"name": "Modified Room"}
        response = self.client.patch(f"/api/rooms/{self.room.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
