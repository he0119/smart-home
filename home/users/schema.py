import strawberry
import strawberry_django
from django.contrib import auth
from django.core.exceptions import ValidationError
from strawberry import relay
from strawberry.file_uploads import Upload
from strawberry.types import Info

from home.utils import IsAuthenticated

from . import models, types


@strawberry.type
class Query:
    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def viewer(self, info: Info) -> types.User:
        return info.context.request.user


@strawberry.type
class Mutation:
    @strawberry_django.input_mutation()
    def login(self, info: Info, username: str, password: str) -> types.User:
        request = info.context.request
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return user  # type: ignore
        auth.logout(request)
        raise ValidationError("用户名或密码错误")

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    def logout(self, info: Info) -> types.User:
        request = info.context.request
        user = request.user
        auth.logout(request)
        return user

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_config(self, info: Info, key: str, value: str) -> types.Config:
        user = info.context.request.user

        config = user.configs.filter(key=key).first()
        if config:
            config.value = value
            config.save()
        else:
            config = models.Config(
                user=user,
                key=key,
                value=value,
            )
            config.save()

        return config  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_config(self, info: Info, key: str) -> types.Config:
        user = info.context.request.user

        config = user.configs.filter(key=key).first()
        if config:
            config.delete()
            return config
        else:
            raise ValidationError("key not found")

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def update_avatar(self, info: Info, file: Upload) -> types.Avatar:
        user = info.context.request.user

        if hasattr(user, "avatar"):
            avatar = user.avatar
            avatar.avatar = file
        else:
            avatar = models.Avatar(
                user=user,
                avatar=file,
            )

        avatar.save()

        return avatar  # type: ignore

    @strawberry_django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_session(self, info: Info, id: relay.GlobalID) -> types.Session:
        try:
            session = id.resolve_node_sync(info, ensure_type=models.Session)
        except Exception:
            raise ValidationError("会话不存在")

        if session.user != info.context.request.user:
            raise ValidationError("只能删除自己的会话")

        session.delete()
        return session  # type: ignore
