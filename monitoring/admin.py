
from django.contrib import admin
from .models import Equipment, Measurement


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "equipment_type",
        "location",
        "status",
        "serial_number"
    )

    list_filter = ("equipment_type", "status")
    search_fields = ("name", "serial_number", "location")


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "voltage",
        "current",
        "power",
        "energy_consumption",
        "measured_at"
    )

    list_filter = ("equipment",)
