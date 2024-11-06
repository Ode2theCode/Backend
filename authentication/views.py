from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authentication.utils import send_otp_email
from .serializers import *
from .models import *


class RegisterUserView(APIView):
    serializer_class = UserCreateSerializer
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_otp_email(user['email'])
            return Response({
                'data': user,
                'message': 'User created successfully\n Please check your email for One Time Password',
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmailView(APIView):    
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            return Response({
                'message': 'account verified successfully',
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)