from typing import Optional

from django.db.models import Max
from django.db.models.functions import Greatest
from strawberry import auto, relay
from strawberry_django_plus import gql

from home.users.types import User

from . import models


@gql.django.ordering.order(models.Comment)
class CommentOrder:
    created_at: auto


@gql.django.filters.filter(model=models.Comment, lookups=True)
class CommentFilter:
    topic: "TopicFilter"
    level: auto


@gql.django.ordering.order(models.Topic)
class TopicOrder:
    created_at: auto
    edited_at: auto
    is_closed: auto
    is_pinned: auto
    active_at: auto


@gql.django.filters.filter(model=models.Topic, lookups=True)
class TopicFilter:
    id: relay.GlobalID
    title: auto


@gql.django.type(models.Topic, filters=TopicFilter, order=TopicOrder)
class Topic(relay.Node):
    title: auto
    description: auto
    is_closed: auto
    closed_at: auto
    user: User
    created_at: auto
    edited_at: auto
    is_pinned: auto
    comments: relay.Connection["Comment"] = gql.django.connection(
        filters=CommentFilter, order=CommentOrder
    )

    # FIXME: Strawberry 的 bug，看起来少传了一个 self 参数，暂时对我没影响
    # https://github.com/strawberry-graphql/strawberry-graphql-django/issues/173
    @staticmethod
    def get_queryset(queryset, info):
        return queryset.annotate(
            active_at=Greatest(Max("comments__created_at"), "edited_at")
        )


@gql.django.type(models.Comment, filters=CommentFilter, order=CommentOrder)
class Comment(relay.Node):
    topic: Topic
    user: User
    body: auto
    created_at: auto
    edited_at: auto
    parent: Optional["Comment"]
    reply_to: User | None
