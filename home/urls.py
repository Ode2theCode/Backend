from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()),
]
