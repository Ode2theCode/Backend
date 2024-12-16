from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from silk.profiling.profiler import silk_profile

from .serializers import *
from .models import *
from .services import *

class RegisterUserView(APIView):
    serializer_class = UserCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.create_temp_user(serializer.validated_data)
            return Response("user created successfully, please verify your email", status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        
    
class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            UserService.verify_email(serializer.validated_data['otp'])
            return Response("email verified successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        
    

class LoginUserView(APIView):
    serializer_class = UserLoginSerializer
    
    @silk_profile(name='login')
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tokens = UserService.login(serializer.validated_data['username'], serializer.validated_data['password'])
            return Response(tokens, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            UserService.request_reset_password(serializer.validated_data['email'])
            return Response("password reset link sent successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
   
 
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        try:
            UserService.confirm_reset_password(uidb64, token, serializer.validated_data['password'])
            return Response("password reset successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
    

        
class UserRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class= UserRetriveSerializer
    
    def get(self, request):
        user = request.user
        
        serializer = self.serializer_class(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class= UserDeleteSerializer
    
    def delete(self, request):
        
        user = request.user
        serializer = self.serializer_class(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data.get('password')):
            return Response("invalid password", status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response("user deleted successfully", status=status.HTTP_200_OK)
     

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request):
        try:
            user = request.user
            UserService.update_user(user, request.data)
            return Response("user updated successfully", status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("user not found", status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    serializer_class= ChangePasswordSerializer
    
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            username = request.user.username
            user = User.objects.get(username=username)
            
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')
            
            UserService.change_password(user, old_password, new_password)
        
        except User.DoesNotExist:
            return Response("user not found", status=status.HTTP_404_NOT_FOUND)
        
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        
        return Response("password changed successfully", status=status.HTTP_200_OK)
