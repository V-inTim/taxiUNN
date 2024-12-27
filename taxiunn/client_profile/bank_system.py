import decimal
from asgiref.sync import sync_to_async

from client_auth.models import Client


@sync_to_async
def check_solvency(email: str, amount: decimal.Decimal):
    """Проверить платежеспособность."""
    user = Client.objects.get(email=email)
    print(user.bank_balance, amount, user.bank_balance >= amount)
    return user.bank_balance >= amount


@sync_to_async
def withdraw_amount(email: str, amount: decimal.Decimal):
    """Снять сумму со счета."""
    user = Client.objects.get(email=email)
    user.bank_balance = user.bank_balance - amount
    user.save()
