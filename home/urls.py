from django.urls import include, path
from .views import *

urlpatterns = [
    path('', HomeView.as_view()),
    
    path('time-slot/create/', TimeSlotCreateView.as_view()),
    path('time-slots/', TimeSlotListView.as_view()),
    path('time-slots/<int:id>/delete/', TimeSlotDeleteView.as_view()),
    
    path('group-time-slot/create/', GroupTimeSlotCreateView.as_view()),
    path('group-time-slots/', GroupTimeSlotListView.as_view()),
    path('group-time-slots/<int:id>/delete/', GroupTimeSlotDeleteView.as_view()),
]
