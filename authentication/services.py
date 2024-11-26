from datetime import datetime, timedelta
from urllib import response

from rest_framework.exceptions import ValidationError
from rest_framework import status

from .models import *
from .utils import send_otp_email

class UserService:
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    TTL = datetime.now() - timedelta(minutes=1)
    
    def check_username(username):
        if User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'Username already exists', 'status': status.HTTP_400_BAD_REQUEST})
    
    def check_email(email):
        if User.objects.filter(email=email).exists():
            raise ValidationError({'detail': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def check_temp_user(cls, username, email):
        temp_user_by_username = TempUser.objects.filter(username=username).first()
        temp_user_by_email = TempUser.objects.filter(email=email).first()
        
        if temp_user_by_username and temp_user_by_username.date_joined < cls.TTL:
            raise ValidationError({'detail': 'Username already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
        if temp_user_by_email and temp_user_by_email.date_joined < cls.TTL:
            raise ValidationError({'detail': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
        if temp_user_by_username and temp_user_by_username.date_joined > cls.TTL:
            temp_user_by_username.delete()
        
        if temp_user_by_email and temp_user_by_email.date_joined > cls.TTL:
            temp_user_by_email.delete()
    
    @classmethod
    def create_temp_user(cls, data):
        cls.check_username(data['username'])
        cls.check_email(data['email'])
        cls.check_temp_user(data['username'], data['email'])
        
        temp_user = TempUser.objects.create_user(data['username'], data['email'], data['password'])
        send_otp_email(data['email'])
        return response({'detail': 'User created successfully\n Please check your email for One Time Password', 'status': status.HTTP_201_CREATED})
    
    @classmethod
    def verify_email(cls, email, otp):
        if not OneTimePassword.objects.filter(otp=otp).exists():
            raise ValidationError({'detail': 'invalid one time password', 'status': status.HTTP_400_BAD_REQUEST})
        
        otp_obj = OneTimePassword.objects.get(otp=otp)
        temp_user = otp_obj.temp_user
        
        User.objects.create(uusername=temp_user.username, email=temp_user.email, password=temp_user.password)
        
        return response({'detail': 'email verified', 'status': status.HTTP_201_CREATED})
        
    
    @classmethod
    def check_level(cls, level):
        if level not in cls.VALID_LEVELS:
            raise ValidationError({'detail': f'Invalid level. Please select one of the following: {", ".join(cls.VALID_LEVELS)}', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def update_user(cls, user, data):
        user.level = data.get('level', user.level)
        cls.check_level(user.level)
        user.city = data.get('city', user.city)
        user.neighborhood = data.get('neighborhood', user.neighborhood)
        user.profile_image = data.get('profile_image', user.profile_image)
        user.save()
        return user
        
    
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError({'detail': 'Invalid password', 'status': status.HTTP_400_BAD_REQUEST})
        
        if old_password == new_password:
            raise ValidationError({'detail': 'New password cannot be the same as the old password', 'status': status.HTTP_400_BAD_REQUEST})
        
        user.set_password(new_password)
        user.save()
        return user