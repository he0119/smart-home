import graphene
import graphql_jwt
from graphene import relay

import home.board.schema
import home.iot.schema
import home.push.schema
import home.storage.schema
import home.users.schema


class Query(
    home.storage.schema.Query,
    home.board.schema.Query,
    home.iot.schema.Query,
    home.push.schema.Query,
    home.users.schema.Query,
    graphene.ObjectType,
):
    node = relay.Node.Field()


class Mutation(
    home.storage.schema.Mutation,
    home.board.schema.Mutation,
    home.iot.schema.Mutation,
    home.push.schema.Mutation,
    graphene.ObjectType,
):
    token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()
    revoke_token = graphql_jwt.relay.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
