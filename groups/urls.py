from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', GroupView.as_view()),
    path('<str:title>/', GroupView.as_view()), #retrieve
    path('<str:title>/delete/', GroupView.as_view()),
    path('<str:title>/update/', GroupView.as_view()),
]