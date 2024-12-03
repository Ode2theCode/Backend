import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from rest_framework_simplejwt.tokens import AccessToken

from .models import Notification
from authentication.models import User


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
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
        
        
        self.room_group_name = "owner_%s" % user.id
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        
        self.accept()
        
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except:
            return None
        
    def disconnect(self, close_code):
        pass
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification = text_data_json["notification"]
        user = self.scope["user"]
        
        db_notification = Notification.objects.create(
            recipient=user,
            message=notification
        )
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "notification_message",
                "notification": db_notification.message
            }
        )
        
    
    def send_notification(self, event):
        message = event["message"]
        
        self.send(text_data=json.dumps({
            "notification": message
        }))