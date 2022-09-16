from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from graphql import GraphQLFormattedError
from strawberry.channels import GraphQLWSConsumer
from strawberry.permission import BasePermission
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
from strawberry.types import Info
from strawberry_django_plus.test.client import TestClient


class IsAuthenticated(BasePermission):
    """验证是否登录

    支持 websocket 和 http
    https://strawberry.rocks/docs/guides/permissions
    """

    message = "User is not authenticated"

    # This method can also be async!
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if not hasattr(info.context.request, "user"):
            user = info.context.request.scope["user"]
        else:
            user = info.context.request.user
        return user.is_authenticated and user.is_active


@dataclass
class Response:
    errors: List[GraphQLFormattedError]
    data: Dict[str, Any]
    extensions: Optional[Dict[str, Any]]


class MyTestClient(TestClient):
    def __init__(self):
        super().__init__("/graphql/")

    def authenticate(self, user):
        """登录"""
        self.client.force_login(user)

    def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        asserts_errors: Optional[bool] = True,
        files: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """执行查询

        和之前的格式相同
        """
        return super().query(query, variables, headers, asserts_errors, files)  # type: ignore


class GraphQLTestCase(TestCase):
    client_class = MyTestClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为了正确的类型提示
        self.client: MyTestClient


def channel_group_send(group: str, message: dict) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group, message)  # type: ignore


def get_ws_client(user) -> WebsocketCommunicator:
    """获取 WebSocket 客户端"""
    from home.schema import schema

    class DebuggableGraphQLWSConsumer(GraphQLWSConsumer):
        async def get_context(self, *args, **kwargs) -> object:
            context = await super().get_context(*args, **kwargs)
            context.tasks = self._handler.tasks  # type: ignore
            context.connectionInitTimeoutTask = None  # type: ignore
            context.ws.scope["user"] = user
            return context

    return WebsocketCommunicator(
        DebuggableGraphQLWSConsumer.as_asgi(
            schema=schema, subscription_protocols=(GRAPHQL_WS_PROTOCOL,)
        ),
        "",
        subprotocols=[
            GRAPHQL_WS_PROTOCOL,
        ],
    )
