from typing import Optional

import strawberry
import strawberry_django
from django.db.models import Q
from strawberry import relay
from strawberry_django import FilterLookup

from home.users.types import User

from . import models


@strawberry_django.order(models.Item)
class ItemOrder:
    created_at: strawberry.auto
    edited_at: strawberry.auto
    expired_at: strawberry.auto
    deleted_at: strawberry.auto


@strawberry_django.order(models.Picture)
class PictureOrder:
    created_at: strawberry.auto


@strawberry.input
class StorageFilterLookup:
    id: relay.GlobalID | None = strawberry.UNSET
    name: FilterLookup[str] | None = strawberry.UNSET
    description: FilterLookup[str] | None = strawberry.UNSET
    level: FilterLookup[int] | None = strawberry.UNSET
    is_null: bool | None = strawberry.UNSET


@strawberry_django.filter(model=models.Item, lookups=True)
class ItemFilter:
    name: strawberry.auto
    description: strawberry.auto
    expired_at: strawberry.auto
    # FIXME: 现在这样只能在提供了 filter 参数的情况下，才会生效（就算参数为空字典也行）。
    is_deleted: bool = False
    """ 默认排除已删除的物品 """
    storage: StorageFilterLookup | None = strawberry.UNSET

    @strawberry_django.filter_field(filter_none=True)
    def consumables(self, value: bool | None, prefix: str) -> Q:
        if value is None:
            return Q()
        if value:
            return Q(consumables__isnull=False)
        return Q(consumables__isnull=True)


@strawberry_django.filter(model=models.Storage, lookups=True)
class StorageFilter:
    name: strawberry.auto
    description: strawberry.auto
    level: strawberry.auto


@strawberry_django.filter(models.Picture, lookups=True)
class PictureFilter:
    id: strawberry.auto
    description: strawberry.auto
    item: ItemFilter | None = strawberry.UNSET


@strawberry_django.type(models.Item, filters=ItemFilter, order=ItemOrder)
class Item(relay.Node):
    name: strawberry.auto
    number: strawberry.auto
    description: strawberry.auto
    price: strawberry.auto
    expired_at: strawberry.auto
    storage: "Storage | None"
    created_at: strawberry.auto
    created_by: User
    edited_at: strawberry.auto
    edited_by: User
    is_deleted: strawberry.auto
    deleted_at: strawberry.auto
    consumables: strawberry_django.relay.DjangoListConnection["Item"] = (
        strawberry_django.connection(filters=ItemFilter, order=ItemOrder)
    )
    pictures: strawberry_django.relay.DjangoListConnection["Picture"] = (
        strawberry_django.connection(filters=PictureFilter, order=PictureOrder)
    )


@strawberry_django.type(models.Storage, filters=StorageFilter)
class Storage(relay.Node):
    name: strawberry.auto
    description: strawberry.auto
    parent: Optional["Storage"]
    children: strawberry_django.relay.DjangoListConnection["Storage"] = (
        strawberry_django.connection(filters=StorageFilter)
    )
    items: strawberry_django.relay.DjangoListConnection[Item] = (
        strawberry_django.connection(filters=ItemFilter, order=ItemOrder)
    )
    ancestors: strawberry_django.relay.DjangoListConnection["Storage"] = (
        strawberry_django.connection(filters=StorageFilter)
    )

    # NOTE: 如果是像下面这样写就会报错
    # AttributeError: 'str' object has no attribute 'CONNECTION_CLASS'
    # @strawberry_django.connection
    # def ancestors(self, info) -> list["Storage"]:
    #     return self.get_ancestors()


@strawberry_django.type(models.Picture, filters=PictureFilter, order=PictureOrder)
class Picture(relay.Node):
    description: strawberry.auto
    item: Item
    created_at: strawberry.auto
    created_by: User
    box_x: strawberry.auto
    box_y: strawberry.auto
    box_h: strawberry.auto
    box_w: strawberry.auto

    @strawberry.field
    def name(self, info) -> str:
        return self.picture.name.split("/")[-1]  # type: ignore

    @strawberry.field
    def url(self, info) -> str:
        return self.picture.url  # type: ignore
