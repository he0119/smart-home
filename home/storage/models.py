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

    name = models.CharField(max_length=200, unique=True, verbose_name='名字')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children',
                            verbose_name='属于')
    description = models.CharField(max_length=200,
                                   null=True,
                                   blank=True,
                                   verbose_name='备注')

    def __str__(self):
        return self.name


class Item(models.Model):
    """ 物品 """
    class Meta:
        verbose_name = '物品'
        verbose_name_plural = '物品'
        ordering = ['name']

    name = models.CharField(max_length=200, unique=True, verbose_name='名字')
    number = models.IntegerField(verbose_name='数量')
    description = models.CharField(max_length=200,
                                   null=True,
                                   blank=True,
                                   verbose_name='备注')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                null=True,
                                blank=True,
                                verbose_name='价格')
    expired_at = models.DateTimeField(null=True,
                                      blank=True,
                                      verbose_name='有效日期')
    # 如果值为 null，指未分类，没有设定存放位置
    storage = models.ForeignKey(Storage,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='items',
                                verbose_name='属于')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL,
                                   related_name='created_items',
                                   null=True,
                                   blank=True,
                                   verbose_name='录入人')
    edited_at = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.SET_NULL,
                                  related_name='edited_items',
                                  null=True,
                                  blank=True,
                                  verbose_name='修改人')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    deleted_at = models.DateTimeField(null=True,
                                      blank=True,
                                      verbose_name='删除时间')
    consumables = models.ManyToManyField('self',
                                         related_name='consumed_by',
                                         symmetrical=False,
                                         blank=True,
                                         verbose_name='耗材')

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
