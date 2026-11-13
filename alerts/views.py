
from django.shortcuts import render, redirect, get_object_or_404

from .models import Alert
from .forms import AlertForm
from .services import AlertService


def alerts_list(request):
    alerts = Alert.objects.all().order_by("-created_at")

    return render(request, "alerts/alerts_list.html", {
        "alerts": alerts
    })


def alert_create(request):
    if request.method == "POST":
        form = AlertForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("alerts:alerts_list")
    else:
        form = AlertForm()

    return render(request, "alerts/alert_form.html", {
        "form": form
    })


def alert_resolve(request, pk):
    alert = get_object_or_404(Alert, pk=pk)

    AlertService.resolve_alert(alert.id)

    return redirect("alerts:alerts_list")


def alert_reopen(request, pk):
    alert = get_object_or_404(Alert, pk=pk)

    AlertService.reopen_alert(alert.id)

    return redirect("alerts:alerts_list")
