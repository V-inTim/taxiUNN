from rest_framework import serializers
from driver_auth.models import Driver, Car
from taxi_fare.models import TaxiFare


class DriverSerializer(serializers.ModelSerializer):
    """Сериалайзер водительских данных."""

    make = serializers.CharField(write_only=True, required=True)
    model = serializers.CharField(write_only=True, required=True)
    color = serializers.CharField(write_only=True, required=True)
    state_number = serializers.CharField(write_only=True, required=True)
    fare_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Driver
        fields = [
            'email', 'full_name', 'fare_id', 'make',
            'model', 'color', 'state_number',
        ]
        # Указываем, что поля name и description также обязательны
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
        }

    def validate_fare_id(self, value):
        """Проверка имени тарифа."""
        if not TaxiFare.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Such fare not exist.",
            )
        return value

    def save(self, password: str):
        """Сохранить."""
        make = self.validated_data['make']
        model = self.validated_data['model']
        color = self.validated_data['color']
        state_number = self.validated_data['state_number']
        car = Car.objects.create(
            make=make,
            model=model,
            color=color,
            state_number=state_number,
        )
        car.save()

        fare_id = self.validated_data['fare_id']
        fare = TaxiFare.objects.filter(pk=fare_id).first()

        user = Driver.objects.create_user(
            email=self.validated_data['email'],
            full_name=self.validated_data['full_name'],
            password=password,
        )

        user.fare = fare
        user.car = car
        user.save()
