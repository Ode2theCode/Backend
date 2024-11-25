from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    
    path('login/', LoginUserView.as_view()),
    path('logout/', LogoutUserView.as_view()),

    
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('users/retrieve/', UserRetriveView.as_view()),
    path('users/delete/', UserDeleteView.as_view()),
    path('users/update/', UserUpdateView.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]