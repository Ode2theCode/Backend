from django.urls import include, path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('suggestions/', SuggestionsView.as_view(), name='suggestions'),
    path('all-groups/', AllGroupsView.as_view(), name='all-groups'),


    
    path('user-time-slots/create/', UserTimeSlotCreateView.as_view(), name='user-time-slot-create'),
    path('user-time-slots/', UserTimeSlotListView.as_view(), name='user-time-slot-list'),
    path('user-time-slots/<int:id>/delete/', UserTimeSlotDeleteView.as_view(), name='user-time-slot-delete'),
    
    path('group-time-slots/<str:title>/create/', GroupTimeSlotCreateView.as_view(), name='group-time-slot-create'),
    path('group-time-slots/<str:title>/', GroupTimeSlotListView.as_view(), name='group-time-slot-list'),
    path('group-time-slots/<str:title>/<int:id>/delete/', GroupTimeSlotDeleteView.as_view(), name='group-time-slot-delete'),
    
    path('neighborhoods/', get_table_data, name='table_data'),
]
