from django.contrib import admin

from .models import Avatar, Config


class AvatarAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")


class ConfigAdmin(admin.ModelAdmin):
    list_display = ("user", "config", "updated_at")


admin.site.register(Avatar, AvatarAdmin)
admin.site.register(Config, ConfigAdmin)
