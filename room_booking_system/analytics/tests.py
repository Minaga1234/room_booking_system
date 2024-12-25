from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class AnalyticsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="adminuser",
            password="password",
            email="admin@example.com",
            role="admin"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_basic_notifications_access(self):
        url = reverse("notifications:notification-list")
        response = self.client.get(url)
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, 200)
