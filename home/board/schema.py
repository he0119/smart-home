from django.core.exceptions import ValidationError
from django.utils import timezone
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay

from home.push.tasks import get_enable_reg_ids_except_user, push_to_users
from home.utils import IsAuthenticated

from . import models, types
from .utils import unmark


@gql.type
class Query:
    topic: types.Topic = gql.django.node(permission_classes=[IsAuthenticated])
    topics: relay.Connection[types.Topic] = gql.django.connection(
        permission_classes=[IsAuthenticated]
    )
    comment: types.Comment = gql.django.node(permission_classes=[IsAuthenticated])
    comments: relay.Connection[types.Comment] = gql.django.connection(
        permission_classes=[IsAuthenticated]
    )


@gql.type
class Mutation:
    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def add_topic(
        self,
        info: Info,
        title: str,
        description: str | None,
    ) -> types.Topic:
        topic = models.Topic(
            title=title,
            description=description,
            user=info.context.request.user,
        )

        topic.edited_at = timezone.now()
        topic.save()

        reg_ids = get_enable_reg_ids_except_user(topic.user)
        if reg_ids:
            push_to_users.delay(
                reg_ids,
                f"{topic.user.username} 发布新话题",
                f"{topic.title}\n{unmark(topic.description)}",
                f"/topic/{relay.to_base64(types.Topic, topic.id)}",
                True,
            )  # type: ignore

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def update_topic(
        self,
        info: Info,
        id: relay.GlobalID,
        title: str | None,
        description: str | None,
    ) -> types.Topic:
        try:
            topic = id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        if topic.user != info.context.request.user:
            raise ValidationError("只能修改自己创建的话题")

        if topic.is_closed:
            raise ValidationError("不能修改已关闭的话题")

        # 仅在传入数据时修改
        if title is not None:
            topic.title = title
        if description is not None:
            topic.description = description

        topic.edited_at = timezone.now()
        topic.save()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_topic(self, info: Info, topic_id: relay.GlobalID) -> types.Topic:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        if topic.user != info.context.request.user:
            raise ValidationError("只能删除自己创建的话题")

        if topic.is_closed:
            raise ValidationError("不能删除已关闭的话题")

        topic.delete()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def close_topic(self, info: Info, topic_id: relay.GlobalID) -> types.Topic:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        topic.is_closed = True
        topic.closed_at = timezone.now()
        topic.save()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def reopen_topic(self, info: Info, topic_id: relay.GlobalID) -> types.Topic:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        topic.is_closed = False
        topic.closed_at = None
        topic.save()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def pin_topic(self, info: Info, topic_id: relay.GlobalID) -> types.Topic:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        topic.is_pinned = True
        topic.save()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def unpin_topic(self, info: Info, topic_id: relay.GlobalID) -> types.Topic:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        topic.is_pinned = False
        topic.save()

        return topic  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def add_comment(
        self,
        info: Info,
        topic_id: relay.GlobalID,
        body: str,
        parent_id: relay.GlobalID | None,
    ) -> types.Comment:
        try:
            topic = topic_id.resolve_node_sync(info, ensure_type=models.Topic)
        except:
            raise ValidationError("话题不存在")

        if topic.is_closed:
            raise ValidationError("不能向已关闭话题添加评论")

        comment = models.Comment(
            topic=topic,
            user=info.context.request.user,
            body=body,
        )
        if parent_id:
            try:
                parent_comment = parent_id.resolve_node_sync(
                    info, ensure_type=models.Comment
                )
            except:
                raise ValidationError("回复的评论不存在")
            # 若回复层级超过二级，则转换为二级
            comment.parent_id = parent_comment.get_root().id  # type: ignore
            # 被回复人
            comment.reply_to = parent_comment.user
        comment.save()

        reg_ids = get_enable_reg_ids_except_user(comment.user)
        if reg_ids:
            push_to_users.delay(
                reg_ids,
                f"{comment.topic.title} 下有新回复",
                f"{comment.user.username}：{unmark(comment.body)}",
                f"/topic/{relay.to_base64(types.Topic, topic.id)}",
                True,
            )  # type: ignore
        return comment  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def update_comment(
        self,
        info: Info,
        id: relay.GlobalID,
        body: str,
    ) -> types.Comment:
        try:
            comment = id.resolve_node_sync(info, ensure_type=models.Comment)
        except:
            raise ValidationError("评论不存在")

        if comment.user != info.context.request.user:
            raise ValidationError("只能修改自己创建的评论")

        if comment.topic.is_closed:
            raise ValidationError("不能修改已关闭话题下的评论")

        comment.body = body

        comment.save()

        return comment  # type: ignore

    @gql.django.input_mutation(permission_classes=[IsAuthenticated])
    def delete_comment(self, info: Info, comment_id: relay.GlobalID) -> types.Comment:
        try:
            comment = comment_id.resolve_node_sync(info, ensure_type=models.Comment)
        except:
            raise ValidationError("评论不存在")

        if comment.user != info.context.request.user:
            raise ValidationError("只能删除自己创建的评论")

        if comment.topic.is_closed:
            raise ValidationError("不能删除已关闭话题下的评论")

        comment.delete()

        return comment  # type: ignore
