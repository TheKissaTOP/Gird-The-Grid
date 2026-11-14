from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.analytics_dashboard, name="dashboard"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/export/", views.report_export_csv, name="report_export_csv"),
]