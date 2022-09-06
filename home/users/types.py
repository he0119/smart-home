from typing import Optional

from django.contrib.auth import get_user_model
from strawberry import auto
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay

from . import models


@gql.django.type(models.Config)
class Config(relay.Node):
    user: "User"
    key: auto
    value: auto


@gql.django.type(get_user_model())
class User(relay.Node):
    id: auto
    username: auto
    password: auto
    email: auto

    @gql.field
    def avatar_url(self) -> Optional[str]:
        if hasattr(self, "avatar"):
            return self.avatar.avatar.url  # type: ignore

    configs: list[Config]
