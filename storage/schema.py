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


class UpdateStorageMutation(graphene.Mutation):
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
        return UpdateStorageMutation(storage=storage)


class UpdateItemMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        number = graphene.Int()
        description = graphene.String()
        price = graphene.String()
        expiration_date = graphene.DateTime()
        storage_id = graphene.ID()

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self,
               info,
               id,
               name=None,
               number=None,
               description=None,
               price=None,
               expiration_date=None,
               storage_id=None):
        item = Item.objects.get(pk=id)
        if name:
            item.name = name
        if number:
            item.number = number
        if storage_id:
            storage = Storage.objects.get(pk=storage_id)
            item.storage = storage
        if description:
            item.description = description
        if price:
            item.price = price
        if expiration_date:
            item.expiration_date = expiration_date
        item.editor = info.context.user
        item.save()
        return UpdateItemMutation(item=item)


class CreateStorageMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        parent_id = graphene.ID()

    storage = graphene.Field(StorageType)

    @login_required
    def mutate(self, info, name, description=None, parent_id=None):
        storage = Storage(name=name, description=description)
        if parent_id:
            parent = Storage.objects.get(pk=parent_id)
            storage.parent = parent
        storage.save()
        return CreateStorageMutation(storage=storage)


class CreateItemMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        number = graphene.Int(required=True)
        storage_id = graphene.ID(required=True)
        description = graphene.String()
        price = graphene.String()
        expiration_date = graphene.DateTime()

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self,
               info,
               name,
               number,
               storage_id,
               description=None,
               price=None,
               expiration_date=None):
        storage = Storage.objects.get(pk=storage_id)
        item = Item(
            name=name,
            number=number,
            description=description,
            storage=storage,
            price=price,
            expiration_date=expiration_date,
        )
        item.editor = info.context.user
        item.save()
        return CreateItemMutation(item=item)


class Mutation(graphene.ObjectType):
    update_storage = UpdateStorageMutation.Field()
    update_item = UpdateItemMutation.Field()
    create_storage = CreateStorageMutation.Field()
    create_item = CreateItemMutation.Field()
