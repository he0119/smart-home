import strawberry
import strawberry_django
from django.conf import settings
from strawberry.types import Info

from home.utils import IsAuthenticated

from . import models, types


@strawberry.type
class Query:
    mipush: types.MiPush = strawberry_django.node(permission_classes=[IsAuthenticated])
    mi_pushs: strawberry_django.relay.ListConnectionWithTotalCount[types.MiPush] = (
        strawberry_django.connection(permission_classes=[IsAuthenticated])
    )

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def mi_push(self, info: Info, device_id: str) -> types.MiPush | None:
        try:
            mi_push = models.MiPush.objects.filter(user=info.context.request.user).get(
                device_id=device_id
            )
            return mi_push  # type: ignore
        except models.MiPush.DoesNotExist:
            return

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def mi_push_key(self) -> types.MiPushKey:
        return types.MiPushKey(
            app_id=settings.MI_PUSH_APP_ID, app_key=settings.MI_PUSH_APP_KEY
        )


@strawberry.type
class Mutation:
    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_mi_push(
        self,
        info: Info,
        reg_id: str,
        device_id: str,
        model: str,
    ) -> types.MiPush:
        try:
            # 因为一个设备可能登录其他账号
            # 并且一个设备只有一个设备标识码
            # 查找设备标识码对应的记录
            # 并更新相关信息
            mi_push = models.MiPush.objects.get(device_id=device_id)
            mi_push.user = info.context.request.user
            mi_push.reg_id = reg_id
            mi_push.model = model
        except models.MiPush.DoesNotExist:
            # 首次创建时，自动启用
            mi_push = models.MiPush(
                user=info.context.request.user,
                reg_id=reg_id,
                device_id=device_id,
                model=model,
                enable=True,
            )

        mi_push.save()

        return mi_push  # type: ignore
