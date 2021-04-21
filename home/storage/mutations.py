import graphene
from django.utils import timezone
from graphene import relay
from graphene_file_upload.scalars import Upload
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import Item, Picture, Storage
from .types import ItemType, PictureType, StorageType


class AddStorageMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=True, description='备注')
        parent_id = graphene.ID()

    storage = graphene.Field(StorageType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        name = input.get('name')
        description = input.get('description')
        parent_id = input.get('parent_id')

        try:
            Storage.objects.get(name=name)
            raise GraphQLError('名称重复')
        except Storage.DoesNotExist:
            storage = Storage(name=name, description=description)
            if parent_id:
                _, parent_id = from_global_id(parent_id)

                # 检查上一级位置是否存在
                try:
                    parent = Storage.objects.get(pk=parent_id)
                except Storage.DoesNotExist:
                    raise GraphQLError('上一级位置不存在')

                storage.parent = parent

            storage.save()
            return AddStorageMutation(storage=storage)


class DeleteStorageMutation(relay.ClientIDMutation):
    class Input:
        storage_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, storage_id = from_global_id(input.get('storage_id'))

        try:
            storage = Storage.objects.get(pk=storage_id)
            storage.delete()
            return DeleteStorageMutation()
        except Storage.DoesNotExist:
            raise GraphQLError('无法删除不存在的位置')


class UpdateStorageMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        parent_id = graphene.ID()

    storage = graphene.Field(StorageType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, id = from_global_id(input.get('id'))
        name = input.get('name')
        description = input.get('description')
        parent_id = input.get('parent_id')

        # 检查需要修改的位置是否存在
        try:
            storage = Storage.objects.get(pk=id)
        except Storage.DoesNotExist:
            raise GraphQLError('无法修改不存在的位置')

        # 当名称不为空，且与当前名称不同时，才需要修改名称
        if name and name != storage.name:
            try:
                Storage.objects.get(name=name)
                raise GraphQLError('名称重复')
            except Storage.DoesNotExist:
                storage.name = name

        storage.description = description

        if parent_id:
            _, parent_id = from_global_id(parent_id)

            # 检查上一级位置是否存在
            try:
                parent = Storage.objects.get(pk=parent_id)
            except Storage.DoesNotExist:
                raise GraphQLError('上一级位置不存在')

            storage.parent = parent

        storage.save()
        return UpdateStorageMutation(storage=storage)


class AddItemMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        number = graphene.Int(required=True)
        storage_id = graphene.ID(required=True)
        description = graphene.String(required=True, description='备注')
        price = graphene.Float()
        expired_at = graphene.DateTime()

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        name = input.get('name')
        number = input.get('number')
        storage_id = input.get('storage_id')
        description = input.get('description')
        price = input.get('price')
        expired_at = input.get('expired_at')

        try:
            Item.objects.get(name=name)
            raise GraphQLError('名称重复')
        except Item.DoesNotExist:
            _, storage_id = from_global_id(storage_id)
            try:
                storage = Storage.objects.get(pk=storage_id)
            except Storage.DoesNotExist:
                raise GraphQLError('位置不存在')

            item = Item(
                name=name,
                number=number,
                description=description,
                storage=storage,
                price=price,
                expired_at=expired_at,
            )
            item.created_by = info.context.user
            item.edited_by = info.context.user
            item.edited_at = timezone.now()
            item.save()
            return AddItemMutation(item=item)


class DeleteItemMutation(relay.ClientIDMutation):
    class Input:
        item_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, item_id = from_global_id(input.get('item_id'))

        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
            return DeleteItemMutation()
        except Item.DoesNotExist:
            raise GraphQLError('无法删除不存在的物品')


class RestoreItemMutation(relay.ClientIDMutation):
    class Input:
        item_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, item_id = from_global_id(input.get('item_id'))

        try:
            item = Item.objects.get(pk=item_id)
            item.restore()
            return DeleteItemMutation()
        except Item.DoesNotExist:
            raise GraphQLError('物品不存在')


class UpdateItemMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        number = graphene.Int()
        description = graphene.String()
        price = graphene.Float()
        expired_at = graphene.DateTime()
        storage_id = graphene.ID()

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, id = from_global_id(input.get('id'))
        name = input.get('name')
        number = input.get('number')
        storage_id = input.get('storage_id')
        description = input.get('description')
        price = input.get('price')
        expired_at = input.get('expired_at')

        try:
            item = Item.objects.get(pk=id)
        except Item.DoesNotExist:
            raise GraphQLError('无法修改不存在的物品')

        if name and name != item.name:
            try:
                Item.objects.get(name=name)
                raise GraphQLError('名称重复')
            except Item.DoesNotExist:
                item.name = name

        _, storage_id = from_global_id(input.get('storage_id'))
        try:
            storage = Storage.objects.get(pk=storage_id)
        except Storage.DoesNotExist:
            raise GraphQLError('位置不存在')

        item.storage = storage
        item.number = number
        item.description = description
        item.price = price
        item.expired_at = expired_at
        item.edited_by = info.context.user
        item.edited_at = timezone.now()
        # 如果修改已删除的物品，则自动恢复它
        if item.is_deleted:
            item.restore()
        else:
            item.save()
        return UpdateItemMutation(item=item)


class AddConsumableMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True, description='物品的 ID')
        consumable_ids = graphene.List(graphene.ID,
                                       required=True,
                                       description='耗材的 ID')

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, id = from_global_id(input.get('id'))
        consumable_ids = input.get('consumable_ids')

        try:
            item = Item.objects.get(pk=id)
        except Item.DoesNotExist:
            raise GraphQLError('无法修改不存在的物品')

        for consumable_id in consumable_ids:
            try:
                _, consumable_id = from_global_id(consumable_id)
                consumable = Item.objects.get(pk=consumable_id)
            except Item.DoesNotExist:
                raise GraphQLError('耗材不存在')
            # 不能添加自己作为自己的耗材
            if item.name == consumable.name:
                raise GraphQLError('不能添加自己作为自己的耗材')
            item.consumables.add(consumable)

        item.edited_by = info.context.user
        item.edited_at = timezone.now()
        item.save()
        return AddConsumableMutation(item=item)


class DeleteConsumableMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True, description='物品的 ID')
        consumable_ids = graphene.List(graphene.ID,
                                       required=True,
                                       description='耗材的 ID')

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, id = from_global_id(input.get('id'))
        consumable_ids = input.get('consumable_ids')

        try:
            item = Item.objects.get(pk=id)
        except Item.DoesNotExist:
            raise GraphQLError('无法修改不存在的物品')

        for consumable_id in consumable_ids:
            try:
                _, consumable_id = from_global_id(consumable_id)
                consumable = Item.objects.get(pk=consumable_id)
            except Item.DoesNotExist:
                raise GraphQLError('耗材不存在')
            item.consumables.remove(consumable)

        item.edited_by = info.context.user
        item.edited_at = timezone.now()
        item.save()
        return DeleteConsumableMutation(item=item)


class AddPictureMutation(graphene.ClientIDMutation):
    class Input:
        item_id = graphene.ID(required=True, description='物品的 ID')
        file = Upload(required=True, description='图片')
        description = graphene.String(required=True, description='备注')
        box_x = graphene.Float(required=True, description='边界框中心点 X')
        box_y = graphene.Float(required=True, description='边界框中心点 Y')
        box_h = graphene.Float(required=True, description='边界框高')
        box_w = graphene.Float(required=True, description='边界框宽')

    picture = graphene.Field(PictureType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, item_id = from_global_id(input.get('item_id'))
        description = input.get('description')
        file = input.get('file')
        box_x = input.get('box_x')
        box_y = input.get('box_y')
        box_h = input.get('box_h')
        box_w = input.get('box_w')

        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise GraphQLError('无法给不存在的物品添加图片')

        picture = Picture(
            item=item,
            picture=file,
            description=description,
            box_x=box_x,
            box_y=box_y,
            box_h=box_h,
            box_w=box_w,
            created_by=info.context.user,
        )
        picture.save()

        return AddPictureMutation(picture=picture)


class DeletePictureMutation(relay.ClientIDMutation):
    class Input:
        picture_id = graphene.ID(required=True, description='图片的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, picture_id = from_global_id(input.get('picture_id'))

        try:
            picture = Picture.objects.get(pk=picture_id)
            picture.delete()
            return DeletePictureMutation()
        except Picture.DoesNotExist:
            raise GraphQLError('无法删除不存在的图片')


class UpdatePictureMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        file = Upload(description='图片')
        description = graphene.String(required=True, description='备注')
        box_x = graphene.Float(required=True, description='边界框中心点 X')
        box_y = graphene.Float(required=True, description='边界框中心点 Y')
        box_h = graphene.Float(required=True, description='边界框高')
        box_w = graphene.Float(required=True, description='边界框宽')

    picture = graphene.Field(PictureType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        _, id = from_global_id(input.get('id'))
        description = input.get('description')
        file = input.get('file')
        box_x = input.get('box_x')
        box_y = input.get('box_y')
        box_h = input.get('box_h')
        box_w = input.get('box_w')

        try:
            picture: Picture = Picture.objects.get(pk=id)
        except Picture.DoesNotExist:
            raise GraphQLError('无法修改不存在的图片')

        picture.description = description
        if file:
            picture.picture = file
        picture.box_x = box_x
        picture.box_y = box_y
        picture.box_h = box_h
        picture.box_w = box_w
        picture.save()

        return UpdatePictureMutation(picture=picture)