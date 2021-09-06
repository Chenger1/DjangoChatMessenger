from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        """
        Potentially, checking for query_string is a bad idea. Because we can put some info in this scope key.
        Maybe, in ProtocolTypeRouter we can two 'websocket' route sources, for common django views and for RestApi
        And set different auth middlewares for them.
        """
        if scope.get('user') or not scope.get('query_string'):
            return await super().__call__(scope, receive, send)
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split('&')))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
