from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ChatbotLog

User = get_user_model()  # Use the custom user model

class ChatbotTestCase(TestCase):
    def setUp(self):
        """
        Setup test user and initial configuration for chatbot tests.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",  # Ensure email is provided
            password="testpass"
        )

    def test_chatbot_log_creation(self):
        """
        Test that a chatbot log is created correctly.
        """
        log = ChatbotLog.objects.create(
            user=self.user,
            query="Test query",
            response="Test response"
        )
        self.assertEqual(log.query, "Test query")
        self.assertEqual(log.response, "Test response")
        self.assertEqual(log.user, self.user)
