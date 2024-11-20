from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework import status

from .models import Admin


class LoginViewTests(APITestCase):
    """Тесты авторизации."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email='test@test.ru',
            password='1234',
        )

    def test_login_admin(self):
        data = {
            'email': 'test@test.ru',
            'password': '1234',
        }
        response = self.client.post(
            reverse('admin_login'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_admin_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(
            reverse('admin_login'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('password'),
            [ErrorDetail(string='This field is required.', code='required')],
        )

    def test_login_admin_invalid_credentials(self):
        data = {
            'email': 'test@test.ru',
            'password': '12345',
        }
        response = self.client.post(
            reverse('admin_login'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(
            response.data.get('password'),
            ["Invalid credentials."],
        )


class RefreshViewTests(APITestCase):
    """Тесты refresh токена."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email='test@test.ru',
            password='1234',
        )
        data = {
            'email': 'test@test.ru',
            'password': '1234',
        }
        response = self.client.post(
            reverse('admin_login'),
            data,
            format='json',
        )
        self.refresh = response.data['refresh']

    def test_refresh_client(self):
        data = {
            'refresh': self.refresh,
        }
        response = self.client.post(
            reverse('admin_refresh'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_client_missing_parameters(self):
        data = {}
        response = self.client.post(
            reverse('admin_refresh'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('refresh'),
            [ErrorDetail(string='This field is required.', code='required')],
        )
