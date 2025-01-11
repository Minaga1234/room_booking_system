from django.test import TestCase
from rest_framework.test import APIClient
<<<<<<< HEAD
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
=======
from django.contrib.auth import get_user_model
from .models import Room, UsageLog

class RoomTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an admin user
        cls.admin_user = get_user_model().objects.create_user(
            username="admin_test",
            password="Admin1234",
            email="admin_test@example.com",
            role="admin"
        )

        # Create a student user
        cls.student_user = get_user_model().objects.create_user(
            username="student_test",
            password="Student1234",
            email="student_test@example.com",
            role="student"
        )

        # Create test rooms
        cls.room1 = Room.objects.create(
            name="Conference Room A",
            location="Building 1",
            capacity=15,
            is_available=True
        )
        cls.room2 = Room.objects.create(
            name="Lecture Hall 1",
            location="Building 2",
            capacity=50,
            is_available=False
        )

    def setUp(self):
        self.client = APIClient()

        # Authenticate admin user for most tests
        response = self.client.post(
            "/api/users/login/",
            {"username": "admin_test", "password": "Admin1234"},
            format="json"
        )
        self.admin_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

    def test_list_rooms(self):
        """Test listing all rooms"""
        response = self.client.get("/api/rooms/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # Two rooms should be listed

    def test_filter_rooms(self):
        """Test filtering rooms by availability"""
        response = self.client.get("/api/rooms/?is_available=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Only one room is available

    def test_create_room(self):
        """Test creating a room as an admin"""
        data = {
            "name": "New Room 101",
            "location": "Building 3",
            "capacity": 25,
            "is_available": True
        }
        response = self.client.post("/api/rooms/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Room.objects.count(), 3)  # Two rooms created in setUpTestData

    def test_soft_delete_room(self):
        """Test soft-deleting a room"""
        response = self.client.delete(f"/api/rooms/{self.room1.id}/")
        self.assertEqual(response.status_code, 204)

        # Verify the room is marked as deleted
        self.room1.refresh_from_db()
        self.assertTrue(self.room1.is_deleted)

    def test_start_and_end_usage(self):
        """Test starting and ending room usage"""
        # Start usage
        response = self.client.post(f"/api/rooms/{self.room1.id}/start_usage/")
        self.assertEqual(response.status_code, 200)
        log_id = response.data["log"]["id"]

        # Verify usage log was created
        usage_log = UsageLog.objects.get(id=log_id)
        self.assertIsNotNone(usage_log.start_time)
        self.assertIsNone(usage_log.end_time)

        # End usage
        response = self.client.post(f"/api/rooms/{self.room1.id}/end_usage/")
        self.assertEqual(response.status_code, 200)

        # Verify usage log was updated
        usage_log.refresh_from_db()
        self.assertIsNotNone(usage_log.end_time)

    def test_non_admin_cannot_create_room(self):
        """Test that a non-admin user cannot create a room"""
        # Authenticate student user
        response = self.client.post(
            "/api/users/login/",
            {"username": "student_test", "password": "Student1234"},
            format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Attempt to create a room
        data = {
            "name": "Unauthorized Room",
            "location": "Building 4",
            "capacity": 20,
            "is_available": True
        }
        response = self.client.post("/api/rooms/", data, format="json")
        self.assertEqual(response.status_code, 403)
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
