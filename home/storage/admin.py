from django.contrib import admin

from .models import Item, Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage', 'number', 'price', 'description',
                    'expired_at', 'get_consumables', 'edited_at', 'edited_by',
                    'created_at', 'created_by')

    def get_consumables(self, obj):
        return '\n'.join([p.name for p in obj.consumables.all()])

    get_consumables.short_description = '耗材'


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
