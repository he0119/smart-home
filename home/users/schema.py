# import graphene
# from graphql_jwt.decorators import login_required

# from .mutations import DeleteConfigMutation, UpdateAvatarMutation, UpdateConfigMutation
# from .types import UserType


# class Query(graphene.ObjectType):
#     viewer = graphene.Field(UserType)

#     @login_required
#     def resolve_viewer(self, info):
#         return info.context.user


# class Mutation(graphene.ObjectType):
#     update_avatar = UpdateAvatarMutation.Field()
#     update_config = UpdateConfigMutation.Field()
#     delete_config = DeleteConfigMutation.Field()

from strawberry.types import Info
from strawberry_django_plus import gql

from .types import User


@gql.type
class Query:
    @gql.field
    def viewer(self, info: Info) -> User:
        return info.context.request.user
