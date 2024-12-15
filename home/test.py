from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from groups.models import Group
from home.models import UserTimeSlot, GroupTimeSlot

class TestHomeAPI(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='user@test.com', password='testpassword')
        cls.group = Group.objects.create(title='testgroup', owner=cls.user)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suggestions_view(self):
        url = reverse('suggestions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_groups_view(self):
        url = reverse('all-groups')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_time_slot(self):
        url = reverse('user-time-slot-create')
        data = {
            'day_of_week': 'Monday',
            'start_time': 9.00,
            'end_time': 17.00
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_user_time_slots(self):
        url = reverse('user-time-slot-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_time_slot(self):
        time_slot = UserTimeSlot.objects.create(user=self.user, day_of_week='Monday', start_time=9.00, end_time=17.00)
        url = reverse('user-time-slot-delete', kwargs={'id': time_slot.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_group_time_slot(self):
        url = reverse('group-time-slot-create', kwargs={'title': self.group.title})
        data = {
            'day_of_week': 'Monday',
            'start_time': 9.00,
            'end_time': 17.00
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_group_time_slots(self):
        url = reverse('group-time-slot-list', kwargs={'title': self.group.title})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_group_time_slot(self):
        time_slot = GroupTimeSlot.objects.create(group=self.group, day_of_week='Monday', start_time=9.00, end_time=17.00)
        url = reverse('group-time-slot-delete', kwargs={'title': self.group.title, 'id': time_slot.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)