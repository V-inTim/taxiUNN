from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
)
from django.urls import reverse
from rest_framework import status

from .views import DriverProfileView
from driver_auth.models import Driver


class DriverProfileTests(APITestCase):
    """Тестирование профиля водителя."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Driver.objects.create_user(
            email='test@test.ru',
            password='12345678',
            full_name='Lion Alex',
        )
        self.url = reverse('driver')
        self.view = DriverProfileView.as_view()

    def test_get_user_data(self):
        request = self.factory.get(
            path=self.url,
            format='json',
        )

        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('full_name'),
            'Lion Alex',
        )
        self.assertEqual(
            response.data.get('email'),
            'test@test.ru',
        )

    def test_delete_user(self):
        request = self.factory.delete(
            path=self.url,
            format='json',
        )

        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'User account successfully removed.',
        )

    def test_user_does_not_authenticate(self):
        request = self.factory.get(
            path=self.url,
            format='json',
        )

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get('detail'),
            "Authentication credentials were not provided.",
        )
