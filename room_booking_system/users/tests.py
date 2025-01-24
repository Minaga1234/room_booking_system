#Users/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import CustomUser

class UserTests(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = CustomUser.objects.create_user(
            username="AdminUser",
            email="admin@example.com",
            password="AdminPass@123",
            role="admin",
            is_active=True
        )
        # Create a staff user
        self.staff_user = CustomUser.objects.create_user(
            username="StaffUser",
            email="staff@example.com",
            password="StaffPass@123",
            role="staff",
            is_active=True
        )
        # Create a student user
        self.student_user = CustomUser.objects.create_user(
            username="StudentUser",
            email="student@example.com",
            password="StudentPass@123",
            role="student",
            is_active=True
        )
        self.client = APIClient()

    def test_user_login(self):
        # Test login for admin user
        response = self.client.post(
            "/api/token/",
            {"username": "AdminUser", "password": "AdminPass@123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_invalid_login(self):
        # Test login with invalid credentials
        response = self.client.post(
            "/api/token/",
            {"username": "AdminUser", "password": "WrongPassword"}
        )
        self.assertEqual(response.status_code, 401)

    def test_view_profile(self):
        # Authenticate as admin user
        response = self.client.post(
            "/api/token/",
            {"username": "AdminUser", "password": "AdminPass@123"}
        )
        access_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/users/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "AdminUser")
