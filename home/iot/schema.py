from distutils.util import strtobool
from enum import Enum
from typing import AsyncGenerator, Optional

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay

from home.utils import IsAuthenticated, channel_group_send

from . import models, types
from .api import DeviceAPI
from .models import AutowateringData, Device


@gql.type
class Query:
    device: types.Device = gql.django.node(permission_classes=[IsAuthenticated])
    devices: relay.Connection[types.Device] = gql.django.connection(
        permission_classes=[IsAuthenticated]
    )
    autowatering_data: relay.Connection[types.AutowateringData] = gql.django.connection(
        permission_classes=[IsAuthenticated]
    )


@gql.enum
class ValueType(Enum):
    BOOLEAN = "boolean"
    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"


@gql.type
class Mutation:
    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def add_device(
        self,
        info: Info,
        name: str,
        device_type: str,
        location: str,
    ) -> types.Device:
        device = Device(
            name=name,
            device_type=device_type,
            location=location,
            is_online=False,
        )
        device.generate_token()
        device.save()

        return device  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def update_device(
        self,
        info: Info,
        id: relay.GlobalID,
        name: Optional[str],
        device_type: Optional[str],
        location: Optional[str],
    ) -> types.Device:
        try:
            device = id.resolve_node(info, ensure_type=models.Device)
        except:
            raise ValidationError("设备不存在")

        # 仅在传入数据时修改
        if name is not None:
            device.name = name
        if device_type is not None:
            device.device_type = device_type
        if location is not None:
            device.location = location

        device.save()
        channel_group_send(f"device.{device.id}", {"type": "update"})

        return device  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_device(self, info: Info, device_id: relay.GlobalID) -> types.Device:
        try:
            device = device_id.resolve_node(info, ensure_type=models.Device)
        except:
            raise ValidationError("设备不存在")

        device.delete()

        return device  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def set_device(
        self,
        info: Info,
        id: relay.GlobalID,
        key: str,
        value: str,
        value_type: ValueType,
    ) -> types.Device:
        try:
            device = id.resolve_node(info, ensure_type=models.Device)
        except:
            raise ValidationError("设备不存在")

        # 转换 value 的类型
        if value_type == ValueType.BOOLEAN:
            value = strtobool(value)  # type: ignore
        elif value_type == ValueType.FLOAT:
            value = float(value)  # type: ignore
        elif value_type == ValueType.INTEGER:
            value = int(value)  # type: ignore

        device_api = DeviceAPI(str(device.id))
        device_api.set_status(key, value)

        return device  # type: ignore


@gql.type
class Subscription:
    @gql.subscription(permission_classes=[IsAuthenticated])
    async def autowatering_data(
        self,
        info: Info,
        device_id: relay.GlobalID,
    ) -> AsyncGenerator[types.AutowateringData, None]:
        ws = info.context.ws

        # 发送最新的数据
        # 让客户端可以马上显示数据
        try:
            device = device_id.resolve_node(info, ensure_type=models.Device)
        except:
            raise ValidationError("设备不存在")

        last = await sync_to_async(device.data.last)()  # type: ignore
        if last:
            yield last

        async for message in ws.channel_listen(
            "update", groups=[f"autowatering_data.{device.id}"]
        ):
            data = await sync_to_async(AutowateringData.objects.get)(pk=message["pk"])
            yield data

    @gql.subscription(permission_classes=[IsAuthenticated])
    async def device(
        self,
        info: Info,
        id: relay.GlobalID,
    ) -> AsyncGenerator[types.Device, None]:
        ws = info.context.ws

        device: models.Device = await id.resolve_node(info)  # type: ignore
        if not device:
            raise ValidationError("设备不存在")

        yield device  # type: ignore

        async for message in ws.channel_listen(
            "update", groups=[f"device.{device.id}"]
        ):
            device = await sync_to_async(Device.objects.get)(pk=device.id)
            yield device  # type: ignore
