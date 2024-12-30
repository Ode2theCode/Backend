from django.urls import path, include
from .views import *

urlpatterns = [
    path('all-notifications/', AllNotificationsView.as_view(), name='all-notifications'),
    path('delete-notification/', DeleteNotificationView.as_view(), name='delete-notification'),
    path('delete-all-notifications/', DeleteAllNotificationsView.as_view(), name='delete-all-notifications'),
]