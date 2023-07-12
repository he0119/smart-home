from typing import Optional

import strawberry
import strawberry_django
from strawberry import relay
from strawberry_django.filters import FilterLookup

from home.users.types import User

from . import models


@strawberry_django.ordering.order(models.Item)
class ItemOrder:
    created_at: strawberry.auto
    edited_at: strawberry.auto
    expired_at: strawberry.auto
    deleted_at: strawberry.auto


@strawberry_django.ordering.order(models.Picture)
class PictureOrder:
    created_at: strawberry.auto


@strawberry.input
class StorageFilterLookup:
    id: relay.GlobalID | None = strawberry.UNSET
    name: FilterLookup[str] | None = strawberry.UNSET
    description: FilterLookup[str] | None = strawberry.UNSET
    level: FilterLookup[int] | None = strawberry.UNSET
    is_null: bool | None = strawberry.UNSET


@strawberry_django.filters.filter(model=models.Item, lookups=True)
class ItemFilter:
    name: strawberry.auto
    description: strawberry.auto
    expired_at: strawberry.auto
    # FIXME: 现在这样只能在提供了 filter 参数的情况下，才会生效（就算参数为空字典也行）。
    is_deleted: strawberry.auto = False
    """ 默认排除已删除的物品 """
    consumables: bool | None = None
    storage: StorageFilterLookup | None = strawberry.UNSET

    def filter_consumables(self, queryset):
        if self.consumables is None:
            return queryset
        if self.consumables:
            return queryset.exclude(consumables=None)
        return queryset.filter(consumables=None)


@strawberry_django.filters.filter(model=models.Storage, lookups=True)
class StorageFilter:
    name: strawberry.auto
    description: strawberry.auto
    level: strawberry.auto


@strawberry_django.filters.filter(models.Picture, lookups=True)
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
    consumables: strawberry_django.relay.ListConnectionWithTotalCount[
        "Item"
    ] = strawberry_django.connection(filters=ItemFilter, order=ItemOrder)
    pictures: strawberry_django.relay.ListConnectionWithTotalCount[
        "Picture"
    ] = strawberry_django.connection(filters=PictureFilter, order=PictureOrder)


@strawberry_django.type(models.Storage, filters=StorageFilter)
class Storage(relay.Node):
    name: strawberry.auto
    description: strawberry.auto
    parent: Optional["Storage"]
    children: strawberry_django.relay.ListConnectionWithTotalCount[
        "Storage"
    ] = strawberry_django.connection(filters=StorageFilter)
    items: strawberry_django.relay.ListConnectionWithTotalCount[
        Item
    ] = strawberry_django.connection(filters=ItemFilter, order=ItemOrder)
    ancestors: strawberry_django.relay.ListConnectionWithTotalCount[
        "Storage"
    ] = strawberry_django.connection(filters=StorageFilter)

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
