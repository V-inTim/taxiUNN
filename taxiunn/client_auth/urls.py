from django.urls import path

from .views import (
    RegisterVerifyView,
    LoginView,
    PasswordRecoveryChangeView,
    PasswordRecoveryVerifyView,
    PasswordRecoveryView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path(
        'register',
        RegisterView.as_view(),
        name='register',
    ),
    path(
        'activate',
        RegisterVerifyView.as_view(),
        name='register_verify',
    ),
    path(
        'login',
        LoginView.as_view(),
        name='login',
    ),
    path(
        'refresh',
        RefreshView.as_view(),
        name='refresh',
    ),
    path(
        'password-recovery',
        PasswordRecoveryView.as_view(),
        name='password_recovery',
    ),
    path(
        'password-recovery/verify',
        PasswordRecoveryVerifyView.as_view(),
        name='password_recovery_verify',
    ),
    path(
        'password-recovery/change',
        PasswordRecoveryChangeView.as_view(),
        name='password_recovery_change',
    ),
]
