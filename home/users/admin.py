from django.contrib import admin

from .models import Avatar


class AvatarAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")


admin.site.register(Avatar, AvatarAdmin)
