from django.db import models


class TaxiFare(models.Model):
    """Model Class for taxi fare."""

    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Model string."""
        return self.name
