from enum import Enum
from typing import List, Optional

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

from .mipush.APIMessage import *
from .mipush.APISender import APISender

sender = APISender(settings.MI_PUSH_APP_SECRET)


class PushChannel(Enum):
    """ 通知类别 """
    IOT = ['pre54', 'IoT消息'],
    STORAGE = ['pre213', '物品管理信息'],
    BOARD = ['pre84', '留言板消息'],


def get_enable_reg_ids() -> List[str]:
    """ 获取所有启用的设备标识码 """
    users = get_user_model().objects.exclude(mipush__enable=False)
    return [user.mipush.reg_id for user in users if hasattr(user, 'mipush')]


def get_enable_reg_ids_except_user(user) -> List[str]:
    """ 获取除指定用户的所有启用的设备标识码 """
    users = get_user_model().objects.exclude(pk=user.id).exclude(
        mipush__enable=False)
    return [user.mipush.reg_id for user in users if hasattr(user, 'mipush')]


def build_message(title: str, description: str,
                  channel: Optional[List]) -> PushMessage:
    # 每条内容相同的消息单独显示，不覆盖
    # 限制最多可以有 10001 条消息共存
    notify_id = abs(hash(title + description)) % (10**4)

    message = PushMessage() \
        .restricted_package_name(settings.MI_PUSH_PACKAGE_NAME) \
        .title(title).description(description) \
        .notify_id(notify_id) \
        .extra({Constants.extra_param_notify_effect: Constants.notify_launcher_activity}) \
        .extra({'notification_style_type': '1'})

    # 通知类别
    if channel:
        message = message.extra({Constants.extra_param_channel_id: channel[0]})
        message = message.extra(
            {Constants.extra_param_channel_name: channel[1]})

    return message


@shared_task(max_retries=3, default_retry_delay=5)
def push_to_users(reg_ids: List[str],
                  title: str,
                  description: str,
                  channel: Optional[List] = None):
    """ 向用户推送消息

    支持向一个或多个用户推送消息

    根据 regids, 发送消息到指定的一组设备上, regids 的个数不得超过 1000 个。
    <https://dev.mi.com/console/doc/detail?pId=1278#_2_1>
    """
    message = build_message(title, description, channel)
    return sender.send(message.message_dict(), reg_ids)
