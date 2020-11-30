import graphene
import graphql_jwt

import home.board.schema
import home.iot.schema
import home.storage.schema
import home.push.schema
import home.users.schema


class Query(
        home.storage.schema.Query,
        home.board.schema.Query,
        home.iot.schema.Query,
        home.push.schema.Query,
        home.users.schema.Query,
        graphene.ObjectType,
):
    pass


class Mutation(
        home.storage.schema.Mutation,
        home.board.schema.Mutation,
        home.iot.schema.Mutation,
        home.push.schema.Mutation,
        graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
