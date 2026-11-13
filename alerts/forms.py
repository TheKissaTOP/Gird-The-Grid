
from django import forms
from .models import Alert


class AlertForm(forms.ModelForm):

    class Meta:
        model = Alert
        fields = [
            "title",
            "description",
            "equipment",
            "severity",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Назва інциденту"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Опис проблеми"
            }),
            "equipment": forms.Select(attrs={
                "class": "form-control"
            }),
            "severity": forms.Select(attrs={
                "class": "form-control"
            }),
        }
