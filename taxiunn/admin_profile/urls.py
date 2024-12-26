from django.urls import path

from .views import AdminView

urlpatterns = [
    path('', AdminView.as_view(), name="admin_profile"),
]
