from django.db import models


class BaseReport(models.Model):
    """Абстрактна базова модель аналітичного звіту."""

    title = models.CharField(max_length=150, verbose_name="Назва звіту")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        abstract = True

    def get_information(self):
        """Повертає базову інформацію про звіт."""
        return f"{self.title} (створено: {self.created_at:%Y-%m-%d %H:%M})"

    def get_report_data(self):
        """Базовий метод отримання даних звіту (перевизначається у нащадках)."""
        return {}


class Report(BaseReport):
    """Модель звіту щодо показників електричної мережі."""

    period_start = models.DateField(verbose_name="Початок періоду")
    period_end = models.DateField(verbose_name="Кінець періоду")
    data = models.JSONField(default=dict, blank=True, verbose_name="Результати аналізу")

    def generate(self):
        """Формує аналітичний звіт за вказаний період та зберігає результати."""
        from .services import AnalyticsService

        service = AnalyticsService(
            period_start=self.period_start,
            period_end=self.period_end,
        )
        self.data = {
            "period_start": str(self.period_start),
            "period_end": str(self.period_end),
            "average_voltage": service.calculate_average_voltage(),
            "total_consumption": service.calculate_total_consumption(),
            "consumption_details": service.consumption_analyzer.get_summary(),
            "equipment_statistics": service.get_equipment_statistics(),
            "alert_statistics": service.get_alert_statistics(),
        }
        self.save(update_fields=["data"])
        return self.data

    def get_report_data(self):
        """Повертає сформовані дані звіту (за потреби генерує їх)."""
        if not self.data:
            return self.generate()
        return self.data

    def __str__(self):
        return f"{self.title} ({self.period_start} — {self.period_end})"
