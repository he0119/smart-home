import graphene
from django.contrib.auth import get_user_model
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Comment, Topic


#region query
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


# endregion


#region mutation
class TopicInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    title = graphene.String()
    description = graphene.String()


class CommentInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    topic = TopicInput()
    body = graphene.String()


class AddTopicInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    parent = TopicInput()


class UpdateTopicInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    title = graphene.String()
    description = graphene.String()


class AddCommentInput(graphene.InputObjectType):
    topic = TopicInput(required=True)
    body = graphene.String(required=True)
    parent = CommentInput()


class UpdateCommentInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    body = graphene.String()


class AddTopicMutation(graphene.Mutation):
    class Arguments:
        input = AddTopicInput(required=True)

    topic = graphene.Field(TopicType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        topic = Topic(
            title=input.title,
            description=input.description,
            user=info.context.user,
        )
        topic.save()
        return AddTopicMutation(topic=topic)


class DeleteTopicMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    deletedId = graphene.ID()

    @login_required
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')

        try:
            storage = Topic.objects.get(pk=id)
            storage.delete()
            return DeleteTopicMutation(deletedId=id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')


class UpdateTopicMutation(graphene.Mutation):
    class Arguments:
        input = UpdateTopicInput(required=True)

    topic = graphene.Field(TopicType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            topic = Topic.objects.get(pk=input.id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        topic.title = input.title
        topic.description = input.description
        topic.save()
        return UpdateTopicMutation(topic=topic)


# class AddCommentMutation(graphene.Mutation):
#     pass

# class DeleteCommentMutation(graphene.Mutation):
#     pass

# class UpdateCommentMutation(graphene.Mutation):
#     pass


class Mutation(graphene.ObjectType):
    add_topic = AddTopicMutation.Field()
    delete_topic = DeleteTopicMutation.Field()
    update_topic = UpdateTopicMutation.Field()


#endregion
