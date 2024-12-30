from django.urls import path, include
from .views import *

urlpatterns = [
    path('all-notifications/', AllNotificationsView.as_view(), name='all-notifications'),
]