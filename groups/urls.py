from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', GroupCreateView.as_view()),
    path('<str:title>/', GroupRetrieveView.as_view()), #retrieve
    path('<str:title>/delete/', GroupDeleteView.as_view()),
    path('<str:title>/update/', GroupUpdateView.as_view()),
    
    # path('<str:title>/join/', GroupMembershipView.as_view()),
]