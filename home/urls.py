from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()),
    path('time-slot-create/', views.TimeSlotCreate.as_view()),
]
