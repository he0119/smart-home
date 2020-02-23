from django.db import models
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
    update_date = models.DateTimeField(verbose_name='更新时间')
    storage = models.ForeignKey(Storage,
                                on_delete=models.CASCADE,
                                verbose_name='属于')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                null=True,
                                blank=True,
                                verbose_name='价格')

    def __str__(self):
        return self.name
