from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
)
from rest_framework.exceptions import ErrorDetail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Admin
from .views import RegisterView


class LoginViewTests(APITestCase):
    """Тесты авторизации."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name="Tim",
        )

    def test_login_admin(self):
        data = {
            'email': 'test@test.ru',
            'password': '1234',
            'full_name': 'Tim',
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
        user = Admin.objects.create_user(
            email='test@test.ru',
            password='1234',
            full_name="Tim",
        )
        self.refresh = RefreshToken.for_user(user)

    def test_refresh_client(self):
        data = {
            'refresh': str(self.refresh),
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


class PasswordRecoveryTests(APITestCase):
    """Тестирование восстановления пароля."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )

    def test_just_password_recovery(self):
        response = self.client.post(
            path=reverse("admin_password_recovery"),
            data={
                "email": "check@check.ru",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("message"),
            'Check your email for the verification_code.',
        )

    def test_missing_parameters(self):
        response = self.client.post(
            path=reverse("admin_password_recovery"),
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_this_email_does_not_exist(self):
        response = self.client.post(
            path=reverse("admin_password_recovery"),
            data={
                "email": "check_check@check.ru",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data.get("email"),
            [
                ErrorDetail(
                    string='An account with this email does not exist.',
                    code='invalid',
                ),
            ],
        )


class PasswordRecoveryVerifyTests(APITestCase):
    """Тестирование верификации восстановления пароля."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )

        self.email = "check@check.ru"
        self.verification_code = "12345"
        cache.set(
            key=f"verification_code_{self.email}",
            value=self.verification_code,
            timeout=1000,
        )

    def test_just_password_recovery_verify(self):
        response = self.client.post(
            path=reverse("admin_password_verify"),
            data={
                "email": self.email,
                "verification_code": self.verification_code,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data.get("message"),
            ['Verification was successful.'],
        )

    def test_missing_parameters(self):
        response = self.client.post(
            path=reverse("admin_password_verify"),
            data={
                "email": self.email,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verification_code", response.data)

    def test_invalid_email(self):
        response = self.client.post(
            path=reverse("admin_password_verify"),
            data={
                "email": "check_check@check.ru",
                "verification_code": self.verification_code,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_invalid_verification_code(self):
        response = self.client.post(
            path=reverse("admin_password_verify"),
            data={
                "email": self.email,
                "verification_code": "12344",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verification_code", response.data)
        self.assertEqual(
            response.data.get("verification_code"),
            ['The verification code is not active.'],
        )


class PasswordRecoveryChangeTests(APITestCase):
    """Тестирование смены пароля для администратора."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )
        self.email = "check@check.ru"
        cache.set(
            key=f"password_recovery_{self.email}",
            value=True,
            timeout=1000,
        )

    def test_just_change_password(self):
        response = self.client.post(
            path=reverse("admin_password_change"),
            data={
                "email": self.email,
                "password": "123456789",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data.get("message"),
            ['Password successfully changed.'],
        )

    def test_missing_parameters(self):
        response = self.client.post(
            path=reverse("admin_password_change"),
            data={
                "email": self.email,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_invalid_email(self):
        response = self.client.post(
            path=reverse("admin_password_change"),
            data={
                "email": "check_check@check.ru",
                "password": "123456789",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data.get("email"),
            [
                ErrorDetail(
                    string='An account with this email does not exist.',
                    code='invalid',
                ),
            ],
        )


class Test(APITestCase):
    """Tests for TaxiFareView."""

    def setUp(self):
        self.user = Admin.objects.create_user(
            email='proba@test.ru',
            password='test',
            full_name='Tim Dinner',
        )
        self.factory = APIRequestFactory()

        self.url = reverse('admin_register')
        self.view = RegisterView.as_view()

    def test_repeit_email(self):
        self.user = Admin.objects.create_user(
            email='test@test.ru',
            password='test',
            full_name='Tim Dinner',
        )
        request = self.factory.get(self.url, format='json')
        data = {
            'email': 'test@test.ru',
            'password': 'test',
            'full_name': 'Tim Dinner',
        }
        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
