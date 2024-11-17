from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()),
    path('time-slot/create/', views.TimeSlotCreateView.as_view()),
    path('time-slots/', views.TimeSlotListView.as_view()),
    path('time-slots/<int:id>/delete/', views.TimeSlotDeleteView.as_view()),
]
