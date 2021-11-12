import graphene
from graphene import relay
from graphene_file_upload.scalars import Upload
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Avatar


class UpdateAvatarMutation(graphene.ClientIDMutation):
    class Input:
        file = Upload(required=True, description="头像")

    avatar = graphene.String()

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

        return UpdateAvatarMutation(avatar=avatar.avatar.url)
