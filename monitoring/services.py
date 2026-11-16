from .models import Equipment, Measurement


class EquipmentStatusService:
    """Сервіс перевірки та оновлення стану обладнання."""

    @staticmethod
    def update_equipment_status(equipment, voltage):
        equipment.update_status(voltage)
        return equipment.status


class EquipmentQueryService:
    """Сервіс отримання обладнання та пов'язаних вимірювань."""

    @staticmethod
    def get_all_equipment():
        return Equipment.objects.all().order_by("-created_at")

    @staticmethod
    def get_equipment(equipment_id):
        return Equipment.objects.get(pk=equipment_id)

    @staticmethod
    def get_measurements(equipment):
        return equipment.measurements.all().order_by("-measured_at")


class MeasurementService:
    """Сервіс створення та отримання вимірювань."""

    @staticmethod
    def create_measurement(equipment, voltage, current, power, energy_consumption):
        measurement = Measurement.objects.create(
            equipment=equipment,
            voltage=voltage,
            current=current,
            power=power,
            energy_consumption=energy_consumption,
        )
        MeasurementService._update_equipment_status(equipment, voltage)
        return measurement

    @staticmethod
    def _update_equipment_status(equipment, voltage):
        EquipmentStatusService.update_equipment_status(equipment, voltage)
