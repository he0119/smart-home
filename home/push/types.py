from strawberry import auto, relay
from strawberry_django_plus import gql

from home.users.types import User, UserFilter

from . import models


@gql.django.filters.filter(model=models.MiPush, lookups=True)
class MiPushFilter:
    user: UserFilter
    model: auto


@gql.django.type(models.MiPush, filters=MiPushFilter)
class MiPush(relay.Node):
    user: User
    enable: auto
    reg_id: auto
    device_id: auto
    model: auto


@gql.type
class MiPushKey:
    app_id: str
    app_key: str
