import base64
import logging
from typing import Any, TypedDict, cast

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
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


class CommandContent(TypedDict):
    id: str
    method: str
    params: dict[str, Any]


class IotConsumer(AsyncJsonWebsocketConsumer):
    groups = ["iot"]

    # FIXME: 有时候会出现之前的连接，在重连之后才断开的情况
    # 从而导致设备状态不正确
    # WebSocket HANDSHAKING /api/iot/ [127.0.0.1:46468]
    # WebSocket CONNECT /api/iot/ [127.0.0.1:46468]
    # 2022-10-02 11:46:11 CST - iot - INFO - test 在线
    # WebSocket DISCONNECT /api/iot/ [127.0.0.1:57946]
    # 2022-10-02 11:46:47 CST - iot - INFO - test 离线
    # 注意两个的端口不一致，说明是两次连接
    async def connect(self):
        if device := self.scope["device"]:
            await self.accept()
            device = cast(Device, device)
            device.is_online = True
            device.online_at = timezone.now()
            await sync_to_async(device.save)(update_fields=["is_online", "offline_at"])
            await self.channel_layer.group_send(f"device.{device.pk}", {"type": "update"})  # type: ignore
            logger.info(f"{device.name} 在线")
        else:
            await self.close(3000)

    async def disconnect(self, close_code):
        if device := self.scope["device"]:
            device = cast(Device, device)
            device.is_online = False
            device.offline_at = timezone.now()
            await sync_to_async(device.save)(update_fields=["is_online", "offline_at"])
            await self.channel_layer.group_send(f"device.{device.pk}", {"type": "update"})  # type: ignore
            logger.info(f"{device.name} 离线")

    async def receive_json(self, content: CommandContent):
        device: Device = self.scope["device"]

        method = content["method"]
        if method == "properties_changed":
            data = content["params"]
            autowatering_data = AutowateringData(
                device=device,
                time=timezone.now(),
                temperature=data["temperature"],
                humidity=data["humidity"],
                wifi_signal=data["wifi_signal"],
                valve1=data["valve1"],
                valve2=data["valve2"],
                valve3=data["valve3"],
                pump=data["pump"],
                valve1_delay=data["valve1_delay"],
                valve2_delay=data["valve2_delay"],
                valve3_delay=data["valve3_delay"],
                pump_delay=data["pump_delay"],
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
            await self.send_json(
                {
                    "id": str(timezone.now().timestamp()),
                    "method": "set_properties",
                    "params": event["data"],
                }
            )
