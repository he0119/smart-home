import strawberry
from strawberry.tools import merge_types
from strawberry_django_plus.directives import SchemaDirectiveExtension

import home.board.schema
import home.iot.schema
import home.push.schema
import home.storage.schema
import home.users.schema

from .utils import CompatibilityExtension

Query = merge_types(
    "Query",
    (
        home.users.schema.Query,
        home.storage.schema.Query,
        home.board.schema.Query,
        home.push.schema.Query,
        home.iot.schema.Query,
    ),
)
Mutation = merge_types(
    "Mutation",
    (
        home.users.schema.Mutation,
        home.storage.schema.Mutation,
        home.board.schema.Mutation,
        home.push.schema.Mutation,
        home.iot.schema.Mutation,
    ),
)
Subscription = merge_types("Subscription", (home.iot.schema.Subscription,))


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[SchemaDirectiveExtension],
)
