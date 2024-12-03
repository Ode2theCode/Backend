from django.db import models

class Notification(models.Model):
    recipient = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"
        
