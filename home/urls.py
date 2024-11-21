from django.urls import include, path
from .views import *

urlpatterns = [
    path('', HomeView.as_view()),
    path('suggestions/', SuggestionsView.as_view()),
    
    path('user-time-slots/create/', TimeSlotCreateView.as_view()),
    path('user-time-slots/', TimeSlotListView.as_view()),
    path('user-time-slots/<int:id>/delete/', TimeSlotDeleteView.as_view()),
    
    path('group-time-slots/create/', GroupTimeSlotCreateView.as_view()),
    path('group-time-slots/', GroupTimeSlotListView.as_view()),
    path('group-time-slots/<int:id>/delete/', GroupTimeSlotDeleteView.as_view()),
    
    path('neighborhoods/', get_table_data, name='table_data'),
]
