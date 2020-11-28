import graphene
import graphql_jwt

import board.schema
import iot.schema
import storage.schema
import push.schema
import users.schema


class Query(
        storage.schema.Query,
        board.schema.Query,
        iot.schema.Query,
        push.schema.Query,
        users.schema.Query,
        graphene.ObjectType,
):
    pass


class Mutation(
        storage.schema.Mutation,
        board.schema.Mutation,
        iot.schema.Mutation,
        push.schema.Mutation,
        graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
