from django.forms import ModelForm

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

    class Meta:
        model = Item
        fields = ['name', 'number', 'storage', 'description']
        labels = {
            'name': '名字',
            'number': '数量',
            'storage': '属于',
            'description': '备注',
        }
