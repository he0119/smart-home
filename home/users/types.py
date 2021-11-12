import graphene
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from home.users.models import Config


class ConfigType(DjangoObjectType):
    class Meta:
        model = Config
        fields = "__all__"
        interfaces = (relay.Node,)


class UserType(DjangoObjectType):
    avatar = graphene.String()
    configs = graphene.List(ConfigType)

    class Meta:
        model = get_user_model()
        fields = "__all__"
        interfaces = (relay.Node,)

    @login_required
    def resolve_avatar(self, info, **args):
        if hasattr(self, "avatar"):
            return self.avatar.avatar.url

    @login_required
    def resolve_configs(self, info, **args):
        return self.configs.all()
