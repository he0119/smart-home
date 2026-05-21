from django.conf import settings
from django.db import models
from tree_queries.query import TreeQuerySet


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


class CommentQuerySet(TreeQuerySet):
    pass


class Comment(models.Model):
    """评论"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments", verbose_name="话题")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="评论者",
    )
    body = models.TextField("内容")
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    edited_at = models.DateTimeField("修改时间", auto_now=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="属于",
    )
    level = models.PositiveIntegerField("层级", default=0, editable=False, db_index=True)
    reply_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repliers",
        verbose_name="回复给",
    )

    objects = CommentQuerySet.as_manager(with_tree_fields=True)

    class Meta:  # type: ignore
        verbose_name = "评论"
        verbose_name_plural = "评论"

    def __str__(self):
        return self.body[:20]

    def save(self, *args, **kwargs):
        previous_parent_id = None
        if self.pk:
            previous_parent_id = type(self).objects.filter(pk=self.pk).values_list("parent_id", flat=True).first()

        if self.parent_id is None:
            self.level = 0
        elif self.parent is not None:
            self.level = self.parent.level + 1
        else:
            parent = type(self).objects.only("level").get(pk=self.parent_id)
            self.level = parent.level + 1

        super().save(*args, **kwargs)

        if previous_parent_id != self.parent_id:
            descendants = type(self).objects.descendants(self).with_tree_fields()
            updates = []
            for descendant in descendants:
                if descendant.level != descendant.tree_depth:
                    descendant.level = descendant.tree_depth
                    updates.append(descendant)
            if updates:
                type(self).objects.bulk_update(updates, ["level"])

    def get_children(self):
        return self.children.all().order_by("created_at")

    def get_ancestors(self):
        return type(self).objects.ancestors(self)

    def get_root(self):
        return type(self).objects.ancestors(self, include_self=True).first()
