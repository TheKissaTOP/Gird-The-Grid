
from django.test import TestCase
from django.utils import timezone

from .models import Alert
from monitoring.models import Equipment


class AlertModelTest(TestCase):

    def setUp(self):
        self.equipment = Equipment.objects.create(
            name="Test Transformer",
            location="Test Location",
            equipment_type="transformer",
            serial_number="TEST-001"
        )

        self.alert = Alert.objects.create(
            title="High voltage",
            description="Voltage is above the allowed limit",
            equipment=self.equipment,
            severity="high"
        )

    def test_alert_creation(self):
        self.assertEqual(self.alert.status, "open")

    def test_resolve_alert(self):
        self.alert.resolve()

        self.assertEqual(self.alert.status, "resolved")
        self.assertIsNotNone(self.alert.resolved_at)

    def test_reopen_alert(self):
        self.alert.resolve()
        self.alert.reopen()

        self.assertEqual(self.alert.status, "open")
        self.assertIsNone(self.alert.resolved_at)
