from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from admin_auth.models import Admin


class AdminViewTests(APITestCase):
    """Тесты админских данных."""

    def setUp(self):
        self.user = Admin.objects.create(
            password="aaaa",
            email='admin@example.com',
            full_name='Admin User',
        )

        # Аутентифицируем пользователя
        self.client.force_authenticate(user=self.user)

    def test_retrieve_admin(self):
        # Тест для получения данных админа
        url = reverse('admin_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@example.com')
        self.assertEqual(response.data['full_name'], 'Admin User')

    def test_update_admin(self):
        # Тест для обновления данных админа
        url = reverse('admin_profile')
        data = {'full_name': 'Updated Admin User'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Admin User')

    def test_update_admin_invalid_data(self):
        # Тест для обновления данных админа с некорректными данными
        url = reverse('admin_profile')
        data = {'full_name': ''}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
