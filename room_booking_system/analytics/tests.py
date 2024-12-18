from django.test import TestCase
from rooms.models import Room
from .models import Analytics

class AnalyticsTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Test Room", location="First Floor", capacity=10)
        self.analytics = Analytics.objects.create(
            room=self.room, total_bookings=5, total_checkins=3, peak_hours='{"10AM-12PM": 2}'
        )

    def test_analytics_creation(self):
        self.assertEqual(self.analytics.total_bookings, 5)
        self.assertEqual(self.analytics.total_checkins, 3)
