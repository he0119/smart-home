from django.contrib import admin

from .models import Item, Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage', 'number', 'price', 'description',
                    'expired_at', 'edited_at', 'edited_by', 'created_at',
                    'created_by')


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
