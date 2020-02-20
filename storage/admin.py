from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from .models import Item, Storage


class StorageResource(ModelResource):
    parent = Field(column_name='parent',
                   attribute='parent',
                   widget=ForeignKeyWidget(Storage, 'name'))

    class Meta:
        model = Storage
        export_order = (
            'id',
            'name',
            'parent',
            'description',
        )


class ItemResource(ModelResource):
    storage = Field(column_name='storage',
                    attribute='storage',
                    widget=ForeignKeyWidget(Storage, 'name'))

    class Meta:
        model = Item
        export_order = (
            'id',
            'storage',
            'name',
            'number',
            'description',
            'update_date',
        )


class StorageAdmin(ImportExportModelAdmin):
    resource_class = StorageResource
    list_display = ('name', 'parent', 'description')


class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
    list_display = ('name', 'number', 'description', 'update_date', 'storage')


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
