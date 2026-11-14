from .models import User
from .roles import Role

MIN_PASSWORD_LENGTH = 8


class UserService:
    def register_user(self, username, password, role):
        if not self._is_valid(username, password, role):
            return None
        return self._create_user(username, password, role)

    def update_user_role(self, user_id, new_role):
        if new_role not in Role.ALL:
            return None
        return self._update_user(user_id, role=new_role)

    def deactivate_user(self, user_id):
        return self._update_user(user_id, is_active=False)

    def activate_user(self, user_id):
        return self._update_user(user_id, is_active=True)

    def get_user_by_email(self, email):
        return User.objects.filter(email__iexact=email).first()

    def _is_valid(self, username, password, role):
        if username == "":
            return False
        if len(password) < MIN_PASSWORD_LENGTH:
            return False
        if role not in Role.ALL:
            return False
        if User.objects.filter(username=username).exists():
            return False
        return True

    def _create_user(self, username, password, role):
        user = User(username=username, role=role)
        user.set_password(password)
        user.save()
        return user

    def _update_user(self, user_id, **fields):
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return None
        for name, value in fields.items():
            setattr(user, name, value)
        user.save()
        return user