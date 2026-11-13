
from django.urls import path
from . import views

app_name = "monitoring"

urlpatterns = [
    path("", views.equipment_list, name="equipment_list"),

    path(
        "equipment/add/",
        views.equipment_create,
        name="equipment_create"
    ),

    path(
        "equipment/<int:pk>/",
        views.equipment_detail,
        name="equipment_detail"
    ),

    path(
        "measurements/add/",
        views.measurement_create,
        name="measurement_create"
    ),
]
