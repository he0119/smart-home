import strawberry
from strawberry.tools import merge_types
from strawberry_django_plus.directives import SchemaDirectiveExtension

import home.storage.schema
import home.users.schema

Query = merge_types("Query", (home.users.schema.Query, home.storage.schema.Query))
Mutation = merge_types(
    "Mutation", (home.users.schema.Mutation, home.storage.schema.Mutation)
)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        SchemaDirectiveExtension,
    ],
)
