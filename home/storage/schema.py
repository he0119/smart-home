import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from .models import Item, Picture, Storage
from .mutations import (AddConsumableMutation, AddItemMutation,
                        AddPictureMutation, AddStorageMutation,
                        DeleteConsumableMutation, DeleteItemMutation,
                        DeletePictureMutation, DeleteStorageMutation,
                        RestoreItemMutation, UpdateItemMutation,
                        UpdatePictureMutation, UpdateStorageMutation)
from .types import (ItemFilter, ItemType, PictureFilter, PictureType,
                    StorageFilter, StorageType)


class Query(graphene.ObjectType):
    item = relay.Node.Field(ItemType)
    items = DjangoFilterConnectionField(ItemType, filterset_class=ItemFilter)
    storage = relay.Node.Field(StorageType)
    storages = DjangoFilterConnectionField(StorageType,
                                           filterset_class=StorageFilter)
    picture = relay.Node.Field(PictureType)
    pictures = DjangoFilterConnectionField(PictureType,
                                           filterset_class=PictureFilter)

    @login_required
    def resolve_items(self, info, **args):
        return Item.objects.all()

    @login_required
    def resolve_storages(self, info, **args):
        return Storage.objects.all()

    @login_required
    def resolve_pictures(self, info, **args):
        return Picture.objects.all()



class Mutation(graphene.ObjectType):
    update_storage = UpdateStorageMutation.Field()
    update_item = UpdateItemMutation.Field()
    add_storage = AddStorageMutation.Field()
    add_item = AddItemMutation.Field()
    delete_storage = DeleteStorageMutation.Field()
    delete_item = DeleteItemMutation.Field()
    restore_item = RestoreItemMutation.Field()
    add_consumable = AddConsumableMutation.Field()
    delete_consumable = DeleteConsumableMutation.Field()
    add_picture = AddPictureMutation.Field()
    delete_picture = DeletePictureMutation.Field()
    update_picture = UpdatePictureMutation.Field()

