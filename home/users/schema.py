import graphene
from graphql_jwt.decorators import login_required

from home.users.mutations import UpdateAvatarMutation

from .types import UserType


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserType)

    @login_required
    def resolve_viewer(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    update_avatar = UpdateAvatarMutation.Field()
