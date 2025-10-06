"""
ASGI config for chat_app project.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns
from chat_app.middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})


