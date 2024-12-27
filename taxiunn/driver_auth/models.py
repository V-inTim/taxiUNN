from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.backends import BaseBackend

from taxi_fare.models import TaxiFare


class Car(models.Model):
    """Автомобиль."""

    make = models.CharField(null=True, default=None)
    model = models.CharField(null=True, default=None)
    color = models.CharField(null=True, default=None)
    state_number = models.CharField(null=True, default=None)


class DriverManager(BaseUserManager):
    """Менеджер для пользователя класса Driver."""

    def create_user(self, email: str, password: str, full_name: str):
        """Создание обычного пользователя."""
        if email is None:
            raise TypeError('Driver must have an email!')

        if password is None:
            raise TypeError('Driver must have a password!')

        if full_name is None or full_name == "":
            raise TypeError('Driver must have a name!')

        user = self.model(
            full_name=full_name,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str, full_name: str):
        """Создание суперпользователя."""
        user = self.create_user(email, password, full_name)
        user.make_superuser()
        user.save()

        return user


def get_default_fare():
    """Дать дефолтное значение."""
    TaxiFare.objects.create(pk=1, price='100.00', name='usual')
    return 1


class Driver(AbstractBaseUser):
    """Класс водителя."""

    email = models.EmailField(db_index=True, unique=True)
    full_name = models.CharField(null=True, default=None)

    is_active = models.BooleanField(default=True)
    is_stuff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    fare = models.ForeignKey(
        TaxiFare,
        on_delete=models.DO_NOTHING,
        null=False,
        default=get_default_fare,
    )
    car = models.OneToOneField(Car, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'email'

    objects = DriverManager()

    def __str__(self):
        """Строковое представление объекта класса Driver."""
        return self.email

    def make_superuser(self):
        """Создаёт объект класса Driver с привелегиями суперпользователя."""
        self.is_staff = True
        self.is_superuser = True

    def fget_full_name(self):
        """Метод get для взятия полного имени."""
        return self.full_name

    def fget_short_name(self):
        """Метод get для взятия короткого имени."""
        return self.full_name.split()[0]

    def fget_data(self) -> dict:
        """Метод get для взятия свех обязательных данных."""
        return {
            'email': self.email,
            'password': self.password,
            'full_name': self.full_name,
        }


class DriverBackend(BaseBackend):
    """Класс для управления процессом аутентификации водителя."""

    def authenticate(self, request, email=None, password=None):
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
