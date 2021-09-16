import graphene
from django_filters import FilterSet
from graphene import ObjectType, relay
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import MiPush


class MiPushFilter(FilterSet):
    class Meta:
        model = MiPush
        fields = {
            "user__username": ["exact"],
            "model": ["exact", "icontains"],
        }


class MiPushType(DjangoObjectType):
    class Meta:
        model = MiPush
        fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return MiPush.objects.get(pk=id)


class MiPushKeyType(ObjectType):
    app_id = graphene.String()
    app_key = graphene.String()
