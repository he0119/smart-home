from django.contrib import admin

from .models import Item, Picture, Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "description")
    search_fields = ["name", "description"]


class PictureAdmin(admin.ModelAdmin):
    list_filter = ("item",)
    list_display = ("item", "picture", "description", "created_at", "created_by")


class PictureInline(admin.TabularInline):
    model = Picture
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    inlines = [PictureInline]
    list_display = (
        "name",
        "storage",
        "number",
        "price",
        "description",
        "expired_at",
        "get_consumables",
        "edited_at",
        "edited_by",
        "created_at",
        "created_by",
    )
    search_fields = ["name", "description"]

    @admin.display(description="耗材")
    def get_consumables(self, obj):
        return "\n".join([p.name for p in obj.consumables.all()])


admin.site.register(Storage, StorageAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Picture, PictureAdmin)
