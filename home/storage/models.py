import os
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from tree_queries.query import TreeQuerySet


class StorageQuerySet(TreeQuerySet):
    pass


class Storage(models.Model):
    id = models.AutoField("ID", primary_key=True, auto_created=True)
    name = models.CharField("名字", max_length=200)
    parent = models.ForeignKey(
        "self",
        verbose_name="属于",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    description = models.CharField("备注", max_length=200, blank=True)
    level = models.PositiveIntegerField("层级", default=0, editable=False, db_index=True)

    objects = StorageQuerySet.as_manager(with_tree_fields=True)

    class Meta:  # type: ignore
        verbose_name = "位置"
        verbose_name_plural = "位置"

    def __str__(self):
        return self.name

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

    @property
    def ancestors(self):
        return self.get_ancestors()

    def get_children(self):
        return self.children.all().order_by("name")

    def get_ancestors(self):
        return type(self).objects.ancestors(self)

    def get_root(self):
        return type(self).objects.ancestors(self, include_self=True).first()


class Item(models.Model):
    id = models.AutoField("ID", primary_key=True, auto_created=True)
    name = models.CharField("名字", max_length=200)
    number = models.IntegerField("数量")
    description = models.CharField("备注", max_length=200, blank=True)
    price = models.FloatField(
        "价格",
        null=True,
        blank=True,
    )
    expired_at = models.DateTimeField("有效日期", null=True, blank=True)
    # 如果值为 null，指未分类，没有设定存放位置
    storage = models.ForeignKey(
        Storage,
        verbose_name="属于",
        related_name="items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("添加时间", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="录入人",
        related_name="created_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    edited_at = models.DateTimeField("修改时间")
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="修改人",
        related_name="edited_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField("逻辑删除", default=False)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    consumables = models.ManyToManyField(
        "self",
        verbose_name="耗材",
        related_name="consumed_by",
        symmetrical=False,
        blank=True,
    )

    class Meta:
        verbose_name = "物品"
        verbose_name_plural = "物品"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def delete(self):  # type: ignore
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


def get_file_path(instance, filename):
    """生成独一无二的 ID

    物品 ID + UUID4
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("item_pictures", f"{instance.item.id}-{filename}")


class Picture(models.Model):
    id = models.AutoField("ID", primary_key=True, auto_created=True)
    description = models.CharField(
        "备注",
        max_length=200,
        blank=True,
    )
    item = models.ForeignKey(
        Item,
        verbose_name="物品",
        related_name="pictures",
        on_delete=models.CASCADE,
    )
    picture = models.ImageField(
        "图片",
        upload_to=get_file_path,
    )
    created_at = models.DateTimeField(
        "添加时间",
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="添加人",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    box_x = models.FloatField("边界框中心点 X")
    box_y = models.FloatField("边界框中心点 Y")
    box_h = models.FloatField("边界框高")
    box_w = models.FloatField("边界框宽")

    class Meta:
        verbose_name = "图片"
        verbose_name_plural = "图片"

    def __str__(self):
        return self.description or self.picture.name.split("/")[-1]
