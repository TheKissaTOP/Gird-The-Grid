
from django import forms
from .models import Equipment, Measurement


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = Equipment
        fields = [
            "name",
            "location",
            "equipment_type",
            "serial_number",
            "min_voltage",
            "max_voltage",
        ]

        labels = {
            "name": "Назва обладнання",
            "location": "Розташування",
            "equipment_type": "Тип обладнання",
            "serial_number": "Серійний номер",
            "min_voltage": "Мінімальна напруга (В)",
            "max_voltage": "Максимальна напруга (В)",
        }


class MeasurementForm(forms.ModelForm):

    class Meta:
        model = Measurement
        fields = [
            "equipment",
            "voltage",
            "current",
            "power",
            "energy_consumption",
        ]

        labels = {
            "equipment": "Обладнання",
            "voltage": "Напруга (В)",
            "current": "Струм (А)",
            "power": "Потужність (Вт)",
            "energy_consumption": "Споживання енергії (кВт·год)",
        }
