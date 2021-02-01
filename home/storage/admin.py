from django.contrib import admin

from .models import Item, ItemConsumables, Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')


class ItemConsumablesInline(admin.TabularInline):
    model = ItemConsumables
    extra = 1
    fk_name = 'item'


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage', 'number', 'price', 'description',
                    'expired_at', 'get_consumables', 'edited_at', 'edited_by',
                    'created_at', 'created_by')

    inlines = (ItemConsumablesInline, )

    def get_consumables(self, obj):
        return ','.join([p.name for p in obj.consumables.all()])

    get_consumables.short_description = '耗材'


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
