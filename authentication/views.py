from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from authentication.utils import send_otp_email
from .serializers import *
from .models import *
from .services import *

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
        serializer = self.serializer_class(data=request.data, context={'request': request})

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
    
    def delete(self, request, *args, **kwargs):
        
        user = request.user
        serializer = self.serializer_class(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if user.check_password(serializer.validated_data.get('password')):
            return Response("invalid password", status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response("user deleted successfully", status=status.HTTP_200_OK)
     

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class= UserUpdateSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request):
        try:
            user = request.user
            serializer = self.serializer_class(user, data = request.data, partial=True)
        
            if serializer.is_valid():
                UserService.update_user(user, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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