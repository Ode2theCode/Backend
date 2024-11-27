from django.db import models



class Chat(models.Model):
    group = models.OneToOneField('groups.Group', on_delete=models.CASCADE, related_name='chat')
    
    
    def __str__(self) -> str:
        return self.group.title
    
    
class Message(models.Model):
    chat = models.ForeignKey('chat.Chat', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='sent_messages')
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    