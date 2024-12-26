import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from django.core.serializers.json import DjangoJSONEncoder

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from authentication.models import User

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        token = self.scope['url_route']['kwargs']['token']
        user = self.get_user_from_token(token)
        
        if not user:
            self.close(403)
        
        self.scope['user'] = user

        
        async_to_sync(self.channel_layer.group_add)(
            f"user_{user.id}",
            self.channel_name
        )
        
        self.accept()
        
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            f"user_{self.scope['user'].id}",
            self.channel_name
        )
        
    def send_notification(user, message):
        notification = {
            'message': message,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'notify',
                'notification': notification,
            }
        )

    def notify(self, event):
        notification = event['notification']
        self.send(text_data=json.dumps(notification, cls=DjangoJSONEncoder))