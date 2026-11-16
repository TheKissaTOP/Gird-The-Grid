from django.test import TestCase

from monitoring.models import Equipment
from .models import Alert
from .services import AlertQueryService, AlertService


class AlertModelTests(TestCase):
    def setUp(self):
        self.equipment = Equipment.objects.create(
            name="Тестовий трансформатор",
            location="Тестова підстанція",
            equipment_type="transformer",
            serial_number="ALT-001",
        )
        self.alert = Alert.objects.create(
            title="Перевищення напруги",
            description="Напруга вища за допустиме значення",
            equipment=self.equipment,
            severity=Alert.Severity.HIGH,
        )

    def test_alert_has_open_default_status(self):
        self.assertEqual(self.alert.status, Alert.Status.OPEN)
        self.assertFalse(self.alert.is_resolved())

    def test_resolve_sets_status_and_timestamp(self):
        self.alert.resolve()
        self.assertEqual(self.alert.status, Alert.Status.RESOLVED)
        self.assertIsNotNone(self.alert.resolved_at)
        self.assertTrue(self.alert.is_resolved())

    def test_reopen_clears_resolution_timestamp(self):
        self.alert.resolve()
        self.alert.reopen()
        self.assertEqual(self.alert.status, Alert.Status.OPEN)
        self.assertIsNone(self.alert.resolved_at)

    def test_alert_string_representation(self):
        self.assertEqual(str(self.alert), "Перевищення напруги")


class AlertServiceTests(TestCase):
    def setUp(self):
        self.equipment = Equipment.objects.create(
            name="Лінія електропередач",
            location="Сектор А",
            equipment_type="power_line",
            serial_number="ALT-002",
        )

    def test_create_alert(self):
        alert = AlertService.create_alert(
            "Аварійна ситуація", "Опис проблеми", self.equipment, Alert.Severity.CRITICAL
        )
        self.assertEqual(alert.equipment, self.equipment)
        self.assertEqual(alert.severity, Alert.Severity.CRITICAL)
        self.assertEqual(alert.status, Alert.Status.OPEN)

    def test_query_service_filters_open_alerts(self):
        open_alert = Alert.objects.create(
            title="Відкритий", description="Тест", equipment=self.equipment
        )
        Alert.objects.create(
            title="Закритий", description="Тест", equipment=self.equipment,
            status=Alert.Status.RESOLVED,
        )
        self.assertEqual(list(AlertQueryService.get_open_alerts()), [open_alert])
        self.assertEqual(AlertQueryService.get_equipment_alerts(self.equipment).count(), 2)

    def test_service_resolves_and_reopens_alert(self):
        alert = AlertService.create_alert("Тест", "Опис", self.equipment, Alert.Severity.LOW)
        AlertService.resolve_alert(alert)
        self.assertTrue(alert.is_resolved())
        AlertService.reopen_alert(alert)
        self.assertFalse(alert.is_resolved())
