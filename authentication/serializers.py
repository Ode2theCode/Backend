from rest_framework import serializers

from .models import *



class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = TempUser
        fields = ['username', 'email', 'password', 'date_joined']


class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    class Meta:
        model = TempUser
        fields = ['otp']
    

class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password']
        
        
        
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email']

        
class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = User
        fields = ['password']       
    

class UserRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'level', 'date_joined', 'city', 'neighborhood', 'profile_image']
        

class UserDeleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = User
        fields = ['password']
        

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['level', 'city', 'neighborhood', 'profile_image']
        

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    new_password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = User
        fields = ['old_password', 'new_password']
