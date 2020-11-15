from django.db import models

from django.conf import settings


class MiPush(models.Model):
    class Meta:
        verbose_name = '小米推送'
        verbose_name_plural = '小米推送'

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name='用户')
    enable = models.BooleanField(verbose_name='启用')

    def __str__(self):
        return self.user.username
