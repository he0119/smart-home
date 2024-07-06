import strawberry
import strawberry_django
from strawberry import relay

from home.users.types import User, UserFilter

from . import models


@strawberry_django.filter(model=models.MiPush, lookups=True)
class MiPushFilter:
    user: UserFilter
    model: strawberry.auto


@strawberry_django.type(models.MiPush, filters=MiPushFilter)
class MiPush(relay.Node):
    user: User
    enable: strawberry.auto
    reg_id: strawberry.auto
    device_id: strawberry.auto
    model: strawberry.auto


@strawberry.type
class MiPushKey:
    app_id: str
    app_key: str
