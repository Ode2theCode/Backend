from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', GroupCreateView.as_view(), name='create-group'),
    path('<str:title>/', GroupRetrieveView.as_view(), name='retrieve-group'), 
    path('<str:title>/update/', GroupUpdateView.as_view(), name='update-group'),
    path('<str:title>/delete/', GroupDeleteView.as_view(), name='delete-group'),
    
    
    path('<str:title>/join/', GroupJoinRequestView.as_view(), name='join-group'),
    path('<str:title>/cancel/', GroupCancelRequestView.as_view(), name='cancel-join-request'),
    path('<str:title>/leave/', GroupLeaveView.as_view(), name='leave-group'),

    
    path('<str:title>/members/', GroupMemberListView.as_view(), name='retrieve-members'),
    path('<str:title>/pending/', GroupPendingRequestView.as_view(), name='retrieve-pending-members'),
    path('<str:title>/accept/', GroupAcceptRequestView.as_view(), name='accept-request'),
    path('<str:title>/decline/', GroupDeclineRequestView.as_view(), name='decline-request'),
    path('<str:title>/kick/', GroupKickView.as_view(), name='kick-member'),

]