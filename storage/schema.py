from datetime import timedelta

import graphene
from django.contrib.auth import get_user_model
from django.utils import timezone
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


class SearchType(graphene.ObjectType):
    items = graphene.List(ItemType)
    storages = graphene.List(StorageType)


class StorageInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()


class UpdateStorageInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    parent = StorageInput()


class UpdateItemInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    number = graphene.Int()
    description = graphene.String()
    price = graphene.Float()
    expiration_date = graphene.DateTime()
    storage = StorageInput()


class AddStorageInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    parent = StorageInput()


class AddItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    number = graphene.Int(required=True)
    storage = StorageInput(required=True)
    description = graphene.String()
    price = graphene.Float()
    expiration_date = graphene.DateTime()


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    root_storage = graphene.List(StorageType)
    storages = graphene.List(StorageType)
    items = graphene.List(ItemType)
    storage = graphene.Field(StorageType, id=graphene.ID(required=True))
    item = graphene.Field(ItemType, id=graphene.ID(required=True))
    search = graphene.Field(SearchType, key=graphene.String(required=True))
    latest_update_items = graphene.List(ItemType, number=graphene.Int(required=True))
    latest_added_items = graphene.List(ItemType, number=graphene.Int(required=True))
    near_expired_items = graphene.List(ItemType,
                                       within=graphene.Int(required=True),
                                       number=graphene.Int())
    expired_items = graphene.List(ItemType, number=graphene.Int())

    @login_required
    def resolve_me(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_root_storage(self, info, **kwargs):
        return Storage.objects.filter(level=0)

    @login_required
    def resolve_storages(self, info, **kwargs):
        return Storage.objects.all()

    @login_required
    def resolve_items(self, info, **kwargs):
        return Item.objects.all()

    @login_required
    def resolve_storage(self, info, id):
        return Storage.objects.get(pk=id)

    @login_required
    def resolve_item(self, info, id):
        return Item.objects.get(pk=id)

    @login_required
    def resolve_search(self, info, key):
        items = (Item.objects.filter(name__icontains=key)
                 | Item.objects.filter(description__icontains=key)).distinct()
        storages = (
            Storage.objects.filter(name__icontains=key)
            | Storage.objects.filter(description__icontains=key)).distinct()
        return SearchType(items=items, storages=storages)

    @login_required
    def resolve_latest_update_items(self, info, number):
        items = Item.objects.all().order_by('-update_date')[:number]
        return items

    @login_required
    def resolve_latest_added_items(self, info, number):
        items = Item.objects.all().order_by('-date_added')[:number]
        return items

    @login_required
    def resolve_near_expired_items(self, info, within, number=None):
        """ 接近过期的物品

        within: 最近多少天内过期
        number: 显示多少物品，不提供则显示全部
        """
        now = timezone.now()
        expired = now + timedelta(days=within)
        items = Item.objects.all().filter(
            expiration_date__isnull=False,
            expiration_date__range=(now, expired)).order_by('expiration_date')
        if number:
            return items[:number]
        return items

    @login_required
    def resolve_expired_items(self, info, number=None):
        """ 已经过期的物品 """
        now = timezone.now()
        items = Item.objects.all().filter(
            expiration_date__isnull=False,
            expiration_date__lt=now).order_by('expiration_date')
        if number:
            return items[:number]
        return items


class UpdateStorageMutation(graphene.Mutation):
    class Arguments:
        input = UpdateStorageInput(required=True)

    storage = graphene.Field(StorageType)

    @login_required
    def mutate(self, info, input):
        storage = Storage.objects.get(pk=input.id)
        if input.name and input.name != storage.name:
            try:
                Storage.objects.get(name=input.name)
            except Storage.DoesNotExist:
                storage.name = input.name
            else:
                raise GraphQLError('名称重复')
        storage.description = input.description
        if input.parent:
            parent = Storage.objects.get(pk=input.parent.id)
            storage.parent = parent
        storage.save()
        return UpdateStorageMutation(storage=storage)


class UpdateItemMutation(graphene.Mutation):
    class Arguments:
        input = UpdateItemInput(required=True)

    item = graphene.Field(ItemType)

    @login_required
    def mutate(self, info, input):
        item = Item.objects.get(pk=input.id)
        if input.name and input.name != item.name:
            try:
                Item.objects.get(name=input.name)
            except Item.DoesNotExist:
                item.name = input.name
            else:
                raise GraphQLError('名称重复')
        item.number = input.number
        item.storage = Storage.objects.get(pk=input.storage.id)
        item.description = input.description
        item.price = input.price
        item.expiration_date = input.expiration_date
        item.editor = info.context.user
        item.save()
        return UpdateItemMutation(item=item)


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
                parent = Storage.objects.get(pk=input.parent.id)
                storage.parent = parent
            storage.save()
            return AddStorageMutation(storage=storage)


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
            item = Item(
                name=input.name,
                number=input.number,
                description=input.description,
                storage=Storage.objects.get(pk=input.storage.id),
                price=input.price,
                expiration_date=input.expiration_date,
            )
            item.editor = info.context.user
            item.save()
            return AddItemMutation(item=item)


class DeleteStorageMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    deletedId = graphene.ID()

    @login_required
    def mutate(self, info, id):
        try:
            storage = Storage.objects.get(pk=id)
            storage.delete()
            return DeleteStorageMutation(deletedId=id)
        except Storage.DoesNotExist:
            raise GraphQLError('位置不存在')


class DeleteItemMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    deletedId = graphene.ID()

    @login_required
    def mutate(self, info, id):
        try:
            item = Item.objects.get(pk=id)
            item.delete()
            return DeleteItemMutation(deletedId=id)
        except Item.DoesNotExist:
            raise GraphQLError('物品不存在')


class Mutation(graphene.ObjectType):
    update_storage = UpdateStorageMutation.Field()
    update_item = UpdateItemMutation.Field()
    add_storage = AddStorageMutation.Field()
    add_item = AddItemMutation.Field()
    delete_storage = DeleteStorageMutation.Field()
    delete_item = DeleteItemMutation.Field()
