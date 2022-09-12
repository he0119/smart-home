import hashlib
from distutils.util import strtobool
from typing import Optional

from django.core.exceptions import ValidationError
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay
from strawberry_django_plus.permissions import IsAuthenticated

from . import models, types
from .models import Device
from .tasks import set_status


@gql.type
class Query:
    device: types.Device = gql.django.node(directives=[IsAuthenticated()])
    devices: relay.Connection[types.Device] = gql.django.connection(
        directives=[IsAuthenticated()]
    )
    autowatering_data: relay.Connection[types.AutowateringData] = gql.django.connection(
        directives=[IsAuthenticated()]
    )


def sha256(s: str) -> str:
    m = hashlib.sha256()
    m.update(s.encode("utf8"))
    return m.hexdigest()


@gql.type
class Mutation:
    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def add_device(
        self,
        info: Info,
        name: str,
        device_type: str,
        location: str,
        password: str,
    ) -> types.Device:
        device = Device(
            name=name,
            device_type=device_type,
            location=location,
            is_online=False,
            password=sha256(password),
        )
        device.save()

        return device  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def update_device(
        self,
        info: Info,
        id: relay.GlobalID,
        name: Optional[str],
        device_type: Optional[str],
        location: Optional[str],
        password: Optional[str],
    ) -> types.Device:
        device: models.Device = id.resolve_node(info)  # type: ignore

        if not device:
            raise ValidationError("设备不存在")

        # 仅在传入数据时修改
        if name is not None:
            device.name = name
        if device_type is not None:
            device.device_type = device_type
        if location is not None:
            device.location = location
        if password is not None:
            device.password = sha256(password)

        device.save()

        return device  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def delete_device(self, info: Info, device_id: relay.GlobalID) -> types.Device:
        device: models.Device = device_id.resolve_node(info)  # type: ignore

        if not device:
            raise ValidationError("设备不存在")

        device.delete()

        return device  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def set_device(
        self,
        info: Info,
        id: relay.GlobalID,
        key: str,
        value: str,
        value_type: str,
    ) -> types.Device:
        device: models.Device = id.resolve_node(info)  # type: ignore

        if not device:
            raise ValidationError("设备不存在")

        # 转换 value 的类型
        if value_type == "bool":
            value = strtobool(value)  # type: ignore
        elif value_type == "float":
            value = float(value)  # type: ignore
        elif value_type == "int":
            value = int(value)  # type: ignore
        elif value_type == "str":
            pass

        set_status.delay(device.name, key, value)

        return device  # type: ignore
