from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
]