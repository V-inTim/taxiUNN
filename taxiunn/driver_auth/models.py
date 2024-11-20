from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.backends import BaseBackend


def validation(func):
    """Функция-декоратор для валидации данных."""

    def wrapper(self, email, password, *args, **kwargs):
        """Валидация полей email и password."""
        if email is None:
            raise TypeError('Driver must have an email!')

        if password is None:
            raise TypeError('Driver must have a password!')

        return func(self, email, password, *args, **kwargs)
    return wrapper


class DriverManager(BaseUserManager):
    """Менеджер для пользователя класса Driver."""

    @validation
    def create_user(self, email, password):
        """Создание обычного пользователя."""
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    @validation
    def create_superuser(self, email, password):
        """Создание суперпользователя."""
        user = self.create_user(email, password)
        user.make_superuser()
        user.save()

        return user


class Driver(AbstractBaseUser):
    """Класс водителя."""

    email = models.EmailField(db_index=True, unique=True)
    full_name = models.CharField(null=True, default=None)

    is_active = models.BooleanField(default=True)
    is_stuff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tariff = models.CharField(null=True, default=None)
    rating = models.DecimalField(
        max_digits=2,
        null=True,
        default=None,
        decimal_places=2,
    )

    USERNAME_FIELD = 'email'

    objects = DriverManager()

    def __str__(self):
        """Строковое представление объекта класса Driver."""
        return self.email

    def make_superuser(self):
        """Создаёт объект класса Driver с привелегиями суперпользователя."""
        self.is_staff = True
        self.is_superuser = True


class DriverBackend(BaseBackend):
    """.Класс для управления процессом аутентификации водителя."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        """Метод для аутентификации."""
        try:
            user = Driver.objects.get(email=email)
        except Driver.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """Getter пользователя."""
        try:
            return Driver.objects.get(pk=user_id)
        except Driver.DoesNotExist:
            return None
