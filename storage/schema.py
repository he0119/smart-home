import graphene
from graphene_django.types import DjangoObjectType

from .models import Item, Storage


class StorageType(DjangoObjectType):
    class Meta:
        model = Storage


class ItemType(DjangoObjectType):
    class Meta:
        model = Item


class Query:
    storages = graphene.List(StorageType)
    items = graphene.List(ItemType)

    def resolve_storages(self, info, **kwargs):
        return Storage.objects.all()

    def resolve_items(self, info, **kwargs):
        return Item.objects.all()
