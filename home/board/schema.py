import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from .models import Comment, Topic
from .mutations import (AddCommentMutation, AddTopicMutation,
                        CloseTopicMutation, DeleteCommentMutation,
                        DeleteTopicMutation, PinTopicMutation,
                        ReopenTopicMutation, UnpinTopicMutation,
                        UpdateCommentMutation, UpdateTopicMutation)
from .types import CommentFilter, CommentType, TopicFilter, TopicType


class Query(graphene.ObjectType):
    topic = relay.Node.Field(TopicType)
    topics = DjangoFilterConnectionField(TopicType,
                                         filterset_class=TopicFilter)
    comment = relay.Node.Field(CommentType)
    comments = DjangoFilterConnectionField(CommentType,
                                           filterset_class=CommentFilter)

    @login_required
    def resolve_topics(self, info, **args):
        return Topic.objects.all()

    @login_required
    def resolve_comments(self, info, **args):
        return Comment.objects.all()


class Mutation(graphene.ObjectType):
    add_topic = AddTopicMutation.Field()
    delete_topic = DeleteTopicMutation.Field()
    update_topic = UpdateTopicMutation.Field()
    close_topic = CloseTopicMutation.Field()
    reopen_topic = ReopenTopicMutation.Field()
    add_comment = AddCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    pin_topic = PinTopicMutation.Field()
    unpin_topic = UnpinTopicMutation.Field()
