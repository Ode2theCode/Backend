import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.core.serializers.json import DjangoJSONEncoder

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import Chat, Message
from authentication.models import User

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        try:
            self.chat = Chat.objects.get(group__title=self.room_name)
        except Chat.DoesNotExist:
            self.close()
            
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', b'').decode()
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = self.get_user_from_token(token)
            if user:
                self.scope['user'] = user
            else:
                self.close()
                return
        else:
            self.close()
            return
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        
        messages =  self.get_chat_messages()
        self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }, cls=DjangoJSONEncoder))

    
    def get_chat_messages(self):
        return list(self.chat.messages.all().order_by('timestamp').values(
            'content', 'sender__username', 'timestamp'
        ))
        
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope["user"]
        
        db_message = Message.objects.create(
            chat=self.chat,
            content=message,
            sender=user
        )
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message", 
                "message": db_message.content, 
                "username": db_message.sender.username,
                "timestamp": db_message.timestamp.isoformat(),
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))