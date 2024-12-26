from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from groups.models import Group
from groups.services import GroupService
from authentication.models import User

class TestGroupAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", 
            password="testpassword", 
            email="test@gmail.com"
        )
        
        cls.group_data = {
            "title": "Test Group",
            "description": "This is a test group",
            "level": "A1",
            "city": "Test City",
            "neighborhood": "Test Neighborhood",
            "meeting_url": "https://example.com",
            "private": False
        }

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_group_api(self):
        url = reverse('create-group')
        response = self.client.post(url, self.group_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get().title, 'Test Group')
    
    def test_retrieve_group_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        url = reverse('retrieve-group', kwargs={'title': group.title})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], group.title)
        group.delete()

    def test_update_group_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        url = reverse('update-group', kwargs={'title': group.title})
        updated_data = {
            "description": "Updated description",
            "level": "B1"
        }
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.description, "Updated description")
        self.assertEqual(group.level, "B1")
        group.delete()

    def test_delete_group_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        url = reverse('delete-group', kwargs={'title': group.title})
        response = self.client.delete(url)
        self.assertEqual(self.user.groups.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 0)

    def test_join_request_api(self):
        group = GroupService.create_group(self.user, self.group_data)

        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        self.client.force_authenticate(user=other_user)
        
        url = reverse('join-group', kwargs={'title': group.title})
        
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(group.members.filter(username="other_user").exists())
        group.members.remove(other_user)
        
        group.private = True
        group.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(group.pending_members.filter(username="other_user").exists())
        other_user.delete()
        group.delete()
            
    def test_cancel_request_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        
        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        group.add_pending_member(other_user)
        self.client.force_authenticate(user=other_user)
        
        url = reverse('cancel-join-request', kwargs={'title': group.title})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(group.pending_members.filter(username="other_user").exists())
        other_user.delete()
        group.delete()
    
    def test_leave_group_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        
        url = reverse('leave-group', kwargs={'title': group.title})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(group.members.filter(username=self.user.username).exists())
        group.delete()

    def test_member_list_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        url = reverse('retrieve-members', kwargs={'title': group.title})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], group.members.count())
        group.delete()
        
    def test_pending_member_list_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        group.add_pending_member(other_user)
        url = reverse('retrieve-pending-members', kwargs={'title': group.title})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], group.pending_members.count())
        other_user.delete()
        group.delete()
        
    def test_accept_request_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        
        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        group.add_pending_member(other_user)
        self.client.force_authenticate(user=other_user)
        
        data = {
            "username": other_user.username
        }
        
        url = reverse('accept-request', kwargs={'title': group.title})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(group.members.filter(username="other_user").exists())
        self.assertFalse(group.pending_members.filter(username="other_user").exists())
        other_user.delete()
        group.delete()
        
    def test_decline_request_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        
        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        group.add_pending_member(other_user)
        self.client.force_authenticate(user=other_user)
        
        data = {
            "username": other_user.username
        }
        url = reverse('decline-request', kwargs={'title': group.title})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(group.pending_members.filter(username="other_user").exists())
        other_user.delete()
        group.delete()
        
    def test_kick_member_api(self):
        group = GroupService.create_group(self.user, self.group_data)
        
        other_user = User.objects.create_user(
            username="other_user", 
            password="testpassword", 
            email="other@gmail.com"
        )
        group.add_member(other_user)
        self.client.force_authenticate(user=self.user)
        
        data = {
            "username": other_user.username
        }
        
        url = reverse('kick-member', kwargs={'title': group.title})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(group.members.filter(username="other_user").exists())
        other_user.delete()
        group.delete()
        
    def cleanup(self):
        self.user.delete()