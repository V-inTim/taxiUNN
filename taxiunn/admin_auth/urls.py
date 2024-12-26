from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    RefreshView,
    PasswordRecoveryView,
    PasswordRecoveryVerifyView,
    PasswordRecoveryChangeView,
)

urlpatterns = [
    path(
        'login',
        LoginView.as_view(),
        name='admin_login',
    ),
    path(
        'refresh',
        RefreshView.as_view(),
        name='admin_refresh',
    ),
    path(
        'password-recovery',
        PasswordRecoveryView.as_view(),
        name='admin_password_recovery',
    ),
    path(
        'password-recovery/verify',
        PasswordRecoveryVerifyView.as_view(),
        name='admin_password_verify',
    ),
    path(
        'password-recovery/change',
        PasswordRecoveryChangeView.as_view(),
        name='admin_password_change',
    ),
    path(
        'register',
        RegisterView.as_view(),
        name='admin_register',
    ),
]
