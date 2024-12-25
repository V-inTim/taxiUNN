
from channels.db import database_sync_to_async

from client_auth.authentication import ClientJWTAuthentication
from driver_auth.authentication import DriverJWTAuthentication


@database_sync_to_async
def get_client_from_token(token):
    """Получение клиента из токена."""
    try:
        jwt_auth = ClientJWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)

        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return None


@database_sync_to_async
def get_driver_from_token(token):
    """Получение водителя из токена."""
    try:
        jwt_auth = DriverJWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return None


class TokenAuthMiddleware:
    """Водительский аутентификационный middleware."""

    def __init__(self, inner):
        """Конструктор."""
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """Вызов."""
        headers = dict(scope['headers'])
        token = headers.get(b'token', None)
        if token:
            path = scope['path']
            if path.startswith('/ws/client'):
                scope['user'] = await get_client_from_token(token)
            elif path.startswith('/ws/driver'):
                scope['user'] = await get_driver_from_token(token)
            if scope['user']:
                return await self.inner(scope, receive, send)
            else:
                await send({
                    "type": "websocket.close",
                    "code": 4000,  # Custom close code for bad request
                })
        else:
            await send({
                "type": "websocket.close",
                "code": 4000,  # Custom close code for bad request
            })
