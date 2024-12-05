import re

from rest_framework import serializers


def validate_password(value: str):
    """Password validation."""
    if len(value) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long.",
        )

    if not re.match(r"^[A-Za-z0-9!@#$%^&*(),.?|<>]{8,50}$", value):
        raise serializers.ValidationError(
            "The password contains invalid characters."
            "The password can only contain Latin letters, "
            "numbers and special characters !@#$%^&*(),.?|<>.",
        )
