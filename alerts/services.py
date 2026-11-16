from .models import Alert


class AlertQueryService:
    """Сервіс читання та фільтрації аварійних сповіщень."""

    @staticmethod
    def get_all_alerts():
        return Alert.objects.select_related("equipment").order_by("-created_at")

    @staticmethod
    def get_open_alerts():
        return AlertQueryService.get_all_alerts().filter(status=Alert.Status.OPEN)

    @staticmethod
    def get_equipment_alerts(equipment):
        return AlertQueryService.get_all_alerts().filter(equipment=equipment)


class AlertService:
    """Сервіс створення та зміни стану аварійних сповіщень."""

    @staticmethod
    def create_alert(title, description, equipment, severity):
        return Alert.objects.create(
            title=title,
            description=description,
            equipment=equipment,
            severity=severity,
        )

    @staticmethod
    def resolve_alert(alert):
        alert.resolve()
        return alert

    @staticmethod
    def reopen_alert(alert):
        alert.reopen()
        return alert
