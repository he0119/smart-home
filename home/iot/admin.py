from django.contrib import admin, messages

from .models import AutowateringData, AutowateringDataDaily, Device


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "device_type",
        "location",
        "created_at",
        "edited_at",
        "is_online",
        "online_at",
        "offline_at",
    )

    actions = ["regenerate_token"]

    @admin.action(
        permissions=["change"],
        description="重新生成所选设备的令牌",
    )
    def regenerate_token(self, request, queryset):
        for device in queryset:
            device.generate_token()
            device.save(update_fields=["token"])
        self.message_user(request, "令牌已重新生成", messages.SUCCESS)


class AutowateringDataAdmin(admin.ModelAdmin):
    list_filter = ("valve1", "valve2", "valve3", "pump")
    list_display = (
        "device",
        "time",
        "temperature",
        "humidity",
        "wifi_signal",
        "valve1",
        "valve2",
        "valve3",
        "pump",
    )


class AutowateringDataDailyAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "time",
        "min_temperature",
        "max_temperature",
        "min_humidity",
        "max_humidity",
        "min_wifi_signal",
        "max_wifi_signal",
    )


admin.site.register(Device, DeviceAdmin)
admin.site.register(AutowateringData, AutowateringDataAdmin)
admin.site.register(AutowateringDataDaily, AutowateringDataDailyAdmin)
