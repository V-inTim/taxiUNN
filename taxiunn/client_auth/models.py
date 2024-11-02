from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class ClientManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. .
    """

    def create_user(self, email: str, password: str):
        """
        Создает и возвращает клиента с имэйлом, паролем.

        Args:
            email (str): почта
            password (str): пароль

        Raises:
            TypeError: Если email или password равны None.

        Returns:
            Client
        """

        if email is None:
            raise TypeError('Clients must have an email address.')

        if password is None:
            raise TypeError('Clients must have a password.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str):
        """
        Создает и возвращает клиента с привилегиями суперадмина.

        Args:
            email (str): почта
            password (str): пароль

        Raises:
            TypeError: Если email или password равны None.

        Returns:
            Client

        """

        user = self.create_user(email, password)
        user.make_superuser()
        user.save()

        return user


class Client(AbstractBaseUser):
    """ Класс клиента. """

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

    bank_balance = models.IntegerField(default=1000)

    # USERNAME_FIELD - поле, которое используется для входа в систему.
    USERNAME_FIELD = 'email'

    # класс UserManager должен управлять объектами этого типа.
    objects = ClientManager()

    def __str__(self):
        """ Строковое представление модели """
        return self.email

    def make_superuser(self):
        self.is_staff = True
        self.is_superuser = True
