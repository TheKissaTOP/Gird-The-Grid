from django.shortcuts import render, redirect, get_object_or_404

from .models import Alert
from .forms import AlertForm
from .services import AlertQueryService, AlertService


def alerts_list(request):
    alerts = AlertQueryService.get_all_alerts()
    return render(request, "alerts/alerts_list.html", {"alerts": alerts})


def alert_create(request):
    if request.method == "POST":
        form = AlertForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            AlertService.create_alert(
                title=data["title"],
                description=data["description"],
                equipment=data["equipment"],
                severity=data["severity"],
            )
            return redirect("alerts:alerts_list")
    else:
        form = AlertForm()
    return render(request, "alerts/alert_form.html", {"form": form})


def alert_resolve(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    AlertService.resolve_alert(alert)
    return redirect("alerts:alerts_list")


def alert_reopen(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    AlertService.reopen_alert(alert)
    return redirect("alerts:alerts_list")
