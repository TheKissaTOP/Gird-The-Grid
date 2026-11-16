from django.db import models


DEFAULT_MIN_VOLTAGE = 200
DEFAULT_MAX_VOLTAGE = 240


class BaseEquipment(models.Model):
    """Базова модель електричного обладнання."""

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_information(self):
        return f"{self.name} — {self.location}"


class VoltageStatusCalculator:
    """Визначає стан обладнання за виміряною напругою."""

    @staticmethod
    def calculate(voltage, min_voltage, max_voltage):
        if voltage <= 0:
            return "offline"
        if voltage < min_voltage or voltage > max_voltage:
            return "critical"
        return "normal"


class Equipment(BaseEquipment):
    """Модель електричного обладнання."""

    EQUIPMENT_TYPES = [
        ("transformer", "Трансформатор"),
        ("power_line", "Лінія електропередач"),
        ("generator", "Генератор"),
        ("other", "Інше"),
    ]

    STATUS_CHOICES = [
        ("normal", "Нормальний"),
        ("warning", "Попередження"),
        ("critical", "Критичний"),
        ("offline", "Не працює"),
    ]

    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES, default="other")
    serial_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="normal")
    min_voltage = models.DecimalField(max_digits=10, decimal_places=2, default=DEFAULT_MIN_VOLTAGE)
    max_voltage = models.DecimalField(max_digits=10, decimal_places=2, default=DEFAULT_MAX_VOLTAGE)

    def update_status(self, voltage):
        """Оновлює та зберігає стан обладнання за значенням напруги."""
        self.status = VoltageStatusCalculator.calculate(
            voltage=voltage,
            min_voltage=self.min_voltage,
            max_voltage=self.max_voltage,
        )
        self.save(update_fields=["status"])

    def __str__(self):
        return self.name


class Measurement(models.Model):
    """Модель вимірювань електричного обладнання."""

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="measurements")
    voltage = models.DecimalField(max_digits=10, decimal_places=2)
    current = models.DecimalField(max_digits=10, decimal_places=2)
    power = models.DecimalField(max_digits=10, decimal_places=2)
    energy_consumption = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    measured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment.name} — {self.measured_at}"

    def get_power_description(self):
        """Повертає текстовий опис наявності електричної потужності."""
        if self.power <= 0:
            return "Потужність відсутня"
        return "Потужність присутня"
