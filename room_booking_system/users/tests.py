#Users/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
<<<<<<< HEAD
from rest_framework import status
from users.models import CustomUser
from django.utils.timezone import now

class CustomUserModelTestCase(TestCase):
    """
    Test cases for the CustomUser model.
    """
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            role="student",
=======
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
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
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

<<<<<<< HEAD
    def test_create_superuser(self):
        """Test that a superuser can be created successfully."""
        admin_user = CustomUser.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpass",
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, "admin")

    def test_user_string_representation(self):
        """Test the string representation of a user."""
        self.assertEqual(str(self.user), "testuser")


class UserAPITestCase(TestCase):
    """
    Test cases for User API endpoints.
    """
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpass",
            role="admin",
        )
        self.student_user = CustomUser.objects.create_user(
            username="studentuser",
            email="student@example.com",
            password="studentpass",
            role="student",
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_user_login(self):
        """Test user login and JWT token generation."""
        self.client.logout()
        response = self.client.post(
            "/api/users/login/", {
                "username": "studentuser",
                "password": "studentpass",
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_profile_retrieval(self):
        """Test retrieving the profile of the authenticated user."""
        response = self.client.get("/api/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "adminuser")

    def test_change_password(self):
        """Test changing the user's password."""
        response = self.client.post(
            "/api/users/change_password/",
            {
                "old_password": "adminpass",
                "new_password": "newadminpass",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_as_admin(self):
        """Test creating a new user as an admin."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "role": "student",
        }
        response = self.client.post("/api/users/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 3)

    def test_create_user_as_non_admin(self):
        """
        Test that a non-admin user cannot create a new user.
        """
        self.client.force_authenticate(user=self.student_user)  # Authenticate as a non-admin user
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "student",
        }
        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Ensure forbidden status
        self.assertEqual(CustomUser.objects.filter(username="newuser").count(), 0)  # Ensure user is not created


    def test_deactivate_user_as_admin(self):
        """Test deactivating a user as an admin."""
        response = self.client.patch(f"/api/users/{self.student_user.id}/deactivate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_user.refresh_from_db()
        self.assertFalse(self.student_user.is_active)


class UserPermissionTestCase(TestCase):
    """
    Test cases for user permissions.
    """
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpass",
            role="admin",
        )
        self.staff_user = CustomUser.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="staffpass",
            role="staff",
        )
        self.student_user = CustomUser.objects.create_user(
            username="studentuser",
            email="student@example.com",
            password="studentpass",
            role="student",
        )

    def test_admin_can_access_list(self):
        """
        Test that the list endpoint is disabled for all users, including admins.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Not allowed.")

    def test_admin_cannot_access_list(self):
        """
        Test that the list endpoint is disabled for all users except admins.
        """
        self.client.force_authenticate(user=self.student_user)  # Authenticate as a student user
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
=======
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
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
