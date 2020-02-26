import graphene
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
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


class UpdateStorageInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    parent = graphene.ID()


class UpdateStorageMutation(graphene.Mutation):
    class Arguments:
        input = UpdateStorageInput(required=True)

    storage = graphene.Field(StorageType)

    @login_required
    def mutate(self, info, input):
        storage = Storage.objects.get(pk=input.id)
        if input.name:
            storage.name = input.name
        if input.description:
            storage.description = input.description
        if input.parent:
            parent = Storage.objects.get(pk=input.parent)
            storage.parent = parent
        storage.save()
        return UpdateStorageMutation(storage=storage)


class UpdateItemInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    number = graphene.Int()
    description = graphene.String()
    price = graphene.String()
    expiration_date = graphene.DateTime()
    storage = graphene.ID()


class UpdateItemMutation(graphene.Mutation):
    class Arguments:
        input = UpdateItemInput(required=True)

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self, info, input):
        item = Item.objects.get(pk=input.id)
        if input.name:
            item.name = input.name
        if input.number:
            item.number = input.number
        if input.storage:
            storage = Storage.objects.get(pk=input.storage)
            item.storage = storage
        if input.description:
            item.description = input.description
        if input.price:
            item.price = input.price
        if input.expiration_date:
            item.expiration_date = make_aware(input.expiration_date)
        item.editor = info.context.user
        item.save()
        return UpdateItemMutation(item=item)


class AddStorageInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    parent = graphene.ID()


class AddStorageMutation(graphene.Mutation):
    class Arguments:
        input = AddStorageInput(required=True)

    storage = graphene.Field(StorageType)

    @login_required
    def mutate(self, info, input):
        try:
            Storage.objects.get(name=input.name)
            raise GraphQLError('名称重复')
        except Storage.DoesNotExist:
            storage = Storage(name=input.name, description=input.description)
            if input.parent:
                parent = Storage.objects.get(pk=input.parent)
                storage.parent = parent
            storage.save()
            return AddStorageMutation(storage=storage)


class AddItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    number = graphene.Int(required=True)
    storage = graphene.ID(required=True)
    description = graphene.String()
    price = graphene.String()
    expiration_date = graphene.DateTime()


class AddItemMutation(graphene.Mutation):
    class Arguments:
        input = AddItemInput(required=True)

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self, info, input):
        try:
            Item.objects.get(name=input.name)
            raise GraphQLError('名称重复')
        except Item.DoesNotExist:
            storage = Storage.objects.get(pk=input.storage)
            item = Item(
                name=input.name,
                number=input.number,
                description=input.description,
                storage=storage,
                price=input.price,
            )
            if input.expiration_date:
                item.expiration_date = make_aware(input.expiration_date)
            item.editor = info.context.user
            item.save()
            return AddItemMutation(item=item)


class Mutation(graphene.ObjectType):
    update_storage = UpdateStorageMutation.Field()
    update_item = UpdateItemMutation.Field()
    add_storage = AddStorageMutation.Field()
    add_item = AddItemMutation.Field()
