import os

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models


class SessionStore(DBStore):
    def __init__(self, session_key=None, user_agent=None, ip=None):
        super().__init__(session_key)
        # Truncate user_agent string to max_length of the CharField
        self.user_agent = user_agent[:200] if user_agent else user_agent
        self.ip = ip

    @classmethod
    def get_model_class(cls):  # type: ignore
        return Session

    def create_model_instance(self, data):
        try:
            user_id = int(data.get("_auth_user_id"))  # type: ignore
        except (ValueError, TypeError):
            user_id = None
        return self.model(
            session_key=self._get_or_create_session_key(),  # type: ignore
            session_data=self.encode(data),  # type: ignore
            expire_date=self.get_expiry_date(),  # type: ignore
            user_agent=self.user_agent,  # type: ignore
            user_id=user_id,  # type: ignore
            ip=self.ip,  # type: ignore
        )


class Session(AbstractBaseSession):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="用户",
        related_name="session",
    )
    user_agent = models.CharField("用户代理", blank=True, max_length=200)
    last_activity = models.DateTimeField("最近活跃时间", auto_now=True)
    ip = models.GenericIPAddressField("IP", null=True, blank=True)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore

    class Meta:
        verbose_name = "会话"
        verbose_name_plural = "会话"


def get_file_path(instance, filename):
    """存放在专门的头像目录中

    用户 ID + 后缀名命名
    """
    ext = filename.split(".")[-1]
    return os.path.join("avatar_pictures", f"{instance.user.id}.{ext}")


class Avatar(models.Model):
    id = models.AutoField("ID", primary_key=True, auto_created=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="avatar",
        on_delete=models.CASCADE,
        verbose_name="用户",
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


class Config(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        related_name="configs",
        on_delete=models.CASCADE,
    )
    key = models.CharField(
        "键",
        max_length=200,
    )
    value = models.TextField(
        "值",
    )

    class Meta:
        verbose_name = "配置"
        verbose_name_plural = "配置"
        unique_together = ["user", "key"]

    def __str__(self):
        return self.key
