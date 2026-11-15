from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    """Форма створення аналітичного звіту за обраний період."""

    class Meta:
        model = Report
        fields = ["title", "period_start", "period_end"]
        labels = {
            "title": "Назва звіту",
            "period_start": "Початок періоду",
            "period_end": "Кінець періоду",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Наприклад: Тижневий звіт мережі"}),
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("period_start")
        end = cleaned_data.get("period_end")
        if start and end and start > end:
            raise forms.ValidationError("Дата початку періоду не може бути пізнішою за дату завершення.")
        return cleaned_data