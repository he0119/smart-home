import base64
import logging
from typing import Any, TypedDict, cast

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import AutowateringData, Device
from .types import SetDeviceEvent

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
                except Exception:
                    pass

                break

        return await self.app(scope, receive, send)


class CommandContent(TypedDict):
    id: str
    method: str
    params: dict[str, Any]


class IotConsumer(AsyncJsonWebsocketConsumer):
    groups = ["iot"]

    async def _set_device_online(self, device: Device):
        """设置设备在线"""
        device.is_online = True
        device.online_at = timezone.now()
        await sync_to_async(device.save)(update_fields=["is_online", "online_at"])
        await self.channel_layer.group_send(  # type: ignore
            f"device.{device.id}", {"type": "update"}
        )
        logger.info(f"{device.name} 在线")

    async def connect(self):
        if device := self.scope["device"]:
            await self.accept()
            await self._set_device_online(device)
        else:
            await self.close(3000)

    async def disconnect(self, close_code):
        if device := self.scope["device"]:
            device = cast("Device", device)
            await sync_to_async(device.refresh_from_db)()
            device.is_online = False
            device.offline_at = timezone.now()
            # 第一次连接建立
            # [2022-10-22 10:48:11 +0800] [10] [INFO] ('172.20.0.7', 60862) - "WebSocket /api/iot/" [accepted]
            # [2022-10-22 10:48:11 +0800] [10] [INFO] connection open
            # 然后设备离线，重连，第二次连接建立
            # [2022-10-22 10:48:27 +0800] [10] [INFO] ('172.20.0.7', 50890) - "WebSocket /api/iot/" [accepted]
            # [2022-10-22 10:48:27 +0800] [10] [INFO] connection open
            # 第一次连接超时关闭
            # [2022-10-22 10:48:30 +0800] [10] [INFO] connection closed
            # 如果设备离线，会自动重连，但是会新建一个连接，但是旧的连接此时还没有超时关闭
            # 当在线时间与离线时间的差值小于 20 秒（当前 WebSocket 的超时时间）时，则不修改状态。
            # 因为此时的离线事件是上一次的连接，而不是当前连接
            if device.online_at and (device.offline_at - device.online_at) < timezone.timedelta(seconds=20):
                return

            await sync_to_async(device.save)(update_fields=["is_online", "offline_at"])
            await self.channel_layer.group_send(  # type: ignore
                f"device.{device.id}", {"type": "update"}
            )
            logger.info(f"{device.name} 离线")

    async def receive_json(self, content: CommandContent):
        device: Device = self.scope["device"]

        # 如果接收到数据时设备记录的状态不是在线则将其设置为在线
        # 不知道为什么有时候状态还是不同步
        if not device.is_online:
            await self._set_device_online(device)

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
                f"autowatering_data.{device.id}",
                {"type": "update", "pk": autowatering_data.id},
            )
            logger.debug(f"{device.name} {autowatering_data.time} 保存成功")

    async def set_device(self, event: SetDeviceEvent):
        device_id = event["id"]
        device: Device = self.scope["device"]
        if device.device_type == "autowatering" and device_id == str(device.id):
            await self.send_json(
                {
                    "id": str(timezone.now().timestamp()),
                    "method": "set_properties",
                    "params": event["data"],
                }
            )
