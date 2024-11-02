from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache
from .models import Client


class RegisterViewTests(APITestCase):
    def test_register_invalid_data(self):
        url = reverse('register')  # Replace with your actual URL name
        data = {
            'email': 'proba@test@ru',
            'password': '3333',
            # Add other required fields for ClientSerializer
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ActivateViewTests(APITestCase):
    def setUp(self):
        self.email = 'proba@mail.ru'
        self.code = '12345'
        self.user_data = {
            'email': self.email,
            'password': '3333',
        }
        cache.set(f'verification_code_{self.email}', self.code, timeout=3600)
        cache.set(f'user_data_{self.email}', self.user_data, timeout=3600)

    def test_activate_success(self):
        url = reverse('activate')  # Replace with your actual URL name
        data = {
            'email': self.email,
            'verification_code': self.code,
        }

        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'You have successfully registered.')

    def test_activate_invalid_code(self):
        url = reverse('activate')  # Replace with your actual URL name
        data = {
            'email': self.email,
            'verification_code': '99999',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],
                         'Incorrect verification code.')

    def test_activate_missing_parameters(self):
        url = reverse('activate')  # Replace with your actual URL name
        data = {
            'email': self.email,
            # 'verification_code' is missing
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Missing parameters.')


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(email='test@test.ru',
                                               password='1234')

    def test_login_client(self):
        data = {
            'email': 'test@test.ru',
            'password': '1234'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_client_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Missing parameters.')

    def test_login_client_invalid_credentials(self):
        data = {
            'email': 'test@test.ru',
            'password': '12345'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid credentials.")


class RefreshViewTests(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(email='test@test.ru',
                                               password='1234')
        data = {
            'email': 'test@test.ru',
            'password': '1234'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.refresh = response.data['refresh']

    def test_refresh_client(self):
        data = {
            'refresh_token': self.refresh
        }
        response = self.client.post(reverse('refresh'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_client_missing_parameters(self):
        data = {}
        response = self.client.post(reverse('refresh'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Missing parameters.')
