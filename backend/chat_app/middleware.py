from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """Simple token auth for Channels using DRF Token model.

    Expects a query string parameter named `token` on the WebSocket URL.
    Example: ws://host/ws/chat/<conversation_id>/?token=abc123
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Ensure DB connections are usable in async context
        close_old_connections()

        user = AnonymousUser()
        try:
            query_string = scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            token_key = params.get("token", [None])[0]

            if token_key:
                try:
                    token = await Token.objects.select_related("user").aget(key=token_key)
                    user = token.user
                except Token.DoesNotExist:
                    user = AnonymousUser()
        except Exception:
            user = AnonymousUser()

        scope["user"] = user
        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))






















