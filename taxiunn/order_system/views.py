from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from client_auth.authentication import (
    ClientJWTAuthentication,
    IsAuthenticatedClient,
)
from .serializers import CoordinateSerializer
from .order_planning_service.price_list import get_price_list
from .order_planning_service.price_manager import PriceManager


class PriceListView(APIView):
    """Отображает список цен по тарифам."""

    permission_classes = [IsAuthenticatedClient]
    authentication_classes = [ClientJWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = CoordinateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        location_to = serializer.validated_data['location_to']
        location_from = serializer.validated_data['location_from']
        try:
            price_list = get_price_list(location_from, location_to)
        except Exception:
            return Response(
                {'error': ['Error when interacting with the service.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = request.user
        PriceManager.set(email, price_list)

        return Response(
            {'price_list': price_list},
            status=status.HTTP_200_OK,
        )
