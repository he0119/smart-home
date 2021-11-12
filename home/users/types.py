import graphene
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required


class UserType(DjangoObjectType):
    avatar = graphene.String()

    class Meta:
        model = get_user_model()
        fields = "__all__"
        interfaces = (relay.Node,)

    @login_required
    def resolve_avatar(self, info, **args):
        return self.avatar.avatar.url
