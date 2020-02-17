from django.db import models


class Storage(models.Model):
    """ 存储空间 """
    name = models.CharField(max_length=30)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
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
