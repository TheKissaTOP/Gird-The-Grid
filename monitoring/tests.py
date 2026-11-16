from decimal import Decimal
from django.test import TestCase

from .models import Equipment, Measurement, VoltageStatusCalculator
from .services import EquipmentQueryService, MeasurementService


class EquipmentModelTests(TestCase):
    def setUp(self):
        self.equipment = Equipment.objects.create(
            name="Тестовий трансформатор",
            location="Підстанція №1",
            equipment_type="transformer",
            serial_number="MON-001",
        )

    def test_base_equipment_information_is_inherited(self):
        self.assertEqual(
            self.equipment.get_information(),
            "Тестовий трансформатор — Підстанція №1",
        )

    def test_voltage_status_calculator_boundaries(self):
        self.assertEqual(VoltageStatusCalculator.calculate(Decimal("0"), 200, 240), "offline")
        self.assertEqual(VoltageStatusCalculator.calculate(Decimal("199"), 200, 240), "critical")
        self.assertEqual(VoltageStatusCalculator.calculate(Decimal("220"), 200, 240), "normal")
        self.assertEqual(VoltageStatusCalculator.calculate(Decimal("241"), 200, 240), "critical")

    def test_update_status_saves_result(self):
        self.equipment.update_status(Decimal("250"))
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, "critical")


class MeasurementServiceTests(TestCase):
    def setUp(self):
        self.equipment = Equipment.objects.create(
            name="Генератор",
            location="Енергоблок",
            equipment_type="generator",
            serial_number="MON-002",
        )

    def test_create_measurement_and_update_equipment_status(self):
        measurement = MeasurementService.create_measurement(
            equipment=self.equipment,
            voltage=Decimal("220.00"),
            current=Decimal("10.00"),
            power=Decimal("2200.00"),
            energy_consumption=Decimal("12.50"),
        )
        self.assertEqual(Measurement.objects.count(), 1)
        self.assertEqual(measurement.equipment, self.equipment)
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, "normal")

    def test_power_description_for_zero_and_positive_power(self):
        measurement = Measurement.objects.create(
            equipment=self.equipment,
            voltage=0,
            current=0,
            power=0,
            energy_consumption=0,
        )
        self.assertEqual(measurement.get_power_description(), "Потужність відсутня")
        measurement.power = Decimal("100.00")
        self.assertEqual(measurement.get_power_description(), "Потужність присутня")

    def test_equipment_query_service_returns_equipment(self):
        self.assertEqual(EquipmentQueryService.get_all_equipment().count(), 1)
        self.assertEqual(EquipmentQueryService.get_equipment(self.equipment.pk), self.equipment)
        self.assertEqual(EquipmentQueryService.get_measurements(self.equipment).count(), 0)
