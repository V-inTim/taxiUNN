from django.urls import path

from .views import (
    RegistrationView,
    VerificationOfRegistrationView
)

urlpatterns = [
    path(
        'register',
        RegistrationView.as_view(),
        name='registration'
    ),
    path(
        'activate',
        VerificationOfRegistrationView.as_view(),
        name='verify_register'
    ),
]
