import graphene
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import Item, Storage


#region type
class ItemFilter(FilterSet):
    class Meta:
        model = Item
        fields = {
            'name': ['exact', 'icontains'],
            'storage': ['exact', 'isnull'],
            'description': ['exact', 'icontains'],
            'expired_at': ['lt', 'gt'],
            'is_delete': ['exact'],
        }

    order_by = OrderingFilter(fields=(
        ('created_at', 'created_at'),
        ('updated_at', 'updated_at'),
        ('expired_at', 'expired_at'),
    ))


class StorageFilter(FilterSet):
    class Meta:
        model = Storage
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'level': ['exact'],
        }


class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        fields = '__all__'
        interfaces = (relay.Node, )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Item.objects.get(pk=id)


class StorageType(DjangoObjectType):
    class Meta:
        model = Storage
        fields = '__all__'
        interfaces = (relay.Node, )

    items = DjangoFilterConnectionField(ItemType, filterset_class=ItemFilter)
    ancestors = DjangoFilterConnectionField(lambda: StorageType,
                                            filterset_class=StorageFilter)

    @login_required
    def resolve_items(self, info, **args):
        return self.items

    @login_required
    def resolve_ancestors(self, info, **args):
        return self.get_ancestors()

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Storage.objects.get(pk=id)


#endregion


#region query
class Query(graphene.ObjectType):
    item = relay.Node.Field(ItemType)
    items = DjangoFilterConnectionField(ItemType, filterset_class=ItemFilter)
    storage = relay.Node.Field(StorageType)
    storages = DjangoFilterConnectionField(StorageType,
                                           filterset_class=StorageFilter)

    @login_required
    def resolve_items(self, info, **args):
        return Item.objects.all()

    @login_required
    def resolve_storages(self, info, **args):
        return Storage.objects.all()


#endregion


#region mutation
#region storage
class AddStorageMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String()
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
            raise GraphQLError('位置不存在，无法删除')


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


#endregion


#region item
class AddItemMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        number = graphene.Int(required=True)
        storage_id = graphene.ID(required=True)
        description = graphene.String()
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
            raise GraphQLError('物品不存在')


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
        item.save()
        return UpdateItemMutation(item=item)


#endregion
class Mutation(graphene.ObjectType):
    update_storage = UpdateStorageMutation.Field()
    update_item = UpdateItemMutation.Field()
    add_storage = AddStorageMutation.Field()
    add_item = AddItemMutation.Field()
    delete_storage = DeleteStorageMutation.Field()
    delete_item = DeleteItemMutation.Field()
    restore_item = RestoreItemMutation.Field()


#endregion
