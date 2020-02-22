from django.forms import ModelForm
from mptt.forms import TreeNodeChoiceField

from .models import Item, Storage


class StorageForm(ModelForm):
    prefix = 'storage'

    class Meta:
        model = Storage
        fields = ['name', 'parent', 'description']
        labels = {
            'name': '名字',
            'parent': '属于',
            'description': '备注',
        }


class ItemForm(ModelForm):
    prefix = 'item'

    storage = TreeNodeChoiceField(queryset=Storage.objects.all(), label='属于')

    class Meta:
        model = Item
        fields = ['name', 'number', 'storage', 'price', 'description']
        labels = {
            'name': '名字',
            'number': '数量',
            'storage': '属于',
            'price': '价格',
            'description': '备注',
        }
