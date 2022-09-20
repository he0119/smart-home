"""
ASGI config for home project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/zh-hans/4.0/howto/deployment/asgi/
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from strawberry.channels import GraphQLWSConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home.settings")
django_asgi_app = get_asgi_application()
# Import your Strawberry schema after creating the django ASGI application
# This ensures django.setup() has been called before any ORM models are imported
# for the schema.
from home.iot.views import BasicAuthMiddleware, IotConsumer
from home.schema import schema

websocket_urlpatterns = [
    path(r"graphql/", AuthMiddlewareStack(GraphQLWSConsumer.as_asgi(schema=schema))),  # type: ignore
    path(r"iot/", BasicAuthMiddleware(IotConsumer.as_asgi())),  # type: ignore
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
