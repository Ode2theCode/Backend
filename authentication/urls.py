from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    
    path('login/', LoginUserView.as_view(), name='login'),


    
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    path('users/retrieve/', UserRetriveView.as_view(), name='user-retrieve'),
    path('users/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('users/update/', UserUpdateView.as_view(), name='user-update'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]