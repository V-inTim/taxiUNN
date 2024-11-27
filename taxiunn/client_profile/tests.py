from django.urls import reverse
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
)
from client_auth.models import Client
from rest_framework import status

from .views import ClientView


class ClientTests(APITestCase):
    """Тесты операций с клиентом."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Client.objects.create_user(
            email='swe@mail.ru',
            password='rrr',
            full_name='fff',
        )
        self.url = reverse('client')
        self.view = ClientView.as_view()

    def test_get_success(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('email'),
            'swe@mail.ru',
        )

    def test_delete_success(self):
        request = self.factory.delete(self.url, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'User account deleted.',
        )

    def test_auth_credentions_not_provided(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get('detail'),
            "Authentication credentials were not provided.",
        )
