
from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "equipment",
        "severity",
        "status",
        "created_at",
        "resolved_at",
    )

    list_filter = ("severity", "status", "created_at")
    search_fields = ("title", "description")
