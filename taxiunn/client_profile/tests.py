from django.urls import reverse
from rest_framework.test import APITestCase

from client_auth.models import Client
from rest_framework import status


class AdminViewTests(APITestCase):
    """Тесты админских данных."""

    def setUp(self):
        self.user = Client.objects.create(
            password="aaaa",
            email='admin@example.com',
            full_name='Client User',
        )

        self.client.force_authenticate(user=self.user)

    def test_retrieve_admin(self):
        url = reverse('client_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@example.com')
        self.assertEqual(response.data['full_name'], 'Client User')

    def test_update_admin(self):
        url = reverse('client_profile')
        data = {'full_name': 'Updated Client User'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Client User')

    def test_update_admin_invalid_data(self):
        url = reverse('client_profile')
        data = {'full_name': ''}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
