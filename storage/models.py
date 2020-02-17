from django.db import models


class Storage(models.Model):
    """ 存储空间 """
    name = models.CharField(max_length=30)
    parent = models.ForeignKey('self', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)



class Item(models.Model):
    """ 物品 """
    name = models.CharField(max_length=200)
    number = models.IntegerField()
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    update_date = models.DateTimeField('date updated')
