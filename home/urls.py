from django.urls import include, path
from .views import *

urlpatterns = [
    path('', HomeView.as_view()),
    path('suggestions/', SuggestionsView.as_view()),
    
    path('user-time-slots/create/', UserTimeSlotCreateView.as_view()),
    path('user-time-slots/', UserTimeSlotListView.as_view()),
    path('user-time-slots/<int:id>/delete/', UserTimeSlotDeleteView.as_view()),
    
    path('group-time-slots/<str:title>/create/', GroupTimeSlotCreateView.as_view()),
    path('group-time-slots/<str:title>/', GroupTimeSlotListView.as_view()),
    path('group-time-slots/<str:title>/<int:id>/delete/', GroupTimeSlotDeleteView.as_view()),
    
    path('neighborhoods/', get_table_data, name='table_data'),
]
