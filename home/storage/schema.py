from datetime import datetime
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils import timezone
from strawberry.file_uploads import Upload
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay
from strawberry_django_plus.permissions import IsAuthenticated

from . import models, types


@gql.type
class Query:
    item: types.Item = gql.django.node(directives=[IsAuthenticated()])
    items: relay.Connection[types.Item] = gql.django.connection(
        directives=[IsAuthenticated()]
    )
    storage: types.Storage = gql.django.node(directives=[IsAuthenticated()])
    storages: relay.Connection[types.Storage] = gql.django.connection(
        directives=[IsAuthenticated()]
    )
    picture: types.Picture = gql.django.node(directives=[IsAuthenticated()])
    pictures: relay.Connection[types.Picture] = gql.django.connection(
        directives=[IsAuthenticated()]
    )


@gql.type
class Mutation:
    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def add_storage(
        self,
        info: Info,
        name: str,
        description: Optional[str],
        parent_id: Optional[relay.GlobalID],
    ) -> types.Storage:
        try:
            models.Storage.objects.get(name=name)
            raise ValidationError("名称重复")
        except models.Storage.DoesNotExist:
            storage = models.Storage(name=name, description=description)
            if parent_id:
                parent: models.Storage = parent_id.resolve_node(info)  # type: ignore
                # 检查上一级位置是否存在
                if not parent:
                    raise ValidationError("上一级位置不存在")

                storage.parent = parent

            storage.save()
            return storage  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def update_storage(
        self,
        info: Info,
        id: relay.GlobalID,
        name: Optional[str],
        description: Optional[str],
        parent_id: Optional[relay.GlobalID],
    ) -> types.Storage:

        # 检查需要修改的位置是否存在
        storage: models.Storage = id.resolve_node(info)  # type: ignore
        if not storage:
            raise ValidationError("无法修改不存在的位置")

        # 当名称不为空，且与当前名称不同时，才需要修改名称
        if name and name != storage.name:
            try:
                models.Storage.objects.get(name=name)
                raise ValidationError("名称重复")
            except models.Storage.DoesNotExist:
                storage.name = name

        storage.description = description

        if parent_id:
            parent: models.Storage = parent_id.resolve_node(info)  # type: ignore
            if not parent:
                raise ValidationError("上一级位置不存在")

            storage.parent = parent

        storage.save()
        return storage  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def delete_storage(self, info: Info, storage_id: relay.GlobalID) -> types.Storage:
        storage: models.Storage = storage_id.resolve_node(info)  # type: ignore
        if not storage:
            raise ValidationError("无法删除不存在的位置")

        storage.delete()
        return storage  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def add_item(
        self,
        info: Info,
        name: str,
        number: int,
        storage_id: relay.GlobalID,
        description: str,
        price: Optional[float],
        expired_at: Optional[datetime],
    ) -> types.Item:
        try:
            models.Item.objects.get(name=name)
            raise ValidationError("名称重复")
        except models.Item.DoesNotExist:
            storage: models.Storage = storage_id.resolve_node(info)  # type: ignore
            if not storage:
                raise ValidationError("位置不存在")

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

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def update_item(
        self,
        info: Info,
        id: relay.GlobalID,
        name: Optional[str],
        number: Optional[int],
        description: Optional[str],
        price: Optional[float],
        expired_at: Optional[datetime],
        storage_id: Optional[relay.GlobalID],
    ) -> types.Item:
        item: models.Item = id.resolve_node(info)  # type: ignore
        if not item:
            raise ValidationError("无法修改不存在的物品")

        if name and name != item.name:
            try:
                models.Item.objects.get(name=name)
                raise ValidationError("名称重复")
            except models.Item.DoesNotExist:
                item.name = name

        storage: models.Storage = storage_id.resolve_node(info)  # type: ignore
        if not storage:
            raise ValidationError("位置不存在")

        item.storage = storage
        item.number = number
        item.description = description
        item.price = price
        item.expired_at = expired_at
        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        # 如果修改已删除的物品，则自动恢复它
        if item.is_deleted:
            item.restore()
        else:
            item.save()
        return item  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def delete_item(self, info: Info, item_id: relay.GlobalID) -> types.Item:
        item: models.Item = item_id.resolve_node(info)  # type: ignore
        if not item:
            raise ValidationError("无法删除不存在的物品")

        item.delete()
        return item  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def restore_item(self, info: Info, item_id: relay.GlobalID) -> types.Item:
        item: models.Item = item_id.resolve_node(info)  # type: ignore
        if not item:
            raise ValidationError("物品不存在")
        item.restore()
        return item  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def add_consumable(
        self,
        info: Info,
        id: relay.GlobalID,
        consumable_ids: list[relay.GlobalID],
    ) -> types.Item:
        item: models.Item = id.resolve_node(info)  # type: ignore
        if not item:
            raise ValidationError("无法修改不存在的物品")

        for consumable_id in consumable_ids:
            consumable: models.Item = consumable_id.resolve_node(info)  # type: ignore
            if not consumable:
                raise ValidationError("耗材不存在")
            # 不能添加自己作为自己的耗材
            if item.name == consumable.name:
                raise ValidationError("不能添加自己作为自己的耗材")
            item.consumables.add(consumable)

        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        item.save()
        return item  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def delete_consumable(
        self,
        info: Info,
        id: relay.GlobalID,
        consumable_ids: list[relay.GlobalID],
    ) -> types.Item:
        item: models.Item = id.resolve_node(info)  # type: ignore
        if not item:
            raise ValidationError("无法修改不存在的物品")

        for consumable_id in consumable_ids:
            consumable: models.Item = consumable_id.resolve_node(info)  # type: ignore
            if not consumable:
                raise ValidationError("耗材不存在")
            item.consumables.remove(consumable)

        item.edited_by = info.context.request.user
        item.edited_at = timezone.now()
        item.save()
        return item  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
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
        item: models.Item = item_id.resolve_node(info)  # type: ignore
        if not item:
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

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def update_picture(
        self,
        info: Info,
        id: relay.GlobalID,
        file: Optional[Upload],
        description: Optional[str],
        box_x: Optional[float],
        box_y: Optional[float],
        box_h: Optional[float],
        box_w: Optional[float],
    ) -> types.Picture:
        picture: models.Picture = id.resolve_node(info)  # type: ignore
        if not picture:
            raise ValidationError("无法修改不存在的图片")

        picture.description = description
        if file:
            picture.picture = file
        picture.box_x = box_x
        picture.box_y = box_y
        picture.box_h = box_h
        picture.box_w = box_w
        picture.save()
        return picture  # type: ignore

    @gql.django.input_mutation(directives=[IsAuthenticated()])
    def delete_picture(self, info: Info, picture_id: relay.GlobalID) -> types.Picture:
        picture: models.Picture = picture_id.resolve_node(info)  # type: ignore
        if not picture:
            raise ValidationError("无法删除不存在的图片")
        picture.delete()
        return picture  # type: ignore
