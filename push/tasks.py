from typing import List
from celery import shared_task
from django.conf import settings

from .mipush.APIMessage import *
from .mipush.APISender import APISender

sender = APISender(settings.MI_PUSH_APP_SECRET)


def build_message(title: str, description: str) -> PushMessage:
    # 每条内容相同的消息单独显示，不覆盖
    notify_id = abs(hash(title + description)) % (10**8)
    return PushMessage() \
        .restricted_package_name(settings.MI_PUSH_PACKAGE_NAME) \
        .title(title).description(description) \
        .pass_through(0) \
        .notify_id(notify_id) \
        .extra({Constants.extra_param_notify_effect: Constants.notify_launcher_activity})


@shared_task(max_retries=3, default_retry_delay=5)
def push_to_user(username: str, title: str, description: str) -> None:
    """ 向指定用户推送消息 """
    message = build_message(title, description)
    return sender.send_to_alias(message.message_dict(), username)


@shared_task(max_retries=3, default_retry_delay=5)
def push_to_users(usernames: List[str], title: str, description: str) -> None:
    """ 向多位用户推送消息 """
    message = build_message(title, description)
    return sender.send_to_alias(message.message_dict(), usernames)


@shared_task(max_retries=3, default_retry_delay=5)
def push_to_all(title: str, description: str) -> None:
    """ 向所有用户推送消息 """
    message = build_message(title, description)
    return sender.broadcast_all(message.message_dict())
