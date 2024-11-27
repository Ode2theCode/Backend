from rest_framework import serializers

from .models import *

class ChatSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id', 'sender', 'chat', 'content', 'timestamp']
        
    def get_chat(self, obj):
        return obj.chat.group.title
    
    def get_sender(self, obj):
        return obj.sender.username