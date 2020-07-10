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
    topic = graphene.Field(TopicType, id=graphene.ID(required=True))
    topics = graphene.List(
        TopicType,
        number=graphene.Int(),
    )
    comments = graphene.List(
        CommentType,
        topic_id=graphene.ID(required=True),
        number=graphene.Int(),
    )

    @login_required
    def resolve_topic(self, info, id):
        return Topic.objects.get(pk=id)

    @login_required
    def resolve_topics(self, info, **kwargs):
        number = kwargs.get('number')

        q = Topic.objects.all().order_by('-is_open', '-date_modified')
        if number:
            return q[:number]
        return q

    @login_required
    def resolve_comments(self, info, **kwargs):
        topic_id = kwargs.get('topic_id')
        number = kwargs.get('number')

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        q = topic.comments.all().order_by('date_created')
        if number:
            return q[:number]
        return q


# endregion


#region mutation
#region inputs
class AddTopicInput(graphene.InputObjectType):
    title = graphene.String(required=True, description='话题的标题')
    description = graphene.String(description='话题的说明')


class DeleteTopicInput(graphene.InputObjectType):
    topic_id = graphene.ID(required=True, description='话题的 ID')


class UpdateTopicInput(graphene.InputObjectType):
    id = graphene.ID(required=True, description='话题的 ID')
    title = graphene.String(description='话题的标题')
    description = graphene.String(description='话题的说明')


class AddCommentInput(graphene.InputObjectType):
    topic_id = graphene.ID(required=True, description='属于的话题 ID')
    body = graphene.String(required=True, description='评论的内容')
    parent_id = graphene.ID(description='上一级评论的 ID')


class DeleteCommentInput(graphene.InputObjectType):
    comment_id = graphene.ID(required=True, description='评论的 ID')


class UpdateCommentInput(graphene.InputObjectType):
    id = graphene.ID(required=True, description='评论的 ID')
    body = graphene.String(description='评论的内容')


class CloseTopicInput(graphene.InputObjectType):
    topic_id = graphene.ID(required=True, description='话题的 ID')


class ReopenTopicInput(graphene.InputObjectType):
    topic_id = graphene.ID(required=True, description='话题的 ID')


#endregion
#region Topic
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
            is_open=True,
        )
        topic.save()
        return AddTopicMutation(topic=topic)


class DeleteTopicMutation(graphene.Mutation):
    class Arguments:
        input = DeleteTopicInput(required=True)

    topic_id = graphene.ID()

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            topic = Topic.objects.get(pk=input.topic_id)
            if topic.user != info.context.user:
                raise GraphQLError('只能删除自己创建的话题')
            topic.delete()
            return DeleteTopicMutation(topic_id=input.topic_id)
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

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')
        # 仅在传入数据时修改
        if input.title is not None:
            topic.title = input.title
        if input.description is not None:
            topic.description = input.description
        topic.save()
        return UpdateTopicMutation(topic=topic)


class CloseTopicMutation(graphene.Mutation):
    class Arguments:
        input = CloseTopicInput(required=True)

    topic = graphene.Field(TopicType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            topic = Topic.objects.get(pk=input.topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')

        topic.is_open = False
        topic.save()
        return CloseTopicMutation(topic=topic)


class ReopenTopicMutation(graphene.Mutation):
    class Arguments:
        input = ReopenTopicInput(required=True)

    topic = graphene.Field(TopicType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            topic = Topic.objects.get(pk=input.topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')

        topic.is_open = True
        topic.save()
        return ReopenTopicMutation(topic=topic)


#endregion
#region Comment
class AddCommentMutation(graphene.Mutation):
    class Arguments:
        input = AddCommentInput(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        comment = Comment(
            topic=Topic.objects.get(pk=input.topic_id),
            user=info.context.user,
            body=input.body,
        )
        if input.parent_id:
            parent_comment = Comment.objects.get(pk=input.parent_id)
            # 若回复层级超过二级，则转换为二级
            comment.parent_id = parent_comment.get_root().id
            # 被回复人
            comment.reply_to = parent_comment.user
        comment.save()
        return AddCommentMutation(comment=comment)


class DeleteCommentMutation(graphene.Mutation):
    class Arguments:
        input = DeleteCommentInput(required=True)

    deletedId = graphene.ID()

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            comment = Comment.objects.get(pk=input.comment_id)
            if comment.user != info.context.user:
                raise GraphQLError('只能删除自己创建的评论')
            comment.delete()
            return DeleteCommentMutation(deletedId=input.comment_id)
        except Comment.DoesNotExist:
            raise GraphQLError('评论不存在')


class UpdateCommentMutation(graphene.Mutation):
    class Arguments:
        input = UpdateCommentInput(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            comment = Comment.objects.get(pk=input.id)
        except Comment.DoesNotExist:
            raise GraphQLError('评论不存在')

        if comment.user != info.context.user:
            raise GraphQLError('只能修改自己创建的评论')
        comment.body = input.body
        comment.save()
        return UpdateCommentMutation(comment=comment)


#endregion


class Mutation(graphene.ObjectType):
    add_topic = AddTopicMutation.Field()
    delete_topic = DeleteTopicMutation.Field()
    update_topic = UpdateTopicMutation.Field()
    close_topic = CloseTopicMutation.Field()
    reopen_topic = ReopenTopicMutation.Field()
    add_comment = AddCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()


#endregion
