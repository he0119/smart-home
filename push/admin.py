from django.contrib import admin

from .models import MiPush


class MiPushAdmin(admin.ModelAdmin):
    fields = ['user', 'enable']
    list_display = ('user', 'enable')


admin.site.register(MiPush, MiPushAdmin)
