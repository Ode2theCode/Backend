from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import EmailMessage
from django.core.validators import MaxLengthValidator
from django.utils import timezone



from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

import datetime

from FD import settings
from .models import *



class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    
    class Meta:
        model = TempUser
        fields = ['username', 'email', 'password', 'date_joined']
        
    def validate(self, attrs):
        temp_user_ttl = timezone.now() - datetime.timedelta(minutes=1)
        
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        user_username = User.objects.filter(username=username).first()
        user_email = User.objects.filter(email=email).first()
        
        temp_user_username = TempUser.objects.filter(username=username).first()
        print(temp_user_username)
        temp_user_email = TempUser.objects.filter(email=email).first()
        
        if temp_user_username:
            print(timezone.now() -temp_user_username.date_joined)
        
        if user_username:
            raise serializers.ValidationError('username already exists')
        
        if user_email:
            raise serializers.ValidationError('email already exists')
        
        if temp_user_username and temp_user_username.date_joined > temp_user_ttl:
            raise serializers.ValidationError('username already exists')
        
        if temp_user_email and temp_user_email.date_joined > temp_user_ttl:
            raise serializers.ValidationError('email already exists')
        
        if temp_user_username and temp_user_username.date_joined < temp_user_ttl:
            temp_user_username.delete()
        
        if temp_user_email and temp_user_email.date_joined < temp_user_ttl:
            temp_user_email.delete()
        
        return attrs

    def create(self, validated_data):
        temp_user = TempUser.objects.create(**validated_data)
        return temp_user
    

class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        otp = attrs.get('otp')
        
        try:
            otp_obj = OneTimePassword.objects.get(otp=otp)
            temp_user = otp_obj.temp_user
            user = User.objects.create_user(username=temp_user.username, email=temp_user.email, password=temp_user.password)
            temp_user.delete()
            return user
            
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError('invalid one time password')
    

class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'access_token', 'refresh_token']
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            temp_user = TempUser.objects.filter(username=username).exists()
            if temp_user:
                raise AuthenticationFailed('please verify your email')
            else:
                raise AuthenticationFailed('wrong password')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid password, try again')
        
        tokens = user.tokens()
        
        return {
            'email': user.email,
            'username': user.username,
            'access_token': str(tokens['access']),
            'refresh_token': str(tokens['refresh']),
        }
    
    
class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
     
        
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # relative_link = reverse('reset-password', kwargs={'uidb64': uidb64, 'token': token})
            # absolute_url = f'http://localhost:5173/{relative_link}'
            absolute_url = f'https://localhost:5173/reset-password/{uidb64}/{token}'
            
            email_subject = 'Reset your password'
            email_body = f'Click the link below to reset your password\n{absolute_url}'
            
            email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_USER, to=[email])
            email.send()
            
            return {'email': user.email}
            
        except User.DoesNotExist:
            raise AuthenticationFailed('user not found')
        
        
class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    uidb64 = serializers.CharField(max_length=255, validators=[MaxLengthValidator(255)], read_only=True)
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = User
        fields = ['password', 'uidb64']
        
    def validate(self, attrs):
        password = attrs.get('password')
        token = self.context.get('token')
        uidb64 = self.context.get('uidb64')
        
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed('The reset link is invalid', 401)
        
        user.set_password(password)
        user.save()
        
        return user
    

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
        
        def update(self, instance, validated_data):
            instance.level = validated_data.get('level', instance.level)
            instance.city = validated_data.get('city', instance.city)
            instance.neighborhood = validated_data.get('neighborhood', instance.neighborhood)
            profile_image = validated_data.get('profile_image', instance.profile_image)
            instance.save()
            return instance
    