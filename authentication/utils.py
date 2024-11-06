from django.core.mail import EmailMessage
import secrets
from .models import OneTimePassword, User
from django.conf import settings

def send_otp_email(email):
    from_email = settings.EMAIL_HOST_USER
    
    otp = secrets.randbelow(10**6)
    otp = str(otp).zfill(6)
    
    user = User.objects.get(email=email)
    OneTimePassword.objects.create(user=user, otp=otp)
    
    email_subject = 'One Time Password'
    email_body = f'Thanks for registering on freediscussion.ir.\nYour One Time Password is {otp}' 
    
    confirmation_email = EmailMessage(subject=email_subject, body=email_body, from_email=from_email, to=[email])
    confirmation_email.send()