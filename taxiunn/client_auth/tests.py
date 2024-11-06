from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
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


class PasswordRecoveryViewTests(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(email='test@test.ru',
                                               password='1234')

    def test_client_password_recovery(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(reverse('password_recovery'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'),
                         "Check your email for the verification code.")

    def test_client_password_recovery_missing_parameters(self):
        data = {}
        response = self.client.post(reverse('password_recovery'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_client_password_recovery_account_not_exist(self):
        data = {
            'email': 'test@test1.ru',
        }
        response = self.client.post(reverse('password_recovery'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(string='An account with this email does not exist.',
                         code='invalid')]
            )


class PasswordRecoveryVerifyViewTests(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(email='test@test.ru',
                                               password='1234')
        self.email = 'test@test.ru'
        self.code = '34567'
        cache.set(f'verification_code_{self.email}', self.code, timeout=300)

    def test_client_password_recovery_verify(self):
        data = {
            'email': 'test@test.ru',
            'verification_code': '34567'
        }
        response = self.client.post(reverse('password_recovery_verify'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'),
                         'Verification was successful.')

    def test_client_password_recovery_verify_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(reverse('password_recovery_verify'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('verification_code'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_client_password_recovery_verify_account_not_exist(self):
        data = {
            'email': 'test@test1.ru',
            'verification_code': '34567'
        }
        response = self.client.post(reverse('password_recovery_verify'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(string='An account with this email does not exist.',
                         code='invalid')]
        )


class PasswordRecoveryChangeViewTests(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(email='test@test.ru',
                                               password='1234')
        self.email = 'test@test.ru'
        cache.set(f'password_recovery_{self.email}', True, timeout=300)

    def test_client_password_recovery_change(self):
        data = {
            'email': 'test@test.ru',
            'password': '34567',
        }
        response = self.client.post(reverse('password_recovery_change'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'),
                         'Password changed.')

    def test_client_password_recovery_change_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(reverse('password_recovery_change'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('password'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_client_password_recovery_change_account_not_exist(self):
        data = {
            'email': 'test@test1.ru',
            'password': '34567'
        }
        response = self.client.post(reverse('password_recovery_change'), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(string='An account with this email does not exist.',
                         code='invalid')]
        )
