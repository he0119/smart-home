from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.test import TestCase
from graphql import GraphQLFormattedError
from strawberry_django_plus.test.client import TestClient


@dataclass
class Response:
    errors: Optional[List[GraphQLFormattedError]]
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
        asserts_errors: Optional[bool] = False,
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
