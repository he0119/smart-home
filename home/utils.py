from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.test import TestCase
from graphql import GraphQLFormattedError
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


# from strawberry.extensions import Extension
# from strawberry.types import Info
# class CompatibilityExtension(Extension):
#     """尝试兼容 strawberry_django_plus"""

#     def resolve(self, _next, root, info: Info, *args, **kwargs):
#         if not hasattr(info.context.request, "user"):
#             info.context.request.user = info.context.request.scope["user"]
#         return _next(root, info, *args, **kwargs)


def channel_group_send(group: str, message: dict) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group, message)  # type: ignore
