
from django.db import models
from django.utils import timezone
from monitoring.models import Equipment


class BaseAlert(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Низький"),
        ("medium", "Середній"),
        ("high", "Високий"),
        ("critical", "Критичний"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="medium"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Alert(BaseAlert):
    STATUS_CHOICES = [
        ("open", "Відкрито"),
        ("resolved", "Вирішено"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="alerts"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="open"
    )

    resolved_at = models.DateTimeField(null=True, blank=True)

    def resolve(self):
        self.status = "resolved"
        self.resolved_at = timezone.now()
        self.save()

    def reopen(self):
        self.status = "open"
        self.resolved_at = None
        self.save()

    def is_resolved(self):
        return self.status == "resolved"

    def __str__(self):
        return self.title
