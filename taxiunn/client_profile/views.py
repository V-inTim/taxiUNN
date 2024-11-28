from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class ClientView(APIView):
    """View клиентских данных."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            user.get_data(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {'message': 'User account deleted.'},
            status=status.HTTP_200_OK,
        )
