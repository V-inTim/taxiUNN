from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from .models import Admin


class AdminManager(BaseUserManager):
    """Специфика Django.

    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager.
    """

    def create_user(self, email: str, password: str) -> Admin:
        """Создает и возвращает администратора с имэйлом, паролем."""
        if email is None:
            raise TypeError('Clients must have an email address.')

        if password is None:
            raise TypeError('Clients must have a password.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str) -> Admin:
        """Создает и возвращает администратора с привилегиями суперадмина."""
        user = self.create_user(email, password)
        user.make_superuser()
        user.save()

        return user


class Admin(AbstractBaseUser):
    """Класс администратора."""

    email = models.EmailField(db_index=True, unique=True)
    full_name = models.CharField(null=True, default=None)

    is_active = models.BooleanField(default=True)
    # определяет, кто может войти в административную часть нашего сайта.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)
    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    # USERNAME_FIELD - поле, которое используется для входа в систему.
    USERNAME_FIELD = 'email'

    # класс UserManager должен управлять объектами этого типа.
    objects = AdminManager()

    def __str__(self):
        """Строковое представление модели."""
        return self.email

    def make_superuser(self):
        """Создание суперпользователя."""
        self.is_staff = True
        self.is_superuser = True
