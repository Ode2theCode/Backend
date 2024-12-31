from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated



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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResendVerificationEmailView(APIView):
    serializer_class = ResendVerificationEmailSerializer
    def post(self, request):
        try:
            UserService.resend_verification_email(request.data['email'])
            return Response("verification email sent successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginUserView(APIView):
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tokens = UserService.login(serializer.validated_data['username'], serializer.validated_data['password'])
            return Response(tokens, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
 
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request):
        try:
            tokens = UserService.confirm_reset_password(request.data['otp'])
            return Response(tokens, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class UserRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class= UserRetriveSerializer
    
    def get(self, request):
        try:
            user = request.user
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class= ChangePasswordSerializer
    
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            username = request.user.username
            user = User.objects.get(username=username)
            
            new_password = serializer.validated_data.get('new_password')
            
            UserService.change_password(user, new_password)
            return Response("password changed successfully", status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            UserService.delete_account(request.user)
            return Response("account deleted successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

