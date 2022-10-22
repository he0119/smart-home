from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

from .mipush.APIMessage import *
from .mipush.APISender import APISender

sender = APISender(settings.MI_PUSH_APP_SECRET)


def get_enable_reg_ids() -> list[str]:
    """获取所有启用的设备标识码"""
    users = get_user_model().objects.exclude(mipush__enable=False)
    return [mipush.reg_id for user in users for mipush in user.mipush.all()]  # type: ignore


def get_enable_reg_ids_except_user(user) -> list[str]:
    """获取除指定用户的所有启用的设备标识码"""
    users = get_user_model().objects.exclude(pk=user.id).exclude(mipush__enable=False)
    return [mipush.reg_id for user in users for mipush in user.mipush.all()]  # type: ignore


def build_message(
    title: str,
    description: str,
    payload: str,
    is_important: bool,
) -> PushMessage:
    """生成推送消息

    使用多文字模式，最多支持 128 字。
    <https://dev.mi.com/console/doc/detail?pId=1278#_3_3>
    """
    # 去掉过多的字符
    description = description[:128]

    # 每条内容相同的消息单独显示，不覆盖
    # 限制最多可以有 10001 条消息共存
    notify_id = abs(hash(title + description)) % (10**4)

    message = (
        PushMessage()
        .restricted_package_name(settings.MI_PUSH_PACKAGE_NAME)
        .title(title)
        .description(description)
        .payload(payload)
        .notify_id(notify_id)
        .extra({"notification_style_type": "1"})
    )

    # 重要通知
    if is_important:
        message = message.extra({Constants.extra_param_channel_id: "high_system"})
        message = message.extra({Constants.extra_param_channel_name: "服务提醒"})

    return message


@shared_task(max_retries=3, default_retry_delay=5)
def push_to_users(
    reg_ids: list[str],
    title: str,
    description: str,
    payload: str,
    is_important: bool = False,
):
    """向用户推送消息

    支持向一个或多个用户推送消息

    根据 regids, 发送消息到指定的一组设备上, regids 的个数不得超过 1000 个。
    <https://dev.mi.com/console/doc/detail?pId=1278#_2_1>
    """
    if settings.MI_PUSH_APP_SECRET:
        message = build_message(title, description, payload, is_important)
        return sender.send(message.message_dict(), ",".join(reg_ids))
    return "未设置 MI_PUSH_APP_SECRET，不推送"
