from django.test import TestCase
from rest_framework.test import APIClient
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
