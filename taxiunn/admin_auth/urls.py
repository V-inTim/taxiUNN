from django.urls import path

from .views import LoginView, RefreshView

urlpatterns = [
    path('login', LoginView.as_view(), name='admin_login'),
    path('refresh', RefreshView.as_view(), name='admin_refresh'),
]
