from datetime import datetime

import strawberry
import strawberry_django
from django.core.exceptions import ValidationError
from django.utils import timezone
from strawberry import relay
from strawberry.file_uploads import Upload
from strawberry.types import Info

from home.utils import IsAuthenticated

from . import models, types


@strawberry.type
class Query:
    item: types.Item = strawberry_django.node(permission_classes=[IsAuthenticated])
    items: strawberry_django.relay.DjangoListConnection[types.Item] = strawberry_django.connection(
        permission_classes=[IsAuthenticated]
    )
    storage: types.Storage = strawberry_django.node(permission_classes=[IsAuthenticated])
    storages: strawberry_django.relay.DjangoListConnection[types.Storage] = strawberry_django.connection(
        permission_classes=[IsAuthenticated]
    )
    picture: types.Picture = strawberry_django.node(permission_classes=[IsAuthenticated])
    pictures: strawberry_django.relay.DjangoListConnection[types.Picture] = strawberry_django.connection(
        permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def add_storage(
        self,
        info: Info,
        name: str,
        description: str | None,
        parent_id: relay.GlobalID | None,
    ) -> types.Storage:
        storage = models.Storage(name=name, description=description)
        if parent_id:
            # 检查上一级位置是否存在
            try:
                parent = parent_id.resolve_node_sync(info, ensure_type=models.Storage)
            except Exception:
                raise ValidationError("上一级位置不存在")

            storage.parent = parent

        storage.save()
        return storage  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_storage(
        self,
        info: Info,
        id: relay.GlobalID,
        name: str | None,
        description: str | None,
        parent_id: relay.GlobalID | None,
    ) -> types.Storage:
        # 检查需要修改的位置是否存在
        try:
            storage = id.resolve_node_sync(info, ensure_type=models.Storage)
        except Exception:
            raise ValidationError("无法修改不存在的位置")

        # 当名称不为空，且与当前名称不同时，才需要修改名称
        if name and name != storage.name:
            storage.name = name

        if description is not strawberry.UNSET and description is not None:
            storage.description = description

        if parent_id is not strawberry.UNSET:
            # 为空则说明是根位置，即 家
            if parent_id:
                try:
                    parent = parent_id.resolve_node_sync(info, ensure_type=models.Storage)
                except Exception:
                    raise ValidationError("上一级位置不存在")
            else:
                parent = None

            storage.parent = parent

        storage.save()
        return storage  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_storage(self, info: Info, storage_id: relay.GlobalID) -> types.Storage:
        try:
            storage = storage_id.resolve_node_sync(info, ensure_type=models.Storage)
        except Exception:
            raise ValidationError("无法删除不存在的位置")

        storage.delete()
        return storage  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def add_item(
        self,
        info: Info,
        name: str,
        number: int,
        storage_id: relay.GlobalID,
        description: str,
        price: float | None,
        expired_at: datetime | None,
    ) -> types.Item:
        try:
            storage = storage_id.resolve_node_sync(info, ensure_type=models.Storage)
        except Exception:
            raise ValidationError("位置不存在")

        if price is strawberry.UNSET:
            price = None

        if expired_at is strawberry.UNSET:
            expired_at = None

        item = models.Item(
            name=name,
            number=number,
            description=description,
            storage=storage,
            price=price,
            expired_at=expired_at,
        )
        item.created_by = info.context.request.user
        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        item.save()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_item(
        self,
        info: Info,
        id: relay.GlobalID,
        name: str | None,
        number: int | None,
        description: str | None,
        price: float | None,
        expired_at: datetime | None,
        storage_id: relay.GlobalID | None,
    ) -> types.Item:
        try:
            item = id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("无法修改不存在的物品")

        if name and name != item.name:
            item.name = name

        if storage_id is not strawberry.UNSET and storage_id is not None:
            try:
                storage = storage_id.resolve_node_sync(info, ensure_type=models.Storage)
            except Exception:
                raise ValidationError("位置不存在")

            item.storage = storage

        if number is not strawberry.UNSET and number is not None:
            item.number = number

        if description is not strawberry.UNSET and description is not None:
            item.description = description

        if price is not strawberry.UNSET:
            item.price = price

        if expired_at is not strawberry.UNSET:
            item.expired_at = expired_at

        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        # 如果修改已删除的物品，则自动恢复它
        if item.is_deleted:
            item.restore()
        else:
            item.save()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_item(self, info: Info, item_id: relay.GlobalID) -> types.Item:
        try:
            item = item_id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("无法删除不存在的物品")

        item.delete()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def restore_item(self, info: Info, item_id: relay.GlobalID) -> types.Item:
        try:
            item = item_id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("物品不存在")

        item.restore()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def add_consumable(
        self,
        info: Info,
        id: relay.GlobalID,
        consumable_ids: list[relay.GlobalID],
    ) -> types.Item:
        try:
            item = id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("无法修改不存在的物品")

        for consumable_id in consumable_ids:
            try:
                consumable = consumable_id.resolve_node_sync(info, ensure_type=models.Item)
            except Exception:
                raise ValidationError("耗材不存在")
            # 不能添加自己作为自己的耗材
            if item.name == consumable.name:
                raise ValidationError("不能添加自己作为自己的耗材")
            item.consumables.add(consumable)

        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        item.save()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_consumable(
        self,
        info: Info,
        id: relay.GlobalID,
        consumable_ids: list[relay.GlobalID],
    ) -> types.Item:
        try:
            item = id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("无法修改不存在的物品")

        for consumable_id in consumable_ids:
            try:
                consumable = consumable_id.resolve_node_sync(info, ensure_type=models.Item)
            except Exception:
                raise ValidationError("耗材不存在")
            item.consumables.remove(consumable)

        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        item.save()
        return item  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def add_picture(
        self,
        info: Info,
        item_id: relay.GlobalID,
        file: Upload,
        description: str,
        box_x: float,
        box_y: float,
        box_h: float,
        box_w: float,
    ) -> types.Picture:
        try:
            item = item_id.resolve_node_sync(info, ensure_type=models.Item)
        except Exception:
            raise ValidationError("无法给不存在的物品添加图片")

        picture = models.Picture(
            item=item,
            picture=file,
            description=description,
            box_x=box_x,
            box_y=box_y,
            box_h=box_h,
            box_w=box_w,
            created_by=info.context.request.user,
        )
        picture.save()
        return picture  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_picture(
        self,
        info: Info,
        id: relay.GlobalID,
        file: Upload | None,
        description: str | None,
        box_x: float | None,
        box_y: float | None,
        box_h: float | None,
        box_w: float | None,
    ) -> types.Picture:
        try:
            picture = id.resolve_node_sync(info, ensure_type=models.Picture)
        except Exception:
            raise ValidationError("无法修改不存在的图片")

        if description is not strawberry.UNSET and description is not None:
            picture.description = description
        if file:
            picture.picture = file  # type: ignore
        if box_x is not strawberry.UNSET and box_x is not None:
            picture.box_x = box_x
        if box_y is not strawberry.UNSET and box_y is not None:
            picture.box_y = box_y
        if box_h is not strawberry.UNSET and box_h is not None:
            picture.box_h = box_h
        if box_w is not strawberry.UNSET and box_w is not None:
            picture.box_w = box_w

        picture.save()
        return picture  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_picture(self, info: Info, picture_id: relay.GlobalID) -> types.Picture:
        try:
            picture = picture_id.resolve_node_sync(info, ensure_type=models.Picture)
        except Exception:
            raise ValidationError("无法删除不存在的图片")

        picture.delete()
        return picture  # type: ignore
