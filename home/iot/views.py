import base64
import json
import logging
from datetime import datetime
from typing import cast

import pytz
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from home.utils import channel_group_send

from .models import AutowateringData, Device

logger = logging.getLogger("iot")


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
    groups = ["iot"]

    def connect(self):
        if device := self.scope["device"]:
            self.accept()
            device = cast(Device, device)
            device.is_online = True
            device.online_at = timezone.now()
            device.save()
            channel_group_send(f"device.{device.pk}", {"type": "update"})
            logger.info(f"{device.name} 在线")

    def disconnect(self, close_code):
        if device := self.scope["device"]:
            device = cast(Device, device)
            device.is_online = False
            device.offline_at = timezone.now()
            device.save()
            channel_group_send(f"device.{device.pk}", {"type": "update"})
            logger.info(f"{device.name} 离线")

    def receive(self, text_data):
        event = json.loads(text_data)
        device: Device = self.scope["device"]
        if device.device_type == "autowatering":
            autowatering_data = AutowateringData(
                device=device,
                time=datetime.fromtimestamp(event["timestamp"], pytz.utc),
                temperature=event["data"]["temperature"],
                humidity=event["data"]["humidity"],
                wifi_signal=event["data"]["wifi_signal"],
                valve1=event["data"]["valve1"],
                valve2=event["data"]["valve2"],
                valve3=event["data"]["valve3"],
                pump=event["data"]["pump"],
                valve1_delay=event["data"]["valve1_delay"],
                valve2_delay=event["data"]["valve2_delay"],
                valve3_delay=event["data"]["valve3_delay"],
                pump_delay=event["data"]["pump_delay"],
            )
            autowatering_data.save()
            channel_group_send(
                f"autowatering_data.{device.pk}",
                {"type": "update", "pk": autowatering_data.pk},
            )
            logger.debug(f"{device.name} {autowatering_data.time} 保存成功")

    def set_device(self, event):
        device_id = event["pk"]
        device: Device = self.scope["device"]
        if device.device_type == "autowatering" and device_id == device.pk:
            self.send(text_data=json.dumps(event["data"]))
