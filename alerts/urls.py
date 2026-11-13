
from django.urls import path
from . import views

app_name = "alerts"

urlpatterns = [
    path("", views.alerts_list, name="alerts_list"),
    path("create/", views.alert_create, name="alert_create"),
    path("<int:pk>/resolve/", views.alert_resolve, name="alert_resolve"),
    path("<int:pk>/reopen/", views.alert_reopen, name="alert_reopen"),
]
