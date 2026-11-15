from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from alerts.models import Alert
from monitoring.models import Equipment, Measurement
from users.models import User
from analytics.models import Report
from analytics.services import (
    AlertAnalyzer,
    AnalyticsService,
    ConsumptionAnalyzer,
    EquipmentAnalyzer,
)


class AnalyticsModuleTest(TestCase):

    def setUp(self):
        self.analyst = User.objects.create_user(
            username="analyst_test",
            password="password123",
            role="analyst",
        )
        self.executor = User.objects.create_user(
            username="executor_test",
            password="password123",
            role="executor",
        )

        self.eq_normal = Equipment.objects.create(
            name="Трансформатор ТП-1",
            location="Північ",
            equipment_type="transformer",
            serial_number="TEST-TR-01",
            status="normal",
        )
        self.eq_critical = Equipment.objects.create(
            name="Трансформатор ТП-2",
            location="Південь",
            equipment_type="transformer",
            serial_number="TEST-TR-02",
            status="critical",
        )

        Measurement.objects.create(
            equipment=self.eq_normal,
            voltage=Decimal("220.00"),
            current=Decimal("10.00"),
            power=Decimal("2200.00"),
            energy_consumption=Decimal("120.50"),
        )
        Measurement.objects.create(
            equipment=self.eq_critical,
            voltage=Decimal("248.00"),
            current=Decimal("15.00"),
            power=Decimal("3720.00"),
            energy_consumption=Decimal("80.50"),
        )

        now = timezone.now()
        alert_resolved = Alert.objects.create(
            title="Перенапруга",
            description="Тест",
            equipment=self.eq_critical,
            severity="critical",
            status="resolved",
            resolved_at=now,
        )
        Alert.objects.filter(pk=alert_resolved.pk).update(created_at=now - timedelta(minutes=30))

        Alert.objects.create(
            title="Попередження",
            description="Тест 2",
            equipment=self.eq_normal,
            severity="medium",
            status="open",
        )

    def test_analytics_service_metrics(self):
        service = AnalyticsService()
        self.assertEqual(service.calculate_average_voltage(), 234.0)
        self.assertEqual(service.calculate_total_consumption(), 201.0)

        eq_stats = service.get_equipment_statistics()
        self.assertEqual(eq_stats["total_equipment"], 2)
        self.assertEqual(eq_stats["critical_count"], 1)

        al_stats = service.get_alert_statistics()
        self.assertEqual(al_stats["total_alerts"], 2)
        self.assertEqual(al_stats["by_severity"]["critical"], 1)

    def test_analyzers_directly(self):
        eq_analyzer = EquipmentAnalyzer()
        self.assertEqual(eq_analyzer.count_equipment(), 2)
        self.assertEqual(eq_analyzer.find_critical_equipment().count(), 1)

        al_analyzer = AlertAnalyzer()
        self.assertAlmostEqual(al_analyzer.calculate_resolution_time(), 30.0, places=1)

        cons_analyzer = ConsumptionAnalyzer()
        self.assertEqual(cons_analyzer.calculate_daily_consumption(), 201.0)
        self.assertEqual(cons_analyzer.calculate_monthly_consumption(), 201.0)

    def test_report_generation_and_views(self):
        today = timezone.now().date()
        report = Report.objects.create(
            title="Тижневий звіт",
            period_start=today - timedelta(days=7),
            period_end=today,
        )
        data = report.generate()
        self.assertEqual(data["average_voltage"], 234.0)
        self.assertEqual(report.get_report_data()["total_consumption"], 201.0)

        self.client.force_login(self.executor)
        resp_forbidden = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(resp_forbidden.status_code, 403)

        self.client.force_login(self.analyst)
        resp_dash = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(resp_dash.status_code, 200)

        resp_detail = self.client.get(reverse("analytics:report_detail", args=[report.pk]))
        self.assertEqual(resp_detail.status_code, 200)