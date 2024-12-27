from django.urls import path

from .views import PriceListView

urlpatterns = [
    path('price_list/', PriceListView.as_view(), name="order_price_list"),
]
