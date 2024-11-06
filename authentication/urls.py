from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('login/', LoginUserView.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]