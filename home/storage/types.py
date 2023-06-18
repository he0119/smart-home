from typing import Optional

from strawberry import auto, relay
from strawberry_django.filters import FilterLookup
from strawberry_django_plus import gql

from home.users.types import User

from . import models


@gql.django.ordering.order(models.Item)
class ItemOrder:
    created_at: auto
    edited_at: auto
    expired_at: auto
    deleted_at: auto


@gql.django.ordering.order(models.Picture)
class PictureOrder:
    created_at: auto


@gql.input
class StorageFilterLookup:
    id: relay.GlobalID | None = gql.UNSET
    name: FilterLookup[str] | None = gql.UNSET
    description: FilterLookup[str] | None = gql.UNSET
    level: FilterLookup[int] | None = gql.UNSET
    is_null: bool | None = gql.UNSET


@gql.django.filters.filter(model=models.Item, lookups=True)
class ItemFilter:
    name: auto
    storage: StorageFilterLookup
    description: auto
    expired_at: auto
    # FIXME: 现在这样只能在提供了 filter 参数的情况下，才会生效（就算参数为空字典也行）。
    is_deleted: auto = False
    """ 默认排除已删除的物品 """
    consumables: bool

    def filter_consumables(self, queryset):
        if self.consumables is None:
            return queryset
        if self.consumables:
            return queryset.exclude(consumables=None)
        return queryset.filter(consumables=None)


@gql.django.filters.filter(model=models.Storage, lookups=True)
class StorageFilter:
    name: auto
    description: auto
    level: auto


@gql.django.filters.filter(models.Picture, lookups=True)
class PictureFilter:
    id: auto
    item: ItemFilter
    description: auto


@gql.django.type(models.Item, filters=ItemFilter, order=ItemOrder)
class Item(relay.Node):
    name: auto
    number: auto
    description: auto
    price: auto
    expired_at: auto
    storage: "Storage | None"
    created_at: auto
    created_by: User
    edited_at: auto
    edited_by: User
    is_deleted: auto
    deleted_at: auto
    consumables: gql.django.ListConnectionWithTotalCount[
        "Item"
    ] = gql.django.connection(filters=ItemFilter, order=ItemOrder)
    pictures: gql.django.ListConnectionWithTotalCount[
        "Picture"
    ] = gql.django.connection(filters=PictureFilter, order=PictureOrder)


@gql.django.type(models.Storage, filters=StorageFilter)
class Storage(relay.Node):
    name: auto
    description: auto
    parent: Optional["Storage"]
    children: gql.django.ListConnectionWithTotalCount[
        "Storage"
    ] = gql.django.connection(filters=StorageFilter)
    items: gql.django.ListConnectionWithTotalCount[Item] = gql.django.connection(
        filters=ItemFilter, order=ItemOrder
    )
    ancestors: gql.django.ListConnectionWithTotalCount[
        "Storage"
    ] = gql.django.connection(filters=StorageFilter)

    # NOTE: 如果是像下面这样写就会报错
    # AttributeError: 'str' object has no attribute 'CONNECTION_CLASS'
    # @gql.django.connection
    # def ancestors(self, info) -> list["Storage"]:
    #     return self.get_ancestors()


@gql.django.type(models.Picture, filters=PictureFilter, order=PictureOrder)
class Picture(relay.Node):
    description: auto
    item: Item
    created_at: auto
    created_by: User
    box_x: auto
    box_y: auto
    box_h: auto
    box_w: auto

    @gql.field
    def name(self, info) -> str:
        return self.picture.name.split("/")[-1]  # type: ignore

    @gql.field
    def url(self, info) -> str:
        return self.picture.url  # type: ignore
