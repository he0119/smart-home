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
            'description': ['exact', 'icontains'],
            'expiration_date': ['lt', 'gt'],
        }

    order_by = OrderingFilter(fields=(
        ('date_added', 'date_added'),
        ('update_date', 'update_date'),
        ('expiration_date', 'expiration_date'),
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

    @login_required
    def resolve_items(self, info, **args):
        return self.items

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
    storage_ancestors = DjangoFilterConnectionField(
        StorageType,
        filterset_class=StorageFilter,
        id=graphene.ID(required=True))

    @login_required
    def resolve_items(self, info, **kwargs):
        return Item.objects.all()

    @login_required
    def resolve_storages(self, info, **kwargs):
        return Storage.objects.all()

    @login_required
    def resolve_storage_ancestors(self, info, **kwargs):
        _, storage_id = from_global_id(kwargs.get('id'))

        storage = Storage.objects.get(pk=storage_id)
        return storage.get_ancestors(include_self=True)


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
    def mutate_and_get_payload(cls, root, info, **kwargs):
        try:
            Storage.objects.get(name=kwargs.get('name'))
            raise GraphQLError('名称重复')
        except Storage.DoesNotExist:
            storage = Storage(name=kwargs.get('name'),
                              description=kwargs.get('description'))
            if kwargs.get('parent_id'):
                _, parent_id = from_global_id(kwargs.get('parent_id'))
                parent = Storage.objects.get(pk=parent_id)
                storage.parent = parent
            storage.save()
            return AddStorageMutation(storage=storage)


class DeleteStorageMutation(relay.ClientIDMutation):
    class Input:
        storage_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, storage_id = from_global_id(kwargs.get('storage_id'))

        try:
            storage = Storage.objects.get(pk=storage_id)
            storage.delete()
            return DeleteStorageMutation()
        except Storage.DoesNotExist:
            raise GraphQLError('位置不存在')


class UpdateStorageMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        parent_id = graphene.ID()

    storage = graphene.Field(StorageType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, id = from_global_id(kwargs.get('id'))

        storage = Storage.objects.get(pk=id)
        if kwargs.get('name') and kwargs.get('name') != storage.name:
            try:
                Storage.objects.get(name=kwargs.get('name'))
            except Storage.DoesNotExist:
                storage.name = kwargs.get('name')
            else:
                raise GraphQLError('名称重复')
        storage.description = kwargs.get('description')
        if kwargs.get('parent_id'):
            _, parent_id = from_global_id(kwargs.get('parent_id'))
            parent = Storage.objects.get(pk=parent_id)
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
        expiration_date = graphene.DateTime()

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        try:
            Item.objects.get(name=kwargs.get('name'))
            raise GraphQLError('名称重复')
        except Item.DoesNotExist:
            _, storage_id = from_global_id(kwargs.get('storage_id'))
            item = Item(
                name=kwargs.get('name'),
                number=kwargs.get('number'),
                description=kwargs.get('description'),
                storage=Storage.objects.get(pk=storage_id),
                price=kwargs.get('price'),
                expiration_date=kwargs.get('expiration_date'),
            )
            item.editor = info.context.user
            item.save()
            return AddItemMutation(item=item)


class DeleteItemMutation(relay.ClientIDMutation):
    class Input:
        item_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, item_id = from_global_id(kwargs.get('item_id'))

        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
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
        expiration_date = graphene.DateTime()
        storage_id = graphene.ID()

    item = graphene.Field(ItemType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, id = from_global_id(kwargs.get('id'))

        item = Item.objects.get(pk=id)
        if kwargs.get('name') and kwargs.get('name') != item.name:
            try:
                Item.objects.get(name=kwargs.get('name'))
            except Item.DoesNotExist:
                item.name = kwargs.get('name')
            else:
                raise GraphQLError('名称重复')
        item.number = kwargs.get('number')
        _, storage_id = from_global_id(kwargs.get('storage_id'))
        item.storage = Storage.objects.get(pk=storage_id)
        item.description = kwargs.get('description')
        item.price = kwargs.get('price')
        item.expiration_date = kwargs.get('expiration_date')
        item.editor = info.context.user
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


#endregion
