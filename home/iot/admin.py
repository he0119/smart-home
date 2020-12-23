from django.contrib import admin

from .models import Device, AutowateringData


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_type', 'location', 'created_at',
                    'edited_at', 'is_online', 'online_at', 'offline_at')


class AutowateringDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'time', 'temperature', 'humidity', 'wifi_signal',
                    'valve1', 'valve2', 'valve3', 'pump')


admin.site.register(Device, DeviceAdmin)
admin.site.register(AutowateringData, AutowateringDataAdmin)
