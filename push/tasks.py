from typing import List
from celery import shared_task
from django.conf import settings

from .mipush.APIMessage import *
from .mipush.APISender import APISender

sender = APISender(settings.MI_PUSH_APP_SECRET)


def build_message(title: str, description: str) -> PushMessage:
    return PushMessage() \
        .restricted_package_name(settings.MI_PUSH_PACKAGE_NAME) \
        .title(title).description(description) \
        .pass_through(0)


@shared_task
def push_to_user(username: str, title: str, description: str) -> None:
    """ 向指定用户推送消息 """
    message = build_message(title, description)
    sender.send_to_alias(message, username)


@shared_task
def push_to_users(usernames: List[str], title: str, description: str) -> None:
    """ 向多位用户推送消息 """
    message = build_message(title, description)
    sender.send_to_alias(message, usernames)


@shared_task
def push_to_all(title: str, description: str) -> None:
    """ 向所有用户推送消息 """
    message = build_message(title, description)
    sender.broadcast_all(message)
