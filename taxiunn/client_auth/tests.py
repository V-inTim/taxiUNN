from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Client


class RegisterViewTests(APITestCase):
    """Тесты регистрации."""

    def test_register_invalid_data(self):
        data = {
            'email': 'proba@test@ru',
            'password': '3333',
        }

        response = self.client.post(
            reverse('register'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterVerifyViewTests(APITestCase):
    """Тесты активации аккаунта."""

    def setUp(self):
        self.email = 'proba@mail.ru'
        self.code = '12345'
        self.user_data = {
            'email': 'proba@mail.ru',
            'password': '3333',
            'full_name': 'Tim',
        }
        cache.set(f'verification_code_{self.email}', self.code, timeout=300)
        cache.set(f'user_data_{self.email}', self.user_data, timeout=300)

    def test_register_verify_success(self):
        url = reverse('register_verify')  # Replace with your actual URL name
        data = {
            'email': self.email,
            'verification_code': self.code,
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'You have successfully registered.',
        )

    def test_register_verify_invalid_code(self):
        url = reverse('register_verify')  # Replace with your actual URL name
        data = {
            'email': self.email,
            'verification_code': '99999',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('verification_code'),
            [ErrorDetail(
                string='Incorrect verification code.',
                code='invalid',
            )],
        )

    def test_register_verify_missing_parameters(self):
        url = reverse('register_verify')  # Replace with your actual URL name
        data = {
            'email': self.email,
            # 'verification_code' is missing
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('verification_code'),
            [ErrorDetail(string='This field is required.', code='required')],
        )


class LoginViewTests(APITestCase):
    """Тесты авторизации."""

    def setUp(self):
        self.user = Client.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name='Tim',
        )

    def test_login_client(self):
        data = {
            'email': 'test@test.ru',
            'password': '1234',
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
        self.assertEqual(
            response.data.get('password'),
            [ErrorDetail(string='This field is required.', code='required')],
        )

    def test_login_client_invalid_credentials(self):
        data = {
            'email': 'test@test.ru',
            'password': '12345',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'], ["Invalid credentials."])


class RefreshViewTests(APITestCase):
    """Тесты refresh токена."""

    def setUp(self):
        user = Client.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name='Tim',
        )
        self.refresh = RefreshToken.for_user(user)

    def test_refresh_client(self):
        data = {
            'refresh_token': str(self.refresh),
        }
        response = self.client.post(
            reverse('refresh'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_client_missing_parameters(self):
        data = {}
        response = self.client.post(reverse('refresh'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('refresh'),
            [ErrorDetail(string='This field is required.', code='required')],
        )


class PasswordRecoveryViewTests(APITestCase):
    """Тесты восстановления пароля."""

    def setUp(self):
        self.user = Client.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name='Tim',
        )

    def test_client_password_recovery(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(
            reverse('password_recovery'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data.get('message'),
            "Check your email for the verification code.",
        )

    def test_client_password_recovery_missing_params(self):
        data = {}
        response = self.client.post(
            reverse('password_recovery'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email'),
            [ErrorDetail(string='This field is required.', code='required')],
        )

    def test_client_password_recovery_not_exist(self):
        data = {
            'email': 'test@test1.ru',
        }
        response = self.client.post(
            reverse('password_recovery'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(
                string='An account with this email does not exist.',
                code='invalid',
            )],
        )


class PasswordRecoveryVerifyViewTests(APITestCase):
    """Тесты верификации при восстановлении пароля."""

    def setUp(self):
        self.user = Client.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name='Tim',
        )
        self.email = 'test@test.ru'
        self.code = '34567'
        cache.set(f'verification_code_{self.email}', self.code, timeout=300)

    def test_ok(self):
        data = {
            'email': 'test@test.ru',
            'verification_code': '34567',
        }
        response = self.client.post(
            reverse('password_recovery_verify'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data.get('message'),
            'Verification was successful.',
        )

    def test_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(
            reverse('password_recovery_verify'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('verification_code'),
            [ErrorDetail(string='This field is required.', code='required')],
        )

    def test_account_not_exist(self):
        data = {
            'email': 'test@test1.ru',
            'verification_code': '34567',
        }
        response = self.client.post(
            reverse('password_recovery_verify'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(
                string='An account with this email does not exist.',
                code='invalid',
            )],
        )


class PasswordRecoveryChangeViewTests(APITestCase):
    """Тесты изменения пароля."""

    def setUp(self):
        self.user = Client.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name='Tim',
        )
        self.email = 'test@test.ru'
        cache.set(
            key=f'password_recovery_{self.email}',
            value=True,
            timeout=300,
        )

    def test_client_password_recovery_change(self):
        data = {
            'email': 'test@test.ru',
            'password': '34567',
        }
        response = self.client.post(
            reverse('password_recovery_change'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data.get('message'),
            'Password changed.',
        )

    def test_missing_parameters(self):
        data = {
            'email': 'test@test.ru',
        }
        response = self.client.post(
            reverse('password_recovery_change'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('password'),
            [ErrorDetail(string='This field is required.', code='required')],
        )

    def test_account_not_exist(self):
        data = {
            'email': 'test@test1.ru',
            'password': '34567',
        }
        response = self.client.post(
            reverse('password_recovery_change'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'],
            [ErrorDetail(
                string='An account with this email does not exist.',
                code='invalid',
            )],
        )
