import graphene
from graphql_jwt.decorators import login_required

from .types import UserType


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserType)

    @login_required
    def resolve_viewer(self, info):
        return info.context.user
