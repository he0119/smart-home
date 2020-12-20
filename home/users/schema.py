import graphene
from django.contrib.auth import get_user_model
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = '__all__'


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserType)

    @login_required
    def resolve_viewer(self, info):
        return info.context.user
