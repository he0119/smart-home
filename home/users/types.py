import strawberry
import strawberry_django
from django.contrib.auth import get_user_model
from django.utils import timezone
from strawberry import relay
from strawberry.types import Info

from . import models


@strawberry_django.filters.filter(model=get_user_model(), lookups=True)
class UserFilter:
    username: strawberry.auto


@strawberry_django.type(models.Session)
class Session(relay.Node):
    expire_date: strawberry.auto
    user: "User"
    user_agent: strawberry.auto
    last_activity: strawberry.auto
    ip: strawberry.auto

    @strawberry.field
    def is_valid(self) -> bool:
        return self.expire_date > timezone.now()

    @strawberry.field
    def is_current(self, info: Info) -> bool:
        return info.context.request.session.session_key == self.session_key  # type: ignore


@strawberry_django.type(models.Config)
class Config(relay.Node):
    user: "User"
    key: strawberry.auto
    value: strawberry.auto


@strawberry_django.type(models.Avatar)
class Avatar(relay.Node):
    user: "User"
    avatar: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(get_user_model())
class User(relay.Node):
    id: strawberry.auto
    username: strawberry.auto
    password: strawberry.auto
    email: strawberry.auto
    session: list[Session]
    avatar: Avatar

    @strawberry_django.field(select_related=["avatar"])
    def avatar_url(self) -> str | None:
        if hasattr(self, "avatar"):
            return self.avatar.avatar.url  # type: ignore

    configs: list[Config]
