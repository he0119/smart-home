import graphene
from django_filters import FilterSet, OrderingFilter
from django_filters.filters import BooleanFilter
from graphene import relay
from graphene_django.fields import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import Item, Picture, Storage


class ItemFilter(FilterSet):
    consumables = BooleanFilter(field_name="consumables", method="filter_consumables")

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            # 默认不显示已删除的物品
            if data.get("is_deleted") is None:
                data["is_deleted"] = False

        super().__init__(data, *args, **kwargs)

    def filter_consumables(self, queryset, name, value):
        if value:
            return queryset.exclude(consumables=None)
        else:
            return queryset.filter(consumables=None)

    class Meta:
        model = Item
        fields = {
            "name": ["exact", "icontains"],
            "storage": ["exact", "isnull"],
            "description": ["exact", "icontains"],
            "expired_at": ["lt", "gt"],
            "is_deleted": ["exact"],
            "consumables": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("edited_at", "edited_at"),
            ("expired_at", "expired_at"),
            ("deleted_at", "deleted_at"),
        )
    )


class StorageFilter(FilterSet):
    class Meta:
        model = Storage
        fields = {
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "level": ["exact"],
        }


class PictureFilter(FilterSet):
    class Meta:
        model = Picture
        fields = {
            "item__id": ["exact"],
            "item__name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
        }

    order_by = OrderingFilter(fields=(("created_at", "created_at"),))


class PictureType(DjangoObjectType):
    class Meta:
        model = Picture
        fields = "__all__"
        interfaces = (relay.Node,)

    name = graphene.String(required=True)
    url = graphene.String(required=True)

    @login_required
    def resolve_name(self, info, **args):
        return self.picture.name.split("/")[-1]

    @login_required
    def resolve_url(self, info, **args):
        return self.picture.url

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Picture.objects.get(pk=id)


class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        fields = "__all__"
        interfaces = (relay.Node,)

    consumables = DjangoFilterConnectionField(
        lambda: ItemType, filterset_class=ItemFilter
    )
    pictures = DjangoConnectionField(PictureType)

    @login_required
    def resolve_pictures(self, info, **args):
        return self.pictures

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Item.objects.get(pk=id)


class StorageType(DjangoObjectType):
    class Meta:
        model = Storage
        fields = "__all__"
        interfaces = (relay.Node,)

    items = DjangoFilterConnectionField(ItemType, filterset_class=ItemFilter)
    ancestors = DjangoFilterConnectionField(
        lambda: StorageType, filterset_class=StorageFilter
    )

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
