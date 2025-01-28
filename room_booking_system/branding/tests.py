from django.test import TestCase
from .models import Branding

class BrandingTestCase(TestCase):
    def setUp(self):
        self.branding = Branding.objects.create(
            institution_name="Test Institution",
            logo_path="branding/logos/test_logo.png"
        )

    def test_branding_creation(self):
        self.assertEqual(self.branding.institution_name, "Test Institution")
