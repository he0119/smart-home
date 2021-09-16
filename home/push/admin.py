from django.contrib import admin

from .models import MiPush


class MiPushAdmin(admin.ModelAdmin):
    list_filter = ("user",)
    list_display = ("user", "enable", "reg_id", "device_id", "model")


admin.site.register(MiPush, MiPushAdmin)
