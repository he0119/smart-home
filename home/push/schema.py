import graphene
from django.conf import settings
from django_filters import FilterSet
from graphene import ObjectType, relay
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import MiPush


#region type
class MiPushFilter(FilterSet):
    class Meta:
        model = MiPush
        fields = {
            'user': ['exact'],
            'model': ['exact', 'icontains', 'istartswith'],
        }


class MiPushType(DjangoObjectType):
    class Meta:
        model = MiPush
        fields = '__all__'
        interfaces = (relay.Node, )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return MiPush.objects.get(pk=id)


class MiPushKeyType(ObjectType):
    app_id = graphene.String()
    app_key = graphene.String()


#endregion


#region query
class Query(graphene.ObjectType):
    mi_push = graphene.Field(MiPushType,
                             device_id=graphene.String(required=True))
    mi_push_key = graphene.Field(MiPushKeyType)

    @login_required
    def resolve_mi_push(self, info, device_id):
        try:
            mi_push = MiPush.objects.filter(user=info.context.user).get(
                device_id=device_id)
            return mi_push
        except MiPush.DoesNotExist:
            raise GraphQLError('推送未绑定')

    @login_required
    def resolve_mi_push_key(self, info):
        return MiPushKeyType(app_id=settings.MI_PUSH_APP_ID,
                             app_key=settings.MI_PUSH_APP_KEY)


#endregion


#region mutation
class UpdateMiPushMutation(relay.ClientIDMutation):
    class Input:
        reg_id = graphene.String(required=True)
        device_id = graphene.String(required=True)
        model = graphene.String(required=True)

    mi_push = graphene.Field(MiPushType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        try:
            # 查找当前用户下的对应设备标识码的记录
            mi_push = MiPush.objects.filter(user=info.context.user).get(
                device_id=kwargs.get('device_id'))
            mi_push.reg_id = kwargs.get('reg_id')
        except MiPush.DoesNotExist:
            # 首次创建时，自动启用
            mi_push = MiPush(
                user=info.context.user,
                reg_id=kwargs.get('reg_id'),
                device_id=kwargs.get('device_id'),
                model=kwargs.get('model'),
                enable=True,
            )

        mi_push.save()
        return UpdateMiPushMutation(mi_push=mi_push)


class Mutation(graphene.ObjectType):
    update_mi_push = UpdateMiPushMutation.Field()


#endregion
