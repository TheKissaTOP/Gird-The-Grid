
from .models import Measurement


class EquipmentStatusService:
    """Сервіс перевірки стану обладнання."""

    @staticmethod
    def update_equipment_status(equipment, voltage):
        equipment.update_status(voltage)


class MeasurementService:
    """Сервіс роботи з вимірюваннями."""

    @staticmethod
    def create_measurement(
        equipment,
        voltage,
        current,
        power,
        energy_consumption
    ):
        measurement = Measurement.objects.create(
            equipment=equipment,
            voltage=voltage,
            current=current,
            power=power,
            energy_consumption=energy_consumption
        )

        EquipmentStatusService.update_equipment_status(
            equipment,
            voltage
        )

        return measurement
