from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User

class AuthenticationAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    def test_login(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        
    def test_change_password(self):
        url = reverse('change-password')
        data = {'old_password': 'testpassword', 'new_password': 'newpassword'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "password changed successfully")

    def test_retrieve_user(self):
        url = reverse('user-retrieve')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def test_delete_user(self):
        url = reverse('user-delete')
        data = {'password': 'testpassword'}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "user deleted successfully")
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_update_user(self):
        url = reverse('user-update')
        data = {'username': 'newuser'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "user updated successfully")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newuser')