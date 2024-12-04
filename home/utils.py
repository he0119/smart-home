from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    """验证是否登录

    支持 websocket 和 http
    https://strawberry.rocks/docs/guides/permissions
    """

    message = "User is not authenticated"

    # This method can also be async!
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if isinstance(info.context, dict):
            user = info.context["request"].scope["user"]
        else:
            user = info.context.request.user
        return user.is_authenticated and user.is_active


def channel_group_send(group: str, message: dict) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group, message)  # type: ignore


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError(f"invalid truth value {val!r}")
