from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Topic(models.Model):
    """话题"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    title = models.CharField("标题", max_length=200)
    description = models.TextField("说明")
    is_closed = models.BooleanField("已关闭", default=False)
    closed_at = models.DateTimeField("关闭时间", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="创建者",
    )
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    edited_at = models.DateTimeField("修改时间")
    is_pinned = models.BooleanField("置顶", default=False)

    class Meta:
        verbose_name = "话题"
        verbose_name_plural = "话题"

    def __str__(self):
        return self.title


class Comment(MPTTModel):
    """评论"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="comments", verbose_name="话题"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="评论者",
    )
    body = models.TextField("内容")
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    edited_at = models.DateTimeField("修改时间", auto_now=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="属于",
    )
    reply_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repliers",
        verbose_name="回复给",
    )

    class Meta:  # type: ignore
        verbose_name = "评论"
        verbose_name_plural = "评论"

    def __str__(self):
        return self.body[:20]
