import csv
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from users.permissions import can
from .forms import ReportForm
from .models import Report
from .services import AnalyticsService, DemoDataService


@login_required
def analytics_dashboard(request):
    """Головна панель аналітики електричної мережі."""
    if not can(request.user, "view_stats"):
        return HttpResponseForbidden("Недостатньо прав для перегляду аналітики")

    if request.method == "POST" and request.POST.get("action") == "seed_demo":
        DemoDataService.seed_placeholder_data()
        return redirect("analytics:dashboard")

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    service = AnalyticsService()
    average_voltage = service.calculate_average_voltage()
    total_consumption = service.calculate_total_consumption()
    equipment_stats = service.get_equipment_statistics()
    alert_stats = service.get_alert_statistics()
    critical_equipment = service.equipment_analyzer.find_critical_equipment()

    daily_consumption = service.consumption_analyzer.calculate_daily_consumption(today)
    monthly_consumption = service.consumption_analyzer.calculate_monthly_consumption(today.year, today.month)
    period_comparison = service.consumption_analyzer.compare_consumption(
        current_start=week_ago,
        current_end=today,
        previous_start=two_weeks_ago,
        previous_end=week_ago - timedelta(days=1),
    )

    has_data = equipment_stats["total_equipment"] > 0 or total_consumption > 0

    return render(
        request,
        "analytics/dashboard.html",
        {
            "has_data": has_data,
            "average_voltage": average_voltage,
            "total_consumption": total_consumption,
            "daily_consumption": daily_consumption,
            "monthly_consumption": monthly_consumption,
            "period_comparison": period_comparison,
            "equipment_stats": equipment_stats,
            "critical_equipment": critical_equipment,
            "alert_stats": alert_stats,
        },
    )


@login_required
def report_list(request):
    """Список звітів та форма формування нового аналітичного звіту."""
    if not can(request.user, "view_reports"):
        return HttpResponseForbidden("Недостатньо прав для перегляду звітів")

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save()
            report.generate()
            return redirect("analytics:report_detail", pk=report.pk)
    else:
        today = timezone.now().date()
        form = ReportForm(initial={
            "period_start": today - timedelta(days=7),
            "period_end": today,
        })

    reports = Report.objects.all().order_by("-created_at")
    return render(
        request,
        "analytics/reports.html",
        {
            "form": form,
            "reports": reports,
        },
    )


@login_required
def report_detail(request, pk):
    """Детальний перегляд сформованого звіту."""
    if not can(request.user, "view_reports"):
        return HttpResponseForbidden("Недостатньо прав для перегляду звітів")

    report = get_object_or_404(Report, pk=pk)
    report_data = report.get_report_data()
    return render(
        request,
        "analytics/report_detail.html",
        {
            "report": report,
            "report_data": report_data,
        },
    )


@login_required
def report_export_csv(request, pk):
    """Експорт даних звіту у формат CSV."""
    if not can(request.user, "view_reports"):
        return HttpResponseForbidden("Недостатньо прав для експорту звітів")

    report = get_object_or_404(Report, pk=pk)
    data = report.get_report_data()
    eq_stats = data.get("equipment_statistics", {})
    al_stats = data.get("alert_statistics", {})

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="report_{report.pk}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Показник", "Значення"])
    writer.writerow(["Назва звіту", report.title])
    writer.writerow(["Період", f"{report.period_start} — {report.period_end}"])
    writer.writerow(["Середня напруга (В)", data.get("average_voltage", 0)])
    writer.writerow(["Загальне споживання (кВт·год)", data.get("total_consumption", 0)])
    writer.writerow(["Усього обладнання", eq_stats.get("total_equipment", 0)])
    writer.writerow(["Критичне обладнання", eq_stats.get("critical_count", 0)])
    writer.writerow(["Усього інцидентів", al_stats.get("total_alerts", 0)])
    writer.writerow(["Середній час вирішення інцидентів (хв)", al_stats.get("avg_resolution_minutes", 0)])
    return response