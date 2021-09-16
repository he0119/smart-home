import graphene
from django.conf import settings
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import MiPush
from .mutations import UpdateMiPushMutation
from .types import MiPushFilter, MiPushKeyType, MiPushType


class Query(graphene.ObjectType):
    mi_push = graphene.Field(MiPushType, device_id=graphene.String(required=True))
    mi_pushs = DjangoFilterConnectionField(MiPushType, filterset_class=MiPushFilter)
    mi_push_key = graphene.Field(MiPushKeyType)

    @login_required
    def resolve_mi_push(self, info, device_id):
        try:
            mi_push = MiPush.objects.filter(user=info.context.user).get(
                device_id=device_id
            )
            return mi_push
        except MiPush.DoesNotExist:
            raise GraphQLError("推送未绑定")

    @login_required
    def resolve_mi_pushs(self, info, **args):
        return MiPush.objects.all()

    @login_required
    def resolve_mi_push_key(self, info):
        return MiPushKeyType(
            app_id=settings.MI_PUSH_APP_ID, app_key=settings.MI_PUSH_APP_KEY
        )


class Mutation(graphene.ObjectType):
    update_mi_push = UpdateMiPushMutation.Field()


# endregion
