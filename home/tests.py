from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from channels.testing import WebsocketCommunicator
from django.test import TestCase
from graphql import GraphQLFormattedError
from strawberry.channels import GraphQLWSConsumer
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
from strawberry_django_plus.test.client import TestClient


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

    def request(
        self,
        body: Dict[str, object],
        headers: Optional[Dict[str, object]] = None,
        files: Optional[Dict[str, object]] = None,
    ):
        kwargs: Dict[str, object] = {"data": body}
        # 默认的测试客户端居然没用上 headers
        if headers:
            kwargs.update(headers)
        if files:
            kwargs["format"] = "multipart"
        else:
            kwargs["content_type"] = "application/json"

        return self.client.post(self.path, **kwargs)

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
