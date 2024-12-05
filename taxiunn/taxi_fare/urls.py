from django.urls import path

from .views import (
    TaxiFareView,
    TaxiFareCreateView,
)

urlpatterns = [
    path('<int:pk>/', TaxiFareView.as_view(), name="taxi_fare"),
    path('', TaxiFareCreateView.as_view(), name="taxi_fare_create"),
]
