from .models import Notification


class NotificationService:
    @staticmethod
    def get_notifications(user):
        result = Notification.objects.filter(recipient=user)
        return result[::-1]