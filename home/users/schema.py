from django.core.exceptions import ValidationError
from strawberry.file_uploads import Upload
from strawberry.types import Info
from strawberry_django_plus import gql

from home.utils import IsAuthenticated

from . import models, types


@gql.type
class Query:
    @gql.django.field(permission_classes=[IsAuthenticated])
    def viewer(self, info: Info) -> types.User:
        return info.context.request.user


@gql.type
class Mutation:
    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
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

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_config(self, info: Info, key: str) -> types.Config:
        user = info.context.request.user

        config = user.configs.filter(key=key).first()
        if config:
            config.delete()
            return config
        else:
            raise ValidationError("key not found")

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
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
