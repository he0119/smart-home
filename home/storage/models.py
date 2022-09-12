import os
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class Storage(MPTTModel):
    name = models.CharField("名字", max_length=200, unique=True)
    parent = TreeForeignKey(
        "self",
        verbose_name="属于",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    description = models.CharField("备注", max_length=200, blank=True)

    @property
    def ancestors(self):
        return self.get_ancestors()

    class Meta:
        verbose_name = "位置"
        verbose_name_plural = "位置"

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField("名字", max_length=200, unique=True)
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

    def delete(self):
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
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("item_pictures", f"{instance.item.id}-{filename}")


class Picture(models.Model):
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
