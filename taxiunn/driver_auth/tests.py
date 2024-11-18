from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase


class DriverRegistrationTests(APITestCase):
    """ Тестирование регистрации водителя """

    def test_IncorrectEmail(self):
        data = {
            'email': 'thecoolestdriver&thehood@gmail.com',
            'password': '12345678',
        }

        response = self.client.post(
            path=reverse('register'),
            data=data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DriverVerificationOfRegistrationTests(APITestCase):
    """ Тестирование верификации авторизации водителя """

    def setUp(self):
        self.email = 'proba@mail.com'
        self.verification_code = '76543'
        self.user_data = {
            'email': self.email,
            'password': '12345678',
        }

        cache.set(
            f'verification_code_{self.email}',
            self.verification_code,
            timeout=1000
        )
        cache.set(
            f'user_data_{self.email}',
            self.user_data,
            timeout=1000
        )

    def test_correct_data(self):
        response = self.client.post(
            path=reverse('verify_register'),
            data={
                'email': self.email,
                'verification_code': self.verification_code,
            },
            format='json',
        )

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_data(self):
        response = self.client.post(
            path=reverse('verify_register'),
            data={
                'email': self.email,
                'verification_code': '78123',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
