
from .models import Alert


class AlertService:

    @staticmethod
    def create_alert(title, description, equipment, severity):
        return Alert.objects.create(
            title=title,
            description=description,
            equipment=equipment,
            severity=severity
        )

    @staticmethod
    def get_active_alerts():
        return Alert.objects.filter(status="open").order_by("-created_at")

    @staticmethod
    def get_equipment_alerts(equipment):
        return Alert.objects.filter(
            equipment=equipment
        ).order_by("-created_at")

    @staticmethod
    def resolve_alert(alert_id):
        alert = Alert.objects.get(id=alert_id)
        alert.resolve()
        return alert

    @staticmethod
    def reopen_alert(alert_id):
        alert = Alert.objects.get(id=alert_id)
        alert.reopen()
        return alert
