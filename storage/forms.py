from django.forms import ModelForm
from mptt.forms import TreeNodeChoiceField

from .models import Item, Storage


class StorageForm(ModelForm):
    prefix = 'storage'

    class Meta:
        model = Storage
        fields = ['name', 'parent', 'description']


class ItemForm(ModelForm):
    prefix = 'item'

    storage = TreeNodeChoiceField(queryset=Storage.objects.all(), label='属于')

    class Meta:
        model = Item
        fields = ['name', 'number', 'storage', 'price', 'description']
