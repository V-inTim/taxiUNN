from rest_framework import serializers
from .models import TaxiFare


class TaxiFareSerializer(serializers.ModelSerializer):
    """Serializer for TaxiFare."""

    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = TaxiFare
        fields = ['id', 'name', 'price']


class TaxiFareCreateSerializer(serializers.ModelSerializer):
    """Serializer for create TaxiFare."""

    name = serializers.CharField(max_length=100, write_only=True)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
    )

    class Meta:
        model = TaxiFare
        fields = ['id', 'name', 'price']

    def validate_name(self, value):
        """Validate field name in TaxiFare model."""
        if TaxiFare.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Taxi fare with such name exist.",
            )
        return value
