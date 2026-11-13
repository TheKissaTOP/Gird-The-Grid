from .models import User


def process(username, password, role):
    if username != "":
        if len(password) >= 8:
            if role == "manager" or role == "generator" or role == "executor" or role == "analyst":
                if not User.objects.filter(username=username).exists():
                    u = User(username=username, role=role)
                    u.set_password(password)
                    u.save()
                    return u
    return None


def can(user, action):
    if user.role == "manager":
        return True
    elif user.role == "generator":
        if action == "view_equipment" or action == "edit_equipment":
            return True
        return False
    elif user.role == "executor":
        if action == "create_alert" or action == "change_status" or action == "view_equipment":
            return True
        return False
    elif user.role == "analyst":
        if action == "view_stats" or action == "view_reports" or action == "view_equipment":
            return True
        return False
    return False

def change_role(user_id, new_role):
    if new_role == "manager" or new_role == "generator" or new_role == "executor" or new_role == "analyst":
        u = User.objects.filter(id=user_id).first()
        if u is not None:
            u.role = new_role
            u.save()
            return u
    return None


def deactivate_user(user_id):
    u = User.objects.filter(id=user_id).first()
    if u is not None:
        u.is_active = False
        u.save()
        return u
    return None


def activate_user(user_id):
    u = User.objects.filter(id=user_id).first()
    if u is not None:
        u.is_active = True
        u.save()
        return u
    return None