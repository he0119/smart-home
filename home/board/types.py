from typing import Optional

import strawberry
import strawberry_django
from django.db.models import Max
from django.db.models.functions import Greatest
from strawberry import relay

from home.users.types import User

from . import models


@strawberry_django.ordering.order(models.Comment)
class CommentOrder:
    created_at: strawberry.auto


@strawberry_django.filters.filter(model=models.Comment, lookups=True)
class CommentFilter:
    level: strawberry.auto
    topic: "TopicFilter | None" = strawberry.UNSET


@strawberry_django.ordering.order(models.Topic)
class TopicOrder:
    created_at: strawberry.auto
    edited_at: strawberry.auto
    is_closed: strawberry.auto
    is_pinned: strawberry.auto
    active_at: strawberry.auto


@strawberry_django.filters.filter(model=models.Topic, lookups=True)
class TopicFilter:
    id: relay.GlobalID
    title: strawberry.auto


@strawberry_django.type(models.Topic, filters=TopicFilter, order=TopicOrder)
class Topic(relay.Node):
    title: strawberry.auto
    description: strawberry.auto
    is_closed: strawberry.auto
    closed_at: strawberry.auto
    user: User
    created_at: strawberry.auto
    edited_at: strawberry.auto
    is_pinned: strawberry.auto
    comments: strawberry_django.relay.ListConnectionWithTotalCount["Comment"] = (
        strawberry_django.connection(filters=CommentFilter, order=CommentOrder)
    )

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        return queryset.annotate(
            active_at=Greatest(Max("comments__created_at"), "edited_at")
        )


@strawberry_django.type(models.Comment, filters=CommentFilter, order=CommentOrder)
class Comment(relay.Node):
    topic: Topic
    user: User
    body: strawberry.auto
    created_at: strawberry.auto
    edited_at: strawberry.auto
    parent: Optional["Comment"]
    reply_to: User | None
