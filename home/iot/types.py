from typing import Any, Literal, TypedDict

from strawberry import auto, relay
from strawberry_django_plus import gql

from . import models


class SetDeviceEvent(TypedDict):
    """设置设备事件"""

    type: Literal["set_device"]
    id: str
    data: dict[str, Any]


@gql.django.ordering.order(models.AutowateringData)
class AutowateringDataOrder:
    time: auto


@gql.django.filters.filter(model=models.AutowateringData, lookups=True)
class AutowateringDataFilter:
    device: "DeviceFilter"
    time: auto


@gql.django.ordering.order(models.Device)
class DeviceOrder:
    created_at: auto
    edited_at: auto
    is_online: auto
    online_at: auto
    offline_at: auto


@gql.django.filters.filter(model=models.Device, lookups=True)
class DeviceFilter:
    id: relay.GlobalID
    name: auto
    device_type: auto
    location: auto


@gql.django.type(
    models.AutowateringData, filters=AutowateringDataFilter, order=AutowateringDataOrder
)
class AutowateringData(relay.Node):
    device: "Device"
    time: auto
    temperature: auto
    humidity: auto
    wifi_signal: auto
    valve1: auto
    valve2: auto
    valve3: auto
    pump: auto
    valve1_delay: auto
    valve2_delay: auto
    valve3_delay: auto
    pump_delay: auto


@gql.django.type(models.Device, filters=DeviceFilter, order=DeviceOrder)
class Device(relay.Node):
    name: auto
    device_type: auto
    location: auto
    created_at: auto
    edited_at: auto
    is_online: auto
    online_at: auto
    offline_at: auto
    token: auto

    @gql.django.connection(filters=AutowateringDataFilter, order=AutowateringDataOrder)
    def autowatering_data(self, info) -> relay.Connection[AutowateringData]:
        return models.AutowateringData.objects.all()  # type: ignore
