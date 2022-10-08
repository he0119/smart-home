from django.conf import settings
from django.db import models


class MiPush(models.Model):
    class Meta:
        verbose_name = "小米推送"
        verbose_name_plural = "小米推送"

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mipush",
        verbose_name="用户",
    )
    enable = models.BooleanField(verbose_name="启用")
    reg_id = models.CharField(max_length=100, verbose_name="注册标识码", unique=True)
    device_id = models.CharField(max_length=100, verbose_name="设备标识码", unique=True)
    model = models.CharField(max_length=100, verbose_name="设备型号")

    def __str__(self):
        return self.user.username
