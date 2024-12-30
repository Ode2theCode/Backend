import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, TempUser
import boto3
from moto import mock_aws
from django.core import mail
from django.conf import settings
import os

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )
    return user

@pytest.fixture
def test_temp_user():
    temp_user = TempUser.objects.create(
        email='temp@example.com',
        username='tempuser',
        password='temppass123',
        otp='123456'
    )
    return temp_user

@pytest.fixtureh
def auth_client(api_client, test_user):
    tokens = test_user.tokens()
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client

@pytest.fixture
def aws_credentials():
    boto3.setup_default_session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing"
    )

@pytest.fixture
def s3_bucket(aws_credentials):
    with mock_aws():
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        yield s3

@pytest.mark.django_db
class TestAuthentication:
    def test_register_user_success(self, api_client):
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert TempUser.objects.filter(email=data['email']).exists()

    def test_verify_email_success(self, api_client, test_temp_user):
        url = reverse('verify-email')
        data = {'otp': test_temp_user.otp}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert User.objects.filter(email=test_temp_user.email).exists()
        assert not TempUser.objects.filter(email=test_temp_user.email).exists()

    def test_login_success(self, api_client, test_user):
        url = reverse('login')
        data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        

    def test_password_reset_request(self, api_client, test_user):
        url = reverse('password-reset')
        data = {'email': test_user.email}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == test_user.email
        
        otp = mail.outbox[0].body.split()[-1]
        confirmation_url = reverse('password-reset-confirm')
        data = {'otp': otp}
        response = api_client.post(confirmation_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        
            
    

    def test_change_password(self, auth_client, test_user):
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.check_password('newpass123')

    @mock_aws
    def test_update_user_profile(self, auth_client, test_user, s3_bucket):
        url = reverse('user-update')
        with open('test_image.jpg', 'wb') as f:
            f.write(b'fake image content')
        
        with open('test_image.jpg', 'rb') as image:
            data = {
                'username': 'updateduser',
                'level': 'B2',
                'city': 'Test City',
                'profile_image': image
            }
            response = auth_client.patch(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.username == 'updateduser'
        assert test_user.level == 'B2'
        assert test_user.city == 'Test City'
        assert test_user.profile_image is not None

        os.remove('test_image.jpg')

    def test_delete_account(self, auth_client, test_user):
        url = reverse('delete-account')
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert not User.objects.filter(id=test_user.id).exists()

    def test_register_existing_user(self, api_client, test_user):
        url = reverse('register')
        data = {
            'email': test_user.email,
            'username': test_user.username,
            'password': 'newpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_login_failure_wrong_credentials(self, api_client, test_user):
        url = reverse('login')
        data = {'username': test_user.username, 'password': 'invalidpass'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED