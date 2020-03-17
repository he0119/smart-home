from datetime import timedelta

import graphene
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Comment, Topic


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = '__all__'


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = '__all__'


class Query(graphene.ObjectType):
    topics = graphene.List(TopicType)
    comments = graphene.List(CommentType, topic_id=graphene.ID(required=True))

    @login_required
    def resolve_topics(self, info, **kwargs):
        return Topic.objects.all()

    @login_required
    def resolve_comments(self, info, **kwargs):
        topic_id = kwargs.get('topic_id')

        return Topic.objects.get(pk=topic_id).comments.all()


# class AddTopicMutation(graphene.Mutation):
#     pass

# class DeleteTopicMutation(graphene.Mutation):
#     pass

# class UpdateTopicMutation(graphene.Mutation):
#     pass

# class AddCommentMutation(graphene.Mutation):
#     pass

# class DeleteCommentMutation(graphene.Mutation):
#     pass

# class UpdateCommentMutation(graphene.Mutation):
# pass


class Mutation(graphene.ObjectType):
    pass
