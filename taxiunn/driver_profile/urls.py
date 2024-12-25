from django.urls import path

from .views import DriverProfileView

urlpatterns = [
    path('', DriverProfileView.as_view(), name='driver'),
]
