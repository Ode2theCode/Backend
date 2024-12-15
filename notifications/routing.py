from django.urls import re_path

from .consumers import NotificationConsumer

notifications_websocket_urlpatterns = [
    re_path(r"ws/notifications/(?P<token>[-\w.]+)/$", NotificationConsumer.as_asgi()),

]