from rest_framework.exceptions import ValidationError
from rest_framework import status

from groups.models import Group
from .models import *

class ChatService:
    
    @staticmethod
    def check_user(user, title):
        group = Group.objects.get(title=title)
        if not group.members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
    
    @staticmethod    
    def get_messages(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        chat = group.chat
        
        messages = chat.messages.all()
        return messages
    
    @classmethod
    def send_message(cls, user, title, content):
        cls.check_user(user, title)
        
        group = Group.objects.get(title=title)
        chat = group.chat
        message = Message.objects.create(chat=chat, sender=user, content=content)
        return message
        
        