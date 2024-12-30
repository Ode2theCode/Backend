from .models import Notification


class NotificationService:
    @staticmethod
    def get_notifications(user):
        return Notification.objects.filter(recipient=user)