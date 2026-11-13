from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import User
from .services import activate_user, can, change_role, deactivate_user, process

ROLES = [
    ("manager", "Керівник"),
    ("generator", "Генератор"),
    ("executor", "Виконавець"),
    ("analyst", "Аналітик"),
]


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = process(d["username"], d["password"], "analyst")
            if user is None:
                form.add_error(None, "Не вдалося зареєструвати: логін зайнятий або пароль закороткий")
            else:
                return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    error = ""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("home")
        error = "Невірний логін або пароль"
    return render(request, "users/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


def home_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "users/home.html")


def manage_users_view(request):
    if not request.user.is_authenticated or not can(request.user, "manage_users"):
        return HttpResponseForbidden("Недостатньо прав")

    message = ""
    if request.method == "POST":
        target_id = int(request.POST["user_id"])
        action = request.POST["action"]
        if target_id == request.user.id:
            message = "Не можна змінювати власний акаунт"
        elif action == "role":
            change_role(target_id, request.POST["role"])
            message = "Роль змінено"
        elif action == "deactivate":
            deactivate_user(target_id)
            message = "Акаунт вимкнено"
        elif action == "activate":
            activate_user(target_id)
            message = "Акаунт увімкнено"

    context = {"users": User.objects.order_by("username"), "roles": ROLES, "message": message}
    return render(request, "users/manage.html", context)