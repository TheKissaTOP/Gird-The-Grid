from django.contrib.auth.models import AbstractUser
from django.db import models

from .roles import Role


class User(AbstractUser):
    role = models.CharField(max_length=20, default=Role.ANALYST)

    def get_role(self):
        return self.role