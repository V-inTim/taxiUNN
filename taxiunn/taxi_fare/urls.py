from django.urls import path

from .views import (
    TaxiFareView,
    TaxiFareCreateView,
    TaxiFareListView,
)

urlpatterns = [
    path('<int:pk>/', TaxiFareView.as_view(), name="taxi_fare"),
    path('', TaxiFareCreateView.as_view(), name="taxi_fare_create"),
    path('list/', TaxiFareListView.as_view(), name="taxi_fare_list"),
]
