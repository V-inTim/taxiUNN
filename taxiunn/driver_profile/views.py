from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class DriverProfileView(APIView):
    """View данных профиля водителя."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        user = request.user
        return Response(
            user.fget_data(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request) -> Response:
        user = request.user
        user.delete()
        return Response(
            {'message': 'User account successfully removed.'},
            status=status.HTTP_200_OK,
        )
