from dataclasses import dataclass
from typing import Any

from django.test import TestCase
from graphql import GraphQLFormattedError
from strawberry_django.test.client import TestClient


@dataclass
class Response:
    errors: list[GraphQLFormattedError]
    data: dict[str, Any]
    extensions: dict[str, Any] | None


class MyTestClient(TestClient):
    def __init__(self):
        super().__init__("/graphql/")

    def authenticate(self, user):
        """登录"""
        self.client.force_login(user)

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        asserts_errors: bool | None = True,
        files: dict[str, Any] | None = None,
    ) -> Response:
        """执行查询

        和之前的格式相同
        """
        return super().query(query, variables, headers, files, asserts_errors)  # type: ignore


class GraphQLTestCase(TestCase):
    client_class = MyTestClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为了正确的类型提示
        self.client: MyTestClient  # type: ignore


# def get_ws_client(user) -> WebsocketCommunicator:
#     """获取 WebSocket 客户端"""
#     from home.schema import schema

#     class DebuggableGraphQLWSConsumer(GraphQLWSConsumer):
#         async def get_context(self, *args, **kwargs):  # type: ignore[override]
#             context = await super().get_context(*args, **kwargs)
#             if context is None:
#                 return None
#             context["ws"].scope["user"] = user
#             return context

#     return WebsocketCommunicator(
#         DebuggableGraphQLWSConsumer.as_asgi(schema=schema, subscription_protocols=(GRAPHQL_TRANSPORT_WS_PROTOCOL,)),
#         "",
#         subprotocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL],
#     )
