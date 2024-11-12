from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authentication.utils import send_otp_email
from .serializers import *
from .models import *


class RegisterUserView(APIView):
    serializer_class = UserCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            temp_user = serializer.data
            send_otp_email(temp_user['email'])
            return Response({
                'data': temp_user,
                'message': 'User created successfully\n Please check your email for One Time Password',
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            return Response({
                'message': 'account verified successfully',
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginUserView(APIView):
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            return Response("password reset link has been sent to your email", status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
 
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data, context={'request': request, 'uidb64': uidb64, 'token': token})
        
        if serializer.is_valid(raise_exception=True):
            return Response("password reset successfully", status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutUserView(APIView):
    serializer_class = UserLogoutSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response("logout successfully", status=status.HTTP_200_OK)
        except:
            return Response("invalid token", status=status.HTTP_400_BAD_REQUEST)
        
class UserRetriveView(APIView):
    serializer_class= UserRetriveSerializer
    
    def get(self, request, username):
        user = User.objects.get(username=username)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)