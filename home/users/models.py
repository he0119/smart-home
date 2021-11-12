import os

from django.conf import settings
from django.db import models


def get_file_path(instance, filename):
    """存放在专门的头像目录中

    用户 ID + 后缀名命名
    """
    ext = filename.split(".")[-1]
    return os.path.join("avatar_pictures", f"{instance.user.id}.{ext}")


class Avatar(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        related_name="avatar",
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(
        "头像",
        upload_to=get_file_path,
    )
    created_at = models.DateTimeField(
        "添加时间",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "头像"
        verbose_name_plural = "头像"

    def __str__(self):
        return self.user.username
