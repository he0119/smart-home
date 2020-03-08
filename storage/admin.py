from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from .models import Item, Storage


class StorageResource(ModelResource):
    parent = Field(column_name='parent',
                   attribute='parent',
                   widget=ForeignKeyWidget(Storage, 'name'))

    class Meta:
        model = Storage
        exclude = (
            'lft',
            'rght',
            'tree_id',
            'level',
        )
        export_order = (
            'id',
            'name',
            'parent',
            'description',
        )
        skip_unchanged = True
        report_skipped = False


class ItemResource(ModelResource):
    storage = Field(column_name='storage',
                    attribute='storage',
                    widget=ForeignKeyWidget(Storage, 'name'))
    editor = Field(column_name='editor',
                   attribute='editor',
                   widget=ForeignKeyWidget(get_user_model(), 'username'))

    class Meta:
        model = Item
        export_order = (
            'id',
            'storage',
            'name',
            'number',
            'price',
            'description',
            'expiration_date',
            'update_date',
            'editor',
        )
        skip_unchanged = True
        report_skipped = False


class StorageAdmin(ImportExportModelAdmin):
    resource_class = StorageResource
    list_display = ('name', 'parent', 'description')


class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
    list_display = ('name', 'number', 'price', 'description',
                    'expiration_date', 'update_date', 'storage', 'editor')


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
