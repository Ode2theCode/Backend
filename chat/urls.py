from django.urls import path

from .views import *

urlpatterns = [
    path('<str:title>/send/', ChatView.as_view()),
    path('<str:title>/retrieve/', ChatView.as_view()),
]