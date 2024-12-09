from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', GroupCreateView.as_view()),
    path('<str:title>/', GroupRetrieveView.as_view()), #retrieve
    path('<str:title>/delete/', GroupDeleteView.as_view()),
    path('<str:title>/update/', GroupUpdateView.as_view()),
    
    path('<str:title>/members/', GroupMemberListView.as_view()),
    
    path('<str:title>/join/', GroupJoinRequestView.as_view()),
    path('<str:title>/cancel/', GroupCancelRequestView.as_view()),

    path('<str:title>/leave/', GroupLeaveView.as_view()),
    
    path('<str:title>/pending/', GroupPendingRequestView.as_view()),
    path('<str:title>/accept/', GroupAcceptRequestView.as_view()),
    path('<str:title>/decline/', GroupDeclineRequestView.as_view()),
    path('<str:title>/kick/', GroupKickView.as_view()),
]