from datetime import timedelta
import random
from django.utils import timezone
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage

from rest_framework.exceptions import ValidationError
from rest_framework import status

import boto3

from notifications.models import Notification
from .models import *
from .utils import send_otp_email
from FD import settings

from notifications.consumers import NotificationConsumer


class UserService:
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    
    @staticmethod
    def delete_s3_object(file_path):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
        


    
    @staticmethod
    def check_username(username):
        if User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'Username already exists', 'status': status.HTTP_400_BAD_REQUEST})
    
    @staticmethod
    def check_email(email):
        if User.objects.filter(email=email).exists():
            raise ValidationError({'detail': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def check_temp_user(cls, username, email):
        temp_user_by_username = TempUser.objects.filter(username=username).first()
        temp_user_by_email = TempUser.objects.filter(email=email).first()

        if temp_user_by_username and (timezone.now() - temp_user_by_username.date_joined) > timedelta(minutes=5):
            temp_user_by_username.delete()
            return
        
        if temp_user_by_email and (timezone.now() - temp_user_by_email.date_joined) > timedelta(minutes=5):
            temp_user_by_email.delete()
            return
            
        if temp_user_by_username :
            raise ValidationError({'detail': 'Username already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
        if temp_user_by_email:
            raise ValidationError({'detail': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
    
    @classmethod
    def create_temp_user(cls, data):
        cls.check_username(data['username'])
        cls.check_email(data['email'])
        cls.check_temp_user(data['username'], data['email'])
        
        TempUser.objects.create(username=data['username'], email=data['email'], password=data['password'])
        send_otp_email(data['email'])
    
    @classmethod
    def verify_email(cls, otp):
        if not TempUser.objects.filter(otp=otp).exists():
            raise ValidationError({'detail': 'invalid one time password', 'status': status.HTTP_400_BAD_REQUEST})
        
        temp_user = TempUser.objects.get(otp=otp)
        
        if User.objects.filter(username=temp_user.username).exists():
            raise ValidationError({'detail': 'user already verified', 'status': status.HTTP_400_BAD_REQUEST})
        
        user = User.objects.create(username=temp_user.username, email=temp_user.email, password=temp_user.password)
        user.set_password(temp_user.password)
        user.save()
        temp_user.delete()
    
    @staticmethod
    def resend_verification_email(email):
        if not TempUser.objects.filter(email=email).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        temp_user = TempUser.objects.get(email=email)
        
        if (timezone.now() - temp_user.date_joined) < timedelta(minutes=0):
            raise ValidationError({'detail': 'Please wait for 2 minutes before requesting another OTP', 'status': status.HTTP_400_BAD_REQUEST})
        
        send_otp_email(temp_user.email)
        temp_user.refresh_from_db()
        temp_user.date_joined = timezone.now()
        temp_user.save()
         
    @classmethod
    def check_level(cls, level):
        if level not in cls.VALID_LEVELS:
            raise ValidationError({'detail': f'Invalid level. Please select one of the following: {", ".join(cls.VALID_LEVELS)}', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def update_user(cls, user, data):
        
        if 'username' in data and user.username != data.get('username'):
            UserService.check_username(data.get('username'))
            user.username = data.get('username')
        
        if 'level' in data and user.level != data.get('level'):
            cls.check_level(data.get('level'))
            user.level = data.get('level')
        
        if not user.profile_image and data.get('profile_image'):
            path = data.get('profile_image').name + f'_{user.id}'
            user.profile_image.save(path, data.get('profile_image'))
        
        if user.profile_image and data.get('profile_image') == '':
            cls.delete_s3_object(user.profile_image.name)
            user.profile_image = None
        
        if user.profile_image and data.get('profile_image') and user.profile_image != data.get('profile_image'):
            cls.delete_s3_object(user.profile_image.name)
            path = data.get('profile_image').name + f'_{user.id}'
            user.profile_image.save(path, data.get('profile_image'))
            
        user.city = data.get('city', user.city)
        user.neighborhood = data.get('neighborhood', user.neighborhood)

        user.save()
        return user
    
    @staticmethod
    def change_password(user, new_password):        
        user.set_password(new_password)
        user.save()
        return user
    
    @staticmethod
    def login(username, password):
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise ValidationError({'detail': 'Invalid password', 'status': status.HTTP_400_BAD_REQUEST})
        
        if TempUser.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'Please verify your email', 'status': status.HTTP_400_BAD_REQUEST})
        
        tokens = user.tokens()
        return {
            'email': user.email,
            'username': user.username,
            'access_token': str(tokens['access']),
            'refresh_token': str(tokens['refresh']),
        }
        
    @staticmethod
    def request_reset_password(email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(email=email)
        
        if (OTP.objects.filter(user=user).exists()) and (timezone.now() - OTP.objects.get(user=user).date_created) < timedelta(minutes=2):
            raise ValidationError({'detail': 'Please wait for 2 minutes before requesting another OTP', 'status': status.HTTP_400_BAD_REQUEST})
        
        if OTP.objects.filter(user=user).exists():
            old_otp = OTP.objects.get(user=user)
            old_otp.delete()
        
        otp = random.randint(100000, 999999)
        OTP.objects.create(user=user, otp=otp)
        email_subject = 'Forgot Password'
        email_body = f'Your OTP is {otp}'
            
        email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_USER, to=[email])
        email.send()
        
    @staticmethod
    def confirm_reset_password(otp):
        print(otp)
        print(OTP.objects.all())
        if not OTP.objects.filter(otp=otp).exists():
            raise ValidationError({'detail': 'Invalid OTP', 'status': status.HTTP_400_BAD_REQUEST})
        if (timezone.now() - OTP.objects.get(otp=otp).date_created) > timedelta(minutes=2):
            raise ValidationError({'detail': 'OTP has expired', 'status': status.HTTP_400_BAD_REQUEST})
        
        otp = OTP.objects.get(otp=otp)
        user = otp.user
        tokens = user.tokens()
        otp.delete()
        return {
            'email': user.email,
            'username': user.username,
            'access_token': str(tokens['access']),
            'refresh_token': str(tokens['refresh']),
        }
        
    
    @classmethod
    def delete_account(cls, user):
        for group in user.owned_groups.all():
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{group.title} has been deleted")
                Notification.objects.create(recipient=member, message=f"{group.title} has been deleted")
            group.delete()
            
        if user.profile_image:
            cls.delete_s3_object(user.profile_image.name)
        
        user.delete()

        
          