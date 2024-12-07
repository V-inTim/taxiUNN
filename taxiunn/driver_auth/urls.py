from django.urls import path

from .views import (
    RegistrationView,
    VerificationOfRegistrationView,
    LoginView,
    RefreshView,
)

urlpatterns = [
    path(
        'register',
        RegistrationView.as_view(),
        name='registration',
    ),
    path(
        'activate',
        VerificationOfRegistrationView.as_view(),
        name='verify_register',
    ),
    path(
        'login',
        LoginView.as_view(),
        name='login_driver',
    ),
    path(
        'refresh',
        RefreshView.as_view(),
        name='refresh_driver',
    ),
]
