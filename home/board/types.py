from django.db.models import Max
from django.db.models.functions import Greatest
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import Comment, Topic


class CommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = {
            "topic": ["exact"],
            "level": ["exact"],
        }

    order_by = OrderingFilter(fields=(("created_at", "created_at"),))


class CustomTopicOrderingFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] += [
            ("active_at", "Active At"),
            ("-active_at", "Active At (descending)"),
        ]

    def filter(self, qs, value):
        if value and any(v in ["active_at", "-active_at"] for v in value):
            # 新增一个最近活动的时间
            # 取话题修改时间与最新评论的创建时间的最大值
            qs = qs.annotate(
                active_at=Greatest(Max("comments__created_at"), "edited_at")
            )

        return super().filter(qs, value)


class TopicFilter(FilterSet):
    class Meta:
        model = Topic
        fields = {
            "title": ["exact", "icontains", "istartswith"],
        }

    order_by = CustomTopicOrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("edited_at", "edited_at"),
            ("closed_at", "closed_at"),
            ("is_open", "is_open"),
            ("is_pin", "is_pin"),
        )
    )


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"
        interfaces = (relay.Node,)

    children = DjangoFilterConnectionField(
        lambda: CommentType, filterset_class=CommentFilter
    )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Comment.objects.get(pk=id)


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = "__all__"
        interfaces = (relay.Node,)

    comments = DjangoFilterConnectionField(CommentType, filterset_class=CommentFilter)

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Topic.objects.get(pk=id)
