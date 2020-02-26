import graphene
from django.contrib.auth import get_user_model
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import Item, Storage


class StorageType(DjangoObjectType):
    class Meta:
        model = Storage
        fields = '__all__'


class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        fields = '__all__'


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = '__all__'


class Query:
    storages = graphene.List(StorageType)
    items = graphene.List(ItemType)
    storage = graphene.Field(StorageType, storage_id=graphene.String())
    item = graphene.Field(ItemType, item_id=graphene.String())
    me = graphene.Field(UserType)

    @login_required
    def resolve_me(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_storages(self, info, **kwargs):
        return Storage.objects.all()

    @login_required
    def resolve_items(self, info, **kwargs):
        return Item.objects.all()

    @login_required
    def resolve_storage(self, info, storage_id):
        return Storage.objects.get(pk=storage_id)

    @login_required
    def resolve_item(self, info, item_id):
        return Item.objects.get(pk=item_id)


class StorageMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        parent_id = graphene.ID()

    storage = graphene.Field(StorageType)

    @login_required
    def mutate(self, info, id, name=None, description=None, parent_id=None):
        storage = Storage.objects.get(pk=id)
        if name:
            storage.name = name
        if description:
            storage.description = description
        if parent_id:
            parent = Storage.objects.get(pk=parent_id)
            storage.parent = parent
        storage.save()
        return StorageMutation(storage=storage)


class ItemMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        storage_id = graphene.ID()
        description = graphene.String()
        price = graphene.String()
        expiration_date = graphene.DateTime()

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self,
               info,
               id,
               name=None,
               description=None,
               storage_id=None,
               price=None):
        item = Item.objects.get(pk=id)
        if name:
            item.name = name
        if price:
            item.price = price
        if description:
            item.description = description
        if storage_id:
            storage = Storage.objects.get(pk=storage_id)
            item.storage = storage
        item.editor = info.context.user
        item.save()
        return ItemMutation(item=item)


class Mutation(graphene.ObjectType):
    update_storage = StorageMutation.Field()
    update_item = ItemMutation.Field()
