from django.urls import path

from .views import RegisterView, ActivateView, LoginView, RefreshView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('activate', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', RefreshView.as_view(), name='refresh'),
]
