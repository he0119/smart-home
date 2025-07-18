"""生产环境配置"""

import json
import os

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = ["*"]

# CSRF
# https://docs.djangoproject.com/zh-hans/4.0/ref/settings/#csrf-trusted-origins

CSRF_TRUSTED_ORIGINS = json.loads(os.getenv("CSRF_TRUSTED_ORIGINS", "[]"))

# Database
# https://docs.djangoproject.com/zh-hans/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

# Security
# https://docs.djangoproject.com/zh-hans/4.0/topics/security/

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email
# https://docs.djangoproject.com/zh-hans/4.0/topics/email/

EMAIL_HOST = "smtp.exmail.qq.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
SERVER_EMAIL = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
ADMINS = list(
    zip(
        os.getenv("ADMINS_NAME", "").split(";"),
        os.getenv("ADMINS_EMAIL", "").split(";"),
    )
)

# Celery
# https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# 小米小爱
# https://developers.xiaoai.mi.com/documents/Home?type=/api/doc/render_markdown/SkillAccess/SkillDocument/CustomSkills/Signature

XIAOAI_KEY_ID = os.getenv("XIAOAI_KEY_ID")
XIAOAI_SECRET = os.getenv("XIAOAI_SECRET")

# 小米推送
# https://dev.mi.com/console/doc/detail?pId=1788

MI_PUSH_PACKAGE_NAME = os.getenv("MI_PUSH_PACKAGE_NAME")
MI_PUSH_APP_ID = os.getenv("MI_PUSH_APP_ID")
MI_PUSH_APP_KEY = os.getenv("MI_PUSH_APP_KEY")
MI_PUSH_APP_SECRET = os.getenv("MI_PUSH_APP_SECRET")

# https://docs.djangoproject.com/zh-hans/3.1/ref/settings/#media-url

MEDIA_URL = os.getenv("MEDIA_URL")

# Django Storages(S3)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

if os.getenv("AWS_S3_ENDPOINT_URL"):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    MEDIA_ROOT = ""

    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

# Channels
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html
# https://pypi.org/project/channels-redis/

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("CHANNEL_REDIS_URL")],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}
