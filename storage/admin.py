from django.contrib import admin

from .models import Item, Storage

admin.site.register(Storage)
admin.site.register(Item)
