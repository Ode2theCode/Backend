from .models import Notification
from rest_framework.exceptions import ValidationError

class NotificationService:
    @staticmethod
    def get_notifications(user):
        result = Notification.objects.filter(recipient=user)
        return result[::-1]
    
    def delete_notification(user, notification_id):
        try:
            notification = Notification.objects.get(recipient=user, id=notification_id)
            notification.delete()
        except Notification.DoesNotExist:
            raise ValidationError({'detail': 'Notification not found', 'status': 404})
        
    def delete_all_notifications(user):
        Notification.objects.filter(recipient=user).delete()