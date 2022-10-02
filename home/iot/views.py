import base64
import json
import logging
from datetime import datetime
from typing import cast

import pytz
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import AutowateringData, Device

logger = logging.getLogger("iot")


async def get_device(device_id: str, token: str) -> Device | None:
    """获取设备"""
    try:
        device: Device = await sync_to_async(Device.objects.get)(pk=device_id)
        if device.token == token:
            return device
    except Device.DoesNotExist:
        return


class BasicAuthMiddleware:
    """Basic Authorization

    给物联网设备认证用
    https://channels.readthedocs.io/en/stable/topics/authentication.html#custom-authentication
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["device"] = None

        for header in scope["headers"]:
            if header[0] == b"authorization":
                try:
                    split = header[1].decode().strip().split(" ")
                    device_id, token = base64.b64decode(split[1]).decode().split(":", 1)
                    scope["device"] = await get_device(device_id, token)
                except:
                    pass

                break

        return await self.app(scope, receive, send)


class IotConsumer(AsyncWebsocketConsumer):
    groups = ["iot"]

    async def connect(self):
        if device := self.scope["device"]:
            await self.accept()
            device = cast(Device, device)
            device.is_online = True
            device.online_at = timezone.now()
            await sync_to_async(device.save)(update_fields=["is_online", "offline_at"])
            await self.channel_layer.group_send(f"device.{device.pk}", {"type": "update"})  # type: ignore
            logger.info(f"{device.name} 在线")

    async def disconnect(self, close_code):
        if device := self.scope["device"]:
            device = cast(Device, device)
            device.is_online = False
            device.offline_at = timezone.now()
            await sync_to_async(device.save)(update_fields=["is_online", "offline_at"])
            await self.channel_layer.group_send(f"device.{device.pk}", {"type": "update"})  # type: ignore
            logger.info(f"{device.name} 离线")

    async def receive(self, text_data):
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
            await sync_to_async(autowatering_data.save)()
            await self.channel_layer.group_send(  # type: ignore
                f"autowatering_data.{device.pk}",
                {"type": "update", "pk": autowatering_data.pk},
            )
            logger.debug(f"{device.name} {autowatering_data.time} 保存成功")

    async def set_device(self, event):
        device_id = event["pk"]
        device: Device = self.scope["device"]
        if device.device_type == "autowatering" and device_id == device.pk:
            await self.send(text_data=json.dumps(event["data"]))
