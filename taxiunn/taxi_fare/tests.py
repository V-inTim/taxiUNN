from django.urls import reverse
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
)
from rest_framework import status

from .models import TaxiFare
from .views import TaxiFareView
from admin_auth.models import Admin


class TaxiFareTest(APITestCase):
    """Tests for TaxiFareView."""

    def setUp(self):
        self.fare = TaxiFare.objects.create(name='test', price=100)
        self.factory = APIRequestFactory()
        self.user = Admin.objects.create_user(
            email='proba@test.ru',
            password='test',
            full_name='Tim Dinner',
        )

        self.url = reverse('taxi_fare', kwargs={'pk': self.fare.pk})
        self.view = TaxiFareView.as_view()

    def test_receive_ok(self):
        request = self.factory.get(self.url, format='json')

        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.fare.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), 'test')

    def test_patch_ok(self):
        updated_data = {
            'name': 'updated_test',
            'price': 150,
        }
        request = self.factory.patch(self.url, updated_data, format='json')

        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.fare.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('price'), "150.00")

    def test_delete_ok(self):
        request = self.factory.delete(self.url, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request, pk=self.fare.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaxiFare.objects.filter(pk=self.fare.pk).exists())
