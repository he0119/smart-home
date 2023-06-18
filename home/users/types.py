from django.contrib.auth import get_user_model
from django.utils import timezone
from strawberry import auto, relay
from strawberry.types import Info
from strawberry_django_plus import gql

from . import models


@gql.django.filters.filter(model=get_user_model(), lookups=True)
class UserFilter:
    username: auto


@gql.django.type(models.Session)
class Session(relay.Node):
    expire_date: auto
    user: "User"
    user_agent: auto
    last_activity: auto
    ip: auto

    @gql.field
    def is_valid(self) -> bool:
        return self.expire_date > timezone.now()

    @gql.field
    def is_current(self, info: Info) -> bool:
        return info.context.request.session.session_key == self.session_key  # type: ignore


@gql.django.type(models.Config)
class Config(relay.Node):
    user: "User"
    key: auto
    value: auto


@gql.type
class Image:
    @gql.field
    def name(self) -> str:
        return self.name  # type: ignore

    @gql.field
    def url(self) -> str:
        return self.url  # type: ignore


@gql.django.type(models.Avatar)
class Avatar(relay.Node):
    user: "User"
    avatar: Image
    created_at: auto


@gql.django.type(get_user_model())
class User(relay.Node):
    id: auto
    username: auto
    password: auto
    email: auto
    session: list[Session]

    @gql.django.field(select_related=["avatar"])
    def avatar_url(self) -> str | None:
        if hasattr(self, "avatar"):
            return self.avatar.avatar.url  # type: ignore

    configs: list[Config]
