import graphene
from graphene import relay
from graphene_file_upload.scalars import Upload
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Avatar, Config
from .types import ConfigType


class UpdateAvatarMutation(graphene.ClientIDMutation):
    class Input:
        file = Upload(required=True, description="头像")

    avatar_url = graphene.String()

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        file = input.get("file")

        user = info.context.user

        if hasattr(user, "avatar"):
            avatar = user.avatar
            avatar.avatar = file
        else:
            avatar = Avatar(
                user=user,
                avatar=file,
            )

        avatar.save()

        return UpdateAvatarMutation(avatar_url=avatar.avatar.url)


class UpdateConfigMutation(graphene.ClientIDMutation):
    class Input:
        key = graphene.String(required=True)
        value = graphene.String(required=True)

    config = graphene.Field(ConfigType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        key = input.get("key")
        value = input.get("value")

        user = info.context.user

        config = user.configs.filter(key=key).first()
        if config:
            config.value = value
            config.save()
        else:
            config = Config(
                user=user,
                key=key,
                value=value,
            )
            config.save()

        return UpdateConfigMutation(config=config)


class DeleteConfigMutation(graphene.ClientIDMutation):
    class Input:
        key = graphene.String(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        key = input.get("key")

        user = info.context.user

        user.configs.filter(key=key).delete()

        return DeleteConfigMutation()
