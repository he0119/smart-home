from django.conf import settings
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class Storage(MPTTModel):
    """ 存储位置 """
    class Meta:
        verbose_name = '位置'
        verbose_name_plural = '位置'

    class MPTTMeta:
        order_insertion_by = ['name']

    name = models.CharField('名字', max_length=200, unique=True)
    parent = TreeForeignKey('self',
                            verbose_name='属于',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children')
    description = models.CharField('备注', max_length=200, blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    """ 物品 """
    class Meta:
        verbose_name = '物品'
        verbose_name_plural = '物品'
        ordering = ['name']

    name = models.CharField('名字', max_length=200, unique=True)
    number = models.IntegerField('数量')
    description = models.CharField('备注', max_length=200, blank=True)
    price = models.DecimalField('价格',
                                max_digits=10,
                                decimal_places=2,
                                null=True,
                                blank=True)
    expired_at = models.DateTimeField('有效日期', null=True, blank=True)
    # 如果值为 null，指未分类，没有设定存放位置
    storage = models.ForeignKey(Storage,
                                verbose_name='属于',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='items')
    created_at = models.DateTimeField('添加时间', auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='录入人',
                                   on_delete=models.SET_NULL,
                                   related_name='created_items',
                                   null=True,
                                   blank=True)
    edited_at = models.DateTimeField('修改时间')
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  verbose_name='修改人',
                                  on_delete=models.SET_NULL,
                                  related_name='edited_items',
                                  null=True,
                                  blank=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)
    consumables = models.ManyToManyField('self',
                                         verbose_name='耗材',
                                         related_name='consumed_by',
                                         symmetrical=False,
                                         blank=True)

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.name
