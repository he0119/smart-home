import graphene
from graphene import relay
from graphql_jwt.decorators import login_required

from .models import MiPush
from .types import MiPushType


class UpdateMiPushMutation(relay.ClientIDMutation):
    class Input:
        reg_id = graphene.String(required=True)
        device_id = graphene.String(required=True)
        model = graphene.String(required=True)

    mi_push = graphene.Field(MiPushType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        reg_id = input.get('reg_id')
        device_id = input.get('device_id')
        model = input.get('model')

        try:
            # 因为一个设备可能登录其他账号
            # 并且一个设备只有一个设备标识码
            # 查找设备标识码对应的记录
            # 并更新相关信息
            mi_push = MiPush.objects.get(device_id=device_id)
            mi_push.user = info.context.user
            mi_push.reg_id = reg_id
            mi_push.model = model
        except MiPush.DoesNotExist:
            # 首次创建时，自动启用
            mi_push = MiPush(
                user=info.context.user,
                reg_id=reg_id,
                device_id=device_id,
                model=model,
                enable=True,
            )

        mi_push.save()
        return UpdateMiPushMutation(mi_push=mi_push)
