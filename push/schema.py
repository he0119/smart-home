import graphene
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import MiPush


class MiPushType(DjangoObjectType):
    class Meta:
        model = MiPush
        fields = '__all__'


class Query(graphene.ObjectType):
    mi_push = graphene.Field(MiPushType)

    @login_required
    def resolve_mi_push(self, info):
        try:
            mi_push = MiPush.objects.get(user=info.context.user)
            return mi_push
        except MiPush.DoesNotExist:
            raise GraphQLError('推送未绑定')


class UpdateMiPushInput(graphene.InputObjectType):
    reg_id = graphene.String(required=True)


class UpdateMiPushMutation(graphene.Mutation):
    class Arguments:
        input = UpdateMiPushInput(required=True)

    mi_push = graphene.Field(MiPushType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            mi_push = MiPush.objects.get(user=info.context.user)
            mi_push.reg_id = input.reg_id
        except MiPush.DoesNotExist:
            # 首次创建时，自动启用
            mi_push = MiPush(
                user=info.context.user,
                reg_id=input.reg_id,
                enable=True,
            )

        mi_push.save()
        return UpdateMiPushMutation(mi_push=mi_push)


class Mutation(graphene.ObjectType):
    update_mi_push = UpdateMiPushMutation.Field()
