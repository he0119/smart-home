from django.db import models
from mptt.models import TreeForeignKey, MPTTModel


class Storage(MPTTModel):
    """ 存储位置 """
    name = models.CharField(max_length=200)
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
    name = models.CharField(max_length=200)
    number = models.IntegerField()
    description = models.CharField(max_length=200, null=True, blank=True)
    update_date = models.DateTimeField('date updated')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
