
from django.shortcuts import render, redirect, get_object_or_404

from .models import Equipment
from .forms import EquipmentForm, MeasurementForm
from .services import MeasurementService


def equipment_list(request):
    """Показує список усього обладнання."""

    equipment = Equipment.objects.all().order_by("-created_at")

    return render(
        request,
        "monitoring/equipment_list.html",
        {"equipment": equipment}
    )


def equipment_detail(request, pk):
    """Показує інформацію про конкретний пристрій."""

    item = get_object_or_404(Equipment, pk=pk)

    measurements = item.measurements.all().order_by("-measured_at")

    return render(
        request,
        "monitoring/equipment_detail.html",
        {
            "item": item,
            "measurements": measurements
        }
    )


def equipment_create(request):
    """Створює нове обладнання."""

    if request.method == "POST":
        form = EquipmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("monitoring:equipment_list")
    else:
        form = EquipmentForm()

    return render(
        request,
        "monitoring/equipment_form.html",
        {"form": form}
    )


def measurement_create(request):
    """Додає нове вимірювання."""

    if request.method == "POST":
        form = MeasurementForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            MeasurementService.create_measurement(
                equipment=data["equipment"],
                voltage=data["voltage"],
                current=data["current"],
                power=data["power"],
                energy_consumption=data["energy_consumption"]
            )

            return redirect(
                "monitoring:equipment_detail",
                pk=data["equipment"].pk
            )
    else:
        form = MeasurementForm()

    return render(
        request,
        "monitoring/measurement_form.html",
        {"form": form}
    )
