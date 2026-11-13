from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label="Логін")
    password = forms.CharField(label="Пароль (мінімум 8 символів)", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторіть пароль", widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password2"):
            raise forms.ValidationError("Паролі не збігаються")
        return data