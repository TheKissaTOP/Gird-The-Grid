from datetime import timedelta
from decimal import Decimal
import math
import random

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from alerts.models import Alert
from monitoring.models import Equipment, Measurement


class BaseAnalyzer:
    """Базовий клас аналізатора з інкапсуляцією фільтрації за періодом."""

    def __init__(self, period_start=None, period_end=None):
        self._period_start = period_start
        self._period_end = period_end

    def _filter_by_period(self, queryset, date_field):
        """Фільтрує QuerySet за початковою та кінцевою датами періоду."""
        if self._period_start:
            queryset = queryset.filter(**{f"{date_field}__date__gte": self._period_start})
        if self._period_end:
            queryset = queryset.filter(**{f"{date_field}__date__lte": self._period_end})
        return queryset

    def get_summary(self):
        """Повертає зведені показники (перевизначається у дочірніх класах)."""
        return {}


class ConsumptionAnalyzer(BaseAnalyzer):
    """Клас для аналізу споживання електроенергії."""

    def _get_measurements(self):
        qs = Measurement.objects.select_related("equipment").all()
        return self._filter_by_period(qs, "measured_at")

    def calculate_daily_consumption(self, target_date=None):
        """Розрахунок споживання електроенергії (кВт·год) за день."""
        day = target_date or self._period_end or timezone.now().date()
        total = (
            Measurement.objects.filter(measured_at__date=day)
            .aggregate(total=Sum("energy_consumption"))["total"]
        )
        return round(float(total or 0.0), 2)

    def calculate_monthly_consumption(self, year=None, month=None):
        """Розрахунок споживання електроенергії (кВт·год) за місяць."""
        ref_date = self._period_end or timezone.now().date()
        target_year = year or ref_date.year
        target_month = month or ref_date.month
        total = (
            Measurement.objects.filter(
                measured_at__year=target_year,
                measured_at__month=target_month,
            )
            .aggregate(total=Sum("energy_consumption"))["total"]
        )
        return round(float(total or 0.0), 2)

    def compare_consumption(self, current_start, current_end, previous_start, previous_end):
        """Порівняння показників споживання електроенергії за два періоди."""
        current_total = float(
            Measurement.objects.filter(
                measured_at__date__gte=current_start,
                measured_at__date__lte=current_end,
            ).aggregate(total=Sum("energy_consumption"))["total"] or 0.0
        )
        previous_total = float(
            Measurement.objects.filter(
                measured_at__date__gte=previous_start,
                measured_at__date__lte=previous_end,
            ).aggregate(total=Sum("energy_consumption"))["total"] or 0.0
        )

        diff = round(current_total - previous_total, 2)
        if previous_total > 0:
            change_percent = round((diff / previous_total) * 100, 2)
        else:
            change_percent = 100.0 if current_total > 0 else 0.0

        return {
            "current_kwh": round(current_total, 2),
            "previous_kwh": round(previous_total, 2),
            "difference_kwh": diff,
            "change_percent": change_percent,
        }

    def get_summary(self):
        qs = self._get_measurements()
        total_period = float(qs.aggregate(total=Sum("energy_consumption"))["total"] or 0.0)
        return {
            "period_consumption_kwh": round(total_period, 2),
            "daily_consumption_kwh": self.calculate_daily_consumption(),
            "monthly_consumption_kwh": self.calculate_monthly_consumption(),
        }


class EquipmentAnalyzer(BaseAnalyzer):
    """Клас для аналізу стану та кількості електрообладнання."""

    def _get_equipment(self):
        return Equipment.objects.all()

    def count_equipment(self):
        """Підрахунок загальної кількості обладнання."""
        return self._get_equipment().count()

    def count_by_status(self):
        """Підрахунок кількості обладнання за кожним станом."""
        counts = {
            "normal": 0,
            "warning": 0,
            "critical": 0,
            "offline": 0,
        }
        grouped = self._get_equipment().values("status").annotate(total=Count("id"))
        for row in grouped:
            status_key = row["status"]
            if status_key in counts:
                counts[status_key] = row["total"]
        return counts

    def find_critical_equipment(self):
        """Пошук обладнання, що перебуває у критичному стані."""
        return self._get_equipment().filter(status="critical").order_by("name")

    def get_summary(self):
        critical_qs = self.find_critical_equipment()
        return {
            "total_equipment": self.count_equipment(),
            "by_status": self.count_by_status(),
            "critical_count": critical_qs.count(),
            "critical_names": [eq.name for eq in critical_qs],
        }


class AlertAnalyzer(BaseAnalyzer):
    """Клас для аналізу аварійних ситуацій та інцидентів."""

    def _get_alerts(self):
        qs = Alert.objects.select_related("equipment").all()
        return self._filter_by_period(qs, "created_at")

    def count_alerts(self):
        """Підрахунок загальної кількості інцидентів."""
        return self._get_alerts().count()

    def count_by_severity(self):
        """Підрахунок інцидентів за рівнями важливості."""
        counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }
        grouped = self._get_alerts().values("severity").annotate(total=Count("id"))
        for row in grouped:
            sev_key = row["severity"]
            if sev_key in counts:
                counts[sev_key] = row["total"]
        return counts

    def calculate_resolution_time(self):
        """Розрахунок середнього часу вирішення інцидентів (у хвилинах)."""
        resolved_alerts = self._get_alerts().filter(
            status="resolved",
            resolved_at__isnull=False,
        )
        durations = [
            (alert.resolved_at - alert.created_at).total_seconds() / 60.0
            for alert in resolved_alerts
        ]
        if not durations:
            return 0.0
        return round(sum(durations) / len(durations), 2)

    def get_summary(self):
        qs = self._get_alerts()
        return {
            "total_alerts": self.count_alerts(),
            "open_alerts": qs.filter(status="open").count(),
            "resolved_alerts": qs.filter(status="resolved").count(),
            "by_severity": self.count_by_severity(),
            "avg_resolution_minutes": self.calculate_resolution_time(),
        }


class AnalyticsService:
    """Основний сервісний клас для виконання комплексних аналітичних операцій."""

    def __init__(self, period_start=None, period_end=None):
        self.period_start = period_start
        self.period_end = period_end
        self.consumption_analyzer = ConsumptionAnalyzer(period_start, period_end)
        self.equipment_analyzer = EquipmentAnalyzer(period_start, period_end)
        self.alert_analyzer = AlertAnalyzer(period_start, period_end)

    def _get_measurements_queryset(self):
        qs = Measurement.objects.all()
        if self.period_start:
            qs = qs.filter(measured_at__date__gte=self.period_start)
        if self.period_end:
            qs = qs.filter(measured_at__date__lte=self.period_end)
        return qs

    def calculate_average_voltage(self):
        """Розрахунок середньої напруги (В) за вимірюваннями."""
        avg_val = self._get_measurements_queryset().aggregate(avg=Avg("voltage"))["avg"]
        return round(float(avg_val or 0.0), 2)

    def calculate_total_consumption(self):
        """Розрахунок загального споживання електроенергії (кВт·год)."""
        total_val = self._get_measurements_queryset().aggregate(total=Sum("energy_consumption"))["total"]
        return round(float(total_val or 0.0), 2)

    def get_equipment_statistics(self):
        """Отримання зведеної статистики щодо обладнання."""
        return self.equipment_analyzer.get_summary()

    def get_alert_statistics(self):
        """Отримання зведеної статистики щодо аварійних сповіщень."""
        return self.alert_analyzer.get_summary()


class DemoDataService:
    """Допоміжний сервіс для наповнення БД тестовими даними на етапі демонстрації."""

    @staticmethod
    def seed_placeholder_data():
        demo_equipment = [
            ("Трансформатор ТП-101", "Підстанція Північна", "transformer", "TR-101-UA", "normal"),
            ("Трансформатор ТП-204", "Підстанція Південна", "transformer", "TR-204-UA", "critical"),
            ("ЛЕП-110кВ Магістральна", "Сектор Захід", "power_line", "PL-110-UA", "warning"),
            ("Генератор резервний ГТГ-1", "Енергоблок №1", "generator", "GEN-01-UA", "normal"),
        ]

        equipment_objs = []
        for name, location, eq_type, serial, status in demo_equipment:
            obj, _ = Equipment.objects.get_or_create(
                serial_number=serial,
                defaults={
                    "name": name,
                    "location": location,
                    "equipment_type": eq_type,
                    "status": status,
                    "min_voltage": Decimal("200.00"),
                    "max_voltage": Decimal("240.00"),
                },
            )
            equipment_objs.append(obj)

        if Measurement.objects.count() < 10:
            now = timezone.now()
            for hours_ago in range(24, 0, -1):
                ts = now - timedelta(hours=hours_ago)
                factor = 0.75 + 0.25 * math.sin((ts.hour - 6) * math.pi / 12)
                for eq in equipment_objs:
                    voltage = round(220.0 + random.uniform(-8.0, 9.0), 2)
                    if eq.status == "critical":
                        voltage = 246.50
                    current = round(45.0 * factor + random.uniform(-3.0, 3.0), 2)
                    power = round(voltage * current, 2)
                    energy = round((power / 1000.0), 2)

                    m = Measurement.objects.create(
                        equipment=eq,
                        voltage=Decimal(str(voltage)),
                        current=Decimal(str(current)),
                        power=Decimal(str(power)),
                        energy_consumption=Decimal(str(energy)),
                    )
                    Measurement.objects.filter(pk=m.pk).update(measured_at=ts)

        if Alert.objects.count() == 0:
            now = timezone.now()
            Alert.objects.create(
                title="Перевищення допустимої напруги",
                description="Зафіксовано 246.5 В на трансформаторі ТП-204",
                equipment=equipment_objs[1],
                severity="critical",
                status="open",
            )
            Alert.objects.create(
                title="Коливання навантаження на лінії",
                description="Підвищений струм на ЛЕП-110кВ Магістральна",
                equipment=equipment_objs[2],
                severity="high",
                status="open",
            )
            a3 = Alert.objects.create(
                title="Короткочасне просідання напруги",
                description="Напруга відновилася до номінального рівня",
                equipment=equipment_objs[0],
                severity="medium",
                status="resolved",
                resolved_at=now,
            )
            Alert.objects.filter(pk=a3.pk).update(created_at=now - timedelta(minutes=45))