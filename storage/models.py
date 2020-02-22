from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Storage(MPTTModel):
    """ 存储位置 """
    class MPTTMeta:
        order_insertion_by = ['name']

    name = models.CharField(max_length=200, unique=True)
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children')
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    """ 物品 """
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200, unique=True)
    number = models.IntegerField()
    description = models.CharField(max_length=200, null=True, blank=True)
    update_date = models.DateTimeField('date updated')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                null=True,
                                blank=True)

    def __str__(self):
        return self.name
