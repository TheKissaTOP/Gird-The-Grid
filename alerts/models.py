from django.db import models
from django.utils import timezone
from monitoring.models import Equipment


class BaseAlert(models.Model):
    """Базова абстрактна модель аварійного сповіщення."""

    class Severity(models.TextChoices):
        LOW = "low", "Низький"
        MEDIUM = "medium", "Середній"
        HIGH = "high", "Високий"
        CRITICAL = "critical", "Критичний"

    title = models.CharField(max_length=150)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Alert(BaseAlert):
    """Модель аварійного інциденту, пов'язаного з обладнанням."""

    class Status(models.TextChoices):
        OPEN = "open", "Відкрито"
        RESOLVED = "resolved", "Вирішено"

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="alerts")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def _change_status(self, status, resolved_at=None):
        self.status = status
        self.resolved_at = resolved_at
        self.save(update_fields=["status", "resolved_at"])

    def resolve(self):
        """Позначає інцидент як вирішений."""
        self._change_status(self.Status.RESOLVED, timezone.now())

    def reopen(self):
        """Повторно відкриває раніше вирішений інцидент."""
        self._change_status(self.Status.OPEN)

    def is_resolved(self):
        return self.status == self.Status.RESOLVED

    def __str__(self):
        return self.title
