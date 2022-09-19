import json
import logging
from datetime import datetime

import pytz
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from home.utils import channel_group_send

from .models import AutowateringData, Device

logger = logging.getLogger("iot")


@csrf_exempt
def iot(request):
    """物联网

    EMQX WebHook
    """
    if request.method == "POST":
        event = json.loads(request.body)
        logger.debug(event)
        if event["action"] == "message_publish":
            process_message_publish(event)
        elif event["action"] == "client_connected":
            process_client_connected(event)
        elif event["action"] == "client_disconnected":
            process_client_disconnected(event)
        else:
            logger.warning("未处理的事件")
            logger.warning(event)

    return JsonResponse({"iot": "working"})


def process_message_publish(event):
    """处理消息发布事件"""
    device_name = event["from_username"]
    topic = event["topic"]
    if "status" in topic:
        payload = json.loads(event["payload"])
        try:
            device: Device = Device.objects.get(name=device_name)
            if device.device_type == "autowatering":
                autowatering_data = AutowateringData(
                    device=device,
                    time=datetime.fromtimestamp(payload["timestamp"], pytz.utc),
                    temperature=payload["data"]["temperature"],
                    humidity=payload["data"]["humidity"],
                    wifi_signal=payload["data"]["wifi_signal"],
                    valve1=payload["data"]["valve1"],
                    valve2=payload["data"]["valve2"],
                    valve3=payload["data"]["valve3"],
                    pump=payload["data"]["pump"],
                    valve1_delay=payload["data"]["valve1_delay"],
                    valve2_delay=payload["data"]["valve2_delay"],
                    valve3_delay=payload["data"]["valve3_delay"],
                    pump_delay=payload["data"]["pump_delay"],
                )
                autowatering_data.save()
                channel_group_send(
                    f"autowatering_data.{device.pk}",
                    {"type": "update", "pk": autowatering_data.pk},
                )
                logger.debug(f"{device.name} {autowatering_data.time} 保存成功")
        except Device.DoesNotExist:
            logger.error(f"设备({device_name}) 不存在")


def process_client_disconnected(event):
    """处理设备下线事件"""
    device_name = event["username"]
    try:
        device: Device = Device.objects.get(name=device_name)
        device.is_online = False
        device.offline_at = timezone.now()
        device.save()
        channel_group_send(f"device.{device.pk}", {"type": "update"})
        logger.info(f"{device.name} 离线")
    except Device.DoesNotExist:
        logger.error(f"设备({device_name}) 不存在")


def process_client_connected(event):
    """处理设备上线事件"""
    device_name = event["username"]
    try:
        device: Device = Device.objects.get(name=device_name)
        device.is_online = True
        device.online_at = timezone.now()
        device.save()
        channel_group_send(f"device.{device.pk}", {"type": "update"})
        logger.info(f"{device.name} 在线")
    except Device.DoesNotExist:
        logger.error(f"设备({device_name}) 不存在")


import base64

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer


@database_sync_to_async
def get_device(username: str, password: str):
    """获取设备"""
    try:
        device: Device = Device.objects.get(id=username)
        if device.password == password:
            return device
    except Device.DoesNotExist:
        return


class BasicAuthMiddleware:
    """Basic Authorization

    给物联网设备认证用
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        for header in scope["headers"]:
            if header[0] == b"authorization":
                split = header[1].decode().strip().split(" ")
                if len(split) == 2 or split[0].strip().lower() == "basic":
                    username, password = (
                        base64.b64decode(split[1]).decode().split(":", 1)
                    )
                    scope["device"] = await get_device(username, password)
                else:
                    scope["device"] = None

                break

        return await self.app(scope, receive, send)


class IotConsumer(WebsocketConsumer):
    def connect(self):
        if device := self.scope["device"]:
            self.accept()
            device.is_online = True
            device.online_at = timezone.now()
            device.save()
            channel_group_send(f"device.{device.pk}", {"type": "update"})
            logger.info(f"{device.name} 在线")

    def disconnect(self, close_code):
        if device := self.scope["device"]:
            device.is_online = False
            device.offline_at = timezone.now()
            device.save()
            channel_group_send(f"device.{device.pk}", {"type": "update"})
            logger.info(f"{device.name} 离线")

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
