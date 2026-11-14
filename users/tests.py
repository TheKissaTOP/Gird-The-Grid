from django.test import TestCase

from .models import User
from .permissions import can
from .services import UserService

service = UserService()


class RegistrationTests(TestCase):
    def test_success(self):
        user = service.register_user("anna", "password123", "analyst")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, "analyst")

    def test_password_is_hashed(self):
        user = service.register_user("anna", "password123", "analyst")
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))

    def test_empty_username(self):
        self.assertIsNone(service.register_user("", "password123", "analyst"))

    def test_short_password(self):
        self.assertIsNone(service.register_user("anna", "123", "analyst"))

    def test_unknown_role(self):
        self.assertIsNone(service.register_user("anna", "password123", "boss"))

    def test_duplicate_username(self):
        service.register_user("anna", "password123", "analyst")
        self.assertIsNone(service.register_user("anna", "password123", "analyst"))


class AccessTests(TestCase):
    def make(self, role):
        return User(username="x", role=role)

    def test_manager_can_everything(self):
        self.assertTrue(can(self.make("manager"), "manage_users"))

    def test_executor_rights(self):
        executor = self.make("executor")
        self.assertTrue(can(executor, "create_alert"))
        self.assertFalse(can(executor, "view_stats"))

    def test_analyst_rights(self):
        analyst = self.make("analyst")
        self.assertTrue(can(analyst, "view_stats"))
        self.assertFalse(can(analyst, "manage_users"))

    def test_generator_rights(self):
        generator = self.make("generator")
        self.assertTrue(can(generator, "edit_equipment"))
        self.assertFalse(can(generator, "create_alert"))


class ManagementTests(TestCase):
    def test_change_role(self):
        user = service.register_user("anna", "password123", "analyst")
        service.update_user_role(user.id, "executor")
        user.refresh_from_db()
        self.assertEqual(user.role, "executor")

    def test_change_role_unknown(self):
        user = service.register_user("anna", "password123", "analyst")
        self.assertIsNone(service.update_user_role(user.id, "boss"))

    def test_deactivate(self):
        user = service.register_user("anna", "password123", "analyst")
        service.deactivate_user(user.id)
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class FindTests(TestCase):
    def test_get_user_by_email(self):
        user = service.register_user("anna", "password123", "analyst")
        user.email = "anna@example.com"
        user.save()
        self.assertEqual(service.get_user_by_email("ANNA@example.com"), user)