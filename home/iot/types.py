from collections.abc import Iterable
from typing import Any, Literal, TypedDict

import strawberry_django
from strawberry import UNSET, auto, relay
from strawberry_django.filters import apply as apply_filters
from strawberry_django.ordering import apply as apply_ordering

from . import models


class SetDeviceEvent(TypedDict):
    """设置设备事件"""

    type: Literal["set_device"]
    id: str
    data: dict[str, Any]


@strawberry_django.ordering.order(models.AutowateringData)
class AutowateringDataOrder:
    time: auto


@strawberry_django.filters.filter(model=models.AutowateringData, lookups=True)
class AutowateringDataFilter:
    time: auto
    device: "DeviceFilter |None" = UNSET


@strawberry_django.ordering.order(models.Device)
class DeviceOrder:
    created_at: auto
    edited_at: auto
    is_online: auto
    online_at: auto
    offline_at: auto


@strawberry_django.filters.filter(model=models.Device, lookups=True)
class DeviceFilter:
    id: relay.GlobalID
    name: auto
    device_type: auto
    location: auto


@strawberry_django.type(
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


@strawberry_django.type(models.Device, filters=DeviceFilter, order=DeviceOrder)
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

    # NOTE: 临时的解决方法
    # https://github.com/blb-ventures/strawberry-django-plus/issues/245
    @strawberry_django.connection(
        strawberry_django.relay.ListConnectionWithTotalCount[AutowateringData],
        filters=AutowateringDataFilter,
        order=AutowateringDataOrder,
    )
    def autowatering_data(
        self,
        info,
        filters: AutowateringDataFilter | None = UNSET,
        order: AutowateringDataOrder | None = UNSET,
    ) -> Iterable[models.AutowateringData]:
        qs = models.AutowateringData.objects.all()
        if filters is not UNSET:
            qs = apply_filters(filters, qs, info=info)
        if order is not UNSET:
            qs = apply_ordering(order, qs)  # type: ignore
        return qs
