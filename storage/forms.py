from django.forms import ModelForm, DateTimeInput
from django.utils.translation import gettext_lazy as _

from .models import Item, Storage


class StorageForm(ModelForm):
    prefix = 'storage'

    class Meta:
        model = Storage
        fields = ['name', 'parent', 'description']
        labels = {
            'name': _('名字'),
            'parent': _('属于'),
            'description': _('备注'),
        }


class ItemForm(ModelForm):
    prefix = 'item'

    class Meta:
        model = Item
        fields = ['name', 'number', 'storage', 'description']
        labels = {
            'name': _('名字'),
            'number': _('数量'),
            'storage': _('属于'),
            'description': _('备注'),
        }
