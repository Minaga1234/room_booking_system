from django.test import TestCase
from .models import CustomUser

class UserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpass"))
