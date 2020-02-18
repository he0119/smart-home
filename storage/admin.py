from django.contrib import admin

from .models import Item, Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'description', 'update_date', 'storage')


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
