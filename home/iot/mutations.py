import hashlib
from distutils.util import strtobool

import graphene
from graphene import relay
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import Device
from .tasks import set_status
from .types import DeviceType


def sha256(s: str) -> str:
    m = hashlib.sha256()
    m.update(s.encode("utf8"))
    return m.hexdigest()


class AddDeviceMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        device_type = graphene.String(required=True)
        location = graphene.String(required=True)
        password = graphene.String(required=True)

    device = graphene.Field(DeviceType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        name = input.get("name")
        device_type = input.get("device_type")
        location = input.get("location")
        password = input.get("password")

        device = Device(
            name=name,
            device_type=device_type,
            location=location,
            is_online=False,
            password=sha256(password),
        )
        device.save()
        return AddDeviceMutation(device=device)


class DeleteDeviceMutation(relay.ClientIDMutation):
    class Input:
        device_id = graphene.ID(required=True, description="设备的 ID")

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, device_id = from_global_id(input.get("device_id"))

        try:
            device = Device.objects.get(pk=device_id)
            device.delete()
            return DeleteDeviceMutation()
        except Device.DoesNotExist:
            raise GraphQLError("设备不存在")


class UpdateDeviceMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        device_type = graphene.String()
        location = graphene.String()
        password = graphene.String()

    device = graphene.Field(DeviceType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, device_id = from_global_id(input.get("id"))
        name = input.get("name")
        device_type = input.get("device_type")
        location = input.get("location")
        password = input.get("password")

        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            raise GraphQLError("设备不存在")

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
        return UpdateDeviceMutation(device=device)


class SetDeviceMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        value = graphene.String(required=True)
        value_type = graphene.String(
            required=True, description="支持 bool, float, int, str 类型"
        )

    device = graphene.Field(DeviceType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, device_id = from_global_id(input.get("id"))
        key = input.get("key")
        value = input.get("value")
        value_type = input.get("value_type")

        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            raise GraphQLError("设备不存在")

        # 转换 value 的类型
        if value_type == "bool":
            value = strtobool(value)
        elif value_type == "float":
            value = float(value)
        elif value_type == "int":
            value = int(value)
        elif value_type == "str":
            pass

        set_status.delay(device.name, key, value)

        return SetDeviceMutation(device=device)
