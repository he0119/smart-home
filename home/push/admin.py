from django.contrib import admin

from .models import MiPush


class MiPushAdmin(admin.ModelAdmin):
    fields = ['user', 'enable', 'reg_id']
    list_display = ('user', 'enable', 'reg_id')


admin.site.register(MiPush, MiPushAdmin)
