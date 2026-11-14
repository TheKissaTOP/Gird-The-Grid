from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "period_start", "period_end", "created_at")
    list_filter = ("period_start", "period_end", "created_at")
    search_fields = ("title",)
