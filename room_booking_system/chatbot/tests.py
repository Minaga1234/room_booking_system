from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ChatbotLog

class ChatbotTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")

    def test_chatbot_log_creation(self):
        log = ChatbotLog.objects.create(user=self.user, query="Test query", response="Test response")
        self.assertEqual(log.query, "Test query")
        self.assertEqual(log.response, "Test response")
