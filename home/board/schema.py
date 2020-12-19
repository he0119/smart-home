import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from home.push.tasks import (PushChannel, get_enable_reg_ids_except_user,
                             push_to_users)

from .models import Comment, Topic


#region type
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        exclude = (
            'lft',
            'rght',
            'treeId',
            'level',
        )
        filter_fields = {
            'id': ['exact'],
            'topic': ['exact'],
        }
        interfaces = (relay.Node, )

    @classmethod
    def get_node(cls, info, id):
        return Comment.objects.get(pk=id)


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = '__all__'
        filter_fields = {
            'id': ['exact'],
            'title': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )

    comments = DjangoFilterConnectionField(CommentType)

    @login_required
    def resolve_comments(self, info, **args):
        return self.comments

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Topic.objects.get(pk=id)


#endregion

#region query


class Query(graphene.ObjectType):
    topics = DjangoFilterConnectionField(TopicType)
    comments = DjangoFilterConnectionField(CommentType)

    @login_required
    def resolve_topics(self, info, **kwargs):
        return Topic.objects.all()

    @login_required
    def resolve_comments(self, info, **kwargs):
        return Comment.objects.all()


# endregion


#region mutation
#region Topic
class AddTopicMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True, description='话题的标题')
        description = graphene.String(required=True, description='话题的说明')

    topic = graphene.Field(TopicType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        topic = Topic(
            title=kwargs.get('title'),
            description=kwargs.get('description'),
            user=info.context.user,
            is_open=True,
        )
        topic.save()

        reg_ids = get_enable_reg_ids_except_user(topic.user)
        if reg_ids:
            push_to_users.delay(
                reg_ids,
                '新话题',
                f'{topic.user.username} 刚发布了一个新话题\n{topic.title}\n{topic.description[:30]}',
                PushChannel.BOARD.value,
            )

        return AddTopicMutation(topic=topic)


class DeleteTopicMutation(relay.ClientIDMutation):
    class Input:
        topic_id = graphene.ID(required=True, description='话题的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, topic_id = from_global_id(kwargs.get('topic_id'))

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能删除自己创建的话题')
        topic.delete()

        return DeleteTopicMutation()


class UpdateTopicMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True, description='话题的 ID')
        title = graphene.String(description='话题的标题')
        description = graphene.String(description='话题的说明')

    topic = graphene.Field(TopicType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, topic_id = from_global_id(kwargs.get('id'))

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')

        # 仅在传入数据时修改
        if kwargs.get('title') is not None:
            topic.title = kwargs.get('title')
        if kwargs.get('description') is not None:
            topic.description = kwargs.get('description')
        topic.save()
        return UpdateTopicMutation(topic=topic)


class CloseTopicMutation(relay.ClientIDMutation):
    class Input:
        topic_id = graphene.ID(required=True, description='话题的 ID')

    topic = graphene.Field(TopicType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, topic_id = from_global_id(kwargs.get('topic_id'))

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')

        topic.is_open = False
        topic.save()
        return CloseTopicMutation(topic=topic)


class ReopenTopicMutation(relay.ClientIDMutation):
    class Input:
        topic_id = graphene.ID(required=True, description='话题的 ID')

    topic = graphene.Field(TopicType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, topic_id = from_global_id(kwargs.get('topic_id'))

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        if topic.user != info.context.user:
            raise GraphQLError('只能修改自己创建的话题')

        topic.is_open = True
        topic.save()
        return ReopenTopicMutation(topic=topic)


#endregion
#region Comment
class AddCommentMutation(relay.ClientIDMutation):
    class Input:
        topic_id = graphene.ID(required=True, description='属于的话题 ID')
        body = graphene.String(required=True, description='评论的内容')
        parent_id = graphene.ID(description='上一级评论的 ID')

    comment = graphene.Field(CommentType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, topic_id = from_global_id(kwargs.get('topic_id'))

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            raise GraphQLError('话题不存在')

        comment = Comment(
            topic=topic,
            user=info.context.user,
            body=kwargs.get('body'),
        )
        if input.parent_id:
            _, parent_id = from_global_id(kwargs.get('parent_id'))
            parent_comment = Comment.objects.get(pk=parent_id)
            # 若回复层级超过二级，则转换为二级
            comment.parent_id = parent_comment.get_root().id
            # 被回复人
            comment.reply_to = parent_comment.user
        comment.save()

        reg_ids = get_enable_reg_ids_except_user(comment.user)
        if reg_ids:
            push_to_users.delay(
                reg_ids,
                '新回复',
                f'{comment.user.username} 在 {comment.topic.title} 话题下发表了新回复\n{comment.body[:30]}',
                PushChannel.BOARD.value,
            )

        return AddCommentMutation(comment=comment)


class DeleteCommentMutation(relay.ClientIDMutation):
    class Input:
        comment_id = graphene.ID(required=True, description='评论的 ID')

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, comment_id = from_global_id(kwargs.get('comment_id'))

        try:
            comment = Comment.objects.get(pk=comment_id)
            if comment.user != info.context.user:
                raise GraphQLError('只能删除自己创建的评论')
            comment.delete()
            return DeleteCommentMutation()
        except Comment.DoesNotExist:
            raise GraphQLError('评论不存在')


class UpdateCommentMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True, description='评论的 ID')
        body = graphene.String(description='评论的内容')

    comment = graphene.Field(CommentType)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        _, comment_id = from_global_id(kwargs.get('id'))

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise GraphQLError('评论不存在')

        if comment.user != info.context.user:
            raise GraphQLError('只能修改自己创建的评论')

        comment.body = kwargs.get('body')
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
